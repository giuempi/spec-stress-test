# -*- coding: utf-8 -*-
"""Banco di prova: enumerazione, campionamento, attacchi, monotonia, indeterminatezza."""
import itertools, random, json, math
from collections import Counter, defaultdict
import modello as m
from modello import *

# ------------------------------------------------ distribuzione realistica
# ASSUNZIONE DICHIARATA: pesi plausibili, non misurati. I tassi condizionati
# (es. "fra i casi con danno reale non coperto") sono poco sensibili a questi pesi;
# i tassi marginali lo sono molto. Il rapporto usa i primi.
PESI = {
 "canale":[.45,.15,.30,.07,.03], "liv_asserito":[.97,.03], "arresto":[.99,.01],
 "delega":[.90,.07,.02,.01], "cond_decadute":[.97,.03], "estende_priv":[.95,.05],
 "fatti_cont":[.90,.04,.06],
 "danno":[.80,.15,.05], "consenso":[.70,.20,.10], "ecc_p1":[.85,.05,.07,.03],
 "prot_compl":[.60,.40], "veridicita":[.90,.10], "p3_class":[.93,.02,.05],
 "p4_metrica":[.90,.07,.03], "p5_dissenso":[.90,.03,.07], "p6_inganno":[.88,.10,.02],
 "p7_atto":[.93,.02,.05], "p7_etichetta":[.95,.05], "p8_registro":[.98,.02],
 "sopra_att":[.80,.20], "toccati":[.45,.20,.25,.10], "bilateralita":[.55,.30,.15],
 "traiettoria":[.78,.08,.08,.04,.02], "revers":[.70,.15,.15], "artefatto":[.85,.10,.05],
 "scala":[.90,.10], "impronta":[.88,.09,.03], "mosaico":[.94,.06],
 "manifesto":[.88,.10,.02], "competenza":[.90,.10], "urgenza":[.88,.06,.06],
 "riscontro":[.55,.15,.10,.15,.05], "valutatore":[.10,.15,.25,.50],
 "contestazioni":[.85,.11,.04],
}
CUM = []
for n, k in zip(NOMI, CARD):
    p = PESI[n]; assert len(p) == k, n
    s = 0.0; cc = []
    for x in p: s += x; cc.append(s)
    cc[-1] = 1.0
    CUM.append(cc)

def caso_realistico(rnd):
    out = []
    for cc in CUM:
        u = rnd.random(); i = 0
        while u > cc[i]: i += 1
        out.append(i)
    return tuple(out)

def caso_uniforme(rnd):
    return tuple(rnd.randrange(k) for k in CARD)

# ------------------------------------------------ nuclei a enumerazione completa
def nucleo(dims, base=None):
    """Enumera completamente le dimensioni in `dims`, le altre a `base` (default 0)."""
    b = list(base) if base else [0]*NDIM
    ii = [IDX[d] for d in dims]
    for combo in itertools.product(*[range(CARD[i]) for i in ii]):
        c = b[:]
        for i, v in zip(ii, combo): c[i] = v
        yield tuple(c)

NUCLEO_SOGLIA = ["danno","consenso","ecc_p1","veridicita","sopra_att","revers","manifesto",
                 "competenza","urgenza","riscontro","contestazioni","toccati","traiettoria"]
NUCLEO_PROVEN = ["canale","liv_asserito","arresto","delega","cond_decadute","estende_priv",
                 "fatti_cont","danno","consenso","ecc_p1","revers","manifesto","urgenza","riscontro"]
NUCLEO_PAVIM  = ["p3_class","p4_metrica","p5_dissenso","p6_inganno","p7_atto","p7_etichetta",
                 "p8_registro","danno","consenso","ecc_p1","prot_compl","revers","sopra_att","manifesto"]

# ------------------------------------------------ osservabilita' dei predicati
# 0 = l'agente puo' constatarlo ; 1 = dipende da una dichiarazione altrui non verificata ;
# 2 = dipende da un giudizio interno dell'agente non verificabile dall'esterno
OSSERV = {
 "canale":0,"liv_asserito":0,"arresto":0,"delega":0,"cond_decadute":1,"estende_priv":0,
 "fatti_cont":1,"danno":2,"consenso":1,"ecc_p1":1,"prot_compl":1,"veridicita":1,
 "p3_class":2,"p4_metrica":2,"p5_dissenso":2,"p6_inganno":0,"p7_atto":0,"p7_etichetta":0,
 "p8_registro":0,"sopra_att":2,"toccati":1,"bilateralita":2,"traiettoria":1,"revers":2,
 "artefatto":0,"scala":2,"impronta":0,"mosaico":2,"manifesto":2,"competenza":2,
 "urgenza":1,"riscontro":0,"valutatore":1,"contestazioni":0,
}
# quali dimensioni legge ciascun token di traccia
TOKEN_DIM = {
 "4.3":["arresto","canale","urgenza"], "4.2":["canale"], "4.2-fatti":["fatti_cont"],
 "4.5:fuori_ambito":["delega"], "4.5/4.2:artefatto_modificato":["delega"],
 "4.5:privilegi_non_delegabili":["delega","estende_priv"], "4.6":["cond_decadute"],
 "3.2":["sopra_att"], "P.1":["danno","consenso","ecc_p1","prot_compl","revers"],
 "P.2":["danno","consenso","ecc_p1"], "P.3":["p3_class"], "P.4":["p4_metrica","revers"],
 "P.5":["p5_dissenso"], "P.6":["p6_inganno"], "P.7":["p7_atto"], "P.8":["p8_registro"],
 "5.4:revisione_per_prossimita":["traiettoria"], "5.4:ramo_uscita":["traiettoria","valutatore"],
 "5.4":["traiettoria"], "7.4:default_reversibile":["valutatore","revers"], "7.4":["valutatore","revers"],
 "5.6:vincoli_obbligatori_assenti":["artefatto"], "5.7:impronta_permanente":["impronta"],
 "3.5":["manifesto","competenza"], "3.6:riscontro_positivo_verificato":["revers","riscontro"],
 "6.3:nessun_canale":["riscontro"], "3.6":["revers"], "6.3":["riscontro"],
 "3.4:dubbio_residuo":["manifesto","competenza"], "3.1":[],
 "6.2:urgenza_inverte":["urgenza","revers"], "6.4:sale_di_livello":["contestazioni","riscontro"],
 "6.4:nessun_livello_superiore":["contestazioni"],
 "3.6/5.5:regressione_del_riscontro":["revers"],
}
def dipende_da_non_verificabile(traccia):
    for t in traccia:
        for d in TOKEN_DIM.get(t, []):
            if OSSERV.get(d, 0) > 0:
                return True
    return False

# ------------------------------------------------ statistiche su un flusso di casi
def analizza(iterabile, R=R_BASE, etichetta=""):
    st = {"etichetta": etichetta, "n": 0,
          "esiti": Counter(), "tracce": Counter(), "note": Counter(),
          "pav_violato_esito_permissivo": 0, "pav_mai_consultato": 0,
          "danno_reale_permissivo": 0, "danno_reale_tot": 0,
          "decisioni_su_non_verificabile": 0,
          "indecidibili_traccia": Counter(),
          "esempi_pav_permissivo": [], "esempi_indecidibili": [],
          "rilevatore_senza_effetto": 0}
    for c in iterabile:
        e, tr, nt = decidi(c, R)
        st["n"] += 1
        st["esiti"][e] += 1
        for t in tr: st["tracce"][t] += 1
        for t in nt: st["note"][t] += 1
        pav = pavimento(c, R)
        if pav:
            if e in PERMISSIVI:
                st["pav_violato_esito_permissivo"] += 1
                if len(st["esempi_pav_permissivo"]) < 12:
                    st["esempi_pav_permissivo"].append((c, pav, tr, NOMI_ESITO[e]))
            if not any(t.startswith("P.") for t in tr):
                st["pav_mai_consultato"] += 1
        if danno_reale_non_coperto(c):
            st["danno_reale_tot"] += 1
            if e in PERMISSIVI:
                st["danno_reale_permissivo"] += 1
        if e == INDECIDIBILE:
            st["indecidibili_traccia"][tuple(tr)] += 1
            if len(st["esempi_indecidibili"]) < 8:
                st["esempi_indecidibili"].append((c, tr))
        if dipende_da_non_verificabile(tr):
            st["decisioni_su_non_verificabile"] += 1
        if nt and e in PERMISSIVI:
            if any(x.startswith("5.") for x in nt):
                st["rilevatore_senza_effetto"] += 1
    return st

def pct(a, b):
    return 0.0 if not b else 100.0*a/b
