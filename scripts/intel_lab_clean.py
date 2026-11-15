# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Solutions
"""IMUT-Q no Intel Quantum SDK (qBraid Lab). Sintaxe documentada v1.1.

Fluxo: QASM 2.0 -> openqasm_bridge.translate -> compileProgram -> callCppFunction
-> getProbabilities -> amostragem com seed -> JSON de recibo.

Uso:  python3 intel_lab_clean.py [BELL_Z|BELL_X|DJ_balanced|DJ_constant|GHZ_3|IDENTITY]
"""
import json, os, shutil, sys, hashlib, glob
import numpy as np

SHOTS, SEED = 1024, 12345
SDK_NAME = "imutq"

QASM = {
"BELL_Z": 'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[2];\ncreg c[2];\nh q[0];\ncx q[0],q[1];\nmeasure q -> c;\n',
"BELL_X": 'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[2];\ncreg c[2];\nh q[0];\ncx q[0],q[1];\nh q[0];\nh q[1];\nmeasure q -> c;\n',
"DJ_constant": 'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[4];\ncreg c[3];\nx q[3];\nh q[0];h q[1];h q[2];h q[3];\nh q[0];h q[1];h q[2];\nmeasure q[0] -> c[0];\nmeasure q[1] -> c[1];\nmeasure q[2] -> c[2];\n',
"DJ_balanced": 'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[4];\ncreg c[3];\nx q[3];\nh q[0];h q[1];h q[2];h q[3];\ncx q[0],q[3];\ncx q[1],q[3];\ncx q[2],q[3];\nh q[0];h q[1];h q[2];\nmeasure q[0] -> c[0];\nmeasure q[1] -> c[1];\nmeasure q[2] -> c[2];\n',
"GHZ_3": 'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[3];\ncreg c[3];\nh q[0];\ncx q[0],q[1];\ncx q[1],q[2];\nmeasure q -> c;\n',
"IDENTITY": 'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[1];\ncreg c[1];\nmeasure q -> c;\n',
}

def achar_compilador():
    for c in (os.environ.get("IQS_COMPILER"), shutil.which("intel-quantum-compiler"),
              "/opt/intel/intel-quantum-sdk/intel-quantum-compiler"):
        if c and os.path.exists(c):
            return c
    for p in glob.glob("/**/intel-quantum-compiler", recursive=True)[:1]:
        return p
    return None

def n_qubits(qasm):
    import re
    m = re.search(r"qreg\s+\w+\[(\d+)\]", qasm)
    return int(m.group(1)) if m else 2

def rodar(nome):
    qasm = QASM[nome]
    import intelqsdk.cbindings as cb
    from openqasm_bridge.v2 import translate
    cpp = f"/tmp/{nome.lower()}.cpp"
    open(cpp, "w").write("\n".join(translate(qasm, kernel_name="imutq_kernel")))
    comp = achar_compilador()
    if not comp:
        raise RuntimeError("intel-quantum-compiler nao encontrado; defina IQS_COMPILER")
    cb.compileProgram(comp, cpp, "-s", SDK_NAME)
    cfg = cb.IqsConfig(); cfg.num_qubits = n_qubits(qasm); cfg.simulation_type = "noiseless"
    dev = cb.FullStateSimulator(cfg); dev.ready()
    cb.callCppFunction("imutq_kernel", SDK_NAME)
    refs = cb.RefVec()
    for i in range(n_qubits(qasm)):
        refs.append(cb.QbitRef("q", i, SDK_NAME).get_ref())
    probs = list(dev.getProbabilities(refs))
    dev.wait()
    rng = np.random.default_rng(SEED)
    sorteio = rng.choice(len(probs), size=SHOTS, p=np.array(probs) / sum(probs))
    largura = n_qubits(qasm)
    contagens = {}
    for s in sorteio:
        chave = format(int(s), f"0{largura}b")   # ordem_bits: q0 e o bit menos significativo
        contagens[chave] = contagens.get(chave, 0) + 1
    return {"teste": nome, "provedor": "Intel", "backend": "iqs",
            "dispositivo": "Intel Quantum Simulator (qBraid Lab)", "proveniencia": "simulada_sdk",
            "hash_circuito": hashlib.sha3_256(qasm.encode()).hexdigest(),
            "shots_pedido": SHOTS, "shots_efetivo": sum(contagens.values()),
            "contagens": contagens, "seed": SEED, "ordem_bits": "q0 = bit menos significativo",
            "metodo_contagem": "amostragem das probabilidades do simulador com seed fixa",
            "probabilidades": [round(float(p), 8) for p in probs],
            "versao_sdk": getattr(__import__("intelqsdk"), "__version__", "v1.1")}

if __name__ == "__main__":
    alvos = sys.argv[1:] or list(QASM)
    saida = []
    for alvo in alvos:
        try:
            r = rodar(alvo); saida.append(r); print(f"OK   {alvo} {r['contagens']}", file=sys.stderr)
        except Exception as e:
            saida.append({"teste": alvo, "estado": "BLOQUEADO", "erro": f"{type(e).__name__}: {e}"[:300]})
            print(f"FALHA {alvo}: {e}", file=sys.stderr)
    print(json.dumps({"recibos": saida}, ensure_ascii=False, indent=1))
