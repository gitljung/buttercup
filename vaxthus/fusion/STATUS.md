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
- 2026-11-03 Victor: ja, byt till Wiberger-köpdelar (GJ60 A2 100x100 nativt parametrisk, GN425 A2 200, EL2030-100, EL1035-200 + BPG-6 som STEP). v08a_sond.py (läsande import) KÖAD efter syllfix; placering v08b skrivs efter sonden.
- 2026-11-03 Syllfix KLAR: 4 gavelsyllar, 399 kroppar, 0 fel/krock, flex OK, sparad.
- 2026-11-03 Sond klar (GN425: fötter y=0, +y 43, långt längs z; EL2030: fäste y=0 +y, längs x; EL1035: fäste y=0, en del till y -0,8 -> +1 mm). v08b_kopdelar.py KÖAD.
- 2026-11-03 v08b försök 1 FEL: exec av v03 skrev över K (saknade ext). Rättat: kontroll tas från eget namnrum. Försök 2 KÖAD.
- 2026-11-03 v08b försök 2: allt byggt, 0 krock, men STEP-importens tidslinjegrupper Group1-3 har healthState!=0 (tomt meddelande) -> sparade ej. Försök 3: grupperna löses upp.
- 2026-11-03 Steg 6d KLAR (försök 3): Wiberger-köpdelar. 421 kroppar, 0 fel/krock, flex OK (köpdelar ej omplacerade), sparad. Importgrupper (healthState 5) upplösta.
- 2026-11-03 Victor: fortsätt + börja räkna skruv. v09_lasprofil.py (låsprofiler gavelbåge/långsida/gavelsyll/dörrkarm + antal-JSON för skruvlista) KÖAD. Film ej som kropp (räknas).
- 2026-11-03 v09 försök 1: geometri OK (alla skisser låsta), FEL i loggningen (enhetslösa parametrar via evaluateExpression mm). Rättat, försök 2 KÖAD.
- 2026-11-03 v09 försök 2: 4 krockar gavelbågsprofil mot ytterlask. Ändrat: gavelbågens profil på bågens gavelsida (y=-BagB/2), yttre kant, från SyllH+VinkelA. Försök 3 KÖAD.
- 2026-11-03 Steg 7a KLAR (försök 3): Låsprofiler 16 st, 53,0 m (gavelbåge 4x4086 på gavelsidan, långsida 2x10310, dörrstolpe 4x2095, överliggare 2x2126, gavelsyll 4x848). 437 kroppar, 0 fel/krock, flex OK, sparad. skruvlista.py -> SKRUVLISTA.md (ur v09_antal.json).
- 2026-11-03 Victor: belastningsberäkning. berakning/ (FEM stegbåge, EKS/EN1991, Båstad sk1,5 vb27): nuvarande båge underkänd (snö ~7x, vind instabil). Varianter i BERAKNING.md. Väntar beslut.
- 2026-11-03 Hugo: film 4,5 m bred -> en våd per sida (halvbåge ytter 4,20 m nu / 4,31 m vid 230 djup) + plåt i nocken. Låsprofil längs nocken per sida under plåten (ej ritat än).
- 2026-11-03 Victor: filmbredden bestämmer nockhöjd (4,5 m -> ≈3,5 m). Svep klossar: 230 djup 2x15, klossar c/c 200 + hanbjälke = 0,35/1,21/1,35 (Eurocode 50 år), ≈ OK med EN 13031-1. Väntar beslut.
- 2026-11-03 Plats: Blommeröd vid Ringsjön (Höör: sk 1,5, vb 27 – samma som antaget). Plywood: konstruktionsplywood K20/70 (Moelven, Byggmax, 12x2500x1200 429 kr) sågas till remsor; limklass ej verifierad. Victor frågade om kanalplast (svar givet, ej beslut). Victor: behöver inte räkna om.
- 2026-11-03 Victor: skiss alt 1 stålsidoplåtar 3 mm (zon 0,8–3,0 m, 2x220x2232, 11,4 kg/st, 36 st ≈ 410 kg, M10 c/c150 540 st) -> berakning/skiss_sidoplat.png. Ej beräknat.
- 2026-11-03 Victor: bara raka sågsnitt. svep_remsor: 2x12 lameller, bredd 95, djup 200, c/c 1250 -> 0,37/0,71/0,79 vid 30 m/s (Eurocode ≈1,4). v10_bagdim.py (bara parametrar) KÖAD.
- 2026-11-03 Hugo: klossar ~120 långa, ~10 st per halvbåge. Räknat (30 m/s, c/c 1250, raka klossar c/c ~410): 2x12/200 → 1,23 (UNDERKÄND), 2x12/250 → 1,19, 3x12/200 → 0,64 OK, 3x12/250 → 0,58. Förslag: 3x12 lameller, djup 200, 10 klossar. Fackverkssvep avbrutet (diagonaler: flänsknäckning, krångliga förband).
- 2026-11-03 Victor: vind 20 m/s, bågdjup ~100. Svep klart (svep_20ms).
- 2026-11-03 Victor: B. 3x12 lameller, bredd 95, KlossH 2xLamellT (djup 96), KlossCCmax 450 (11 klossar/halva), sidoregel 22x95. Beräknat 20 m/s: 0,75/0,66/0,67. v10b_bagB.py KÖAD.
- 2026-11-03 Steg 10b KLAR: 473 kroppar, 0 fel/krock, flex OK (667, 13 bågar), återställt identiskt. Fläns ritas som en kropp 36 mm (lameller ej separata).
- 2026-11-03 Victor: rita klart allt (sover). Hanbjälke ej (20 m/s utan: 0,87). v11_nock.py (nockprofil + nockplåt + antal + STEP) KÖAD.
- 2026-11-03 v11 försök 1 FEL: combine av speglad nockplåt (invalid argument). Rättat: båda halvorna i samma skiss, ett extrude. Försök 2 KÖAD.
- 2026-11-03 Steg 11 KLAR (försök 2): nockprofil + nockplåt 300×0,6. 475 kroppar, 0 fel/krock, flex OK (669), återställt identiskt, sparad. STEP: fusion/export/Vaxthus.step (2,3 MB). v11c_lista.py (läsande kroppsdump) KÖAD.
