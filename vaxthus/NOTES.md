# Bågväxthus – hur modellen är byggd

Byggd av Hugo i Claude (desktop). En fil, `index.html`, three.js r128 från cdnjs och typsnitten Archivo + IBM Plex Mono. Ljust och mörkt tema följer systemet.

## Geometri (meter i koden, mm i gränssnittet)
- `A` = halva bredden, `H` = nockhöjd. Standard nu **4 000 × 3 500 mm**, dörr 2 000 × 2 000, överljus 450, bågavstånd 2 000 (Hugos val, okt 2026). Originalet var 7 000 × 4 200.
- Bågen är en **cirkelbåge** med centrum under marken, förskjutet i sidled:
  - `C = (H² − A²) / 2A` → förskjutning 0,77 m
  - `R = C + A` → radie 4,27 m
  - `ARC = R·(π − atan2(H, −C))` → halvbåge 5,933 m, hel båge 11,866 m
- **Spetsighet (tillagd av Vickan):** `YC` är radiecentrums höjd. Det var 0 i originalet, alltså centrum i marknivå, och det är 0 även som standard nu. Hugos spetsiga form kommer från proportionerna (smalt och högt: 4,8 × 4,5 m ger R 5 419, båge 5 310 och 34° vid nock, med lodräta bågfötter). Bredd och nockhöjd är låsta, så när centrum sänks växer radien och bågarna möts i en spetsigare (gotisk) nock.
  - `C = (H² − A² − 2·H·YC) / 2A`, `R = √((C+A)² + YC²)`
  - Taklutning vid nock = atan(C / (H − YC)). Den gamla rundade bågen gav 10°, standard nu 21° och max (YC = −2,5) ca 30°.
  - Bågen möter marken något lutad i stället för lodrät. Reglaget "Spetsighet" går från 0 (rund) till 2,5 m.
- `ap(u, side, r)` ger punkten längs bågen (u = 0 vid marken, 1 vid nocken). `xa(y)` ger bågens x vid höjden y.
- `fit()` håller dörr och överljus under bågen. Om de inte får plats krymps först överljuset och sedan dörrhöjden, i steg om 5 cm, med 20 cm marginal.

## Stomme
| Del | Dimension | Placering |
|---|---|---|
| Syll, långsidor och gavlar | 120×120 tryckimpregnerat | Vid gavlarna avbruten för dörröppningen |
| Bågar | **Stegbåge:** två remsor plywood (12 mm, 70 mm breda, två limmade lager) med klossar 70×70 emellan | Bågavstånd `SP` (1 000 mm), antal = ceil(L/SP)+1 |
| Klossar | 70×70, 120 mm | ca var 30:e cm längs bågen |
| Nockregel | 45×145 | 13 cm under nocken |
| Sidoreglar | 34×145 | på höjden 1,9 m, en per sida |
| Dörrstolpar | 95×95 | ×4 |
| Överliggare dörr och överljus | 95×95 | |
| Nockstolpe i gavel | 95×95 | från överljuset upp till nocken |
| Gavelstag mot båge | 95×95 | vågrätt i överljusets överkant, ut till bågen |
| Dörrblad | 45×70-ram | pardörrar, 4 blad totalt |

Film: polyeten. Taket rullas ut i rader längs längden, och gavlarna har dörröppningen urklippt. Filmytan = 2·ARC·L + 2·gavelyta.

## Byggsekvens (reglaget 0–100 %)
1. Syllram 0–10 %
2. Bågar 10–52 %, en i taget längs längden
3. Nock och sidoreglar 52–64 %
4. Gavlar 64–78 %
5. Dörrar 78–87 %, svänger igen
6. Polyetenfilm 87–100 %, taket först och gavlarna sist

Varje regel har `t0` och `t1` och "växer" fram längs sin egen längd. Alla reglar ritas som en enda InstancedMesh.

## Reglage
- Längd: 10 / 12 / 14 / 16 / 18 / 20 / 30 / 40 m
- Gavelsektion (SVG): nockhöjden kan dras direkt, mellan 3,5 och 7 m och aldrig under A
- Bredd 4–12 m, dörrbredd (max 4 m), dörrhöjd, överljus, bågavstånd

## Inköpslista
- Räknar virke i löpmeter plus 10 % spill.
- Plywoodremsor: n bågar × 2 halvor × 2 skivor × 2 lager × ARC. 15 remsor om 70 mm ur en skiva 1220×2440.
- Polyetenfilm: yta plus 10 %.
- Skruv, lim, beslag och gångjärn ingår inte.
- Dimensionerna är antaganden och ska stämmas av mot snö- och vindlast.
- "Kopiera" ger tabbseparerad text för Excel och Sheets.
- "Exportera CSV" använder Claudes nedladdning (`window.claude.use('downloads')`) när sidan körs inne i Claude. Annars blir det en vanlig nedladdning via webbläsaren, med semikolon och BOM så att Excel läser åäö rätt.

## GLB-export (tillagd av Vickan)
- Knappen "Exportera 3D (GLB)". Använder GLTFExporter för three r128 från jsdelivr (`examples/js`, ingen modul).
- Exporterar alltid det **färdigbyggda** huset, oavsett var byggreglaget står, och ställer sedan tillbaka reglaget.
- Struktur: `Bagvaxthus_<B>x<L>m` → `Stomme` (en nod per regel), `Dorrar` (4 blad), `Film` (tak + 2 gavlar).
- Två material: `Tra` och `Polyetenfilm`. Enhet meter, Y uppåt. Öppnas i Blender, SketchUp (via import) och Rhino.

## STEP-export (tillagd av Vickan)
- Knappen "Exportera CAD (STEP)". Den delade skrivaren ligger i `../lib/step.js` och används även av hönshuset.
- AP214, riktiga solider (MANIFOLD_SOLID_BREP med plana ytor), mm, Z uppåt. Varje regel och kloss blir en egen solid med namn och träfärg.
- Film och glas är bara ytor, inga solider, och följer därför inte med i STEP. Ta GLB om du vill ha dem.
- Kontrollerad med OpenCascade: 547 solider, 0 ogiltiga, bbox 4 120 × 10 120 × 3 570 mm.
