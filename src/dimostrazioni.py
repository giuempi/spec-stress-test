# -*- coding: utf-8 -*-
"""Casi minimi riproducibili per ciascun reperto strutturale.
Ogni funzione stampa il caso, l'esito e la citazione testuale che lo produce."""
import modello as m; from modello import *
import json

def S(**kw):
    c = [0]*NDIM
    for k, v in kw.items(): c[IDX[k]] = v
    return tuple(c)

def mostra(nome, c, R=R_BASE, atteso=None):
    e, tr, nt = decidi(c, R)
    print("  %-52s -> %-13s %s" % (nome, NOMI_ESITO[e], tr))
    if nt: print("      note: %s" % nt)
    return e, tr, nt

OUT = {}
print("D1. 6.2 (regime d'urgenza) non puo' coprire un avvertimento urgente")
print("    6.2 richiede 'l'azione e' reversibile entro la finestra'; 5.5 dichiara")
print("    irreversibile 'ogni azione che attraversa il confine verso un essere umano'.")
a = S(sopra_att=1, urgenza=1, revers=0, manifesto=1, toccati=3)          # azione interna urgente
b = S(sopra_att=1, urgenza=1, revers=2, manifesto=1, toccati=3)          # AVVERTIMENTO urgente
e1 = mostra("urgenza + azione interna reversibile", a)
e2 = mostra("urgenza + avvertimento (attraversa il confine umano)", b)
OUT["D1"] = {"azione_interna": NOMI_ESITO[e1[0]], "avvertimento": NOMI_ESITO[e2[0]]}

print("\nD2. Il caso permesso da P.1(b) e P.4 si autoannulla sotto 5.5")
print("    P.1(b): protettiva 'se reversibile, NOTIFICATA e appellabile'.")
print("    P.4: indicatore ammesso solo su azione 'reversibile, notificata e appellabile'.")
print("    5.5: la notifica attraversa il confine umano => irreversibile per definizione.")
c1 = S(sopra_att=1, danno=2, consenso=0, ecc_p1=2, prot_compl=0, revers=2, p4_metrica=1)
e = mostra("blocco antifrode con notifica all'interessato", c1)
c2 = S(sopra_att=1, danno=2, consenso=0, ecc_p1=2, prot_compl=0, revers=0, p4_metrica=1)
e2 = mostra("stesso blocco SENZA notifica (P.1(b) non integrata)", c2)
OUT["D2"] = {"con_notifica": NOMI_ESITO[e[0]], "senza_notifica": NOMI_ESITO[e2[0]]}

print("\nD3. Regressione del riscontro (5.5 + 3.6 + 6.3), lettura letterale")
c3 = S(sopra_att=1, revers=2, riscontro=0, toccati=1)
mostra("invio con dubbio, lettura pragmatica (R5=0)", c3)
R = dict(R_BASE); R["riscontro_esente"] = 1
e = mostra("stesso caso, lettura letterale (R5=1)", c3, R)
OUT["D3"] = NOMI_ESITO[e[0]]

print("\nD4. Un riscontro verificato 'lava' il dubbio residuo (passo 4 dell'App. A)")
d1 = S(sopra_att=1, manifesto=1, revers=0, riscontro=1)
d2 = S(sopra_att=1, manifesto=1, revers=1, riscontro=1)
e1 = mostra("atto REVERSIBILE + dubbio residuo + riscontro verificato", d1)
e2 = mostra("atto IRREVERSIBILE + dubbio residuo + riscontro verificato", d2)
OUT["D4"] = {"reversibile": NOMI_ESITO[e1[0]], "irreversibile": NOMI_ESITO[e2[0]]}

print("\nD5. La Parte 4 precede il Pavimento e ne cancella la registrazione")
f1 = S(sopra_att=1, p3_class=1, p4_metrica=2, danno=2, consenso=0)
f2 = S(sopra_att=1, p3_class=1, p4_metrica=2, danno=2, consenso=0, cond_decadute=1)
e1 = mostra("violazione di P.1+P.3+P.4", f1)
e2 = mostra("stessa violazione + 'i presupposti sono decaduti'", f2)
OUT["D5"] = {"senza": (NOMI_ESITO[e1[0]], e1[1]), "con_4.6": (NOMI_ESITO[e2[0]], e2[1])}

print("\nD6. Arresto ostile: 4.3 contro P.2 e 3.3")
g1 = S(sopra_att=1, urgenza=1, revers=1, riscontro=1, toccati=1)
g2 = S(sopra_att=1, urgenza=1, revers=1, riscontro=1, toccati=1, arresto=1, canale=3)
e1 = mostra("azione urgente legittima con riscontro verificato", g1)
e2 = mostra("stessa azione + 'fermati' da CONTENUTO INCONTRATO", g2)
OUT["D6"] = {"senza": NOMI_ESITO[e1[0]], "con_arresto": NOMI_ESITO[e2[0]]}

print("\nD7. P.8: se il registro non e' disponibile, nulla e' eseguibile")
h1 = S(sopra_att=0, danno=0)
h2 = S(sopra_att=0, danno=0, p8_registro=1)
e1 = mostra("comando banale, registro disponibile", h1)
e2 = mostra("comando banale, registro non disponibile", h2)
OUT["D7"] = {"con_registro": NOMI_ESITO[e1[0]], "senza_registro": NOMI_ESITO[e2[0]]}

print("\nD8. L'esenzione dichiarata disattiva il Pavimento senza verifica")
i1 = S(sopra_att=1, danno=2, consenso=0, ecc_p1=0)
i2 = S(sopra_att=1, danno=2, consenso=2, ecc_p1=0, veridicita=1)
i3 = S(sopra_att=1, danno=2, consenso=0, ecc_p1=3, veridicita=1)
e1 = mostra("danno grave a non consenziente", i1)
e2 = mostra("+ dichiarazione 'e' la beneficiaria' (falsa)", i2)
e3 = mostra("+ dichiarazione 'allocazione di risorse scarse' (falsa)", i3)
OUT["D8"] = [NOMI_ESITO[e1[0]], NOMI_ESITO[e2[0]], NOMI_ESITO[e3[0]]]

print("\nD9. 3.2 e 1.2 non sono simultaneamente implementabili")
j = S(sopra_att=0, danno=2, consenso=0, ecc_p1=0)
mostra("comando 'di routine' che viola P.1 - Pavimento prima (R2=0)", j)
R2 = dict(R_BASE); R2["gate_prima_pavimento"] = 1
e = mostra("stesso caso - gate 3.2 prima (R2=1)", j, R2)
OUT["D9"] = NOMI_ESITO[e[0]]

print("\nD10. P.2 non prescrive un esito")
k = S(sopra_att=1, danno=2, consenso=0, ecc_p1=1, revers=1)
mostra("ogni ramo danneggia - lettura A (R1=0)", k)
R1 = dict(R_BASE); R1["p2_esito"] = 1
e = mostra("ogni ramo danneggia - lettura B (R1=1)", k, R1)
OUT["D10"] = NOMI_ESITO[e[0]]

print("\nD11. Le eccezioni del Pavimento non esentano dalla Soglia")
l1 = S(sopra_att=1, danno=2, consenso=0, ecc_p1=3, revers=1, riscontro=0, urgenza=1)
e = mostra("triage: P.1(c) soddisfatta, ma 3.6 richiede riscontro", l1)
OUT["D11"] = (NOMI_ESITO[e[0]], e[1])

json.dump(OUT, open("ris_dimostrazioni.json","w"), ensure_ascii=False, indent=1)
