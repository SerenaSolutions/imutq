# Varredura qBraid — 15/11/2026

Circuito BELL_Z em OpenQASM 3, 1024 tiros, submetido a todos os 21 dispositivos ONLINE
via API REST. Custo total: 0.

## Executaram (7, simuladores)

| Dispositivo | Contagens | Veredito |
|---|---|---|
| qbraid:qbraid:sim:qir-sv | 00:498 11:526 | 1 |
| ionq:ionq:sim:simulator | 00:512 11:512 | 1 |
| qbraid:quobly:sim:alloy-forge | 00:491 11:506 01:2 10:1 | 0 |
| qbraid:qbraid:sim:gpu-sv | 00:509 11:515 | 1 |
| qbraid:qbraid:sim:gpu-tn | 00:490 11:534 | 1 |
| qperfect:qperfect:sim:mimiq-sv | 00:537 11:487 | 1 |
| qperfect:qperfect:sim:mimiq-mps | 00:481 11:543 | 1 |

O alloy-forge é o único que vaza para fora do suporte de Bell, coerente com ser
simulador que aplica modelo de ruído. Veredito 0 registrado como está, sem maquiagem.

## Não executaram

| Bloqueio | Dispositivos |
|---|---|
| Conta Open Quantum não vinculada | 6 QPUs (AQT ibex-q1, IonQ forte-1 e forte-enterprise, IQM emerald e garnet, Rigetti cepheus) |
| Créditos insuficientes, 0 disponíveis | AWS sv1 (0,38), AWS dm1 (1,99), IonQ Forte-1 (8.222,00) |
| Só aceita entrada Qiskit | 4 IBM (marrakesh, kingston, miami, boston) |
| Só aceita braket_ahs | QuEra Aquila (atômico, precisa de programa AHS) |

## Recibos

`receipts/2026-11-15/qbraid-assinados.json` com 7 recibos, `provedor=qBraid`,
`job_id` = jobQrn capturado na submissao, assinados em ML-DSA-44 e verificados pelo
nucleo Rust: 7 recibos, 0 falhas.
