// SPDX-License-Identifier: Apache-2.0
// Copyright (c) 2026 Serena Solutions
//! IMUT-Q — verificador de recibos da linguagem ZYQL.
//! Veredito trivalente: 1 / 0 / REFUSED. Nunca arredonda.


use imutq::canonica::canonical;
mod recibo;
use serde::Deserialize;
use sha3::{Digest, Sha3_256};
use std::process::ExitCode;

/// Banda declarada do kernel. Fora dela, decide; dentro, recusa.
pub const BANDA: f64 = 0.15;

/// O veredito é o produto, não um booleano.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Veredito {
    Zero,
    Um,
    Recusado,
}

impl Veredito {
    pub fn texto(self) -> &'static str {
        match self {
            Veredito::Zero => "0",
            Veredito::Um => "1",
            Veredito::Recusado => "REFUSED",
        }
    }
    pub fn codigo(self) -> u8 {
        match self {
            Veredito::Zero => 0,
            Veredito::Um => 1,
            Veredito::Recusado => 2,
        }
    }
}

/// p acima de 1-banda decide 1; abaixo da banda decide 0; o meio é recusa.
pub fn decidir(p: f64, banda: f64) -> Veredito {
    if !(0.0..=1.0).contains(&p) {
        return Veredito::Recusado;
    }
    if p >= 1.0 - banda {
        Veredito::Um
    } else if p <= banda {
        Veredito::Zero
    } else {
        Veredito::Recusado
    }
}

/// Probabilidade de falha de Hoeffding: P(|p_hat - p| >= eps) <= 2*exp(-2n*eps^2).
pub fn prob_falha_hoeffding(n: u32, eps: f64) -> f64 {
    if n == 0 {
        return 1.0;
    }
    (2.0 * (-2.0 * (n as f64) * eps * eps).exp()).min(1.0)
}

/// Margem de erro de Hoeffding, invertendo a cota para confianca 1-delta.
/// eps = sqrt(ln(2/delta) / (2n)). Esta e a margem que vai no recibo.
pub fn margem_hoeffding(n: u32, delta: f64) -> f64 {
    if n == 0 || !(delta > 0.0 && delta < 1.0) {
        return 1.0;
    }
    ((2.0 / delta).ln() / (2.0 * n as f64)).sqrt().min(1.0)
}

/// Intervalo de Wilson, dentro de [0,1] por construção.
pub fn intervalo_wilson(k: u32, n: u32, z: f64) -> (f64, f64) {
    if n == 0 {
        return (0.0, 1.0);
    }
    let n = n as f64;
    let p = k as f64 / n;
    let z2 = z * z;
    let centro = (p + z2 / (2.0 * n)) / (1.0 + z2 / n);
    let meio = z * (p * (1.0 - p) / n + z2 / (4.0 * n * n)).sqrt() / (1.0 + z2 / n);
    ((centro - meio).max(0.0), (centro + meio).min(1.0))
}

#[derive(Debug, Deserialize)]
pub struct Recibo {
    pub teste: String,
    pub payload: serde_json::Value,
    pub sha3_256: String,
}

/// Serialização idêntica a json.dumps(obj, sort_keys=True): chaves ordenadas,
/// separadores ", " e ": ", não-ASCII escapado.
/// Reconferência: recalcula o SHA3 do payload canônico e compara com o gravado.
pub fn conferir(recibo: &Recibo) -> Result<String, String> {
    let mut h = Sha3_256::new();
    h.update(canonical(&recibo.payload).as_bytes());
    let calc = format!("{:x}", h.finalize());
    if calc == recibo.sha3_256.to_lowercase() {
        Ok(calc)
    } else {
        Err(format!(
            "{}: hash diverge (gravado {}, calculado {})",
            recibo.teste, recibo.sha3_256, calc
        ))
    }
}

fn main() -> ExitCode {
    let args: Vec<String> = std::env::args().collect();
    match args.get(1).map(String::as_str) {
        Some("veredito") => {
            let p: f64 = args.get(2).and_then(|s| s.parse().ok()).unwrap_or(f64::NAN);
            let n: u32 = args.get(3).and_then(|s| s.parse().ok()).unwrap_or(0);
            let v = decidir(p, BANDA);
            let (lo, hi) = intervalo_wilson((p * n as f64).round() as u32, n, 1.96);
            println!("veredito: {}", v.texto());
            println!("p={p:.4} n={n} banda={BANDA}");
            println!("wilson95: [{lo:.4}, {hi:.4}]");
            println!("margem_hoeffding(delta=0.05): {:.4}", margem_hoeffding(n, 0.05));
            println!("prob_falha(n, banda): {:.3e}", prob_falha_hoeffding(n, BANDA));
            ExitCode::from(v.codigo())
        }
        Some("checar") => {
            let caminho = match args.get(2) {
                Some(c) => c,
                None => {
                    eprintln!("uso: imutq checar <arquivo.json>");
                    return ExitCode::from(2);
                }
            };
            let texto = match std::fs::read_to_string(caminho) {
                Ok(t) => t,
                Err(e) => {
                    eprintln!("erro de leitura: {e}");
                    return ExitCode::from(2);
                }
            };
            let raiz: serde_json::Value = match serde_json::from_str(&texto) {
                Ok(v) => v,
                Err(e) => {
                    eprintln!("json invalido: {e}");
                    return ExitCode::from(2);
                }
            };
            let recibos: Vec<Recibo> =
                serde_json::from_value(raiz["recibos"].clone()).unwrap_or_default();
            let mut falhas = 0usize;
            for r in &recibos {
                match conferir(r) {
                    Ok(h) => println!("OK    {:12} {}", r.teste, &h[..16]),
                    Err(e) => {
                        falhas += 1;
                        println!("FALHA {e}");
                    }
                }
            }
            println!("{} recibos, {} falhas", recibos.len(), falhas);
            ExitCode::from(if falhas == 0 { 0 } else { 1 })
        }
        Some("verificar") => recibo::cli(&args[2..].iter().map(|s| s.clone()).collect::<Vec<_>>()),
        _ => {
            eprintln!("uso: imutq veredito <p> <n> | imutq checar <arq> | imutq verificar <arq...>");
            ExitCode::from(2)
        }
    }
}
