# Steg 2: detaljfil "Växthus - halvbåge" (höger halvbåge, x > 0, i bågplanet y = 0).
# Allt styrs av masterparametrarna via Derive (<namn>_Ref). Inga siffror i skisserna.
#  - Skiss "Bågform": mittlinjens båge (konstruktion) genom foten och nocken med radie BagR,
#    fyra koncentriska bågar = remsornas ytor, fotlinjer (syllens ovansida) och nocklinjer (mot nockregeln).
#  - Remsor: ytter- och innerremsa (PlyT), extruderade symmetriskt BagB, delade i skarvplanen.
#  - Klossar: fotkloss, nedre/övre fackkloss (bär skarvarna), nockkloss + två cirkulära mönster av vanliga klossar.
#  - Laskar: 15 mm plywood på remsornas utsida över skarvarna.
# Vinklar längs bågen = (mått längs mittlinjen) / BagR * 1 rad, mätt från linjen centrum -> foten.
NAMN = 'Växthus - halvbåge'
LOGF = os.path.expanduser('~/code/buttercup/vaxthus/fusion/v02_resultat.json')


def run(_context: str):
    gammal = dfile(NAMN)          # ombygge: egen fil från tidigare försök raderas först
    if gammal:
        for x in list(app.documents):
            try:
                if bas(x.name) == NAMN: x.close(False)
            except Exception: pass
        gammal.deleteMe(); log('raderade gammal', NAMN)
        import time
        for _ in range(10):
            if not dfile(NAMN): break
            time.sleep(2); adsk.doEvents()
    D = Del(NAMN)
    r, des = D.r, D.des
    E, ev = D.E, D.ev
    gcons = lambda sk: sk.geometricConstraints
    R = ev('BagR'); cx = -ev('BagCx'); cz = ev('BagCz'); SH = ev('SyllH'); NT2 = ev('NockT') / 2
    H2 = ev('BagDjup') / 2; K2 = ev('KlossH') / 2; PT = ev('PlyT')
    f0 = math.asin(ev('Spetsighet') / R)

    def pt(rr, th):
        return (cx + rr * math.cos(th), 0.0, cz + rr * math.sin(th))

    def th_foot(rr):
        return math.asin((SH - cz) / rr)

    def th_nock(rr):
        return math.acos((NT2 - cx) / rr)

    def ang(s):  # vinkel (rad, absolut) för mått s längs mittlinjen
        return f0 + s / R

    def mk_arc(sk, rr, t0, t1):
        a = sk.sketchCurves.sketchArcs.addByThreePoints(SP(sk, *pt(rr, t0)), SP(sk, *pt(rr, (t0 + t1) / 2)), SP(sk, *pt(rr, t1)))
        p0 = SP(sk, *pt(rr, t0))
        s, e = a.startSketchPoint, a.endSketchPoint
        return (a, s, e) if s.geometry.distanceTo(p0) < e.geometry.distanceTo(p0) else (a, e, s)

    def rad_dim(sk, arc, expr, rr, th):
        d = sk.sketchDimensions.addRadialDimension(arc, SP(sk, *pt(rr * 0.9, th)))
        d.parameter.expression = E(expr); return d

    # ---------- Bågform ----------
    sk = r.sketches.add(r.xZConstructionPlane); sk.name = 'Bågform'
    o = sk.originPoint; gc = gcons(sk)
    zax = proj_axis(sk, r, 'z')
    tN = math.atan2(ev('BagHojd') + ev('Spetsighet') - 0, 0 - cx)  # mittlinjen vid x = 0
    tN = math.atan2(ev('Nockhojd') - cz, -cx)
    Am, AmF, AmN = mk_arc(sk, R, th_foot(R), tN)
    Am.isConstruction = True
    dimx(sk, o, AmF, 'x', E('HalvBredd'), (ev('HalvBredd') / 2, 0, SH - 150))
    dimx(sk, o, AmF, 'z', E('SyllH'), (ev('HalvBredd') + 150, 0, SH / 2))
    gc.addCoincident(AmN, zax)
    dimx(sk, o, AmN, 'z', E('Nockhojd'), (-200, 0, ev('Nockhojd') / 2))
    rad_dim(sk, Am, 'BagR', R, 0.9)
    C0 = Am.centerSketchPoint
    radii = [('BagR + BagDjup / 2', R + H2), ('BagR + KlossH / 2', R + K2), ('BagR - KlossH / 2', R - K2), ('BagR - BagDjup / 2', R - H2)]
    A = []
    for k, (ex, rr) in enumerate(radii):
        a, pf, pn = mk_arc(sk, rr, th_foot(rr), th_nock(rr))
        gc.addCoincident(a.centerSketchPoint, C0)
        rad_dim(sk, a, ex, rr, 0.5 + 0.1 * k)
        A.append((a, pf, pn))
    LS = sk.sketchCurves.sketchLines
    for (i, j, nm) in ((1, 0, 'ytter'), (3, 2, 'inner')):
        lf = LS.addByTwoPoints(A[i][1], A[j][1]); along(sk, lf, 'x')
        dimx(sk, o, A[i][1], 'z', E('SyllH'), (pt(R, 0)[0] + 60 * (i + 1), 0, SH / 2))
        ln = LS.addByTwoPoints(A[i][2], A[j][2]); along(sk, ln, 'z')
        dimx(sk, o, A[i][2], 'x', E('NockT / 2'), (NT2 / 2, 0, pt(R, th_nock(R))[2] + 60 * (i + 1)))
    log('Bågform låst', sk.isFullyConstrained, free_report(sk)[:6])

    def prof_near(sk_, p):
        q = SP(sk_, *p); best = None
        for i in range(sk_.profiles.count):
            pr = sk_.profiles.item(i)
            d = pr.areaProperties().centroid.distanceTo(q)
            if best is None or d < best[0]: best = (d, pr)
        return best[1]

    def ext_sym(prof, name):
        inp = D.ef.createInput(prof, NEWB)
        inp.setSymmetricExtent(VI(E('BagB')), True)
        f = D.ef.add(inp); f.name = name
        return f.bodies.item(0)

    def prof_band(sk_, r0, r1):
        # bågformade band: tyngdpunkten ligger utanför bandet -> välj på bbox
        pts = [SP(sk_, *pt(rr, th_foot(rr) + (th_nock(rr) - th_foot(rr)) * k / 20)) for rr in (r0, r1) for k in range(21)]
        ex = [min(q.x for q in pts), min(q.y for q in pts), max(q.x for q in pts), max(q.y for q in pts)]
        best = None
        for i in range(sk_.profiles.count):
            pr = sk_.profiles.item(i); bb = pr.boundingBox
            d = sum(abs(a - b) for a, b in zip(ex, [bb.minPoint.x, bb.minPoint.y, bb.maxPoint.x, bb.maxPoint.y]))
            if best is None or d < best[0]: best = (d, pr)
        log('band', round(best[0] * 10, 2), 'mm bbox-avvikelse')
        return best[1]
    ytter = ext_sym(prof_band(sk, R + K2, R + H2), 'Ytterremsa')
    inner = ext_sym(prof_band(sk, R - H2, R - K2), 'Innerremsa')
    ytter.name = 'Ytterremsa'; inner.name = 'Innerremsa'

    # ---------- hjälpskiss-funktioner för radiella linjer ----------
    def ref_sketch(name, proj):
        s2 = r.sketches.add(r.xZConstructionPlane); s2.name = name
        pa = s2.project(Am).item(0); pa.isConstruction = True
        cc = pa.centerSketchPoint
        ps, pe = pa.startSketchPoint, pa.endSketchPoint
        pF = ps if ps.geometry.distanceTo(SP(s2, *pt(R, th_foot(R)))) < pe.geometry.distanceTo(SP(s2, *pt(R, th_foot(R)))) else pe
        refl = s2.sketchCurves.sketchLines.addByTwoPoints(cc, pF); refl.isConstruction = True
        pc = {k: s2.project(A[k][0]).item(0) for k in proj}
        return s2, cc, refl, pc

    def radial(s2, cc, refl, s_expr, s_val, onto, rr, construction=False):
        th = ang(s_val)
        l = s2.sketchCurves.sketchLines.addByTwoPoints(cc, SP(s2, *pt(rr, th)))
        gcons(s2).addCoincident(l.endSketchPoint, onto)
        dd = s2.sketchDimensions.addAngularDimension(refl, l, SP(s2, *pt(R * 0.35, (f0 + th) / 2 if th - f0 > 0.02 else th + 0.02)))
        dd.parameter.expression = E('( %s ) / BagR * 1 rad' % s_expr)
        if construction: l.isConstruction = True
        return l

    def cap(s2, kind, pc_in, pc_out):
        """fotlinje (z = SyllH) eller nocklinje (x = NockT/2) mellan två projicerade bågar"""
        if kind == 'fot':
            a = SP(s2, *pt(R - K2, th_foot(R - K2))); b = SP(s2, *pt(R + K2, th_foot(R + K2)))
        else:
            a = SP(s2, *pt(R - K2, th_nock(R - K2))); b = SP(s2, *pt(R + K2, th_nock(R + K2)))
        l = s2.sketchCurves.sketchLines.addByTwoPoints(a, b)
        g = gcons(s2); g.addCoincident(l.startSketchPoint, pc_in); g.addCoincident(l.endSketchPoint, pc_out)
        if kind == 'fot':
            along(s2, l, 'x'); dimx(s2, s2.originPoint, l.startSketchPoint, 'z', E('SyllH'), (pt(R, 0)[0], 0, SH / 2))
        else:
            along(s2, l, 'z'); dimx(s2, s2.originPoint, l.startSketchPoint, 'x', E('NockT / 2'), (NT2 / 2, 0, pt(R, th_nock(R))[2] + 100))
        return l

    def kloss(name, lo, hi):
        """lo/hi = ('fot'|'nock'|(uttryck, värde)) längs mittlinjen"""
        s2, cc, refl, pc = ref_sketch('Skiss ' + name, (1, 2))
        for e in (lo, hi):
            if isinstance(e, str): cap(s2, e, pc[2], pc[1])
            else: radial(s2, cc, refl, e[0], e[1], pc[1], R + K2)
        log(name, 'låst', s2.isFullyConstrained, free_report(s2)[:4])
        sv = lambda e: 0 if e == 'fot' else (ev('BagLangd') if e == 'nock' else e[1])
        exp = pt(R, ang((sv(lo) + sv(hi)) / 2))
        b = ext_sym(prof_near(s2, exp), name)
        bb = b.boundingBox
        got = ((bb.minPoint.x + bb.maxPoint.x) * 5, (bb.minPoint.z + bb.maxPoint.z) * 5)
        if abs(got[0] - exp[0]) > 40 or abs(got[1] - exp[2]) > 40:
            raise Exception('%s hamnar fel: %s, väntat %s' % (name, got, (exp[0], exp[2])))
        b.name = name; return b

    BL = ev('BagLangd')
    S = {k: ev(k) for k in ('FotKlossS', 'FackNedreS', 'FackOvreS', 'NockKlossS', 'NedrePitch', 'OvrePitch', 'KlossL', 'FackKlossL', 'SkarvYtterS', 'SkarvInnerS', 'LaskL')}
    KL, FL = S['KlossL'], S['FackKlossL']
    klossar = []
    klossar.append(kloss('Fotkloss', 'fot', ('KlossL', KL)))
    n0 = S['FotKlossS'] + S['NedrePitch']
    klossar.append(kloss('Kloss nedre 1', ('FotKlossS + NedrePitch - KlossL / 2', n0 - KL / 2), ('FotKlossS + NedrePitch + KlossL / 2', n0 + KL / 2)))
    klossar.append(kloss('Fackkloss nedre', ('FackNedreS - FackKlossL / 2', S['FackNedreS'] - FL / 2), ('FackNedreS + FackKlossL / 2', S['FackNedreS'] + FL / 2)))
    klossar.append(kloss('Fackkloss övre', ('FackOvreS - FackKlossL / 2', S['FackOvreS'] - FL / 2), ('FackOvreS + FackKlossL / 2', S['FackOvreS'] + FL / 2)))
    o0 = S['FackOvreS'] + (FL - KL) / 2 + S['OvrePitch']
    klossar.append(kloss('Kloss övre 1', ('FackOvreS + ( FackKlossL - KlossL ) / 2 + OvrePitch - KlossL / 2', o0 - KL / 2), ('FackOvreS + ( FackKlossL - KlossL ) / 2 + OvrePitch + KlossL / 2', o0 + KL / 2)))
    klossar.append(kloss('Nockkloss', ('BagLangd - KlossL', BL - KL), 'nock'))

    # ---------- bågens centrumaxel (för mönstren) ----------
    pi = r.constructionPlanes.createInput(); pi.setByOffset(r.xZConstructionPlane, VI(E('BagB / 2'))); pl = r.constructionPlanes.add(pi); pl.name = 'Hjälpplan bågcentrum'
    s3 = r.sketches.add(pl); s3.name = 'Bågcentrum (hjälp)'
    c2 = s3.project(C0).item(0)
    ai = r.constructionAxes.createInput(); ai.setByTwoPoints(C0, c2); axis = r.constructionAxes.add(ai); axis.name = 'Bågens centrumaxel'

    def pattern(seed, qty, step_expr, step_val, s_first, name):
        n = int(round(des.allParameters.itemByName(E(qty)).value))
        if n < 2:
            log(name, 'bara en kloss, inget mönster'); return []
        cp = r.features.circularPatternFeatures
        for sg in ('', '-'):
            inp = cp.createInput(coll([seed]), axis)
            inp.quantity = VI(E(qty))
            inp.totalAngle = VI(sg + '( ' + E('( %s - 1 ) * ( %s ) / BagR * 1 rad' % (qty, step_expr)) + ' )')
            inp.isSymmetric = False
            f = cp.add(inp)
            last = [f.bodies.item(i) for i in range(f.bodies.count)]
            exp = pt(R, ang(s_first + (n - 1) * step_val))
            ok = any(abs((b.boundingBox.minPoint.x + b.boundingBox.maxPoint.x) * 5 - exp[0]) < 30 and abs((b.boundingBox.minPoint.z + b.boundingBox.maxPoint.z) * 5 - exp[2]) < 30 for b in last)
            if ok:
                f.name = name
                bs = [b for b in last if b.entityToken != seed.entityToken]
                return bs
            f.deleteMe()
        raise Exception('mönstret hamnar fel: ' + name)

    nedre = pattern(klossar[1], 'NedreMellan', 'NedrePitch', S['NedrePitch'], n0, 'Klossar nedre (mönster)')
    ovre = pattern(klossar[4], 'OvreMellan', 'OvrePitch', S['OvrePitch'], o0, 'Klossar övre (mönster)')
    for k, b in enumerate(nedre): b.name = 'Kloss nedre %d' % (k + 2)
    for k, b in enumerate(ovre): b.name = 'Kloss övre %d' % (k + 2)

    # ---------- skarvar ----------
    s4, cc4, ref4, pc4 = ref_sketch('Skarvplan', (0, 3))
    ly = radial(s4, cc4, ref4, 'SkarvYtterS', S['SkarvYtterS'], pc4[0], R + H2, construction=True)
    li = radial(s4, cc4, ref4, 'SkarvInnerS', S['SkarvInnerS'], pc4[0], R + H2, construction=True)
    log('Skarvplan låst', s4.isFullyConstrained, free_report(s4)[:4])
    sb = r.features.splitBodyFeatures
    delar = {}
    for body, line, nm, sv in ((ytter, ly, 'Ytterremsa', S['SkarvYtterS']), (inner, li, 'Innerremsa', S['SkarvInnerS'])):
        pi = r.constructionPlanes.createInput(); pi.setByAngle(line, VI('90 deg'), r.xZConstructionPlane)
        pp = r.constructionPlanes.add(pi); pp.name = 'Skarvplan ' + nm.lower()[:-1]
        f = sb.add(sb.createInput(body, pp, True)); f.name = 'Skarv ' + nm.lower()
        bs = sorted([f.bodies.item(i) for i in range(f.bodies.count)], key=lambda b: b.boundingBox.minPoint.z)
        for k, b in enumerate(bs): b.name = '%s %d' % (nm, k + 1)
        delar[nm] = bs

    # ---------- laskar ----------
    def lask(name, s_expr, s_val, outer):
        s5, cc5, ref5, pc5 = ref_sketch('Skiss ' + name, (0, 3))
        g = gcons(s5)
        if outer:
            rr, base = R + H2 + PT, pc5[0]
            l1 = radial(s5, cc5, ref5, '%s - LaskL / 2' % s_expr, s_val - S['LaskL'] / 2, pc5[0], R + H2)
            l2 = radial(s5, cc5, ref5, '%s + LaskL / 2' % s_expr, s_val + S['LaskL'] / 2, pc5[0], R + H2)
            # linjerna slutar på ytterremsans yta; förläng med bågen utanför
            t1, t2 = ang(s_val - S['LaskL'] / 2), ang(s_val + S['LaskL'] / 2)
            a, p1, p2 = mk_arc(s5, rr, t1, t2)
            g.addCoincident(a.centerSketchPoint, cc5)
            m1 = s5.sketchCurves.sketchLines.addByTwoPoints(l1.endSketchPoint, p1)
            m2 = s5.sketchCurves.sketchLines.addByTwoPoints(l2.endSketchPoint, p2)
            g.addCollinear(m1, l1); g.addCollinear(m2, l2)
            rad_dim(s5, a, 'BagR + BagDjup / 2 + PlyT', rr, t1)
        else:
            rr = R - H2 - PT
            l1 = radial(s5, cc5, ref5, '%s - LaskL / 2' % s_expr, s_val - S['LaskL'] / 2, pc5[3], R - H2)
            l2 = radial(s5, cc5, ref5, '%s + LaskL / 2' % s_expr, s_val + S['LaskL'] / 2, pc5[3], R - H2)
            t1, t2 = ang(s_val - S['LaskL'] / 2), ang(s_val + S['LaskL'] / 2)
            a, p1, p2 = mk_arc(s5, rr, t1, t2)
            g.addCoincident(a.centerSketchPoint, cc5); g.addCoincident(p1, l1); g.addCoincident(p2, l2)
            rad_dim(s5, a, 'BagR - BagDjup / 2 - PlyT', rr, t1)
        log(name, 'låst', s5.isFullyConstrained, free_report(s5)[:4])
        b = ext_sym(prof_near(s5, pt(rr - PT / 2 if outer else rr + PT / 2, ang(s_val))), name)
        b.name = name; return b
    laskar = [lask('Lask ytter', 'SkarvYtterS', S['SkarvYtterS'], True), lask('Lask inner', 'SkarvInnerS', S['SkarvInnerS'], False)]

    # ---------- utseende, kontroll ----------
    for b in r.bRepBodies:
        b.appearance = plywood(des) if (b.name.startswith('Ytter') or b.name.startswith('Inner') or b.name.startswith('Lask')) else tra(des)
    r.partNumber = 'VH-HALVBAGE'; r.description = 'Halvbåge, stegbåge 15 mm plywood + klossar 70x70'
    des.computeAll()
    tl = des.timeline
    fel = [(tl.item(i).name, tl.item(i).errorOrWarningMessage[:80]) for i in range(tl.count) if tl.item(i).healthState != 0]
    ej = [(s.name, free_report(s)[:3]) for s in r.sketches if not s.isFullyConstrained]
    tb = adsk.fusion.TemporaryBRepManager.get()
    bl = [b for b in r.bRepBodies]
    krock = []
    for i in range(len(bl)):
        for j in range(i + 1, len(bl)):
            x = tb.copy(bl[i]); y = tb.copy(bl[j])
            try:
                tb.booleanOperation(x, y, adsk.fusion.BooleanTypes.IntersectionBooleanType)
                v = x.volume * 1000
            except Exception: v = 0
            if v > 1: krock.append((bl[i].name, bl[j].name, round(v)))
    kroppar = []
    for b in bl:
        it = {'namn': b.name, 'bbox': bbmm(b), 'vol_cm3': round(b.volume, 1)}
        if b.name.startswith(('Ytter', 'Inner', 'Lask')):
            it['langd_mm'] = round(b.volume * 1000 / (ev('PlyT') * ev('BagB')))
        elif b.name.startswith(('Kloss', 'Fot', 'Fack', 'Nock')):
            it['langd_mm'] = round(b.volume * 1000 / (ev('KlossH') * ev('BagB')))
        kroppar.append(it)
    langa = [(k['namn'], k['langd_mm']) for k in kroppar if k['namn'].startswith(('Ytter', 'Inner')) and k['langd_mm'] > ev('SkivaL')]
    res = {'kroppar': len(bl), 'tidslinje': tl.count, 'fel': fel, 'ej_last': ej, 'krock': krock, 'for_langa_remsor': langa, 'lista': kroppar}
    json.dump(res, open(LOGF, 'w'), ensure_ascii=False, indent=1)
    log(json.dumps({k: v for k, v in res.items() if k != 'lista'}, ensure_ascii=False))
    for k in kroppar: log(k['namn'], k.get('langd_mm'), k['bbox'])
    if fel: raise Exception('tidslinjefel, sparar inte')

    # ---------- bilder ----------
    vp = app.activeViewport
    def bild(fn, eye, target, ext):
        cam = vp.camera; cam.isSmoothTransition = False
        cam.target = P3(*[v / 10 for v in target]); cam.eye = P3(*[v / 10 for v in eye]); cam.upVector = adsk.core.Vector3D.create(0, 0, 1)
        cam.isFitView = False; cam.viewExtents = ext / 10
        vp.camera = cam; vp.camera = cam; vp.camera = cam; adsk.doEvents()
        vp.saveAsImageFile(OUT + fn, 1600, 1000)
    os.makedirs(OUT, exist_ok=True)
    mid = (ev('HalvBredd') / 2, 0, ev('Nockhojd') / 2)
    bild('v02_dummy.png', (mid[0], -10000, mid[2]), mid, 4500)
    bild('v02_halvbage_sida.png', (mid[0], -10000, mid[2]), mid, 4500)
    bild('v02_halvbage_iso.png', (mid[0] + 4000, -5000, mid[2] + 2500), mid, 4800)
    fk = pt(R, ang(ev('FackS')))
    bild('v02_fack_skarvar.png', (fk[0] + 700, -1000, fk[2] + 400), fk, 1100)
    ft = pt(R, ang(150))
    bild('v02_fot.png', (ft[0] + 500, -800, ft[2] + 200), ft, 700)
    nk = pt(R, th_nock(R))
    bild('v02_nock.png', (nk[0] + 500, -800, nk[2] + 200), nk, 700)
    try: os.remove(OUT + 'v02_dummy.png')
    except Exception: pass

    D.d.saveAs(NAMN, folder(), 'Steg 2: halvbåge (remsor, klossar, skarvar, laskar) helt parametrisk', '')
    log('sparad', NAMN)
