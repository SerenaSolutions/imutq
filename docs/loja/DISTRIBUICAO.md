# Onde publicar sem pagar taxa

| Loja | Taxa de desenvolvedor | Aceita nosso pacote | Observacao |
|---|---|---|---|
| Chrome Web Store | 5 dolares, taxa unica | sim | bloqueado por falta de cartao internacional |
| Microsoft Edge Add-ons | sem taxa | sim, o mesmo zip do Chrome | cadastro no Partner Center; aceita Manifest V3 |
| Firefox (addons.mozilla.org) | sem taxa | precisa variante | usa background.scripts e exige gecko.id |
| Opera Add-ons | sem taxa | sim, zip do Chrome | alcance menor, revisao humana |
| Safari | exige conta Apple de 99 dolares por ano | nao | fora de escopo |

## Pacotes gerados

1. `extension-zseal-0.1.0.zip` e `extension-zgate-0.1.0.zip` — Chrome e Edge.
2. `extension-zseal-0.1.0-firefox.zip` e `extension-zgate-0.1.0-firefox.zip` — Firefox, com
   `background.scripts` e `browser_specific_settings.gecko.id`.

## Caminho sem gastar nada

1. Registrar conta gratuita no Partner Center da Microsoft e publicar os dois pacotes no Edge.
2. Registrar conta no addons.mozilla.org e publicar as variantes Firefox.
3. Manter o zip do Chrome pronto para quando o cartao internacional existir.

## Aviso de honestidade

A verificacao de "sem taxa" foi feita nas paginas oficiais em 15/11/2026. Taxa e politica de
cadastro mudam; conferir na hora de submeter.
