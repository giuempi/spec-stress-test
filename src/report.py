# -*- coding: utf-8 -*-
"""Prints every table quoted in README.md and findings/FINDINGS.md, from the raw results.
If a number here disagrees with the documents, the documents are wrong."""
import json, os, signal
try: signal.signal(signal.SIGPIPE, signal.SIG_DFL)   # clean output when piped into head/less
except (AttributeError, ValueError): pass
HERE = os.path.dirname(os.path.abspath(__file__))
def L(n):
    for p in (os.path.join(HERE, "..", "findings", "results", n), os.path.join(HERE, n)):
        if os.path.exists(p): return json.load(open(p))
    raise SystemExit("missing %s — run ./run_all.sh first" % n)
def rule(t): print("\n" + t + "\n" + "-"*len(t))

a = L("cfr_a.json")["risultati"]; f = a["falso_allarme"]
b = L("cfr_b.json")["risultati"]["operatori"]
c = L("cfr_c.json")["risultati"]; d = L("cfr_d.json")["risultati"]["ambiguita"]
e = L("cfr_e.json")["risultati"]

rule("1. HEADLINE — v3 vs v4 on identical cases")
print("  %-54s %10s %10s" % ("measure", "v3", "v4"))
for n, x, y, p in [
 ("Harmful commands executed (realistic mixture)", a["realistica"]["v3"]["tasso_elusione_pct"], a["realistica"]["v4"]["tasso_elusione_pct"], 2),
 ("Harmful commands executed (threshold nucleus, full enum)", e["nucleo_soglia"]["v3"]["tasso_elusione_pct"], e["nucleo_soglia"]["v4"]["tasso_elusione_pct"], 2),
 ("False alarms on legitimate requests", f["v3"]["tasso_non_esecuzione_pct"], f["v4"]["tasso_non_esecuzione_pct"], 2),
 ("Cases with no unique outcome across faithful readings", d["v3"]["non_unico_pct"], d["v4"]["non_unico_pct"], 2),
 ("Cases swinging >= 2 permissiveness levels", d["v3"]["salto_ge2_pct"], d["v4"]["salto_ge2_pct"], 2),
 ("Cases undecidable under at least one reading", d["v3"]["indecidibile_pct"], d["v4"]["indecidibile_pct"], 2),
 ("Non-monotone pairs (more severity -> more permissive)", c["monotonia"]["v3"]["pct"], c["monotonia"]["v4"]["pct"], 3),
]: print("  %-54s %*.*f%% %*.*f%%" % (n, 9, p, x, 9, p, y))
print("  %-54s %10d %10d" % ("Ambiguous points in the text", d["v3"]["n_risoluzioni"], d["v4"]["n_risoluzioni"]))
print("  %-54s %10d %10d" % ("Floor violations with a permissive outcome", a["realistica"]["v3"]["pav_violato_permissivo"], a["realistica"]["v4"]["pav_violato_permissivo"]))

rule("2. RULE INERTNESS — how often a detector's value changes the outcome")
i3, i4 = c["inerzia"]["v3"]["rilevatori"], c["inerzia"]["v4"]["rilevatori"]
NAME = {"5.1":"5.1 who is touched","5.2":"5.2 bilateral concreteness","5.8":"5.8 scale","5.9":"5.9 mosaic",
        "5.3/5.4":"5.3/5.4 trajectory","5.5":"5.5 reversibility","5.6":"5.6 artefacts","5.7":"5.7 footprint"}
for k in sorted(i3): print("  %-32s %8.3f%% %8.3f%%" % (NAME[k], i3[k], i4[k]))
print("  %-32s %8.3f%% %8.3f%%" % ("hierarchy level (4.1/4.4/4.8)",
      c["inerzia"]["v3"]["livello_cambia_esito_pct"], c["inerzia"]["v4"]["livello_cambia_esito_pct"]))

rule("3. ELUSION OPERATORS — make it execute what it should not")
for base in ("pavimento","soglia"):
    print("  base: blocked by the %s" % ("Floor" if base=="pavimento" else "Threshold"))
    v3, v4 = b[base]["v3"]["elusione"], b[base]["v4"]["elusione"]
    for k in sorted(v3, key=lambda k: -max(v3[k], v4[k])):
        if v3[k] > 0.05 or v4[k] > 0.05: print("    %-26s %7.1f%% -> %7.1f%%" % (k, v3[k], v4[k]))

rule("4. PARALYSIS OPERATORS — stop what should have been done")
print("  'pure' = any legitimate request stopped. 'harmful' = stopped when the delay is verifiably")
print("  irreversible. v4 deliberately does not reduce the first: anyone must be able to stop the agent.")
v3, v4 = b["soglia"]["v3"], b["soglia"]["v4"]
print("  %-26s %20s %20s" % ("", "pure block", "harmful block"))
for k in sorted(v3["paralisi"], key=lambda k: -v3["paralisi_dannosa"][k]):
    print("    %-24s %8.1f%% ->%6.1f%% %9.1f%% ->%6.1f%%" % (k, v3["paralisi"][k], v4["paralisi"][k],
          v3["paralisi_dannosa"][k], v4["paralisi_dannosa"][k]))

rule("5. LEGITIMATE SCENARIOS — named cases the spec exists to allow")
EN = {"triage_risorse_scarse":"triage / scarce-resource allocation","congelamento_conto_sotto_attacco":"freezing an account under attack",
 "rianimazione_su_incosciente":"resuscitating an unconscious person","informazione_medica_ad_adulto":"medical information to an adult who asks",
 "invio_email_di_lavoro":"sending a work email","script_di_pulizia_con_vincoli":"cleanup script with 5.6 constraints",
 "moderazione_su_condotta":"moderation based on observable conduct","prognosi_attuariale_su_evento":"actuarial prognosis about an event",
 "rifiuto_di_azione_dannosa":"refusing a harmful action","avviso_urgente_al_pubblico":"urgent public warning",
 "correzione_di_errore_in_corso":"correcting an error in progress","avvertimento_del_secondo_pilota":"the first officer's warning (6.2's own example)",
 "notifica_dovuta_dopo_blocco":"the notification P.1(b) requires after a block"}
ok3 = ok4 = 0
for k, v in f["scenari"].items():
    ok3 += v["v3"].startswith("ESEGUI"); ok4 += v["v4"].startswith("ESEGUI")
    print("    %-46s %-13s %-13s" % (EN.get(k,k), v["v3"], v["v4"]))
print("    %-46s %-13s %-13s" % ("EXECUTED, of 13", ok3, ok4))
print("\n  ESEGUI = execute | ESEGUI+ALERT = execute with contextual challenge | CHIEDI = ask")
print("  SOSPENDI = suspend | RIFIUTO = refuse")

rule("6. EVALUATION VOLUME")
tot = sum(L(n).get("valutazioni",0) for n in ("cfr_a.json","cfr_b.json","cfr_c.json","cfr_d.json","cfr_e.json"))
print("  v3-vs-v4 comparison: %s decision evaluations" % f"{tot:,}")
print("  v3 stand-alone stress test (src/esegui.py): 194,502,912")
