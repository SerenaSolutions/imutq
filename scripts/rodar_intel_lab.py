# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Solutions
"""Sonda o ambiente Intel do qBraid Lab e roda BELL_Z, devolvendo JSON de recibo.

Nao assume API: descobre o que existe e reporta o que funcionou.
Cole o JSON final de volta para selagem e assinatura no nucleo Rust.
"""
import json, os, shutil, subprocess, sys, time

CIRC = {
 "BELL_Z": 'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[2];\ncreg c[2];\nh q[0];\ncx q[0],q[1];\nmeasure q -> c;\n',
 "BELL_X": 'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[2];\ncreg c[2];\nh q[0];\ncx q[0],q[1];\nh q[0];\nh q[1];\nmeasure q -> c;\n',
 "DJ_constant": 'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[4];\ncreg c[3];\nx q[3];\nh q[0];h q[1];h q[2];h q[3];\nh q[0];h q[1];h q[2];\nmeasure q[0] -> c[0];\nmeasure q[1] -> c[1];\nmeasure q[2] -> c[2];\n',
 "DJ_balanced": 'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[4];\ncreg c[3];\nx q[3];\nh q[0];h q[1];h q[2];h q[3];\ncx q[0],q[3];\ncx q[1],q[3];\ncx q[2],q[3];\nh q[0];h q[1];h q[2];\nmeasure q[0] -> c[0];\nmeasure q[1] -> c[1];\nmeasure q[2] -> c[2];\n',
 "GHZ_3": 'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[3];\ncreg c[3];\nh q[0];\ncx q[0],q[1];\ncx q[1],q[2];\nmeasure q -> c;\n',
 "IDENTITY": 'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[1];\ncreg c[1];\nmeasure q -> c;\n',
}
SHOTS = 1024
SEED = 12345

def roda(cmd, timeout=120):
    try:
        p = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return {"cmd": cmd, "rc": p.returncode, "out": (p.stdout or "")[-1500:], "err": (p.stderr or "")[-800:]}
    except Exception as e:
        return {"cmd": cmd, "rc": None, "out": "", "err": str(e)[:300]}

rel = {"sonda": {}, "execucao": None, "json_recibo": None}

# 1) SONDA
mods = {}
for m in ("intelqsdk", "intelqsdk.cbindings", "intelqsdk.circuit", "iqs", "intel_quantum_simulator", "qiskit"):
    try:
        mod = __import__(m, fromlist=["*"])
        mods[m] = {"import": "ok", "version": getattr(mod, "__version__", None),
                   "atributos": [a for a in dir(mod) if not a.startswith("_")][:25]}
    except Exception as e:
        mods[m] = {"import": "falhou", "erro": str(e)[:160]}
bins = {b: shutil.which(b) for b in ("intelqsdk", "iqs", "qasm", "g++", "make", "python3")}
rel["sonda"] = {"python": sys.version.split()[0], "modulos": mods, "binarios": bins,
                "cwd": os.getcwd(), "env_relevante": {k: v for k, v in os.environ.items() if "INTEL" in k.upper() or "QULACS" in k.upper()}}

# 2) TENTATIVA via bindings Python
execucao = None
try:
    import intelqsdk  # noqa
    cand = [a for a in dir(intelqsdk) if any(t in a.lower() for t in ("sim", "backend", "circuit", "run"))]
    execucao = {"caminho": "intelqsdk", "candidatos": cand, "resultado": "modulo presente, API a descobrir"}
except Exception as e:
    execucao = {"caminho": "intelqsdk", "resultado": "indisponivel", "erro": str(e)[:200]}

# 3) FALLBACK: compilar BELL_Z com o compilador do SDK, se existir
if bins.get("intelqsdk"):
    open("/tmp/bell.qasm", "w").write(CIRC["BELL_Z"])
    c1 = roda("intelqsdk /tmp/bell.qasm -B", timeout=180)
    c2 = roda("intelqsdk --help", timeout=60)
    execucao = {"caminho": "compilador intelqsdk", "compilar": c1, "ajuda": (c2.get("out") or c2.get("err"))[:900]}

rel["execucao"] = execucao
rel["json_recibo"] = {
  "provedor": "Intel", "backend": "iqs", "dispositivo": "Intel Quantum Simulator local (qBraid Lab)",
  "proveniencia": "simulada_sdk", "shots": SHOTS, "seed": SEED,
  "circuitos": list(CIRC), "hash_programas": {k: __import__("hashlib").sha3_256(v.encode()).hexdigest() for k, v in CIRC.items()},
  "contagens": None, "versao_sdk": mods.get("intelqsdk", {}).get("version"),
  "preenchido": False, "nota": "preencher contagens apos execucao",
}
print(json.dumps(rel, ensure_ascii=False, indent=1))
