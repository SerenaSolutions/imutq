import re, json, os
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
    Image as RLImage, PageBreak, KeepTogether)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

D="/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("DV",D+"DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DVB",D+"DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DVI",D+"DejaVuSerif.ttf"))
pdfmetrics.registerFont(TTFont("DVBI",D+"DejaVuSerif-Bold.ttf"))
pdfmetrics.registerFontFamily("DV",normal="DV",bold="DVB",italic="DVI",boldItalic="DVBI")

ex=json.load(open("exprs.json"))
t=open("texto.txt").read()

# --- recorta o miolo: do 1o cabecalho de licao em diante, sem o indice inicial
def corte(t):
    i=t.index("Single systems — Introduction\nIntroduction")
    return t[i:]
t=corte(t)

# --- normaliza markdown cru
t=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',lambda m:m.group(1).replace("\n"," "),t)   # links -> so o texto
t=re.sub(r'\(definition:\s*([^)]*)\)',lambda m:"  ["+re.sub(r'\s+',' ',m.group(1)).strip()+"]",t)
t=re.sub(r'^> ?','',t,flags=re.M)
t=re.sub(r'\*\*([^*]+)\*\*',r'<b>\1</b>',t)
t=re.sub(r'(?<![*\w])\*([^*\n]+?)\*(?!\w)',r'<i>\1</i>',t)

LICOES=[("Single systems","Introduction"),("Single systems","Classical information"),
("Single systems","Quantum information"),("Multiple systems","Introduction"),
("Multiple systems","Quantum information"),("Quantum circuits","Introduction"),
("Quantum circuits","Circuits"),("Entanglement in action","Introduction"),
("Entanglement in action","Quantum teleportation"),("Entanglement in action","Superdense coding"),
("Entanglement in action","The CHSH game")]
cab=re.compile(r'^(Single systems|Multiple systems|Quantum circuits|Entanglement in action) — (.+)$',re.M)
pos=[(m.start(),m.end(),m.group(1),m.group(2)) for m in cab.finditer(t)]

PAGEW=A4[0]-36*mm
def img(h,display):
    p=f"png/{h}.png"
    w,hh=Image.open(p).size
    # escala: pixel -> pt coerente com o corpo de 10pt
    k=0.20 if display else 0.205
    W,H=w*k,hh*k
    if display and W>PAGEW: H*=PAGEW/W; W=PAGEW
    return p,W,H

body=ParagraphStyle("b",fontName="DV",fontSize=10,leading=15,spaceAfter=6)
h1=ParagraphStyle("h1",fontName="DVB",fontSize=20,leading=24,spaceAfter=4,textColor=colors.HexColor("#0b1f3a"))
modl=ParagraphStyle("m",fontName="DV",fontSize=9,textColor=colors.HexColor("#5b6b82"),spaceAfter=10)
h3=ParagraphStyle("h3",fontName="DVB",fontSize=13,leading=17,spaceBefore=12,spaceAfter=6,textColor=colors.HexColor("#8a6a1a"))
h4=ParagraphStyle("h4",fontName="DVB",fontSize=11,leading=15,spaceBefore=8,spaceAfter=4,textColor=colors.HexColor("#0b1f3a"))
cap=ParagraphStyle("c",fontName="DVI",fontSize=8.5,textColor=colors.HexColor("#6b7686"),spaceAfter=2)
li=ParagraphStyle("li",parent=body,leftIndent=14,bulletIndent=2)

def esc(s): return s.replace("&","&amp;").replace("<b>","\0b").replace("</b>","\0/b").replace("<i>","\0i").replace("</i>","\0/i").replace("<","&lt;").replace(">","&gt;").replace("\0b","<b>").replace("\0/b","</b>").replace("\0i","<i>").replace("\0/i","</i>")

def inline(s):
    # marcador inline vira <img> alinhado na linha de base
    def r(m):
        h=m.group(1); e=ex.get(h)
        if not e: return ""
        p,W,H=img(h,e["display"])
        return f'<img src="{p}" width="{W:.1f}" height="{H:.1f}" valign="-{H*0.18:.1f}"/>'
    return re.sub(r'@@([0-9a-f]{10})@@',r,esc(s))

story=[]
def novo_corpo(trecho):
    # separa por linhas em branco; blocos de formula ficam isolados
    out=[]
    for par in re.split(r'\n\s*\n',trecho.strip()):
        par=par.strip()
        if not par: continue
        # blocos de formula (display) sozinhos no paragrafo
        mm=re.fullmatch(r'@@([0-9a-f]{10})@@',par)
        if mm and ex.get(mm.group(1),{}).get("display"):
            p,W,H=img(mm.group(1),True)
            out.append(Spacer(1,3)); out.append(RLImage(p,width=W,height=H,hAlign="CENTER")); out.append(Spacer(1,5))
            continue
        # linhas que so tem um bloco + texto curto -> trata cada pedaco
        partes=re.split(r'(@@[0-9a-f]{10}@@)',par)
        buf=""
        for pt in partes:
            m=re.fullmatch(r'@@([0-9a-f]{10})@@',pt)
            if m and ex.get(m.group(1),{}).get("display"):
                if buf.strip(): out.append(Paragraph(inline(re.sub(r'\s*\n\s*',' ',buf)),body)); buf=""
                p,W,H=img(m.group(1),True)
                out.append(Spacer(1,3)); out.append(RLImage(p,width=W,height=H,hAlign="CENTER")); out.append(Spacer(1,5))
            else: buf+=pt
        if buf.strip():
            txt=buf.strip()
            if txt.startswith("#### "): out.append(Paragraph(inline(txt[5:]),h4)); continue
            if re.fullmatch(r'[A-Z][^\n.]{2,70}',txt) and "\n" not in txt and not txt.endswith((".",":",",")):
                out.append(Paragraph(inline(txt),h3)); continue
            lines=[l for l in txt.split("\n")]
            if all(re.match(r'^\s*(\d+\.|-)\s',l) or l.startswith("  ") or not l.strip() for l in lines) and re.match(r'^\s*(\d+\.|-)\s',lines[0]):
                for l in lines:
                    if l.strip(): 
                        mm=re.match(r'^\s*(\d+\.|-)\s+(.*)$',l)
                        out.append(Paragraph(inline(mm.group(2)) if mm else inline(l.strip()),li,bulletText=(mm.group(1) if mm else "")))
                continue
            out.append(Paragraph(inline(re.sub(r'\s*\n\s*',' ',txt)),body))
    return out

# capa
capaT=ParagraphStyle("ct",fontName="DVB",fontSize=26,leading=32,textColor=colors.HexColor("#0b1f3a"),spaceAfter=10)
capaS=ParagraphStyle("cs",fontName="DV",fontSize=12,leading=18,textColor=colors.HexColor("#3b4a60"),spaceAfter=6)
story+= [Spacer(1,60*mm),Paragraph("Basics of Quantum Information",capaT),
 Paragraph("Curso completo, com as fórmulas renderizadas",capaS),
 Spacer(1,8*mm),
 Paragraph("Fonte: IBM Quantum Learning, curso de John Watrous.<br/>Texto original em inglês. Cópia pessoal de estudo, sem redistribuição.",capaS),
 Spacer(1,6*mm),
 Paragraph("11 lições · 4 módulos",capaS),
 Spacer(1,60*mm),
 Paragraph("As equações foram redesenhadas a partir do LaTeX original por um motor de fórmulas local (MathJax). Nenhum texto foi alterado.",
   ParagraphStyle("n",fontName="DVI",fontSize=8.5,textColor=colors.HexColor("#6b7686"))),
 PageBreak()]

modulo_anterior=None
for k,(a,b,mod,tit) in enumerate(pos):
    fim=pos[k+1][0] if k+1<len(pos) else len(t)
    trecho=t[b:fim]
    # o titulo da licao se repete como 1a linha do corpo (ex.: "Introduction")
    trecho=re.sub(r'^\s*'+re.escape(tit)+r'\s*\n','',trecho,count=1)
    story.append(Paragraph(f"{mod.upper()} · LIÇÃO {k+1} DE 11",modl))
    story.append(Paragraph(tit,h1))
    story+=novo_corpo(trecho)
    story.append(PageBreak())

def rodape(c,doc):
    c.saveState(); c.setFont("DV",8); c.setFillColor(colors.HexColor("#8b95a5"))
    c.drawCentredString(A4[0]/2,12*mm,f"Basics of Quantum Information · IBM Quantum Learning · {doc.page}")
    c.restoreState()
doc=BaseDocTemplate("curso_ibm_com_formulas.pdf",pagesize=A4,leftMargin=18*mm,rightMargin=18*mm,topMargin=18*mm,bottomMargin=20*mm,
    title="Basics of Quantum Information, curso completo com fórmulas",author="Serena Solutions")
doc.addPageTemplates([PageTemplate(id="p",frames=[Frame(18*mm,20*mm,A4[0]-36*mm,A4[1]-38*mm,id="f")],onPage=rodape)])
doc.build(story)
print("PDF gerado:",os.path.getsize("curso_ibm_com_formulas.pdf"),"bytes")
