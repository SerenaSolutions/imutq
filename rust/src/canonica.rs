// SPDX-License-Identifier: Apache-2.0
// Copyright (c) 2026 Serena Solutions
//! Serializacao canonica identica a json.dumps(sort_keys=True).

pub fn canonical(v: &serde_json::Value) -> String {
    match v {
        serde_json::Value::Null => "null".into(),
        serde_json::Value::Bool(b) => b.to_string(),
        serde_json::Value::Number(n) => {
            if let Some(i) = n.as_i64() {
                i.to_string()
            } else if let Some(u) = n.as_u64() {
                u.to_string()
            } else {
                let f = n.as_f64().unwrap_or(0.0);
                let mut t = format!("{f}");
                if !t.contains('.') && !t.contains('e') && !t.contains('E') {
                    t.push_str(".0");
                }
                t
            }
        }
        serde_json::Value::String(s) => {
            let mut out = String::from("\"");
            for c in s.chars() {
                match c {
                    '"' => out.push_str("\\\""),
                    '\\' => out.push_str("\\\\"),
                    '\n' => out.push_str("\\n"),
                    '\r' => out.push_str("\\r"),
                    '\t' => out.push_str("\\t"),
                    c if (c as u32) < 0x20 => out.push_str(&format!("\\u{:04x}", c as u32)),
                    c if (c as u32) > 0x7e => {
                        let mut buf = [0u16; 2];
                        for u in c.encode_utf16(&mut buf) {
                            out.push_str(&format!("\\u{:04x}", u));
                        }
                    }
                    c => out.push(c),
                }
            }
            out.push('"');
            out
        }
        serde_json::Value::Array(a) => {
            let itens: Vec<String> = a.iter().map(canonical).collect();
            format!("[{}]", itens.join(", "))
        }
        serde_json::Value::Object(m) => {
            let mut pares: Vec<(&String, &serde_json::Value)> = m.iter().collect();
            pares.sort_by(|a, b| a.0.cmp(b.0));
            let itens: Vec<String> = pares
                .iter()
                .map(|(k, val)| {
                    let chave = canonical(&serde_json::Value::String((*k).clone()));
                    format!("{}{}{}", chave, ": ", canonical(val))
                })
                .collect();
            format!("{{{}}}", itens.join(", "))
        }
    }
}

