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
- 2026-11-03 Beslut (vickesluring): täckning = växthusfilm + wiggle wire (låsprofil + fjädertråd). Research: Norhage 200 µm UV/antidropp (Patilux/Lirsa, 7,5/9,2/10/10,5/11,4 m bredd; 10,5 m = 374 kr/m inkl moms 2026-11-03), VEVOR 50×2 m alu-profil 32×13×1,5 + PE-belagd tråd 164,90 € (vevor.de). Norhage 'klämprofil enkel' (7036, 157 kr/m) är clips, INTE wiggle wire. Mått: ytterbåge hel 8,40 m, gavelyta 10,0 m²/st, profil ~55 lpm. Läggs in i steg 7 (komponent Låsprofil + film viks in i profilen).
- 2026-11-03 Victor: bågavstånd 1250, plywood = mest prisvärd (K20/70 15x2500x900 Byggmax 459 kr -> SkivaL 2500), börja med fästelement/spikplåtar. v04_syll_nock.py KÖAD.
- 2026-11-03 Victor OK på beslagsförslaget. v05_beslag.py (vinklar bågfot + nock mönstrade, syllbeslag) KÖAD efter v04; avbryter själv om v04 inte sparats. Öppet: gavelbågarnas yttre bågfot (långsyllen slutar 25 mm utanför bågen).
- 2026-11-03 Victor: kör a -> SyllUtstick 120 (långsyll förbi gavlarna), hörnvinkel utsida i st f spikplåt. kedja_45.sh (v04 + v05) KÖAD.
- 2026-11-03 Steg 4 + 6a KLARA (kedja_45): Växthus sparad. 9 bågar c/c 1250, Syllram (utstick 120), Nockregel, Sidoreglar, Vinklar bågfot 32, Vinklar nock 32, Syllbeslag 8 (4 hörn × insida/utsida). 350 kroppar, 0 fel, 0 krockar, alla skisser låsta. Flex (13 bågar): 0 fel/krock, beslag följer (48/48/8); återställt identiskt.
  Känt: speglade kroppar har fel namn (höger/vänster, fram/bak byter) – kosmetiskt, fixas. Nästa: steg 5 gavlar + dörrar (dörrstolpar på gavelsyllens ändar, överliggare, nockstolpe, gavelstag) + beslag där.
- 2026-11-03 Victor: kör steg 5. v06_gavlar.py (gavlar, dörrar, gavelbeslag, namnrättning) KÖAD. Gavelstag utelämnat: dörrstolparna går upp till bågen.
- 2026-11-03 Victor: kör (dörrbeslag). v06 ändrad: dörrblad i liv med stolparnas utsida. v07_dorrbeslag.py KÖAD efter v06. Stolptopp/nockstolpe: snedskruvad konstruktionsskruv (ej ritad).
- 2026-11-03 Steg 5 + 6c KLARA (398 kroppar, 0 fel/krock, flex OK). FEL hittat: bakre vänstra gavelsyllen saknades sedan steg 4 (spegling). v04 rättad för ombygge; v07b_syllfix.py KÖAD.
