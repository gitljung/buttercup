# Steg 14 (Victor "ja" 2026-11-04): hanbjälken flyttas till mitten av övre kloss 2 (HanZ följer klossens läge)
#  och ändarna kapas snett längs bågen (korda på bågens ytterradie mellan över- och underkant) så att den
#  överlappar fläns + kloss + fläns och bultas genom klossen. Nocklask i samma 15 mm plywood som flänsarna.
#  Skriver v11_antal.json, bilder, STEP. Sparar bara om kontrollen går igenom.
import builtins as _bi
_o = _bi.open
def open(f, m='r', *a, **k):
    if 'b' not in m and 'encoding' not in k and not a: k['encoding'] = 'utf-8'
    return _o(f, m, *a, **k)
exec(open(os.path.expanduser('~/code/buttercup/vaxthus/fusion/v12_nocklask_han.py'), encoding='utf-8').read().split('\ndef run(')[0])
NYA14 = [
    ('HanKloss', '2', '', 'Hanbjälken sitter mitt på denna övre kloss (räknat från facket)'),
    ('HanXu', '-BagCx + sqrt( ( BagR + BagDjup / 2 ) * ( BagR + BagDjup / 2 ) - ( HanZ - HanH / 2 - BagCz ) * ( HanZ - HanH / 2 - BagCz ) )', 'mm',
     'Härledd: hanbjälkens halva längd i underkant (snett kapad ände längs bågens ytterradie)'),
]
ANDRA14 = [
    ('HanZ', 'BagCz + BagR * sin( ( FackOvreS + ( FackKlossL - KlossL ) / 2 + HanKloss * OvrePitch ) / BagR * 1 rad )',
     'Hanbjälkens mitt = mitt på övre kloss nr HanKloss (bultas genom klossen)'),
    ('HanX', '-BagCx + sqrt( ( BagR + BagDjup / 2 ) * ( BagR + BagDjup / 2 ) - ( HanZ + HanH / 2 - BagCz ) * ( HanZ + HanH / 2 - BagCz ) )',
     'Härledd: hanbjälkens halva längd i överkant (snett kapad ände längs bågens ytterradie)'),
    ('NockLaskT', 'LamellT', 'Nocklask i samma plywood som flänsarna (15 mm)'),
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
    for n, e, u, c in NYA14[:1]:
        p = up.itemByName(n)
        if p: p.expression = e
        else: up.add(n, VI(e), u, c).isFavorite = True
    for n, e, c in ANDRA14:
        p = up.itemByName(n); p.expression = e; p.comment = c
    for n, e, u, c in NYA14[1:]:
        p = up.itemByName(n)
        if p: p.expression = e
        else: up.add(n, VI(e), u, c).isFavorite = True
    des.computeAll()
    log('HanZ', round(ev('HanZ'), 1), 'HanX', round(ev('HanX'), 1), 'HanXu', round(ev('HanXu'), 1), 'NockLaskT', round(ev('NockLaskT'), 1))
    c = des.allComponents.itemByName('Nocklask och hanbjälke'); D = K(des, c)
    for f in list(c.features.rectangularPatternFeatures):
        if f.name == 'Hanbjälke mönster': f.deleteMe()
    for f in list(c.features.extrudeFeatures):
        if f.name == 'Hanbjälke': f.deleteMe()
    sk0 = c.sketches.itemByName('Skiss Hanbjälke')
    if sk0: sk0.deleteMe()
    sk = c.sketches.add(c.xZConstructionPlane); sk.name = 'Skiss Hanbjälke'
    S = Skiss(D, sk, 'x', 'z'); hx, hu, hz, hh = ev('HanX'), ev('HanXu'), ev('HanZ'), ev('HanH')
    S.poly([(-hu, hz - hh / 2, 'HanXu', 'HanZ - HanH / 2'), (hu, hz - hh / 2, 'HanXu', 'HanZ - HanH / 2'),
            (hx, hz + hh / 2, 'HanX', 'HanZ + HanH / 2'), (-hx, hz + hh / 2, 'HanX', 'HanZ + HanH / 2')])
    log('hanbjälkeskiss', S.report())
    if not sk.isFullyConstrained: raise Exception('hanbjälkeskiss ej låst')
    f = D.ext(S.biggest(), 'y', 'BagCC + BagB / 2', 'HanT', ev('BagCC + BagB / 2'), 'Hanbjälke'); hb0 = f.bodies.item(0); hb0.name = 'Hanbjälke'
    L = ev('Langd')
    pat(c, [hb0], 'AntalBagar - 2', 'BagCC', 'Hanbjälke mönster', L - ev('BagCC') + ev('BagB / 2 + HanT'))
    for b in c.bRepBodies:
        dz = (b.boundingBox.maxPoint.z - b.boundingBox.minPoint.z) * 10
        b.name = 'Hanbjälke' if dz < hh + 1 else 'Nocklask'
        b.appearance = plywood(des) if b.name == 'Nocklask' else tra(des)
    for s_ in c.sketches: s_.isVisible = False
    c.description = 'Nocklask 15 mm plywood (båda sidor, gavelbågar insida) + hanbjälke 45x120 mitt på övre kloss HanKloss, ändar snett längs bågen, 2 x M10 genom klossen'
    des.computeAll()
    lg = langder(des, des.allComponents.itemByName('Låsprofiler'), ev)
    lg['Låsprofil nock'] = [round(ev('Langd + BagB'))]
    def pval(k):
        q = up.itemByName(k)
        return round(q.value, 3) if q.unit == '' else round(ev(k), 1)
    pv = {up.item(i).name: pval(up.item(i).name) for i in range(up.count)}
    gom(des)
    FLEXMODE = False
    alla = [kontroll(des, root, 'standard')]
    json.dump({'parametrar': pv, 'lasprofil_mm': lg, 'antal': antal_alla(des), 'remsor_mm': alla[0].get('remsor_mm')},
              open(os.path.expanduser('~/code/buttercup/vaxthus/fusion/v11_antal.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump(pv, open(os.path.expanduser('~/code/buttercup/vaxthus/fusion/v13_param.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    hb = ev('HalvBredd'); nk = ev('NockOK')
    bild('v14_dummy.png', (7000, -7000, 4500), (0, L / 2, 1700), 9000)
    bild('v14_iso.png', (7000, -7000, 4500), (0, L / 2, 1700), 9000)
    bild('v14_han.png', (hb + 400, 1250 - 1300, hz + 500), (hu - 100, 1250, hz), 900)
    bild('v14_inifran.png', (hb - 600, -700, 1300), (0, L / 2, 2400), 5600)
    bild('v14_nock.png', (800, 1250 - 1100, nk + 300), (0, 1250 + 300, nk - 120), 900)
    orig = {k: up.itemByName(k).expression for k in FLEX}
    try:
        FLEXMODE = True
        for k, v in FLEX.items(): up.itemByName(k).expression = v
        alla.append(kontroll(des, root, 'flex (köpdelar ej omplacerade)'))
    finally:
        for k, v in orig.items(): up.itemByName(k).expression = v
        FLEXMODE = False
    alla.append(kontroll(des, root, 'återställt'))
    json.dump(alla, open(os.path.expanduser('~/code/buttercup/vaxthus/fusion/v14_resultat.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    try: os.remove(OUT + 'v14_dummy.png')
    except Exception: pass
    a0, a1, a2 = alla
    if any(a[k] for a in alla for k in ('antal_krock', 'fel', 'ej_last')) or a2['kroppar_totalt'] != a0['kroppar_totalt']:
        raise Exception('kontroll underkänd, sparar inte')
    d.save('Steg 14: hanbjälke mitt på övre kloss 2, ändar snett längs bågen; nocklask 15 mm')
    log('sparad', TOPPNAMN)
    try:
        sp = os.path.expanduser('~/code/buttercup/vaxthus/fusion/export/Vaxthus.step')
        em = des.exportManager; ok = em.execute(em.createSTEPExportOptions(sp, root)); log('STEP', ok, os.path.getsize(sp))
    except Exception as e: log('STEP FEL', str(e)[:200])
