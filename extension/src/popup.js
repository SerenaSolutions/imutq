// SPDX-License-Identifier: Apache-2.0
const $ = (id) => document.getElementById(id);
const inEl = $("in"), out = $("out");

inEl.addEventListener("dragover", (e) => e.preventDefault());
inEl.addEventListener("drop", async (e) => {
  e.preventDefault();
  const f = e.dataTransfer.files[0];
  if (f) inEl.value = await f.text();
});

function linha(k, v, mono) {
  return `<div class="row"><span class="k">${k}</span><span class="${mono ? "mono" : ""}">${v}</span></div>`;
}

function statusAssinatura(codigo) {
  if (codigo === 1) return '<span style="color:#3fb950;font-weight:700">' + T.sigOk + "</span>";
  if (codigo === 0) return '<span style="color:#f85149;font-weight:700">' + T.sigBad + "</span>";
  if (codigo === -1) return '<span style="color:#f85149">' + T.sigIlegivel + "</span>";
  return '<span style="color:#8b949e">' + T.sigSemWasm + "</span>";
}

function selo(recibo, integro) {
  if (!integro) return '<span class="selo bad">' + T.invalido + "</span>";
  if (recibo.veredito === "REFUSED") return '<span class="selo ref">REFUSED</span>';
  return recibo.veredito === "1"
    ? '<span class="selo ok">1</span>'
    : '<span class="selo ok">0</span>';
}

async function render(recibos) {
  out.style.display = "block";
  out.innerHTML = "";
  let integros = 0;

  for (const r of recibos) {
    const c = { ...r };
    const base = verificarRecibo(c, sha3_256);
    let codigo = null;
    if (base.integro) codigo = await verificarAssinatura(c);
    if (base.integro) integros += 1;

    out.insertAdjacentHTML(
      "beforeend",
      selo(base, base.integro) +
        linha(T.campos.teste, base.teste) +
        linha(T.campos.provedor, base.provedor) +
        linha(T.campos.backend, base.backend) +
        linha(T.campos.job_id, base.job_id, true) +
        linha(T.campos.shots, base.shots) +
        linha(T.campos.proveniencia, base.proveniencia) +
        linha(T.campos.assinatura, statusAssinatura(codigo)) +
        linha(T.campos.hash, base.hash_calculado.slice(0, 24) + "...", true) +
        `<div class="mono" style="margin-top:6px">${base.integro ? T.msgInteiro : base.mensagem}</div>`
    );
  }

  // resumo do lote, para nao virar parede de blocos iguais
  if (recibos.length > 1) {
    const resumo = document.createElement("div");
    resumo.className = "resumo";
    resumo.textContent = T.lote(integros, recibos.length);
    out.prepend(resumo);
  }
}

function mostrarUltima(quando) {
  const alvo = $("ultima");
  if (!alvo) return;
  alvo.textContent = T.ultima + ": " + (quando ? new Date(quando).toLocaleString() : T.nunca);
}

function carregarUltima() {
  try {
    chrome.storage.local.get(["ultimo"], (d) => mostrarUltima(d && d.ultimo));
  } catch (e) {
    mostrarUltima(null);
  }
}

$("go").addEventListener("click", async () => {
  try {
    const parsed = JSON.parse(inEl.value);
    const lista = Array.isArray(parsed) ? parsed : parsed.recibos || [parsed];
    await render(lista);
    const agora = new Date().toISOString();
    chrome.storage.local.set({ ultimo: agora });
    mostrarUltima(agora);
  } catch (e) {
    out.style.display = "block";
    out.innerHTML = '<span class="selo bad">' + T.erro + '</span><div class="mono">' + T.jsonRuim + e.message + "</div>";
  }
});

// rotulos e rodape
$("titulo").textContent = T.titulo;
$("sub").textContent = T.sub;
inEl.placeholder = T.dica;
$("go").textContent = T.botao;
$("legenda").textContent = T.legenda;
$("link-privacidade").textContent = T.privacidade;
try {
  const v = chrome.runtime.getManifest ? chrome.runtime.getManifest().version : "";
  if (v) $("versao").textContent = "v" + v;
} catch (e) {}

carregarUltima();
