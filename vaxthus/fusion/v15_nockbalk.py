# Steg 15 (Victor "ja" 2026-11-04): nocken som Norhage.
#  - Nockbalk 45x70 i HELA längder som läggs uppifrån i nockglipan (glipa = NockBalkB + 2 x NockSpel = 50) genom alla bågar.
#    (Köps i längder om 2 x BagCC så att skarvarna hamnar på en båge + skarvplåt – modelleras som en kropp.)
#  - Nocklaskarna (15 mm, raka snitt) får ett urtag för balken och går NockLaskUnder under urtaget; balken vilar i urtagen.
#  - Nockregelbitarna utgår. Nockstolpen i gaveln följer balkens bredd/underkant.
import builtins as _bi
_o = _bi.open
def open(f, m='r', *a, **k):
    if 'b' not in m and 'encoding' not in k and not a: k['encoding'] = 'utf-8'
    return _o(f, m, *a, **k)
exec(open(os.path.expanduser('~/code/buttercup/vaxthus/fusion/v14_hanbjalke.py'), encoding='utf-8').read().split('\ndef run(')[0])
NYA15 = [
    ('NockBalkB', '45 mm', 'mm', 'Nockbalk bredd (regel 45x70 på högkant, som Norhage)'),
    ('NockBalkH', '70 mm', 'mm', 'Nockbalk höjd'),
    ('NockSpel', '2.5 mm', 'mm', 'Spel per sida mellan nockbalken och halvbågarnas nockändar'),
    ('NockLaskUnder', '60 mm', 'mm', 'Nocklask: material under balkens urtag'),
    ('NockBalkLangd', '2 * BagCC', 'mm', 'Inköpslängd nockbalk (skarv på varannan båge, skarvplåt)'),
]
ANDRA15 = [('NockT', 'NockBalkB + 2 * NockSpel', 'Nockglipa mellan halvbågarna = nockbalk + spel (Norhage 50)')]
E_ = lambda r, x: 'BagCz + sqrt( ( %s ) * ( %s ) - ( %s + BagCx ) * ( %s + BagCx ) )' % (r, r, x, x)
RR = 'BagR + BagDjup / 2 - NockLaskAvdrag'


def lask_skiss(D, c, name, ev):
    sk = c.sketches.add(c.xZConstructionPlane); sk.name = name
    S = Skiss(D, sk, 'x', 'z')
    zE, zS = E_(RR, 'NockLaskL / 2'), E_(RR, 'NockT / 2')
    zN = 'NockOK - NockBalkH'; zU0 = 'NockOK - NockBalkH - NockLaskUnder'; zUE = '%s - ( ( %s ) - ( %s ) )' % (zU0, zS, zE)
    v = lambda e: ev(e)
    LX, XS = ev('NockLaskL / 2'), ev('NockT / 2')
    pts = [(-LX, v(zE), 'NockLaskL / 2', zE), (-XS, v(zS), 'NockT / 2', zS), (-XS, v(zN), 'NockT / 2', zN), (XS, v(zN), 'NockT / 2', zN),
           (XS, v(zS), 'NockT / 2', zS), (LX, v(zE), 'NockLaskL / 2', zE), (LX, v(zUE), 'NockLaskL / 2', zUE), (0.0, v(zU0), '0', zU0),
           (-LX, v(zUE), 'NockLaskL / 2', zUE)]
    S.poly(pts)
    log(name, S.report())
    if not sk.isFullyConstrained: raise Exception('nocklaskskiss ej låst: ' + name)
    return S.biggest()


def run(_context: str):
    global FLEXMODE
    keepalive()
    d = find_doc(TOPPNAMN)
    if d: d.close(False)
    d = app.documents.open(dfile(TOPPNAMN)); d.activate()
    des = adsk.fusion.Design.cast(d.products.itemByProductType('DesignProductType'))
    root = des.rootComponent; up = des.userParameters
    ev = lambda s: des.unitsManager.evaluateExpression(s, 'mm') * 10
    for n, e, u, cm in NYA15:
        p = up.itemByName(n)
        if p: p.expression = e
        else: up.add(n, VI(e), u, cm).isFavorite = True
    for n, e, cm in ANDRA15:
        p = up.itemByName(n); p.expression = e; p.comment = cm
    # nockstolpe + gamla nockregelskissen: bredd/underkant följer nockbalken
    nd = 0
    for comp in des.allComponents:
        for sk in comp.sketches:
            for dm in sk.sketchDimensions:
                try:
                    ex = dm.parameter.expression
                    if comp.name in ('Gavlar', 'Nock och sidoreglar') and sk.name.startswith(('Nockstolpe', 'Nockregel', 'Skiss Nockstolpe')) or 'Nockstolpe' in sk.name:
                        nx = ex.replace('NockT / 2', 'NockBalkB / 2').replace('NockOK - NockH', 'NockOK - NockBalkH')
                        if nx != ex: dm.parameter.expression = nx; nd += 1; log('mått', comp.name, sk.name, nx)
                except Exception: pass
    log('ändrade mått', nd)
    des.computeAll()
    # --- nockbalk: gamla bitar bort, ny hel balk ---
    nc = des.allComponents.itemByName('Nock och sidoreglar'); D = K(des, nc)
    for f in list(nc.features.rectangularPatternFeatures):
        if f.name == 'Nockregel bitar': f.deleteMe()
    for f in list(nc.features.extrudeFeatures):
        if f.name in ('Nockregel bit', 'Nockbalk'): f.deleteMe()
    sk = nc.sketches.itemByName('Nockregel')
    log('nockregelskiss', sk.name, sk.isFullyConstrained, [dm.parameter.expression for dm in sk.sketchDimensions])
    prof = max([sk.profiles.item(i) for i in range(sk.profiles.count)], key=lambda p: p.areaProperties().area)
    f = D.ext(prof, 'y', 'BagB / 2', 'Langd + BagB', -ev('BagB / 2'), 'Nockbalk')
    for i in range(f.bodies.count): f.bodies.item(i).name = 'Nockbalk'
    # --- nocklaskar med urtag ---
    c = des.allComponents.itemByName('Nocklask och hanbjälke'); D = K(des, c)
    for f in list(c.features.rectangularPatternFeatures):
        if f.name.startswith('Nocklask'): f.deleteMe()
    for f in list(c.features.extrudeFeatures):
        if f.name.startswith('Nocklask'): f.deleteMe()
    for s_ in list(c.sketches):
        if s_.name.startswith('Skiss Nocklask'): s_.deleteMe()
    L = ev('Langd')
    p = lask_skiss(D, c, 'Skiss Nocklask +y', ev)
    f = D.ext(p, 'y', 'BagB / 2', 'NockLaskT', ev('BagB / 2'), 'Nocklask +y'); la = f.bodies.item(0); la.name = 'Nocklask'
    pat(c, [la], 'AntalBagar - 1', 'BagCC', 'Nocklask +y mönster', L - ev('BagCC') + ev('BagB / 2 + NockLaskT'))
    p = lask_skiss(D, c, 'Skiss Nocklask -y', ev)
    f = D.ext(p, 'y', 'BagCC - BagB / 2 - NockLaskT', 'NockLaskT', ev('BagCC - BagB / 2 - NockLaskT'), 'Nocklask -y'); lb = f.bodies.item(0); lb.name = 'Nocklask'
    pat(c, [lb], 'AntalBagar - 1', 'BagCC', 'Nocklask -y mönster', L - ev('BagB / 2'))
    hh = ev('HanH')
    for b in c.bRepBodies:
        dz = (b.boundingBox.maxPoint.z - b.boundingBox.minPoint.z) * 10
        b.name = 'Hanbjälke' if abs(dz - hh) < 1 else 'Nocklask'
        b.appearance = plywood(des) if b.name == 'Nocklask' else tra(des)
    for s_ in c.sketches: s_.isVisible = False
    for s_ in nc.sketches: s_.isVisible = False
    c.description = 'Nocklask 15 mm plywood med urtag för nockbalken (båda sidor, gavelbågar insida) + hanbjälke 45x120 på övre kloss HanKloss'
    des.computeAll()
    log('NockT', ev('NockT'), 'NockOK', round(ev('NockOK'), 1), 'balk uk', round(ev('NockOK - NockBalkH'), 1))
    lg = langder(des, des.allComponents.itemByName('Låsprofiler'), ev)
    lg['Låsprofil nock'] = [round(ev('Langd + BagB'))]
    def pval(k):
        q = up.itemByName(k)
        return round(q.value * 10, 1) if q.unit == 'mm' else round(q.value, 4)
    pv = {up.item(i).name: pval(up.item(i).name) for i in range(up.count)}
    gom(des)
    FLEXMODE = False
    alla = [kontroll(des, root, 'standard')]
    json.dump({'parametrar': pv, 'lasprofil_mm': lg, 'antal': antal_alla(des), 'remsor_mm': alla[0].get('remsor_mm')},
              open(os.path.expanduser('~/code/buttercup/vaxthus/fusion/v11_antal.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump(pv, open(os.path.expanduser('~/code/buttercup/vaxthus/fusion/v13_param.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    hb = ev('HalvBredd'); nk = ev('NockOK')
    bild('v15_dummy.png', (7000, -7000, 4500), (0, L / 2, 1700), 9000)
    bild('v15_iso.png', (7000, -7000, 4500), (0, L / 2, 1700), 9000)
    bild('v15_nock.png', (700, 1250 - 1000, nk - 700), (0, 1250 + 200, nk - 60), 800)
    bild('v15_nock_ovan.png', (600, 1250 - 900, nk + 600), (0, 1250 + 200, nk - 40), 800)
    bild('v15_gavel.png', (900, -1600, nk - 400), (0, 0, nk - 200), 1400)
    orig = {k: up.itemByName(k).expression for k in FLEX}
    try:
        FLEXMODE = True
        for k, v in FLEX.items(): up.itemByName(k).expression = v
        alla.append(kontroll(des, root, 'flex (köpdelar ej omplacerade)'))
    finally:
        for k, v in orig.items(): up.itemByName(k).expression = v
        FLEXMODE = False
    alla.append(kontroll(des, root, 'återställt'))
    json.dump(alla, open(os.path.expanduser('~/code/buttercup/vaxthus/fusion/v15_resultat.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    try: os.remove(OUT + 'v15_dummy.png')
    except Exception: pass
    a0, a1, a2 = alla
    if any(a[k] for a in alla for k in ('antal_krock', 'fel', 'ej_last')) or a2['kroppar_totalt'] != a0['kroppar_totalt']:
        raise Exception('kontroll underkänd, sparar inte')
    d.save('Steg 15: nock som Norhage – hel nockbalk 45x70 i glipan 50, nocklaskar med urtag')
    log('sparad', TOPPNAMN)
    try:
        sp = os.path.expanduser('~/code/buttercup/vaxthus/fusion/export/Vaxthus.step')
        em = des.exportManager; ok = em.execute(em.createSTEPExportOptions(sp, root)); log('STEP', ok, os.path.getsize(sp))
    except Exception as e: log('STEP FEL', str(e)[:200])
