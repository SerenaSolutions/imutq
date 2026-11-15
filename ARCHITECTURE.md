# Arquitetura — IMUT-Q (imutique)

Decisão de arquiteto, 15/11/2026: Rust é o núcleo permanente. Nenhuma migração.

## Stack oficial

| Tecnologia | Função | Estado |
|---|---|---|
| Rust | núcleo principal: decisão, recibo, verificação, ML-DSA-44 | IMPLEMENTADO |
| Python | adaptadores Qiskit/Cirq e bibliotecas científicas | IMPLEMENTADO |
| C / C++ | interoperabilidade com SDKs de baixo nível | ESPECIFICAÇÃO |
| LLVM / MLIR | compilação e otimização de circuitos e IR | ESPECIFICAÇÃO |
| QIR | interoperabilidade com o ecossistema Microsoft | ESPECIFICAÇÃO |
| OpenQASM 3 | intercâmbio de circuitos | IMPLEMENTADO (saída) |

## Fronteiras

1. Rust é dono do veredito (1 / 0 / REFUSED), do payload canônico, do SHA3-256 e da
   verificação ML-DSA-44. Nenhum adaptador decide veredito nem calcula hash.
2. Python submete circuitos e monta candidatos a recibo. Ele propõe; o núcleo sela.
3. C/C++ entra por ABI estável apenas quando houver SDK que exija isso (Intel).
4. LLVM/MLIR e QIR são rota de compilação, não de verificação.
5. OpenQASM 3 é o formato de intercâmbio declarado no hash_circuito.

## Por que Rust

Desempenho de C/C++ com segurança de memória, concorrência sem corrida de dados,
binário nativo multiplataforma e boa base para múltiplos backends. Um produto cuja
tese é integridade não pode ter o verificador escrito em linguagem que estoure
buffer.

## Prova de interoperabilidade entre implementações

O mesmo recibo assinado pelo adaptador Python (`dilithium-py`, ML-DSA-44) foi
verificado pelo núcleo Rust (`fips204`), sem conversão de formato:

```
./rust/target/release/imutq verificar receipts/2026-11-15/lote.json
OK    BELL_Z: integro e assinado
OK    DJ_balanced: integro e assinado
2 recibos, 0 falhas
```

Duas implementações independentes concordando é o que separa "nós assinamos" de
"qualquer um pode conferir".

## Congelamento de esquema

O recibo v2.0 grava o campo `versao_multiq`. O código usa `versao_imutq`. O payload
assinado preserva o nome antigo; o rename entra no esquema v3, com recibos novos.
Renomear agora invalidaria as assinaturas já emitidas.
