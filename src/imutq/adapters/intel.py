# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Solutions
"""Adaptador Intel para o IMUT-Q.

Emissao do dialeto QASM do Intel Quantum SDK para os seis circuitos canonicos,
montagem do candidato a recibo v2 e a costura unica com o SDK.

Fronteira declarada (ARCHITECTURE.md, regra 1 e 2):
    este modulo PROPOE. Ele emite circuito, le contagens e monta candidato a
    recibo. Quem DECIDE o veredito definitivo e quem SELA a assinatura e o
    nucleo Rust (`imutq veredito`, `imutq verificar`). O `veredito` que sai
    daqui se chama `candidato` no docstring e nas funcoes internas por isso.

Nenhuma dependencia obrigatoria do SDK no import: `iqs` so e tocado dentro de
`PonteSDKIntel` / `sdk_disponivel()`, e a ausencia dele e um estado normal, nao
um erro de importacao.

O que e IMPLEMENTADO aqui (roda e e testado sem o SDK):
    - emissao de QASM para BELL_Z, BELL_X, DJ_balanced, DJ_constant, GHZ_3, IDENTITY
    - normalizacao de contagens, p-valor, veredito candidato trivalente
    - montagem e selagem do recibo v2 (ReciboV2 de ..receipt)

O que e ESPECIFICACAO (nao validado contra hardware/SDK real, acesso bloqueado):
    - `PonteSDKIntel.submeter` e a tabela `_TRADUCAO_PORTA`: nomes de chamada do
      SDK, semantica de `ordem_bits` e formato de `job_id` devolvido pelo SDK.
    - o perfil de dialeto em `DialetoIntel` (cabecalho e `include`). Se o
      front-end QASM do SDK exigir outro `include` ou um pragma de alvo, troca-se
      apenas `DialetoIntel`; o emissor nao muda.
"""
from __future__ import annotations

import importlib
import os
import shutil
import subprocess
from dataclasses import dataclass, field
from typing import Callable, Iterable, Mapping, Protocol

from ..receipt import ReciboV2, canonical, sha3_hex

# ---------------------------------------------------------------------------
# Constantes de recibo
# ---------------------------------------------------------------------------

PROVEDOR = "Intel Quantum SDK"
VERSAO_ADAPTADOR = "intel-qsdksim"      # igual em espirito a "qiskit-ibm-runtime" do hw.py
VERSAO_IMUTQ = "0.1.0"                  # paridade com src/imutq/hw.py e recibos ja selados
VERSAO_ZYQL = "2.5.9"                   # paridade com src/imutq/hw.py

#: Banda do kernel. Tem de casar com `BANDA` em rust/src/main.rs.
BANDA = 0.15

#: Circuitos canonicos exigidos pelo contrato do adaptador.
TESTES_CANONICOS = (
    "BELL_Z",
    "BELL_X",
    "DJ_balanced",
    "DJ_constant",
    "GHZ_3",
    "IDENTITY",
)


# ---------------------------------------------------------------------------
# Dialeto
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class DialetoIntel:
    """Perfil de dialeto QASM aceito pelo front-end do Intel Quantum SDK.

    ESPECIFICACAO: o perfil foi fixado no subconjunto de OpenQASM 2.0 que o SDK
    documenta aceitar (qreg/creg, `h`, `x`, `cx`, `barrier`, `measure`). O acesso
    ao SDK esta bloqueado nesta maquina, entao o cabecalho e o `include` NAO
    foram confrontados com o parser real. Quando o acesso sair, este dataclass e
    o unico ponto a ajustar: `cabecalho` e `include` sao texto puro e o emissor
    nao depende deles.
    """

    cabecalho: tuple[str, ...] = ("OPENQASM 2.0;", 'include "qelib1.inc";')
    nome_medida: str = "measure"
    separador_operandos: str = ","
    fecha_instrucao: str = ";"

    def linha(self, instrucao: str) -> str:
        return instrucao + self.fecha_instrucao


DIALETO_PADRAO = DialetoIntel()


# ---------------------------------------------------------------------------
# Emissor de QASM (escrito do zero; sem Qiskit, sem SDK)
# ---------------------------------------------------------------------------

class _Circuito:
    """Acumulador de instrucoes. Ordem de emissao = ordem de chamada."""

    def __init__(self, qubits: int, classicos: int, dialeto: DialetoIntel = DIALETO_PADRAO):
        if qubits < 1 or classicos < 1:
            raise ValueError("circuito exige ao menos 1 qubit e 1 bit classico")
        self.qubits = qubits
        self.classicos = classicos
        self.dialeto = dialeto
        self._linhas: list[str] = []

    def porta(self, nome: str, *alvos: int) -> "_Circuito":
        for a in alvos:
            if not 0 <= a < self.qubits:
                raise ValueError(f"{nome}: qubit {a} fora de 0..{self.qubits - 1}")
        ops = self.dialeto.separador_operandos.join(f"q[{a}]" for a in alvos)
        self._linhas.append(self.dialeto.linha(f"{nome} {ops}" if ops else nome))
        return self

    def barreira(self) -> "_Circuito":
        ops = self.dialeto.separador_operandos.join(f"q[{a}]" for a in range(self.qubits))
        self._linhas.append(self.dialeto.linha(f"barrier {ops}"))
        return self

    def medir_todos(self) -> "_Circuito":
        for a in range(self.classicos):
            self._linhas.append(
                self.dialeto.linha(f"{self.dialeto.nome_medida} q[{a}] -> c[{a}]")
            )
        return self

    def render(self) -> str:
        cabeca = list(self.dialeto.cabecalho)
        corpo = [
            self.dialeto.linha(f"qreg q[{self.qubits}]"),
            self.dialeto.linha(f"creg c[{self.classicos}]"),
            *self._linhas,
        ]
        return "\n".join([*cabeca, *corpo]) + "\n"


def _bell_z(d: DialetoIntel) -> _Circuito:
    c = _Circuito(2, 2, d)
    c.porta("h", 0).porta("cx", 0, 1).barreira().medir_todos()
    return c


def _bell_x(d: DialetoIntel) -> _Circuito:
    # |Phi+> medido na base X: rotaciona os dois qubits com H antes de medir.
    c = _Circuito(2, 2, d)
    c.porta("h", 0).porta("cx", 0, 1).barreira()
    c.porta("h", 0).porta("h", 1).barreira().medir_todos()
    return c


def _dj(n: int, balanceado: bool, d: DialetoIntel) -> _Circuito:
    # n qubits de entrada + 1 ancilla (q[n]); mede os n de entrada.
    c = _Circuito(n + 1, n, d)
    c.porta("x", n)
    for i in range(n + 1):
        c.porta("h", i)
    if balanceado:
        for i in range(n):
            c.porta("cx", i, n)
    for i in range(n):
        c.porta("h", i)
    c.barreira().medir_todos()
    return c


def _ghz_3(d: DialetoIntel) -> _Circuito:
    c = _Circuito(3, 3, d)
    c.porta("h", 0).porta("cx", 0, 1).porta("cx", 1, 2).barreira().medir_todos()
    return c


def _identity(d: DialetoIntel) -> _Circuito:
    c = _Circuito(2, 2, d)
    c.barreira().medir_todos()
    return c


def qasm_canonico(teste: str, *, dialeto: DialetoIntel = DIALETO_PADRAO) -> str:
    """Texto QASM do circuito canonico `teste`, no dialeto Intel.

    Puro: nao importa SDK, nao importa Qiskit, nao toca rede.
    """
    if teste == "BELL_Z":
        return _bell_z(dialeto).render()
    if teste == "BELL_X":
        return _bell_x(dialeto).render()
    if teste == "DJ_balanced":
        return _dj(3, True, dialeto).render()
    if teste == "DJ_constant":
        return _dj(3, False, dialeto).render()
    if teste == "GHZ_3":
        return _ghz_3(dialeto).render()
    if teste == "IDENTITY":
        return _identity(dialeto).render()
    raise KeyError(f"teste fora do contrato: {teste!r} (validos: {', '.join(TESTES_CANONICOS)})")


def todos_os_qasm(*, dialeto: DialetoIntel = DIALETO_PADRAO) -> dict[str, str]:
    """Os seis circuitos canonicos de uma vez, prontos para hash_circuito."""
    return {t: qasm_canonico(t, dialeto=dialeto) for t in TESTES_CANONICOS}


#: Quantos bits cada circuito mede. Usado para normalizar as contagens.
LARGURA_CLASSICA = {
    "BELL_Z": 2,
    "BELL_X": 2,
    "DJ_balanced": 3,
    "DJ_constant": 3,
    "GHZ_3": 3,
    "IDENTITY": 2,
}

#: Estados que contam a favor do teste. O p-valor e a fracao neles.
ESTADOS_FAVORAVEIS: dict[str, tuple[str, ...]] = {
    "BELL_Z": ("00", "11"),
    "BELL_X": ("00", "11"),
    "DJ_balanced": ("111",),
    "DJ_constant": ("000",),
    "GHZ_3": ("000", "111"),
    "IDENTITY": ("00",),
}


def estados_favoraveis(teste: str) -> tuple[str, ...]:
    if teste not in ESTADOS_FAVORAVEIS:
        raise KeyError(f"teste fora do contrato: {teste!r}")
    return ESTADOS_FAVORAVEIS[teste]


# ---------------------------------------------------------------------------
# Contagens vindas do SDK
# ---------------------------------------------------------------------------

def normalizar_contagens(contagens: Mapping[object, object], largura: int) -> dict[str, int]:
    """Normaliza contagens para {bitstring_de_largura_fixa: int}.

    Aceita chaves que o SDK costuma devolver: int (0, 3), str binaria ("011"),
    str com espacos ("0 1 1") e str com prefixo de medida. Valores viram int.

    ESPECIFICACAO: a ordem de bits e a convencao do Qiskit (indice 0 = qubit 0,
    bit menos significativo a direita), que e o que os recibos ja emitidos usam.
    Se o SDK entregar o bit mais significativo em q[0], o chamador inverte antes
    de passar aqui (`ordem_bits` da PonteSDKIntel). Nao adivinhamos: contagem de
    largura errada levanta erro em vez de silenciosamente truncar.
    """
    if largura < 1:
        raise ValueError("largura tem de ser >= 1")
    saida: dict[str, int] = {}
    for chave, valor in contagens.items():
        if isinstance(chave, bool):
            raise ValueError(f"chave booleana nao e estado: {chave!r}")
        if isinstance(chave, int):
            if chave < 0:
                raise ValueError(f"estado negativo: {chave!r}")
            bits = format(chave, f"0{largura}b")
            if len(bits) > largura:
                raise ValueError(f"estado {chave} nao cabe em {largura} bits")
        else:
            bruto = str(chave).replace(" ", "").replace("_", "")
            if bruto.startswith("0b"):
                bruto = bruto[2:]
            if not bruto or set(bruto) - {"0", "1"}:
                raise ValueError(f"estado nao binario: {chave!r}")
            if len(bruto) != largura:
                raise ValueError(
                    f"estado {chave!r} tem {len(bruto)} bits, esperado {largura}"
                )
            bits = bruto
        n = int(valor)
        if n < 0:
            raise ValueError(f"contagem negativa para {chave!r}: {n}")
        saida[bits] = saida.get(bits, 0) + n
    return saida


def p_valor(teste: str, contagens: Mapping[str, int]) -> float:
    """Fracao das amostras nos estados favoraveis. 0.0 para amostra vazia."""
    total = sum(int(v) for v in contagens.values())
    if total <= 0:
        return 0.0
    favor = sum(int(contagens.get(e, 0)) for e in estados_favoraveis(teste))
    return favor / total


def veredito_candidato(p: float, banda: float = BANDA) -> str:
    """Espelho de `decidir` em rust/src/main.rs: "1" | "0" | "REFUSED".

    Trivalente de proposito: dentro da banda nao ha decisao, ha recusa. Nunca
    arredonda. O nome diz `candidato` porque o veredito definitivo e do nucleo.
    """
    if not (0.0 <= p <= 1.0):
        return "REFUSED"
    if p >= 1.0 - banda:
        return "1"
    if p <= banda:
        return "0"
    return "REFUSED"


def hash_resultado_bruto(contagens: Mapping[str, int]) -> str:
    """SHA3-256 do resultado ordenado. Mesma formula de src/imutq/hw.py."""
    return sha3_hex(canonical({str(k): int(v) for k, v in sorted(contagens.items())}))


# ---------------------------------------------------------------------------
# Recibo v2
# ---------------------------------------------------------------------------

def montar_recibo_v2(
    teste: str,
    contagens: Mapping[object, object],
    *,
    job_id: str | None = None,
    shots_pedido: int | None = None,
    backend: str = "iqs-sim",
    dispositivo: str = "IQS (simulador de vetor de estado)",
    qasm: str | None = None,
    provedor: str = PROVEDOR,
    versao_adaptador: str = VERSAO_ADAPTADOR,
    banda: float = BANDA,
    sk: bytes | None = None,
    pk: bytes | None = None,
    emitido_em: str | None = None,
) -> ReciboV2:
    """Monta o candidato a recibo v2 a partir de contagens do Intel Quantum SDK.

    Regra dura de proveniencia (README, RECIBO.md): o `job_id` so entra como
    proveniencia `primaria` se foi capturado na submissao. Sem `job_id`, o
    recibo e marcado `reconstruida` e a nota diz por que. Nao inventamos id.

    `qasm` e o texto efetivamente submetido; se omitido, usa o canonico do teste.
    O `hash_circuito` e sempre SHA3-256 do texto que vai no campo, entao o
    verificador pode reconferir o que foi enviado.

    `sk`/`pk` selam a assinatura ML-DSA-44. Sem chaves o recibo sai sem
    assinatura e o nucleo Rust o rejeita -- que e o comportamento correto.
    """
    if teste not in TESTES_CANONICOS:
        raise KeyError(f"teste fora do contrato: {teste!r}")

    texto_qasm = qasm if qasm is not None else qasm_canonico(teste)
    normalizadas = normalizar_contagens(contagens, LARGURA_CLASSICA[teste])
    total = sum(normalizadas.values())
    if total <= 0:
        raise ValueError("contagens vazias: recibo exigiria shots_efetivo=0 e p indefinido")

    p = p_valor(teste, normalizadas)

    if job_id:
        proveniencia = "primaria"
        nota = None
    else:
        proveniencia = "reconstruida"
        nota = (
            "job_id nao capturado na submissao; vinculo posterior nao eleva a "
            "proveniencia a primaria (regra do recibo v2)"
        )

    recibo = ReciboV2(
        teste=teste,
        veredito=veredito_candidato(p, banda),
        job_id=job_id or "",
        provedor=provedor,
        backend=backend,
        dispositivo=dispositivo,
        hash_circuito=sha3_hex(texto_qasm),
        shots_pedido=int(shots_pedido) if shots_pedido is not None else total,
        shots_efetivo=total,
        contagens=dict(sorted(normalizadas.items())),
        hash_resultado_bruto=hash_resultado_bruto(normalizadas),
        versao_imutq=VERSAO_IMUTQ,
        versao_zyql=VERSAO_ZYQL,
        versao_adaptador=versao_adaptador,
        proveniencia=proveniencia,
        nota_proveniencia=nota,
    )
    if emitido_em:
        recibo.emitido_em = emitido_em
    return recibo.selar(sk, pk)


def montar_lote(
    resultados: Mapping[str, Mapping[object, object]],
    *,
    job_ids: Mapping[str, str] | None = None,
    shots_pedido: int | None = None,
    sk: bytes | None = None,
    pk: bytes | None = None,
    **comum,
) -> list[ReciboV2]:
    """Um recibo por teste, na ordem de TESTES_CANONICOS presente em `resultados`."""
    job_ids = job_ids or {}
    return [
        montar_recibo_v2(
            teste,
            contagens,
            job_id=job_ids.get(teste),
            shots_pedido=shots_pedido,
            sk=sk,
            pk=pk,
            **comum,
        )
        for teste, contagens in resultados.items()
    ]


# ---------------------------------------------------------------------------
# Costura com o SDK (ESPECIFICACAO)
# ---------------------------------------------------------------------------

class SDKIndisponivel(RuntimeError):
    """O Intel Quantum SDK nao esta instalado acessivel neste ambiente."""


class ErroSDKIntel(RuntimeError):
    """O SDK respondeu de forma inesperada: a costura precisa de ajuste."""


#: Modulos candidatos dos bindings Python do Intel Quantum SDK, em ordem de
#: preferencia. ESPECIFICACAO: `intelqsdk.cbindings` e o binding Python citado na
#: documentacao do ambiente Intel do qBraid; `iqs` e o simulador de vetor de
#: estado por tras do SDK. Nenhum dos dois pode ser importado nesta maquina
#: (acesso bloqueado), entao a ordem e o nome exatos NAO foram confirmados.
MODULOS_SDK = ("intelqsdk", "iqs")

#: Compatibilidade: nome unico usado nas mensagens de erro.
MODULO_SDK = MODULOS_SDK[0]

#: Como o SDK traduz QASM para o seu IR (documentado no ambiente Intel do qBraid).
#: ESPECIFICACAO: `openqasm-bridge` (pacote `openqasm_bridge`) e o front-end
#: OpenQASM 2.0; `intel-quantum-compiler -B arquivo.qasm` faz a mesma traducao
#: pela linha de comando. O emissor deste modulo produz OpenQASM 2.0 justamente
#: para cair nesse caminho.
FERRAMENTA_QASM = "openqasm_bridge / intel-quantum-compiler -B"

#: ESPECIFICACAO: porta QASM -> chamada no SDK. Nao validado, o SDK esta fora
#: de alcance aqui. Serve para deixar explicito onde a traducao acontece e para
#: o dia em que o acesso sair so isso precisar de conferencia.
_TRADUCAO_PORTA = {
    "h": "apply_h",
    "x": "apply_x",
    "cx": "apply_cnot",
}


class ExecutorSDK(Protocol):
    """Assinatura do ponto de injecao.

    Um executor recebe (qasm, shots) e devolve (job_id, contagens). E aqui que
    entra a chamada real ao SDK quando houver acesso. Injetar o executor mantem
    o adaptador testavel sem SDK e deixa a fronteira num unico lugar.
    """

    def __call__(self, qasm: str, shots: int) -> tuple[str, Mapping[object, object]]: ...


def sdk_disponivel() -> bool:
    """True se algum binding Python do Intel Quantum SDK pode ser importado.

    Import tardio de proposito: o modulo nunca falha ao ser importado por causa
    da ausencia do SDK.
    """
    return _importar_sdk(opcional=True) is not None


def _importar_sdk(opcional: bool = False):
    """Devolve o primeiro modulo do SDK importavel.

    Com `opcional=True`, esgota a lista e devolve None. Sem ele, levanta
    SDKIndisponivel com o motivo de cada tentativa.
    """
    falhas: list[str] = []
    for nome in MODULOS_SDK:
        try:
            return importlib.import_module(nome)
        except Exception as exc:  # ImportError, ou erro de carga de lib nativa
            falhas.append(f"{nome}: {type(exc).__name__}: {exc}")
    if opcional:
        return None
    raise SDKIndisponivel(
        "Intel Quantum SDK ausente: nenhum dos bindings importou ("
        + "; ".join(falhas)
        + "). O emissor de QASM e a montagem de recibo funcionam sem ele; so a "
        "submissao exige o SDK."
    )


@dataclass
class PonteSDKIntel:
    """Ponto unico de acoplamento com o Intel Quantum SDK.

    ESPECIFICACAO: a API real do SDK nao foi exercitada (acesso bloqueado). A
    ponte isola tres suposicoes que o acesso vai ter de confirmar:
      1. como pedir um dispositivo (`abrir_dispositivo`),
      2. como aplicar portas e medir (`aplicar`/`medir`, via `_TRADUCAO_PORTA`),
      3. qual a ordem de bits das contagens devolvidas (`ordem_bits`).

    Enquanto as tres nao forem conferidas, `submeter` levanta `SDKIndisponivel`
    em vez de devolver numero inventado. Preferimos recusar a fingir medicao.
    """

    backend: str = "iqs-sim"
    shots: int = 1024
    ordem_bits: str = "big"          # "big": q[0] e o bit mais a esquerda
    dispositivo: str = "IQS (simulador de vetor de estado)"
    executor: ExecutorSDK | None = None
    _sdk: object | None = field(default=None, repr=False)

    def abrir_dispositivo(self):
        """Devolve o dispositivo do SDK. ESPECIFICACAO.

        Procura um construtor conhecido (`QuantumDevice`, `FullStateSimulator`)
        no modulo importado. Se nenhum existir, recusa em vez de adivinhar: a
        API real do SDK nao foi observada aqui.
        """
        self._sdk = _importar_sdk()
        for nome in ("QuantumDevice", "FullStateSimulator"):
            fabrica = getattr(self._sdk, nome, None)
            if callable(fabrica):
                return fabrica(num_qubits=3, seed=0)
        raise ErroSDKIntel(
            f"{MODULO_SDK!r} importou mas nao expoe QuantumDevice nem "
            "FullStateSimulator: a costura precisa ser reescrita contra a API "
            "real do SDK"
        )

    def _inverter(self, contagens: Mapping[object, object]) -> dict[str, int]:
        if self.ordem_bits == "big":
            return dict(contagens)
        if self.ordem_bits == "little":
            return {str(k)[::-1]: v for k, v in contagens.items()}
        raise ValueError(f"ordem_bits invalida: {self.ordem_bits!r}")

    def submeter(self, teste: str, *, shots: int | None = None) -> tuple[str, dict[str, int]]:
        """Submete um circuito canonico e devolve (job_id, contagens normalizadas).

        Com `executor` injetado, usa o executor (util para ensaio e para plugar
        um transporte proprio). Sem executor e sem SDK, recusa.
        """
        if teste not in TESTES_CANONICOS:
            raise KeyError(f"teste fora do contrato: {teste!r}")
        n = int(shots if shots is not None else self.shots)
        if n < 1:
            raise ValueError("shots tem de ser >= 1")
        qasm = qasm_canonico(teste)
        if self.executor is None:
            if not sdk_disponivel():
                raise SDKIndisponivel(
                    f"Intel Quantum SDK ausente: {MODULO_SDK!r} nao importa. "
                    "Sem SDK, sem submissao. Injetar um executor permite ensaiar "
                    "o caminho completo sem hardware."
                )
            raise ErroSDKIntel(
                "SDK presente, mas a costura de submissao nao foi validada contra "
                "a API real (ESPECIFICACAO). Injetar um executor ou implementar "
                "`submeter` contra o SDK antes de usar em recibo."
            )
        job_id, contagens = self.executor(qasm, n)
        if not job_id:
            raise ErroSDKIntel("executor devolveu job_id vazio: sem proveniencia primaria")
        normalizadas = normalizar_contagens(
            self._inverter(contagens), LARGURA_CLASSICA[teste]
        )
        return str(job_id), normalizadas

    def executar_e_montar(
        self, teste: str, *, shots: int | None = None, sk: bytes | None = None,
        pk: bytes | None = None,
    ) -> ReciboV2:
        """Caminho completo: submeter, medir, montar recibo. Exige SDK/executor."""
        n = int(shots if shots is not None else self.shots)
        job_id, contagens = self.submeter(teste, shots=n)
        return montar_recibo_v2(
            teste,
            contagens,
            job_id=job_id,
            shots_pedido=n,
            backend=self.backend,
            dispositivo=self.dispositivo,
            sk=sk,
            pk=pk,
        )


# ---------------------------------------------------------------------------
# Conferencia no nucleo Rust (opcional)
# ---------------------------------------------------------------------------

def confirmar_no_nucleo(p: float, n: int, binario: str = "./rust/target/release/imutq") -> str | None:
    """Pede o veredito ao nucleo Rust: `imutq veredito <p> <n>`.

    Devolve "1", "0", "REFUSED", ou None se o binario nao estiver construido.
    Serve para o adaptador nao se arrogar a decisao: ele propoe o candidato e
    confere com quem tem autoridade sobre o veredito.
    """
    if not (shutil.which(binario) or os.path.isfile(binario)):
        return None
    saida = subprocess.run(
        [binario, "veredito", repr(float(p)), str(int(n))],
        capture_output=True, text=True, timeout=30, check=False,
    )
    for linha in saida.stdout.splitlines():
        if linha.startswith("veredito:"):
            return linha.split(":", 1)[1].strip()
    return None
