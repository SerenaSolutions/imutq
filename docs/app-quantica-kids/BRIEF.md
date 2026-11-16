# App "Quantum Kids" — especificação de construção

Fonte de conteúdo: livro "Soft Path to Artificial Intelligence — Child Edition"
(74 páginas, bilíngue PT/EN, método "um conceito por página") e o livro
"Ação Fantasmagórica à Distância" (entrelaçamento, 3 páginas de fundamentos).
Vídeos: 4 aulas da série IBM Quantum Learning (Single Systems, Multiple Systems,
Quantum Circuits, Entanglement in Action).

Público: 10 a 15 anos, em português, com opção de inglês.

## Princípio de design

1. Uma ideia por tela. Nunca duas.
2. Nada de fórmula antes do desenho. Primeiro a intuição, depois o nome técnico.
3. Toda lição termina em uma ação: mexer, medir ou responder.
4. Zero texto com mais de três frases por bloco.

## Estrutura do app

1. Boas-vindas, com o personagem-guia e a promessa: "entender o computador mais
   estranho do mundo sem decorar nada".
2. Trilha em quatro partes, na ordem do livro:
   Parte 1 O mundo do computador: bit, byte, memória, processador, algoritmo.
   Parte 2 A rede e a nuvem: internet, dados, nuvem.
   Parte 3 A inteligência artificial: rede neural, treino, modelo, prompt, agente.
   Parte 4 O mundo quântico: qubit, superposição, emaranhamento, porta quântica,
   circuito, medição, decoerência, correção de erro.
3. Lição: bloco de desenho, bloco de texto curto, termo novo destacado e um botão
   "entendi, próximo".
4. Laboratório: simulador de 1 e 2 qubits no navegador.
   a) Moeda mágica: aplicar H, ver 50/50, medir e comparar com a previsão.
   b) Sino de Bell: H no primeiro qubit, CNOT no segundo, duas medições
      correlacionadas. Mostrar que 00 e 11 aparecem e 01 e 10 não.
   c) Contador de repetições: 10, 100 e 1000 medições, com barra de proporção.
5. Glossário vivo: os termos do minidicionário do livro, cada um com desenho,
   definição de uma frase e o link para a lição onde apareceu.
6. Desafio da semana: três perguntas de múltipla escolha, feedback explicando o
   erro, sem punição.
7. Progresso: barra por parte, selos por conceito dominado. Nada de ranking
   público nem comparação entre crianças.

## Entidades sugeridas

1. Licao: numero, parte, titulo, texto, termo, midia, ordem.
2. Termo: palavra, definicao, desenho, licao_origem.
3. Progresso: crianca_id, licao_id, concluida_em, acertos, erros.
4. Desafio: pergunta, alternativas, correta, explicacao_erro.
5. SessaoLab: crianca_id, tipo, resultado, tiragens, criado_em.

## Regras de honestidade pedagógica

1. Não dizer que o qubit "é" uma moeda. Dizer que a moeda é um modelo para começar.
2. Explicar que medir muda o estado, sem misticismo.
3. Não prometer que a criança vai programar hardware quântico: o app ensina conceito.
4. Emaranhamento apresentado como correlação que não depende de mensagem entre as
   partes, nunca como comunicação mais rápida que a luz.
5. Nenhuma coleta de dado pessoal de menor. Sem chat aberto entre crianças.


## O método ZEPHIRUM dentro do app (pedido do dono, 16/11/2026)

O app não ensina quântica "no estilo de vídeo". Ele usa o ZEPHIRUM como método de
aprendizagem. Três peças concretas:

### 1. Três respostas, nunca duas

Toda pergunta do app aceita uma de três respostas: 1, 0 ou REFUSED.

1. 1 é "sei, e consigo mostrar por quê".
2. 0 é "errei, e o app mostra o motivo exato".
3. REFUSED é "não tenho evidência para responder". É resposta legítima, não é erro,
   e a criança nunca é punida por usá-la.

O ganho pedagógico é direto: ensina a criança a distinguir "chutei" de "sei". O botão
REFUSED aparece do lado dos outros dois, com o mesmo peso visual, e a cada uso o app
registra qual informação faltava para que ela pudesse decidir.

### 2. Recibo por conceito dominado

Cada lição concluída gera um recibo selado, como no IMUT-Q: hash SHA3-256 do conteúdo
mais a data, guardado no próprio aparelho. O recibo vira um selo visível na trilha e
pode ser exportado como diploma. Se alguém tentar editar o recibo, o hash não confere e
o app mostra "selo inválido". A criança vê, na prática, para que serve integridade.

Implementação: reaproveitar `sha3.js` e `canonical.js` do IMUT-Q, que já estão
verificados contra os vetores oficiais do NIST.

### 3. Decisão com regra declarada

Exercício "o robô decide": a criança monta uma regra visual (se isto, então 1; se
aquilo, então 0; se não houver dado, REFUSED) e o app testa a regra com casos reais de
qubit. Ela vê que a regra vale para os casos previstos e que o REFUSED existe
justamente para o caso não previsto. É o primeiro contato com a ideia de contrato de
honestidade, sem uma linha de sintaxe.

Versão seguinte: subconjunto visual do ZYQL, com blocos, mostrando a mesma decisão em
texto ao lado do desenho, para quem quiser ver o código por trás.

### O que nunca fazer sob o nome ZEPHIRUM

1. Não chamar o app de "quântico" quando a simulação roda no processador do celular.
   O laboratório é simulador clássico, e o app diz isso na primeira tela do laboratório.
2. Não prometer que criança vai rodar job em hardware quântico real.
3. Não esconder erro atrás de animação bonita: se a resposta é 0, o motivo é dito.

## Faseamento

1. MVP: trilha, 12 lições da Parte 4 e da Parte 1, laboratório da moeda, glossário,
   e o método ZEPHIRUM nas três peças: três respostas, recibo selado, regra declarada.
2. Segunda entrega: sino de Bell, desafios, progresso, inglês.
3. Terceira: modo professor, com roteiro de 45 minutos para sala de aula.

## Arquitetura técnica decidida (16/11/2026)

### Núcleo em Rust, interface em JS

O cálculo não fica no JavaScript. O núcleo vai em Rust, compilado para
`wasm32-unknown-unknown`, embarcado no app. O JavaScript só desenha e capta toque.

Módulos do núcleo:

1. `simulador`: vetor de estado com 1 a 6 qubits, portas H, X, Y, Z, S, T, CNOT, CZ,
   Rx, Ry, Rz, e medição com amostragem semeada (mesma semente, mesmo resultado, o que
   permite repetir a aula e conferir).
2. `selo`: serialização canônica mais SHA3-256, com encadeamento `prev_sha3`, o mesmo
   código do IMUT-Q. Vetores oficiais do NIST já validados.
3. `evidencia`: limites de Wilson e de Hoeffding para decidir se um conceito está
   dominado. É o mesmo raciocínio que a CLI do IMUT-Q já usa para julgar um sino.

Justificativa: já existe toolchain funcionando nesta máquina. O `imutq.wasm` de hoje
saiu com 234 KB, compilou em 2 segundos e verificou sete recibos assinados dentro do
Node. Reaproveitar é mais barato e mais seguro do que reescrever em JS.

### Limite declarado do simulador

Vetor de estado é exato, mas cresce exponencialmente: 2^n amplitudes complexas.
Até 6 qubits, tranquilo em celular modesto. Entre 10 e 12, ainda roda, com atraso
visível. Acima disso, o app não promete nada e diz o motivo. Nada de fingir que
simulou 30 qubits.

### Algoritmos de ensino, e por que cada um

1. *Repetição espaçada com FSRS* (sucessor do SM-2). Cada conceito tem um cartão com
   estabilidade e dificuldade próprias. O app escolhe o que revisar hoje pelo risco de
   esquecimento, não por ordem fixa de capítulo. Isso é o que faz 15 minutos por dia
   valerem mais do que uma hora no domingo.
2. *Dificuldade adaptativa por Elo.* Cada exercício tem uma nota e cada criança tem uma
   nota. Acerto sobe a nota dela, erro desce, e o app serve exercício com ~75% de chance
   de acerto, que é a faixa em que se aprende sem desistir.
3. *Domínio por limite inferior de Wilson.* Conceito dominado não é "acertou 3 de 3".
   É "o limite inferior de 95% da proporção de acertos passou de 0,80 com pelo menos
   N respostas". Três acertos de três dão limite de 0,44 e não bastam. É estatística
   honesta, e a criança não vê número, vê selo.
4. *REFUSED conta como evidência, não como erro.* Quando ela marca REFUSED, o app
   guarda o que faltava e volta ao pré-requisito. Isso é o que diferencia o método
   ZEPHIRUM de um quiz comum.
5. *Amostragem semeada para ensinar probabilidade.* Com 10, 100 e 1000 medições da
   mesma moeda, ela vê a proporção convergir. O núcleo devolve as contagens reais, não
   um número inventado para ficar bonito.

### O que fica de fora, de propósito

1. Não há LLM gerando lição em tempo real. O texto vem do livro e é revisado. Modelo de
   linguagem em app infantil implica risco de alucinação e de conteúdo impróprio sem
   revisor humano.
2. Não há telemetria de menor. Progresso fica no aparelho; exportação é escolha do
   responsável.
3. Não há download de código em tempo de execução. O wasm viaja no pacote, como na
   extensão já publicada.
