## [0.3.2] - 2026-11-15

### Adicionado
- `tools/assinar_intel.py`: ingere contagens do Intel IQS vindas em arquivo e emite
  recibo v2 com `proveniencia=reconstruida`, porque nao existe job remoto no SDK.
- Primeiro recibo Intel: BELL_Z, 200 tiros, veredito REFUSED.

### Decidido
- Quando duas regras plausiveis discordam sobre a mesma entrada (suporte estrito da 0,
  TVD de 0,05 da 1), o veredito e REFUSED. A regra tem que ser declarada antes do dado,
  nao escolhida depois.

## [0.3.1] - 2026-11-15

### Adicionado
- Adaptador Intel (`src/imutq/adapters/intel.py`) emitindo QASM 2.0 para os seis circuitos canônicos, com recibo marcado como `simulada_sdk`. 48 testes verdes, 1 skip de integração.
- Varredura qBraid: BELL_Z em 21 dispositivos ONLINE, 7 simuladores executados a custo zero, 7 recibos assinados e verificados pelo núcleo Rust.
- `tools/assinar_qbraid.py`: transforma a varredura bruta em recibos de proveniência primária, com julgamento por 5 sigma binomial.
- `docs/intel/` (relatório de acesso, contrato do adaptador) e `docs/qbraid/VARREDURA.md`.

### Corrigido
- `sdk_disponivel()` chamava `next()` sobre o retorno de `_importar_sdk`, que já devolve o módulo.

### Refutado
- Não existe dialeto "intelqasm". O SDK aceita QASM 2.0 e nada de QASM 3, QIR ou MLIR.
- O SDK não tem backend de hardware: Tunney e T12 estão declarados como futuros.

## [0.3.0] - 2026-11-15

### Adicionado
- Núcleo Rust verifica recibo v2 completo: payload canônico, SHA3-256 e ML-DSA-44
  via `fips204`, sem depender do Python.
- Comando `imutq verificar <arquivo...>`; aceita lista, objeto com `recibos` ou recibo único.
- Interoperabilidade provada: recibo assinado por `dilithium-py` verificado por `fips204`.
- ARCHITECTURE.md com a stack oficial (Rust núcleo, Python adaptador, C/C++, LLVM/MLIR, QIR, OpenQASM 3).

### Corrigido
- `Cargo.toml` apontava para `LICENSE-COMERCIAL.md`, arquivo removido no commit Apache-2.0.

## [0.2.0] - 2026-11-15

### Alterado
- Nome do produto e do pacote: IMUT-Q (pronuncia "imutique"). Repositorio unico com
  o verificador em Rust (`rust/`) e o motor de execucao em Python (`src/imutq/`).
- Campo de versao renomeado no codigo para `versao_imutq`; o payload assinado no
  esquema 2.0 preserva `versao_multiq` para nao invalidar recibos ja emitidos.

## [0.1.0] - 2026-11-15

### Adicionado
- Execucao em hardware IBM com job_id capturado na submissao.
- Recibo v2 assinado em ML-DSA-44, com hash de circuito e de resultado bruto.
- Verificador que rejeita recibo sem assinatura.
- Primeiro lote: BELL_Z e DJ_balanced no ibm_fez, 1.024 tiros cada.
