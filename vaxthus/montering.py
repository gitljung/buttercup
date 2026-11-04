#!/usr/bin/env python3
"""Enkel monteringsanvisning + inköpslista (utan gångjärn och handtag) -> MONTERINGSANVISNING.pdf"""
import json, os, subprocess
V = os.path.expanduser('~/code/buttercup/vaxthus')
B = V + '/fusion/bilder/'; K = V + '/berakning/'
def H(t, l=1): return {'type': 'heading', 'text': t, 'level': l}
def Pp(t): return {'type': 'paragraph', 'text': t}
def I(p, w=480): return {'type': 'image', 'path': p, 'width': w}
def T(rows): return {'type': 'table', 'rows': rows, 'header': True}
def steg(lista): return Pp('<br/>'.join(f'<b>{i + 1}.</b> {s}' for i, s in enumerate(lista)))
E = [
 H('Växthus 4 × 10 m – monteringsanvisning'),
 Pp('Bågväxthus i plywood och regel (som Norhage: fläns 1 × 15 × 95, klossar regel 45×95), 9 bågar c/c 1250, nock 3,5 m. Film 4,5 m med wiggle wire. '
    'Mått och delar enligt Fusion-modellen "Växthus" och ritningen <i>ritning_bage.pdf</i> (blad 1–3). '
    'Ingen ny hållfasthetsberäkning för den här bågen.'),
 I(B + 'v14_iso.png', 470),
 H('Verktyg', 2),
 Pp('Cirkelsåg med anslag (eller spårsåg med skena), kapsåg, skruvdragare + slagskruvdragare, borr Ø11 (lång), '
    'måttband, vinkelhake, vattenpass/laser, snöre, tvingar, handskar. Limning vid minst 15 °C.'),
 H('1. Såga remsor, laskar och klossar', 2),
 steg(['Såga plywood 15 × 2500 × 1200 i remsor 95 mm (12 per skiva), se ritning blad 2.',
       'Kapa flänsbitarna enligt kapplistan: 4 bitar per halvbåge (innerfläns 1747 + 2350, ytterfläns 2005 + 2188, med 25 mm övermått).',
       'Kapa 2 skarvlaskar 15 × 95 × 400 per halvbåge, gärna ur spillet.',
       'Kapa klossar av regel 45×95: 15 st à 130 och 1 fotkloss 300 per halvbåge (blad 3).',
       'Såga 16 nocklaskar i 15 mm plywood (sexhörning, raka snitt, blad 3). Gör en mall av den första.']),
 H('2. Bygg halvbågarna (18 st)', 2),
 steg(['Lägg upp bågens innerradie R 3819 i full skala (böjmall eller uppritad båge på golvet).',
       'Märk klossarnas lägen längs flänsen (tabell blad 1, mätt längs ytterkanten från foten).',
       'Böj innerflänsens två bitar mot mallen, skarven mitt på nedre fackklossen (kloss 7).',
       'Lim + 2 skruv 5×60 genom innerflänsen i varje kloss. Böj ytterflänsen runt klossarna, skarven mitt på övre fackklossen (kloss 8), lim + 2 skruv 5×60 per kloss.',
       'Skarvlaskar: innerflänsens på insidan, ytterflänsens på utsidan, PU-lim + 8 skruv 4,5×25.',
       'Kapa foten vågrätt och nocken lodrätt. Märk halvbågen H1–H18.']),
 I(K + 'ritning_bage_1.png', 480),
 H('3. Grund och syll', 2),
 steg(['Mät ut 4000 × 10000, kontrollera diagonalerna. Skruva ner 22 markskruvar (en per bågfot + 4 vid dörrstolparna).',
       'Lägg syllen 120×120. Långsidan skarvas med spikplåtar mellan två bågfötter, inte under en fot.',
       'Hörnvinklar + 6×200 i hörnen. Nivellera och skruva syllen i markskruvarna.']),
 H('4. Montera bågarna på marken och res dem', 2),
 steg(['Lägg två halvbågar plant på marken. Kontrollera 4000 mellan fötternas mittlinje.',
       'Nocklask 15 mm på båda sidor med PU-lim + 4,5×40 i nockklossarna (gavelbågar: bara insidan).',
       'Hanbjälke 45×120 mitt på kloss 10, ändarna snett kapade längs bågen. Borra Ø11 genom klossen, 2 × M10×160 per ände (inte gavelbågarna).',
       'Res bågen (3–4 personer), ställ den på syllen, vinklar vid foten. Börja i ena gaveln och stötta första bågen.',
       'Sätt nockregelbiten 45×120 mellan bågen och föregående båge innan nästa reses. Mät c/c 1250 vid foten och nocken.']),
 I(B + 'v14_nock.png', 380), I(B + 'v14_han.png', 380),
 H('5. Sidoreglar och vindkryss', 2),
 steg(['Trä sidoregeln 19×95 genom facken i bågarna på 1,9 m höjd, skruva 4×50 genom flänsarna.',
       'Skarva sidoregeln vid en båge.',
       'Hålband diagonalt i de två ändfacken på båda långsidorna, spänn och spika.']),
 H('6. Gavlar och dörrar', 2),
 steg(['Dörrstolpar 95×95 på markskruv, kapas mot bågen på plats.',
       'Överliggare 95×95 och nockstolpe 45×120.',
       'Dörrblad med ram 45×70. Gångjärn, handtag och lås monteras enligt leverantör (ingår inte i listan).']),
 I(B + 'v12_gavel.png', 400),
 H('7. Låsprofiler och film', 2),
 steg(['Skruva låsprofilerna (4,2×25) på syllen, gavelbågarnas utsida, dörrkarmarna och nocken.',
       'Välj en stilla dag. Tak: lås våden i nockprofilen först, dra ut mot syllen och lås. Andra sidan likadant.',
       'Gavlar: lås mot gavelbågen och ner mot syllen, skär ut för dörrarna.',
       'Nockplåten skruvas över nocken med takskruv med EPDM-bricka.']),
 I(B + 'v11_nock_gavel.png', 380),
 H('8. Kontroll', 2),
 Pp('Alla skruvar i vinklar och laskar på plats, filmen spänd utan veck, dörrarna går fritt. '
    'Efter första hårda vinden: efterdra fjädertrådarna och kontrollera syllen.'),
 {'type': 'pagebreak'},
 H('Inköpslista (utan gångjärn och handtag)'),
 Pp('Ur modellen, med ca 10 % spill. Priser 2026-11-03 där de är kollade; övrigt pris ej kollat.'),
 H('Plywood och virke', 2),
 T([['Vara', 'Antal', 'Not'],
    ['Plywood 15 × 2500 × 1200 K20/70', '9 skivor', 'pris ej kollat'],
    ['Regel 45×95 (klossar)', '45 m', 'pris ej kollat'],
    ['120×120 tryckimpregnerat (syll)', '27 m', 'köp 5,4 m-längder'],
    ['45×120 C24 (hanbjälke, nock)', '33 m', 'ca 1 300 kr'],
    ['19×95 gran (sidoreglar)', '22 m', 'skarvas vid en båge'],
    ['95×95 tryckimp. (dörrstolpar)', '11 m', ''],
    ['95×95 gran (överliggare)', '4,4 m', ''],
    ['45×70 (dörrblad)', '26 m', 'ca 630 kr']]),
 Pp('Plywood: 7 skivor till flänsremsor och skarvlaskar, 1 till nocklaskar, 1 i reserv. Kontrollera limning EN 314 klass 3 (utomhus).'),
 H('Grund, beslag och nock', 2),
 T([['Vara', 'Antal', 'Not'],
    ['Markskruv', '22 st', '119 kr/st, ca 2 600 kr'],
    ['Vinkelbeslag 90×90×65 vfz', '44 st', 'bågfot, syllhörn, stolpfot. Ca 660 kr'],
    ['Spikplåt 2×100×200 vfz', '8 st', 'syllskarvar'],
    ['Hålband 40×2 vfz', '20 m', 'vindkryss, 8 band à 2,2 m'],
    ['Excenterlås ställbart med ögla', '2 st', 'dörrar'],
    ['Stormhake / excenterlås fast, rostfritt', '2 st', 'dörrar'],
    ['Kantregel 300', '4 st', 'passiva dörrblad'],
    ['Nockplåt 0,6 mm, bredd 300', '10,1 m', 'i 2–3 längder, 100 mm omlott']]),
 H('Film', 2),
 T([['Vara', 'Antal', 'Not'],
    ['Låsprofil alu + fjädertråd (wiggle wire)', '63 m', 'ca 46 bitar à 2 m'],
    ['Växthusfilm 4,5 m bred', '31 m', 'ni har den (tak 2 × 11,1 m, gavlar 2 × 4,5 m)']]),
 H('Skruv, bult och lim', 2),
 T([['Vara', 'Antal', 'Till'],
    ['Träskruv 5,0×60 C4', '1270 st', 'fläns mot kloss'],
    ['Träskruv 4,5×25 C4', '320 st', 'skarvlaskar'],
    ['Träskruv 5,0×90 C4', '36 st', 'dörrramar'],
    ['Träskruv 4,5×40 C4', '141 st', 'nocklaskar'],
    ['Träskruv 4,0×50 C4', '80 st', 'sidoregel'],
    ['Bult M10×160 vfz + 2 brickor + mutter', '31 st', 'hanbjälkar'],
    ['Konstruktionsskruv 6×120', '44 st', 'stolpfot, nockregelbitar'],
    ['Konstruktionsskruv 6×160 helgängad', '27 st', 'gavelstomme'],
    ['Konstruktionsskruv 6×200', '9 st', 'syllhörn'],
    ['Ankarspik/beslagsskruv 4,0×40 vfz', '660 st', 'vinklar, spikplåtar, hålband'],
    ['Takskruv 4,8×50 med EPDM-bricka', '20 st', 'nockplåt'],
    ['Rostfri skruv brickhuvud 4,2×25', '302 st', 'låsprofiler'],
    ['Rostfri träskruv A2 5,0×25 / 3,0×20', '11 / 9 st', 'lås'],
    ['Träskruv 4,0×25', '18 st', 'kantreglar'],
    ['PU-lim utomhus D4', '2 kg', 'klossar och laskar']]),
]
spec = {'title': 'Växthus – monteringsanvisning', 'author': 'Vickan', 'page_size': 'A4', 'elements': E}
sp = V + '/montering_spec.json'
json.dump(spec, open(sp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
out = V + '/MONTERINGSANVISNING.pdf'
subprocess.run(['python3', os.path.expanduser('~/.hermes/skills/productivity/pdf/scripts/pdf_create.py'), sp, '-o', out], check=True)
print(out)
