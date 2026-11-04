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
 Pp('Bågväxthus i limmad plywood, 9 bågar c/c 1250, nock 3,5 m. Film 4,5 m med wiggle wire. '
    'Mått och delar enligt Fusion-modellen "Växthus" och ritningen <i>ritning_bage.pdf</i> (blad 1–3). '
    'Dimensionerat för snölast Höör och vind ca 20 m/s.'),
 I(B + 'v12_iso.png', 470),
 H('Verktyg', 2),
 Pp('Cirkelsåg med anslag (eller spårsåg med skena), kapsåg, skruvdragare + slagskruvdragare, borr Ø11 (lång), '
    'måttband, vinkelhake, vattenpass/laser, snöre, tvingar, handskar. Limning vid minst 15 °C.'),
 H('1. Såga remsor och klossar', 2),
 steg(['Såga plywoodskivorna 12 × 2500 × 1200 i remsor 95 mm (12 per skiva), se ritning blad 2.',
       'Kapa flänsbitarna enligt kapplistan: 12 bitar per halvbåge (bit A + bit B i 6 lager). Märk lager 1–6.',
       'Klossar ur spillet: limma två remsor på varandra, kapa 9 st 120 och 2 st 250 per halvbåge (blad 3).',
       'Såga 16 nocklaskar (sexhörning, bara raka snitt, blad 3). Gör en mall av den första.']),
 H('2. Limma halvbågarna (18 st)', 2),
 steg(['Böj och limma innerflänsen (lager 1–3, PU-lim) i en böjmall med innerradie R 3808 och pressa jämnt. Härdar 2–4 h.',
       'Märk klossarnas lägen (tabell blad 1). Limma klossarna och sedan ytterflänsens lager 4–6, pressa.',
       'Efter härdning: 2 skruv 5×90 per kloss utifrån (3 i fackklossarna).',
       'Kapa foten vågrätt och nocken lodrätt efter kaplinjerna. Märk halvbågen H1–H18.',
       'Borra 2 × Ø11 för hanbjälken (inte på de 4 gavelhalvorna).']),
 I(K + 'ritning_bage_1.png', 480),
 H('3. Grund och syll', 2),
 steg(['Mät ut 4000 × 10000, kontrollera diagonalerna. Skruva ner 22 markskruvar (en per bågfot + 4 vid dörrstolparna).',
       'Lägg syllen 120×120. Långsidan skarvas med spikplåtar mellan två bågfötter, inte under en fot.',
       'Hörnvinklar + 6×200 i hörnen. Nivellera och skruva syllen i markskruvarna.']),
 H('4. Montera bågarna på marken och res dem', 2),
 steg(['Lägg två halvbågar plant på marken. Kontrollera 4000 mellan fötternas mittlinje.',
       'Nocklask på båda sidor med PU-lim + 4,5×40 (gavelbågar: bara insidan).',
       'Bulta hanbjälken 45×120 med 2 × M10 per ände (inte gavelbågarna).',
       'Res bågen (3–4 personer), ställ den på syllen, vinklar vid foten. Börja i ena gaveln och stötta första bågen.',
       'Sätt nockregelbiten 45×120 mellan bågen och föregående båge innan nästa reses. Mät c/c 1250 vid foten och nocken.']),
 I(B + 'v12_nock.png', 380), I(B + 'v12_han.png', 380),
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
    ['Plywood 12 × 2500 × 1200 K20/70', '21 skivor', 'ca 9 000 kr'],
    ['120×120 tryckimpregnerat (syll)', '27 m', 'köp 5,4 m-längder'],
    ['45×120 C24 (hanbjälke, nock)', '32 m', 'ca 1 300 kr'],
    ['19×95 gran (sidoreglar)', '22 m', 'skarvas vid en båge'],
    ['95×95 tryckimp. (dörrstolpar)', '11 m', ''],
    ['95×95 gran (överliggare)', '4,4 m', ''],
    ['45×70 (dörrblad)', '26 m', 'ca 630 kr']]),
 Pp('Plywood: 18 skivor till remsor och klossar, 1 till nocklaskar, 2 i reserv. Kontrollera att limningen är EN 314 klass 3 (utomhus). 429 kr/st hos Byggmax.'),
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
    ['Träskruv 5,0×90 C4', '990 st', 'klossar genom flänsar + dörrramar'],
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
    ['PU-lim utomhus D4', '9 kg', 'lameller och klossar']]),
]
spec = {'title': 'Växthus – monteringsanvisning', 'author': 'Vickan', 'page_size': 'A4', 'elements': E}
sp = V + '/montering_spec.json'
json.dump(spec, open(sp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
out = V + '/MONTERINGSANVISNING.pdf'
subprocess.run(['python3', os.path.expanduser('~/.hermes/skills/productivity/pdf/scripts/pdf_create.py'), sp, '-o', out], check=True)
print(out)
