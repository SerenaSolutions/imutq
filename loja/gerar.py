import json, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

D="/usr/share/fonts/truetype/dejavu/"
def F(sz,b=False,m=False):
    n="DejaVuSansMono" if m else "DejaVuSans"
    return ImageFont.truetype(D+n+("-Bold" if b else "")+".ttf",sz)

BG=(14,17,22); CARD=(22,27,34); LINE=(48,54,61); TXT=(230,237,243)
DIM=(139,148,158); BLUE=(31,111,235); OK=(26,127,55); BAD=(182,35,36); REF=(158,106,3)
GREEN=(63,185,80); CYAN=(56,189,248)

def grad(w,h,c1,c2):
    im=Image.new("RGB",(w,h)); px=im.load()
    for y in range(h):
        for x in range(w):
            t=(x/w*0.6+y/h*0.4)
            px[x,y]=tuple(int(c1[i]+(c2[i]-c1[i])*t) for i in range(3))
    return im

def logo(sz):
    s=sz*4
    im=grad(s,s,(10,24,48),(18,70,140)).convert("RGBA")
    m=Image.new("L",(s,s),0); ImageDraw.Draw(m).rounded_rectangle((0,0,s,s),radius=int(s*.22),fill=255)
    im.putalpha(m)
    d=ImageDraw.Draw(im)
    cx=cy=s/2
    # escudo
    pts=[(cx,s*.12),(s*.82,s*.24),(s*.82,s*.52),(cx,s*.90),(s*.18,s*.52),(s*.18,s*.24)]
    # curva do escudo mais suave
    sh=[]
    for t in range(0,101):
        u=t/100
        # lado direito: do topo ate a ponta
        x=cx+ (s*.32)*(1-u**2.2)*1.0
        y=s*.24+(s*.66)*u
        sh.append((x,y))
    right=[(cx+(s*.32)*(1-(i/60)**2.4), s*.24+(s*.66)*(i/60)) for i in range(61)]
    left=[(2*cx-x,y) for x,y in reversed(right)]
    top=[(cx,s*.12)]
    poly=top+right+left
    d.polygon(poly,fill=(255,255,255,235))
    inner=[(cx,s*.18)]+[(cx+(s*.27)*(1-(i/60)**2.4), s*.27+(s*.58)*(i/60)) for i in range(61)]
    inner+= [(2*cx-x,y) for x,y in reversed(inner[1:])]
    d.polygon(inner,fill=(12,40,86,255))
    # esfera de Bloch estilizada: circulo + elipse + eixo
    r=s*.17; cy2=s*.47
    d.ellipse((cx-r,cy2-r,cx+r,cy2+r),outline=(125,211,252,255),width=max(2,int(s*.018)))
    d.ellipse((cx-r,cy2-r*.35,cx+r,cy2+r*.35),outline=(125,211,252,200),width=max(2,int(s*.012)))
    d.line((cx,cy2-r*1.15,cx,cy2+r*1.15),fill=(125,211,252,200),width=max(2,int(s*.012)))
    # vetor de estado
    ex,ey=cx+r*.62,cy2-r*.62
    d.line((cx,cy2,ex,ey),fill=(255,255,255,255),width=max(3,int(s*.022)))
    d.ellipse((ex-s*.022,ey-s*.022,ex+s*.022,ey+s*.022),fill=(63,185,80,255))
    # check
    kx,ky=cx,s*.74
    d.line((kx-s*.075,ky,kx-s*.02,ky+s*.05),fill=(63,185,80,255),width=int(s*.03))
    d.line((kx-s*.02,ky+s*.05,kx+s*.085,ky-s*.055),fill=(63,185,80,255),width=int(s*.03))
    return im.resize((sz,sz),Image.LANCZOS)

def pill(d,xy,txt,col,font,pad=14):
    w=d.textlength(txt,font=font)
    x,y=xy
    d.rounded_rectangle((x,y,x+w+pad*2,y+font.size+pad),radius=8,fill=col)
    d.text((x+pad,y+pad/2-1),txt,font=font,fill=(255,255,255))
    return w+pad*2

# ---------------- LOGO 300 ----------------
logo(300).save("logo-300x300.png")
logo(128).save("logo-128x128.png")

# ---------------- popup (reconstrucao fiel da UI real) ----------------
def popup(img,x0,y0,rec,scale=1.0,mostrar_entrada=False):
    d=ImageDraw.Draw(img)
    W=int(340*scale); 
    f11=F(int(11*scale)); f13=F(int(13*scale)); f14b=F(int(14*scale),True)
    f10m=F(int(10*scale),m=True); f11m=F(int(11*scale),m=True)
    pad=int(14*scale)
    # medir altura
    linhas=8
    H=int((14+14+10+(110+8+36+12 if mostrar_entrada else 0)+26+linhas*22+50)*scale)
    d.rounded_rectangle((x0,y0,x0+W,y0+H),radius=int(10*scale),fill=BG,outline=LINE,width=2)
    x=x0+pad; y=y0+pad
    d.text((x,y),"IMUT-Q",font=f14b,fill=TXT); y+=int(18*scale)
    d.text((x,y),"Verificador de recibo — Serena Solutions",font=f11,fill=DIM); y+=int(22*scale)
    if mostrar_entrada:
        d.rounded_rectangle((x,y,x0+W-pad,y+int(110*scale)),radius=6,fill=CARD,outline=LINE)
        t=['{"esquema":"2.0","recibos":[{"teste":"BELL_Z",','"veredito":"1","job_id":"qbraid:qbraid:sim:','qir-sv-2ef5-qjob-6af92193c8f5...",','"provedor":"qBraid","shots_efetivo":1024,','"proveniencia":"primaria",...']
        for i,l in enumerate(t): d.text((x+8,y+8+i*int(15*scale)),l,font=f10m,fill=(201,209,217))
        y+=int(118*scale)
        d.rounded_rectangle((x,y,x0+W-pad,y+int(34*scale)),radius=6,fill=BLUE)
        tw=d.textlength("Verificar",font=f13)
        d.text((x+(W-2*pad-tw)/2,y+int(9*scale)),"Verificar",font=F(int(13*scale),True),fill=(255,255,255))
        y+=int(46*scale)
    d.line((x,y,x0+W-pad,y),fill=LINE); y+=int(10*scale)
    v=rec["ver"]; ok=rec["integro"]
    if not ok: lab,col="INVALIDO",BAD
    elif v=="REFUSED": lab,col="REFUSED",REF
    else: lab,col=v,OK
    fb=F(int(13*scale),True)
    tw=d.textlength(lab,font=fb)
    d.rounded_rectangle((x,y,x+tw+int(16*scale),y+int(24*scale)),radius=5,fill=col)
    d.text((x+int(8*scale),y+int(4*scale)),lab,font=fb,fill=(255,255,255)); y+=int(32*scale)
    def row(k,val,mono=False,color=TXT):
        nonlocal y
        d.text((x,y),k,font=f11,fill=DIM)
        ft=f11m if mono else f11
        t=val
        mx=W-2*pad-int(88*scale)
        while d.textlength(t,font=ft)>mx and len(t)>4: t=t[:-4]+"..."
        tw=d.textlength(t,font=ft)
        d.text((x0+W-pad-tw,y),t,font=ft,fill=color); y+=int(21*scale)
    row("teste",rec["teste"]); row("provedor",rec["prov"]); row("backend",rec["back"])
    row("job_id",rec["job"],True,DIM); row("shots",str(rec["shots"])); row("proveniencia",rec["proven"])
    sig={1:("assinatura ML-DSA-44 CONFIRMADA",GREEN),0:("ASSINATURA INVALIDA",(248,81,73))}.get(rec["sig"],("wasm indisponivel",DIM))
    row("assinatura",sig[0],False,sig[1])
    row("hash",rec["hash"][:24]+"...",True,DIM)
    y+=int(4*scale)
    msg="integro; assinatura presente (conferencia criptografica no nucleo)"
    ws=msg.split(); line=""
    for w in ws:
        if d.textlength(line+" "+w,font=f10m)>W-2*pad: d.text((x,y),line,font=f10m,fill=DIM); y+=int(13*scale); line=w
        else: line=(line+" "+w).strip()
    d.text((x,y),line,font=f10m,fill=DIM)
    return H

res=json.load(open("/tmp/res.json"))
R={x["back"]:x for x in res}
rs1=[x for x in res if x["back"]=="qbraid:qbraid:sim:qir-sv"][0]
rs0=[x for x in res if x["back"]=="qbraid:quobly:sim:alloy-forge"][0]
rsR=[x for x in res if x["back"]=="iqs"][0]

def cena(titulo,sub,recs,fname,lados=None):
    W,H=1280,800
    im=grad(W,H,(9,14,26),(15,48,102))
    d=ImageDraw.Draw(im)
    # grade sutil
    for gx in range(0,W,64): d.line((gx,0,gx,H),fill=(255,255,255,0),width=1)
    lg=logo(88); im.paste(lg,(70,64),lg)
    d.text((176,70),"IMUT-Q Receipt Checker",font=F(30,True),fill=(255,255,255))
    d.text((176,110),"Serena Solutions",font=F(17),fill=(147,197,253))
    # titulo esquerdo
    y=230
    for l in titulo:
        d.text((70,y),l,font=F(44,True),fill=(255,255,255)); y+=60
    y+=14
    for l in sub:
        d.text((70,y),l,font=F(21),fill=(186,214,250)); y+=32
    # chips
    y=H-120
    cx=70
    for t in ["SHA3-256","ML-DSA-44","WebAssembly","Sem servidor"]:
        f=F(16,True); w=d.textlength(t,font=f)
        d.rounded_rectangle((cx,y,cx+w+28,y+36),radius=18,outline=(147,197,253),width=2)
        d.text((cx+14,y+8),t,font=f,fill=(219,234,254)); cx+=w+28+12
    # popup(s) a direita
    px=760
    sc=1.28
    if len(recs)==1:
        popup(im,px,70,recs[0],scale=sc,mostrar_entrada=True)
    else:
        popup(im,700,60,recs[0],scale=1.0,mostrar_entrada=False)
        popup(im,700+360,60,recs[1],scale=1.0,mostrar_entrada=False) if False else None
    im.convert("RGB").save(fname)

# 1) verificado
cena(["Confira se um recibo","foi alterado."],["Cole o recibo e veja o veredito,","o job e a assinatura em segundos."],[rs1],"captura-1-verificado-1280x800.png")
# 2) veredito 0
cena(["Veredito 0 também","fica assinado."],["Um resultado desfavorável não é","escondido: tem hash e assinatura."],[rs0],"captura-2-veredito-0-1280x800.png")
# 3) refused
cena(["REFUSED é uma","resposta honesta."],["Quando o protocolo não cobre o caso,","a extensão mostra REFUSED, sem forçar 1 ou 0."],[rsR],"captura-3-refused-1280x800.png")

# 4) como funciona
W,H=1280,800
im=grad(W,H,(9,14,26),(15,48,102)); d=ImageDraw.Draw(im)
lg=logo(88); im.paste(lg,(70,64),lg)
d.text((176,70),"IMUT-Q Receipt Checker",font=F(30,True),fill=(255,255,255))
d.text((176,110),"Serena Solutions",font=F(17),fill=(147,197,253))
d.text((70,210),"Tudo acontece no seu navegador.",font=F(46,True),fill=(255,255,255))
passos=[("1","Recalcula o hash","SHA3-256 do conteúdo canônico do recibo, na sua máquina."),
        ("2","Confere a assinatura","ML-DSA-44 pós-quântica, verificada em WebAssembly."),
        ("3","Mostra o veredito","1, 0 ou REFUSED, com provedor, backend, job e proveniência.")]
y=330
for n,t,s in passos:
    d.rounded_rectangle((70,y,1210,y+112),radius=16,fill=(10,22,44),outline=(48,84,140),width=2)
    d.ellipse((96,y+26,156,y+86),fill=BLUE)
    d.text((115,y+36),n,font=F(32,True),fill=(255,255,255))
    d.text((184,y+20),t,font=F(28,True),fill=(255,255,255))
    d.text((184,y+62),s,font=F(19),fill=(186,214,250)); y+=134
d.text((70,H-62),"Sem conta  ·  Sem servidor  ·  Sem rastreamento  ·  Sem anúncios",font=F(20,True),fill=(147,197,253))
im.convert("RGB").save("captura-4-como-funciona-1280x800.png")

# ---------------- tiles promocionais ----------------
def tile(W,H,fname,big):
    im=grad(W,H,(9,14,26),(18,70,140)); d=ImageDraw.Draw(im)
    s=int(H*(0.5 if big else 0.42)); lg=logo(s)
    im.paste(lg,(int(W*.06),(H-s)//2),lg)
    x=int(W*.06)+s+int(W*.04)
    f1=F(int(H*(0.115 if big else 0.105)),True); f2=F(int(H*(0.056 if big else 0.058)))
    d.text((x,int(H*.30)),"IMUT-Q",font=F(int(H*(0.17 if big else 0.16)),True),fill=(255,255,255))
    d.text((x,int(H*.52)),"Receipt Checker",font=f1,fill=(186,214,250))
    d.text((x,int(H*.74)),"SHA3-256 + ML-DSA-44, no navegador",font=f2,fill=(147,197,253))
    im.convert("RGB").save(fname)
tile(440,280,"tile-pequeno-440x280.png",False)
tile(1400,560,"tile-grande-1400x560.png",True)
print("ok")
