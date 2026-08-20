# -*- coding: utf-8 -*-
"""Protocollo v3 sullo spazio dei casi comune: identico al modello gia' misurato,
i quattro predicati introdotti dalla v4 non sono letti (il suo esito non ne dipende)."""
from comune import *
RISOLUZIONI = ["p2_esito","gate_prima_pavimento","arresto_ogni_canale","p2_batte_arresto",
 "riscontro_esente","stato_traiettoria","sopra_rifiuto","urgenza_asserita","p7_su_rifiuto",
 "ecc_p1b_stretta","urgenza_scavalca","prossimita_esito"]
NR=len(RISOLUZIONI); R_BASE={r:0 for r in RISOLUZIONI}
def r_da_bit(m): return {r:(m>>i)&1 for i,r in enumerate(RISOLUZIONI)}

def pavimento(c,R):
    v=[]
    if c[I_DANNO]==2 and c[I_CONSENSO]==0:
        e=c[I_ECC_P1]
        if e==0: v.append("P.1")
        elif e==1: v.append("P.2")
        elif e==2:
            if ((c[I_PROT_COMPL]==1) or (c[I_REVERS]!=0)) and R["ecc_p1b_stretta"]==0: v.append("P.1")
    if c[I_P3_CLASS]==1: v.append("P.3")
    if c[I_P4_METRICA]==2: v.append("P.4")
    elif c[I_P4_METRICA]==1 and c[I_REVERS]!=0: v.append("P.4")
    if c[I_P5_DISSENSO]==1: v.append("P.5")
    if c[I_P6_INGANNO]==2: v.append("P.6")
    if c[I_P7_ATTO]==1: v.append("P.7")
    elif c[I_P7_ATTO]==2 and R["p7_su_rifiuto"]==1 and c[I_CANALE] in (0,1): v.append("P.7")
    if c[I_P8_REGISTRO]==1: v.append("P.8")
    return v

def decidi(c,R=R_BASE):
    tr=[];nt=[]
    if c[I_LIV_ASSERITO]==1: nt.append("4.1:anomalia_segnalata")
    if c[I_CANALE]==4: nt.append("4.4:livello_minimo")
    if c[I_ARRESTO]==1:
        if (R["arresto_ogni_canale"]==0) or (c[I_CANALE]!=3):
            inaz=(c[I_URGENZA]==1)
            if R["p2_batte_arresto"]==1 and inaz: nt.append("4.3/P.2:conflitto")
            else:
                if inaz: nt.append("4.3:sospende_benche_l_inazione_sia_irreversibile")
                return SOSPENDI,["4.3"],nt
    if c[I_CANALE]==3: return RIFIUTO,["4.2"],nt
    if c[I_FATTI_CONT]==1: return SOSPENDI,["4.2-fatti"],nt
    if c[I_FATTI_CONT]==2: nt.append("4.2:fatti_iniettati_passo_non_distruttivo_NON_COPERTO")
    if c[I_DELEGA]==2: return RIFIUTO,["4.5:fuori_ambito"],nt
    if c[I_DELEGA]==3: return SOSPENDI,["4.5/4.2:artefatto_modificato"],nt
    if c[I_DELEGA]==1 and c[I_ESTENDE_PRIV]==1: return RIFIUTO,["4.5:privilegi"],nt
    if c[I_COND_DECADUTE]==1: return SOSPENDI,["4.6"],nt
    if R["gate_prima_pavimento"]==1 and c[I_SOPRA_ATT]==0:
        return ESEGUI,["3.2"],nt+["3.2_scavalca_il_pavimento"]
    pav=pavimento(c,R)
    if pav:
        if "P.2" in pav and len(pav)==1:
            if R["p2_esito"]==0: return SOSPENDI,["P.2"],nt
            return (ESEGUI if c[I_REVERS]==0 else ALERT),["P.2"],nt+["P.2:esito_non_prescritto"]
        return RIFIUTO,pav,nt
    if c[I_SOPRA_ATT]==0: return ESEGUI,["3.2"],nt
    if c[I_TOCCATI]!=0: nt.append("5.1:toccati_enumerati_nessun_esito")
    if c[I_BILATERALITA]!=0: nt.append("5.2:un_solo_lato_nessun_esito")
    if c[I_SCALA]==1: nt.append("5.8:scala_nessun_esito")
    if c[I_MOSAICO]>=1: nt.append("5.9:capacita_emergente_nessun_esito")
    irrev=(c[I_REVERS]!=0)
    if c[I_TRAIETTORIA]==4:
        if R["prossimita_esito"]==0: return RIFIUTO,["5.4:revisione_per_prossimita"],nt
        nt.append("5.4:esito_del_comando_non_prescritto")
    if c[I_TRAIETTORIA]==2:
        if R["stato_traiettoria"]==0:
            if c[I_VALUTATORE] in (0,1): return SOSPENDI,["5.4:ramo_uscita"],nt
            if not irrev: return ESEGUI,["5.4","7.4:default_reversibile"],nt
            return SOSPENDI,["5.4","7.4"],nt
        nt.append("5.3/5.4:traiettoria_non_osservabile")
    if c[I_ARTEFATTO]==2: return RIFIUTO,["5.6"],nt
    if c[I_IMPRONTA]==2: return RIFIUTO,["5.7"],nt
    manifesto = c[I_MANIFESTO] if c[I_COMPETENZA]==0 else min(c[I_MANIFESTO],1)
    if c[I_COMPETENZA]==1 and c[I_MANIFESTO]==2: nt.append("9.1:manifesto_mascherato")
    esito,traccia=None,[]
    if manifesto==2:
        esito,traccia=RIFIUTO,["3.5"]
        if R["urgenza_scavalca"]==0: return esito,traccia,nt
    elif irrev:
        if R["riscontro_esente"]==1: return INDECIDIBILE,["3.6/5.5:regressione"],nt
        rr=c[I_RISCONTRO]
        if rr in (1,2): esito,traccia=ESEGUI,["3.6:riscontro_verificato"]
        elif rr==4: esito,traccia=SOSPENDI,["6.3:nessun_canale"]
        else:
            if rr==3: nt.append("6.3:riscontro_dalla_fonte_non_vale")
            esito,traccia=CHIEDI,["3.6","6.3"]
    elif manifesto==1: esito,traccia=CHIEDI,["3.4:dubbio_residuo"]
    else: esito,traccia=ESEGUI,["3.1"]
    urg=(c[I_URGENZA]==1) or (R["urgenza_asserita"]==1 and c[I_URGENZA]==2)
    if urg and c[I_REVERS]==0 and esito!=ESEGUI:
        traccia=traccia+["6.2"]
        if esito==RIFIUTO: nt.append("6.2:urgenza_scavalca_il_rifiuto")
        esito=ALERT
    if c[I_CONTESTAZIONI]>=2 and c[I_RISCONTRO] not in (1,2):
        traccia=traccia+["6.4"]
        if esito==RIFIUTO:
            if R["sopra_rifiuto"]==1: return INDECIDIBILE,traccia+["6.4:nessun_livello"],nt
        else:
            esito={ESEGUI:CHIEDI,ALERT:CHIEDI,CHIEDI:SOSPENDI,SOSPENDI:RIFIUTO}.get(esito,esito)
    return esito,traccia,nt
