# Módulo 1 · Lição 1 — O que é um qubit

## Ideia única

Um bit guarda um de dois valores. Um qubit guarda um vetor de comprimento unitário em um
espaço de duas dimensões complexas. A diferença não é "dois ao mesmo tempo": é que o
estado tem direção, e a direção carrega informação que o bit não tem.

## Formalização

Estado: |ψ⟩ = α|0⟩ + β|1⟩, com α e β complexos e |α|² + |β|² = 1.

α e β são amplitudes, não probabilidades. Probabilidade é |α|² e |β|², e só aparece na
medição. Antes de medir, não existe valor escondido: existe direção.

Um fator de fase global (e^{iθ} multiplicando tudo) não tem efeito observável. Fase
relativa entre α e β tem, e é o que portas como S e T alteram.

## Geometria

Todo estado puro de um qubit corresponde a um ponto na esfera de Bloch: eixo z para
|0⟩ e |1⟩, eixo x para superposições com fase 0 e π, eixo y para fase ±π/2. A esfera
não é enfeite: distância angular na esfera é mensurável em experimento.

## Portas como rotações

1. X: rotação de π em torno de x. Troca |0⟩ e |1⟩.
2. H: rotação de π em torno do eixo (x+z)/√2. Leva |0⟩ para (|0⟩+|1⟩)/√2.
3. Z: rotação de π em torno de z. Muda a fase relativa, não as probabilidades.
4. S e T: rotações de π/2 e π/4 em torno de z.

Toda porta de um qubit é uma matriz unitária 2x2. Unitária significa que preserva o
comprimento do vetor, e é por isso que a evolução quântica é reversível.

## Medição

Medir em z devolve 0 com probabilidade |α|² e 1 com |β|². Depois da medição o estado
colapsa no resultado obtido, e medir de novo dá o mesmo valor. Medir em outra base é
possível e muda o resultado, o que mostra que a base faz parte do experimento.

## Por que isso não é só marketing

Três consequências concretas:

1. Não dá para copiar um estado quântico desconhecido. O teorema da não clonagem é o que
   sustenta a criptografia quântica.
2. Dois qubits podem estar correlacionados de forma que nenhum modelo de variável oculta
   local reproduz. Isso é medido, não postulado, pela violação de Bell.
3. Erro é contínuo, não discreto. Um qubit desvia aos poucos, e por isso correção de erro
   quântica codifica um qubit lógico em muitos físicos.

## Verificação de compreensão

Pergunta 1. Se α = 1/2, qual é a probabilidade de medir 0?
Resposta: 0,25. E o estado não é normalizável com esse α sozinho: β teria de ser √3/2.

Pergunta 2. Aplicar Z em (|0⟩+|1⟩)/√2 e medir em z muda a distribuição?
Resposta: não. Z só muda a fase relativa, e a medição em z ignora fase.

Pergunta 3. Aplicar H duas vezes em |0⟩ devolve o quê?
Resposta: |0⟩. H é a própria inversa, porque H² = I.

## Erro comum a evitar

Dizer que o qubit "é 0 e 1 ao mesmo tempo". O enunciado correto é que o estado é uma
superposição com amplitudes definidas, e a medição devolve um valor só. Quem ensina a
frase errada cria a expectativa de que medir revela algo que já estava lá.
