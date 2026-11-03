#!/usr/bin/env python3
"""Inköpslista för växthuset, räknad ur modellen (v11_antal.json + v11_kroppar.json från Fusion) och SKRUVLISTA.md.
Kör: python3 skruvlista.py && python3 inkopslista.py  -> INKOPSLISTA.md
Priser: bara de som är kollade (källa + datum står vid priset). Övriga: 'pris ej kollat'."""
import json, math, os, re, collections

HERE = os.path.dirname(os.path.abspath(__file__))
A = json.load(open(os.path.join(HERE, 'v11_antal.json'), encoding='utf-8'))
KR = json.load(open(os.path.join(HERE, 'v11_kroppar.json'), encoding='utf-8'))
P, LG, RM = A['parametrar'], A['lasprofil_mm'], A['remsor_mm']
SPILL = 1.10
nb = int(P['AntalBagar']); halv = 2 * nb
lam, LT, BB = int(P['Lameller']), P['LamellT'], P['BagB']
SKIVA_L, SKIVA_B, SAGSNITT = P['SkivaL'], 1200.0, 3.0
PRIS = {
    'ply12': (429, 'Byggmax konstruktionsplywood 12×2500×1200 (Moelven K20/70), 429 kr/st, byggmax.se 2026-11-03'),
    '45x120': (39.95, 'Byggmax regel 45×120 C24, 39,95 kr/m (kategorisidan) 2026-11-03'),
    '45x70': (23.95, 'Byggmax regel 45×70, 23,95 kr/m (kategorisidan) 2026-11-03'),
}
rader = collections.OrderedDict()
def rad(grupp, text, pris=None):
    rader.setdefault(grupp, []).append((text, pris))

def bas(n): return re.sub(r' (fram|bak|höger|vänster|insida|utsida|nedre|övre|\+y|-y|\d+|\(\d+\))', '', n).strip()

# ---------- 1. plywood: alla bågdelar ur 95 mm-remsor av 12 mm-skiva ----------
bitar = []   # längder (mm) av 95 × 12-bitar
per_halv = collections.Counter()
for b in KR:
    if b['komp'] != 'Halvbåge': continue
    per_halv[bas(b['kropp'])] += 1
per_halv = {k: v / halv for k, v in per_halv.items()}
for nm, L in RM.items():                       # flänsbitar: varje bit = lam lameller
    bitar += [L] * lam * halv
kl_n = per_halv.get('Kloss', 0) + per_halv.get('Fotkloss', 0) + per_halv.get('Nockkloss', 0)
fk_n = per_halv.get('Fackkloss', 0)
kl_lager = max(1, round(P['KlossH'] / LT))
bitar += [P['KlossL']] * int(round(kl_n * halv)) * kl_lager
bitar += [P['FackKlossL']] * int(round(fk_n * halv)) * kl_lager
laskL = max([max(b['mått']) for b in KR if b['komp'] == 'Halvbåge' and b['kropp'].startswith('Lask')] or [0])
lask_n = sum(v for k, v in per_halv.items() if k.startswith('Lask'))
bitar += [laskL] * int(round(lask_n * halv)) * lam
# first-fit decreasing i 2500-remsor (sågsnitt 3 mm)
remsor = []
for L in sorted(bitar, reverse=True):
    for i, r in enumerate(remsor):
        if r + L + SAGSNITT <= SKIVA_L: remsor[i] = r + L + SAGSNITT; break
    else: remsor.append(L)
per_skiva = int((SKIVA_B + SAGSNITT) // (BB + SAGSNITT))
skivor = math.ceil(len(remsor) / per_skiva)
skivor_k = math.ceil(skivor * SPILL)
rad('Plywood', f'Konstruktionsplywood 12×2500×1200: {skivor_k} skivor (netto {skivor} + 10 %). '
               f'Sågas till {len(remsor)} remsor 95 × 2500 ({per_skiva} per skiva). Innehåll: {len(RM) * lam * halv} flänsbitar '
               f'({lam} lager × {len(RM)} bitar × {halv} halvbågar, längder {", ".join(str(v) for v in RM.values())} mm), '
               f'{int(round((kl_n + fk_n) * halv))} klossar à {kl_lager} lager, {int(round(lask_n * halv))} laskar à {lam} lager.',
    skivor_k * PRIS['ply12'][0])

# ---------- 2. virke (gran / tryckimpregnerat) ----------
virke = collections.defaultdict(list)
for b in KR:
    k = b['komp']
    if k not in ('Syllram', 'Nock och sidoreglar', 'Gavlar'): continue
    n = bas(b['kropp'])
    tvar = {'Syll': '120×120 tryckimpregnerat', 'Nockregel': '45×120 C24', 'Sidoregel': f"{P['SidoregelT']:g}×{P['SidoregelH']:g} (råspont/panel, gran)",
            'Dörrstolpe': '95×95 tryckimpregnerat (stolpe)', 'Överliggare': '95×95 gran', 'Nockstolpe': '45×120 C24'}
    key = next((v for kk, v in tvar.items() if n.startswith(kk)), n)
    virke[key].append(max(b['mått']) if n not in ('Sidoregel',) else P['Langd'] + P['BagB'])
MAXL = 5400.0
for key, ls in virke.items():
    lm = sum(ls) / 1000
    st = sum(math.ceil(L / MAXL) for L in ls)
    pr = PRIS['45x120'][0] * lm * SPILL if key.startswith('45×120') else None
    rad('Virke', f'{key}: {len(ls)} delar, {lm:.1f} lpm (+10 % → {lm * SPILL:.1f} m). Längsta {max(ls) / 1000:.2f} m'
                 + (f' → skarvas, Byggmax säljer max 5,4 m ({st} längder)' if max(ls) > MAXL else ''), pr)
ram = [b for b in KR if b['komp'] == 'Dörrar']
if ram:
    d = sorted(ram[0]['mått'])
    lm = len(ram) * 2 * (d[1] + d[2]) / 1000
    rad('Virke', f'Dörrblad: {len(ram)} blad {d[1]:.0f}×{d[2]:.0f}, ram 45×70 ≈ {lm:.1f} lpm (+10 % → {lm * SPILL:.1f} m)', PRIS['45x70'][0] * lm * SPILL)

# ---------- 3. metall ----------
c = collections.Counter((b['komp'], bas(b['kropp'])) for b in KR)
vink = sum(v for (k, n), v in c.items() if 'Vinkel' in n or 'vinkel' in n)
rad('Beslag', f'Vinkelbeslag 90×90×65 vfz: {vink} st (bågfot {c[("Vinklar bågfot", "Vinkel bågfot båge")]}, nock {c[("Vinklar nock", "Vinkel nock båge")]}, syllhörn {c[("Syllbeslag", "Hörnvinkel")]}, stolpfot {c[("Gavelbeslag", "Stolpfotsvinkel")]}). Jula 012856 14,90 kr/st (2026-11-03)', vink * 14.90)
sp = sum(v for (k, n), v in c.items() if n.startswith('Spikplåt'))
rad('Beslag', f'Spikplåt 2×100×200 vfz: {sp} st', None)
kd = json.load(open(os.path.join(HERE, 'kopdelar.json'), encoding='utf-8'))
for k in ('gangjarn', 'handtag', 'las', 'stormhake'):
    x = kd[k]; rad('Beslag', f"{x['art']} ({x['namn']}): {x['antal']} st à {x['pris_ex']:.2f} kr ex moms (Wiberger, summan inkl. moms)", x['antal'] * x['pris_ex'] * 1.25)
rad('Beslag', f"Kantregel 300: {c[('Dörrbeslag', 'Kantregel')]} st", None)
mark = 2 * nb + 4
rad('Grund', f'Markskruv: {mark} st (en per bågfot + 4 vid dörrstolparna). 119 kr/st (2026-11-03)', mark * 119)
npL = P['Langd'] + P['BagB']
rad('Nock', f"Nockplåt {P['NockPlatT']:g} mm förzinkad/lackerad, bredd {P['NockPlatB']:.0f} (≈ {P['NockPlatB'] * 1.03:.0f} utvikt), {npL / 1000:.2f} m – bockas efter bågen på plats eller beställs i 2–3 längder med 100 mm omlott", None)

# ---------- 4. film + låsprofil ----------
pl, PLL = 0, P['ProfilL']; nbit = 0
for k, ls in LG.items():
    for L in ls: pl += L; nbit += max(1, math.ceil(L / PLL))
rad('Film', f'Låsprofil alu 32×13 + fjädertråd (wiggle wire): {pl / 1000:.1f} m → {nbit} bitar à {PLL / 1000:g} m '
            f'(nock {sum(LG.get("Låsprofil nock", [0])) / 1000:.1f} m). VEVOR-sats 50 × 2 m 164,90 € (2026-11-03) räcker om ≤ 50 bitar', None)
tak = 2 * (P['Langd'] + P['BagB'] + 2 * P['FilmOverlapp']) / 1000
gav = 2 * (P['Nockhojd'] + 2 * P['FilmOverlapp']) / 1000
rad('Film', f'Växthusfilm 4,5 m bred (ni har den): tak 2 våder × {tak / 2:.1f} m = {tak:.1f} m, gavlar 2 × {gav / 2:.1f} m = {gav:.1f} m '
            f'(gavelns bredd {P["Bredd"] / 1000:g} m ryms i 4,5 m). Totalt {tak + gav:.1f} m av 4,5 m-rullen.', None)

# ---------- 5. skruv (ur SKRUVLISTA.md) + lim ----------
sl = open(os.path.join(HERE, 'SKRUVLISTA.md'), encoding='utf-8').read()
kop = sl.split('## Att köpa (inkl. spill)')[1].split('\n\n')[0].strip().splitlines()
for r in kop: rad('Skruv', r.lstrip('- '), None)
lim_m2 = (sum(RM.values()) * (lam - 1) * BB * halv + (kl_n + fk_n) * halv * 2 * BB * 150) / 1e6
rad('Lim', f'PU-lim utomhus (D4/vattenfast): limyta ≈ {lim_m2:.1f} m² (lamellerna + klossarna) → ca {math.ceil(lim_m2 * 0.25):.0f} kg vid 250 g/m²', None)
rad('Rekommenderas (ej ritat)', 'Vindkryss: hålband 40×2 vfz diagonalt i de två ändfacken på båda långsidorna (8 band à ca 2,2 m) – stabiliserar i längsled mot gavelvind', None)

out = ['# Inköpslista växthus (ur modellen)', '',
       f"Hus {P['Bredd']:g}×{P['Langd']:g}, nock {P['Nockhojd']:g}, {nb} bågar c/c {P['BagCC']:g}. Båge: flänsar {lam}×{LT:g} × {BB:g}, djup {P['BagDjup']:g}, "
       f"{kl_n + fk_n:g} klossar per halvbåge. Spill +10 %. Priser inkl. moms där inget annat står.", '']
tot = 0
for g, rs in rader.items():
    out.append(f'## {g}')
    for t, p in rs:
        out.append(f'- {t}' + (f' — **≈ {p:,.0f} kr**'.replace(',', ' ') if p else ''))
        tot += p or 0
    out.append('')
out.append(f'**Summa av de prissatta raderna: ≈ {tot:,.0f} kr**'.replace(',', ' ') + ' (virke 120×120, 95×95, 22×95, spikplåt, nockplåt, skruv, lim och låsprofil är inte prissatta; filmen har ni).')
out.append('')
out.append('Källor priser: ' + '; '.join(v[1] for v in PRIS.values()) + '; Jula 012856; Wiberger (kopdelar.json); markskruv 119 kr.')
txt = '\n'.join(out)
open(os.path.join(HERE, 'INKOPSLISTA.md'), 'w', encoding='utf-8').write(txt + '\n')
print(txt)
