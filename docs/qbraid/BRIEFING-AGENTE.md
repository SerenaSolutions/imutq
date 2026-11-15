# Briefing para o agente do qBraid Lab — trabalho no ZEPHIRUM/ZYQL

Pacote de comando. Cole o bloco do item 1 no chat do agente do qBraid Lab.
O item 2 e o formato de relatorio que ele precisa devolver.
O item 3 e o que eu faco com o que voltar.

## 1. Bloco de comando

Voce atua como executor tecnico subordinado a Serena Solutions no projeto IMUT-Q
(antes MultiQ), camada de verificacao de resultados quanticos. O nucleo do produto
e Rust e verifica recibos v2 assinados em ML-DSA-44. Voce nao decide veredito nem
calcula hash: voce produz resultados brutos e devolve para selagem no nucleo.

Regras nao negociaveis:

1. Nao copie codigo de terceiros para o repositorio. Inspecione, cite a origem e
   reescreva do zero.
2. Todo resultado vem com: comando executado, saida literal, versao do pacote,
   tempo, e identificador do job quando existir.
3. Nunca reporte simulacao como hardware. Se rodou em simulador, escreva simulador.
4. Nunca gaste credito sem autorizacao. Se o custo estimado for maior que zero,
   pare e reporte o valor.
5. Nao invente contagens. Se falhou, reporte a mensagem literal da API.
6. Autoria e metadados sempre "Serena Solutions".
7. Escreva IMUT-Q com hifen e Q maiusculo.

Tarefas, em ordem de prioridade:

T1. Confirmar o schema de job da API do qBraid e registrar o corpo exato aceito para
    qasm3, qasm2, qir.bc e qir.ll. Para cada formato: um exemplo minimo e o status
    HTTP real.

T2. Rodar BELL_Z em qasm3 e em qir.bc no dispositivo qbraid:qbraid:sim:qir-sv.
    Comparar as contagens. Se qir.bc for aceito, esse e o caminho de interoperabilidade
    QIR do IMUT-Q: documente o passo a passo.

T3. Rodar os seis circuitos canonicos (BELL_Z, BELL_X, DJ_balanced, DJ_constant,
    GHZ_3, IDENTITY) em qir-sv, 1024 tiros cada, e devolver as contagens brutas.

T4. Repetir GHZ_3 com 100, 1024 e 4096 tiros no mesmo simulador e medir como a
    distribuicao converge. Reportar desvio por estado.

T5. Verificar quais dos dispositivos ONLINE aceitam qasm2 sem erro de formato,
    testando com um circuito de 1 qubit e 1 porta.

T6. Testar o emissor QASM 2.0 do adaptador Intel contra as restricoes do SDK:
    sem QASM 3, sem portas fora de u1/u2/u3/cx, declaracao de qreg/creg explicita.
    Apontar cada porta dos seis circuitos que precisaria reescrita.

T7. Se o ambiente intelqsdk estiver disponivel no Lab, rodar BELL_Z no IQS e devolver
    versao, commit quando possivel, e contagens. Se nao estiver, reportar o bloqueio
    com a mensagem literal.

T8. Propor, sem implementar, um teste de fidelidade entre qir-sv e IQS para o mesmo
    circuito, com o criterio estatistico explicito.

## 2. Formato de relatorio (devolver a cada bloco de tarefas)

```
TAREFA: T<n>
ESTADO: IMPLEMENTADO | EXPERIMENTADO | ESPECIFICACAO | BLOQUEADO
COMANDO:
SAIDA: (literal, sem resumo)
JOB_ID:
DISPOSITIVO:
SHOTS:
CUSTO:
VERSAO_PACOTE:
TEMPO:
OBSERVACAO:
```

Ao final de cada rodada, devolva um JSON unico com essas chaves por tarefa. Sem
JSON, o resultado nao entra no recibo.

## 3. O que eu faco com o retorno

1. Confiro o JSON contra o schema do recibo v2.
2. Selo com SHA3-256 e assino em ML-DSA-44.
3. Verifico com o nucleo Rust (`imutq verificar`), que nao depende do seu ambiente.
4. Registro no repositorio com proveniencia primaria e job_id capturado na submissao.

## 4. O que nao pedir a ele

1. Nada que exija cartao ou credito pago.
2. Nada de hardware real sem conta Open Quantum vinculada: a mensagem literal e
   "Open Quantum account not connected".
3. Nada de decisao de arquitetura. Ele executa; quem decide e o nucleo.
