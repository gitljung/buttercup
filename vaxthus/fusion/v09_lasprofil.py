# Steg 7a: låsprofiler för wiggle wire (alu U-profil ProfilB x ProfilH x ProfilT, öppning utåt) i komponenten "Låsprofiler":
#  - gavelbågarnas utsida (bågform r = BagR + BagDjup / 2, i bågens mitt), tak- och gavelfilm delar profil
#  - långsyllarnas utsida, överkant i liv med syllens ovansida, hela syllens längd
#  - gavelsyllarnas framsida, från dörrstolpen till hörnvinkeln
#  - runt dörren: dörrstolparnas framsida (yttre kant) + överliggarens framsida (överkant), utanpå spikplåtarna
#  Filmen modelleras inte som kropp (räknas ut: m², löpmeter rulle). Loggar alla kroppsantal till v09_antal.json (skruvlistan).
exec(open(os.path.expanduser('~/code/buttercup/vaxthus/fusion/v08b_kopdelar.py')).read().split('\ndef run(')[0])
import collections, re
_ns['skip_par'] = skip_par; kontroll = _ns['kontroll']
NYA9 = [
    ('ProfilB', '32 mm', 'mm', 'Låsprofil (wiggle wire): bredd'),
    ('ProfilH', '13 mm', 'mm', 'Låsprofil: höjd'),
    ('ProfilT', '1.5 mm', 'mm', 'Låsprofil: godstjocklek'),
    ('ProfilL', '2000 mm', 'mm', 'Låsprofil: leveranslängd'),
    ('ProfilSkruvCC', '300 mm', 'mm', 'Låsprofil: c/c skruv'),
    ('FilmOverlapp', '500 mm', 'mm', 'Film: extra per ände/kant för hantering'),
]


def band_skiss(D, comp, rin, rout, name, fotz='SyllH'):
    """bågband mellan radierna rin och rout (uttryck), från syllens ovansida till x = 0 (nocken)"""
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
    r1, r2 = ev(rin), ev(rout); ZF = ev(fotz)
    xf = lambda r: cx + math.sqrt(r * r - (ZF - cz) ** 2)
    zn = lambda r: cz + math.sqrt(r * r - cx * cx)
    Lf = LS.addByTwoPoints(Q((xf(r1), 0, ZF)), Q((xf(r2), 0, ZF)))
    Ln = LS.addByTwoPoints(Q((0, 0, zn(r1))), Q((0, 0, zn(r2))))
    arcs = []
    for r, p0, p1 in ((r1, Lf.startSketchPoint, Ln.startSketchPoint), (r2, Lf.endSketchPoint, Ln.endSketchPoint)):
        th = (math.asin((ZF - cz) / r) + math.acos(-cx / r)) / 2
        ar = sk.sketchCurves.sketchArcs.addByThreePoints(p0, Q(pt(r, th)), p1)
        gc.addCoincident(ar.centerSketchPoint, C0)
        arcs.append((ar, r, th))
    along(sk, Lf, 'x'); along(sk, Ln, 'z')
    gc.addCoincident(Ln.startSketchPoint, zax)
    dimx(sk, o, Lf.startSketchPoint, 'z', fotz, (xf(r1) + 100, 0, ZF / 2))
    for (ar, r, th), e in zip(arcs, (rin, rout)):
        sk.sketchDimensions.addRadialDimension(ar, Q(pt(r * 0.95, th + 0.05))).parameter.expression = e
    log(name, 'låst', sk.isFullyConstrained, free_report(sk)[:6])
    if not sk.isFullyConstrained: raise Exception('ej låst: ' + name)
    return min([sk.profiles.item(i) for i in range(sk.profiles.count)], key=lambda p: p.areaProperties().area)


def u_poly(a0, a1, b0, b1, ea0, ea1, eb0, eb1, ea0T, eb0T, eb1T, T, dirb):
    """U-profil: botten vid a = a0 (tjocklek T mot a1), flänsar vid b0 och b1, öppning mot a1.
    a- och b-värden är koordinater, e*-uttryck är beloppet från origo."""
    s = 1 if a1 > a0 else -1
    aT = a0 + s * T
    return [(a0, b0, ea0, eb0), (a1, b0, ea1, eb0), (a1, b0 + T, ea1, eb0T), (aT, b0 + T, ea0T, eb0T),
            (aT, b1 - T, ea0T, eb1T), (a1, b1 - T, ea1, eb1T), (a1, b1, ea1, eb1), (a0, b1, ea0, eb1)]


def bygg_lasprofiler(des, comp):
    D = K(des, comp); ev = D.ev
    T, PB, PH = ev('ProfilT'), ev('ProfilB'), ev('ProfilH')
    hb, sbl, sh = ev('HalvBredd'), ev('SyllB'), ev('SyllH')
    dw, sb, dh, spt = ev('DorrBredd') / 2, ev('StolpeB'), ev('DorrHojd'), ev('SpikplatT')
    gavel = []
    # 1. gavelbåge (höger halva): på bågens gavelsida (y = -BagB / 2), i bågens yttre kant, öppning -y.
    #    (på bågens utsida krockar den med ytterlasken). Börjar ovanför bågfotsvinkeln.
    ro = 'BagR + BagDjup / 2'; fz = 'SyllH + VinkelA'
    b = D.ext(band_skiss(D, comp, ro + ' - ProfilB', ro, 'Låsprofil gavelbåge', fz), 'y', 'BagB / 2', 'ProfilH', -(ev('BagB') / 2 + PH), 'Låsprofil gavelbåge').bodies.item(0)
    b.name = 'Låsprofil gavelbåge'; v0 = b.volume
    cp = band_skiss(D, comp, ro + ' - ProfilB + ProfilT', ro + ' - ProfilT', 'Låsprofil gavelbåge spår', fz)
    ok = False
    for st in ('BagB / 2 + ProfilT', '-( BagB / 2 + ProfilT )'):
        for dd in ('ProfilH - ProfilT', '-( ProfilH - ProfilT )'):
            inp = D.ef.createInput(cp, CUT)
            inp.startExtent = adsk.fusion.OffsetStartDefinition.create(VI(st))
            inp.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(VI(dd)), adsk.fusion.ExtentDirections.PositiveExtentDirection)
            inp.participantBodies = [b]
            try: f = D.ef.add(inp)
            except Exception: continue
            if b.volume < 0.8 * v0: f.name = 'Låsprofil gavelbåge spår'; ok = True; break
            f.deleteMe()
        if ok: break
    log('gavelbåge volym före/efter spår', round(v0, 2), round(b.volume, 2))
    if b.volume > 0.6 * v0: raise Exception('spåret i gavelbågsprofilen blev inte skuret')
    gavel.append(b)
    # 2. gavelsyll (framsida y = -SyllB / 2, öppning -y), x från dörrstolpen till hörnvinkeln
    sk = comp.sketches.add(comp.yZConstructionPlane); sk.name = 'Skiss Låsprofil gavelsyll'
    S = Skiss(D, sk, 'y', 'z')
    S.poly(u_poly(-sbl / 2, -sbl / 2 - PH, sh - PB, sh, 'SyllB / 2', 'SyllB / 2 + ProfilH', 'SyllH - ProfilB', 'SyllH',
                  'SyllB / 2 + ProfilT', 'SyllH - ProfilB + ProfilT', 'SyllH - ProfilT', T, 1)); log(S.report())
    if not S.report()[1]: raise Exception('ej låst gavelsyll')
    f = D.ext(S.biggest(), 'x', 'DorrBredd / 2', 'HalvBredd - SyllB / 2 - VinkelA - VinkelT - DorrBredd / 2', dw, 'Låsprofil gavelsyll')
    f.bodies.item(0).name = 'Låsprofil gavelsyll'; gavel.append(f.bodies.item(0))
    # 3. dörrstolpe (framsida utanpå spikplåten, yttre kanten), z från syllen till överliggarens överkant
    sk = comp.sketches.add(comp.xYConstructionPlane); sk.name = 'Skiss Låsprofil dörrstolpe'
    S = Skiss(D, sk, 'x', 'y')
    y0 = -(sb / 2 + spt)
    xa, xb = dw + sb - PB, dw + sb
    pts = [(xa, y0, 'DorrBredd / 2 + StolpeB - ProfilB', 'StolpeB / 2 + SpikplatT'), (xb, y0, 'DorrBredd / 2 + StolpeB', 'StolpeB / 2 + SpikplatT'),
           (xb, y0 - PH, 'DorrBredd / 2 + StolpeB', 'StolpeB / 2 + SpikplatT + ProfilH'), (xb - T, y0 - PH, 'DorrBredd / 2 + StolpeB - ProfilT', 'StolpeB / 2 + SpikplatT + ProfilH'),
           (xb - T, y0 - T, 'DorrBredd / 2 + StolpeB - ProfilT', 'StolpeB / 2 + SpikplatT + ProfilT'), (xa + T, y0 - T, 'DorrBredd / 2 + StolpeB - ProfilB + ProfilT', 'StolpeB / 2 + SpikplatT + ProfilT'),
           (xa + T, y0 - PH, 'DorrBredd / 2 + StolpeB - ProfilB + ProfilT', 'StolpeB / 2 + SpikplatT + ProfilH'), (xa, y0 - PH, 'DorrBredd / 2 + StolpeB - ProfilB', 'StolpeB / 2 + SpikplatT + ProfilH')]
    S.poly(pts); log(S.report())
    if not S.report()[1]: raise Exception('ej låst dörrstolpe')
    f = D.ext(S.biggest(), 'z', 'SyllH', 'DorrHojd + StolpeB', sh, 'Låsprofil dörrstolpe')
    f.bodies.item(0).name = 'Låsprofil dörrstolpe'; gavel.append(f.bodies.item(0))
    mirror(comp, gavel, comp.yZConstructionPlane, 'Låsprofiler gavel vänster (spegling)')
    # 4. överliggare (framsida, överkant), symmetrisk i x mellan stolpprofilerna
    sk = comp.sketches.add(comp.yZConstructionPlane); sk.name = 'Skiss Låsprofil överliggare'
    S = Skiss(D, sk, 'y', 'z'); zt = sh + dh + sb
    S.poly(u_poly(y0, y0 - PH, zt - PB, zt, 'StolpeB / 2 + SpikplatT', 'StolpeB / 2 + SpikplatT + ProfilH', 'SyllH + DorrHojd + StolpeB - ProfilB', 'SyllH + DorrHojd + StolpeB',
                  'StolpeB / 2 + SpikplatT + ProfilT', 'SyllH + DorrHojd + StolpeB - ProfilB + ProfilT', 'SyllH + DorrHojd + StolpeB - ProfilT', T, 1)); log(S.report())
    if not S.report()[1]: raise Exception('ej låst överliggare')
    ext_sym(D, S.biggest(), '2 * ( DorrBredd / 2 + StolpeB - ProfilB )', 'Låsprofil överliggare')
    mirror(comp, [comp.bRepBodies.item(i) for i in range(comp.bRepBodies.count)], bak_plan(comp, ev), 'Låsprofiler bakre gaveln (spegling)')
    # 5. långsida höger (syllens utsida), sedan vänster
    sk = comp.sketches.add(comp.xZConstructionPlane); sk.name = 'Skiss Låsprofil långsida'
    S = Skiss(D, sk, 'x', 'z')
    S.poly(u_poly(hb + sbl / 2, hb + sbl / 2 + PH, sh - PB, sh, 'HalvBredd + SyllB / 2', 'HalvBredd + SyllB / 2 + ProfilH', 'SyllH - ProfilB', 'SyllH',
                  'HalvBredd + SyllB / 2 + ProfilT', 'SyllH - ProfilB + ProfilT', 'SyllH - ProfilT', T, 1)); log(S.report())
    if not S.report()[1]: raise Exception('ej låst långsida')
    f = D.ext(S.biggest(), 'y', 'BagB / 2 + SyllUtstick', 'Langd + BagB + 2 * SyllUtstick', -(ev('BagB') / 2 + ev('SyllUtstick')), 'Låsprofil långsida')
    mirror(comp, [f.bodies.item(0)], comp.yZConstructionPlane, 'Låsprofil långsida vänster (spegling)')
    L = ev('Langd')
    def bas(b, xm, ym):
        bb = b.boundingBox; dx, dy, dz = [(getattr(bb.maxPoint, k) - getattr(bb.minPoint, k)) * 10 for k in 'xyz']
        if dy > 3000: return 'Låsprofil långsida'
        if dz > 1000 and dx > 1000: return 'Låsprofil gavelbåge'
        if dz > 1000: return 'Låsprofil dörrstolpe'
        if dx > 2 * dw: return 'Låsprofil överliggare'
        return 'Låsprofil gavelsyll'
    namnge(comp, ev, bas)
    for b in comp.bRepBodies:
        if b.name.startswith('Låsprofil långsida'): b.name = b.name.replace(' fram', '').replace(' bak', '')
        b.appearance = appearance(des, 'Aluminium (låsprofil)', 'Paint - Metallic (Silver)', (190, 194, 198))
    comp.partNumber = 'LASPROFIL'; comp.description = 'Låsprofil alu 32x13 + fjädertråd (wiggle wire), t.ex. VEVOR 50x2 m'
    for s in comp.sketches: s.isVisible = False


def langder(des, comp, ev):
    """löpmeter per sort; bågen räknas längs profilens botten (r = BagR + BagDjup / 2)"""
    cx, cz, sh = ev('BagCx'), ev('BagCz'), ev('SyllH') + ev('VinkelA'); r = ev('BagR') + ev('BagDjup') / 2 - ev('ProfilB') / 2
    bage = r * (math.acos(cx / r) - math.asin((sh - cz) / r))
    res = collections.OrderedDict()
    for b in comp.bRepBodies:
        k = re.sub(r' (fram|bak|höger|vänster)', '', b.name)
        bb = b.boundingBox
        l = bage if k == 'Låsprofil gavelbåge' else max((getattr(bb.maxPoint, a) - getattr(bb.minPoint, a)) * 10 for a in 'xyz')
        res.setdefault(k, []).append(round(l))
    return res


def antal_alla(des):
    """antal kroppar per komponent och grundnamn (läge, nummer och speglingssuffix bortstrippade)"""
    out = {}
    for c in des.allComponents:
        cnt = collections.Counter()
        for b in c.bRepBodies:
            k = re.sub(r' (fram|bak|höger|vänster|insida|utsida|nedre|övre|\+y|-y|\d+)', '', b.name).strip()
            cnt[k] += 1
        if cnt: out[c.name] = {'förekomster': des.rootComponent.allOccurrencesByComponent(c).count if c != des.rootComponent else 1, 'kroppar': dict(cnt)}
    return out


def run(_context: str):
    keepalive()
    d = find_doc(TOPPNAMN)
    if d: d.close(False)
    d = app.documents.open(dfile(TOPPNAMN)); d.activate()
    des = adsk.fusion.Design.cast(d.products.itemByProductType('DesignProductType'))
    root = des.rootComponent; up = des.userParameters
    ev = lambda s: des.unitsManager.evaluateExpression(s, 'mm') * 10
    if not des.allComponents.itemByName('Köpdelar dörr'): raise Exception('steg 6d saknas')
    for n, e, u, c in NYA9:
        p = up.itemByName(n)
        if p: p.expression = e
        else: up.add(n, VI(e), u, c).isFavorite = True
    for o in list(root.occurrences):
        if o.component.name == 'Låsprofiler': o.deleteMe()
    o = root.occurrences.addNewComponent(adsk.core.Matrix3D.create()); o.component.name = 'Låsprofiler'
    bygg_lasprofiler(des, o.component); o.isGrounded = True
    lc = o.component
    lg = langder(des, lc, ev); log('längder', json.dumps(lg, ensure_ascii=False))
    def pval(k):
        q = up.itemByName(k)
        return round(q.value, 3) if q.unit == '' else round(ev(k), 1)
    pv = {k: pval(k) for k in ('Bredd', 'Langd', 'Nockhojd', 'BagR', 'BagDjup', 'BagLangd', 'AntalBagar', 'BagCC', 'NedreMellan', 'OvreMellan',
                                       'DorrBredd', 'DorrHojd', 'StolpeB', 'SyllUtstick', 'ProfilL', 'ProfilSkruvCC', 'FilmOverlapp', 'BagB')}
    json.dump({'parametrar': pv, 'lasprofil_mm': lg, 'antal': antal_alla(des)},
              open(os.path.expanduser('~/code/buttercup/vaxthus/fusion/v09_antal.json'), 'w'), ensure_ascii=False, indent=1)
    gom(des)
    global FLEXMODE
    FLEXMODE = False
    alla = [kontroll(des, root, 'standard')]
    hb, sh, dw = ev('HalvBredd'), ev('SyllH'), ev('DorrBredd') / 2; L = ev('Langd')
    bild('v09_dummy.png', (7000, -7000, 4500), (0, L / 2, 1700), 9000)
    bild('v09_iso.png', (7000, -7000, 4500), (0, L / 2, 1700), 9000)
    bild('v09_gavel.png', (1200, -9000, 1900), (0, 0, 1800), 4800)
    bild('v09_hornet.png', (hb + 900, -1300, 700), (hb - 100, 0, 150), 1100)
    bild('v09_dorrhorn.png', (dw + 700, -900, sh + 2400), (dw + 50, -50, sh + 2050), 700)
    bild('v09_nock.png', (700, -1500, 4200), (0, 0, 3550), 900)
    orig = {k: up.itemByName(k).expression for k in FLEX}
    try:
        FLEXMODE = True
        for k, v in FLEX.items(): up.itemByName(k).expression = v
        alla.append(kontroll(des, root, 'flex (köpdelar ej omplacerade)'))
        bild('v09_flex.png', (8000, -8000, 5000), (0, 6000, 1900), 10500)
    finally:
        for k, v in orig.items(): up.itemByName(k).expression = v
        FLEXMODE = False
    alla.append(kontroll(des, root, 'återställt'))
    json.dump(alla, open(os.path.expanduser('~/code/buttercup/vaxthus/fusion/v09_resultat.json'), 'w'), ensure_ascii=False, indent=1)
    try: os.remove(OUT + 'v09_dummy.png')
    except Exception: pass
    a0, a1, a2 = alla
    if a0['antal_krock'] or a0['fel'] or a0['ej_last'] or a2['fel'] or a2['antal_krock'] or a2['ej_last'] or a2['kroppar_totalt'] != a0['kroppar_totalt'] or a1['fel'] or a1['ej_last'] or a1['antal_krock']:
        raise Exception('kontroll underkänd, sparar inte')
    d.save('Steg 7a: låsprofiler (wiggle wire) gavelbågar, långsidor, gavelsyllar, dörrkarm; flextest OK')
    log('sparad', TOPPNAMN)
