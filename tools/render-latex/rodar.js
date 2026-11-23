const {svg}=require('./render.js'); const fs=require('fs');
const ex=JSON.parse(fs.readFileSync('exprs.json')); fs.mkdirSync('svg',{recursive:true});
let ok=0,bad=[];
for(const [h,v] of Object.entries(ex)){
  let tex=v.tex.replace(/\\tag\{[^}]*\}/g,'');
  try{
    let s=svg(tex,v.display);
    if(/merror|data-mjx-error|Undefined control/.test(s)) throw new Error('mjx-error');
    s=s.replace(/<mjx-container[^>]*>|<\/mjx-container>/g,'');
    fs.writeFileSync(`svg/${h}.svg`,s); ok++;
  }catch(e){ bad.push([h,v.tex.slice(0,60),String(e.message).slice(0,40)]); }
}
console.log("ok",ok,"de",Object.keys(ex).length); if(bad.length){console.log("falhas:",bad.length);bad.slice(0,8).forEach(b=>console.log(" ",JSON.stringify(b)));}
