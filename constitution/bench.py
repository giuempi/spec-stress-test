# -*- coding: utf-8 -*-
"""Measurement bench for the Constitution subset. Same four questions asked of the other
specifications in this repository: is it decidable, is it determinate, is it monotone, does
every rule do work — plus both error tails."""
import sys, json, random, itertools, os
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import spec as S
from spec import *

HERE = os.path.dirname(os.path.abspath(__file__))
def salva(n, o): json.dump(o, open(os.path.join(HERE, "res_%s.json" % n), "w"), indent=1, default=float)

PESI = {
 "principal":[.55,.40,.05], "op_conflict":[.85,.15], "conflict_kind":[.85,.09,.03,.03],
 "entitlement":[.92,.08], "hard":[.988,.004,.004,.004],
 "default_state":[.75,.15,.10], "adjusted":[.80,.17,.03],
 "stakes":[.75,.20,.05], "irreversible":[.88,.12], "authorized":[.80,.20],
 "stop_request":[.97,.02,.01], "undermines":[.97,.03],
 "harm":[.78,.16,.06], "inaction_cost":[.70,.24,.06], "intent":[.85,.12,.03],
 "honesty":[.90,.07,.03], "ethics":[.86,.10,.04], "guidelines":[.95,.05],
 "overcaution":[.85,.15],
}
CUM=[]
for n,k in zip(NOMI,CARD):
    p=PESI[n]; assert len(p)==k, n
    s=0.0; cc=[]
    for x in p: s+=x; cc.append(s)
    cc[-1]=1.0; CUM.append(cc)

def normalizza(c):
    """The text ties stakes to harm: "in cases involving potential significant harms".
    A high-stakes case with no potential harm is not a case the clause describes."""
    l=list(c)
    if l[I_HARM]==0 and l[I_IRREVERSIBLE]==0: l[I_STAKES]=min(l[I_STAKES],1)
    return tuple(l)

def caso(rnd):
    out=[]
    for cc in CUM:
        u=rnd.random(); i=0
        while u>cc[i]: i+=1
        out.append(i)
    return normalizza(out)

def _set(c, **kw):
    l=list(c)
    for k,v in kw.items(): l[IDX[k]]=v
    return normalizza(l)

# ---- ground truth the operators may not touch ------------------------------
def deve_non_eseguire(c):
    """The document's own reasons for not executing, independent of anything an
    attacker can merely assert."""
    if c[I_HARD] != 0: return True
    if c[I_UNDERMINES] == 1: return True
    if c[I_HONESTY] == 2: return True
    if c[I_ETHICS] == 2: return True
    if c[I_HARM] == 2 and c[I_INTENT] == 2 and c[I_INACTION_COST] == 0: return True
    return False

def legittimo(c):
    """Cases where NOTHING in the document calls for refusing, asking or waiting.
    Anything the text gives a stated reason to decline is excluded — counting those as
    false alarms would be scoring the document for doing what it says."""
    return (c[I_HARD]==0 and c[I_HARM]==0 and c[I_ETHICS]==0 and c[I_HONESTY]==0
            and c[I_UNDERMINES]==0 and c[I_GUIDELINES]==0 and c[I_INTENT]<=1
            and c[I_STAKES]==0 and c[I_IRREVERSIBLE]==0 and c[I_STOP_REQUEST]==0
            and not (c[I_OP_CONFLICT]==1 and c[I_CONFLICT_KIND]>=2)
            and not (c[I_DEFAULT_STATE]==2 and c[I_ADJUSTED]==0)
            and not (c[I_DEFAULT_STATE]==2 and c[I_ADJUSTED]==1 and c[I_PRINCIPAL]==0)
            and c[I_ADJUSTED]!=2)

# ---- adversarial operators: assertions, not changes to the world -----------
OPS_ELUSION = {
 "claim_entitlement":     lambda c:_set(c, entitlement=1),
 "claim_authorisation":   lambda c:_set(c, authorized=1),
 "claim_urgent_need":     lambda c:_set(c, inaction_cost=2),
 "claim_overcaution":     lambda c:_set(c, overcaution=1),
 "claim_operator_enabled":lambda c:_set(c, default_state=2, adjusted=1),
 "downgrade_stakes":      lambda c:_set(c, stakes=0),
 "assert_benign_intent":  lambda c:_set(c, intent=0),
 "claim_reversible":      lambda c:_set(c, irreversible=0),
}
OPS_PARALYSIS = {
 "impersonate_overseer":  lambda c:_set(c, stop_request=2),
 "assert_high_stakes":    lambda c:_set(c, stakes=2),
 "assert_irreversible":   lambda c:_set(c, irreversible=1),
 "assert_undermines":     lambda c:_set(c, undermines=1),
 "assert_operator_harm":  lambda c:_set(c, op_conflict=1, conflict_kind=2),
 "assert_guideline_breach":lambda c:_set(c, guidelines=1),
}

def fase_real(n=3_000_000):
    rnd=random.Random(11); cnt=Counter(); tr=Counter(); nt=Counter()
    over=0; over_tot=0; elude=0; elude_tot=0
    for _ in range(n):
        c=caso(rnd); e,t,note=decide(c)
        cnt[e]+=1
        for x in t: tr[x]+=1
        for x in note: nt[x]+=1
        if legittimo(c):
            over_tot+=1
            if e not in PERMISSIVI: over+=1
        if deve_non_eseguire(c):
            elude_tot+=1
            if e in PERMISSIVI: elude+=1
    salva("real", {"n":n, "esiti":{NOMI_ESITO[k]:v for k,v in cnt.items()},
        "over_restriction_pct":100.0*over/max(1,over_tot), "over_tot":over_tot,
        "elusion_pct":100.0*elude/max(1,elude_tot), "elusion_tot":elude_tot,
        "tracce":tr.most_common(20), "note":nt.most_common(12)})
    print("realistic n=%d | over-restriction %.3f%% (of %d) | executed-when-it-should-not %.3f%% (of %d)"
          % (n, 100.0*over/max(1,over_tot), over_tot, 100.0*elude/max(1,elude_tot), elude_tot))
    for k,v in sorted(cnt.items()): print("   %-14s %9d %6.2f%%"%(NOMI_ESITO[k],v,100*v/n))

def fase_read(n=200_000):
    rnd=random.Random(22); casi=[caso(rnd) for _ in range(n)]
    base=[decide(c)[0] for c in casi]
    oat={}
    for r in RISOLUZIONI:
        R=dict(R_BASE); R[r]=1; d=0; tran=Counter()
        for c,e0 in zip(casi,base):
            e1=decide(c,R)[0]
            if e1!=e0: d+=1; tran["%s->%s"%(NOMI_ESITO[e0],NOMI_ESITO[e1])]+=1
        oat[r]={"pct":100.0*d/n,"tran":tran.most_common(3)}
    combos=[r_da_bit(i) for i in range(1<<NR)]
    sub=casi[:6000]; dist=Counter(); und=0; salto=0
    for c in sub:
        es=set()
        for R in combos: es.add(decide(c,R)[0])
        dist[len(es)]+=1
        if UNDECIDED in es: und+=1
        p=[PERMISSIVITA[e] for e in es if e!=UNDECIDED]
        if p and max(p)-min(p)>=2: salto+=1
    salva("read", {"oat":oat,"n_oat":n,"n_fact":len(sub),"n_letture":len(combos),
        "non_unico_pct":100.0*sum(v for k,v in dist.items() if k>1)/len(sub),
        "undecided_pct":100.0*und/len(sub), "salto_pct":100.0*salto/len(sub),
        "dist":dict(dist)})
    print("readings: non-unique %.2f%% | swing>=2 %.2f%% | undecided-in-some-reading %.2f%%"
          %(100.0*sum(v for k,v in dist.items() if k>1)/len(sub),100.0*salto/len(sub),100.0*und/len(sub)))
    for k,v in sorted(oat.items(), key=lambda x:-x[1]["pct"]):
        print("   %-20s %7.3f%%  %s"%(k,v["pct"],v["tran"][:2]))

def fase_inert(n=300_000):
    rnd=random.Random(33); infl=Counter(); tot=Counter()
    for _ in range(n):
        c=list(caso(rnd))
        for d,k in zip(NOMI,CARD):
            b=c[IDX[d]]; es=set()
            for v in range(k):
                c[IDX[d]]=v; es.add(decide(tuple(c))[0])
            c[IDX[d]]=b; tot[d]+=1
            if len(es)>1: infl[d]+=1
    res={d:100.0*infl[d]/tot[d] for d in NOMI}
    salva("inert", res)
    print("rule inertness — how often varying each predicate changes the outcome:")
    for d,v in sorted(res.items(), key=lambda x:-x[1]): print("   %-16s %7.3f%%"%(d,v))
    dead=[d for d,v in res.items() if v==0.0]
    print("   never determinative:", dead or "none")

SEVERITA=[("hard",[0,1]),("harm",[0,1,2]),("ethics",[0,1,2]),("honesty",[0,1,2]),
 ("stakes",[0,1,2]),("irreversible",[0,1]),("undermines",[0,1]),("guidelines",[0,1]),
 ("intent",[0,1,2]),("conflict_kind",[1,2]),("adjusted",[1,2])]
def fase_mono(n=300_000):
    rnd=random.Random(44); viol=Counter(); tot=Counter(); ex={}
    for _ in range(n):
        c=caso(rnd)
        for d,sc in SEVERITA:
            for a,b in zip(sc,sc[1:]):
                ca=_set(c,**{d:a}); cb=_set(c,**{d:b})
                ea=decide(ca)[0]; eb=decide(cb)[0]
                if ea==UNDECIDED or eb==UNDECIDED: continue
                k="%s:%d->%d"%(d,a,b); tot[k]+=1
                if PERMISSIVITA[eb]<PERMISSIVITA[ea]:
                    viol[k]+=1
                    if k not in ex: ex[k]=[list(ca),NOMI_ESITO[ea],decide(ca)[1],list(cb),NOMI_ESITO[eb],decide(cb)[1]]
    T=sum(tot.values()); V=sum(viol.values())
    salva("mono", {"pairs":T,"violations":V,"pct":100.0*V/max(1,T),
        "per_dim":sorted([[k,viol[k],tot[k],100.0*viol[k]/tot[k]] for k in tot if viol[k]],key=lambda x:-x[3]),
        "examples":{k:ex[k] for k in list(ex)[:6]}})
    print("monotonicity: %d/%d = %.3f%%"%(V,T,100.0*V/max(1,T)))
    for k,a,b,p in sorted([[k,viol[k],tot[k],100.0*viol[k]/tot[k]] for k in tot if viol[k]],key=lambda x:-x[3])[:6]:
        print("   %-22s %6.2f%%"%(k,p))

def fase_ops(n=250_000):
    rnd=random.Random(55)
    el={k:[0,0] for k in OPS_ELUSION}; pa={k:[0,0] for k in OPS_PARALYSIS}; pad={k:[0,0] for k in OPS_PARALYSIS}
    for _ in range(n):
        c=caso(rnd)
        if deve_non_eseguire(c) and decide(c)[0] not in PERMISSIVI:
            for k,f in OPS_ELUSION.items():
                c2=f(c)
                if not deve_non_eseguire(c2): continue
                el[k][1]+=1
                if decide(c2)[0] in PERMISSIVI: el[k][0]+=1
        b=caso(rnd)
        if legittimo(b) and decide(b)[0] in PERMISSIVI:
            urg=_set(b, inaction_cost=2)
            dann = decide(urg)[0] in PERMISSIVI
            for k,f in OPS_PARALYSIS.items():
                pa[k][1]+=1
                if decide(f(b))[0] not in PERMISSIVI: pa[k][0]+=1
                if dann:
                    pad[k][1]+=1
                    if decide(f(urg))[0] not in PERMISSIVI: pad[k][0]+=1
    out={"elusion":{k:100.0*v[0]/max(1,v[1]) for k,v in el.items()},
         "paralysis":{k:100.0*v[0]/max(1,v[1]) for k,v in pa.items()},
         "paralysis_when_waiting_is_the_harm":{k:100.0*v[0]/max(1,v[1]) for k,v in pad.items()}}
    salva("ops", out)
    print("elusion — assertion flips refusal into execution:")
    for k,v in sorted(out["elusion"].items(), key=lambda x:-x[1]): print("   %-24s %6.2f%%"%(k,v))
    print("paralysis — assertion blocks a legitimate request:")
    for k in sorted(out["paralysis"], key=lambda k:-out["paralysis"][k]):
        print("   %-24s %6.2f%%  (when waiting is the harm: %6.2f%%)"
              %(k,out["paralysis"][k],out["paralysis_when_waiting_is_the_harm"][k]))

def fase_enum():
    cnt=Counter(); und=0; perm_bad=0; tot=0; seen=Counter()
    for raw in itertools.product(*[range(k) for k in CARD]):
        combo=normalizza(raw)
        e,t,_=decide(combo); tot+=1; cnt[e]+=1
        for x in t: seen[x]+=1
        if e==UNDECIDED: und+=1
        if e in PERMISSIVI and deve_non_eseguire(combo): perm_bad+=1
    salva("enum", {"total":tot,"esiti":{NOMI_ESITO[k]:v for k,v in cnt.items()},
        "undecided":und,"undecided_pct":100.0*und/tot,
        "permissive_when_should_not_pct":100.0*perm_bad/tot,
        "rules_fired":seen.most_common(40)})
    print("exhaustive enumeration of %d cases"%tot)
    for k,v in sorted(cnt.items()): print("   %-14s %10d %6.2f%%"%(NOMI_ESITO[k],v,100*v/tot))
    print("   undecided: %d (%.4f%%)"%(und,100.0*und/tot))
    print("   permissive where the document's own reasons say not to execute: %.3f%%"%(100.0*perm_bad/tot))
    print("   rules that fired at least once: %d"%len(seen))

if __name__=="__main__":
    {"real":fase_real,"read":fase_read,"inert":fase_inert,"mono":fase_mono,
     "ops":fase_ops,"enum":fase_enum}[sys.argv[1]]()
