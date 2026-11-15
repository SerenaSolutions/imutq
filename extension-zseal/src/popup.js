// SPDX-License-Identifier: Apache-2.0
const $=id=>document.getElementById(id);
async function carregar(){ const {selos=[]}=await chrome.storage.local.get("selos"); return selos; }
function render(selos, res){
  $("estado").innerHTML = selos.length
    ? `<div class="${res.ok?'ok':'bad'}">${res.ok?'CADEIA INTEGRA':'CADEIA QUEBRADA'} — ${selos.length} selos</div>`
    : '<div class="sub">Nenhum selo ainda. Selecione um trecho numa pagina e use o botao direito.</div>';
  $("lista").innerHTML = selos.slice(-5).reverse().map(s=>
    `<div class="selo"><div class="idx">#${s.indice} · ${s.ts}</div>
     <div class="txt">${(s.texto||"").slice(0,120).replace(/</g,"&lt;")}</div>
     <div class="mono">${s.sha3.slice(0,32)}...</div>
     <div class="mono">prev: ${s.prev_sha3.slice(0,16)}...</div></div>`).join("");
  if(res.falhas.length) $("lista").innerHTML += res.falhas.map(f=>`<div class="bad">#${f.indice}: ${f.motivo}</div>`).join("");
}
(async()=>{ const selos=await carregar(); render(selos, verificarCadeia(selos)); })();
$("verificar").onclick=async()=>{ const selos=await carregar(); render(selos, verificarCadeia(selos)); };
$("exportar").onclick=async()=>{
  const selos=await carregar(); const res=verificarCadeia(selos);
  const blob=new Blob([JSON.stringify({gerado_em:new Date().toISOString(),integro:res.ok,selos},null,1)],{type:"application/json"});
  const a=document.createElement("a"); a.href=URL.createObjectURL(blob); a.download="z-seal.json"; a.click();
};
$("limpar").onclick=async()=>{ await chrome.storage.local.clear(); location.reload(); };
