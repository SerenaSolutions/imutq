# Recibo IMUT-Q v2 — campos

| Campo | Prova |
|---|---|
| job_id | proveniencia primaria (capturado na submissao) |
| provedor, backend, dispositivo | trilha de hardware |
| hash_circuito | o que foi enviado (QASM3) |
| shots_pedido, shots_efetivo | tamanho da amostra |
| contagens | resultado por estado |
| hash_resultado_bruto | resultado nao adulterado |
| versao_multiq, versao_zyql, versao_adaptador | reprodutibilidade |
| hash_payload_canonico | integridade |
| assinatura, algoritmo, chave_publica | autenticidade |
| proveniencia | "primaria" ou "reconstruida" |
