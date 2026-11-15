# Extensão Chrome — IMUT-Q Receipt Checker

Verifica recibos de execução quântica direto no navegador: recalcula o SHA3-256 do
payload canônico e mostra veredito, proveniência e origem.

## O que faz

1. Recebe um recibo IMUT-Q colado ou arrastado.
2. Reconstrói o payload assinado, exatamente como o emissor fez.
3. Calcula SHA3-256 em JS puro, validado contra o vetor oficial do NIST.
4. Compara com o hash gravado e mostra integro ou invalido.

## O que não faz (declarado)

1. Não verifica a assinatura ML-DSA-44 no navegador. Isso fica no núcleo Rust. A
   interface diz "assinatura presente" e aponta para a conferência criptográfica.
2. Não se conecta a servidor nenhum. Sem `host_permissions`, sem telemetria.

## Privacidade

Nada sai do navegador. O único armazenamento é a data da última verificação, local.
