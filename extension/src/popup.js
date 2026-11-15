// SPDX-License-Identifier: Apache-2.0
const $=id=>document.getElementById(id);
const inEl=$("in"), out=$("out");

inEl.addEventListener("dragover",e=>e.preventDefault());
inEl.addEventListener("drop",async e=>{
  e.preventDefault();
  const f=e.dataTransfer.files[0]; if(f) inEl.value=await f.text();
});

function linha(k,v,mono){ return `<div class="row"><span class="k">${k}</span><span class="${mono?'mono':''}">${v}</span></div>`; }

function statusAssinatura(codigo){
  if (codigo === 1) return '<span class="ok" style="color:#3fb950;font-weight:700">assinatura ML-DSA-44 CONFIRMADA</span>';
  if (codigo === 0) return '<span class="bad" style="color:#f85149;font-weight:700">ASSINATURA INVALIDA</span>';
  if (codigo === -1) return '<span class="bad">recibo ilegivel</span>';
  return '<span style="color:#8b949e">wasm indisponivel nesta execucao</span>';
}

async function render(recibos){
  out.style.display="block"; out.innerHTML="";
  for(const r of recibos){
    const c = {...r};
    const base = verificarRecibo(c, sha3_256);
    let codigo = null;
    if (base.integro) codigo = await verificarAssinatura(c);
    const selo = !base.integro ? '<span class="selo bad">INVALIDO</span>'
      : (base.veredito==="REFUSED" ? '<span class="selo ref">REFUSED</span>'
      : (base.veredito==="1" ? '<span class="selo ok">1</span>' : '<span class="selo ok">0</span>'));
    out.insertAdjacentHTML("beforeend", selo
      + linha("teste", base.teste) + linha("provedor", base.provedor)
      + linha("backend", base.backend) + linha("job_id", base.job_id, true)
      + linha("shots", base.shots) + linha("proveniencia", base.proveniencia)
      + linha("assinatura", statusAssinatura(codigo))
      + linha("hash", base.hash_calculado.slice(0,24)+"...", true)
      + `<div class="mono" style="margin-top:6px">${base.mensagem}</div>`);
  }
}

$("go").addEventListener("click",async()=>{
  try{
    const parsed=JSON.parse(inEl.value);
    const lista=Array.isArray(parsed)?parsed:(parsed.recibos||[parsed]);
    await render(lista);
    chrome.storage.local.set({ultimo: new Date().toISOString()});
  }catch(e){
    out.style.display="block";
    out.innerHTML='<span class="selo bad">ERRO</span><div class="mono">JSON invalido: '+e.message+'</div>';
  }
});
