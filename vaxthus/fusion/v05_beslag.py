# Steg 6 (beslag, del 1), i dokumentet "Växthus" efter steg 4:
#  - "Vinklar bågfot": vinkel 90x90x65x2,5 på bågens fram-/baksida ner på långsyllen
#  - "Vinklar nock":   vinkel från nockregelns sida in på bågens fram-/baksida
#    Båda: +y-vinklar på båge 0..N-2, -y-vinklar på båge 1..N-1 (gavelbågarna får bara insidan),
#    speglade till vänster sida och mönstrade 'AntalBagar - 1' × BagCC -> följer antal bågar.
#  - "Syllbeslag": vinkel i syllhörnets insida + spikplåt 100x200x2 på gavelns framsida, speglad till alla fyra hörn.
# Köpdelsförslag: förstärkt vinkelbeslag 90x90x65x2,5 vfz (t.ex. Jula 012856), spikplåt Joma 2x100x200 vfz, ankarspik 4,0x40.
exec(open(os.path.expanduser('~/code/buttercup/vaxthus/fusion/v04_syll_nock.py')).read().split('\ndef run(')[0])
NYA5 = [
    ('VinkelA', '90 mm', 'mm', 'Vinkelbeslag: benlängd'),
    ('VinkelB', '65 mm', 'mm', 'Vinkelbeslag: bredd'),
    ('VinkelT', '2.5 mm', 'mm', 'Vinkelbeslag: plåttjocklek'),
    ('SpikplatL', '200 mm', 'mm', 'Spikplåt: längd'),
    ('SpikplatB', '100 mm', 'mm', 'Spikplåt: bredd'),
    ('SpikplatT', '2 mm', 'mm', 'Spikplåt: tjocklek'),
    ('NockVinkelZ', '( BagCz + sqrt( ( BagR - BagDjup / 2 ) * ( BagR - BagDjup / 2 ) - ( NockT / 2 + BagCx ) * ( NockT / 2 + BagCx ) ) + BagCz + sqrt( ( BagR + BagDjup / 2 ) * ( BagR + BagDjup / 2 ) - ( NockT / 2 + VinkelA + BagCx ) * ( NockT / 2 + VinkelA + BagCx ) ) ) / 2', 'mm', 'Härledd: nockvinkelns mitt i höjd (ryms i bågen över hela benet)'),
]


def zink(des):
    return appearance(des, 'Varmförzinkat', 'Paint - Metallic (Silver)', (185, 190, 194))


def L_body(D, plane, au, av, pts, ext_axis, start, dist, lo, name):
    sk = D.r.sketches.add(D.PL[plane]); sk.name = 'Skiss ' + name
    S = Skiss(D, sk, au, av)
    S.poly(pts)
    rep = S.report(); log(rep)
    if not rep[1]: raise Exception('ej låst: ' + name)
    f = D.ext(S.biggest(), ext_axis, start, dist, lo, name)
    b = f.bodies.item(0); b.name = name
    return b


def pattern_y(comp, bodies, qty, dist, name, check):
    rp = comp.features.rectangularPatternFeatures
    for sg in ('', '-'):
        inp = rp.createInput(coll(bodies), comp.yConstructionAxis, VI(qty), VI(sg + dist), adsk.fusion.PatternDistanceType.SpacingPatternDistanceType)
        inp.setDirectionTwo(comp.xConstructionAxis, VI('1'), VI('0 mm'))
        f = rp.add(inp)
        ys = [b.boundingBox.maxPoint.y * 10 for b in comp.bRepBodies]
        if check(max(ys)): f.name = name; return f
        f.deleteMe()
    raise Exception('mönster fel: ' + name)


def bygg_vinklar(des, comp, kind):
    D = K(des, comp)
    D.PL = {'xy': comp.xYConstructionPlane, 'xz': comp.xZConstructionPlane, 'yz': comp.yZConstructionPlane}
    ev = D.ev
    b2, A, T, cc = ev('BagB') / 2, ev('VinkelA'), ev('VinkelT'), ev('BagCC')
    bodies = []
    for side, base, bexp in ((1, 0.0, None), (-1, cc, 'BagCC')):
        # u = y-koordinat (belopp-uttryck från origo)
        def U(off_expr, off_val):
            y = base + side * (b2 + off_val)
            if bexp is None: e = 'BagB / 2' + ((' + ' + off_expr) if off_expr else '')
            else: e = 'BagCC - BagB / 2' + ((' - ' + off_expr) if off_expr else '')
            return y, e
        y0, e0 = U('', 0); yA, eA = U('VinkelA', A); yT, eT = U('VinkelT', T)
        nm = ('fram' if side == 1 else 'bak')
        if kind == 'fot':
            sh = ev('SyllH')
            pts = [(y0, sh, e0, 'SyllH'), (yA, sh, eA, 'SyllH'), (yA, sh + T, eA, 'SyllH + VinkelT'),
                   (yT, sh + T, eT, 'SyllH + VinkelT'), (yT, sh + A, eT, 'SyllH + VinkelA'), (y0, sh + A, e0, 'SyllH + VinkelA')]
            hb, vb = ev('HalvBredd'), ev('VinkelB')
            b = L_body(D, 'yz', 'y', 'z', pts, 'x', 'HalvBredd - VinkelB / 2', 'VinkelB', hb - vb / 2, 'Vinkel bågfot %s höger' % nm)
        else:
            nt = ev('NockT') / 2
            pts = [(nt, y0, 'NockT / 2', e0), (nt + A, y0, 'NockT / 2 + VinkelA', e0), (nt + A, yT, 'NockT / 2 + VinkelA', eT),
                   (nt + T, yT, 'NockT / 2 + VinkelT', eT), (nt + T, yA, 'NockT / 2 + VinkelT', eA), (nt, yA, 'NockT / 2', eA)]
            zc, vb = ev('NockVinkelZ'), ev('VinkelB')
            b = L_body(D, 'xy', 'x', 'y', pts, 'z', 'NockVinkelZ - VinkelB / 2', 'VinkelB', zc - vb / 2, 'Vinkel nock %s höger' % nm)
        bodies.append(b)
    m = mirror(comp, bodies, comp.yZConstructionPlane, 'Vänster sida (spegling)')
    allb = [comp.bRepBodies.item(i) for i in range(comp.bRepBodies.count)]
    L = ev('Langd')
    pattern_y(comp, allb, 'AntalBagar - 1', 'BagCC', 'Längs huset (AntalBagar - 1)', lambda ymax: abs(ymax - (L - b2)) < 1)
    typ = 'bågfot' if kind == 'fot' else 'nock'
    for b in comp.bRepBodies:
        b.appearance = zink(des)
        bb = b.boundingBox; ym = (bb.minPoint.y + bb.maxPoint.y) * 5; xm = (bb.minPoint.x + bb.maxPoint.x) * 5
        k = int(round(ym / cc)); sida = '+y' if ym > k * cc else '-y'
        b.name = 'Vinkel %s båge %d %s %s' % (typ, k + 1, sida, 'höger' if xm > 0 else 'vänster')
    comp.partNumber = 'VINKEL-90x90x65'; comp.description = 'Förstärkt vinkelbeslag 90x90x65x2,5 vfz (köpdel), ankarspik 4,0x40'
    for s in comp.sketches: s.isVisible = False


def bygg_syllbeslag(des, comp):
    D = K(des, comp)
    D.PL = {'xy': comp.xYConstructionPlane, 'xz': comp.xZConstructionPlane, 'yz': comp.yZConstructionPlane}
    ev = D.ev
    hb, sb, sh, A, T, vb = ev('HalvBredd'), ev('SyllB'), ev('SyllH'), ev('VinkelA'), ev('VinkelT'), ev('VinkelB')
    xi = hb - sb / 2; yi = sb / 2
    # hörnvinkel på insidan: båda benen lodräta, bockaxel lodrät i (xi, yi)
    pts = [(xi, yi, 'HalvBredd - SyllB / 2', 'SyllB / 2'), (xi - A, yi, 'HalvBredd - SyllB / 2 - VinkelA', 'SyllB / 2'),
           (xi - A, yi + T, 'HalvBredd - SyllB / 2 - VinkelA', 'SyllB / 2 + VinkelT'), (xi - T, yi + T, 'HalvBredd - SyllB / 2 - VinkelT', 'SyllB / 2 + VinkelT'),
           (xi - T, yi + A, 'HalvBredd - SyllB / 2 - VinkelT', 'SyllB / 2 + VinkelA'), (xi, yi + A, 'HalvBredd - SyllB / 2', 'SyllB / 2 + VinkelA')]
    v = L_body(D, 'xy', 'x', 'y', pts, 'z', 'SyllH / 2 - VinkelB / 2', 'VinkelB', sh / 2 - vb / 2, 'Hörnvinkel insida fram höger')
    # hörnvinkel på utsidan (gavelsyllens framsida mot långsyllens insida, i långsyllens utstick)
    pts2 = [(xi, -yi, 'HalvBredd - SyllB / 2', 'SyllB / 2'), (xi - A, -yi, 'HalvBredd - SyllB / 2 - VinkelA', 'SyllB / 2'),
            (xi - A, -yi - T, 'HalvBredd - SyllB / 2 - VinkelA', 'SyllB / 2 + VinkelT'), (xi - T, -yi - T, 'HalvBredd - SyllB / 2 - VinkelT', 'SyllB / 2 + VinkelT'),
            (xi - T, -yi - A, 'HalvBredd - SyllB / 2 - VinkelT', 'SyllB / 2 + VinkelA'), (xi, -yi - A, 'HalvBredd - SyllB / 2', 'SyllB / 2 + VinkelA')]
    p = L_body(D, 'xy', 'x', 'y', pts2, 'z', 'SyllH / 2 - VinkelB / 2', 'VinkelB', sh / 2 - vb / 2, 'Hörnvinkel utsida fram höger')
    mirror(comp, [v, p], comp.yZConstructionPlane, 'Vänster (spegling)')
    pi = comp.constructionPlanes.createInput(); pi.setByOffset(comp.xZConstructionPlane, VI('Langd / 2'))
    mid = comp.constructionPlanes.add(pi); mid.name = 'Mittplan längs (Langd / 2)'
    if abs(mid.geometry.origin.y * 10 - ev('Langd') / 2) > 1e-3:
        mid.deleteMe(); pi = comp.constructionPlanes.createInput(); pi.setByOffset(comp.xZConstructionPlane, VI('-Langd / 2'))
        mid = comp.constructionPlanes.add(pi); mid.name = 'Mittplan längs (Langd / 2)'
    mirror(comp, [comp.bRepBodies.item(i) for i in range(comp.bRepBodies.count)], mid, 'Bak (spegling)')
    mid.isLightBulbOn = False
    for b in comp.bRepBodies:
        b.appearance = zink(des)
        bb = b.boundingBox; cxm = (bb.minPoint.x + bb.maxPoint.x) / 2; cym = (bb.minPoint.y + bb.maxPoint.y) * 5
        fram = cym < ev('Langd') / 2
        ins = (cym > 0) if fram else (cym < ev('Langd'))
        b.name = 'Hörnvinkel %s %s %s' % ('insida' if ins else 'utsida', 'fram' if fram else 'bak', 'höger' if cxm > 0 else 'vänster')
    comp.partNumber = 'SYLLBESLAG'; comp.description = 'Hörnvinkel 90x90x65x2,5 vfz, insida + utsida (köpdelar)'
    for s in comp.sketches: s.isVisible = False


def run(_context: str):
    keepalive()
    d = find_doc(TOPPNAMN)
    if d: d.close(False)
    d = app.documents.open(dfile(TOPPNAMN)); d.activate()
    des = adsk.fusion.Design.cast(d.products.itemByProductType('DesignProductType'))
    root = des.rootComponent; up = des.userParameters
    if not des.allComponents.itemByName('Syllram') or abs(up.itemByName('Bagavstand').value * 10 - 1250) > 0.1:
        raise Exception('steg 4 saknas i sparad modell - kör v04 först')
    for n, e, u, c in NYA5:
        p = up.itemByName(n)
        if p: p.expression = e
        else: up.add(n, VI(e), u, c).isFavorite = True
    des.computeAll()
    log('NockVinkelZ', round(up.itemByName('NockVinkelZ').value * 10, 1))
    for o in list(root.occurrences):
        if o.component.name in ('Vinklar bågfot', 'Vinklar nock', 'Syllbeslag'): o.deleteMe()
    I = adsk.core.Matrix3D.create()
    for nm, fn in (('Vinklar bågfot', lambda c: bygg_vinklar(des, c, 'fot')), ('Vinklar nock', lambda c: bygg_vinklar(des, c, 'nock')), ('Syllbeslag', lambda c: bygg_syllbeslag(des, c))):
        o = root.occurrences.addNewComponent(I); o.component.name = nm
        fn(o.component); o.isGrounded = True
        log(nm, o.component.bRepBodies.count, 'kroppar')
    gom(des)
    alla = [kontroll(des, root, 'standard')]
    n = up.itemByName('AntalBagar').value
    antal = {nm: des.allComponents.itemByName(nm).bRepBodies.count for nm in ('Vinklar bågfot', 'Vinklar nock', 'Syllbeslag')}
    log('antal', antal, 'väntat vinklar per sort', 4 * (n - 1))
    L = up.itemByName('Langd').value * 10; nk = up.itemByName('NockOK').value * 10; hb = up.itemByName('HalvBredd').value * 10
    bild('v05_dummy.png', (hb + 900, -900, 900), (hb, 300, 150), 1300)
    bild('v05_bagfot.png', (hb + 900, -900, 900), (hb, 300, 150), 1300)
    bild('v05_bagfot_inne.png', (hb - 1200, 1900, 900), (hb, 1250, 150), 1300)
    bild('v05_nock.png', (700, 500, nk - 900), (0, 1250, nk - 60), 1000)
    bild('v05_syllhorn_ute.png', (hb + 900, -1200, 500), (hb - 100, -60, 60), 1100)
    bild('v05_syllhorn_inne.png', (hb - 1100, 900, 700), (hb - 60, 60, 60), 1100)
    orig = {k: up.itemByName(k).expression for k in FLEX}
    try:
        for k, v in FLEX.items(): up.itemByName(k).expression = v
        alla.append(kontroll(des, root, 'flex'))
        alla[-1]['beslag'] = {nm: des.allComponents.itemByName(nm).bRepBodies.count for nm in antal}
        log('flex beslag', alla[-1]['beslag'], 'AntalBagar', up.itemByName('AntalBagar').value)
    finally:
        for k, v in orig.items(): up.itemByName(k).expression = v
    alla.append(kontroll(des, root, 'återställt'))
    json.dump(alla, open(os.path.expanduser('~/code/buttercup/vaxthus/fusion/v05_resultat.json'), 'w'), ensure_ascii=False, indent=1)
    try: os.remove(OUT + 'v05_dummy.png')
    except Exception: pass
    a0, a1, a2 = alla
    if a2['fel'] or a2['antal_krock'] or a2['ej_last'] or a2['kroppar_totalt'] != a0['kroppar_totalt'] or a1['fel'] or a1['ej_last'] or a1['antal_krock']:
        raise Exception('kontroll underkänd, sparar inte')
    d.save('Steg 6a: vinklar bågfot + nock (mönstrade), syllbeslag; flextest OK')
    log('sparad', TOPPNAMN)
