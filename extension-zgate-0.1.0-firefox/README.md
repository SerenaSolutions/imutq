# Z-Gate — gate de envio com recibo

Antes de o Gmail enviar, o Z-Gate avalia a mensagem e devolve *1*, *0* ou *RECUSADO*,
com recibo selado em SHA3-256 e encadeado no anterior.

## Politica declarada (antes do dado, nunca depois)

| Regra | Condicao | Efeito |
|---|---|---|
| R1 | sem destinatario valido | 0 |
| R2 | assunto vazio | REFUSED |
| R3 | corpo vazio | 0 |
| R4 | CPF no corpo | 0 |
| R5 | sequencia compativel com cartao | 0 |
| R6 | anexo presente | REFUSED |
| R7 | imagem embutida | REFUSED |
| R8 | cadeia de selos quebrada | REFUSED |

Precedencia: qualquer 0 vence. Sem 0, qualquer REFUSED vence. Sem nenhum dos dois, 1.

## O que o gate nao faz

1. Nao le anexo nem imagem: por isso RECUSA, em vez de aprovar sem evidencia.
2. Nao envia nada para servidor. Roda inteiro no navegador, Manifest V3, sem codigo remoto.
3. Nao bloqueia de forma absoluta: o usuario pode enviar contra o gate, e o override e
   registrado como veredito FORCADO, com selo proprio.

## Permissoes

1. storage: guardar os recibos das decisoes.
2. host mail.google.com: unico site em que atua, exigido para interceptar o envio.

## Testes do motor de politica

limpo para 1, sem destinatario para 0, CPF para 0, anexo para REFUSED, assunto vazio
para REFUSED, cadeia quebrada para REFUSED.
