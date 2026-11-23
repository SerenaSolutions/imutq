const {mathjax}=require('/tmp/mj/node_modules/mathjax-full/js/mathjax.js');
const {TeX}=require('/tmp/mj/node_modules/mathjax-full/js/input/tex.js');
const {SVG}=require('/tmp/mj/node_modules/mathjax-full/js/output/svg.js');
const {liteAdaptor}=require('/tmp/mj/node_modules/mathjax-full/js/adaptors/liteAdaptor.js');
const {RegisterHTMLHandler}=require('/tmp/mj/node_modules/mathjax-full/js/handlers/html.js');
const {AllPackages}=require('/tmp/mj/node_modules/mathjax-full/js/input/tex/AllPackages.js');
const ad=liteAdaptor(); RegisterHTMLHandler(ad);
const doc=mathjax.document('',{InputJax:new TeX({packages:AllPackages}),OutputJax:new SVG({fontCache:'none'})});
function svg(tex,display=true){
  const n=doc.convert(tex,{display}); return ad.innerHTML(n);
}
module.exports={svg};
if(require.main===module){
  const t=String.raw`\begin{pmatrix} 1 & 0 \\ 0 & 1 \end{pmatrix} = \mathbb{I},\quad \vert +\rangle=\tfrac{1}{\sqrt2}(\vert0\rangle+\vert1\rangle)`;
  require('fs').writeFileSync('/tmp/mj/t.svg', svg(t).replace(/<mjx-container[^>]*>|<\/mjx-container>/g,''));
  console.log("svg ok", require('fs').statSync('/tmp/mj/t.svg').size,"bytes");
}
