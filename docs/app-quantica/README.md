# Produto: apps de aprendizagem quântica

Duas trilhas, um núcleo. Nada foi descartado: a versão infantil virou produto próprio.

## Trilha A — ZYQL Academy (adulta, prioridade atual)

Público: 22 a 60 anos, técnico ou adjacente. Cinco módulos: fundamentos, circuitos,
emaranhamento, algoritmos, era pós-quântica com verificação de recibo.
Especificação: `BRIEF-ADULTOS.md`.
Proposta de valor: certificado verificável, composer com selo, e o único módulo que
ensina a conferir resultado em vez de acreditar nele.

## Trilha B — Quantum Kids (infantojuvenil, segunda entrega)

Público: 10 a 15 anos. Base: livro "Soft Path to Artificial Intelligence, Child Edition"
(74 páginas, bilíngue, um conceito por página, minidicionário ilustrado) e as quatro
aulas em vídeo da série IBM Quantum Learning.
Especificação: `BRIEF-INFANTIL.md`.
Laboratório: moeda mágica com H e medição, sino de Bell com duas medições
correlacionadas, e contador de 10, 100 e 1000 tiros para ver a proporção aparecer.

## Núcleo compartilhado

1. Simulador, selo SHA3-256 e módulo de evidência em Rust, compilados para WebAssembly.
   Comprovado nesta máquina: 234 KB, verificação de sete recibos assinados.
2. Método ZEPHIRUM em três peças: três respostas (1, 0, REFUSED), recibo por conceito,
   regra declarada antes do resultado.
3. Composer de circuitos, mais simples na trilha infantil, completo na adulta.
4. Conteúdo próprio. Material da IBM e do livro entram como referência e como link, não
   como cópia embarcada. Ver `COBERTURA-IBM.md`.

## Conteúdo já escrito

`conteudo/modulo-1/licao-01-qubit.md`: qubit com formalização, esfera de Bloch, portas
como rotações, medição, não clonagem e três perguntas de verificação.

## Bloqueio único

Criar o app exige o ambiente do Base44. Não há ferramenta nesta sessão que crie app do
zero. Passo do dono: abrir https://app.base44.com, criar o app, e avisar. A partir daí a
construção é feita pelo construtor, com esta especificação.
