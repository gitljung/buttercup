# Steg 11: nock för filmen (Hugo: två våder 4,5 m + plåt i nocken) i komponenten "Nockprofil och nockplåt":
#  - Låsprofil nock: alu U ProfilB x ProfilH x ProfilT ovanpå nockregeln, öppning uppåt, hela längden. Båda takvåderna låses här.
#  - Nockplåt: bockad plåt NockPlatT, bredd NockPlatB, följer bågformen NockPlatSpel ovanför profilen (höger halva + spegling, sammanfogad).
#  Hanbjälke behövs inte (beräknat 20 m/s utan hanbjälke: max 0,87). Nocken är ledad i beräkningen = nuvarande vinklar + nockregel.
#  Skriver v11_antal.json (skruv-/inköpslista) och STEP-export av hela huset.
exec(open(os.path.expanduser('~/code/buttercup/vaxthus/fusion/v09_lasprofil.py')).read().split('\ndef run(')[0])
NYA11 = [
    ('NockPlatB', '300 mm', 'mm', 'Nockplåt: bredd (mätt horisontellt, total)'),
    ('NockPlatT', '0.6 mm', 'mm', 'Nockplåt: tjocklek (förzinkad/lackerad stålplåt)'),
    ('NockPlatSpel', '2 mm', 'mm', 'Nockplåt: spel över nockprofilen (radiellt)'),
]


def band_x(D, comp, rin, rout, xexpr, name, full=False):
    """bågband (höger halva) mellan radierna rin och rout (uttryck), från x = 0 (nocken) till x = xexpr"""
    ev = D.ev
    R = ev('BagR'); cx = -ev('BagCx'); cz = ev('BagCz'); SH = ev('SyllH')
    pt = lambda rr, th: (cx + rr * math.cos(th), 0.0, cz + rr * math.sin(th))
    sk = comp.sketches.add(comp.xZConstructionPlane); sk.name = name
    o = sk.originPoint; gc = sk.geometricConstraints; LS = sk.sketchCurves.sketchLines
    Q = lambda p: SP(sk, *p)
    tF = math.asin((SH - cz) / R); tN = math.atan2(ev('Nockhojd') - cz, -cx)
    a = sk.sketchCurves.sketchArcs.addByThreePoints(Q(pt(R, tF)), Q(pt(R, (tF + tN) / 2)), Q(pt(R, tN)))
    a.isConstruction = True
    ps, pe = a.startSketchPoint, a.endSketchPoint
    pF, pN = (ps, pe) if ps.geometry.distanceTo(Q(pt(R, tF))) < pe.geometry.distanceTo(Q(pt(R, tF))) else (pe, ps)
    zax = proj_axis(sk, comp, 'z')
    dimx(sk, o, pF, 'x', 'HalvBredd', (ev('HalvBredd') / 2, 0, SH - 150))
    dimx(sk, o, pF, 'z', 'SyllH', (ev('HalvBredd') + 150, 0, SH / 2))
    gc.addCoincident(pN, zax)
    dimx(sk, o, pN, 'z', 'Nockhojd', (-200, 0, ev('Nockhojd') / 2))
    sk.sketchDimensions.addRadialDimension(a, Q(pt(R * 0.9, 0.9))).parameter.expression = 'BagR'
    C0 = a.centerSketchPoint
    r1, r2 = ev(rin), ev(rout); X = ev(xexpr)
    zx = lambda r, x: cz + math.sqrt(r * r - (x - cx) ** 2)
    L0 = LS.addByTwoPoints(Q((0, 0, zx(r1, 0))), Q((0, 0, zx(r2, 0))))
    LX = LS.addByTwoPoints(Q((X, 0, zx(r1, X))), Q((X, 0, zx(r2, X))))
    for r, p0, p1 in ((r1, L0.startSketchPoint, LX.startSketchPoint), (r2, L0.endSketchPoint, LX.endSketchPoint)):
        xm = X / 2
        ar = sk.sketchCurves.sketchArcs.addByThreePoints(p0, Q((xm, 0, zx(r, xm))), p1)
        gc.addCoincident(ar.centerSketchPoint, C0)
        sk.sketchDimensions.addRadialDimension(ar, Q((xm * 0.8, 0, zx(r, xm) - 30))).parameter.expression = rin if r == r1 else rout
    along(sk, L0, 'z'); along(sk, LX, 'z')
    gc.addCoincident(L0.startSketchPoint, zax)
    dimx(sk, o, LX.startSketchPoint, 'x', xexpr, (X / 2, 0, zx(r1, X) - 60))
    if full:   # vänster halva i samma skiss: speglade ändpunkter, bågar med samma radier -> ett extrude = en kropp
        LXm = LS.addByTwoPoints(Q((-X, 0, zx(r1, X))), Q((-X, 0, zx(r2, X))))
        gc.addSymmetry(LXm.startSketchPoint, LX.startSketchPoint, zax); gc.addSymmetry(LXm.endSketchPoint, LX.endSketchPoint, zax)
        for r, p0, p1 in ((r1, L0.startSketchPoint, LXm.startSketchPoint), (r2, L0.endSketchPoint, LXm.endSketchPoint)):
            xm = X / 2
            ar = sk.sketchCurves.sketchArcs.addByThreePoints(p0, Q((-xm, 0, zx(r, xm))), p1)
            sk.sketchDimensions.addRadialDimension(ar, Q((-xm * 0.8, 0, zx(r, xm) - 30))).parameter.expression = rin if r == r1 else rout
    log(name, 'låst', sk.isFullyConstrained, free_report(sk)[:6], 'profiler', sk.profiles.count)
    if not sk.isFullyConstrained: raise Exception('ej låst: ' + name)
    if full: return coll([sk.profiles.item(i) for i in range(sk.profiles.count)])
    return min([sk.profiles.item(i) for i in range(sk.profiles.count)], key=lambda p: p.areaProperties().area)


def bygg_nock(des, comp):
    D = K(des, comp); ev = D.ev
    T, PB, PH, nok = ev('ProfilT'), ev('ProfilB'), ev('ProfilH'), ev('NockOK')
    bb2 = ev('BagB') / 2
    # 1. låsprofil på nockregeln (U, öppning uppåt, centrerad)
    sk = comp.sketches.add(comp.xZConstructionPlane); sk.name = 'Skiss Låsprofil nock'
    S = Skiss(D, sk, 'x', 'z')
    h, ht = PB / 2, PB / 2 - T
    eh, eht = 'ProfilB / 2', 'ProfilB / 2 - ProfilT'
    pts = [(-h, nok, eh, 'NockOK'), (h, nok, eh, 'NockOK'), (h, nok + PH, eh, 'NockOK + ProfilH'), (ht, nok + PH, eht, 'NockOK + ProfilH'),
           (ht, nok + T, eht, 'NockOK + ProfilT'), (-ht, nok + T, eht, 'NockOK + ProfilT'), (-ht, nok + PH, eht, 'NockOK + ProfilH'), (-h, nok + PH, eh, 'NockOK + ProfilH')]
    S.poly(pts); log(S.report())
    if not S.report()[1]: raise Exception('ej låst nockprofil')
    f = D.ext(S.biggest(), 'y', 'BagB / 2', 'Langd + BagB', -bb2, 'Låsprofil nock')
    pb = f.bodies.item(0); pb.name = 'Låsprofil nock'
    pb.appearance = appearance(des, 'Aluminium (låsprofil)', 'Paint - Metallic (Silver)', (190, 194, 198))
    # 2. nockplåt (höger halva + spegling, sammanfogad)
    r0 = 'BagR + BagDjup / 2 + ProfilH + NockPlatSpel'
    f = D.ext(band_x(D, comp, r0, r0 + ' + NockPlatT', 'NockPlatB / 2', 'Skiss Nockplåt', full=True), 'y', 'BagB / 2', 'Langd + BagB', -bb2, 'Nockplåt')
    nb = [b for b in comp.bRepBodies if b != pb]
    log('nockplåt kroppar', len(nb), [bbmm(b) for b in nb])
    if len(nb) != 1: raise Exception('nockplåten blev inte en kropp')
    nb[0].name = 'Nockplåt'
    nb[0].appearance = appearance(des, 'Plåt (nock)', 'Paint - Metallic (Dark Grey)', (120, 124, 128))
    comp.partNumber = 'VH-NOCKPLAT'; comp.description = 'Låsprofil nock (alu U 32x13) + nockplåt 0,6 mm bockad efter bågen'
    for s in comp.sketches: s.isVisible = False


def run(_context: str):
    global FLEXMODE
    keepalive()
    d = find_doc(TOPPNAMN)
    if d: d.close(False)
    d = app.documents.open(dfile(TOPPNAMN)); d.activate()
    des = adsk.fusion.Design.cast(d.products.itemByProductType('DesignProductType'))
    root = des.rootComponent; up = des.userParameters
    ev = lambda s: des.unitsManager.evaluateExpression(s, 'mm') * 10
    for n, e, u, c in NYA11:
        p = up.itemByName(n)
        if p: p.expression = e
        else: up.add(n, VI(e), u, c).isFavorite = True
    for o in list(root.occurrences):
        if o.component.name == 'Nockprofil och nockplåt': o.deleteMe()
    o = root.occurrences.addNewComponent(adsk.core.Matrix3D.create()); o.component.name = 'Nockprofil och nockplåt'
    bygg_nock(des, o.component); o.isGrounded = True
    des.computeAll()
    # antal + längder för listorna
    lg = langder(des, des.allComponents.itemByName('Låsprofiler'), ev)
    lg['Låsprofil nock'] = [round(ev('Langd + BagB'))]
    def pval(k):
        q = up.itemByName(k)
        return round(q.value, 3) if q.unit == '' else round(ev(k), 1)
    pv = {k: pval(k) for k in ('Bredd', 'Langd', 'Nockhojd', 'BagR', 'BagDjup', 'BagLangd', 'AntalBagar', 'BagCC', 'NedreMellan', 'OvreMellan',
                               'DorrBredd', 'DorrHojd', 'StolpeB', 'SyllUtstick', 'ProfilL', 'ProfilSkruvCC', 'FilmOverlapp', 'BagB',
                               'PlyT', 'Lameller', 'LamellT', 'KlossH', 'KlossL', 'FackKlossL', 'SidoregelT', 'SidoregelH', 'NockT', 'NockH',
                               'SyllB', 'SyllH', 'SkivaL', 'NockPlatB', 'NockPlatT', 'HalvBredd')}
    gom(des)
    FLEXMODE = False
    alla = [kontroll(des, root, 'standard')]
    json.dump({'parametrar': pv, 'lasprofil_mm': lg, 'antal': antal_alla(des), 'remsor_mm': alla[0]['remsor_mm']},
              open(os.path.expanduser('~/code/buttercup/vaxthus/fusion/v11_antal.json'), 'w'), ensure_ascii=False, indent=1)
    L = ev('Langd'); hb = ev('HalvBredd'); nk = ev('NockOK')
    bild('v11_dummy.png', (7000, -7000, 4500), (0, L / 2, 1700), 9000)
    bild('v11_iso.png', (7000, -7000, 4500), (0, L / 2, 1700), 9000)
    bild('v11_nock.png', (700, 1250 - 1300, nk + 700), (0, 1250, nk - 50), 700)
    bild('v11_nock_gavel.png', (600, -1200, nk + 500), (0, 0, nk - 80), 800)
    bild('v11_gavel.png', (1200, -9000, 1900), (0, 0, 1800), 4800)
    bild('v11_inifran.png', (hb - 700, -600, 1500), (0, L / 2, 2200), 6000)
    orig = {k: up.itemByName(k).expression for k in FLEX}
    try:
        FLEXMODE = True
        for k, v in FLEX.items(): up.itemByName(k).expression = v
        alla.append(kontroll(des, root, 'flex (köpdelar ej omplacerade)'))
        bild('v11_flex.png', (8000, -8000, 5000), (0, 6000, 1900), 10500)
    finally:
        for k, v in orig.items(): up.itemByName(k).expression = v
        FLEXMODE = False
    alla.append(kontroll(des, root, 'återställt'))
    json.dump(alla, open(os.path.expanduser('~/code/buttercup/vaxthus/fusion/v11_resultat.json'), 'w'), ensure_ascii=False, indent=1)
    try: os.remove(OUT + 'v11_dummy.png')
    except Exception: pass
    a0, a1, a2 = alla
    if a0['antal_krock'] or a0['fel'] or a0['ej_last'] or a2['fel'] or a2['antal_krock'] or a2['ej_last'] or a2['kroppar_totalt'] != a0['kroppar_totalt'] or a1['fel'] or a1['ej_last'] or a1['antal_krock']:
        raise Exception('kontroll underkänd, sparar inte')
    d.save('Steg 11: nockprofil + nockplåt (film 2 våder), flextest OK')
    log('sparad', TOPPNAMN)
    try:
        sp = os.path.expanduser('~/code/buttercup/vaxthus/fusion/export/Vaxthus.step')
        os.makedirs(os.path.dirname(sp), exist_ok=True)
        em = des.exportManager
        ok = em.execute(em.createSTEPExportOptions(sp, root))
        log('STEP', ok, sp, os.path.getsize(sp) if os.path.exists(sp) else 0)
    except Exception as e:
        log('STEP FEL', str(e)[:200])
