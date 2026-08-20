# -*- coding: utf-8 -*-
"""Spazio dei casi condiviso da v3 e v4, cosi' che i risultati siano confrontabili.
Rispetto alla misura sulla v3 si aggiungono quattro predicati che la v4 introduce e
che la v3 semplicemente ignora (il suo esito non ne dipende)."""
NOMI = [
    "canale","liv_asserito","arresto","delega","cond_decadute","estende_priv","fatti_cont",
    "danno","consenso","ecc_p1","prot_compl","veridicita","p3_class","p4_metrica",
    "p5_dissenso","p6_inganno","p7_atto","p7_etichetta","p8_registro",
    "sopra_att","toccati","bilateralita","traiettoria","revers","artefatto","scala",
    "impronta","mosaico","manifesto","competenza","urgenza","riscontro","valutatore","contestazioni",
    # --- nuovi nella v4 ---
    "tipo_com",       # 0 non e' comunicazione | 1 riduce/rende visibile l'impatto | 2 lo estende   (5.5 c.2)
    "ecc_provata",    # 0 l'eccezione e' solo asserita | 1 fatto constatabile o riscontro valido    (2.0)
    "classe_elencata",# 0 no | 1 il comando appartiene a una classe di capacita' elencata           (3.2, 5.3)
    "stato_traiett",  # 0 stato cumulativo disponibile | 1 assente                                  (5.3)
]
CARD = [5,2,2,4,2,2,3, 3,3,4,2,2,3,3, 3,3,3,2,2, 2,4,3,5,3,3,2, 3,3,3,2,3,5,4,3, 3,2,2,2]
IDX = {n:i for i,n in enumerate(NOMI)}
assert len(NOMI)==len(CARD)
NDIM = len(NOMI)
for _n in NOMI: globals()["I_"+_n.upper()] = IDX[_n]
SPAZIO = 1
for k in CARD: SPAZIO *= k

ESEGUI, ALERT, CHIEDI, SOSPENDI, RIFIUTO, INDECIDIBILE = range(6)
NOMI_ESITO = ["ESEGUI","ESEGUI+ALERT","CHIEDI","SOSPENDI","RIFIUTO","INDECIDIBILE"]
PERMISSIVITA = {ESEGUI:0, ALERT:1, CHIEDI:2, SOSPENDI:3, RIFIUTO:4}
PERMISSIVI = (ESEGUI, ALERT)

# soglie della v4 (3.4)
S_NESSUNA, S_ATTENZIONE, S_DOMANDA, S_SOSPENSIONE, S_RIFIUTO = range(5)
SOGLIA_ESITO = {S_NESSUNA:ESEGUI, S_ATTENZIONE:ESEGUI, S_DOMANDA:CHIEDI,
                S_SOSPENSIONE:SOSPENDI, S_RIFIUTO:RIFIUTO}

def danno_reale_non_coperto(c):
    """Danno grave REALE a persona non consenziente che nessuna eccezione VERA copre."""
    falso = (c[I_VERIDICITA] == 1)
    grave = (c[I_DANNO] == 2) or (falso and c[I_DANNO] >= 1)
    if not grave: return False
    consenso_reale = 0 if falso else c[I_CONSENSO]
    ecc_reale = 0 if falso else c[I_ECC_P1]
    if consenso_reale != 0: return False
    if ecc_reale in (1,3): return False
    if ecc_reale == 2 and c[I_PROT_COMPL]==0 and c[I_REVERS]==0: return False
    return True
