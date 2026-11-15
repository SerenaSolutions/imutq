// SPDX-License-Identifier: Apache-2.0
// Nucleo do selo: hash do conteudo + encadeamento. Nao depende de rede.
const GENESIS = "0".repeat(64);

function corpoSelo(s){
  return { indice: s.indice, ts: s.ts, url: s.url, titulo: s.titulo, texto: s.texto, prev_sha3: s.prev_sha3 };
}

function criarSelo({ texto, url, titulo, anterior, indice, agora }) {
  const prev = anterior ? anterior.sha3 : GENESIS;
  const base = { indice, ts: agora, url: url || "", titulo: titulo || "", texto, prev_sha3: prev };
  return { ...base, sha3: sha3_256(canonical(base)) };
}

function verificarCadeia(selos) {
  const falhas = [];
  let esperadoPrev = GENESIS;
  selos.forEach((s, i) => {
    const calc = sha3_256(canonical(corpoSelo(s)));
    if (calc !== s.sha3) falhas.push({ indice: s.indice ?? i + 1, motivo: "hash do selo diverge" });
    if (s.prev_sha3 !== esperadoPrev) falhas.push({ indice: s.indice ?? i + 1, motivo: "elo quebrado com o selo anterior" });
    esperadoPrev = calc;
  });
  return { ok: falhas.length === 0, total: selos.length, falhas };
}

if (typeof module !== "undefined") module.exports = { criarSelo, verificarCadeia, corpoSelo, GENESIS };
