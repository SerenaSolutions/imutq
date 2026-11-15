# Recibo IMUT-Q v2 — campos

| Campo | Prova |
|---|---|
| job_id | proveniencia primaria (capturado na submissao) |
| provedor, backend, dispositivo | trilha de hardware |
| hash_circuito | o que foi enviado (QASM3) |
| shots_pedido, shots_efetivo | tamanho da amostra |
| contagens | resultado por estado |
| hash_resultado_bruto | resultado nao adulterado |
| versao_imutq, versao_zyql, versao_adaptador | reprodutibilidade |
| hash_payload_canonico | integridade |
| assinatura, algoritmo, chave_publica | autenticidade |
| proveniencia | "primaria" ou "reconstruida" |

## Nome do campo de versao (esquema 2.0)

O recibo de 15/11/2026 gravou o campo como `versao_multiq`. O esquema 2.0 congela
esse nome, porque renomear mudaria o payload canonico e invalidaria a assinatura
ja emitida. No codigo o campo se chama `versao_imutq`; o rename no esquema entra
apenas na v3, com recibos novos.

## Limite da assinatura

A assinatura ML-DSA-44 prova *quem emitiu* e que o conteudo nao mudou. Nao prova que o
calculo esta correto, nem que houve hardware quantico, nem endosso de fornecedor.
Manter as tres alegacoes separadas: `veredito` (resultado), `proveniencia` (origem),
`assinatura` (emissor).

## Campos propostos para a v3

Ainda nao implementados. Entram so em recibos novos, com esquema declarado.

| Campo | Para que serve |
|---|---|
| versao_simulador, commit_simulador | reprodutibilidade do ambiente |
| hash_programa_original, hash_programa_executado | separa o que escrevemos do que rodou |
| transpilacoes | lista de transformacoes aplicadas |
| seed, modelo_ruido | condicoes de execucao |
| ordem_bits | convencao de leitura das contagens |
| tolerancia, metodo_comparacao | como o veredito foi decidido |
| emissor | identidade de quem assinou |
