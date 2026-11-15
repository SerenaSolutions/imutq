# Adaptador Intel — contrato

`src/imutq/adapters/intel.py` gera o dialeto aceito pelo Intel Quantum SDK e monta o
recibo v2 a partir de contagens vindas do SDK. Estado: IMPLEMENTADO o emissor e o
montador; ESPECIFICAÇÃO a execução real no SDK, ainda bloqueada por cadastro.

## Fronteira

O adaptador nunca decide veredito nem calcula hash. Ele emite QASM 2.0 e devolve as
contagens ao núcleo, que sela e verifica. Sem o SDK instalado, o import continua
funcionando: `sdk_disponivel()` devolve False e os testes de integração são pulados.

## Circuitos cobertos

BELL_Z, BELL_X, DJ_balanced, DJ_constant, GHZ_3, IDENTITY. Cada um tem teste de texto
QASM esperado, que roda sem SDK, e um teste de integração marcado como skip.

## Quando o acesso sair

1. Compilar com `-B` o QASM gerado.
2. Linkar com o IQS.
3. Passar as contagens por `montar_recibo()` com `provedor="Intel"`,
   `backend="iqs"` e `proveniencia="simulada_sdk"`.
4. Conferir com `imutq verificar`, que não depende do SDK.

## Suíte

48 testes passando, 1 pulado (integração que exige SDK).
