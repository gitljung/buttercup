# Bågväxthus – hur modellen är byggd

Byggd av Hugo i Claude (desktop). En fil, `index.html`, three.js r128 från cdnjs och typsnitten Archivo + IBM Plex Mono. Ljust och mörkt tema följer systemet.

## Geometri (meter i koden, mm i gränssnittet)
- `A` = halva bredden (3,5 → 7 000 mm), `H` = nockhöjd (4,2).
- Bågen är en **cirkelbåge** med centrum under marken, förskjutet i sidled:
  - `C = (H² − A²) / 2A` → förskjutning 0,77 m
  - `R = C + A` → radie 4,27 m
  - `ARC = R·(π − atan2(H, −C))` → halvbåge 5,933 m, hel båge 11,866 m
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
- "Exportera CSV" använder `window.claude.use('downloads')`, som bara finns inne i Claude. På en vanlig webbsida är knappen dold.
