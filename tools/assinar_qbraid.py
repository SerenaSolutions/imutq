# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Solutions
"""Assina os recibos dos jobs executados no qBraid a partir da varredura bruta.

Proveniencia primaria: o job_id e o jobQrn devolvido na submissao, nao reconstruido.
"""
import json, math, pathlib, sys
sys.path.insert(0, "src")
from imutq.receipt import ReciboV2, sha3_hex, canonical
from dilithium_py.ml_dsa import ML_DSA_44

SK = pathlib.Path("keys/ml-dsa-44.sk").read_bytes()
PK = pathlib.Path("keys/ml-dsa-44.pk").read_bytes()
QASM = ('OPENQASM 3.0;\ninclude "stdgates.inc";\nbit[2] c;\nqubit[2] q;\n'
        'h q[0];\ncx q[0], q[1];\nc[0] = measure q[0];\nc[1] = measure q[1];')
HASH_CIRC = sha3_hex(canonical(QASM))

def julgar(contagens, shots):
    sig = math.sqrt(shots * 0.5 * 0.5)
    fora = {k: v for k, v in contagens.items() if k not in ("00", "11") and v > 0}
    desvio = max(abs(contagens.get("00", 0) - shots / 2), abs(contagens.get("11", 0) - shots / 2))
    if fora:
        return "0", f"resultados fora do suporte de Bell: {list(fora)[:3]}"
    if desvio > 5 * sig:
        return "0", f"desvio {desvio:.0f} acima de 5 sigma ({5*sig:.0f})"
    return "1", f"desvio {desvio:.0f} dentro de 5 sigma ({5*sig:.0f})"

bruto = json.load(open("receipts/2026-11-15/qbraid-varredura.json"))
recibos = []
for d in bruto["dispositivos"]:
    if d.get("status") != "COMPLETED" or not d.get("resultado"):
        continue
    res = d["resultado"]
    contagens = res.get("measurementCounts") or {}
    shots = d.get("shots") or sum(contagens.values())
    veredito, nota = julgar(contagens, shots)
    r = ReciboV2(
        teste="BELL_Z", veredito=veredito, job_id=d["job_id"],
        provedor="qBraid", backend=d["qrn"], dispositivo=(res.get("simulator") or d["qrn"]),
        hash_circuito=HASH_CIRC, shots_pedido=int(shots), shots_efetivo=int(sum(contagens.values())),
        contagens=contagens, hash_resultado_bruto=sha3_hex(canonical(res)),
        versao_imutq="0.3.0", versao_zyql="2.5.9", versao_adaptador="qbraid-rest-v1",
        proveniencia="primaria", nota_proveniencia=f"{nota}; custo 0; varredura 15/11/2026",
    ).selar(sk=SK, pk=PK)
    assert r.conferir()[0]
    recibos.append(json.loads(r.to_json()))
    print(f"{d['qrn']:42s} veredito={veredito} {contagens}")

destino = "receipts/2026-11-15/qbraid-assinados.json"
json.dump({"esquema": "2.0", "recibos": recibos}, open(destino, "w"), ensure_ascii=False, indent=1)
print(f"\n{len(recibos)} recibos assinados em {destino}")
