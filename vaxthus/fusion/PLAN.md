# Växthus i Fusion – plan för parametrisk modell (förslag 2026-11-03, väntar på OK)

Mål (vickesluring): samma CAD-metodik som Yamay (master → detaljfiler → delmontage → topp), och **en människa ska lätt kunna ändra modellen**.
Gamla `bygg_vaxthus.py` (DirectDesign + TBRep-lådor) är INTE redigerbar → ersätts, används bara som facit för geometri.

## Regler
- Parametric design, ingen DirectDesign/TBRep. Allt syns i tidslinjen.
- Masterfil `Växthus - parametrar`: alla mått som namngivna favoritparametrar med kommentar (svenska). Härledda värden (bågradie, antal bågar, båglängd) som uttryck, så de syns och följer med.
- Inga siffror i skisser/extruderingar: bara parametrar/uttryck. Fullt låsta skisser.
- Namngivna skisser, features, kroppar, komponenter ("Syll långsida", "Skarv 1 ytter" …).
- Montage med joints mot parametrar/geometri (inte as-built), så att Längd/Bredd flyttar gavlar och syll.
- Bågarna i toppen = komponentmönster med antal `ceil(Langd / Bagavstand) + 1` och avstånd ur parametrarna.
- Acceptanstest ("flextest"): ändra Bredd 4000→4800, Längd 10→12 m, Bågavstånd 2000→1000, Nockhöjd 3500→4000 → 0 tidslinjefel, 0 krockar, rimlig geometri. Ändra tillbaka.

## Struktur
```
Växthus (topp)
├─ Syllram                 syll långsida ×2, syll gavel (dörrdelad) ×4, hörnbeslag
├─ Båge  ×N (mönster)      halvbåge ×2 (speglad): ytterremsa, innerremsa (skarvade), klossar, skarvklossar, laskar, ändkloss + bågfotsbeslag
├─ Nock och sidoreglar     nockregel, sidoregel ×2, vinklar
├─ Gavel ×2 (fram/bak)     dörrstolpar, överliggare, överljus, nockstolpe, gavelstag, beslag
│   └─ Dörr ×2 per gavel   aktivt/passivt blad (ram 45×70), T-gångjärn, handtag/överfall, kantreglar
└─ Film                    tak, gavlar (ytor)
```

## Steg (skärmdump i tråden efter varje)
1. Projekt `vaxthus` + master (alla parametrar, även de för senare steg).
2. Halvbåge (svårast): bågband ur A/H/YC, klossar som mönster längs båge, skarvplan (max 2 440) med förskjutna skarvar ytter/inner. Flextest på delen.
3. Båge-delmontage + Syllram.
4. Nock och sidoreglar + toppen med bågmönster.
5. Gavel + dörrar.
6. Beslag (platshållare → köpdelar från leverantörs-STEP).
7. Film.
8. Flextest på hela modellen, krockkoll, bilder, STEP, inköpslista ur Fusion mot webbens lista.
