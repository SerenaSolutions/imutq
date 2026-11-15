// SPDX-License-Identifier: Apache-2.0
// Regra de verificacao do recibo IMUT-Q v2, no navegador.
const DENTRO = ["assinatura","chave_publica","hash_payload_canonico","esquema"];

function payloadAssinado(r){
  const o={...r};
  for(const k of DENTRO) delete o[k];
  if("versao_imutq" in o){ o.versao_multiq=o.versao_imutq; delete o.versao_imutq; }
  return o;
}

function verificarRecibo(r, sha3){
  const canon = canonical(payloadAssinado(r));
  const hash = sha3(canon);
  const gravado = (r.hash_payload_canonico||"").toLowerCase();
  const integro = hash === gravado;
  return {
    teste: r.teste || "?",
    integro,
    hash_calculado: hash,
    hash_gravado: gravado,
    veredito: r.veredito || "?",
    job_id: r.job_id || "?",
    provedor: r.provedor || "?",
    backend: r.backend || "?",
    proveniencia: r.proveniencia || "?",
    shots: r.shots_efetivo || r.shots_pedido || "?",
    assinatura: r.assinatura ? "presente" : "ausente",
    mensagem: integro
      ? (r.assinatura ? "integro; assinatura presente (conferencia criptografica no nucleo)"
                     : "integro, porem SEM assinatura")
      : "conteudo divergiu do hash gravado: recibo invalido"
  };
}

if (typeof module !== "undefined") module.exports = { verificarRecibo, payloadAssinado };
