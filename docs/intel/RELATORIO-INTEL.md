# Intel Quantum SDK — relatório de acesso e capacidade

Levantamento de 15/11/2026, fontes oficiais. Cada afirmação marcada como
CONFIRMADO (com URL) ou NÃO CONFIRMADO.

## 1. O que o SDK entrega

| Item | Situação |
|---|---|
| Simulador IQS (Intel Quantum Simulator) | CONFIRMADO, Apache-2.0, github.com/intel/intel-qs |
| Backend de hardware Tunney/T12 | CONFIRMADO como indisponível: a documentação v1.1 declara disponibilidade "no futuro" |
| API C++ com `quantum_kernel` | CONFIRMADO |
| Compilador `-B` (QASM para C++) | CONFIRMADO |
| Dialeto "intelqasm" | REFUTADO: não existe na documentação oficial |
| OpenQASM 2.0 como entrada | CONFIRMADO, único dialeto aceito |
| OpenQASM 3, QIR, MLIR | CONFIRMADO como ausente: nenhuma menção nas 60+ páginas oficiais |

Consequência para o IMUT-Q: todo recibo de origem Intel será de simulação. O campo
`proveniencia` deve dizer `simulada_sdk`, nunca `hardware`, sob pena de quebrar o
contrato de honestidade.

## 2. Acesso

CONFIRMADO: o cadastro no Intel Developer Cloud exige e-mail corporativo em domínio
próprio. Gmail e afins são recusados. É exatamente o bloqueio atual do projeto.

Caminho alternativo CONFIRMADO e sem cadastro: o IQS de código aberto compila local e
serve como backend de simulação. Não é o SDK completo, mas é o motor de estado.

## 3. qBraid como rota de laboratório

CONFIRMADO pelo ambiente aprovado `intelqsdk` no Quantum Lab do qBraid, porém apenas
em notebook interativo. A API REST não expõe dispositivo Intel: a lista de 40
dispositivos não contém nenhum, e `cost-estimate` com dispositivo Intel devolve
dispositivo não encontrado. Perfil Small Intel listado a 12 créditos por hora.

## 4. Rota mais curta para o primeiro circuito Intel

1. Compilar o IQS localmente (Apache-2.0, sem cadastro).
2. Emitir QASM 2.0 do ZYQL para os seis circuitos canônicos.
3. Traduzir com `-B` para C++ e linkar com o IQS.
4. Selar recibo com `provedor=Intel`, `backend=iqs`, `proveniencia=simulada_sdk`,
   e `job_id` = hash do binário compilado mais o seed do simulador, já que não há
   job remoto. Essa é uma decisão de esquema a registrar.

## 5. Bloqueios

| Bloqueio | Natureza | Contorno |
|---|---|---|
| E-mail corporativo exigido | cadastral | domínio próprio (imutq.com.br, livre, cerca de R$ 40/ano) |
| Sem backend de hardware | do fornecedor | recibo marcado como simulação |
| Só QASM 2.0 | técnico | emissor QASM 2.0 no adaptador (feito) |
| qBraid só interativo | comercial | nenhum; API não serve para Intel |
