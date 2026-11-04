# Reelanalys: crowd-runner shooter → Svinjakten på Blommeröd

Källa: Instagram-reel `https://instagram.com/p/DdWhcquACBO/`  
Lokal kopia: `/Users/hiro/Downloads/ig_DdWhcquACBO/post.mp4`  
Längd: ca 90 sekunder

## Kort sammanfattning

Reelen visar en mobilspelsreklam i genren **crowd-runner shooter**: en grupp blå skyttar rör sig framåt på en smal bana och skjuter automatiskt mot en ström av röda fiender. Spelaren styr gruppen i sidled och väljer mellan att skjuta på portar som ger fler soldater eller på vapenkort som ger starkare eldkraft. Mot slutet kommer större fiender/bossar med hälsostaplar. Reklamen slutar med förlust/”FAIL”-känsla och en uppmaning att spela.

Det viktiga är inte spelet “Total Battle” i sig, utan **reklamens mekanik och känsla**: snabb, dumrolig, nästan-frustrerande, tydliga siffror som tickar ner och valet mellan fler gubbar eller bättre vapen.

## Vad som syns i reelen

### 1. Bana och perspektiv

- Vertikalt mobilformat.
- En lång, smal bro/bana i perspektiv, sedd snett uppifrån och bakifrån.
- Spelarens grupp står längst ner och rör sig framåt.
- Fiender kommer uppifrån och ner mot spelaren.
- Allt är byggt för att förstås på under en sekund.

### 2. Spelarens grupp

- Gruppen består av många små blå figurer.
- De skjuter automatiskt rakt fram.
- Spelaren verkar bara styra vänster/höger.
- När gruppen blir större ökar eldkraften visuellt och mekaniskt.

### 3. Portar med plus/multiplikator

- Längs banan finns tydliga portar/skyltar med siffror.
- Exempel: `+1`, `+2`, `+3`, ibland större bonusar som `+33`.
- När gruppen går genom eller skjuter porten ökar antalet soldater.
- Färgerna hjälper spelaren läsa värdet snabbt:
  - blå/grön/lila/gul = ökande belöning.

### 4. Vapenkort och sidoval

- På ena sidan finns kort med vapen eller hjältar.
- Korten har stora siffror, t.ex. `1585`.
- Siffran fungerar som en hälsa/tröskel: skjut ner till noll för att få vapnet.
- Det skapar ett direkt val:
  - gå mot fler soldater,
  - eller offra tid/position för att låsa upp bättre eldkraft.

### 5. Fiender och bossar

- Många små röda fiender kommer i vågor.
- Större fiender/bossar har hälsostapel.
- Bossens liv tickar ner när gruppen skjuter.
- Om bossen når fram förlorar spelaren.

### 6. Fail-loop

- Reelen visar mycket “nästan klarade det”.
- Det slutar med ord som `FAIL` eller `DEFEAT`.
- Den psykologiska kroken är: “jag hade klarat det om jag bara valt andra porten”.

## Speltanken bakom reelen

Reelen bygger på tre enkla dopamin-krokar:

### 1. Direkt läsbarhet

Man fattar omedelbart:

- blått = jag,
- rött = fiende,
- plus = fler,
- siffra som minskar = framsteg,
- stor fiende = boss.

Ingen tutorial behövs.

### 2. Mikroval hela tiden

Spelaren får små beslut varannan sekund:

- vänster eller höger,
- fler gubbar eller bättre vapen,
- säkert +1 eller riskera vapenkortet,
- sikta på bossen eller rensa småfiender.

Valen är enkla men känns viktiga.

### 3. Nästan-förlust

Spelet är designat för att ofta kännas förlorat med liten marginal. Det gör att man vill testa igen.

Det är samma känsla som:

> “Om jag bara hade hunnit ta +3-porten hade jag fällt bossen.”

## Översättning till Blommeröd/Svinjakten

Vi gör inte en kopia av Total Battle. Vi använder dess **reklamlogik** och bygger en egen Buttercup/Blommeröd-version.

### Rollfigurer

Starten ska vara narrativ:

1. **Peter** börjar ensam.
2. Vid första `+1` ansluter **Hugo**.
3. Nästa `+1` ger **Carl**.
4. Nästa `+1` ger **Jocke**.
5. Nästa `+1` ger **Borka**.
6. Efter det blir `+1` extra kopior/backup.

Det gör att spelet inte bara är “antal gubbar”, utan en liten berättelse: kompisgänget samlas för svinjakt.

### Fiender

- Små vildsvin ersätter de röda fienderna.
- De kommer i ström uppifrån.
- De ska vara lite gulliga men aggressiva.
- Ibland kommer ett **MEGASVIN** som boss.

### Portar

- `+1` = en kompis ansluter.
- `×2` = dubblar gänget.
- På sikt kan portar få mer Blommeröd-ton:
  - `+1 JÄGARE`
  - `+5 DREV`
  - `×2 MOD`
  - `GARIBALDI`

### Vapenkort

Vapenkorten kan översättas till eldkraft:

- `STUDSARE` = mer skada.
- `GARIBALDI` = större eldkraft / eldstads-kanon-känsla.
- Senare: `SPETTET`, `KARL-JOHAN`, `NATTJAKT`, `YAMAY BOOST` etc.

### Miljö

Blommeröd-versionen ska kännas som:

- gård/stall/grusväg,
- Buttercup-färger,
- varm och lite absurd jaktfest,
- vildsvin + eldstad + kompisgäng,
- inte realistiskt våld utan slapstick/arkad.

## Nuvarande Svinjakten-prototyp

Publicerad olistad på:

https://www.buttercup.nu/svinjakt/

### Implementerat

- Startar med **1 skytt**.
- `+1` lägger till kompisarna i ordning:
  1. Peter
  2. Hugo
  3. Carl
  4. Jocke
  5. Borka
- Figurerna är större än första versionen.
- Vildsvin kommer i vågor.
- Megasvin finns som boss.
- Portar `+1` och `×2`.
- Vapenkort `STUDSARE` / `GARIBALDI` ger mer eldkraft.
- Mobilstyrning: dra i sidled.
- Olistad/noindex.

## Vad som kan förbättras härnäst

### 1. Tydligare “kompis ansluter”-moment

När `+1` tas bör spelet visa en liten skylt:

- `HUGO ANSLUTER!`
- `CARL KOMMER!`
- `JOCKE TAR MED FÖRKLÄDET!`
- `BORKA ÄR HÄR!`

Det gör +1-belöningen roligare än bara en ny sprite.

### 2. Mer Blommeröd-bakgrund

Byt den generiska banan till:

- grusväg mot stallet,
- mörk korrugerad plåt,
- eldstaden/scenen i nederkant,
- ljusslingor och gårdskänsla.

### 3. Bättre boss-loop

Megasvinet bör:

- få stor varningsskylt: `MEGASVIN!`
- ha tydlig hälsostapel,
- vara mycket större,
- ge extra poäng/”på spettet”-animation när det fälls.

### 4. Ljud och feedback

- små “pang” för skott,
- grymt från vildsvin,
- publikjubel när megasvinet fälls,
- låg bas/dundring när bossen kommer.

### 5. Fail som känns kul

I stället för bara “Svinet vann”:

- `SVINEN TOG SCENEN`
- `BORKA SKYLLER PÅ VINDEN`
- `HUGO SA JU +1`

## Kärnan att behålla

Det viktiga från reelen är:

1. Börja enkelt.
2. Öka gruppen visuellt.
3. Siffror ska ticka ner.
4. Valet mellan fler kompisar och mer eldkraft ska kännas stressigt.
5. Megasvinet ska alltid kännas “nästan möjligt”.

Det är exakt den känslan Svinjakten ska åt: **en löjligt tydlig, snabb, mobilvänlig jaktfest där Blommeröd-gänget blir fler och fler tills megasvinet faller.**
