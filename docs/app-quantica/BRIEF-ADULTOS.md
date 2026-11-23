# App de computação quântica para adultos — especificação

Versão adulta. A especificação infantil fica guardada em BRIEF-INFANTIL.md como
produto futuro, não como rascunho descartado.

Nome sugerido: *ZYQL Academy*. Alternativa: *Quantum Evidence*.

## Público

1. Profissional de tecnologia que quer entender quântica sem voltar à faculdade.
2. Pesquisador de outra área que precisa ler artigo sem se perder na notação.
3. Gestor técnico que tem de decidir se contrata, se compra ou se espera.
4. Curioso com base de exatas enferrujada, que quer resultado e não entretenimento.

Faixa etária real: 22 a 60. Tom adulto, sem mascote, sem emoji pedagógico, sem
"vamos juntos nessa aventura". Tratamento direto, respeito ao tempo.

## Princípio

1. Uma ideia por tela, com nome técnico desde o começo. Não infantilizar a notação.
2. Toda afirmação tem fonte ou demonstração. Se não tem, é declarada como opinião.
3. Nenhum resultado é mostrado sem dizer o que foi medido e com quantos tiros.
4. O app ensina a conferir, não a acreditar. É a diferença de proposta.

## Trilha em cinco módulos

1. *Fundamentos.* Bit, qubit, amplitude, fase, notação bra-ket, esfera de Bloch.
   Pré-requisito: números complexos em nível de ensino médio, com revisão embutida.
2. *Circuitos.* Portas unitárias, matrizes, composição, reversibilidade, medição e
   colapso. Composer completo a partir daqui.
3. *Emaranhamento e correlação.* Bell, EPR, desigualdade de CHSH, o que a violação
   prova e o que não prova. Aqui entra o texto do livro "Ação Fantasmagórica à
   Distância" como leitura de apoio.
4. *Algoritmos.* Deutsch-Jozsa, Bernstein-Vazirani, Grover, QFT e Shor em nível de
   intuição e de custo. O app mostra por que cada um ganha, e onde perde.
5. *Era pós-quântica e evidência.* Migração para ML-DSA e ML-KEM, o que um recibo de
   execução prova, e o que a verificação independente muda numa auditoria. Este módulo
   é a ponte direta com o IMUT-Q e o ZYQL.

## Método ZEPHIRUM como motor pedagógico

1. *Três respostas.* 1 é "sei e demonstro", 0 é "errei" com o motivo, REFUSED é "não há
   evidência para responder". Em adulto, REFUSED deixa de ser gentileza e vira
   competência: é o que separa o profissional que inventa do que sabe o limite do dado.
2. *Recibo selado por conceito.* Cada módulo concluído emite um recibo com SHA3-256 e
   cadeia de selos, exportável. Serve como credencial verificável, e pode ser conferida
   no verificador público sem instalar nada.
3. *Regra declarada antes do resultado.* Exercícios de decisão no formato 1/0/REFUSED
   com critério escrito antes: por exemplo, dado um conjunto de tiros, decidir se o
   desvio é compatível com o esperado. O aluno escreve a regra, o app testa com dados
   reais e mostra onde a regra falha.
4. *Nada de aprovação sem evidência.* Se o número de tiros é insuficiente para decidir,
   o veredito é REFUSED e o app diz quantos tiros faltariam, usando o mesmo cálculo de
   Hoeffding da CLI do IMUT-Q.

## Composer

1. Quatro a seis qubits, com H, X, Y, Z, S, S†, T, T†, Rx, Ry, Rz, CNOT, CZ, SWAP,
   Toffoli e medição.
2. Estado vivo em painel separado do histograma de tiros, com amplitudes e fases
   visíveis. Fase é mostrada como círculo, não como número solto.
3. Exportação em OpenQASM 2.0 e 3, para o aluno levar o circuito para Qiskit ou qBraid.
4. Botão Selar: circuito e resultado viram recibo assinado com o mesmo esquema do
   IMUT-Q, conferível depois.
5. Se o circuito pedir algo fora do simulador, o veredito é REFUSED com o motivo.
   Nunca resultado aproximado apresentado como exato.

## Avaliação

1. Repetição espaçada com FSRS para retenção.
2. Dificuldade adaptativa por Elo, alvo em torno de 75% de acerto.
3. Domínio por limite inferior de Wilson, acima de 0,80, com mínimo de respostas.
4. Nunca ranking público. Comparação só com o próprio histórico.

## Arquitetura

1. Núcleo em Rust compilado para WebAssembly: simulador, selo e módulo de evidência.
   Prova de viabilidade feita: o núcleo do IMUT-Q compilou hoje para 234 KB e verificou
   sete recibos assinados dentro do Node.
2. Interface no Base44. O wasm viaja no pacote, sem download de código em tempo de
   execução.
3. Progresso no aparelho, com exportação opcional. Nada de telemetria por padrão.
4. Conteúdo em português e inglês, com a mesma estrutura.

## Limites declarados

1. Vetor de estado exato até 6 qubits com folga; 10 a 12 com atraso perceptível.
   Acima disso o app recusa, com explicação.
2. Simulação roda no processador do aparelho. O app nunca chama isso de execução em
   hardware quântico.
3. Sem geração de conteúdo por LLM em tempo real: o texto é revisado e versionado.

## Modelo de negócio, em ordem de facilidade

1. Curso gratuito com dois módulos e recibo básico, para base de usuários.
2. Assinatura individual com os cinco módulos, certificado verificável e composer
   completo.
3. Licença por assento para empresa, com trilha de 8 horas e relatório de progresso
   por equipe, útil para treinamento obrigatório de segurança pós-quântica.

## Faseamento

1. MVP: módulos 1 e 2, composer com 2 qubits, selo de conclusão, revisão de complexos.
2. Segunda entrega: módulo 3 com CHSH interativo e módulo 5 com verificação de recibo.
3. Terceira: módulos 4, exportação QASM, inglês, trilha corporativa.
