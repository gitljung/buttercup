# Steg 10: nya bågdimensioner efter belastningsberäkningen (bara raka sågsnitt, böjda remsor):
#   flänsar 2 lameller x 12 mm K20/70 (limmade vid böjningen), remsbredd 95, bågdjup 200, klossar c/c <= 200,
#   sidoregel 45x145 på högkant i facket (fyller facket radiellt = fungerar som kloss).
#   Ändrar bara parametrar – modellen ska följa med (metodikens test). Krockkontroll + flextest, sparar bara om OK.
exec(open(os.path.expanduser('~/code/buttercup/vaxthus/fusion/v08b_kopdelar.py')).read().split('\ndef run(')[0])
_ns['skip_par'] = skip_par; kontroll = _ns['kontroll']
NYA10 = [
    ('Lameller', '3', '', 'Antal plywoodlameller per fläns (limmas ihop när de böjs)'),
    ('LamellT', '12 mm', 'mm', 'Lamellens tjocklek (K20/70 konstruktionsplywood, Byggmax 12x2500x1200)'),
]
ANDRA10 = [
    ('PlyT', 'Lameller * LamellT', 'Fläns = lameller x lamelltjocklek (3 x 12)'),
    ('BagB', '95 mm', 'Bågens bredd längs huset (remsbredd, 12 remsor ur en 1200-skiva)'),
    ('KlossH', '2 * LamellT', 'Kloss = 2 lager av samma 12 mm-skiva -> bågdjup 96'),
    ('KlossCCmax', '450 mm', 'Största c/c mellan klossar -> 11 klossar per halvbåge (beslut B, 20 m/s)'),
    ('SidoregelT', '22 mm', 'Sidoregel 22x95 (radiellt 22, i facket mellan flänsarna)'),
    ('SidoregelH', '95 mm', 'Sidoregel 22x95: 95 längs bågen'),
]


def run(_context: str):
    global FLEXMODE
    keepalive()
    d = find_doc(TOPPNAMN)
    if d: d.close(False)
    d = app.documents.open(dfile(TOPPNAMN)); d.activate()
    des = adsk.fusion.Design.cast(d.products.itemByProductType('DesignProductType'))
    root = des.rootComponent; up = des.userParameters
    ev = lambda s: des.unitsManager.evaluateExpression(s, 'mm') * 10
    for n, e, u, c in NYA10:
        p = up.itemByName(n)
        if p: p.expression = e
        else: up.add(n, VI(e), u, c).isFavorite = True
    fore = {n: up.itemByName(n).expression for n, _, _ in ANDRA10}
    log('före', fore)
    for n, e, c in ANDRA10:
        p = up.itemByName(n); p.expression = e; p.comment = c
    des.computeAll()
    log('efter', {n: round(up.itemByName(n).value * 10, 1) for n, _, _ in ANDRA10}, 'BagDjup', round(ev('BagDjup'), 1),
        'NedreMellan', up.itemByName('NedreMellan').value, 'OvreMellan', up.itemByName('OvreMellan').value)
    gom(des)
    FLEXMODE = False
    alla = [kontroll(des, root, 'standard')]
    L = ev('Langd'); hb, sh = ev('HalvBredd'), ev('SyllH')
    bild('v10b_dummy.png', (7000, -7000, 4500), (0, L / 2, 1700), 9000)
    bild('v10b_iso.png', (7000, -7000, 4500), (0, L / 2, 1700), 9000)
    bild('v10b_gavel.png', (1200, -9000, 1900), (0, 0, 1800), 4800)
    bild('v10b_bage_nara.png', (hb + 1400, 1250 - 1700, 2300), (hb - 300, 1250, 1700), 1700)
    bild('v10b_nock.png', (700, 1250 - 1500, 4200), (0, 1250, 3500), 900)
    bild('v10b_fot.png', (hb + 900, 1250 - 900, 700), (hb, 1250, 200), 900)
    orig = {k: up.itemByName(k).expression for k in FLEX}
    try:
        FLEXMODE = True
        for k, v in FLEX.items(): up.itemByName(k).expression = v
        alla.append(kontroll(des, root, 'flex (köpdelar ej omplacerade)'))
    finally:
        for k, v in orig.items(): up.itemByName(k).expression = v
        FLEXMODE = False
    alla.append(kontroll(des, root, 'återställt'))
    json.dump(alla, open(os.path.expanduser('~/code/buttercup/vaxthus/fusion/v10b_resultat.json'), 'w'), ensure_ascii=False, indent=1)
    try: os.remove(OUT + 'v10b_dummy.png')
    except Exception: pass
    a0, a1, a2 = alla
    if a0['antal_krock'] or a0['fel'] or a0['ej_last'] or a2['fel'] or a2['antal_krock'] or a2['kroppar_totalt'] != a0['kroppar_totalt'] or a1['fel'] or a1['antal_krock']:
        raise Exception('kontroll underkänd, sparar inte')
    d.save('Steg 10b: båge B – 3x12 lameller, bredd 95, djup 96, 11 klossar, sidoregel 22x95 (vind 20 m/s)')
    log('sparad', TOPPNAMN)
