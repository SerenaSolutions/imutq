// SPDX-License-Identifier: Apache-2.0
// Copyright (c) 2026 Serena Solutions
//! CLI de verificacao. A regra mora em `imutq::verificacao`, compartilhada com o WebAssembly.

use imutq::verificacao::conferir;
use std::process::ExitCode;

pub fn cli(arquivos: &[String]) -> ExitCode {
    if arquivos.is_empty() {
        eprintln!("uso: imutq verificar <arquivo.json> [mais arquivos]");
        return ExitCode::from(2);
    }
    let (mut total, mut falhas) = (0usize, 0usize);
    for caminho in arquivos {
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
            if !ok { falhas += 1; }
        }
    }
    println!("{total} recibos, {falhas} falhas");
    ExitCode::from(if falhas == 0 { 0 } else { 1 })
}
