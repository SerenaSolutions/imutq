// SPDX-License-Identifier: Apache-2.0
const $=id=>document.getElementById(id);
(async()=>{
  const {gates=[]}=await chrome.storage.local.get("gates");
  if(!gates.length){ $("lista").innerHTML='<div class="sub">Nenhuma decisao ainda. Abra o Gmail e tente enviar.</div>'; return; }
  $("lista").innerHTML = gates.slice(-8).reverse().map(g=>{
    const cls = g.veredito==="1"?"ok":g.veredito==="0"?"bad":g.veredito==="FORCADO"?"force":"ref";
    const motivos = (g.motivos||[]).map(m=>m.texto).join("; ") || "sem impedimento";
    return `<div class="item"><div class="v ${cls}">${g.veredito} · ${g.ts||""}</div>
      <div class="mono">${motivos}</div>
      <div class="mono">${(g.sha3||"").slice(0,32)}...</div></div>`;
  }).join("");
})();
$("exp").onclick=async()=>{
  const {gates=[]}=await chrome.storage.local.get("gates");
  const blob=new Blob([JSON.stringify({gerado_em:new Date().toISOString(),gates},null,1)],{type:"application/json"});
  const a=document.createElement("a"); a.href=URL.createObjectURL(blob); a.download="z-gate.json"; a.click();
};
