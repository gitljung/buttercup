# Växthus Fusion – status (läs först)
Plan: PLAN.md (godkänd av vickesluring 2026-11-03, "börja där"). Körning: `./run.sh skript.py [--ro]` (_n.py + _v.py + skript), alltid via fusion_status.sh-kön.
Projekt `vaxthus`, master "Växthus - parametrar". Gammal DirectDesign-modell i gammal/ (bara facit).

## Logg
- 2026-11-03 Steg 1 v01_master.py skrivet, KÖAD (Fusion upptagen av Josper-tråden).
- 2026-11-03 Steg 1 KLAR: master sparad, 53 parametrar, värden stämmer med handräkning (BagR 3856,1, BagLangd 4095, 6 bågar). Steg 2 v02_halvbage.py KÖAD.
- 2026-11-03 Steg 2 KLAR (försök 3): Växthus - halvbåge, 15 kroppar, 30 tidslinjesteg, 0 fel, alla 10 skisser låsta, 0 krockar, remsor 2073/2091 (ytter) 1632/2394 (inner). Steg 2b v02b_flextest.py KÖAD (Bredd 4800, Nockhöjd 4000, Spetsighet 300 -> återställ). Sedan steg 3 (Båge-delmontage + Syllram).
- 2026-11-03 Steg 2b: flextest UNDERKÄNT – Derive-länken följer inte mastern via API (se v02c/v02d/v02e-loggar). Väntar på beslut från vickesluring: A) ett dokument med parametrar + interna komponenter (rekommenderat) eller B) felsöka Derive vidare. Testfil 'Växthus - derivtest' ska raderas.
- 2026-11-03 vickesluring valde A (ett dokument). v03_topp.py: raderar flerfilsförsöket, bygger 'Växthus' med parametrar + Båge-delmontage mönstrat + flextest. KÖAD.
- 2026-11-03 Steg 3 KLAR (struktur A, försök 9): dokumentet 'Växthus' sparat i projekt vaxthus. 52 parametrar i dokumentet; Båge (Halvbåge + vriden kopia) mönstrad AntalBagar × BagCC. All halvbågsgeometri i EN skiss 'Bågform' (inga projektioner). Klossmönster = cirkulärt kring axel C0 -> konstruktionspunkt (fast +y). Flextest (4800/4000/300/12 m/1000): 13 bågar, 0 fel, 0 krockar, alla skisser låsta; återställt = identiskt med före.
  Känt: vid större hus blir remsorna > SkivaL (flex: 2724/3023) – skarvantalet är fast (1 per remsa). Gamla flerfilsfiler raderade.
- NÄSTA: steg 4 = Syllram + Nock och sidoreglar (komponenter i toppen, längder = Langd-uttryck).
