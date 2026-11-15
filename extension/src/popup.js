// SPDX-License-Identifier: Apache-2.0
const $=id=>document.getElementById(id);
const inEl=$("in"), out=$("out");

inEl.addEventListener("dragover",e=>e.preventDefault());
inEl.addEventListener("drop",async e=>{
  e.preventDefault();
  const f=e.dataTransfer.files[0]; if(f) inEl.value=await f.text();
});

function linha(k,v,mono){ return `<div class="row"><span class="k">${k}</span><span class="${mono?'mono':''}">${v}</span></div>`; }

function render(results){
  out.style.display="block";
  out.innerHTML="";
  for(const r of results){
    const selo = !r.integro ? '<span class="selo bad">INVALIDO</span>'
      : (r.veredito==="REFUSED" ? '<span class="selo ref">REFUSED</span>'
      : (r.veredito==="1" ? '<span class="selo ok">1</span>' : '<span class="selo ok">0</span>'));
    out.insertAdjacentHTML("beforeend", selo
      + linha("teste", r.teste) + linha("provedor", r.provedor)
      + linha("backend", r.backend) + linha("job_id", r.job_id, true)
      + linha("shots", r.shots) + linha("proveniencia", r.proveniencia)
      + linha("assinatura", r.assinatura)
      + linha("hash", r.hash_calculado.slice(0,24)+"...", true)
      + `<div class="mono" style="margin-top:6px">${r.mensagem}</div>`);
  }
}

$("go").addEventListener("click",()=>{
  try{
    const parsed=JSON.parse(inEl.value);
    const lista=Array.isArray(parsed)?parsed:(parsed.recibos||[parsed]);
    render(lista.map(r=>verificarRecibo(r, sha3_256)));
    chrome.storage.local.set({ultimo: new Date().toISOString()});
  }catch(e){
    out.style.display="block";
    out.innerHTML='<span class="selo bad">ERRO</span><div class="mono">JSON invalido: '+e.message+'</div>';
  }
});
