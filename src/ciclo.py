# -*- coding: utf-8 -*-
"""Il ciclo di revisione come sistema dinamico.
Metodo: entrambe le politiche di ciclo sono CALIBRATE per essere ferme all'ottimo
in assenza di attacco. Cosi' la differenza misurata non e' la taratura, ma la
manovrabilita': quanto un avversario riesce a spostarle. E la seconda prova misura
la coda opposta: quanto restano sorde a un cambiamento vero del mondo."""
import numpy as np, json

FRAZ_DAN, MU_LEG, SIGMA = 0.06, 0.35, 0.18
C_DANNO, C_FA = 8.0, 1.0
P_RICH, P_TOCC = 0.70, 0.05
Q_VERO, Q_FALSO = 0.80, 0.10
N_CASO, FIN = 2000, 40

def genera(n, rng, mu=0.72):
    dan = rng.random(n) < FRAZ_DAN
    return dan, np.clip(np.where(dan, rng.normal(mu,SIGMA,n), rng.normal(MU_LEG,SIGMA,n)),0,1)

def errore(th, dan, s):
    return C_DANNO*np.sum(dan & (s<=th)) + C_FA*np.sum((~dan) & (s>th))

def ottimo(mu, seed=3, n=300000):
    dan,s = genera(n, np.random.default_rng(seed), mu)
    gr = np.linspace(0.05,0.95,181)
    return float(gr[int(np.argmin([errore(t,dan,s) for t in gr]))])

def segnali(th, mu, attacco, rng):
    dan, s = genera(N_CASO, rng, mu)
    if attacco:
        dan = np.concatenate([dan, np.zeros(attacco,bool)])
        s   = np.concatenate([s, np.clip(rng.normal(th+0.05,0.03,attacco),0,1)])
    bloc = s>th
    P = int(np.sum((~dan)&bloc&(rng.random(len(s))<P_RICH)))       # proteste (legittime e ostili insieme)
    Po= int(np.sum(dan&bloc&(rng.random(len(s))<P_RICH)))
    H = int(np.sum(dan&~bloc&(rng.random(len(s))<P_TOCC)))         # voce del toccato
    return P, Po, H, dan, s

def calibra(th, mu, pol, seed=1, rounds=300):
    """Trova il fattore che rende la politica ferma all'ottimo senza attacco."""
    rng=np.random.default_rng(seed); a=b=0.0
    for _ in range(rounds):
        P,Po,H,_,_ = segnali(th, mu, 0, rng)
        if pol=="B": a += P+Po; b += H
        else:
            amm = np.sum(rng.random(P+Po)<Q_VERO*0+1)*0  # placeholder
            a += (P+Po); b += H
    return a/max(b,1e-9)

def stratifica(dan,s,rng,n=40000):
    """10.5 — la batteria si compone secondo le classi dichiarate, non le frequenze osservate."""
    id_,il = np.flatnonzero(dan), np.flatnonzero(~dan)
    if len(id_)==0 or len(il)==0: return dan,s
    kd=int(n*FRAZ_DAN); i=np.concatenate([rng.choice(id_,kd,True), rng.choice(il,n-kd,True)])
    return dan[i], s[i]

def simula(pol, rounds, attacco, th0, seed, lam, mu0=0.72, cambio=None, eta=0.006, W=10):
    rng=np.random.default_rng(seed); th=th0; mu=mu0
    batt = genera(40000, rng, mu); buf_d=[]; buf_s=[]; fin=[]
    st=[th]
    for r in range(rounds):
        if cambio and r==cambio[0]: mu=cambio[1]
        P,Po,H,dan,s = segnali(th, mu, attacco, rng)
        buf_d.append(dan); buf_s.append(s)
        if pol=="A": st.append(th); continue
        if pol=="B":
            fin.append((P+Po) - lam*H)
            if len(fin)>=W:
                th=float(np.clip(th - eta*np.sign(np.mean(fin[-W:])), 0.05, 0.95))
            st.append(th); continue
        # ---- Parte 10 ----
        amm = int(np.sum(rng.random(P)<Q_VERO) + np.sum(rng.random(Po)<Q_FALSO))  # 10.6 valutatore
        fin.append(amm/P_RICH*C_FA - lam*H/P_TOCC*C_DANNO)                        # 10.4 riponderazione
        if pol in ("C2","C3") and r%25==24:
            td=np.concatenate(buf_d[-25:]); ts=np.concatenate(buf_s[-25:])
            batt = (td,ts) if pol=="C2" else stratifica(td,ts,rng)
            buf_d=[]; buf_s=[]
        if len(fin)>=W:
            m=np.mean(fin[-W:])                                                   # 10.7 il volume non scala il passo
            cand=float(np.clip(th - eta*np.sign(m), 0.05, 0.95))
            if errore(cand,*batt) <= errore(th,*batt): th=cand                    # 10.6 test bilaterale
        st.append(th)
    return np.array(st)

def taratura(pol, th, mu, seed=2, rounds=400):
    """lambda che annulla il segnale netto medio all'ottimo, senza attacco."""
    rng=np.random.default_rng(seed); num=den=0.0
    for _ in range(rounds):
        P,Po,H,_,_ = segnali(th, mu, 0, rng)
        if pol=="B": num+=P+Po; den+=H
        else:
            amm=int(np.sum(rng.random(P)<Q_VERO)+np.sum(rng.random(Po)<Q_FALSO))
            num+=amm/P_RICH*C_FA; den+=H/P_TOCC*C_DANNO
    return num/max(den,1e-9)

if __name__=="__main__":
    TH=ottimo(0.72); val=genera(300000,np.random.default_rng(21),0.72); base=errore(TH,*val)
    lamB=taratura("B",TH,0.72); lamC=taratura("C",TH,0.72)
    print("theta ottimo %.3f | taratura B %.2f  C %.2f  (entrambe ferme all'ottimo senza attacco)"%(TH,lamB,lamC))
    R={"theta_ottimo":TH,"deriva":{},"sordita":{}}
    POL=["A","B","C1","C2","C3"]
    LAM={"A":0,"B":lamB,"C1":lamC,"C2":lamC,"C3":lamC}
    SEMI=range(11)
    print("\n=== PROVA 1 — DERIVA: sovracosto rispetto all'ottimo dopo 500 round (mediana su 11 semi) ===")
    print("  %-9s %9s %9s %9s %9s %9s"%("attacco","A","B","C1","C2","C3"))
    for att in (0,25,100,400,1600):
        riga={}
        for p in POL:
            fs=[float(simula(p,500,att,TH,900+att*7+k,LAM[p])[-1]) for k in SEMI]
            cs=[100.0*(errore(f,*val)/base-1) for f in fs]
            riga[p]={"theta":float(np.median(fs)),"sovracosto_pct":float(np.median(cs))}
        print("  %-9d %8.0f%% %8.0f%% %8.0f%% %8.0f%% %8.0f%%"%(att,*[riga[p]["sovracosto_pct"] for p in POL]))
        R["deriva"][att]=riga
    print("  (theta finale mediano)")
    print("  %-9s %9s %9s %9s %9s %9s"%("attacco","A","B","C1","C2","C3"))
    for att in R["deriva"]:
        print("  %-9s %9.3f %9.3f %9.3f %9.3f %9.3f"%(att,*[R["deriva"][att][p]["theta"] for p in POL]))

    print("\n=== PROVA 2 — SORDITA': il mondo cambia al round 150, nessun attacco ===")
    for mu2 in (0.62,0.55):
        nuovo=ottimo(mu2); val2=genera(300000,np.random.default_rng(31),mu2); b2=errore(nuovo,*val2)
        print("  mondo -> mu %.2f, nuovo ottimo %.3f"%(mu2,nuovo))
        print("    %-4s %9s %10s %13s"%("pol","finale","round","sovracosto"))
        for p in POL:
            hh=[simula(p,900,0,TH,300+k,LAM[p],cambio=(150,mu2)) for k in SEMI]
            fs=[float(h[-1]) for h in hh]
            ts=[]
            for h in hh:
                d=np.flatnonzero(np.abs(h[150:]-nuovo)<=0.03)
                ts.append(int(d[0]) if len(d) else 10**6)
            t=int(np.median(ts)); sc=float(np.median([100.0*(errore(f,*val2)/b2-1) for f in fs]))
            print("    %-4s %9.3f %10s %12.0f%%"%(p,np.median(fs),t if t<10**6 else "mai",sc))
            R["sordita"].setdefault("%.2f"%mu2,{})[p]={"finale":float(np.median(fs)),
              "round":t if t<10**6 else None,"nuovo_ottimo":nuovo,"sovracosto_pct":sc}
    json.dump(R,open("ris_ciclo.json","w"),indent=1,default=float)
