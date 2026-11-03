# Belastningsberäkning – växthusets bågar (förenklad)

Skript: `belastning.py` (alla fall), `svep.py`/`svep2.py`/`svep3.py` (varianter). Kör med `~/retro_upscale/.venv/bin/python`.
Ingen ersättning för en konstruktör – men ordningen på resultaten är tydlig.

## Antaganden
- Plats: Torekov, Båstad kommun → snö sk = 1,5 kN/m², vind vb = 27 m/s (BFS 2024:6). Terräng I (kust). qp(3,5 m) = 0,99 kN/m².
- Snö (EN 1991-1-3, cylindriskt tak): jämn 0,8·sk där lutningen < 60°; osymmetrisk μ3 = 2,0 (läsida) / 1,0 (lovart), trianglar.
- Vind (EN 1991-1-4 fig 7.11, h/d = 0, f/d = 0,5 – vårt f/d = 0,85 ligger utanför diagrammet): A +0,8, B −1,2, C −0,4; cpi +0,2 / −0,3.
- Lastkombination EKS 6.10b, säkerhetsklass 2 (γd 0,91). Klimatklass 3 (fuktigt växthus): kmod 0,65 snö, 0,70 vind; γM 1,2.
- Plywood: Metsä spruce 15 mm (fm 23,1, fc 17,6, ft 10,6 MPa, E 7 034 MPa) – K20/70 antas likvärdig.
- Mellanbåge c/c 1 250. Bågen modelleras som byggd: två remsor 15×70 + klossar (stegbalk/Vierendeel), led i fot och nock.
  Skruvglidning i klossarna är inte medräknad (verkligheten blir vekare). Linjär knäckning → förstoring 1/(1−1/λ).
- Inte räknat: gavlarnas stabilisering i längsled, förankring i detalj, snöras från taket, olyckslast.

## Resultat – nuvarande båge (djup 100, remsor 15, klossar c/c ~0,5 m)
Utnyttjandegrad (≤ 1,0 = OK):
- Snö jämn: 7,5   Snö osymmetrisk: 7,1   Vind: instabil (λcr < 1)
- Orsak: mellan klossarna (≈ 0,4 m fritt) måste varje 15 mm-remsa böjas själv av tvärkraften (Vierendeel-verkan).
- Dessutom: sidoregelns fack (150 mm utan kloss) är en svag punkt.

## Varianter (utnyttjandegrad snö osymm / vind+snö / vindlyft)
- Klossar c/c 0,3 m: 2,6 / 10,5 / 8,5
- Klossar c/c 0,2 m: 2,0 / 7,7 / 6,7
- Låda (limmade sidoskivor, full samverkan), fyllt fack: 1,6 / 7,5 / 6,5
- + hanbjälke 45×120 på 2,0–2,4 m: 1,7 / 5,6 / 5,8
- Djup 200, remsa 15, låda: 0,8 / 3,7 / 3,3
- Djup 230, remsa 2×15 limmat, låda: 0,32 / 1,65 / 1,51 (med hanbjälke 1,21 / 1,35)
- Djup 330, remsa 2×15, låda: 0,25 / 1,15 / 1,08
- Djup 230, 2×15, låda, c/c 0,9 m: 0,23 / 1,19 / 1,09
- Djup 330, 2×15, låda, c/c 0,9 m: 0,18 / 0,82 / 0,78 ✓
- Inspänd fot / stel nock ändrar lite (±10 %).

## Övrigt
- Fotreaktioner (dim., per båge): tryck upp till 3,4 kN, lyft upp till 3,1 kN, horisontellt upp till 3,8 kN.
  → förankring: ca en markskruv per bågfot (≈ 20 st), syllen skruvad till markskruven.
- Längsled: vind mot gaveln ≈ 11 kN (kar.) per gavel → vindkryss behövs i ändfacken (finns inte i modellen).
- Bruksgräns (kar.): snö osymm ≈ 55 mm, vind ≈ 370 mm deformation (nuvarande båge).
- Med växthusstandarden EN 13031-1 (kortare livslängd, lägre klass) kan vind- och snölast sänkas ca 30–40 % – vind fäller ändå nuvarande båge med stor marginal.

## Svep klossar (stegbåge utan sidoskivor, fyllt sidoregelfack), nock 3,5 m – svep_klossar.py
Utnyttjande snö / vind / lyft (max):
- 160 djup, 15 remsa, klossar c/c 150 + hanbjälke: 0,85 / 3,11 / 3,48
- 230 djup, 2×15 remsa, c/c 300: 0,53 / 1,86 / 1,76 (+ hanbjälke 0,47 / 1,39 / 1,60)
- 230 djup, 2×15, c/c 200 (20 klossar/halvbåge): 0,33 / 1,65 / 1,50 (+ hanbjälke 0,35 / 1,21 / 1,35)
- 230 djup, 2×15, c/c 150 (25/halvbåge): 0,31 / 1,61 / 1,47 (+ hanbjälke 0,31 / 1,17 / 1,33)
- Slutsats: c/c 200 är optimum – tätare ger nästan inget. Lika bra som limmad låda (1,21/1,35).
- Nock 2,8 / 2,4 m: resultaten hoppar (numeriskt instabil knäckningslösning) – ej redovisade. Film 4,5 m låser nocken till ≈ 3,5 m ändå.
