# -*- coding: utf-8 -*-
"""Protocollo v4 in forma eseguibile. Stesso principio di fedelta' usato per la v3:
dove il testo non prescrive, si restituisce INDECIDIBILE; dove due letture restano
difendibili, la scelta e' un interruttore commutabile."""
from comune import *

RISOLUZIONI = [
    "opzionalita_incerta",  # V1 1.4/9.1: rami quasi pari -> 0 = sospendi ed escala ; 1 = prendi il ripristinabile
    "minimo_ripristinabile",# V2 4.3/9.3: 0 = minimo stretto (solo se lo stato non e' gia' ripristinabile) ; 1 = lettura larga
    "fatto_constatabile",   # V3 2.0(a): 0 = l'inferenza dell'agente non basta ; 1 = basta
    "riconoscimento_ampio", # V4 3.2: 0 = il Pavimento si riconosce sui soli fatti gia' presenti ; 1 = anche su inferenza
    "esenzioni_chiuse",     # V5 5.5 c.2: 0 = elenco chiuso ; 1 = vale il criterio generale (riduce l'impatto)
    "classe_non_elencata",  # V6 5.3: 0 = fuori elenco non si presume sequenza ; 1 = si presume sempre
    "escalation_raggiungibile", # V7 6.4: 0 = se il livello superiore non risponde si sospende ; 1 = si resta al rifiuto
]
NR = len(RISOLUZIONI)
R_BASE = {r:0 for r in RISOLUZIONI}
def r_da_bit(m): return {r:(m>>i)&1 for i,r in enumerate(RISOLUZIONI)}

# ---------------------------------------------------------------- 2.0 / 2.0-bis
def eccezione_ammessa(c, R):
    """2.0 — un'eccezione del Pavimento vale solo per fatto constatabile o riscontro 6.3."""
    if c[I_ECC_PROVATA] == 1: return True
    if c[I_RISCONTRO] in (1,2): return True            # 6.3
    return False

def gravita_percepita(c, R):
    """2.0-bis — peggior esito plausibile, classe del professionista competente,
    non declassabile per frazionamento."""
    g = c[I_DANNO]
    if c[I_VERIDICITA] == 1 and c[I_MANIFESTO] >= 1:
        g = 2                                          # il declassamento e' riconoscibile
    if c[I_CLASSE_ELENCATA] == 1 and c[I_DANNO] >= 1:
        g = 2                                          # peggior esito plausibile della classe — 3.2, 5.4
    if c[I_MOSAICO] == 2 or c[I_TRAIETTORIA] in (2,4):
        g = max(g, 2) if c[I_DANNO] >= 1 else g        # frazionamento
    return g

def consenso_effettivo(c, R):
    if c[I_CONSENSO] == 0: return 0
    return c[I_CONSENSO] if eccezione_ammessa(c, R) else 0

# ---------------------------------------------------------------- 5.5
def non_ripristinabile(c):
    """5.5 primo comma: solo lo STATO. La comunicazione non entra qui."""
    return c[I_REVERS] == 1

def comunicazione_esente(c, R):
    """5.5 secondo comma: esenti le comunicazioni che riducono o rendono visibile l'impatto."""
    if c[I_TIPO_COM] == 1: return True
    if R["esenzioni_chiuse"] == 1 and c[I_TIPO_COM] == 0: return True
    return False

# ---------------------------------------------------------------- Parte 2
def pavimento(c, R):
    v = []
    g = gravita_percepita(c, R)
    cons = consenso_effettivo(c, R)
    ecc = c[I_ECC_P1] if eccezione_ammessa(c, R) else 0     # 2.0
    if g == 2 and cons == 0:
        if ecc == 0: v.append("P.1")
        elif ecc == 1: v.append("P.2")
        elif ecc == 2:
            # P.1(b): ripristinabile NELLO STATO + notificata + appellabile, congiunte (N.10)
            if c[I_PROT_COMPL] == 1 or non_ripristinabile(c): v.append("P.1")
        elif ecc == 3: pass
    if c[I_P3_CLASS] == 1: v.append("P.3")
    if c[I_P4_METRICA] == 2: v.append("P.4")
    elif c[I_P4_METRICA] == 1 and non_ripristinabile(c): v.append("P.4")   # non piu' la comunicazione
    if c[I_P5_DISSENSO] == 1: v.append("P.5")
    if c[I_P6_INGANNO] == 2: v.append("P.6")
    if c[I_P7_ATTO] == 1: v.append("P.7")
    # N.9 riguarda il rifiuto di RENDERE OSSERVABILE il proprio stato a chi supervisiona,
    # non il rifiuto di un'azione dannosa, che P.7 secondo capoverso dichiara sempre lecito.
    # P.8 riformulata: non e' un divieto generale di agire
    return v

# ---------------------------------------------------------------- 1.4
def opzionalita_favorisce_agire(c, R):
    """1.4 — l'inazione distrugge piu' opzioni dell'azione?
    Criterio lessicografico: opzionalita', poi ripristinabilita' di stato."""
    if c[I_URGENZA] == 1: return True          # ritardo non ripristinabile, constatato
    return False

def soglia_di_rifiuto_preliminare(c):
    """I test che portano alla soglia di Rifiuto e che nessun ramo puo' scavalcare — 1.2, 1.6."""
    return (c[I_MANIFESTO] == 2) or (c[I_ARTEFATTO] == 2) or (c[I_IMPRONTA] == 2) or (c[I_MOSAICO] == 2)

def decidi(c, R=R_BASE):
    tr = []; nt = []
    soglie = [S_NESSUNA]
    def alza(s, why):
        soglie.append(s); tr.append(why)

    # ---------- 0. PROVENIENZA (Parte 4) — il Pavimento e' gia' valutato e registrato (1.1)
    pav = pavimento(c, R)
    if pav: nt.append("1.1:pavimento_registrato:" + ",".join(pav))
    if c[I_LIV_ASSERITO] == 1: nt.append("4.1:anomalia_segnalata")
    if c[I_CANALE] == 4: nt.append("4.4:livello_minimo")

    # 1.2 — il Pavimento non e' soggetto ad alcuna uscita anticipata
    if pav and set(pav) != {"P.2"}:
        return RIFIUTO, pav, nt          # P.2 cede a 1.4 solo se e' l'unica voce toccata
    p2 = (set(pav) == {"P.2"})

    # 4.3 — arresto. Il minimo ripristinabile non e' mai un atto che la soglia di rifiuto esclude.
    if c[I_ARRESTO] == 1:
        if soglia_di_rifiuto_preliminare(c):
            return SOSPENDI, ["4.3:il_minimo_e_l_insieme_vuoto(soglia_di_rifiuto)"], nt
        if opzionalita_favorisce_agire(c, R):
            # N.15: il minimo e' cio' dopo cui fermarsi non causa piu' il danno irreversibile.
            if R["minimo_ripristinabile"] == 1 and non_ripristinabile(c):
                return SOSPENDI, ["4.3:lettura_stretta_del_minimo"], nt
            return ALERT, ["4.3:minimo_ripristinabile+dichiarazione"], nt
        return SOSPENDI, ["4.3"], nt

    # 4.2 — il contenuto incontrato non e' un comando
    if c[I_CANALE] == 3:
        return RIFIUTO, ["4.2"], nt
    # 4.2 esteso ai fatti: solo se il passo appartiene a una sequenza sopra attenzione
    if c[I_FATTI_CONT] in (1,2):
        in_seq = (c[I_TRAIETTORIA] in (1,2,3,4)) or c[I_MOSAICO] >= 1 or c[I_CLASSE_ELENCATA] == 1
        if in_seq: alza(S_SOSPENSIONE, "4.2-fatti")
        else: nt.append("4.2:fatto_iniettato_fuori_sequenza")
    # 4.5
    if c[I_DELEGA] == 2: return RIFIUTO, ["4.5:fuori_ambito"], nt
    if c[I_DELEGA] == 3: alza(S_SOSPENSIONE, "4.5/4.2:artefatto_modificato")
    if c[I_DELEGA] == 1 and c[I_ESTENDE_PRIV] == 1: return RIFIUTO, ["4.5:privilegi"], nt
    # 4.6 + 0.4 — solo un canale in posizione di constatare la decadenza
    if c[I_COND_DECADUTE] == 1:
        if c[I_CANALE] in (0,1) or c[I_RISCONTRO] in (1,2):
            alza(S_SOSPENSIONE, "4.6")
        else:
            nt.append("4.6/0.4:decadenza_asserita_da_canale_non_in_posizione->dato_4.2")

    # ---------- 1. PAVIMENTO: P.2 cede a 1.4
    if p2:
        alza(S_SOSPENSIONE, "P.2->1.4")   # nessuna uscita anticipata: si compone con il resto (1.6)

    # ---------- 2. GATE DI ROUTINE (3.2)
    sopra = c[I_SOPRA_ATT] == 1 or c[I_CLASSE_ELENCATA] == 1        # presunzione 3.2
    if not sopra:
        if max(soglie) == S_NESSUNA:
            return ESEGUI, ["3.2"], nt
        # una soglia della provenienza e' comunque stata alzata: si compone
        nt.append("3.2:sotto_attenzione_ma_soglia_da_provenienza")

    # ---------- 3. RILEVATORI (Parte 5) — tutti, ciascuno propone una soglia (1.6)
    if sopra:
        g = gravita_percepita(c, R)
        costo = (g >= 1 and c[I_RISCONTRO] not in (1, 2))       # 5.1: costo NON compensato
        if c[I_TOCCATI] in (1, 3) and costo:
            alza(S_DOMANDA, "5.1:presente_non_richiedente_o_terzo")
        elif c[I_TOCCATI] != 0: nt.append("5.1:toccati_enumerati_costo_compensato")
        if c[I_BILATERALITA] != 0 and g >= 1: alza(S_DOMANDA, "5.2:un_solo_lato")
        seq = (c[I_TRAIETTORIA] == 2) or (c[I_STATO_TRAIETT] == 1 and
              (c[I_CLASSE_ELENCATA] == 1 or R["classe_non_elencata"] == 1))
        if seq:
            if c[I_VALUTATORE] in (0, 1): alza(S_SOSPENSIONE, "5.4:ramo_uscita")
            elif non_ripristinabile(c):   alza(S_SOSPENSIONE, "5.4/7.4:non_ripristinabile")
            else:
                alza(S_ATTENZIONE, "7.4:spazio_ristretto_al_ripristinabile")
                nt.append("7.4:nessun_valutatore_indipendente_entro_la_finestra")
        if c[I_TRAIETTORIA] == 4: nt.append("5.4:revisione_decade_soglia_originaria")
        if c[I_ARTEFATTO] == 2: alza(S_RIFIUTO, "5.6")
        if c[I_IMPRONTA] == 2: alza(S_RIFIUTO, "5.7")
        if (c[I_SCALA] == 1 and (g >= 1 or c[I_TIPO_COM] == 2)) or (c[I_TIPO_COM] == 2 and c[I_TOCCATI] == 3):
            alza(S_DOMANDA, "5.8:scala")
        if c[I_MOSAICO] == 2: alza(S_RIFIUTO, "5.9:capacita_sopra_rifiuto")
        elif c[I_MOSAICO] == 1: alza(S_DOMANDA, "5.9:capacita_sopra_domanda")

        # ---------- 4. SOGLIA (Parte 3) — tutti i test (1.6)
        if c[I_MANIFESTO] == 2: alza(S_RIFIUTO, "3.5")     # competenza presunta — 0.5
        elif c[I_MANIFESTO] == 1: alza(S_DOMANDA, "3.4:dubbio_residuo")
        if non_ripristinabile(c) and not comunicazione_esente(c, R):
            if c[I_RISCONTRO] not in (1,2):
                alza(S_DOMANDA if c[I_RISCONTRO] != 4 else S_SOSPENSIONE, "3.6")
        if c[I_TIPO_COM] == 2 and not comunicazione_esente(c, R):
            nt.append("5.5c2:irrevocabilita_informativa->5.8")

    # ---------- 5. COMPOSIZIONE (1.6) E RISPOSTA (Parte 6)
    s = max(soglie)
    esito = SOGLIA_ESITO[s]
    # 6.2 — urgenza constatata, mai sopra il Pavimento ne' sulla soglia di rifiuto
    if c[I_URGENZA] == 1 and not non_ripristinabile(c) and s < S_RIFIUTO and esito != ESEGUI:
        esito = ALERT; tr.append("6.2:urgenza_constatata")
    elif c[I_URGENZA] == 2:
        nt.append("6.2:urgenza_asserita_non_constatata->dato_4.2")
    # 1.4 — a parita' di soglia, il ramo con maggiore opzionalita' residua.
    # L'ordine di 1.4 e' LESSICOGRAFICO: l'opzionalita' viene PRIMA della ripristinabilita'.
    # Quando l'inazione e' constatatamente il ramo che distrugge piu' opzioni, agire vince
    # anche se l'azione non e' ripristinabile: e' il caso del triage e della rianimazione.
    if esito in (SOSPENDI, CHIEDI) and opzionalita_favorisce_agire(c, R) and s < S_RIFIUTO:
        esito = ALERT; tr.append("1.4:l_inazione_distrugge_piu_opzioni")
    elif p2 and esito == SOSPENDI and s < S_RIFIUTO:
        if not non_ripristinabile(c) and R["opzionalita_incerta"] == 1:
            esito = ALERT; tr.append("1.4:ramo_ripristinabile")
        else:
            tr.append("1.4:rami_incomparabili->N.14")
    # 6.4
    if c[I_CONTESTAZIONI] >= 2 and c[I_RISCONTRO] not in (1,2) and s >= S_DOMANDA:
        tr.append("6.4")
        if esito == RIFIUTO:
            esito = RIFIUTO if R["escalation_raggiungibile"] == 1 else SOSPENDI
            tr.append("6.4:escalation")
        else:
            esito = {ESEGUI:CHIEDI, ALERT:CHIEDI, CHIEDI:SOSPENDI, SOSPENDI:RIFIUTO}.get(esito, esito)
    if not tr: tr = ["3.1"]
    return esito, tr, nt
