# Steg 5 (+ beslag 6b) i dokumentet "Växthus":
#  - "Gavlar": dörrstolpar 95x95 från gavelsyllen upp till bågens insida (toppen kapad i bågens radie),
#              överliggare 95x95 över dörren, nockstolpe 45x120 (samma virke som nockregeln) upp till nockregeln.
#              Byggd vid främre gaveln, speglad till höger/vänster och till bakre gaveln (plan Langd / 2).
#  - "Dörrar":  pardörrar, ram 45x70 (DorrRamT x DorrRamB), spel DorrSpel, 2 blad per gavel.
#  - "Gavelbeslag": vinkel vid varje dörrstolpes fot (utsidan, ner på gavelsyllen),
#              spikplåt 2x100x200 över stöten överliggare/stolpe på båda sidor.
#  - rättar namn på speglade kroppar (höger/vänster, fram/bak) efter läge.
exec(open(os.path.expanduser('~/code/buttercup/vaxthus/fusion/v05_beslag.py')).read().split('\ndef run(')[0])


def ext_sym(D, prof, expr, name):
    inp = D.ef.createInput(prof, NEWB); inp.setSymmetricExtent(VI(expr), True)
    f = D.ef.add(inp); f.name = name
    b = f.bodies.item(0); b.name = name; return b


def bak_plan(comp, ev):
    pi = comp.constructionPlanes.createInput(); pi.setByOffset(comp.xZConstructionPlane, VI('Langd / 2'))
    mid = comp.constructionPlanes.add(pi)
    if abs(mid.geometry.origin.y * 10 - ev('Langd') / 2) > 1e-3:
        mid.deleteMe(); pi = comp.constructionPlanes.createInput(); pi.setByOffset(comp.xZConstructionPlane, VI('-Langd / 2'))
        mid = comp.constructionPlanes.add(pi)
    mid.name = 'Mittplan längs (Langd / 2)'; mid.isLightBulbOn = False
    return mid


def spegla_allt(comp, ev, namn):
    allb = lambda: [comp.bRepBodies.item(i) for i in range(comp.bRepBodies.count)]
    mirror(comp, allb(), comp.yZConstructionPlane, namn + ' vänster (spegling)')
    mirror(comp, allb(), bak_plan(comp, ev), namn + ' bak (spegling)')


def namnge(comp, ev, bas_fn):
    """döp kroppar efter läge: bas_fn(body) -> grundnamn; lägger till fram/bak och höger/vänster"""
    L = ev('Langd')
    for b in comp.bRepBodies:
        bb = b.boundingBox
        xm = (bb.minPoint.x + bb.maxPoint.x) * 5; ym = (bb.minPoint.y + bb.maxPoint.y) * 5
        sida = '' if abs(xm) < 1 else (' höger' if xm > 0 else ' vänster')
        b.name = bas_fn(b, xm, ym) + (' fram' if ym < L / 2 else ' bak') + sida


def stolpe_skiss(D, comp):
    ev = D.ev
    R = ev('BagR'); cx = -ev('BagCx'); cz = ev('BagCz'); SH = ev('SyllH')
    pt = lambda rr, th: (cx + rr * math.cos(th), 0.0, cz + rr * math.sin(th))
    sk = comp.sketches.add(comp.xZConstructionPlane); sk.name = 'Dörrstolpe'
    o = sk.originPoint; gc = sk.geometricConstraints; LS = sk.sketchCurves.sketchLines
    Q = lambda p: SP(sk, *p)
    tF = math.asin((SH - cz) / R); tN = math.atan2(ev('Nockhojd') - cz, -cx)
    a = sk.sketchCurves.sketchArcs.addByThreePoints(Q(pt(R, tF)), Q(pt(R, (tF + tN) / 2)), Q(pt(R, tN)))
    a.isConstruction = True
    ps, pe = a.startSketchPoint, a.endSketchPoint
    pF, pN = (ps, pe) if ps.geometry.distanceTo(Q(pt(R, tF))) < pe.geometry.distanceTo(Q(pt(R, tF))) else (pe, ps)
    dimx(sk, o, pF, 'x', 'HalvBredd', (ev('HalvBredd') / 2, 0, SH - 150))
    dimx(sk, o, pF, 'z', 'SyllH', (ev('HalvBredd') + 150, 0, SH / 2))
    gc.addCoincident(pN, proj_axis(sk, comp, 'z'))
    dimx(sk, o, pN, 'z', 'Nockhojd', (-200, 0, ev('Nockhojd') / 2))
    sk.sketchDimensions.addRadialDimension(a, Q(pt(R * 0.9, 0.9))).parameter.expression = 'BagR'
    C0 = a.centerSketchPoint
    ri = R - ev('BagDjup') / 2
    x0, x1 = ev('DorrBredd') / 2, ev('DorrBredd') / 2 + ev('StolpeB')
    zt = lambda x: cz + math.sqrt(ri * ri - (x - cx) ** 2)
    b = LS.addByTwoPoints(Q((x0, 0, SH)), Q((x1, 0, SH)))
    s1 = LS.addByTwoPoints(b.endSketchPoint, Q((x1, 0, zt(x1))))
    s0 = LS.addByTwoPoints(b.startSketchPoint, Q((x0, 0, zt(x0))))
    xm = (x0 + x1) / 2
    top = sk.sketchCurves.sketchArcs.addByThreePoints(s0.endSketchPoint, Q((xm, 0, zt(xm))), s1.endSketchPoint)
    gc.addCoincident(top.centerSketchPoint, C0)
    sk.sketchDimensions.addRadialDimension(top, Q((xm, 0, zt(xm) - 200))).parameter.expression = 'BagR - BagDjup / 2'
    along(sk, b, 'x'); along(sk, s0, 'z'); along(sk, s1, 'z')
    dimx(sk, o, b.startSketchPoint, 'x', 'DorrBredd / 2', (x0 / 2, 0, SH - 80))
    dimx(sk, o, b.endSketchPoint, 'x', 'DorrBredd / 2 + StolpeB', (x1 / 2, 0, SH - 160))
    dimx(sk, o, b.startSketchPoint, 'z', 'SyllH', (x0 - 80, 0, SH / 2))
    log('Dörrstolpe låst', sk.isFullyConstrained, free_report(sk)[:6])
    if not sk.isFullyConstrained: raise Exception('dörrstolpens skiss är inte låst')
    prof = min([sk.profiles.item(i) for i in range(sk.profiles.count)], key=lambda p: p.areaProperties().area)
    return prof


def bygg_gavlar(des, comp):
    D = K(des, comp); ev = D.ev
    st = ext_sym(D, stolpe_skiss(D, comp), 'StolpeB', 'Dörrstolpe')
    # överliggare över dörren
    sk = comp.sketches.add(comp.xZConstructionPlane); sk.name = 'Överliggare'
    S = Skiss(D, sk, 'x', 'z'); dw = ev('DorrBredd') / 2; z0 = ev('SyllH') + ev('DorrHojd'); sb = ev('StolpeB')
    S.rect(-dw, dw, z0, z0 + sb, 'DorrBredd / 2', 'DorrBredd / 2', 'SyllH + DorrHojd', 'SyllH + DorrHojd + StolpeB'); log(S.report())
    ov = ext_sym(D, S.biggest(), 'StolpeB', 'Överliggare')
    # nockstolpe
    sk = comp.sketches.add(comp.xZConstructionPlane); sk.name = 'Nockstolpe'
    S = Skiss(D, sk, 'x', 'z'); nt = ev('NockT') / 2
    S.rect(-nt, nt, z0 + sb, ev('NockOK') - ev('NockH'), 'NockT / 2', 'NockT / 2', 'SyllH + DorrHojd + StolpeB', 'NockOK - NockH'); log(S.report())
    ns = ext_sym(D, S.biggest(), 'NockH', 'Nockstolpe')
    # spegla stolpen till vänster, sedan allt till bakre gaveln
    mirror(comp, [st], comp.yZConstructionPlane, 'Dörrstolpe vänster (spegling)')
    mirror(comp, [comp.bRepBodies.item(i) for i in range(comp.bRepBodies.count)], bak_plan(comp, ev), 'Bakre gaveln (spegling)')
    def bas(b, xm, ym):
        bb = b.boundingBox
        if (bb.maxPoint.x - bb.minPoint.x) * 10 > 500: return 'Överliggare'
        return 'Nockstolpe' if abs(xm) < 1 else 'Dörrstolpe'
    namnge(comp, ev, bas)
    for b in comp.bRepBodies: b.appearance = tra(des)
    comp.partNumber = 'VH-GAVEL'; comp.description = 'Gavelstomme: dörrstolpar + överliggare 95x95, nockstolpe 45x120'
    for s in comp.sketches: s.isVisible = False


def bygg_dorrar(des, comp):
    D = K(des, comp); ev = D.ev
    sk = comp.sketches.add(comp.xZConstructionPlane); sk.name = 'Dörrblad'
    S = Skiss(D, sk, 'x', 'z')
    sp, dw, rb, sh, dh = ev('DorrSpel'), ev('DorrBredd') / 2, ev('DorrRamB'), ev('SyllH'), ev('DorrHojd')
    S.rect(sp / 2, dw - sp, sh + sp, sh + dh - sp, 'DorrSpel / 2', 'DorrBredd / 2 - DorrSpel', 'SyllH + DorrSpel', 'SyllH + DorrHojd - DorrSpel')
    S.rect(sp / 2 + rb, dw - sp - rb, sh + sp + rb, sh + dh - sp - rb, 'DorrSpel / 2 + DorrRamB', 'DorrBredd / 2 - DorrSpel - DorrRamB', 'SyllH + DorrSpel + DorrRamB', 'SyllH + DorrHojd - DorrSpel - DorrRamB')
    log(S.report())
    ram = max([sk.profiles.item(i) for i in range(sk.profiles.count)], key=lambda p: p.boundingBox.maxPoint.x - p.boundingBox.minPoint.x + p.boundingBox.maxPoint.y - p.boundingBox.minPoint.y + 1e-3 * (1 if p.areaProperties().area < 10000 else 0))
    # ramen = profilen med yttermåtten men minsta arean av dem
    cand = [sk.profiles.item(i) for i in range(sk.profiles.count)]
    big = max(p.boundingBox.maxPoint.x - p.boundingBox.minPoint.x for p in cand)
    ram = min([p for p in cand if abs((p.boundingBox.maxPoint.x - p.boundingBox.minPoint.x) - big) < 1e-4], key=lambda p: p.areaProperties().area)
    # dörrens utsida i liv med stolparnas utsida (y = -StolpeB/2), så att T-gångjärnen ligger plant på dörr och stolpe
    D.ext(ram, 'y', 'StolpeB / 2', 'DorrRamT', -ev('StolpeB') / 2, 'Dörrblad').bodies.item(0).name = 'Dörrblad'
    spegla_allt(comp, ev, 'Dörrblad')
    namnge(comp, ev, lambda b, xm, ym: 'Dörrblad')
    for b in comp.bRepBodies: b.appearance = tra(des)
    comp.partNumber = 'VH-DORR'; comp.description = 'Pardörr, ram 45x70 (film eller lister fylls i senare)'
    for s in comp.sketches: s.isVisible = False


def bygg_gavelbeslag(des, comp):
    D = K(des, comp); ev = D.ev
    D.PL = {'xy': comp.xYConstructionPlane, 'xz': comp.xZConstructionPlane, 'yz': comp.yZConstructionPlane}
    x1 = ev('DorrBredd') / 2 + ev('StolpeB'); A, T, sh = ev('VinkelA'), ev('VinkelT'), ev('SyllH')
    e1 = 'DorrBredd / 2 + StolpeB'
    pts = [(x1, sh, e1, 'SyllH'), (x1 + A, sh, e1 + ' + VinkelA', 'SyllH'), (x1 + A, sh + T, e1 + ' + VinkelA', 'SyllH + VinkelT'),
           (x1 + T, sh + T, e1 + ' + VinkelT', 'SyllH + VinkelT'), (x1 + T, sh + A, e1 + ' + VinkelT', 'SyllH + VinkelA'), (x1, sh + A, e1, 'SyllH + VinkelA')]
    sk = comp.sketches.add(comp.xZConstructionPlane); sk.name = 'Skiss Stolpfotsvinkel'
    S = Skiss(D, sk, 'x', 'z'); S.poly(pts); log(S.report())
    ext_sym(D, S.biggest(), 'VinkelB', 'Stolpfotsvinkel')
    sk = comp.sketches.add(comp.xZConstructionPlane); sk.name = 'Skiss Spikplåt överliggare'
    S = Skiss(D, sk, 'x', 'z'); zc = sh + ev('DorrHojd') + ev('StolpeB') / 2; L_, B_ = ev('SpikplatL'), ev('SpikplatB')
    S.rect(x1 - L_, x1, zc - B_ / 2, zc + B_ / 2, e1 + ' - SpikplatL', e1, 'SyllH + DorrHojd + StolpeB / 2 - SpikplatB / 2', 'SyllH + DorrHojd + StolpeB / 2 + SpikplatB / 2'); log(S.report())
    sb2, pt_ = ev('StolpeB') / 2, ev('SpikplatT')
    D.ext(S.biggest(), 'y', 'StolpeB / 2', 'SpikplatT', -sb2 - pt_, 'Spikplåt överliggare utsida')
    D.ext(S.biggest(), 'y', 'StolpeB / 2', 'SpikplatT', sb2, 'Spikplåt överliggare insida')
    spegla_allt(comp, ev, 'Gavelbeslag')
    def bas(b, xm, ym):
        bb = b.boundingBox
        if (bb.maxPoint.y - bb.minPoint.y) * 10 < 5:
            ins = (ym > 0) if ym < ev('Langd') / 2 else (ym < ev('Langd'))
            return 'Spikplåt överliggare ' + ('insida' if ins else 'utsida')
        return 'Stolpfotsvinkel'
    namnge(comp, ev, bas)
    for b in comp.bRepBodies: b.appearance = zink(des)
    comp.partNumber = 'GAVELBESLAG'; comp.description = 'Vinkel 90x90x65x2,5 + spikplåt 2x100x200 vfz (köpdelar)'
    for s in comp.sketches: s.isVisible = False


def ratta_namn(des, ev):
    c = des.allComponents.itemByName('Syllram')
    namnge(c, ev, lambda b, xm, ym: 'Syll långsida' if (b.boundingBox.maxPoint.y - b.boundingBox.minPoint.y) * 10 > 1000 else 'Syll gavel')
    for b in c.bRepBodies:      # långsidorna går hela längden: ta bort 'fram'
        if b.name.startswith('Syll långsida'): b.name = b.name.replace(' fram', '').replace(' bak', '')
    c = des.allComponents.itemByName('Nock och sidoreglar')
    namnge(c, ev, lambda b, xm, ym: 'Nockregel' if abs(xm) < 1 else 'Sidoregel')
    for b in c.bRepBodies: b.name = b.name.replace(' fram', '').replace(' bak', '')


def run(_context: str):
    keepalive()
    d = find_doc(TOPPNAMN)
    if d: d.close(False)
    d = app.documents.open(dfile(TOPPNAMN)); d.activate()
    des = adsk.fusion.Design.cast(d.products.itemByProductType('DesignProductType'))
    root = des.rootComponent; up = des.userParameters
    ev = lambda s: des.unitsManager.evaluateExpression(s, 'mm') * 10
    if not des.allComponents.itemByName('Vinklar bågfot'): raise Exception('steg 6a saknas')
    for o in list(root.occurrences):
        if o.component.name in ('Gavlar', 'Dörrar', 'Gavelbeslag'): o.deleteMe()
    I = adsk.core.Matrix3D.create()
    for nm, fn in (('Gavlar', bygg_gavlar), ('Dörrar', bygg_dorrar), ('Gavelbeslag', bygg_gavelbeslag)):
        o = root.occurrences.addNewComponent(I); o.component.name = nm
        fn(des, o.component); o.isGrounded = True
        log(nm, sorted(b.name for b in o.component.bRepBodies))
    ratta_namn(des, ev)
    log('Syllram', sorted(b.name for b in des.allComponents.itemByName('Syllram').bRepBodies))
    gom(des)
    alla = [kontroll(des, root, 'standard')]
    L = ev('Langd'); nk = ev('NockOK'); dw = ev('DorrBredd') / 2; sh = ev('SyllH'); dh = ev('DorrHojd')
    bild('v06_dummy.png', (0, -12000, 1800), (0, 0, 1800), 5200)
    bild('v06_gavel_fram.png', (0, -12000, 1800), (0, 0, 1800), 5200)
    bild('v06_iso.png', (7000, -7000, 4500), (0, L / 2, 1700), 9000)
    bild('v06_gavel_inifran.png', (1500, 4500, 1900), (0, 0, 1700), 5000)
    bild('v06_stolpfot.png', (dw + 1100, -900, 700), (dw + 50, 0, 150), 1000)
    bild('v06_overliggare.png', (dw + 600, -1100, sh + dh + 500), (dw, 0, sh + dh + 50), 900)
    bild('v06_stolptopp.png', (dw + 700, -900, 2900), (dw + 50, 0, 2450), 900)
    orig = {k: up.itemByName(k).expression for k in FLEX}
    try:
        for k, v in FLEX.items(): up.itemByName(k).expression = v
        alla.append(kontroll(des, root, 'flex'))
        bild('v06_flex_gavel.png', (0, -14000, 2000), (0, 0, 2000), 6000)
    finally:
        for k, v in orig.items(): up.itemByName(k).expression = v
    alla.append(kontroll(des, root, 'återställt'))
    json.dump(alla, open(os.path.expanduser('~/code/buttercup/vaxthus/fusion/v06_resultat.json'), 'w'), ensure_ascii=False, indent=1)
    try: os.remove(OUT + 'v06_dummy.png')
    except Exception: pass
    a0, a1, a2 = alla
    if a2['fel'] or a2['antal_krock'] or a2['ej_last'] or a2['kroppar_totalt'] != a0['kroppar_totalt'] or a1['fel'] or a1['ej_last'] or a1['antal_krock']:
        raise Exception('kontroll underkänd, sparar inte')
    d.save('Steg 5 + 6b: gavlar, dörrar, gavelbeslag; namn rättade; flextest OK')
    log('sparad', TOPPNAMN)
