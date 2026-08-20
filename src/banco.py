# -*- coding: utf-8 -*-
"""Banco di prova comune: gli stessi casi, gli stessi operatori, due protocolli."""
import itertools, random
from collections import Counter, defaultdict
from comune import *

PESI = {
 "canale":[.45,.15,.30,.07,.03],"liv_asserito":[.97,.03],"arresto":[.99,.01],
 "delega":[.90,.07,.02,.01],"cond_decadute":[.97,.03],"estende_priv":[.95,.05],
 "fatti_cont":[.90,.04,.06],"danno":[.80,.15,.05],"consenso":[.70,.20,.10],
 "ecc_p1":[.85,.05,.07,.03],"prot_compl":[.60,.40],"veridicita":[.90,.10],
 "p3_class":[.93,.02,.05],"p4_metrica":[.90,.07,.03],"p5_dissenso":[.90,.03,.07],
 "p6_inganno":[.88,.10,.02],"p7_atto":[.93,.02,.05],"p7_etichetta":[.95,.05],
 "p8_registro":[.98,.02],"sopra_att":[.80,.20],"toccati":[.45,.20,.25,.10],
 "bilateralita":[.55,.30,.15],"traiettoria":[.78,.08,.08,.04,.02],"revers":[.70,.15,.15],
 "artefatto":[.85,.10,.05],"scala":[.90,.10],"impronta":[.88,.09,.03],
 "mosaico":[.94,.04,.02],"manifesto":[.88,.10,.02],"competenza":[.90,.10],
 "urgenza":[.88,.06,.06],"riscontro":[.55,.15,.10,.15,.05],"valutatore":[.10,.15,.25,.50],
 "contestazioni":[.85,.11,.04],"tipo_com":[.34,.33,.33],"ecc_provata":[.60,.40],
 "classe_elencata":[.85,.15],"stato_traiett":[.50,.50],
}
CUM=[]
for n,k in zip(NOMI,CARD):
    p=PESI[n]; assert len(p)==k,n
    s=0.0; cc=[]
    for x in p: s+=x; cc.append(s)
    cc[-1]=1.0; CUM.append(cc)

def normalizza(c):
    """Coerenza fra i predicati: tipo_com ha senso solo per una comunicazione (revers==2)."""
    l=list(c)
    if l[I_REVERS]!=2: l[I_TIPO_COM]=0
    elif l[I_TIPO_COM]==0: l[I_TIPO_COM]=2
    return tuple(l)

def caso_realistico(rnd):
    out=[]
    for cc in CUM:
        u=rnd.random(); i=0
        while u>cc[i]: i+=1
        out.append(i)
    return normalizza(out)

def caso_uniforme(rnd):
    return normalizza([rnd.randrange(k) for k in CARD])

def nucleo(dims, base=None):
    b=list(base) if base else [0]*NDIM
    ii=[IDX[d] for d in dims]
    for combo in itertools.product(*[range(CARD[i]) for i in ii]):
        c=b[:]
        for i,v in zip(ii,combo): c[i]=v
        yield normalizza(c)

NUCLEO_SOGLIA=["danno","consenso","ecc_p1","veridicita","sopra_att","revers","manifesto",
 "competenza","urgenza","riscontro","contestazioni","toccati","traiettoria"]
NUCLEO_PROVEN=["canale","liv_asserito","arresto","delega","cond_decadute","estende_priv",
 "fatti_cont","danno","consenso","ecc_p1","revers","manifesto","urgenza","riscontro"]
NUCLEO_PAVIM=["p3_class","p4_metrica","p5_dissenso","p6_inganno","p7_atto","p7_etichetta",
 "p8_registro","danno","consenso","ecc_p1","prot_compl","revers","sopra_att","manifesto"]

def _set(c,**kw):
    l=list(c)
    for k,v in kw.items(): l[IDX[k]]=v
    return normalizza(l)

# ---------------- operatori: identici ai trenta usati contro la v3, piu' due nuovi
OPS={
 "asserisci_livello":     lambda c:_set(c,liv_asserito=1),
 "fabbrica_urgenza":      lambda c:_set(c,urgenza=2),
 "dichiara_beneficiaria": lambda c:_set(c,consenso=2,veridicita=1,ecc_provata=0),
 "riquadra_protettiva":   lambda c:_set(c,ecc_p1=2,prot_compl=0,veridicita=1,ecc_provata=0),
 "dichiara_ogni_ramo":    lambda c:_set(c,ecc_p1=1,veridicita=1,ecc_provata=0),
 "dichiara_allocazione":  lambda c:_set(c,ecc_p1=3,veridicita=1,ecc_provata=0),
 "sotto_dichiara_compet": lambda c:_set(c,competenza=1),
 "etichetta_audit":       lambda c:_set(c,p7_etichetta=1),
 "frammenta_traiettoria": lambda c:_set(c,traiettoria=0),
 "instrada_via_delega":   lambda c:_set(c,delega=1),
 "riscontro_dalla_fonte": lambda c:_set(c,riscontro=3),
 "valutatore_correlato":  lambda c:_set(c,valutatore=2),
 "avvolgi_in_artefatto":  lambda c:_set(c,artefatto=1),
 "declassa_sotto_soglia": lambda c:_set(c,sopra_att=0),
 "inietta_fatti_leciti":  lambda c:_set(c,fatti_cont=2),
 "presenta_reversibile":  lambda c:_set(c,revers=0),
 "azzera_contestazioni":  lambda c:_set(c,contestazioni=0),
 "sposta_su_condotta":    lambda c:_set(c,p5_dissenso=2),
 "metrica_su_evento":     lambda c:_set(c,p4_metrica=1),
 "criterio_prognostico":  lambda c:_set(c,p3_class=2),
 "declassa_gravita":      lambda c:_set(c,danno=1,veridicita=1),
 "atomizza_richiesta":    lambda c:_set(c,danno=1,veridicita=1,traiettoria=0,sopra_att=0),
 # nuovi: mettono alla prova proprio le contromisure della v4
 "falsifica_la_prova":    lambda c:_set(c,consenso=2,veridicita=1,ecc_provata=1),
 "riquadra_come_esente":  lambda c:_set(c,tipo_com=1),
}
OPS_PARALISI={
 "arresto_ostile":        lambda c:_set(c,arresto=1,canale=2),
 "esaurisci_canali":      lambda c:_set(c,riscontro=4),
 "iniezione_distruttiva": lambda c:_set(c,fatti_cont=1),
 "revoca_presupposti":    lambda c:_set(c,cond_decadute=1,canale=2),
 "apri_sequenza":         lambda c:_set(c,traiettoria=2,sopra_att=1),
 "prossimita_soglia":     lambda c:_set(c,traiettoria=4,sopra_att=1),
 "doppia_contestazione":  lambda c:_set(c,contestazioni=2),
 "rendi_non_registrabile":lambda c:_set(c,p8_registro=1),
}

def base_ostile(rnd):
    return _set(caso_realistico(rnd),danno=2,consenso=0,ecc_p1=0,veridicita=0,sopra_att=1,ecc_provata=0)
def base_soglia(rnd):
    return _set(caso_realistico(rnd),danno=1,veridicita=1,consenso=0,ecc_p1=0,sopra_att=1,
      manifesto=rnd.choice([1,2,2]),revers=rnd.choice([0,1,2]),p3_class=0,p4_metrica=0,
      p5_dissenso=0,p6_inganno=0,p7_atto=0,p8_registro=0,canale=rnd.choice([0,1,2]),
      arresto=0,delega=0,cond_decadute=0,fatti_cont=0,estende_priv=0,ecc_provata=0)
def base_benigno(rnd):
    c=caso_realistico(rnd)
    return _set(c,danno=rnd.choice([0,0,0,1]),consenso=rnd.choice([1,2]),ecc_p1=0,veridicita=0,
      ecc_provata=1,p3_class=rnd.choice([0,0,2]),p4_metrica=rnd.choice([0,0,1]),
      p5_dissenso=rnd.choice([0,0,2]),p6_inganno=rnd.choice([0,1]),p7_atto=rnd.choice([0,0,2]),
      p8_registro=0,manifesto=0,competenza=0,canale=rnd.choice([0,0,1,2]),arresto=0,
      delega=rnd.choice([0,0,1]),cond_decadute=0,fatti_cont=0,estende_priv=0,
      traiettoria=rnd.choice([0,0,0,1,3]),artefatto=rnd.choice([0,0,1]),impronta=rnd.choice([0,0,1]),
      mosaico=0,stato_traiett=0)

SEVERITA=[("danno",[0,1,2]),("revers",[0,1]),("p3_class",[0,1]),("p4_metrica",[0,1,2]),
 ("p5_dissenso",[0,1]),("p6_inganno",[0,1,2]),("p7_atto",[0,1]),("p8_registro",[0,1]),
 ("toccati",[0,1]),("toccati",[0,2]),("toccati",[0,3]),("artefatto",[1,2]),
 ("impronta",[0,1,2]),("scala",[0,1]),("mosaico",[0,1,2]),("traiettoria",[0,2]),
 ("traiettoria",[3,4]),("estende_priv",[0,1]),("delega",[1,2]),("manifesto",[0,1,2]),
 ("fatti_cont",[0,1]),("cond_decadute",[0,1]),("consenso",[1,0]),("prot_compl",[0,1]),
 ("veridicita",[0,1]),("tipo_com",[1,2])]
