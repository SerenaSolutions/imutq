# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Solutions
"""Recibo IMUT-Q v2: integridade, autenticidade e proveniencia declaradas."""
from __future__ import annotations
import base64, hashlib, json
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone

VERSAO = "2.0"


def canonical(v) -> str:
    """Identico a json.dumps(obj, sort_keys=True)."""
    return json.dumps(v, sort_keys=True, ensure_ascii=True)


def sha3_hex(s: str) -> str:
    return hashlib.sha3_256(s.encode()).hexdigest()


@dataclass
class ReciboV2:
    teste: str
    veredito: str                      # "1" | "0" | "REFUSED"
    job_id: str
    provedor: str
    backend: str
    dispositivo: str
    hash_circuito: str
    shots_pedido: int
    shots_efetivo: int
    contagens: dict
    hash_resultado_bruto: str
    versao_multiq: str
    versao_zyql: str
    versao_adaptador: str
    proveniencia: str = "primaria"     # "primaria" | "reconstruida"
    nota_proveniencia: str | None = None
    emitido_em: str = field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    assinatura: str | None = None
    algoritmo_assinatura: str = "ML-DSA-44"
    chave_publica: str | None = None
    hash_payload_canonico: str | None = None

    def selar(self, sk=None, pk=None) -> "ReciboV2":
        payload = self.payload()
        self.hash_payload_canonico = sha3_hex(canonical(payload))
        if sk is not None:
            from dilithium_py.ml_dsa import ML_DSA_44
            sig = ML_DSA_44.sign(sk, canonical(payload).encode())
            self.assinatura = base64.b64encode(sig).decode()
            self.chave_publica = base64.b64encode(pk).decode()
        return self

    def payload(self) -> dict:
        d = asdict(self)
        for k in ("assinatura", "chave_publica", "hash_payload_canonico"):
            d.pop(k, None)
        return d

    def conferir(self) -> tuple[bool, str]:
        if sha3_hex(canonical(self.payload())) != self.hash_payload_canonico:
            return False, "hash do payload diverge"
        if not self.assinatura:
            return False, "recibo sem assinatura"
        from dilithium_py.ml_dsa import ML_DSA_44
        ok = ML_DSA_44.verify(base64.b64decode(self.chave_publica),
                              canonical(self.payload()).encode(),
                              base64.b64decode(self.assinatura))
        return (True, "integro e assinado") if ok else (False, "assinatura invalida")

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, ensure_ascii=False)
