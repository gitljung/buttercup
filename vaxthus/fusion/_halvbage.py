# Halvbåge (höger, x > 0, bågplanet y = 0) byggd i komponenten D.r.
# ALLT i en skiss, "Bågform" (inga projektioner – de släpper vid omräkning):
#   - mittlinjens båge (konstruktion) genom foten och nocken, radie BagR, centrum C0
#   - fyra koncentriska bågar = remsornas ytor, fot- och nocklinjer
#   - radiella konstruktionslinjer från C0 med vinkel = (mått längs mittlinjen) / BagR, mätt från linjen C0 -> foten
#   - klosskanter och laskkanter = korta linjer kolinjära med de radiella linjerna
# Klossar: fotkloss, nedre/övre fackkloss (bär skarvarna), nockkloss + två mönster längs mittlinjen.
# D: objekt med r (komponent), des, E (namn -> parameternamn), ev (uttryck -> mm), ef (extrudeFeatures).


def bygg_halvbage(D):
    r, des = D.r, D.des
    E, ev = D.E, D.ev
    R = ev('BagR'); cx = -ev('BagCx'); cz = ev('BagCz'); SH = ev('SyllH'); NT2 = ev('NockT') / 2
    H2 = ev('BagDjup') / 2; K2 = ev('KlossH') / 2; PT = ev('PlyT')
    f0 = math.asin(ev('Spetsighet') / R)

    def pt(rr, th): return (cx + rr * math.cos(th), 0.0, cz + rr * math.sin(th))
    def th_foot(rr): return math.asin((SH - cz) / rr)
    def th_nock(rr): return math.acos((NT2 - cx) / rr)
    def ang(s): return f0 + s / R

    sk = r.sketches.add(r.xZConstructionPlane); sk.name = 'Bågform'
    o = sk.originPoint; gc = sk.geometricConstraints; LS = sk.sketchCurves.sketchLines
    Q = lambda p: SP(sk, *p)

    def mk_arc(rr, t0, t1):
        a = sk.sketchCurves.sketchArcs.addByThreePoints(Q(pt(rr, t0)), Q(pt(rr, (t0 + t1) / 2)), Q(pt(rr, t1)))
        p0 = Q(pt(rr, t0)); s, e = a.startSketchPoint, a.endSketchPoint
        return (a, s, e) if s.geometry.distanceTo(p0) < e.geometry.distanceTo(p0) else (a, e, s)

    def rad_dim(arc, expr, rr, th):
        sk.sketchDimensions.addRadialDimension(arc, Q(pt(rr * 0.9, th))).parameter.expression = E(expr)

    zax = proj_axis(sk, r, 'z')   # komponentens egen z-axel (origo-geometri, stabil)
    tN = math.atan2(ev('Nockhojd') - cz, -cx)
    Am, AmF, AmN = mk_arc(R, th_foot(R), tN); Am.isConstruction = True
    dimx(sk, o, AmF, 'x', E('HalvBredd'), (ev('HalvBredd') / 2, 0, SH - 150))
    dimx(sk, o, AmF, 'z', E('SyllH'), (ev('HalvBredd') + 150, 0, SH / 2))
    gc.addCoincident(AmN, zax)
    dimx(sk, o, AmN, 'z', E('Nockhojd'), (-200, 0, ev('Nockhojd') / 2))
    rad_dim(Am, 'BagR', R, 0.9)
    C0 = Am.centerSketchPoint
    radii = [('BagR + BagDjup / 2', R + H2), ('BagR + KlossH / 2', R + K2), ('BagR - KlossH / 2', R - K2), ('BagR - BagDjup / 2', R - H2)]
    A = []
    for k, (ex, rr) in enumerate(radii):
        a, pf, pn = mk_arc(rr, th_foot(rr), th_nock(rr))
        gc.addCoincident(a.centerSketchPoint, C0)
        rad_dim(a, ex, rr, 0.5 + 0.1 * k)
        A.append((a, pf, pn))
    for (i, j) in ((1, 0), (3, 2)):
        lf = LS.addByTwoPoints(A[i][1], A[j][1]); along(sk, lf, 'x')
        dimx(sk, o, A[i][1], 'z', E('SyllH'), (pt(R, 0)[0] + 60 * (i + 1), 0, SH / 2))
        ln = LS.addByTwoPoints(A[i][2], A[j][2]); along(sk, ln, 'z')
        dimx(sk, o, A[i][2], 'x', E('NockT / 2'), (NT2 / 2, 0, pt(R, th_nock(R))[2] + 60 * (i + 1)))
    LS.addByTwoPoints(A[2][1], A[1][1])   # fotkloss underkant (punkterna är redan låsta)
    LS.addByTwoPoints(A[2][2], A[1][2])   # nockkloss överkant
    ref = LS.addByTwoPoints(C0, AmF); ref.isConstruction = True
    log('Bågform grund låst', sk.isFullyConstrained, free_report(sk)[:6])

    def radial(s_expr, s_val, name):
        th = ang(s_val)
        l = LS.addByTwoPoints(C0, Q(pt(R + H2, th))); l.isConstruction = True
        gc.addCoincident(l.endSketchPoint, A[0][0])
        tp = (f0 + th) / 2 if th - f0 > 0.02 else th + 0.02
        dd = sk.sketchDimensions.addAngularDimension(ref, l, Q(pt(R * 0.35, tp)))
        dd.parameter.expression = E('( %s ) / BagR * 1 rad' % s_expr)
        return l

    def edge(rl, s_val, r_in, r_out, c_in, c_out, share=False):
        th = ang(s_val)
        if share:   # kanten börjar i den radiella linjens ändpunkt (på ytterremsans yta)
            e = LS.addByTwoPoints(rl.endSketchPoint, Q(pt(r_out, th)))
            try: gc.addCollinear(e, rl)
            except Exception: gc.addParallel(e, rl)
            return e
        e = LS.addByTwoPoints(Q(pt(r_in, th)), Q(pt(r_out, th)))
        if c_in is not None: gc.addCoincident(e.startSketchPoint, c_in)
        if c_out is not None: gc.addCoincident(e.endSketchPoint, c_out)
        gc.addCollinear(e, rl)
        return e

    def kant(s_expr, s_val, name):  # klosskant mellan A3 (R-K2) och A2 (R+K2)
        return edge(radial(s_expr, s_val, name), s_val, R - K2, R + K2, A[2][0], A[1][0])

    S = {k: ev(k) for k in ('FotKlossS', 'FackNedreS', 'FackOvreS', 'NockKlossS', 'NedrePitch', 'OvrePitch', 'KlossL', 'FackKlossL', 'SkarvYtterS', 'SkarvInnerS', 'LaskL', 'BagLangd')}
    KL, FL, BL = S['KlossL'], S['FackKlossL'], S['BagLangd']
    n0 = S['FotKlossS'] + S['NedrePitch']
    o0 = S['FackOvreS'] + (FL - KL) / 2 + S['OvrePitch']
    K = [  # namn, nedre kant (uttryck, värde) eller None = fotlinjen, övre kant eller None = nocklinjen
        ('Fotkloss', None, ('KlossL', KL)),
        ('Kloss nedre 1', ('FotKlossS + NedrePitch - KlossL / 2', n0 - KL / 2), ('FotKlossS + NedrePitch + KlossL / 2', n0 + KL / 2)),
        ('Fackkloss nedre', ('FackNedreS - FackKlossL / 2', S['FackNedreS'] - FL / 2), ('FackNedreS + FackKlossL / 2', S['FackNedreS'] + FL / 2)),
        ('Fackkloss övre', ('FackOvreS - FackKlossL / 2', S['FackOvreS'] - FL / 2), ('FackOvreS + FackKlossL / 2', S['FackOvreS'] + FL / 2)),
        ('Kloss övre 1', ('FackOvreS + ( FackKlossL - KlossL ) / 2 + OvrePitch - KlossL / 2', o0 - KL / 2), ('FackOvreS + ( FackKlossL - KlossL ) / 2 + OvrePitch + KlossL / 2', o0 + KL / 2)),
        ('Nockkloss', ('BagLangd - KlossL', BL - KL), None),
    ]
    for nm, lo, hi in K:
        for e_ in (lo, hi):
            if e_: kant(e_[0], e_[1], nm)
    ly = radial('SkarvYtterS', S['SkarvYtterS'], 'skarv ytter')
    li = radial('SkarvInnerS', S['SkarvInnerS'], 'skarv inner')

    def lask_skiss(s_expr, s_val, outer):
        LL = S['LaskL']
        r_face, r_l = (R + H2, R + H2 + PT) if outer else (R - H2, R - H2 - PT)
        face = A[0][0] if outer else A[3][0]
        es = []
        for sg in (-1, 1):
            rl = radial('%s %s LaskL / 2' % (s_expr, '-' if sg < 0 else '+'), s_val + sg * LL / 2, 'lask')
            es.append(edge(rl, s_val + sg * LL / 2, r_face, r_l, face, None, share=outer))
        t1, t2 = ang(s_val - LL / 2), ang(s_val + LL / 2)
        a = sk.sketchCurves.sketchArcs.addByThreePoints(es[0].endSketchPoint, Q(pt(r_l, (t1 + t2) / 2)), es[1].endSketchPoint)
        gc.addCoincident(a.centerSketchPoint, C0)
        rad_dim(a, 'BagR + BagDjup / 2 + PlyT' if outer else 'BagR - BagDjup / 2 - PlyT', r_l, t1)
    lask_skiss('SkarvYtterS', S['SkarvYtterS'], True)
    lask_skiss('SkarvInnerS', S['SkarvInnerS'], False)
    log('Bågform låst', sk.isFullyConstrained, free_report(sk)[:8])

    def prof_near(p):
        q = Q(p); best = None
        for i in range(sk.profiles.count):
            pr = sk.profiles.item(i); d = pr.areaProperties().centroid.distanceTo(q)
            if best is None or d < best[0]: best = (d, pr)
        return best[1]

    def prof_band(r0, r1):
        pts = [Q(pt(rr, th_foot(rr) + (th_nock(rr) - th_foot(rr)) * k / 20)) for rr in (r0, r1) for k in range(21)]
        ex = [min(q.x for q in pts), min(q.y for q in pts), max(q.x for q in pts), max(q.y for q in pts)]
        best = None
        for i in range(sk.profiles.count):
            pr = sk.profiles.item(i); bb = pr.boundingBox
            d = sum(abs(a - b) for a, b in zip(ex, [bb.minPoint.x, bb.minPoint.y, bb.maxPoint.x, bb.maxPoint.y]))
            if best is None or d < best[0]: best = (d, pr)
        log('band', round(best[0] * 10, 2), 'mm bbox-avvikelse')
        return best[1]

    def ext_sym(prof, name):
        inp = D.ef.createInput(prof, NEWB); inp.setSymmetricExtent(VI(E('BagB')), True)
        f = D.ef.add(inp); f.name = name
        b = f.bodies.item(0); b.name = name; return b

    def check(b, exp, name):
        bb = b.boundingBox
        got = ((bb.minPoint.x + bb.maxPoint.x) * 5, (bb.minPoint.z + bb.maxPoint.z) * 5)
        if abs(got[0] - exp[0]) > 40 or abs(got[1] - exp[2]) > 40:
            raise Exception('%s hamnar fel: %s, väntat %s' % (name, got, (exp[0], exp[2])))

    ytter = ext_sym(prof_band(R + K2, R + H2), 'Ytterremsa')
    inner = ext_sym(prof_band(R - H2, R - K2), 'Innerremsa')
    kb = {}
    for nm, lo, hi in K:
        s_lo = lo[1] if lo else 0
        s_hi = hi[1] if hi else BL
        exp = pt(R, ang((s_lo + s_hi) / 2))
        kb[nm] = ext_sym(prof_near(exp), nm); check(kb[nm], exp, nm)

    # bågens centrumaxel = skärningen mellan två plan genom radiella linjer (allt från Bågform, inga projektioner)
    def plan_genom(line, name):
        pi = r.constructionPlanes.createInput(); pi.setByAngle(line, VI('90 deg'), r.xZConstructionPlane)
        p_ = r.constructionPlanes.add(pi); p_.name = name; return p_
    pa_ = plan_genom(ref, 'Hjälpplan centrum-fot'); pb_ = plan_genom(ly, 'Hjälpplan centrum-skarv')
    # skärningslinjen mellan två plan får godtycklig riktning vid omräkning (vände -> mönstren gick åt fel håll).
    # Därför: punkt i (plan A, plan B, plan y = BagB/2) och axel från C0 till den punkten = alltid +y.
    pi = r.constructionPlanes.createInput(); pi.setByOffset(r.xZConstructionPlane, VI(E('BagB / 2')))
    pc_ = r.constructionPlanes.add(pi); pc_.name = 'Hjälpplan bågens framsida'
    cpi = r.constructionPoints.createInput(); cpi.setByThreePlanes(pa_, pb_, pc_)
    cpt = r.constructionPoints.add(cpi); cpt.name = 'Bågcentrum fram'
    ai = r.constructionAxes.createInput(); ai.setByTwoPoints(C0, cpt)
    axis = r.constructionAxes.add(ai); axis.name = 'Bågens centrumaxel'

    def pattern(seed, qty, pitch_expr, pitch_val, s_first, name):
        n = int(round(des.allParameters.itemByName(E(qty)).value))
        if n < 2:
            log(name, 'bara en kloss, inget mönster'); return []
        cp = r.features.circularPatternFeatures
        for sg in ('', '-'):
            inp = cp.createInput(coll([seed]), axis)
            inp.quantity = VI(E(qty))
            inp.totalAngle = VI(sg + '( ' + E('( %s - 1 ) * ( %s ) / BagR * 1 rad' % (qty, pitch_expr)) + ' )')
            inp.isSymmetric = False
            f = cp.add(inp)
            bs = [f.bodies.item(i) for i in range(f.bodies.count)]
            exp = pt(R, ang(s_first + (n - 1) * pitch_val))
            ok = any(abs((b.boundingBox.minPoint.x + b.boundingBox.maxPoint.x) * 5 - exp[0]) < 30 and abs((b.boundingBox.minPoint.z + b.boundingBox.maxPoint.z) * 5 - exp[2]) < 30 for b in bs)
            if ok:
                f.name = name
                return [b for b in bs if b.entityToken != seed.entityToken]
            log(name, sg, 'fel läge', [[round(v) for v in bbmm(b)] for b in bs])
            f.deleteMe()
        raise Exception('mönstret hamnar fel: ' + name)
    nedre = pattern(kb['Kloss nedre 1'], 'NedreMellan', 'NedrePitch', S['NedrePitch'], n0, 'Klossar nedre (mönster)')
    ovre = pattern(kb['Kloss övre 1'], 'OvreMellan', 'OvrePitch', S['OvrePitch'], o0, 'Klossar övre (mönster)')
    for k, b in enumerate(nedre): b.name = 'Kloss nedre %d' % (k + 2)
    for k, b in enumerate(ovre): b.name = 'Kloss övre %d' % (k + 2)

    sb = r.features.splitBodyFeatures
    for body, line, nm in ((ytter, ly, 'Ytterremsa'), (inner, li, 'Innerremsa')):
        pi = r.constructionPlanes.createInput(); pi.setByAngle(line, VI('90 deg'), r.xZConstructionPlane)
        pp_ = r.constructionPlanes.add(pi); pp_.name = 'Skarvplan ' + nm.lower()
        f = sb.add(sb.createInput(body, pp_, True)); f.name = 'Skarv ' + nm.lower()
        bs = sorted([f.bodies.item(i) for i in range(f.bodies.count)], key=lambda b: b.boundingBox.minPoint.z)
        for k, b in enumerate(bs): b.name = '%s %d' % (nm, k + 1)

    for nm, sv, outer in (('Lask ytter', S['SkarvYtterS'], True), ('Lask inner', S['SkarvInnerS'], False)):
        exp = pt(R + H2 + PT / 2 if outer else R - H2 - PT / 2, ang(sv))
        b = ext_sym(prof_near(exp), nm); check(b, exp, nm)

    for b in r.bRepBodies:
        b.appearance = plywood(des) if b.name.startswith(('Ytter', 'Inner', 'Lask')) else tra(des)
    r.partNumber = 'VH-HALVBAGE'; r.description = 'Halvbåge, stegbåge 15 mm plywood + klossar 70x70'
    des.computeAll()
    tl = des.timeline
    fel = [(tl.item(i).name, tl.item(i).errorOrWarningMessage[:80]) for i in range(tl.count) if tl.item(i).healthState != 0]
    res = {'kroppar': r.bRepBodies.count, 'fel': fel, 'ej_last': [s.name for s in r.sketches if not s.isFullyConstrained]}
    log(json.dumps(res, ensure_ascii=False))
    if fel: raise Exception('tidslinjefel i halvbågen')
    return res
