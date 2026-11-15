# SPDX-License-Identifier: LicenseRef-Serena-Commercial-1.0
import argparse, json, os, pathlib, sys
from .hw import executar
from .receipt import ReciboV2

def main():
    ap = argparse.ArgumentParser(prog="multiq")
    ap.add_argument("cmd", choices=["executar", "verificar"])
    ap.add_argument("--backend", default="ibm_fez")
    ap.add_argument("--shots", type=int, default=1024)
    ap.add_argument("--saida", default="receipts/2026-11-15")
    ap.add_argument("--recebido", nargs="*", default=[])
    a = ap.parse_args()

    if a.cmd == "executar":
        from dilithium_py.ml_dsa import ML_DSA_44
        os.makedirs("keys", exist_ok=True)
        sk_path = pathlib.Path("keys/ml-dsa-44.sk")
        if sk_path.exists():
            sk = sk_path.read_bytes(); pk = pathlib.Path("keys/ml-dsa-44.pk").read_bytes()
        else:
            pk, sk = ML_DSA_44.keygen()
            sk_path.write_bytes(sk); pathlib.Path("keys/ml-dsa-44.pk").write_bytes(pk)
        recibos = executar(a.backend, a.shots, sk, pk)
        out = pathlib.Path(a.saida); out.mkdir(parents=True, exist_ok=True)
        (out / "lote.json").write_text(json.dumps([json.loads(r.to_json()) for r in recibos], indent=2, ensure_ascii=False))
        print(f"lote gravado em {out/'lote.json'}")
    else:
        falhas = 0
        for c in a.recebido:
            dados = json.loads(pathlib.Path(c).read_text())
            for d in (dados if isinstance(dados, list) else [dados]):
                r = ReciboV2(**{k: v for k, v in d.items() if k in ReciboV2.__dataclass_fields__})
                ok, msg = r.conferir()
                print(f"{'OK  ' if ok else 'FALHA'} {r.teste:12s} {msg}")
                falhas += 0 if ok else 1
        sys.exit(0 if falhas == 0 else 1)

if __name__ == "__main__":
    main()
