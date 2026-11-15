// SPDX-License-Identifier: Apache-2.0
// Copyright (c) 2026 Serena Solutions
//! Verificacao do recibo v2: integridade (SHA3-256) e autenticidade (ML-DSA-44).
//! Este modulo compila para a CLI e para WebAssembly: a extensao usa o mesmo codigo.

use crate::canonica::canonical;
use base64::{engine::general_purpose::STANDARD as B64, Engine};
use fips204::ml_dsa_44;
use fips204::traits::{SerDes, Verifier};
use sha3::{Digest, Sha3_256};

const FORA_DO_PAYLOAD: [&str; 4] = ["assinatura", "chave_publica", "hash_payload_canonico", "esquema"];

pub fn payload_assinado(r: &serde_json::Value) -> serde_json::Value {
    let mut obj = r.as_object().cloned().unwrap_or_default();
    for k in FORA_DO_PAYLOAD { obj.remove(k); }
    if let Some(v) = obj.remove("versao_imutq") {
        obj.insert("versao_multiq".to_string(), v);
    }
    serde_json::Value::Object(obj)
}

pub fn selo(r: &serde_json::Value) -> (String, String) {
    let p = canonical(&payload_assinado(r));
    let mut h = Sha3_256::new();
    h.update(p.as_bytes());
    (format!("{:x}", h.finalize()), p)
}

/// (inteiro, mensagem)
pub fn conferir(r: &serde_json::Value) -> (bool, String) {
    let teste = r.get("teste").and_then(|v| v.as_str()).unwrap_or("?");
    let (hash_calc, payload) = selo(r);
    let gravado = r.get("hash_payload_canonico").and_then(|v| v.as_str()).unwrap_or("");
    if hash_calc != gravado.to_lowercase() {
        return (false, format!("{teste}: hash do payload diverge"));
    }
    let (Some(sig_b64), Some(pk_b64)) = (
        r.get("assinatura").and_then(|v| v.as_str()),
        r.get("chave_publica").and_then(|v| v.as_str()),
    ) else {
        return (false, format!("{teste}: recibo sem assinatura"));
    };
    let (Ok(sig), Ok(pk)) = (B64.decode(sig_b64), B64.decode(pk_b64)) else {
        return (false, format!("{teste}: assinatura malformada"));
    };
    let pk: [u8; ml_dsa_44::PK_LEN] = match pk.try_into() {
        Ok(b) => b,
        Err(_) => return (false, format!("{teste}: tamanho de chave invalido")),
    };
    let Ok(pk) = ml_dsa_44::PublicKey::try_from_bytes(pk) else {
        return (false, format!("{teste}: chave publica invalida"));
    };
    let sig: [u8; ml_dsa_44::SIG_LEN] = match sig.try_into() {
        Ok(s) => s,
        Err(_) => return (false, format!("{teste}: tamanho de assinatura invalido")),
    };
    if pk.verify(payload.as_bytes(), &sig, &[]) {
        (true, format!("{teste}: integro e assinado"))
    } else {
        (false, format!("{teste}: assinatura invalida"))
    }
}

/// Entrada unica usada pela extensao: JSON em bytes, 1 = valido, 0 = invalido.
pub fn verificar_bytes(bytes: &[u8]) -> i32 {
    match serde_json::from_slice::<serde_json::Value>(bytes) {
        Ok(v) => if conferir(&v).0 { 1 } else { 0 },
        Err(_) => -1,
    }
}
