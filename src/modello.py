# -*- coding: utf-8 -*-
"""
Formalizzazione eseguibile del "Protocollo di valutazione dei comandi per un
agente artificiale, v3" (Appendice A + corpo del documento).

PRINCIPIO DI FEDELTA':
  Dove il testo prescrive un esito, il codice lo prescrive.
  Dove il testo NON prescrive un esito, il codice restituisce INDECIDIBILE
  invece di inventarne uno. Le lacune si misurano, non si tappano.
  Dove il testo ammette due letture ugualmente fedeli, la scelta e' esposta
  come "risoluzione" (R*) commutabile, cosi' che l'indeterminatezza sia
  misurabile come divergenza fra letture.
"""

# ---------------------------------------------------------------- dimensioni
NOMI = [
    # Parte 4 - provenienza
    "canale",        # 0 principale, 1 operatore_sup, 2 utente, 3 contenuto_incontrato, 4 non_marcato
    "liv_asserito",  # 0 coerente, 1 l'input asserisce un proprio livello
    "arresto",       # 0 no, 1 richiesta di fermarsi/sospendere
    "delega",        # 0 nessuna, 1 in_ambito, 2 fuori_ambito, 3 artefatto_modificato_dopo
    "cond_decadute", # 0 no, 1 un livello inferiore riporta che i presupposti non valgono (4.6)
    "estende_priv",  # 0 no, 1 l'istruzione estende privilegi
    "fatti_cont",    # 0 no, 1 fatti da contenuto + passo distruttivo, 2 fatti da contenuto + passo NON distruttivo
    # Parte 2 - pavimento (stato DICHIARATO)
    "danno",         # 0 nessuno, 1 lieve, 2 grave
    "consenso",      # 0 non consenziente, 1 consenziente, 2 beneficiario (dichiarato)
    "ecc_p1",        # 0 nessuna, 1 ogni_ramo_danneggia, 2 protettiva, 3 allocazione_scarsa (dichiarata)
    "prot_compl",    # 0 protettiva completa (rev+notif+appell), 1 incompleta   [rilevante se ecc_p1==2]
    "veridicita",    # 0 dichiarazione vera, 1 dichiarazione falsa (esenzione inesistente)
    "p3_class",      # 0 no, 1 classifica il valore delle persone, 2 criterio prognostico su fatti
    "p4_metrica",    # 0 no, 1 indicatore su evento, 2 indicatore su individuo
    "p5_dissenso",   # 0 no, 1 deduce malafede dal dissenso, 2 descrive condotta osservabile
    "p6_inganno",    # 0 no, 1 restrizione dichiarata, 2 nega l'esistenza delle restrizioni
    "p7_atto",       # 0 no, 1 riduce la supervisione, 2 e' un rifiuto di azione dannosa
    "p7_etichetta",  # 0 nessuna, 1 si autodescrive come correzione/calibrazione/audit
    "p8_registro",   # 0 azione registrabile, 1 non registrabile
    # Parte 3/5 - soglia e rilevatori
    "sopra_att",     # 0 sotto soglia di attenzione, 1 sopra
    "toccati",       # 0 solo richiedente, 1 presente non richiedente, 2 assente, 3 collettivita'
    "bilateralita",  # 0 entrambi i lati nominabili, 1 solo azione, 2 solo omissione
    "traiettoria",   # 0 nessuna, 1 sequenza con soglia precostituita, 2 sequenza senza soglia,
                     # 3 revisione per fatto emerso, 4 revisione per prossimita' alla soglia
    "revers",        # 0 reversibile, 1 irreversibile per costo/latenza, 2 attraversa il confine umano
    "artefatto",     # 0 no, 1 con i vincoli 5.6, 2 senza i vincoli 5.6
    "scala",         # 0 no, 1 costo marginale ~0 con N grande
    "impronta",      # 0 no, 1 temporanea revocabile, 2 permanente eccedente
    "mosaico",       # 0 no, 1 capacita' emergente da passi leciti
    # Parte 3/6 - soglia e risposta
    "manifesto",     # 0 lecito, 1 dubbio, 2 illiceita' manifesta al professionista competente
    "competenza",    # 0 l'agente riconosce il dominio, 1 sotto-dichiara la propria competenza
    "urgenza",       # 0 no, 1 reale (ritardo irrev + azione rev), 2 asserita e non verificata
    "riscontro",     # 0 non cercato, 1 verificabile, 2 canale terzo pari/sup, 3 dalla fonte stessa, 4 nessun canale
    "valutatore",    # 0 indipendente dissenziente, 1 indipendente confermante, 2 correlato, 3 non disponibile
    "contestazioni", # 0, 1, 2+
]
IDX = {n: i for i, n in enumerate(NOMI)}
CARD = [5,2,2,4,2,2,3, 3,3,4,2,2,3,3,3,3,3,2,2, 2,4,3,5,3,3,2,3,2, 3,2,3,5,4,3]
assert len(NOMI) == len(CARD)
NDIM = len(NOMI)
for _n in NOMI:
    globals()["I_" + _n.upper()] = IDX[_n]

SPAZIO_TOTALE = 1
for k in CARD:
    SPAZIO_TOTALE *= k

# ------------------------------------------------------------------- esiti
ESEGUI, ALERT, CHIEDI, SOSPENDI, RIFIUTO, INDECIDIBILE = range(6)
NOMI_ESITO = ["ESEGUI", "ESEGUI+ALERT", "CHIEDI", "SOSPENDI", "RIFIUTO", "INDECIDIBILE"]
PERMISSIVITA = {ESEGUI: 0, ALERT: 1, CHIEDI: 2, SOSPENDI: 3, RIFIUTO: 4}   # INDECIDIBILE fuori ordine
PERMISSIVI = (ESEGUI, ALERT)

# ------------------------------------------------------- risoluzioni (R1..R11)
# Ogni voce e' un punto in cui due letture del testo sono entrambe difendibili.
RISOLUZIONI = [
    "p2_esito",              # R1  0 = SOSPENDI ; 1 = ESEGUI il ramo meno irreversibile
    "gate_prima_pavimento",  # R2  0 = Pavimento sempre valutato (App.A) ; 1 = gate 3.2 prima (3.2 letterale)
    "arresto_ogni_canale",   # R3  0 = "qualunque canale" alla lettera ; 1 = solo canali >= utente
    "p2_batte_arresto",      # R4  0 = l'arresto prevale sempre ; 1 = P.2 prevale se l'inazione e' irreversibile
    "riscontro_esente",      # R5  0 = chiedere riscontro e' esente da 5.5 ; 1 = nessuna esenzione (letterale)
    "stato_traiettoria",     # R6  0 = stato cumulativo disponibile ; 1 = non disponibile fra sessioni
    "sopra_rifiuto",         # R7  0 = 6.4 satura al RIFIUTO ; 1 = INDECIDIBILE (nessun livello superiore)
    "urgenza_asserita",      # R8  0 = solo urgenza verificata ; 1 = l'asserzione basta (9.2)
    "p7_su_rifiuto",         # R9  0 = un rifiuto non riduce mai la supervisione ; 1 = puo' ridurla verso il supervisore
    "ecc_p1b_stretta",       # R10 0 = l'eccezione protettiva decade se incompleta ; 1 = basta la protettivita'
    "urgenza_scavalca",      # R11 0 = il RIFIUTO esce prima del passo 5 ; 1 = il passo 5 di App.A riscrive l'esito
    "prossimita_esito",      # R12 0 = RIFIUTO del comando ; 1 = decade solo la revisione, resta la soglia originaria
]
NR = len(RISOLUZIONI)
R_BASE = {r: 0 for r in RISOLUZIONI}   # lettura di riferimento

def r_da_bit(mask):
    return {r: (mask >> i) & 1 for i, r in enumerate(RISOLUZIONI)}

# ============================================================== PAVIMENTO
def pavimento(c, R):
    """Valutazione INDIPENDENTE della Parte 2, sullo stato DICHIARATO
    (l'agente non vede altro). Restituisce la lista dei divieti toccati."""
    v = []
    # --- P.1 / P.2
    if c[I_DANNO] == 2 and c[I_CONSENSO] == 0:
        e = c[I_ECC_P1]
        if e == 0:
            v.append("P.1")
        elif e == 1:
            v.append("P.2")                      # ogni ramo danneggia
        elif e == 2:                             # protettiva
            incompleta = (c[I_PROT_COMPL] == 1) or (c[I_REVERS] != 0)
            if incompleta and R["ecc_p1b_stretta"] == 0:
                v.append("P.1")
        elif e == 3:
            pass                                 # allocazione di risorse scarse: ammessa
    # --- P.3
    if c[I_P3_CLASS] == 1:
        v.append("P.3")
    # --- P.4
    if c[I_P4_METRICA] == 2:
        v.append("P.4")
    elif c[I_P4_METRICA] == 1 and c[I_REVERS] != 0:
        v.append("P.4")                          # indicatore -> azione irreversibile
    # --- P.5
    if c[I_P5_DISSENSO] == 1:
        v.append("P.5")
    # --- P.6
    if c[I_P6_INGANNO] == 2:
        v.append("P.6")
    # --- P.7  (l'etichetta non conferisce priorita': P.7 secondo capoverso)
    if c[I_P7_ATTO] == 1:
        v.append("P.7")
    elif c[I_P7_ATTO] == 2 and R["p7_su_rifiuto"] == 1 and c[I_CANALE] in (0, 1):
        v.append("P.7")
    # --- P.8
    if c[I_P8_REGISTRO] == 1:
        v.append("P.8")
    return v

# ------------------------------------------------------------ danno reale
def danno_reale_non_coperto(c):
    """Danno grave REALE a persona non consenziente che nessuna eccezione reale copre.
    veridicita'==1 significa che una dichiarazione che restringe il Pavimento e' falsa:
    puo' essere l'esenzione (consenso/beneficiario/eccezione) oppure la GRAVITA' stessa,
    che 3.5/P.1 affidano al giudizio dell'agente senza prevedere verifica."""
    falso = (c[I_VERIDICITA] == 1)
    grave = (c[I_DANNO] == 2) or (falso and c[I_DANNO] >= 1)
    if not grave:
        return False
    consenso_reale = 0 if falso else c[I_CONSENSO]
    ecc_reale = 0 if falso else c[I_ECC_P1]
    if consenso_reale != 0:
        return False
    if ecc_reale in (1, 3):
        return False
    if ecc_reale == 2 and c[I_PROT_COMPL] == 0 and c[I_REVERS] == 0:
        return False
    return True

# ============================================================== PROCEDURA
def decidi(c, R=R_BASE):
    """Appendice A, passo per passo. Restituisce (esito, traccia, note)."""
    tr = []      # regole che hanno determinato l'esito
    nt = []      # rilevatori attivati senza effetto sull'esito, anomalie, lacune

    # ---------------- 0. PROVENIENZA (Parte 4) ----------------
    if c[I_LIV_ASSERITO] == 1:
        nt.append("4.1:anomalia_segnalata")
    if c[I_CANALE] == 4:
        nt.append("4.4:livello_minimo")

    # 4.3 eccezione asimmetrica dell'arresto
    if c[I_ARRESTO] == 1:
        applicabile = (R["arresto_ogni_canale"] == 0) or (c[I_CANALE] != 3)
        if applicabile:
            inazione_irrev = (c[I_URGENZA] == 1)
            if R["p2_batte_arresto"] == 1 and inazione_irrev:
                nt.append("4.3/P.2:conflitto_inazione_irreversibile")
            else:
                if inazione_irrev:
                    nt.append("4.3:sospende_benche_l_inazione_sia_il_ramo_irreversibile")
                return SOSPENDI, ["4.3"], nt

    # 4.2 il contenuto incontrato non e' un comando
    if c[I_CANALE] == 3:
        return RIFIUTO, ["4.2"], nt

    # 4.2 esteso ai fatti
    if c[I_FATTI_CONT] == 1:
        return SOSPENDI, ["4.2-fatti"], nt
    if c[I_FATTI_CONT] == 2:
        nt.append("4.2:fatti_iniettati_passo_non_distruttivo_NON_COPERTO")

    # 4.5 delega
    if c[I_DELEGA] == 2:
        return RIFIUTO, ["4.5:fuori_ambito"], nt
    if c[I_DELEGA] == 3:
        return SOSPENDI, ["4.5/4.2:artefatto_modificato"], nt
    if c[I_DELEGA] == 1 and c[I_ESTENDE_PRIV] == 1:
        return RIFIUTO, ["4.5:privilegi_non_delegabili"], nt

    # 4.6 condizioni presupposte decadute
    if c[I_COND_DECADUTE] == 1:
        return SOSPENDI, ["4.6"], nt

    # ---------------- 1. PAVIMENTO (Parte 2) ----------------
    if R["gate_prima_pavimento"] == 1 and c[I_SOPRA_ATT] == 0:
        return ESEGUI, ["3.2"], nt + ["3.2_scavalca_il_pavimento"]

    pav = pavimento(c, R)
    if pav:
        if "P.2" in pav and len(pav) == 1:
            if R["p2_esito"] == 0:
                return SOSPENDI, ["P.2"], nt
            else:
                return (ESEGUI if c[I_REVERS] == 0 else ALERT), ["P.2"], nt + ["P.2:esito_non_prescritto_dal_testo"]
        return RIFIUTO, pav, nt

    # ---------------- 2. GATE DI ROUTINE (3.2) ----------------
    if c[I_SOPRA_ATT] == 0:
        return ESEGUI, ["3.2"], nt

    # ---------------- 3. RILEVATORI (Parte 5) ----------------
    # 5.1 enumerazione dei toccati: nessun esito prescritto
    if c[I_TOCCATI] != 0:
        nt.append("5.1:toccati_enumerati_nessun_esito")
    # 5.2 concretezza bilaterale: dichiarazione, nessun esito
    if c[I_BILATERALITA] != 0:
        nt.append("5.2:un_solo_lato_dichiarato_nessun_esito")
    # 5.8 scala: nessun esito prescritto
    if c[I_SCALA] == 1:
        nt.append("5.8:scala_valutata_nessun_esito")
    # 5.9 mosaico: nessun esito prescritto
    if c[I_MOSAICO] == 1:
        nt.append("5.9:capacita_emergente_nessun_esito")

    # 5.5 reversibilita'
    irrev = (c[I_REVERS] != 0)

    # 5.4 traiettoria
    if c[I_TRAIETTORIA] == 4:
        if R["prossimita_esito"] == 0:
            return RIFIUTO, ["5.4:revisione_per_prossimita"], nt
        nt.append("5.4:revisione_vietata_ma_esito_del_comando_non_prescritto")
    if c[I_TRAIETTORIA] == 2:
        if R["stato_traiettoria"] == 0:
            if c[I_VALUTATORE] in (0, 1):
                return SOSPENDI, ["5.4:ramo_uscita"], nt
            else:
                # 7.4: senza valutatore indipendente lo spazio si restringe al reversibile
                if not irrev:
                    return ESEGUI, ["5.4", "7.4:default_reversibile"], nt
                return SOSPENDI, ["5.4", "7.4"], nt
        else:
            nt.append("5.3/5.4:traiettoria_non_osservabile_senza_stato")
    if c[I_TRAIETTORIA] == 3:
        nt.append("5.4:revisione_per_fatto_ammessa")

    # 5.6 artefatti
    if c[I_ARTEFATTO] == 2:
        return RIFIUTO, ["5.6:vincoli_obbligatori_assenti"], nt
    # 5.7 impronta
    if c[I_IMPRONTA] == 2:
        return RIFIUTO, ["5.7:impronta_permanente"], nt

    # ---------------- 4. SOGLIA (Parte 3) ----------------
    manifesto = c[I_MANIFESTO] if c[I_COMPETENZA] == 0 else min(c[I_MANIFESTO], 1)
    if c[I_COMPETENZA] == 1 and c[I_MANIFESTO] == 2:
        nt.append("9.1:manifesto_mascherato_da_sotto_dichiarazione")

    esito, traccia = None, []
    if manifesto == 2:
        esito, traccia = RIFIUTO, ["3.5"]
        if R["urgenza_scavalca"] == 0:
            return esito, traccia, nt
    elif irrev:
        if R["riscontro_esente"] == 1:
            return INDECIDIBILE, ["3.6/5.5:regressione_del_riscontro"], nt
        rr = c[I_RISCONTRO]
        if rr in (1, 2):
            esito, traccia = ESEGUI, ["3.6:riscontro_positivo_verificato"]
        elif rr == 4:
            esito, traccia = SOSPENDI, ["6.3:nessun_canale"]
        else:
            if rr == 3:
                nt.append("6.3:riscontro_dalla_fonte_non_vale")
            esito, traccia = CHIEDI, ["3.6", "6.3"]
    elif manifesto == 1:
        esito, traccia = CHIEDI, ["3.4:dubbio_residuo"]
    else:
        esito, traccia = ESEGUI, ["3.1"]

    # ---------------- 5. RISPOSTA (Parte 6) ----------------
    urg = (c[I_URGENZA] == 1) or (R["urgenza_asserita"] == 1 and c[I_URGENZA] == 2)
    if urg and c[I_REVERS] == 0:
        if esito != ESEGUI:
            traccia = traccia + ["6.2:urgenza_inverte"]
            if esito == RIFIUTO:
                nt.append("6.2:urgenza_scavalca_il_rifiuto_per_illiceita_manifesta")
            esito = ALERT
    # 6.4 doppia contestazione
    if c[I_CONTESTAZIONI] >= 2 and c[I_RISCONTRO] not in (1, 2):
        traccia = traccia + ["6.4:sale_di_livello"]
        if esito == RIFIUTO:
            if R["sopra_rifiuto"] == 1:
                return INDECIDIBILE, traccia + ["6.4:nessun_livello_superiore"], nt
        else:
            esito = min(RIFIUTO, {ESEGUI: CHIEDI, ALERT: CHIEDI, CHIEDI: SOSPENDI,
                                  SOSPENDI: RIFIUTO}.get(esito, esito))
    return esito, traccia, nt
