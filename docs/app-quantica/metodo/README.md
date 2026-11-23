# Núcleo do método ZEPHIRUM para o app

Crate Rust `metodo`, sem dependência de servidor, compilável para WebAssembly.

## O que faz

1. `wilson_inferior(acertos, total, z)`: limite inferior do intervalo de confiança de
   Wilson. É a régua que impede "acertou 3 de 3, dominou".
2. `decidir(acertos, total, limiar, minimo)`: devolve Dominado, EmProgresso ou
   Insuficiente. O terceiro estado é o REFUSED do método aplicado ao ensino.
3. `respostas_faltantes(...)`: quantas respostas faltam para sustentar domínio no ritmo
   atual. O app mostra isso ao aluno em vez de dizer "tente de novo".
4. `proxima_revisao_dias(estabilidade, acertou)`: agendamento no espírito do FSRS.
5. `selar_recibo(...)`: hash SHA3-256 do recibo canônico, encadeado no anterior.

## Números reais medidos

```
3/3   -> limite 0.439 | Insuficiente
8/10  -> limite 0.490 | Insuficiente
12/12 -> limite 0.758 | Insuficiente
16/16 -> limite 0.806 | Dominado
20/20 -> limite 0.839 | Dominado
20/25 -> limite 0.609 | EmProgresso
faltam para 3/3: 13 respostas
```

## Testes

Sete testes passando: 3/3 não é domínio, 20/20 é, metade das respostas nunca é domínio
em nenhuma amostra, monotonia do limite com o tamanho da amostra, contagem de faltantes
fechando o ciclo, recibo sensível a qualquer alteração, e revisão crescendo no acerto e
caindo no erro.

## Integração com o app

O app consome este crate por WebAssembly. Nenhuma regra de aprovação é reescrita em
JavaScript: se a criança ou o adulto vê "dominado", foi este código que decidiu.
