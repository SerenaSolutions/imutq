// SPDX-License-Identifier: Apache-2.0
// Copyright (c) 2026 Serena Solutions
//! Verificação do recibo IMUT-Q v2: integridade (SHA3-256) e autenticidade
//! (ML-DSA-44). Este é o núcleo em Rust; os adaptadores Python apenas submetem.

use crate::canonical;
use base64::{engine::general_purpose::STANDARD as B64, Engine};
use fips204::ml_dsa_44;
use fips204::traits::{SerDes, Verifier};
use sha3::{Digest, Sha3_256};
use std::process::ExitCode;

const FORA_DO_PAYLOAD: [&str; 4] = [
    "assinatura",
    "chave_publica",
    "hash_payload_canonico",
    "esquema",
];

/// Reconstrói o payload canônico assinado.
/// O esquema 2.0 congelou o campo como `versao_multiq`; no código ele aparece
/// como `versao_imutq`. O rename só entra no esquema v3, com recibos novos.
pub fn payload_assinado(r: &serde_json::Value) -> serde_json::Value {
    let mut obj = r.as_object().cloned().unwrap_or_default();
    for k in FORA_DO_PAYLOAD {
        obj.remove(k);
    }
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

/// Confere um recibo. Devolve (ok, mensagem).
pub fn conferir(r: &serde_json::Value) -> (bool, String) {
    let teste = r.get("teste").and_then(|v| v.as_str()).unwrap_or("?");
    let (hash_calc, payload) = selo(r);
    let hash_grav = r.get("hash_payload_canonico").and_then(|v| v.as_str()).unwrap_or("");
    if hash_calc != hash_grav.to_lowercase() {
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

pub fn cli(args: &[String]) -> ExitCode {
    let mut arquivos: Vec<String> = Vec::new();
    for a in args {
        if a != "verificar" {
            arquivos.push(a.clone());
        }
    }
    if arquivos.is_empty() {
        eprintln!("uso: imutq verificar <arquivo.json> [mais arquivos]");
        return ExitCode::from(2);
    }
    let mut falhas = 0usize;
    let mut total = 0usize;
    for caminho in &arquivos {
        let texto = match std::fs::read_to_string(caminho) {
            Ok(t) => t,
            Err(e) => {
                eprintln!("{caminho}: erro de leitura {e}");
                falhas += 1;
                continue;
            }
        };
        let raiz: serde_json::Value = match serde_json::from_str(&texto) {
            Ok(v) => v,
            Err(e) => {
                eprintln!("{caminho}: json invalido {e}");
                falhas += 1;
                continue;
            }
        };
        let itens: Vec<serde_json::Value> = if raiz.is_array() {
            raiz.as_array().cloned().unwrap_or_default()
        } else if raiz.get("recibos").is_some() {
            raiz["recibos"].as_array().cloned().unwrap_or_default()
        } else {
            vec![raiz]
        };
        for r in &itens {
            let (ok, msg) = conferir(r);
            println!("{} {}", if ok { "OK   " } else { "FALHA" }, msg);
            total += 1;
            if !ok {
                falhas += 1;
            }
        }
    }
    println!("{total} recibos, {falhas} falhas");
    ExitCode::from(if falhas == 0 { 0 } else { 1 })
}
