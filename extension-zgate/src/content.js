// SPDX-License-Identifier: Apache-2.0
// Z-Gate no Gmail: intercepta o envio, avalia e sela a decisao.
(function () {
  const GENESIS = "0".repeat(64);
  const MARCA = "data-zgate";

  const txt = el => (el ? (el.innerText || el.value || "").trim() : "");

  function acharCorpo(dialog) {
    return dialog.querySelector('div[aria-label="Message Body"], div[role="textbox"][contenteditable="true"]');
  }

  function destinatarios(dialog) {
    const alvos = dialog.querySelectorAll('input[aria-label*="To"], input[aria-label*="Para"], span[email]');
    const out = [];
    alvos.forEach(a => {
      if (a.getAttribute && a.getAttribute("email")) out.push(a.getAttribute("email"));
      else if (a.value) a.value.split(/[,;]/).forEach(v => out.push(v.trim()));
      else if (a.textContent && a.textContent.includes("@")) out.push(a.textContent.trim());
    });
    return [...new Set(out)].filter(Boolean);
  }

  function coletar(dialog) {
    const corpo = acharCorpo(dialog);
    const assuntoEl = dialog.querySelector('input[name="subjectbox"], input[aria-label*="Subject"], input[aria-label*="Assunto"]');
    const anexos = dialog.querySelectorAll('div[aria-label*="Attachment"], span[aria-label*="Attachment"]').length;
    const imagens = corpo ? corpo.querySelectorAll("img").length : 0;
    return {
      para: destinatarios(dialog),
      assunto: txt(assuntoEl),
      corpo: txt(corpo),
      anexos,
      imagens,
      url: location.href
    };
  }

  function selar(registro, anterior) {
    const prev = anterior ? anterior.sha3 : GENESIS;
    const base = {
      ts: new Date().toISOString(),
      veredito: registro.veredito,
      motivos: registro.motivos,
      hash_conteudo: sha3_256(canonical({ para: registro.para, assunto: registro.assunto, corpo: registro.corpo })),
      prev_sha3: prev
    };
    return { ...base, sha3: sha3_256(canonical(base)) };
  }

  async function gravar(selo) {
    const { gates = [] } = await chrome.storage.local.get("gates");
    gates.push(selo);
    await chrome.storage.local.set({ gates });
  }

  function pintar(dialog, res, aoForcar) {
    let barra = dialog.querySelector(`[${MARCA}]`);
    if (!barra) {
      barra = document.createElement("div");
      barra.setAttribute(MARCA, "1");
      barra.style.cssText = "display:flex;gap:8px;align-items:center;font:12px system-ui;padding:6px 10px;margin:4px 0;border-radius:6px;flex-wrap:wrap";
      const alvo = acharCorpo(dialog);
      if (alvo && alvo.parentElement) alvo.parentElement.insertBefore(barra, alvo);
    }
    const cor = res.veredito === "1" ? "#1a7f37" : res.veredito === "0" ? "#b62324" : "#9e6a03";
    barra.style.background = cor; barra.style.color = "#fff";
    barra.innerHTML = "";
    const rotulo = document.createElement("b");
    rotulo.textContent = `Z-Gate: ${res.veredito}` + (res.motivos.length ? " — " + res.motivos.map(m => m.texto).join("; ") : " — sem impedimento");
    barra.appendChild(rotulo);
    if (res.veredito !== "1") {
      const b = document.createElement("button");
      b.textContent = "enviar mesmo assim (registrado)";
      b.style.cssText = "margin-left:auto;background:#fff;color:#111;border:0;border-radius:4px;padding:3px 8px;cursor:pointer";
      b.onclick = () => { aoForcar(); barra.remove(); };
      barra.appendChild(b);
    }
  }

  function instalar(dialog) {
    if (dialog.getAttribute(MARCA + "-ligado")) return;
    dialog.setAttribute(MARCA + "-ligado", "1");

    dialog.addEventListener("click", async e => {
      const btn = e.target.closest('div[role="button"][data-tooltip^="Send"], div[role="button"][aria-label^="Send"], div[role="button"][data-tooltip^="Enviar"]');
      if (!btn || btn.getAttribute(MARCA + "-ok")) return;
      const msg = coletar(dialog);
      if (!msg.corpo && !msg.assunto) return; // rascunho vazio, deixa o Gmail agir
      const { gates = [] } = await chrome.storage.local.get("gates");
      const res = avaliar(msg, true);
      const selo = selar({ ...res, ...msg }, gates[gates.length - 1] || null);
      await gravar(selo);
      if (res.veredito !== "1") {
        e.preventDefault(); e.stopPropagation();
        pintar(dialog, res, async () => {
          btn.setAttribute(MARCA + "-ok", "1");
          const forca = selar({ veredito: "FORCADO", motivos: [{ regra: "OVERRIDE", texto: "usuario enviou contra o gate" }], para: msg.para, assunto: msg.assunto, corpo: msg.corpo }, selo);
          await gravar(forca);
          btn.click();
        });
      } else {
        pintar(dialog, res, () => {});
      }
    }, true);
  }

  function varrer() {
    document.querySelectorAll('div[role="dialog"]').forEach(d => {
      if (acharCorpo(d)) instalar(d);
    });
  }
  new MutationObserver(varrer).observe(document.body, { childList: true, subtree: true });
  varrer();
})();
