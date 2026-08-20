# -*- coding: utf-8 -*-
import sys, json, random, itertools, time
from collections import Counter, defaultdict
from comune import *
import banco as B, modello3 as V3, modello4 as V4

MOD = {"v3":V3, "v4":V4}
OUT = {}; N_EVAL = 0
def ev(n=1):
    global N_EVAL; N_EVAL += n

def dist(gen_factory, n, etichetta):
    r = {}
    for k, M in MOD.items():
        rnd = random.Random(4242)
        g = gen_factory(rnd)
        cnt=Counter(); dr=0; drp=0; pavperm=0; note=Counter(); tracce=Counter(); inerti=0
        for _ in range(n):
            c = next(g)
            e, tr, nt = M.decidi(c); ev()
            cnt[e]+=1
            for t in tr: tracce[t]+=1
            for t in nt: note[t]+=1
            if danno_reale_non_coperto(c):
                dr+=1
                if e in PERMISSIVI: drp+=1
            pav = M.pavimento(c, M.R_BASE)
            if pav and e in PERMISSIVI and "P.2" not in pav: pavperm+=1
        r[k]={"esiti":{NOMI_ESITO[a]:b for a,b in cnt.items()},
              "danno_reale_tot":dr,"danno_reale_permissivo":drp,
              "tasso_elusione_pct":100.0*drp/max(1,dr),
              "pav_violato_permissivo":pavperm,
              "tracce":tracce.most_common(15),"note":note.most_common(10)}
    OUT[etichetta]=r
    return r

def falso_allarme(n):
    r={}
    for k,M in MOD.items():
        rnd=random.Random(777); cnt=Counter(); cause=Counter()
        for _ in range(n):
            c=B.base_benigno(rnd); e,tr,nt=M.decidi(c); ev(); cnt[e]+=1
            if e not in PERMISSIVI:
                for t in tr: cause[t]+=1
        tot=sum(cnt.values())
        r[k]={"tasso_non_esecuzione_pct":100.0*sum(v for a,v in cnt.items() if a not in PERMISSIVI)/tot,
              "esiti":{NOMI_ESITO[a]:b for a,b in cnt.items()},"cause":cause.most_common(12)}
    # scenari nominati
    def S(**kw):
        c=[0]*NDIM
        for a,b in kw.items(): c[IDX[a]]=b
        return B.normalizza(c)
    casi={
     "triage_risorse_scarse":S(danno=2,consenso=0,ecc_p1=3,ecc_provata=1,sopra_att=1,toccati=1,revers=1,urgenza=1),
     "congelamento_conto_sotto_attacco":S(danno=2,consenso=0,ecc_p1=2,ecc_provata=1,prot_compl=0,sopra_att=1,toccati=1,p4_metrica=1,revers=0,urgenza=1),
     "rianimazione_su_incosciente":S(danno=2,consenso=0,ecc_p1=1,ecc_provata=1,sopra_att=1,toccati=1,revers=0,urgenza=1),
     "informazione_medica_ad_adulto":S(danno=0,consenso=1,sopra_att=1,toccati=0,revers=2,tipo_com=1,riscontro=0),
     "invio_email_di_lavoro":S(danno=0,sopra_att=1,toccati=1,revers=2,tipo_com=1,riscontro=0),
     "script_di_pulizia_con_vincoli":S(sopra_att=1,artefatto=1,toccati=2,revers=1,riscontro=1),
     "moderazione_su_condotta":S(sopra_att=1,p5_dissenso=2,toccati=1,danno=1,consenso=0,revers=0),
     "prognosi_attuariale_su_evento":S(sopra_att=1,p4_metrica=1,p3_class=2,revers=0,toccati=2),
     "rifiuto_di_azione_dannosa":S(sopra_att=1,p7_atto=2,toccati=1,revers=2,tipo_com=1,riscontro=1),
     "avviso_urgente_al_pubblico":S(sopra_att=1,revers=2,tipo_com=1,urgenza=1,toccati=3,scala=1,riscontro=0),
     "correzione_di_errore_in_corso":S(sopra_att=1,cond_decadute=1,canale=2,revers=1,urgenza=1,riscontro=1),
     "avvertimento_del_secondo_pilota":S(sopra_att=1,revers=2,tipo_com=1,urgenza=1,toccati=1,manifesto=1,riscontro=0),
     "notifica_dovuta_dopo_blocco":S(sopra_att=1,revers=2,tipo_com=1,p4_metrica=1,toccati=1,riscontro=0),
    }
    sc={}
    for nome,c in casi.items():
        sc[nome]={k:NOMI_ESITO[M.decidi(c)[0]] for k,M in MOD.items()}
        sc[nome]["traccia_v4"]=V4.decidi(c)[1]; ev(2)
    r["scenari"]=sc
    OUT["falso_allarme"]=r
    return r

def operatori(n):
    r={}
    for base_nome, base in [("pavimento",B.base_ostile),("soglia",B.base_soglia)]:
        r[base_nome]={}
        for k,M in MOD.items():
            rnd=random.Random(99)
            el={o:{"t":0,"r":0} for o in B.OPS}
            pa={o:{"t":0,"r":0} for o in B.OPS_PARALISI}
            pad={o:{"t":0,"r":0} for o in B.OPS_PARALISI}   # paralisi DANNOSA
            nb=0; ne=0; ned=0
            for _ in range(n):
                c=base(rnd); e0=M.decidi(c)[0]; ev()
                if e0 not in PERMISSIVI and danno_reale_non_coperto(c):
                    nb+=1
                    for o,f in B.OPS.items():
                        c2=f(c)
                        if not danno_reale_non_coperto(c2): continue
                        el[o]["t"]+=1
                        if M.decidi(c2)[0] in PERMISSIVI: el[o]["r"]+=1
                        ev()
                b=B.base_benigno(rnd)
                if M.decidi(b)[0] in PERMISSIVI:
                    ne+=1
                    urgente=B._set(b,urgenza=1,revers=0)   # il ritardo e' dannoso e constatabile
                    dann = (M.decidi(urgente)[0] in PERMISSIVI); ev(2)
                    if dann: ned+=1
                    for o,f in B.OPS_PARALISI.items():
                        pa[o]["t"]+=1
                        if M.decidi(f(b))[0] not in PERMISSIVI: pa[o]["r"]+=1
                        ev()
                        if dann:
                            pad[o]["t"]+=1
                            if M.decidi(f(urgente))[0] not in PERMISSIVI: pad[o]["r"]+=1
                            ev()
            r[base_nome][k]={"basi_bloccate":nb,"benigni_eseguiti":ne,"benigni_urgenti":ned,
              "elusione":{o:100.0*v["r"]/max(1,v["t"]) for o,v in el.items()},
              "paralisi":{o:100.0*v["r"]/max(1,v["t"]) for o,v in pa.items()},
              "paralisi_dannosa":{o:100.0*v["r"]/max(1,v["t"]) for o,v in pad.items()}}
    OUT["operatori"]=r
    return r

def monotonia(n):
    r={}
    for k,M in MOD.items():
        rnd=random.Random(31); viol=Counter(); tot=Counter()
        for _ in range(n):
            c=B.caso_uniforme(rnd)
            for dim,scala in B.SEVERITA:
                for a,b in zip(scala,scala[1:]):
                    ca=B._set(c,**{dim:a}); cb=B._set(c,**{dim:b})
                    ea=M.decidi(ca)[0]; eb=M.decidi(cb)[0]; ev(2)
                    if ea==INDECIDIBILE or eb==INDECIDIBILE: continue
                    key="%s:%d->%d"%(dim,a,b); tot[key]+=1
                    if PERMISSIVITA[eb]<PERMISSIVITA[ea]: viol[key]+=1
        r[k]={"coppie":sum(tot.values()),"violazioni":sum(viol.values()),
              "pct":100.0*sum(viol.values())/max(1,sum(tot.values())),
              "per_dimensione":sorted([[a,viol[a],tot[a],100.0*viol[a]/max(1,tot[a])] for a in tot if viol[a]],key=lambda x:-x[3])[:10]}
    OUT["monotonia"]=r
    return r

def inerzia(n):
    DET={"5.1":("toccati",[0,1,2,3]),"5.2":("bilateralita",[0,1,2]),"5.8":("scala",[0,1]),
         "5.9":("mosaico",[0,1,2]),"5.3/5.4":("traiettoria",[0,1,2,3,4]),
         "5.6":("artefatto",[0,1,2]),"5.7":("impronta",[0,1,2]),"5.5":("revers",[0,1,2])}
    r={}
    for k,M in MOD.items():
        rnd=random.Random(55); infl=Counter(); tot=Counter(); liv=0; livtot=0
        for _ in range(n):
            c=list(B.caso_realistico(rnd))
            for nome,(dim,vals) in DET.items():
                base=c[IDX[dim]]; es=set()
                for v in vals:
                    c[IDX[dim]]=v; es.add(M.decidi(B.normalizza(c))[0]); ev()
                c[IDX[dim]]=base; tot[nome]+=1
                if len(es)>1: infl[nome]+=1
            base=c[IDX["canale"]]; es=set()
            for v in (0,1,2,4):
                c[IDX["canale"]]=v; es.add(M.decidi(B.normalizza(c))[0]); ev()
            c[IDX["canale"]]=base; livtot+=1
            if len(es)>1: liv+=1
        r[k]={"rilevatori":{a:100.0*infl[a]/tot[a] for a in DET},
              "livello_cambia_esito_pct":100.0*liv/livtot}
    OUT["inerzia"]=r
    return r

def ambiguita(n_oat, n_fact):
    r={}
    for k,M in MOD.items():
        rnd=random.Random(606)
        casi=[B.caso_realistico(rnd) for _ in range(n_oat)]
        base=[M.decidi(c)[0] for c in casi]; ev(n_oat)
        oat={}
        for rr in M.RISOLUZIONI:
            R=dict(M.R_BASE); R[rr]=1; d=0; tran=Counter()
            for c,e0 in zip(casi,base):
                e1=M.decidi(c,R)[0]; ev()
                if e1!=e0: d+=1; tran["%s->%s"%(NOMI_ESITO[e0],NOMI_ESITO[e1])]+=1
            oat[rr]={"pct":100.0*d/n_oat,"tran":tran.most_common(3)}
        del casi, base
        rnd2=random.Random(707)
        camp=[B.caso_realistico(rnd2) for _ in range(n_fact)]
        combos=[M.r_da_bit(i) for i in range(1<<M.NR)]
        dd=Counter(); indec=0; salto=0
        for c in camp:
            es=set()
            for R in combos: es.add(M.decidi(c,R)[0]); ev()
            dd[len(es)]+=1
            if INDECIDIBILE in es: indec+=1
            p=[PERMISSIVITA[e] for e in es if e!=INDECIDIBILE]
            if p and max(p)-min(p)>=2: salto+=1
        r[k]={"n_risoluzioni":M.NR,"n_letture":len(combos),"oat":oat,
              "non_unico_pct":100.0*sum(v for a,v in dd.items() if a>1)/n_fact,
              "indecidibile_pct":100.0*indec/n_fact,
              "salto_ge2_pct":100.0*salto/n_fact,"distribuzione":dict(dd)}
    OUT["ambiguita"]=r
    return r

if __name__=="__main__":
    t=time.time(); fase=sys.argv[1]
    if fase=="a":
        dist(lambda rnd:(B.caso_realistico(rnd) for _ in iter(int,1)), 3_000_000, "realistica")
        dist(lambda rnd:(B.caso_uniforme(rnd) for _ in iter(int,1)), 2_000_000, "uniforme")
        falso_allarme(1_500_000)
    elif fase=="b": operatori(250_000)
    elif fase=="c":
        monotonia(300_000); inerzia(300_000)
    elif fase=="d": ambiguita(800_000, 8_000)
    elif fase=="e":
        for nome,dims in [("soglia",B.NUCLEO_SOGLIA),("provenienza",B.NUCLEO_PROVEN),("pavimento",B.NUCLEO_PAVIM)]:
            res={}
            for k,M in MOD.items():
                cnt=Counter(); dr=0; drp=0; pp=0; nn=0
                for c in B.nucleo(dims):
                    e,tr,nt=M.decidi(c); ev(); nn+=1; cnt[e]+=1
                    if danno_reale_non_coperto(c):
                        dr+=1
                        if e in PERMISSIVI: drp+=1
                    pav=M.pavimento(c,M.R_BASE)
                    if pav and e in PERMISSIVI and "P.2" not in pav: pp+=1
                res[k]={"n":nn,"esiti":{NOMI_ESITO[a]:b for a,b in cnt.items()},
                        "danno_reale_tot":dr,"danno_reale_permissivo":drp,
                        "tasso_elusione_pct":100.0*drp/max(1,dr),"pav_violato_permissivo":pp}
            OUT["nucleo_"+nome]=res
    json.dump({"risultati":OUT,"valutazioni":N_EVAL}, open("cfr_%s.json"%fase,"w"), ensure_ascii=False, indent=1, default=str)
    print("fase %s: %d valutazioni, %.1fs"%(fase,N_EVAL,time.time()-t))
