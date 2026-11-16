// SPDX-License-Identifier: Apache-2.0
// Copyright (c) 2026 Serena Solutions
//! Método ZEPHIRUM aplicado ao ensino: três respostas, domínio por evidência e recibo.
//! Mesmo núcleo para o app adulto e o infantojuvenil.

use serde::Serialize;
use sha3::{Digest, Sha3_256};

pub const Z_95: f64 = 1.959_963_984_540_054;

/// Veredito do método. Nunca dois estados: sempre três.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
pub enum Veredito {
    /// Evidência suficiente e proporção acima do limiar.
    Dominado,
    /// Evidência suficiente e proporção abaixo do limiar.
    EmProgresso,
    /// Evidência insuficiente para decidir. Não é erro do aluno.
    Insuficiente,
}

/// Limite inferior do intervalo de confiança de Wilson para uma proporção.
/// Devolve 0.0 quando não há observação alguma.
pub fn wilson_inferior(acertos: u32, total: u32, z: f64) -> f64 {
    if total == 0 {
        return 0.0;
    }
    let n = total as f64;
    let p = acertos as f64 / n;
    let z2 = z * z;
    let centro = p + z2 / (2.0 * n);
    let margem = z * ((p * (1.0 - p) / n) + z2 / (4.0 * n * n)).sqrt();
    let denom = 1.0 + z2 / n;
    ((centro - margem) / denom).clamp(0.0, 1.0)
}

/// Decisão do método: só declara domínio quando a evidência sustenta.
/// `limiar` é o piso do limite inferior (padrão 0.80) e `minimo` o número de
/// respostas exigido antes de qualquer julgamento (padrão 8).
pub fn decidir(acertos: u32, total: u32, limiar: f64, minimo: u32) -> Veredito {
    if total < minimo {
        return Veredito::Insuficiente;
    }
    if wilson_inferior(acertos, total, Z_95) >= limiar {
        Veredito::Dominado
    } else if total < minimo * 2 && acertos as f64 / total as f64 >= limiar {
        // Acima do limiar mas com amostra ainda curta: continua observando.
        Veredito::Insuficiente
    } else {
        Veredito::EmProgresso
    }
}

/// Quantas respostas faltariam, no ritmo atual, para sair de Insuficiente.
/// Devolve 0 quando já há evidência suficiente.
pub fn respostas_faltantes(acertos: u32, total: u32, limiar: f64, minimo: u32) -> u32 {
    if total >= minimo && decidir(acertos, total, limiar, minimo) != Veredito::Insuficiente {
        return 0;
    }
    let p = if total == 0 { 1.0 } else { acertos as f64 / total as f64 };
    let mut n = total.max(1);
    while n < 400 {
        let a = (p * n as f64).round() as u32;
        if n >= minimo && wilson_inferior(a, n, Z_95) >= limiar {
            return n - total;
        }
        n += 1;
    }
    400u32.saturating_sub(total)
}

/// Agendamento de revisão no espírito do FSRS, simplificado para uso em app:
/// estabilidade em dias cresce a cada acerto e cai no erro.
pub fn proxima_revisao_dias(estabilidade: f64, acertou: bool) -> f64 {
    let s = estabilidade.max(0.5);
    if acertou {
        (s * 1.9).min(365.0)
    } else {
        (s * 0.45).max(0.5)
    }
}

/// Recibo de conceito dominado: hash canônico do conteúdo e elo com o recibo anterior.
#[derive(Debug, Clone, Serialize)]
pub struct Recibo {
    pub crianca_ou_aluno: String,
    pub conceito: String,
    pub acertos: u32,
    pub total: u32,
    pub limite_inferior: f64,
    pub veredito: Veredito,
    pub emitido_em: String,
    pub prev_sha3: String,
    pub sha3: String,
}

pub fn selar_recibo(r: &Recibo) -> String {
    let corpo = serde_json::json!({
        "aluno": r.crianca_ou_aluno,
        "conceito": r.conceito,
        "acertos": r.acertos,
        "total": r.total,
        "limite_inferior": format!("{:.6}", r.limite_inferior),
        "veredito": r.veredito,
        "emitido_em": r.emitido_em,
        "prev_sha3": r.prev_sha3,
    });
    let bytes = serde_json::to_vec(&corpo).expect("corpo serializavel");
    let mut h = Sha3_256::new();
    h.update(&bytes);
    format!("{:x}", h.finalize())
}

#[cfg(test)]
mod testes {
    use super::*;

    #[test]
    fn tres_de_tres_nao_e_dominio() {
        // 3 acertos em 3 dão limite inferior perto de 0,44: insuficiente.
        let w = wilson_inferior(3, 3, Z_95);
        assert!(w < 0.5, "limite inferior de 3/3 foi {w}");
        assert_eq!(decidir(3, 3, 0.80, 8), Veredito::Insuficiente);
    }

    #[test]
    fn vinte_de_vinte_e_dominio() {
        assert_eq!(decidir(20, 20, 0.80, 8), Veredito::Dominado);
        assert!(wilson_inferior(20, 20, Z_95) > 0.80);
    }

    #[test]
    fn metade_das_respostas_nunca_e_dominio() {
        for n in [8u32, 30, 100, 400] {
            assert_ne!(decidir(n / 2, n, 0.80, 8), Veredito::Dominado, "n={n}");
        }
    }

    #[test]
    fn monotonia_do_limite_inferior() {
        // Com a mesma proporção, mais amostra aperta o intervalo.
        let a = wilson_inferior(8, 10, Z_95);
        let b = wilson_inferior(80, 100, Z_95);
        assert!(b > a, "{b} deveria superar {a}");
    }

    #[test]
    fn faltantes_para_dominio() {
        let f = respostas_faltantes(3, 3, 0.80, 8);
        assert!(f > 0);
        let a = 3 + f;
        assert_eq!(decidir(a, a, 0.80, 8), Veredito::Dominado);
    }

    #[test]
    fn recibo_muda_se_o_conteudo_muda() {
        let base = Recibo {
            crianca_ou_aluno: "aluno-1".into(),
            conceito: "qubit".into(),
            acertos: 20,
            total: 20,
            limite_inferior: wilson_inferior(20, 20, Z_95),
            veredito: Veredito::Dominado,
            emitido_em: "2026-11-16T12:00:00Z".into(),
            prev_sha3: "0".repeat(64),
            sha3: String::new(),
        };
        let s1 = selar_recibo(&base);
        let mut alterado = base.clone();
        alterado.acertos = 19;
        let s2 = selar_recibo(&alterado);
        assert_ne!(s1, s2);
        assert_eq!(s1.len(), 64);
    }

    #[test]
    fn revisao_cresce_no_acerto_e_cai_no_erro() {
        assert!(proxima_revisao_dias(2.0, true) > 2.0);
        assert!(proxima_revisao_dias(2.0, false) < 2.0);
    }
}
