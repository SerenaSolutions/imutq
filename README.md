# IMUT-Q — plataforma de interoperabilidade quântica com verificação independente

Versão 0.2.0 · 15/11/2026 · Serena Solutions
Licença: Apache-2.0 (ver LICENSE)
Repositório: ainda não publicado.

## O que é

IMUT-Q executa circuitos em provedores quânticos e emite, para cada execução, um
recibo IMUT-Q v2 assinado: integridade (SHA3-256), autenticidade (ML-DSA-44) e
proveniência (job_id capturado na submissão).

## Estado da arte do produto

| Camada | Papel | Estado |
|---|---|---|
| IMUT-Q | interface, compilação, interoperabilidade | EXPERIMENTAL |
| ZYQL / ZEPHIRUM | decisão (1 / 0 / REFUSED) | IMPLEMENTADO |
| IMUT-Q | integridade, autenticidade, proveniência | IMPLEMENTADO (v2) |

## Uso

```
export QISKIT_IBM_TOKEN=...
PYTHONPATH=src python3 -m imutq.cli executar --backend ibm_fez --shots 1024
PYTHONPATH=src python3 -m imutq.cli verificar --recebido receipts/2026-11-15/lote.json
```

## Recibo v2

Campos obrigatórios em RECIBO.md. Regra dura: job_id só entra como proveniência
primaria; vínculo posterior é marcado `reconstruida`.

## Limites conhecidos

1. Assinatura ML-DSA-44 via `dilithium-py`, implementação em Python puro: correta, mas lenta. Uso em escala pede biblioteca nativa.
2. Cota do plano IBM Open: execução limitada; uso comercial exige verificação dos termos.
3. Sem adaptadores para Cirq, QIR, Braket ou Intel nesta versão.
