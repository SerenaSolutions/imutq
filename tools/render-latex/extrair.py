import fitz, re, json, hashlib
d=fitz.open("../incoming_files/4f4759322_curso_completo.pdf")
t="\n".join(p.get_text() for p in d)
# remove rodape/numeracao de pagina
t=re.sub(r'ARQ-ZYQL-001 · \d+\s*','',t)
# o PDF repete cada pagina como texto + imagem do layout; ficamos so com o texto linear
exprs={}
def reg(m,display):
    tex=m.group(1).strip()
    h=hashlib.md5((("D" if display else "I")+tex).encode()).hexdigest()[:10]
    exprs[h]={"tex":tex,"display":display}
    return f"@@{h}@@"
t=re.sub(r'\$\$(.*?)\$\$',lambda m:reg(m,True),t,flags=re.S)
t=re.sub(r'(?<!\$)\$([^$\n]+?)\$(?!\$)',lambda m:reg(m,False),t)
open("texto.txt","w").write(t)
json.dump(exprs,open("exprs.json","w"))
print("expressoes unicas:",len(exprs),"| blocos:",sum(1 for v in exprs.values() if v['display']),"| inline:",sum(1 for v in exprs.values() if not v['display']))
