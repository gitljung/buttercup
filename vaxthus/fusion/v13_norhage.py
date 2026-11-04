# Steg 13 (Victor 2026-11-04): båge "som Norhage" – fläns 1 x 15 plywood x 100, klossar av regel 45 (45 längs bågen),
#   c/c 250, fotkloss 300, bågdjup 100. Bredd 4000 / nock 3500 oförändrat. Ingen hållfasthetsberäkning (Victor: räkna bara på begäran).
#   Bara parametrar + fotklossens längd blir egen parameter (FotKlossL). Flextest, sparar bara om OK.
import builtins as _bi
_o = _bi.open
def open(f, m='r', *a, **k):
    if 'b' not in m and 'encoding' not in k and not a: k['encoding'] = 'utf-8'
    return _o(f, m, *a, **k)
exec(open(os.path.expanduser('~/code/buttercup/vaxthus/fusion/v08b_kopdelar.py')).read().split('\ndef run(')[0])
_ns['skip_par'] = skip_par; kontroll = _ns['kontroll']
NYA10 = [
    ('FotKlossL', '300 mm', 'mm', 'Fotklossens längd längs bågen (Norhage ca 300)'),
]
ANDRA10 = [
    ('Lameller', '1', 'Antal plywoodlager per fläns (1 = som Norhage)'),
    ('LamellT', '15 mm', 'Flänsens plywoodtjocklek'),
    ('PlyT', 'Lameller * LamellT', 'Fläns = lager x tjocklek (1 x 15)'),
    ('BagB', '100 mm', 'Bågens bredd längs huset = flänsbredd 100'),
    ('KlossH', '70 mm', 'Kloss radiellt -> bågdjup 15 + 70 + 15 = 100'),
    ('KlossL', '45 mm', 'Kloss av regel 45 (45 längs bågen), som Norhage'),
    ('FackKlossL', '45 mm', 'Klossarna vid sidoregelns fack: samma regel 45'),
    ('KlossCCmax', '250 mm', 'Största c/c mellan klossar (Norhage ca 250)'),
    ('FotKlossS', 'FotKlossL / 2', 'Fotklossens mitt längs bågen'),
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
    nd = 0
    for comp in des.allComponents:
        for sk in comp.sketches:
            for dm in sk.sketchDimensions:
                try:
                    if dm.parameter and dm.parameter.expression.replace(' ', '') == 'KlossL':
                        dm.parameter.expression = 'FotKlossL'; nd += 1; log('fotklossmått', comp.name, sk.name)
                except Exception: pass
    log('fotklossmått ändrade', nd)
    if nd == 0: raise Exception('hittade inget fotklossmått')
    log('före', fore)
    for n, e, c in ANDRA10:
        p = up.itemByName(n); p.expression = e; p.comment = c
    des.computeAll()
    log('efter', {n: round(up.itemByName(n).value * 10, 1) for n, _, _ in ANDRA10}, 'BagDjup', round(ev('BagDjup'), 1),
        'NedreMellan', up.itemByName('NedreMellan').value, 'OvreMellan', up.itemByName('OvreMellan').value, 'NedrePitch', round(ev('NedrePitch'),1), 'OvrePitch', round(ev('OvrePitch'),1))
    gom(des)
    FLEXMODE = False
    alla = [kontroll(des, root, 'standard')]
    L = ev('Langd'); hb, sh = ev('HalvBredd'), ev('SyllH')
    bild('v13_dummy.png', (7000, -7000, 4500), (0, L / 2, 1700), 9000)
    bild('v13_iso.png', (7000, -7000, 4500), (0, L / 2, 1700), 9000)
    bild('v13_gavel.png', (1200, -9000, 1900), (0, 0, 1800), 4800)
    bild('v13_bage_nara.png', (hb + 1400, 1250 - 1700, 2300), (hb - 300, 1250, 1700), 1700)
    bild('v13_nock.png', (700, 1250 - 1500, 4200), (0, 1250, 3500), 900)
    bild('v13_fot.png', (hb + 900, 1250 - 900, 700), (hb, 1250, 200), 900)
    orig = {k: up.itemByName(k).expression for k in FLEX}
    try:
        FLEXMODE = True
        for k, v in FLEX.items(): up.itemByName(k).expression = v
        alla.append(kontroll(des, root, 'flex (köpdelar ej omplacerade)'))
    finally:
        for k, v in orig.items(): up.itemByName(k).expression = v
        FLEXMODE = False
    alla.append(kontroll(des, root, 'återställt'))
    json.dump(alla, open(os.path.expanduser('~/code/buttercup/vaxthus/fusion/v13_resultat.json'), 'w'), ensure_ascii=False, indent=1)
    try: os.remove(OUT + 'v13_dummy.png')
    except Exception: pass
    a0, a1, a2 = alla
    if a0['antal_krock'] or a0['fel'] or a0['ej_last'] or a2['fel'] or a2['antal_krock'] or a2['kroppar_totalt'] != a0['kroppar_totalt'] or a1['fel'] or a1['antal_krock'] or a0['ej_last'] or a2['ej_last']:
        raise Exception('kontroll underkänd, sparar inte')
    d.save('Steg 13: båge som Norhage – fläns 1x15x100, klossar regel 45 c/c 250, fotkloss 300, djup 100')
    log('sparad', TOPPNAMN)
    try:
        sp = os.path.expanduser('~/code/buttercup/vaxthus/fusion/export/Vaxthus.step')
        em = des.exportManager; ok = em.execute(em.createSTEPExportOptions(sp, root)); log('STEP', ok, os.path.getsize(sp))
    except Exception as e: log('STEP FEL', str(e)[:200])
