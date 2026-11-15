# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Solutions
"""Testes do adaptador Intel do IMUT-Q.

Regra: tudo aqui roda SEM o Intel Quantum SDK. O que exige o SDK esta marcado
com `skipif` e e pulado quando o import falha -- que e o estado atual, porque o
acesso ao SDK esta bloqueado nesta maquina.

Nenhum teste importa Qiskit: o adaptador emite QASM por conta propria e a suite
nao deve depender de terceiros para validar o que ele emite.
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import pytest

RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from dilithium_py.ml_dsa import ML_DSA_44  # noqa: E402

from imutq.adapters import intel  # noqa: E402
from imutq.receipt import ReciboV2, canonical, sha3_hex  # noqa: E402

BINARIO_RUST = RAIZ / "rust" / "target" / "release" / "imutq"
SDK_PRESENTE = intel.sdk_disponivel()
precisa_sdk = pytest.mark.skipif(
    not SDK_PRESENTE, reason="Intel Quantum SDK ausente (acesso bloqueado)"
)


# ---------------------------------------------------------------------------
# QASM esperado, literal. Se o emissor mudar, este texto muda junto e o teste
# acusa a diferenca exata.
# ---------------------------------------------------------------------------

QASM_ESPERADO = {
    "BELL_Z": """OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];
h q[0];
cx q[0],q[1];
barrier q[0],q[1];
measure q[0] -> c[0];
measure q[1] -> c[1];
""",
    "BELL_X": """OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];
h q[0];
cx q[0],q[1];
barrier q[0],q[1];
h q[0];
h q[1];
barrier q[0],q[1];
measure q[0] -> c[0];
measure q[1] -> c[1];
""",
    "DJ_balanced": """OPENQASM 2.0;
include "qelib1.inc";
qreg q[4];
creg c[3];
x q[3];
h q[0];
h q[1];
h q[2];
h q[3];
cx q[0],q[3];
cx q[1],q[3];
cx q[2],q[3];
h q[0];
h q[1];
h q[2];
barrier q[0],q[1],q[2],q[3];
measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
""",
    "DJ_constant": """OPENQASM 2.0;
include "qelib1.inc";
qreg q[4];
creg c[3];
x q[3];
h q[0];
h q[1];
h q[2];
h q[3];
h q[0];
h q[1];
h q[2];
barrier q[0],q[1],q[2],q[3];
measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
""",
    "GHZ_3": """OPENQASM 2.0;
include "qelib1.inc";
qreg q[3];
creg c[3];
h q[0];
cx q[0],q[1];
cx q[1],q[2];
barrier q[0],q[1],q[2];
measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
""",
    "IDENTITY": """OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];
barrier q[0],q[1];
measure q[0] -> c[0];
measure q[1] -> c[1];
""",
}


def test_contrato_tem_os_seis_circuitos():
    assert set(intel.TESTES_CANONICOS) == set(QASM_ESPERADO)
    assert set(intel.todos_os_qasm()) == set(QASM_ESPERADO)


@pytest.mark.parametrize("teste", sorted(QASM_ESPERADO))
def test_qasm_gerado_casa_com_esperado(teste):
    assert intel.qasm_canonico(teste) == QASM_ESPERADO[teste]


def test_qasm_termina_em_newline_e_nao_repete_barreira():
    for teste, qasm in intel.todos_os_qasm().items():
        assert qasm.endswith("\n"), teste
        assert qasm.count("OPENQASM 2.0;") == 1, teste
        assert qasm.count("include \"qelib1.inc\";") == 1, teste


def test_import_nao_exige_sdk():
    """Importar o adaptador em subprocesso limpo, com o SDK escondido."""
    codigo = (
        "import sys\n"
        "class Bloqueio:\n"
        "    def find_module(self, nome, path=None):\n"
        "        if nome.split('.')[0] == 'iqs':\n"
        "            raise ImportError('bloqueado no teste')\n"
        "        return None\n"
        "    def find_spec(self, nome, path=None, alvo=None):\n"
        "        if nome.split('.')[0] == 'iqs':\n"
        "            raise ImportError('bloqueado no teste')\n"
        "        return None\n"
        "sys.meta_path.insert(0, Bloqueio())\n"
        "from imutq.adapters import intel\n"
        "assert intel.sdk_disponivel() is False\n"
        "assert intel.qasm_canonico('BELL_Z').startswith('OPENQASM 2.0;')\n"
        "assert 'iqs' not in sys.modules\n"
        "print('ok')\n"
    )
    r = subprocess.run(
        [sys.executable, "-c", codigo],
        capture_output=True, text=True, cwd=str(RAIZ),
        env={"PYTHONPATH": str(RAIZ / "src"), "PATH": "/usr/bin:/bin"},
        timeout=120,
    )
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip() == "ok"


def test_teste_fora_do_contrato_falha():
    with pytest.raises(KeyError):
        intel.qasm_canonico("GROVER")
    with pytest.raises(KeyError):
        intel.estados_favoraveis("GROVER")


def test_dialeto_e_ponto_unico_de_ajuste():
    """Trocar o perfil de dialeto muda o texto sem tocar no emissor."""
    outro = intel.DialetoIntel(
        cabecalho=("OPENQASM 3.0;", 'include "stdgates.inc";'),
        nome_medida="measure",
    )
    qasm = intel.qasm_canonico("GHZ_3", dialeto=outro)
    assert qasm.startswith("OPENQASM 3.0;\ninclude \"stdgates.inc\";\n")
    assert "h q[0];" in qasm and "measure q[2] -> c[2];" in qasm


# ---------------------------------------------------------------------------
# Contagens
# ---------------------------------------------------------------------------

def test_normalizar_aceita_int_e_texto():
    a = intel.normalizar_contagens({0: 500, 3: 500}, 2)
    b = intel.normalizar_contagens({"00": 500, "11": 500}, 2)
    c = intel.normalizar_contagens({"0 0": 500, "0b11": 500}, 2)
    assert a == b == c == {"00": 500, "11": 500}


def test_normalizar_soma_chaves_que_apontam_para_o_mesmo_estado():
    # "01" (texto, largura exata) e 1 (int, preenchido com zeros) sao o mesmo estado.
    d = intel.normalizar_contagens({"01": 2, 1: 4}, 2)
    assert d == {"01": 6}


def test_normalizar_texto_exige_largura_exata():
    """Int e preenchido com zeros; texto tem de vir na largura declarada.

    Regra deliberada: contagem numerica tem valor semantico e cabe em qualquer
    largura, mas texto curto costuma ser leitura truncada. Recusar e melhor do
    que gravar um recibo com largura errada."""
    assert intel.normalizar_contagens({1: 4}, 3) == {"001": 4}
    with pytest.raises(ValueError):
        intel.normalizar_contagens({"1": 4}, 3)


def test_normalizar_recusa_largura_errada():
    with pytest.raises(ValueError):
        intel.normalizar_contagens({"010": 10}, 2)


def test_normalizar_recusa_estado_invalido():
    with pytest.raises(ValueError):
        intel.normalizar_contagens({"0x1": 10}, 2)
    with pytest.raises(ValueError):
        intel.normalizar_contagens({"01": -3}, 2)
    with pytest.raises(ValueError):
        intel.normalizar_contagens({True: 3}, 2)


# ---------------------------------------------------------------------------
# p-valor e veredito candidato
# ---------------------------------------------------------------------------

def test_p_valor_conta_so_estados_favoraveis():
    assert intel.p_valor("BELL_Z", {"00": 45, "11": 40, "01": 10, "10": 5}) == pytest.approx(0.85)
    assert intel.p_valor("DJ_balanced", {"111": 90, "000": 10}) == pytest.approx(0.9)
    assert intel.p_valor("DJ_constant", {"111": 90, "000": 10}) == pytest.approx(0.1)
    assert intel.p_valor("BELL_Z", {"00": 0}) == 0.0


def test_veredito_candidato_e_trivalente_nos_limites():
    b = intel.BANDA
    assert intel.veredito_candidato(1.0) == "1"
    assert intel.veredito_candidato(1.0 - b) == "1"      # limite entra em 1
    assert intel.veredito_candidato(1.0 - b - 0.001) == "REFUSED"
    assert intel.veredito_candidato(b) == "0"            # limite entra em 0
    assert intel.veredito_candidato(b + 0.001) == "REFUSED"
    assert intel.veredito_candidato(0.5) == "REFUSED"
    assert intel.veredito_candidato(-0.1) == "REFUSED"
    assert intel.veredito_candidato(1.1) == "REFUSED"


@pytest.mark.skipif(not BINARIO_RUST.is_file(), reason="binario Rust nao construido")
@pytest.mark.parametrize("p", [0.0, 0.05, 0.15, 0.1500001, 0.5, 0.8499, 0.85, 0.99, 1.0])
def test_veredito_casa_com_o_nucleo_rust(p):
    r = subprocess.run(
        [str(BINARIO_RUST), "veredito", repr(p), "1024"],
        capture_output=True, text=True, timeout=60,
    )
    linha = next(l for l in r.stdout.splitlines() if l.startswith("veredito:"))
    do_rust = linha.split(":", 1)[1].strip()
    assert do_rust == intel.veredito_candidato(p), f"divergencia em p={p}"


# ---------------------------------------------------------------------------
# Recibo v2
# ---------------------------------------------------------------------------

def base_args(**kw):
    dados = dict(
        contagens={"00": 480, "11": 470, "01": 40, "10": 34},
        job_id="iqs-20261115-0001",
        shots_pedido=1024,
        backend="iqs-sim",
        emitido_em="2026-11-15T03:00:00Z",
    )
    dados.update(kw)
    return dados


def test_recibo_tem_todos_os_campos_do_esquema_v2():
    r = intel.montar_recibo_v2("BELL_Z", **base_args())
    obrigatorios = {
        "teste", "veredito", "job_id", "provedor", "backend", "dispositivo",
        "hash_circuito", "shots_pedido", "shots_efetivo", "contagens",
        "hash_resultado_bruto", "versao_imutq", "versao_zyql", "versao_adaptador",
        "proveniencia", "emitido_em", "algoritmo_assinatura",
    }
    assert obrigatorios <= set(json.loads(r.to_json()))
    assert r.teste == "BELL_Z"
    assert r.veredito == "1"
    assert r.provedor == "Intel Quantum SDK"
    assert r.shots_efetivo == 1024


def test_recibo_hashes_sao_calculaveis_de_novo():
    r = intel.montar_recibo_v2("GHZ_3", contagens={"000": 500, "111": 490, "010": 34})
    assert r.hash_circuito == sha3_hex(intel.qasm_canonico("GHZ_3"))
    assert r.hash_resultado_bruto == sha3_hex(canonical({"000": 500, "010": 34, "111": 490}))
    assert r.shots_pedido == 1024 == r.shots_efetivo


def test_recibo_usa_qasm_efetivamente_submetido():
    qasm = intel.qasm_canonico("BELL_Z").replace("barrier q[0],q[1];\n", "")
    r = intel.montar_recibo_v2("BELL_Z", qasm=qasm, **base_args())
    assert r.hash_circuito == sha3_hex(qasm)
    assert r.hash_circuito != sha3_hex(intel.qasm_canonico("BELL_Z"))


def test_recibo_assina_e_confere():
    pk, sk = ML_DSA_44.keygen()
    r = intel.montar_recibo_v2("DJ_balanced", contagens={"111": 1000, "000": 24}, sk=sk, pk=pk)
    ok, msg = r.conferir()
    assert ok, msg
    assert r.assinatura and r.chave_publica


def test_recibo_sem_chave_sai_sem_assinatura():
    r = intel.montar_recibo_v2("BELL_Z", **base_args())
    ok, msg = r.conferir()
    assert not ok and "assinatura" in msg


def test_adulteracao_de_contagem_quebra_o_selo():
    pk, sk = ML_DSA_44.keygen()
    r = intel.montar_recibo_v2("BELL_Z", sk=sk, pk=pk, **base_args())
    r.contagens = {"00": 1, "11": 1, "01": 1, "10": 1}
    ok, msg = r.conferir()
    assert not ok and "hash" in msg


def test_proveniencia_primaria_exige_job_id_da_submissao():
    r = intel.montar_recibo_v2("BELL_Z", **base_args(job_id="iqs-abc"))
    assert r.proveniencia == "primaria"
    assert r.nota_proveniencia is None


def test_sem_job_id_vira_reconstruida_e_nao_inventa_id():
    r = intel.montar_recibo_v2("BELL_Z", **base_args(job_id=None))
    assert r.proveniencia == "reconstruida"
    assert r.job_id == ""
    assert "nao capturado na submissao" in (r.nota_proveniencia or "")


def test_recusa_contagens_vazias():
    with pytest.raises(ValueError):
        intel.montar_recibo_v2("BELL_Z", contagens={})


def test_veredito_refused_entra_no_recibo():
    # p ~ 0.5: dentro da banda, nao ha decisao.
    r = intel.montar_recibo_v2("BELL_Z", contagens={"00": 500, "11": 500, "01": 480, "10": 520})
    assert r.veredito == "REFUSED"


def test_campos_de_versao_tem_paridade_com_o_adaptador_ibm():
    r = intel.montar_recibo_v2("BELL_Z", **base_args())
    assert (r.versao_imutq, r.versao_zyql) == ("0.1.0", "2.5.9")
    assert r.versao_adaptador != "qiskit-ibm-runtime"


def test_montar_lote_um_recibo_por_teste():
    resultados = {
        "BELL_Z": {"00": 512, "11": 512},
        "GHZ_3": {"000": 512, "111": 512},
    }
    lote = intel.montar_lote(
        resultados, job_ids={"BELL_Z": "j-1", "GHZ_3": "j-2"}, shots_pedido=1024
    )
    assert [r.teste for r in lote] == ["BELL_Z", "GHZ_3"]
    assert [r.job_id for r in lote] == ["j-1", "j-2"]
    assert all(r.proveniencia == "primaria" for r in lote)


@pytest.mark.skipif(not BINARIO_RUST.is_file(), reason="binario Rust nao construido")
def test_recibo_montado_passa_no_verificador_rust(tmp_path):
    """Prova de interoperabilidade: heredoc do Python aceito pelo nucleo Rust."""
    pk, sk = ML_DSA_44.keygen()
    recibos = [
        intel.montar_recibo_v2(t, contagens, sk=sk, pk=pk, emitido_em="2026-11-15T03:00:00Z",
                               job_id=f"iqs-{i}", shots_pedido=1024)
        for i, (t, contagens) in enumerate(
            {
                "BELL_Z": {"00": 500, "11": 500},
                "DJ_balanced": {"111": 1000},
            }.items()
        )
    ]
    alvo = tmp_path / "lote_intel.json"
    alvo.write_text(json.dumps([json.loads(r.to_json()) for r in recibos], indent=2),
                    encoding="utf-8")
    r = subprocess.run([str(BINARIO_RUST), "verificar", str(alvo)],
                       capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "0 falhas" in r.stdout


# ---------------------------------------------------------------------------
# A costura com o SDK: pulada enquanto o import falhar
# ---------------------------------------------------------------------------

def test_sem_sdk_nao_ha_submissao():
    """Sem SDK, `submeter` recusa em vez de devolver contagem inventada."""
    if SDK_PRESENTE:
        pytest.skip("SDK presente: este teste cobre a ausencia dele")
    ponte = intel.PonteSDKIntel()
    with pytest.raises(intel.SDKIndisponivel):
        ponte.submeter("BELL_Z")
    with pytest.raises(intel.SDKIndisponivel):
        ponte.executar_e_montar("BELL_Z")


def test_executor_injetado_ensina_o_caminho_completo_sem_sdk():
    """A injecao de executor e o que deixa o caminho inteiro testavel hoje."""
    def executor(qasm: str, shots: int):
        assert qasm == intel.qasm_canonico("BELL_Z")
        assert shots == 256
        return "iqs-fake-1", {"00": 128, "11": 128}

    ponte = intel.PonteSDKIntel(executor=executor, shots=256)
    r = ponte.executar_e_montar("BELL_Z", sk=None, pk=None)
    assert r.job_id == "iqs-fake-1"
    assert r.proveniencia == "primaria"
    assert r.shots_pedido == 256 and r.shots_efetivo == 256
    assert r.veredito == "1"


def test_executor_sem_job_id_e_recusado():
    ponte = intel.PonteSDKIntel(executor=lambda qasm, shots: ("", {"00": 1}))
    with pytest.raises(intel.ErroSDKIntel):
        ponte.submeter("BELL_Z")


def test_executor_com_contagem_de_largura_errada_e_recusado():
    ponte = intel.PonteSDKIntel(executor=lambda qasm, shots: ("j", {"000": 10}))
    with pytest.raises(ValueError):
        ponte.submeter("BELL_Z")


def test_ordem_bits_little_inverte():
    ponte = intel.PonteSDKIntel(
        ordem_bits="little", executor=lambda qasm, shots: ("j", {"01": 4})
    )
    _, contagens = ponte.submeter("BELL_Z")
    assert contagens == {"10": 4}


@precisa_sdk
def test_com_sdk_o_dispositivo_abre():
    ponte = intel.PonteSDKIntel()
    dispositivo = ponte.abrir_dispositivo()
    assert dispositivo is not None
