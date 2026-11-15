# SPDX-License-Identifier: LicenseRef-Serena-Commercial-1.0
# Copyright (c) 2026 Serena Solutions
"""Adaptador IBM: submete e captura job_id na submissao, nunca depois."""
from __future__ import annotations
import hashlib, json, os
from qiskit import QuantumCircuit, qasm3, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
from .receipt import ReciboV2, canonical, sha3_hex

BANDA = 0.15
VERSAO_MULTIQ = "0.1.0"
VERSAO_ZYQL = "2.5.9"
VERSAO_ADAPTADOR = "qiskit-ibm-runtime"


def bell_witness() -> QuantumCircuit:
    qc = QuantumCircuit(2, 2)
    qc.h(0); qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])
    return qc


def dj_balanced(n: int = 3) -> QuantumCircuit:
    qc = QuantumCircuit(n + 1, n)
    qc.x(n); qc.h(range(n + 1))
    for i in range(n):
        qc.cx(i, n)
    qc.h(range(n))
    qc.measure(range(n), range(n))
    return qc


def _counts(res, key) -> dict:
    return {k: int(v) for k, v in res.data.__getattribute__(key).get_counts().items()}


def executar(backend_nome: str, shots: int, sk=None, pk=None, destino="receipts") -> list[ReciboV2]:
    svc = QiskitRuntimeService(channel="ibm_quantum_platform",
                               token=os.environ["QISKIT_IBM_TOKEN"], instance="auto")
    backend = svc.backend(backend_nome)
    sampler = SamplerV2(mode=backend)
    pt = backend.processor_type or {}
    dispositivo = f"{pt.get('family','?')} r{pt.get('revision','?')}"
    recibos: list[ReciboV2] = []

    casos = [("BELL_Z", bell_witness(), lambda c: (c.get("00", 0) + c.get("11", 0)) / sum(c.values())),
             ("DJ_balanced", dj_balanced(), lambda c: sum(v for k, v in c.items() if k.strip("0")) / sum(c.values()))]

    for nome, qc, pfun in casos:
        alvo = transpile(qc, backend=backend, optimization_level=1)
        qasm = qasm3.dumps(alvo)
        job = sampler.run([alvo], shots=shots)          # job_id nasce aqui
        job_id = job.job_id()
        res = job.result()[0]
        contagens = _counts(res, "c" if "c" in res.data else "meas")
        total = sum(contagens.values())
        p = pfun(contagens)
        veredito = "1" if p >= 1 - BANDA else ("0" if p <= BANDA else "REFUSED")
        r = ReciboV2(
            teste=nome, veredito=veredito, job_id=job_id, provedor="IBM Quantum",
            backend=backend.name, dispositivo=dispositivo, hash_circuito=sha3_hex(qasm),
            shots_pedido=shots, shots_efetivo=total, contagens=contagens,
            hash_resultado_bruto=sha3_hex(canonical({k: int(v) for k, v in sorted(contagens.items())})),
            versao_multiq=VERSAO_MULTIQ, versao_zyql=VERSAO_ZYQL, versao_adaptador=VERSAO_ADAPTADOR,
            proveniencia="primaria",
        ).selar(sk, pk)
        recibos.append(r)
        print(f"  {nome:12s} job={job_id} p={p:.4f} veredito={veredito} shots={total}")
    return recibos
