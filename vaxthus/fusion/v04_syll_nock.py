# Steg 4: i dokumentet "Växthus":
#  - parametrar: Bagavstand 1250 (Victor 2026-11-03), SkivaL 2500 (K20/70 15x2500, mest prisvärd), + NockOK, FackVinkel
#  - komponent "Syllram": syll långsida (höger + spegling), syll gavel fram (höger + spegling) + bak (spegling i Langd/2)
#  - komponent "Nock och sidoreglar": nockregel 45x120 på högkant, sidoregel 34x145 i facket (höger + spegling)
# Allt i skisser med parameteruttryck, fullt låsta. Sedan kontroll + flextest + bilder + spara.
exec(open(os.path.expanduser('~/code/buttercup/vaxthus/fusion/v03_topp.py')).read().split('\ndef run(')[0])
K.ext = Del.ext; K.cut = Del.cut; K.fillet_edges = Del.fillet_edges   # samma extrudering som detaljfilerna
NYA = [
    ('SyllUtstick', '120 mm', 'mm', 'Långsyllens utstick förbi gavelbågens yttersida (bär yttre bågfotsvinkel + hörnvinkel utsida, ≥ VinkelA)'),
    ('NockOK', 'BagCz + sqrt( ( BagR + BagDjup / 2 ) * ( BagR + BagDjup / 2 ) - ( NockT / 2 + BagCx ) * ( NockT / 2 + BagCx ) )', 'mm', 'Härledd: nockregelns överkant = bågens yttersida vid nockregeln'),
]
ANDRA = {'Bagavstand': '1250 mm', 'SkivaL': '2500 mm'}
ANDRA_KOMMENTAR = {'SkivaL': 'Plywoodskivans längd = längsta remsa (K20/70 15x2500, mest prisvärd)'}


def mirror(comp, bodies, plane, name):
    mf = comp.features.mirrorFeatures
    f = mf.add(mf.createInput(coll(bodies), plane)); f.name = name
    return [f.bodies.item(i) for i in range(f.bodies.count)]


def bygg_syll(des, comp):
    D = K(des, comp)
    # långsida höger: profil i xz, extrudera längs y
    sk = comp.sketches.add(comp.xZConstructionPlane); sk.name = 'Syll långsida'
    S = Skiss(D, sk, 'x', 'z')
    hb, sb, sh = D.ev('HalvBredd'), D.ev('SyllB'), D.ev('SyllH')
    S.rect(hb - sb / 2, hb + sb / 2, 0, sh, 'HalvBredd - SyllB / 2', 'HalvBredd + SyllB / 2', '0', 'SyllH')
    log(S.report())
    f = D.ext(S.biggest(), 'y', 'BagB / 2 + SyllUtstick', 'Langd + BagB + 2 * SyllUtstick', -(D.ev('BagB') / 2 + D.ev('SyllUtstick')), 'Syll långsida')
    b = f.bodies.item(0); b.name = 'Syll långsida höger'
    m = mirror(comp, [b], comp.yZConstructionPlane, 'Syll långsida vänster (spegling)')
    m[-1].name = 'Syll långsida vänster'
    # gavel fram höger: profil i yz, extrudera längs x från dörröppningen till långsidan
    sk2 = comp.sketches.add(comp.yZConstructionPlane); sk2.name = 'Syll gavel'
    S2 = Skiss(D, sk2, 'y', 'z')
    S2.rect(-sb / 2, sb / 2, 0, sh, 'SyllB / 2', 'SyllB / 2', '0', 'SyllH')
    log(S2.report())
    dw = D.ev('DorrBredd') / 2
    f2 = D.ext(S2.biggest(), 'x', 'DorrBredd / 2', 'HalvBredd - SyllB / 2 - DorrBredd / 2', dw, 'Syll gavel fram höger')
    g = f2.bodies.item(0); g.name = 'Syll gavel fram höger'
    gv = mirror(comp, [g], comp.yZConstructionPlane, 'Syll gavel fram vänster (spegling)')
    gv[-1].name = 'Syll gavel fram vänster'
    pi = comp.constructionPlanes.createInput(); pi.setByOffset(comp.xZConstructionPlane, VI('Langd / 2'))
    mid = comp.constructionPlanes.add(pi); mid.name = 'Mittplan längs (Langd / 2)'
    if abs(mid.geometry.origin.y * 10 - D.ev('Langd') / 2) > 1e-3:
        mid.deleteMe(); pi = comp.constructionPlanes.createInput(); pi.setByOffset(comp.xZConstructionPlane, VI('-Langd / 2'))
        mid = comp.constructionPlanes.add(pi); mid.name = 'Mittplan längs (Langd / 2)'
    bak = mirror(comp, [g, gv[-1]], mid, 'Syll gavel bak (spegling)')
    for k, bb in enumerate(sorted(bak[-2:], key=lambda x: x.boundingBox.minPoint.x)):
        bb.name = 'Syll gavel bak ' + ('vänster' if k == 0 else 'höger')
    mid.isLightBulbOn = False
    for bb in comp.bRepBodies: bb.appearance = tryck(des)
    comp.partNumber = 'VH-SYLL'; comp.description = 'Syll 120x120 tryckimpregnerat'


def bygg_nock(des, comp):
    D = K(des, comp)
    E, ev = D.E, D.ev
    # nockregel
    sk = comp.sketches.add(comp.xZConstructionPlane); sk.name = 'Nockregel'
    S = Skiss(D, sk, 'x', 'z')
    nt, nok, nh = ev('NockT') / 2, ev('NockOK'), ev('NockH')
    S.rect(-nt, nt, nok - nh, nok, 'NockT / 2', 'NockT / 2', 'NockOK - NockH', 'NockOK')
    log(S.report())
    bb2 = ev('BagB') / 2
    f = D.ext(S.biggest(), 'y', 'BagB / 2', 'Langd + BagB', -bb2, 'Nockregel')
    f.bodies.item(0).name = 'Nockregel'
    # sidoregel: bågens mittlinje i egen skiss (samma låsning som halvbågen), radiell linje till fackets mitt
    R = ev('BagR'); cx = -ev('BagCx'); cz = ev('BagCz'); SH = ev('SyllH')
    f0 = math.asin(ev('Spetsighet') / R)
    pt = lambda rr, th: (cx + rr * math.cos(th), 0.0, cz + rr * math.sin(th))
    s2 = comp.sketches.add(comp.xZConstructionPlane); s2.name = 'Sidoregel'
    o = s2.originPoint; gc = s2.geometricConstraints; LS = s2.sketchCurves.sketchLines
    Q = lambda p: SP(s2, *p)
    tF = math.asin((SH - cz) / R); tN = math.atan2(ev('Nockhojd') - cz, -cx)
    a = s2.sketchCurves.sketchArcs.addByThreePoints(Q(pt(R, tF)), Q(pt(R, (tF + tN) / 2)), Q(pt(R, tN)))
    a.isConstruction = True
    ps, pe = a.startSketchPoint, a.endSketchPoint
    pF, pN = (ps, pe) if ps.geometry.distanceTo(Q(pt(R, tF))) < pe.geometry.distanceTo(Q(pt(R, tF))) else (pe, ps)
    dimx(s2, o, pF, 'x', 'HalvBredd', (ev('HalvBredd') / 2, 0, SH - 150))
    dimx(s2, o, pF, 'z', 'SyllH', (ev('HalvBredd') + 150, 0, SH / 2))
    gc.addCoincident(pN, proj_axis(s2, comp, 'z'))
    dimx(s2, o, pN, 'z', 'Nockhojd', (-200, 0, ev('Nockhojd') / 2))
    s2.sketchDimensions.addRadialDimension(a, Q(pt(R * 0.9, 0.9))).parameter.expression = 'BagR'
    C0 = a.centerSketchPoint
    ref = LS.addByTwoPoints(C0, pF); ref.isConstruction = True
    th = f0 + ev('FackS') / R
    rin = R - ev('KlossH') / 2; T = ev('SidoregelT'); Hh = ev('SidoregelH') / 2
    rad = LS.addByTwoPoints(C0, Q(pt(rin, th))); rad.isConstruction = True
    s2.sketchDimensions.addAngularDimension(ref, rad, Q(pt(R * 0.35, (f0 + th) / 2))).parameter.expression = 'FackS / BagR * 1 rad'
    AL = adsk.fusion.DimensionOrientations.AlignedDimensionOrientation
    s2.sketchDimensions.addDistanceDimension(C0, rad.endSketchPoint, AL, Q(pt(rin * 0.6, th + 0.03))).parameter.expression = 'BagR - KlossH / 2'
    M = rad.endSketchPoint
    tx, tz = -math.sin(th), math.cos(th)          # tangent (uppåt längs bågen)
    nx, nz = math.cos(th), math.sin(th)           # normal utåt
    mx, mz = pt(rin, th)[0], pt(rin, th)[2]
    P = lambda u, v: Q((mx + tx * u + nx * v, 0, mz + tz * u + nz * v))
    e1 = LS.addByTwoPoints(P(-Hh, 0), P(Hh, 0))
    e2 = LS.addByTwoPoints(e1.endSketchPoint, P(Hh, T))
    e3 = LS.addByTwoPoints(e2.endSketchPoint, P(-Hh, T))
    e4 = LS.addByTwoPoints(e3.endSketchPoint, e1.startSketchPoint)
    gc.addPerpendicular(e1, rad); gc.addMidPoint(M, e1)
    gc.addPerpendicular(e2, e1); gc.addParallel(e3, e1); gc.addPerpendicular(e4, e1)
    s2.sketchDimensions.addDistanceDimension(e1.startSketchPoint, e1.endSketchPoint, AL, P(0, -60)).parameter.expression = 'SidoregelH'
    s2.sketchDimensions.addDistanceDimension(e2.startSketchPoint, e2.endSketchPoint, AL, P(Hh + 60, T / 2)).parameter.expression = 'SidoregelT'
    log('Sidoregel låst', s2.isFullyConstrained, free_report(s2)[:6])
    prof = min([s2.profiles.item(i) for i in range(s2.profiles.count)], key=lambda p_: p_.areaProperties().area)
    f = D.ext(prof, 'y', 'BagB / 2', 'Langd + BagB', -bb2, 'Sidoregel')
    sr = f.bodies.item(0); sr.name = 'Sidoregel höger'
    m = mirror(comp, [sr], comp.yZConstructionPlane, 'Sidoregel vänster (spegling)'); m[-1].name = 'Sidoregel vänster'
    for b in comp.bRepBodies: b.appearance = tra(des)
    comp.partNumber = 'VH-NOCK-SIDO'; comp.description = 'Nockregel 45x120, sidoreglar 34x145'
    for s in comp.sketches: s.isVisible = False


def run(_context: str):
    import time
    keepalive()
    d = find_doc(TOPPNAMN)
    if d: d.close(False)
    d = app.documents.open(dfile(TOPPNAMN)); d.activate()
    des = adsk.fusion.Design.cast(d.products.itemByProductType('DesignProductType'))
    root = des.rootComponent; up = des.userParameters
    for n, e, u, c in NYA:
        p = up.itemByName(n)
        if p: p.expression = e
        else: up.add(n, VI(e), u, c).isFavorite = True
    for k, v in ANDRA.items(): up.itemByName(k).expression = v
    for k, v in ANDRA_KOMMENTAR.items(): up.itemByName(k).comment = v
    des.computeAll()
    log('Bagavstand', up.itemByName('Bagavstand').expression, 'AntalBagar', up.itemByName('AntalBagar').value, 'BagCC', round(up.itemByName('BagCC').value * 10), 'NockOK', round(up.itemByName('NockOK').value * 10, 1))
    for o in list(root.occurrences):
        if o.component.name in ('Syllram', 'Nock och sidoreglar'): o.deleteMe(); log('tog bort gammal', o.name)
    I = adsk.core.Matrix3D.create()
    oS = root.occurrences.addNewComponent(I); oS.component.name = 'Syllram'
    bygg_syll(des, oS.component); oS.isGrounded = True
    oN = root.occurrences.addNewComponent(I); oN.component.name = 'Nock och sidoreglar'
    bygg_nock(des, oN.component); oN.isGrounded = True
    gom(des)
    for c in (oS.component, oN.component):
        log(c.name, [(b.name, [round(v) for v in bbmm(b)]) for b in c.bRepBodies])
    alla = [kontroll(des, root, 'standard 1250')]
    L = up.itemByName('Langd').value * 10; nk = up.itemByName('NockOK').value * 10
    os.makedirs(OUT, exist_ok=True)
    bild('v04_dummy.png', (9000, -6000, 6000), (0, L / 2, 1800), 9500)
    bild('v04_iso.png', (9000, -6000, 6000), (0, L / 2, 1800), 9500)
    bild('v04_gavel.png', (0, -12000, 1800), (0, 0, 1800), 5200)
    bild('v04_hörn_syll.png', (3200, -1400, 900), (2000, 0, 150), 1300)
    bild('v04_sidoregel.png', (3200, 900, 2500), (1700, 1250, 1850), 1500)
    bild('v04_nock.png', (900, -900, nk + 500), (0, 600, nk - 60), 1200)
    orig = {k: up.itemByName(k).expression for k in FLEX}
    try:
        for k, v in FLEX.items(): up.itemByName(k).expression = v
        alla.append(kontroll(des, root, 'flex ' + json.dumps(FLEX, ensure_ascii=False)))
        bild('v04_flex_iso.png', (10000, -6000, 6500), (0, 6000, 2000), 11000)
    finally:
        for k, v in orig.items(): up.itemByName(k).expression = v
    alla.append(kontroll(des, root, 'återställt'))
    json.dump(alla, open(os.path.expanduser('~/code/buttercup/vaxthus/fusion/v04_resultat.json'), 'w'), ensure_ascii=False, indent=1)
    try: os.remove(OUT + 'v04_dummy.png')
    except Exception: pass
    a0, a2 = alla[0], alla[-1]
    if a2['fel'] or a2['antal_krock'] or a2['ej_last'] or a2['remsor_mm'] != a0['remsor_mm'] or a2['kroppar_totalt'] != a0['kroppar_totalt'] or alla[1]['fel'] or alla[1]['ej_last']:
        raise Exception('kontroll underkänd, sparar inte')
    d.save('Steg 4: bågavstånd 1250, SkivaL 2500, Syllram + Nock och sidoreglar; flextest OK')
    log('sparad', TOPPNAMN)
