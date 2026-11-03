#!/usr/bin/env python3
"""Skruvlista för växthuset, räknad ur modellen (v09_antal.json från Fusion-körningen).
Reglerna (skruv per förband) står i REGLER nedan – ändra där, kör igen: python3 skruvlista.py
Antal kroppar och längder kommer från modellen, så listan följer parametrarna."""
import json, math, os, collections

HERE = os.path.dirname(os.path.abspath(__file__))
A = json.load(open(os.path.join(HERE, 'v09_antal.json')))
P, LG, N = A['parametrar'], A['lasprofil_mm'], A['antal']
SPILL = 1.10   # +10 % spill/tapp

# skruvsorter
S = {
    'T40':   'Träskruv 4,0×40 C4 (plywood mot kloss)',
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
vanl = kb.get('Kloss', 0) + kb.get('Fotkloss', 0) + kb.get('Nockkloss', 0)       # 120 långa
fack = kb.get('Fackkloss', 0)                                                     # 250 långa
lask = sum(v for k, v in kb.items() if k.startswith('Lask'))
# varje kloss har två plywoodsidor (ytter + inner). Vanlig kloss 4 skruv/sida, fackkloss 6/sida.
# de sidor som täcks av lasken (1 fackkloss per lask) tar längre skruv.
R('Bågar: remsa mot vanlig kloss (4/sida × 2 sidor)', 'T40', halv * vanl * 4 * 2, f'{halv} halvbågar × {vanl} klossar')
R('Bågar: remsa mot fackkloss, sida utan lask (6)', 'T40', halv * (fack * 2 - lask) * 6, f'{halv} × {fack * 2 - lask} sidor')
R('Bågar: lask + remsa mot fackkloss (6)', 'T60', halv * lask * 6, f'{halv} × {lask} laskar')
R('Bågar: lask mot remsa utanför klossen (2 per ände)', 'T25', halv * lask * 4, 'lim också')
nb = int(P['AntalBagar'])
R('Sidoregel genom ytter- och innerremsa (2 + 2 per båge och sida)', 'T45', nb * 2 * 4, f'{nb} bågar × 2 sidor')

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
