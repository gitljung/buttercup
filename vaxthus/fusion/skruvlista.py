#!/usr/bin/env python3
"""Skruvlista för växthuset, räknad ur modellen (v09_antal.json från Fusion-körningen).
Reglerna (skruv per förband) står i REGLER nedan – ändra där, kör igen: python3 skruvlista.py
Antal kroppar och längder kommer från modellen, så listan följer parametrarna."""
import json, math, os, collections

HERE = os.path.dirname(os.path.abspath(__file__))
_f = 'v11_antal.json' if os.path.exists(os.path.join(HERE, 'v11_antal.json')) else 'v09_antal.json'
A = json.load(open(os.path.join(HERE, _f)))
P, LG, N = A['parametrar'], A['lasprofil_mm'], A['antal']
SPILL = 1.10   # +10 % spill/tapp

# skruvsorter
S = {
    'T40':   'Träskruv 4,0×40 C4 (plywood mot kloss)',
    'T30L':  'Träskruv 4,0×30 C4 eller klammer (presskruv när lamellerna limmas)',
    'T95':   'Träskruv 5,0×90 C4 (fläns + kloss genomgående)',
    'T50':   'Träskruv 4,0×50 C4 (fläns mot sidoregel 22×95)',
    'TS':    'Takskruv 4,8×50 med EPDM-bricka (nockplåt)',
    'L45':   'Träskruv 4,5×40 C4 (nocklask mot båge, + PU-lim)',
    'M10':   'Bult M10×160 vfz + 2 brickor + mutter (hanbjälke)',
    'T60':   'Träskruv 4,5×60 C4 (lask + remsa mot kloss)',
    'T25':   'Träskruv 4,0×25 C4 (lask mot remsa utanför klossen)',
    'T45':   'Träskruv 4,5×45 C4 (remsa mot sidoregel)',
    'T90':   'Träskruv 5,0×90 C4 (dörrbladens ramhörn)',
    'AS40':  'Ankarspik/beslagsskruv 4,0×40 vfz (vinklar, spikplåtar)',
    'K160':  'Konstruktionsskruv 6×160 helgängad (gavelstomme)',
    'K120':  'Konstruktionsskruv 6×120 (stolpfot, snedskruv)',
    'K200':  'Konstruktionsskruv 6×200 (syllhörn)',
    'R30':   'Rostfri träskruv A2 4,0×30 (gångjärn GJ60)',
    'R25':   'Rostfri träskruv A2 5,0×25 (excenterlås EL2030)',
    'R20':   'Rostfri träskruv A2 3,0×20 (stormhake EL1035)',
    'M5':    'M5 gängstång A2 65 mm + 2 hattmutter (handtagspar GN425, genom ramen)',
    'P25':   'Rostfri skruv brickhuvud 4,2×25 (låsprofil)',
    'KR25':  'Träskruv 4,0×25 (kantregel, medföljer ofta)',
}


def n(comp, body=None):
    """antal kroppar (× förekomster av komponenten)"""
    c = N.get(comp)
    if not c: return 0
    k = c['kroppar']
    cnt = sum(k.values()) if body is None else sum(v for kk, v in k.items() if kk.startswith(body))
    return cnt * c['förekomster']


rader = []  # (förband, sort, antal, hur)
def R(forband, sort, antal, hur):
    rader.append((forband, sort, int(math.ceil(antal)), hur))

# --- bågar (halvbåge-komponenten finns i 2 × AntalBagar förekomster) ---
hb = N.get('Halvbåge', N.get('Växthus - halvbåge', {}))
halv = hb.get('förekomster', 0); kb = hb.get('kroppar', {})
vanl = sum(v for k, v in kb.items() if k.startswith('Kloss')) + kb.get('Fotkloss', 0) + kb.get('Nockkloss', 0)       # 120 långa
fack = kb.get('Fackkloss', 0)                                                     # 250 långa
lask = sum(v for k, v in kb.items() if k.startswith('Lask'))
# Båge B: flänsar Lameller × LamellT limmade (PU). Klossar limmas + skruvas genomgående 5×90 (fläns 36 + kloss 24 + 30 in i andra flänsen).
lam = int(P.get('Lameller', 1)); BL = P['BagLangd']
if lam > 1:
    R('Lameller: presskruv vid limning (1 rad sicksack c/c 150, per lager utöver det första, 2 flänsar)', 'T30L', halv * 2 * (lam - 1) * BL / 150, f'{halv} halvbågar, {lam} lager')
    R('Vanlig kloss: 2 genomgående från varje sida (+ PU-lim)', 'T95', halv * vanl * 4, f'{halv} × {vanl} klossar')
    R('Fackkloss: 3 genomgående från varje sida (+ PU-lim)', 'T95', halv * fack * 6, f'{halv} × {fack} fackklossar')
    R('Lask över skarv (4 per lask)', 'T25', halv * lask * 4, 'skarvarna förskjuts mellan lagren – lasken kan utgå')
    nb = int(P['AntalBagar'])
    R('Sidoregel 22×95 genom ytter- och innerfläns (2 + 2 per båge och sida)', 'T50', nb * 2 * 4, f'{nb} bågar × 2 sidor')
    R('Nockplåt mot bågarna (1 per sida och båge)', 'TS', nb * 2, f'{nb} bågar')
else:
    R('Bågar: remsa mot vanlig kloss (4/sida × 2 sidor)', 'T40', halv * vanl * 4 * 2, f'{halv} halvbågar × {vanl} klossar')
    R('Bågar: remsa mot fackkloss, sida utan lask (6)', 'T40', halv * (fack * 2 - lask) * 6, f'{halv} × {fack * 2 - lask} sidor')
    R('Bågar: lask + remsa mot fackkloss (6)', 'T60', halv * lask * 6, f'{halv} × {lask} laskar')
    R('Bågar: lask mot remsa utanför klossen (2 per ände)', 'T25', halv * lask * 4, 'lim också')
    nb = int(P['AntalBagar'])
    R('Sidoregel genom ytter- och innerremsa (2 + 2 per båge och sida)', 'T45', nb * 2 * 4, f'{nb} bågar × 2 sidor')

# --- nock och hanbjälke (steg 12) ---
nl = n('Nocklask och hanbjälke', 'Nocklask'); hj = n('Nocklask och hanbjälke', 'Hanbjälke'); nrb = n('Nock och sidoreglar', 'Nockregel bit')
if nl: R('Nocklask mot båge (8 per lask, 4 i varje halvbåge, + PU-lim)', 'L45', nl * 8, f'{nl} laskar')
if nrb: R('Nockregelbit mot lask/båge (2 snedskruv per ände)', 'K120', nrb * 4, f'{nrb} bitar')
if hj: R('Hanbjälke genom båge (2 per ände)', 'M10', hj * 4, f'{hj} hanbjälkar')

# --- beslag ---
vink = n('Vinklar bågfot') + n('Vinklar nock') + n('Syllbeslag') + n('Gavelbeslag', 'Stolpfotsvinkel')
R('Vinklar 90×90×65 (5 per ben)', 'AS40', vink * 10, f'{vink} vinklar')
spik = n('Gavelbeslag', 'Spikplåt')
R('Spikplåt 100×200 (10 per virke)', 'AS40', spik * 20, f'{spik} plåtar')

# --- gavelstomme (konstruktionsskruv) ---
stolp = n('Gavlar', 'Dörrstolpe'); nst = n('Gavlar', 'Nockstolpe'); ovl = n('Gavlar', 'Överliggare')
R('Dörrstolpens topp mot bågen (2 snedskruv)', 'K160', stolp * 2, f'{stolp} stolpar')
R('Nockstolpe mot nockregel och överliggare (2 + 2)', 'K160', nst * 4, f'{nst} nockstolpar')
R('Överliggare genom stolpen (2 per ände)', 'K160', ovl * 4, f'{ovl} överliggare')
R('Dörrstolpens fot mot gavelsyllen (2 snedskruv)', 'K120', stolp * 2, '+ vinkeln')
R('Syllhörn (2 genom långsyllen)', 'K200', 4 * 2, '4 hörn, + vinklar')

# --- dörrar ---
blad = n('Dörrar', 'Dörrblad')
R('Dörrblad, ramhörn (2 per hörn)', 'T90', blad * 4 * 2, f'{blad} blad, + lim')
gj = n('Dörrbeslag', 'Gångjärn')
R('Gångjärn GJ60 100×100 (6 hål)', 'R30', gj * 6, f'{gj} gångjärn – hålantal ej verifierat')
kr = n('Dörrbeslag', 'Kantregel')
R('Kantreglar (4 st per regel)', 'KR25', kr * 4, f'{kr} kantreglar')
kd = N.get('Köpdelar dörr', {})
R('Handtag GN425 ute + inne (2 gängstänger per par)', 'M5', 2 * 2, '2 handtagspar')
R('Excenterlås EL2030-100 (3 + 2 hål)', 'R25', 2 * 5, '2 lås')
R('Stormhake EL1035-200 (2 + 2 hål)', 'R20', 2 * 4, '2 hakar')

# --- låsprofil ---
cc, PL = P['ProfilSkruvCC'], P['ProfilL']
ps = 0; bitar = 0; lm = 0
for k, ls in LG.items():
    for L in ls:
        nbit = max(1, math.ceil(L / PL)); bitar += nbit; lm += L
        ps += nbit * (math.ceil((L / nbit) / cc) + 1)
R(f'Låsprofil, c/c {cc:g} + ändarna', 'P25', ps, f'{lm / 1000:.1f} m i {bitar} bitar')

# --- summering ---
tot = collections.OrderedDict()
for f, s, a, h in rader: tot[s] = tot.get(s, 0) + a
out = ['# Skruvlista växthus (ur modellen)', '', f"Hus {P['Bredd']:g}×{P['Langd']:g}, nock {P['Nockhojd']:g}, {nb} bågar c/c {P['BagCC']:g}. Spill +{round((SPILL - 1) * 100)} %.", '', '## Per förband']
out += [f'- {f}: {a} × {S[s]} ({h})' for f, s, a, h in rader]
out += ['', '## Att köpa (inkl. spill)']
out += [f'- {S[s]}: {a} st → {int(math.ceil(a * SPILL))} st' for s, a in tot.items()]
out += ['', f'Låsprofil: {lm / 1000:.1f} m ({bitar} bitar à {PL / 1000:g} m); fjädertråd lika långt (+ gavelbågarna dubbelt om tak- och gavelfilm låses med var sin tråd).']
txt = '\n'.join(out)
open(os.path.join(HERE, 'SKRUVLISTA.md'), 'w').write(txt + '\n')
print(txt)
