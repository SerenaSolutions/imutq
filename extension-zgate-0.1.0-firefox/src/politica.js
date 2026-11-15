// SPDX-License-Identifier: Apache-2.0
// Z-Gate: politica de pre-envio. Declarada antes do dado, nunca escolhida depois.
// Veredito trivalente: 1 aprova, 0 bloqueia, REFUSED quando nao ha evidencia suficiente.

const RE_EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
const RE_CPF = /\b\d{3}\.\d{3}\.\d{3}-\d{2}\b/;
const RE_CARTAO = /\b(?:\d[ -]?){13,19}\b/;

function avaliar(msg, cadeiaOk) {
  const motivos = [];
  const dest = (msg.para || []).filter(d => RE_EMAIL.test(String(d).trim()));

  if (dest.length === 0) motivos.push({ regra: "R1", efeito: "0", texto: "sem destinatario valido" });
  if (!msg.assunto || !String(msg.assunto).trim()) motivos.push({ regra: "R2", efeito: "REFUSED", texto: "assunto vazio: nao ha contexto para aprovar" });
  if (!msg.corpo || !String(msg.corpo).trim()) motivos.push({ regra: "R3", efeito: "0", texto: "corpo vazio" });
  if (RE_CPF.test(msg.corpo || "")) motivos.push({ regra: "R4", efeito: "0", texto: "CPF no corpo" });
  if (RE_CARTAO.test(msg.corpo || "")) motivos.push({ regra: "R5", efeito: "0", texto: "sequencia compativel com cartao no corpo" });
  if (msg.anexos > 0) motivos.push({ regra: "R6", efeito: "REFUSED", texto: "anexo presente: o gate nao sela anexo" });
  if (msg.imagens > 0) motivos.push({ regra: "R7", efeito: "REFUSED", texto: "imagem embutida: conteudo nao verificavel" });
  if (cadeiaOk === false) motivos.push({ regra: "R8", efeito: "REFUSED", texto: "cadeia de selos quebrada" });

  const efeitos = new Set(motivos.map(m => m.efeito));
  const veredito = efeitos.has("0") ? "0" : (efeitos.has("REFUSED") ? "REFUSED" : "1");
  return { veredito, motivos };
}

if (typeof module !== "undefined") module.exports = { avaliar };
