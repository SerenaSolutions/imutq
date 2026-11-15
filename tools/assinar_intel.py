# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Solutions
"""Ingere contagens do Intel IQS vindas em arquivo e emite recibo v2.

Nao inventa job_id: sem submissao remota, o vinculo nao e primario e o recibo diz isso.
"""
import json, math, pathlib, sys
sys.path.insert(0, "src")
from imutq.receipt import ReciboV2, sha3_hex, canonical

SK = pathlib.Path("keys/ml-dsa-44.sk").read_bytes()
PK = pathlib.Path("keys/ml-dsa-44.pk").read_bytes()
QASM = 'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[2];\ncreg c[2];\nh q[0];\ncx q[0],q[1];\nmeasure q -> c;\n'

def analisar(c, ideal):
    n = sum(c.values())
    obs = {k: v / n for k, v in c.items()}
    tvd = 0.5 * sum(abs(obs.get(k, 0) - ideal.get(k, 0)) for k in set(obs) | set(ideal))
    fora = {k: v for k, v in c.items() if k not in ideal}
    chi2 = sum((c.get(k, 0) - n * p) ** 2 / (n * p) for k, p in ideal.items())
    return n, tvd, fora, chi2

c = json.load(open(sys.argv[1]))
ideal = {"00": 0.5, "11": 0.5}
n, tvd, fora, chi2 = analisar(c, ideal)
sigma = math.sqrt(n * 0.25)

nota = (f"{n} tiros; TVD {tvd:.4f}; chi2 {chi2:.2f} (gl=1, critico 3.841); "
        f"fora do suporte: {fora or 'nenhum'} = {100*sum(fora.values())/n:.2f}%; "
        f"5 sigma = {5*sigma:.1f}")
# Regra vigente (suporte estrito) daria 0; regra estatistica (TVD<=0.05) daria 1.
# Protocolo nao declarado para esta entrada -> REFUSED, e a divergencia fica registrada.
veredito = "REFUSED"
nota += " | regra de suporte daria 0 e regra de TVD daria 1: protocolo nao declarado para esta entrada"

r = ReciboV2(
    teste="BELL_Z", veredito=veredito, job_id="sem_job_remoto:iqs-local",
    provedor="Intel", backend="iqs", dispositivo="Intel Quantum Simulator (qBraid Lab)",
    hash_circuito=sha3_hex(canonical(QASM)), shots_pedido=n, shots_efetivo=n,
    contagens=c, hash_resultado_bruto=sha3_hex(canonical({k: int(v) for k, v in sorted(c.items())})),
    versao_imutq="0.3.1", versao_zyql="2.5.9", versao_adaptador="intel-iqs-local",
    proveniencia="reconstruida",
    nota_proveniencia=nota + " | arquivo recebido do dono, sem registro de submissao",
).selar(sk=SK, pk=PK)
assert r.conferir()[0]
destino = "receipts/2026-11-15/intel-bell-01-assinado.json"
json.dump({"esquema": "2.0", "recibos": [json.loads(r.to_json())]}, open(destino, "w"), ensure_ascii=False, indent=1)
print(f"veredito={veredito} | {nota}")
print("gravado:", destino)
