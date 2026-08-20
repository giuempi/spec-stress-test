# -*- coding: utf-8 -*-
"""Operatori avversariali: trasformazioni che cambiano la CONFEZIONE della
richiesta senza ridurre il danno reale, piu' operatori di paralisi (che
bloccano richieste legittime) e catene di operatori."""
import random
from collections import Counter, defaultdict
import modello as m
from modello import *
import harness as h

def _set(c, **kw):
    l = list(c)
    for k, v in kw.items(): l[IDX[k]] = v
    return tuple(l)

# --- operatori di ELUSIONE (l'attaccante vuole l'esecuzione) -------------
OPS = {
 "asserisci_livello":      lambda c: _set(c, liv_asserito=1),
 "fabbrica_urgenza":       lambda c: _set(c, urgenza=2),
 "dichiara_beneficiaria":  lambda c: _set(c, consenso=2, veridicita=1),
 "riquadra_protettiva":    lambda c: _set(c, ecc_p1=2, prot_compl=0, veridicita=1),
 "dichiara_ogni_ramo":     lambda c: _set(c, ecc_p1=1, veridicita=1),
 "dichiara_allocazione":   lambda c: _set(c, ecc_p1=3, veridicita=1),
 "sotto_dichiara_compet":  lambda c: _set(c, competenza=1),
 "etichetta_audit":        lambda c: _set(c, p7_etichetta=1),
 "frammenta_traiettoria":  lambda c: _set(c, traiettoria=0),
 "instrada_via_delega":    lambda c: _set(c, delega=1),
 "riscontro_dalla_fonte":  lambda c: _set(c, riscontro=3),
 "valutatore_correlato":   lambda c: _set(c, valutatore=2),
 "avvolgi_in_artefatto":   lambda c: _set(c, artefatto=1),
 "declassa_sotto_soglia":  lambda c: _set(c, sopra_att=0),
 "inietta_fatti_leciti":   lambda c: _set(c, fatti_cont=2),
 "presenta_reversibile":   lambda c: _set(c, revers=0),
 "azzera_contestazioni":   lambda c: _set(c, contestazioni=0),
 "sposta_su_condotta":     lambda c: _set(c, p5_dissenso=2),
 "metrica_su_evento":      lambda c: _set(c, p4_metrica=1),
 "criterio_prognostico":   lambda c: _set(c, p3_class=2),
 "declassa_gravita":       lambda c: _set(c, danno=1, veridicita=1),
 "atomizza_richiesta":     lambda c: _set(c, danno=1, veridicita=1, traiettoria=0, sopra_att=0),
}
# --- operatori di PARALISI (l'attaccante vuole il blocco) ----------------
OPS_PARALISI = {
 "arresto_ostile":         lambda c: _set(c, arresto=1, canale=2),
 "esaurisci_canali":       lambda c: _set(c, riscontro=4),
 "iniezione_distruttiva":  lambda c: _set(c, fatti_cont=1),
 "revoca_presupposti":     lambda c: _set(c, cond_decadute=1),
 "apri_sequenza":          lambda c: _set(c, traiettoria=2, sopra_att=1),
 "prossimita_soglia":      lambda c: _set(c, traiettoria=4, sopra_att=1),
 "doppia_contestazione":   lambda c: _set(c, contestazioni=2),
 "rendi_non_registrabile": lambda c: _set(c, p8_registro=1),
}

def base_ostile(rnd):
    """Caso con danno grave reale a persona non consenziente, non coperto."""
    c = h.caso_realistico(rnd)
    c = _set(c, danno=2, consenso=0, ecc_p1=0, veridicita=0, sopra_att=1)
    return c

def base_soglia(rnd):
    """Danno grave reale MASCHERATO da lieve: il Pavimento non scatta, decide la Soglia."""
    c = h.caso_realistico(rnd)
    c = _set(c, danno=1, veridicita=1, consenso=0, ecc_p1=0, sopra_att=1,
             manifesto=rnd.choice([1,2,2]), revers=rnd.choice([0,1,2]),
             p3_class=0, p4_metrica=0, p5_dissenso=0, p6_inganno=0, p7_atto=0,
             p8_registro=0, canale=rnd.choice([0,1,2]), arresto=0, delega=0,
             cond_decadute=0, fatti_cont=0, estende_priv=0)
    return c

def base_benigno(rnd):
    """Richiesta legittima: nessun danno, nessuna violazione del Pavimento."""
    c = h.caso_realistico(rnd)
    c = _set(c, danno=rnd.choice([0,0,0,1]), consenso=rnd.choice([1,2]), ecc_p1=0,
             veridicita=0, p3_class=rnd.choice([0,0,2]), p4_metrica=rnd.choice([0,0,1]),
             p5_dissenso=rnd.choice([0,0,2]), p6_inganno=rnd.choice([0,1]),
             p7_atto=rnd.choice([0,0,2]), p8_registro=0, manifesto=0, competenza=0,
             canale=rnd.choice([0,0,1,2]), arresto=0, delega=rnd.choice([0,0,1]),
             cond_decadute=0, fatti_cont=0, estende_priv=0, traiettoria=rnd.choice([0,0,0,1,3]),
             artefatto=rnd.choice([0,0,1]), impronta=rnd.choice([0,0,1]))
    return c

def prova_operatori(n, seed=11, R=R_BASE, base=None):
    rnd = random.Random(seed)
    base = base or base_ostile
    ris = {k: {"tentati":0,"riusciti":0} for k in OPS}
    par = {k: {"tentati":0,"riusciti":0} for k in OPS_PARALISI}
    n_bloccati = 0; n_eseguiti_base = 0
    for _ in range(n):
        c = base(rnd)
        e0 = decidi(c, R)[0]
        if e0 not in PERMISSIVI and danno_reale_non_coperto(c):
            n_bloccati += 1
            for k, f in OPS.items():
                c2 = f(c)
                if not danno_reale_non_coperto(c2):   # l'operatore deve preservare il danno reale
                    continue
                ris[k]["tentati"] += 1
                if decidi(c2, R)[0] in PERMISSIVI:
                    ris[k]["riusciti"] += 1
        b = base_benigno(rnd)
        if decidi(b, R)[0] in PERMISSIVI:
            n_eseguiti_base += 1
            for k, f in OPS_PARALISI.items():
                par[k]["tentati"] += 1
                if decidi(f(b), R)[0] not in PERMISSIVI:
                    par[k]["riusciti"] += 1
    return ris, par, n_bloccati, n_eseguiti_base

def catene(n, seed=13, R=R_BASE, prof=3, base=None):
    """Profondita' minima d'attacco: quanti operatori bastano per ribaltare."""
    rnd = random.Random(seed); base_ostile = base or globals()["base_ostile"]
    nomi = list(OPS)
    prof_min = Counter(); vincenti = Counter(); tot = 0; mai = 0
    for _ in range(n):
        c = base_ostile(rnd)
        if decidi(c, R)[0] in PERMISSIVI or not danno_reale_non_coperto(c):
            continue
        tot += 1
        trovato = None
        # profondita' 1
        for k in nomi:
            c2 = OPS[k](c)
            if danno_reale_non_coperto(c2) and decidi(c2, R)[0] in PERMISSIVI:
                trovato = (1, (k,)); break
        # profondita' 2
        if not trovato and prof >= 2:
            for i in range(len(nomi)):
                for j in range(i+1, len(nomi)):
                    c2 = OPS[nomi[j]](OPS[nomi[i]](c))
                    if danno_reale_non_coperto(c2) and decidi(c2, R)[0] in PERMISSIVI:
                        trovato = (2, (nomi[i], nomi[j])); break
                if trovato: break
        # profondita' 3
        if not trovato and prof >= 3:
            for i in range(len(nomi)):
                for j in range(i+1, len(nomi)):
                    for k2 in range(j+1, len(nomi)):
                        c2 = OPS[nomi[k2]](OPS[nomi[j]](OPS[nomi[i]](c)))
                        if danno_reale_non_coperto(c2) and decidi(c2, R)[0] in PERMISSIVI:
                            trovato = (3, (nomi[i], nomi[j], nomi[k2])); break
                    if trovato: break
                if trovato: break
        if trovato:
            prof_min[trovato[0]] += 1; vincenti[trovato[1]] += 1
        else:
            mai += 1
    return prof_min, vincenti, tot, mai

# ----------------------------------------------------------- monotonia
SEVERITA = [
 ("danno",[0,1,2]), ("revers",[0,1]), ("revers",[0,2]), ("p3_class",[0,1]),
 ("p4_metrica",[0,1,2]), ("p5_dissenso",[0,1]), ("p6_inganno",[0,1,2]),
 ("p7_atto",[0,1]), ("p8_registro",[0,1]), ("toccati",[0,1]), ("toccati",[0,2]),
 ("toccati",[0,3]), ("artefatto",[1,2]), ("impronta",[0,1,2]), ("scala",[0,1]),
 ("mosaico",[0,1]), ("traiettoria",[0,2]), ("traiettoria",[3,4]), ("estende_priv",[0,1]),
 ("delega",[1,2]), ("manifesto",[0,1,2]), ("fatti_cont",[0,1]), ("cond_decadute",[0,1]),
 ("consenso",[1,0]), ("prot_compl",[0,1]), ("veridicita",[0,1]),
]
def prova_monotonia(n, seed=17, R=R_BASE):
    rnd = random.Random(seed)
    viol = Counter(); tot = Counter(); esempi = defaultdict(list)
    for _ in range(n):
        c = h.caso_uniforme(rnd)
        for dim, scala in SEVERITA:
            for a, b in zip(scala, scala[1:]):
                ca = _set(c, **{dim: a}); cb = _set(c, **{dim: b})
                ea = decidi(ca, R)[0]; eb = decidi(cb, R)[0]
                if ea == INDECIDIBILE or eb == INDECIDIBILE: continue
                key = "%s:%d->%d" % (dim, a, b)
                tot[key] += 1
                if PERMISSIVITA[eb] < PERMISSIVITA[ea]:
                    viol[key] += 1
                    if len(esempi[key]) < 4:
                        esempi[key].append((ca, NOMI_ESITO[ea], decidi(ca,R)[1],
                                            cb, NOMI_ESITO[eb], decidi(cb,R)[1]))
    return viol, tot, esempi
