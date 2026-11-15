# Submissão Microsoft Edge — IMUT-Q Receipt Checker v0.2.0

Cópia dos textos usados no Partner Center. Fonte de verdade para reedições futuras.
Autor: Serena Solutions · Estado: pacote verificado (Complete), submissão em andamento.

## Propriedades

- Categoria: Developer Tools
- Website: https://serenasolutions.github.io/imutq-site/
- Support URL: https://serenasolutions.github.io/imutq-site/suporte.html
- Privacy policy: https://serenasolutions.github.io/imutq-site/privacidade.html
- Mature content: desmarcado

## Single purpose

Verify the integrity and authenticity of execution receipts issued by the IMUT-Q platform. The extension recomputes the SHA3-256 hash of the receipt content and verifies the post-quantum ML-DSA-44 signature, displaying the verdict (1, 0 or REFUSED), provider, backend, job identifier, shot count and declared provenance. It performs no other function, does not access web pages and does not communicate with any server.

## Justificativa da permissão storage

The storage permission is used only to record, in the browser's local storage, the date and time of the most recent verification. Its sole purpose is to show the user when a receipt was last checked. No data is transmitted to any server, shared with third parties or used for tracking, and the record is deleted when the extension is removed.

## Remote code

Resposta: No, I am not using remote code.

All executed code ships inside the submitted package, including the ML-DSA-44 verifier compiled to WebAssembly (ml_dsa_44.wasm). There is no remote script, external module, eval call or runtime code download.

## Uso de dados

Nenhuma caixa de coleta marcada. Três certificações marcadas:
não vende nem transfere dados a terceiros; não usa dados fora da finalidade única; não usa dados para crédito ou empréstimo.

## Store listing (en)

Name: IMUT-Q Receipt Checker

Short description: Verify post-quantum execution receipts in your browser: SHA3-256 integrity and ML-DSA-44 signature.

Full description:

Quantum execution receipts record what ran, where and with which result. This extension checks whether a receipt was altered after it was issued.

It rebuilds the canonical payload, recomputes the SHA3-256 hash on your machine and verifies the post-quantum ML-DSA-44 signature with the same Rust core compiled to WebAssembly. Nothing leaves your browser.

You see the verdict (1, 0 or REFUSED), provider, backend, job identifier, shot count, declared provenance and signature status.

Declared limit: the extension verifies integrity and authenticity of receipts. It does not prove that the underlying quantum computation is physically correct, and simulation is never presented as hardware.

No account, no server, no tracking, no ads.

Search terms: quantum, receipt, sha3, ml-dsa, post-quantum, integrity, verification, imut-q

## Pendências

Capturas de tela 1280x800 (mínimo 1, máximo 4) e ícone 128x128 no Store listing, depois Publish.
