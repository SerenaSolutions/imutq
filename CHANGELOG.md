## [0.2.1] - 2026-11-15

### Corrigido
- Popup le a data da ultima verificacao no `chrome.storage.local` e mostra no rodape.
  Antes a permissao `storage` era usada so na escrita, sem leitura visivel, o que
  deixava a justificativa de permissao sem contrapartida na interface.
- Rotulos, dica do campo, legenda de veredito e mensagem de integridade localizados
  em ingles e portugues, por `navigator.language`. Quem abre em ingles ve a interface
  em ingles, sem depender de traducao de pagina.
- Legenda dos vereditos: 1, 0 e REFUSED explicados em uma linha.
- Resumo de lote: "N recibos — X integros" quando mais de um recibo e colado.
- Rodape com versao visivel e link para a politica de privacidade.

### Adicionado
- Icones 16, 32 e 48 no manifest, alem do 128, para a barra de ferramentas.

### Estado
- NAO submetida a Edge Add-ons. A versao em revisao continua a 0.2.0.
- Pacote: `extension-0.2.1.zip`.

## [0.7.0] - 2026-11-15

### Adicionado
- Núcleo Rust refatorado em biblioteca (`src/lib.rs`, `canonica`, `verificacao`), usada pela CLI e pelo navegador.
- Compilação para WebAssembly (`wasm32-unknown-unknown`, 234 KB) com ABI simples: `alocar`, `liberar`, `verificar`.
- Extensão 0.2.0: verifica a assinatura ML-DSA-44 dentro do navegador, sem servidor. CSP com `wasm-unsafe-eval`.
- `fips204` sem `default-rng`: só verificação, sem gerador de chaves, o que remove a dependência de `getrandom` no wasm.
- Site público com política de privacidade: https://serenasolutions.github.io/imutq-site/

### Verificado
- Wasm: recibo íntegro devolve 1, adulterado devolve 0, json inválido devolve -1, lote qBraid devolve 1 nos sete.
- Popup testado em DOM simulado: renderiza REFUSED e "assinatura ML-DSA-44 CONFIRMADA".

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
