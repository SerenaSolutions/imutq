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
