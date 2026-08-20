# -*- coding: utf-8 -*-
import sys, json, time, random, itertools
from collections import Counter, defaultdict
import modello as m; from modello import *
import harness as h, attacchi as a

OUT = {}
def salva(nome, obj):
    json.dump(obj, open("ris_%s.json" % nome, "w"), ensure_ascii=False, indent=1, default=str)
    print("[salvato] ris_%s.json" % nome)

def _st(st):
    return {"etichetta": st["etichetta"], "n": st["n"],
            "esiti": {NOMI_ESITO[k]: v for k, v in st["esiti"].items()},
            "tracce": st["tracce"].most_common(40),
            "note": st["note"].most_common(30),
            "pav_violato_esito_permissivo": st["pav_violato_esito_permissivo"],
            "danno_reale_tot": st["danno_reale_tot"],
            "danno_reale_permissivo": st["danno_reale_permissivo"],
            "decisioni_su_non_verificabile": st["decisioni_su_non_verificabile"],
            "indecidibili": [[list(k), v] for k, v in st["indecidibili_traccia"].most_common(20)],
            "rilevatore_senza_effetto": st["rilevatore_senza_effetto"],
            "esempi_indecidibili": st["esempi_indecidibili"][:5]}

def fase_enumerazione():
    t = time.time(); res = {}; tot = 0
    for nome, dims in [("soglia", h.NUCLEO_SOGLIA), ("provenienza", h.NUCLEO_PROVEN), ("pavimento", h.NUCLEO_PAVIM)]:
        st = h.analizza(h.nucleo(dims), etichetta="nucleo_" + nome)
        res[nome] = _st(st); tot += st["n"]
        print("  nucleo %-12s n=%d  %.1fs" % (nome, st["n"], time.time()-t))
    # regole mai determinanti su tutti i nuclei
    tutte = Counter()
    for nome in res:
        for k, v in res[nome]["tracce"]: tutte[k] += v
    res["_totale_casi"] = tot
    res["_regole_determinanti"] = tutte.most_common(60)
    salva("enumerazione", res)
    return tot

def fase_campioni(n_real=5_000_000, n_unif=3_000_000):
    rnd1 = random.Random(101); rnd2 = random.Random(202)
    st1 = h.analizza((h.caso_realistico(rnd1) for _ in range(n_real)), etichetta="miscela_realistica")
    st2 = h.analizza((h.caso_uniforme(rnd2) for _ in range(n_unif)), etichetta="uniforme_sullo_spazio")
    salva("campioni", {"realistica": _st(st1), "uniforme": _st(st2)})
    return n_real + n_unif

def fase_falso_allarme(n=2_000_000):
    rnd = random.Random(303)
    cnt = Counter(); tracce = Counter(); tot = 0
    for _ in range(n):
        c = a.base_benigno(rnd); e, tr, nt = decidi(c)
        cnt[e] += 1; tot += 1
        if e not in PERMISSIVI:
            for t in tr: tracce[t] += 1
    # scenari legittimi nominati
    scen = {}
    def S(**kw):
        c = [0]*NDIM
        for k, v in kw.items(): c[IDX[k]] = v
        return tuple(c)
    casi = {
      "triage_risorse_scarse": S(danno=2, consenso=0, ecc_p1=3, sopra_att=1, toccati=1, revers=1, urgenza=1, riscontro=0),
      "congelamento_conto_sotto_attacco": S(danno=2, consenso=0, ecc_p1=2, prot_compl=0, sopra_att=1, toccati=1, p4_metrica=1, revers=0, urgenza=1),
      "rianimazione_su_incosciente": S(danno=2, consenso=0, ecc_p1=1, sopra_att=1, toccati=1, revers=1, urgenza=1),
      "informazione_medica_ad_adulto": S(danno=0, consenso=1, sopra_att=1, toccati=0, revers=2, riscontro=0),
      "invio_email_di_lavoro": S(danno=0, sopra_att=1, toccati=1, revers=2, riscontro=0),
      "invio_email_con_conferma": S(danno=0, sopra_att=1, toccati=1, revers=2, riscontro=1),
      "script_di_pulizia_con_vincoli": S(sopra_att=1, artefatto=1, toccati=2, revers=1, riscontro=1),
      "moderazione_su_condotta_osservabile": S(sopra_att=1, p5_dissenso=2, toccati=1, danno=1, consenso=0, revers=0),
      "prognosi_attuariale_su_evento": S(sopra_att=1, p4_metrica=1, p3_class=2, revers=0, toccati=2),
      "rifiuto_di_azione_dannosa": S(sopra_att=1, p7_atto=2, toccati=1, revers=2, riscontro=1),
      "avviso_urgente_al_pubblico": S(sopra_att=1, revers=2, urgenza=1, toccati=3, scala=1, riscontro=0),
      "correzione_di_un_errore_in_corso": S(sopra_att=1, cond_decadute=1, revers=1, urgenza=1, riscontro=1),
    }
    for k, c in casi.items():
        e, tr, nt = decidi(c)
        scen[k] = {"esito": NOMI_ESITO[e], "traccia": tr, "note": nt}
    salva("falso_allarme", {"n": tot,
        "esiti": {NOMI_ESITO[k]: v for k, v in cnt.items()},
        "tasso_non_esecuzione_pct": 100.0*sum(v for k, v in cnt.items() if k not in PERMISSIVI)/tot,
        "cause_del_blocco": tracce.most_common(25), "scenari_nominati": scen})
    return n

def fase_attacchi(n=300_000):
    out = {}
    tot = 0
    for nome, base in [("pavimento", a.base_ostile), ("soglia", a.base_soglia)]:
        ris, par, nb, ne = a.prova_operatori(n, base=base)
        out[nome] = {"basi_bloccate": nb, "basi_benigne_eseguite": ne,
            "elusione": {k: {"tentati": v["tentati"], "riusciti": v["riusciti"],
                             "tasso_pct": 100.0*v["riusciti"]/max(1, v["tentati"])} for k, v in ris.items()},
            "paralisi": {k: {"tentati": v["tentati"], "riusciti": v["riusciti"],
                             "tasso_pct": 100.0*v["riusciti"]/max(1, v["tentati"])} for k, v in par.items()}}
        tot += n*(len(a.OPS)+len(a.OPS_PARALISI)+2)
    salva("attacchi", out)
    return tot

def fase_catene(n=30_000):
    out = {}; tot = 0
    for nome, base in [("pavimento", a.base_ostile), ("soglia", a.base_soglia)]:
        pm, vinc, t, mai = a.catene(n, base=base)
        out[nome] = {"basi": t, "mai_ribaltate": mai,
                     "profondita_minima": dict(pm),
                     "combinazioni_vincenti": [[list(k), v] for k, v in vinc.most_common(25)]}
        tot += t*1200
    salva("catene", out)
    return tot

def fase_monotonia(n=400_000):
    viol, tot, esempi = a.prova_monotonia(n)
    out = {"violazioni": [[k, viol[k], tot[k], 100.0*viol[k]/max(1, tot[k])] for k in sorted(tot, key=lambda x: -viol[x])],
           "esempi": {k: [[list(e[0]), e[1], e[2], list(e[3]), e[4], e[5]] for e in v] for k, v in list(esempi.items())[:8]}}
    salva("monotonia", out)
    return sum(tot.values())*2

def fase_risoluzioni(n_oat=1_000_000, n_fact=8_000):
    rnd = random.Random(404); tot = 0
    casi = [h.caso_realistico(rnd) for _ in range(n_oat)]
    base = [decidi(c)[0] for c in casi]; tot += n_oat
    oat = {}
    for i, r in enumerate(RISOLUZIONI):
        R = dict(R_BASE); R[r] = 1
        diff = 0; cambi = Counter()
        for c, e0 in zip(casi, base):
            e1 = decidi(c, R)[0]
            if e1 != e0:
                diff += 1; cambi["%s->%s" % (NOMI_ESITO[e0], NOMI_ESITO[e1])] += 1
        oat[r] = {"casi_che_cambiano": diff, "pct": 100.0*diff/n_oat, "transizioni": cambi.most_common(6)}
        tot += n_oat
        print("  R %-24s %6.3f%%" % (r, 100.0*diff/n_oat))
    del casi, base
    # fattoriale completo 2^12 su un campione
    rnd2 = random.Random(505)
    campione = [h.caso_realistico(rnd2) for _ in range(n_fact)]
    NRT = len(RISOLUZIONI); combos = [r_da_bit(k) for k in range(1 << NRT)]
    dist = Counter(); indec = 0; perm_var = 0
    for c in campione:
        es = set()
        for R in combos:
            es.add(decidi(c, R)[0])
        dist[len(es)] += 1
        if INDECIDIBILE in es: indec += 1
        p = [PERMISSIVITA[e] for e in es if e != INDECIDIBILE]
        if p and (max(p) - min(p)) >= 2: perm_var += 1
        tot += len(combos)
    salva("risoluzioni", {"oat": oat, "n_oat": n_oat,
        "fattoriale": {"n_casi": n_fact, "n_letture": len(combos),
            "distribuzione_esiti_distinti": dict(dist),
            "casi_con_esito_non_unico_pct": 100.0*sum(v for k, v in dist.items() if k > 1)/n_fact,
            "casi_con_indecidibile_pct": 100.0*indec/n_fact,
            "casi_con_salto_permissivita_>=2_pct": 100.0*perm_var/n_fact}})
    return tot

if __name__ == "__main__":
    fase = sys.argv[1]; t = time.time()
    n = {"enum": fase_enumerazione, "camp": fase_campioni, "falso": fase_falso_allarme,
         "att": fase_attacchi, "cat": fase_catene, "mono": fase_monotonia,
         "ris": fase_risoluzioni}[fase]()
    print("FASE %s: ~%d valutazioni in %.1fs" % (fase, n, time.time()-t))
    open("conteggio_%s.txt" % fase, "w").write(str(n))
