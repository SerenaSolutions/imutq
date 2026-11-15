// SPDX-License-Identifier: Apache-2.0
// Serializacao canonica identica a json.dumps(sort_keys=True): chaves ordenadas,
// separadores ", " e ": ", nao-ASCII escapado.
function esc(s){
  let out='"';
  for(const ch of s){
    const c=ch.codePointAt(0);
    if(ch==='"') out+='\\"';
    else if(ch==='\\') out+='\\\\';
    else if(ch==='\n') out+='\\n';
    else if(ch==='\r') out+='\\r';
    else if(ch==='\t') out+='\\t';
    else if(c<0x20) out+='\\u'+c.toString(16).padStart(4,"0");
    else if(c>0x7e){ for(const u of ch.split('')) for(let i=0;i<u.length;i++)
      out+='\\u'+u.charCodeAt(i).toString(16).padStart(4,"0"); }
    else out+=ch;
  }
  return out+'"';
}
function num(n){
  if(Number.isInteger(n)) return String(n);
  let t=String(n);
  if(!t.includes('.')&&!t.includes('e')&&!t.includes('E')) t+='.0';
  return t;
}
function canonical(v){
  if(v===null) return "null";
  if(typeof v==="boolean") return v?"true":"false";
  if(typeof v==="number") return num(v);
  if(typeof v==="string") return esc(v);
  if(Array.isArray(v)) return "["+v.map(canonical).join(", ")+"]";
  const ks=Object.keys(v).sort();
  return "{"+ks.map(k=>esc(k)+": "+canonical(v[k])).join(", ")+"}";
}
if (typeof module !== "undefined") module.exports = { canonical };
