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
