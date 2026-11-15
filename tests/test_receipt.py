# SPDX-License-Identifier: Apache-2.0
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from dilithium_py.ml_dsa import ML_DSA_44
from multiq.receipt import ReciboV2

def base():
    return ReciboV2(teste="T", veredito="1", job_id="j1", provedor="IBM",
                    backend="b", dispositivo="d", hash_circuito="h",
                    shots_pedido=10, shots_efetivo=10, contagens={"00": 10},
                    hash_resultado_bruto="r", versao_multiq="0.1.0",
                    versao_zyql="2.5.9", versao_adaptador="a")

def test_recibo_assinado_confere():
    pk, sk = ML_DSA_44.keygen()
    r = base().selar(sk, pk)
    ok, msg = r.conferir()
    assert ok, msg

def test_adulteracao_detectada():
    pk, sk = ML_DSA_44.keygen()
    r = base().selar(sk, pk)
    r.contagens = {"00": 9}
    ok, _ = r.conferir()
    assert not ok

def test_sem_assinatura_rejeitado():
    r = base().selar(None, None)
    ok, msg = r.conferir()
    assert not ok and "assinatura" in msg
