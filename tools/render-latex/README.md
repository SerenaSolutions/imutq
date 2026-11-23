# Render de LaTeX para PDF (local, sem servico externo)

Pipeline: `extrair.py` separa as expressoes ($$ e $) do texto, `rodar.js` desenha cada uma
com MathJax (SVG), `montar.py` converte em PNG e monta o PDF com reportlab.

Resultado medido no curso IBM Basics of Quantum Information: 502 expressoes unicas, 502
renderizadas, zero LaTeX cru no PDF final.

Dependencias: node, `npm i mathjax-full`, python com cairosvg, reportlab e PyMuPDF.

Nota: este diretorio contem apenas o script. O texto do curso e da IBM e nao esta no repositorio.
