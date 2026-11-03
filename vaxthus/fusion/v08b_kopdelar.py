# Steg 6d: Wiberger-köpdelar på dörrarna.
#  - "Dörrbeslag" byggs om: gångjärn GJ60 A2 100x100 ritat parametriskt (plåt + led), kantreglar kvar (förenklade)
#  - "Köpdelar dörr": STEP från Wiberger, placerade efter parametrarnas aktuella värden (följer INTE med automatiskt):
#      GN425 A2 200-M5 bygelhandtag ute + inne på aktiva bladet, EL2030-100 excenterlås med hänglåsögla ute,
#      EL1035-200 excenterlås (stormhake) inne.
exec(open(os.path.expanduser('~/code/buttercup/vaxthus/fusion/v07_dorrbeslag.py')).read().split('\ndef run(')[0])
_src = open(os.path.expanduser('~/code/buttercup/vaxthus/fusion/v03_topp.py')).read().split('\ndef run(')[0]
_src = _src.replace("if not bbs[i].intersects(bbs[j]): continue", "if not bbs[i].intersects(bbs[j]) or skip_par(bw[i][0], bw[j][0]): continue")
_ns = dict(globals()); exec(_src, _ns)       # bara krockkontrollen tas från v03 (resten av v03 skulle skriva över K)
FLEXMODE = False


def grp(n):
    p = n.split('+')
    return '+'.join(p[:2]) if p[0].startswith('Köpdelar dörr') else None


def skip_par(a, b):
    ga, gb = grp(a), grp(b)
    if FLEXMODE and (ga or gb): return True          # köpdelarna står kvar i standardläget under flextestet
    return ga is not None and ga == gb               # delar inne i samma köpdel (axlar i hål) räknas inte


KOP = os.path.expanduser('~/code/buttercup/vaxthus/fusion/kopdelar/')
STEG = {
    'handtag': ('GN425 A2 200-M5 bygelhandtag', KOP + 'gn425a2-a4/Wiberger-GN425-NI-10-200-GS.step'),
    'las': ('EL2030-100-FZB excenterlås med ögla', KOP + 'el2030-100/Wiberger-el2030-100-fzb.step'),
    'storm': ('EL1035-200-RF excenterlås (stormhake)', KOP + 'el1035-200/Wiberger-el1035-200.STEP'),
}
NYA8 = {'GangjarnL': ('100 mm', 'Gångjärn GJ60 100x100: höjd'), 'GangjarnB': ('100 mm', 'Gångjärn GJ60 100x100: bredd uppslaget'),
        'GangjarnT': ('1.5 mm', 'Gångjärn GJ60: plåttjocklek'), 'GangjarnLed': ('8 mm', 'Gångjärn GJ60: ledens diameter'),
        'GangjarnZ': ('200 mm', 'Gångjärn: mitt från dörrbladets över-/underkant')}
BORT = ['GangjarnPlatB', 'GangjarnPlatH', 'HandtagL', 'HandtagB', 'HandtagD', 'OverfallL', 'OverfallB', 'BeslagT']


def M(xa, ya, za, o):
    m = adsk.core.Matrix3D.create()
    V = adsk.core.Vector3D.create
    m.setWithCoordinateSystem(P3(o[0] / 10, o[1] / 10, o[2] / 10), V(*xa), V(*ya), V(*za))
    return m


def bygg_dorrbeslag2(des, comp):
    D = K(des, comp); ev = D.ev
    dw, sp, sh, dh = ev('DorrBredd') / 2, ev('DorrSpel'), ev('SyllH'), ev('DorrHojd')
    sb2, gt = ev('StolpeB') / 2, ev('GangjarnT')
    xg = dw - sp / 2; gb2, gl2 = ev('GangjarnB') / 2, ev('GangjarnL') / 2
    gj = []
    for nm, zc, ezc in (('nedre', sh + sp + ev('GangjarnZ'), 'SyllH + DorrSpel + GangjarnZ'),
                        ('övre', sh + dh - sp - ev('GangjarnZ'), 'SyllH + DorrHojd - DorrSpel - GangjarnZ')):
        pl = box_xz(D, comp, 'Gångjärn ' + nm, xg - gb2, xg + gb2, zc - gl2, zc + gl2,
                    'DorrBredd / 2 - DorrSpel / 2 - GangjarnB / 2', 'DorrBredd / 2 - DorrSpel / 2 + GangjarnB / 2',
                    ezc + ' - GangjarnL / 2', ezc + ' + GangjarnL / 2', 'StolpeB / 2', 'GangjarnT', -sb2 - gt)
        sk = comp.sketches.add(comp.xYConstructionPlane); sk.name = 'Skiss Gångjärnsled ' + nm
        S = Skiss(D, sk, 'x', 'y')
        S.hole(xg, -(sb2 + ev('GangjarnLed') / 2), 'DorrBredd / 2 - DorrSpel / 2', 'StolpeB / 2 + GangjarnLed / 2', dia='GangjarnLed')
        rep = S.report(); log(rep)
        if not rep[1]: raise Exception('led ej låst')
        prof = min([sk.profiles.item(i) for i in range(sk.profiles.count)], key=lambda p: p.areaProperties().area)
        D.ext(prof, 'z', ezc + ' - GangjarnL / 2', 'GangjarnL', zc - gl2, 'Gångjärnsled ' + nm, op=JOIN, parts=[pl])
        gj.append(pl)
    mirror(comp, gj, comp.yZConstructionPlane, 'Gångjärn vänster blad (spegling)')
    xk = sp / 2 + ev('DorrRamB') / 2; kb = ev('KantregelB') / 2; kl = ev('KantregelL'); ins = sb2 - ev('DorrRamT')
    inn = ('StolpeB / 2 - DorrRamT', 'KantregelB', -ins)
    box_xz(D, comp, 'Kantregel övre', -(xk + kb), -(xk - kb), sh + dh - sp - kl, sh + dh - sp,
           'DorrSpel / 2 + DorrRamB / 2 + KantregelB / 2', 'DorrSpel / 2 + DorrRamB / 2 - KantregelB / 2', 'SyllH + DorrHojd - DorrSpel - KantregelL', 'SyllH + DorrHojd - DorrSpel', *inn)
    box_xz(D, comp, 'Kantregel nedre', -(xk + kb), -(xk - kb), sh + sp, sh + sp + kl,
           'DorrSpel / 2 + DorrRamB / 2 + KantregelB / 2', 'DorrSpel / 2 + DorrRamB / 2 - KantregelB / 2', 'SyllH + DorrSpel', 'SyllH + DorrSpel + KantregelL', *inn)
    mirror(comp, [comp.bRepBodies.item(i) for i in range(comp.bRepBodies.count)], bak_plan(comp, ev), 'Bakre gaveln (spegling)')
    def bas(b, xm, ym):
        zm = (b.boundingBox.minPoint.z + b.boundingBox.maxPoint.z) * 5
        k = 'Gångjärn GJ60' if b.name.startswith('Gångjärn') else 'Kantregel'
        return k + (' övre' if zm > sh + dh / 2 else ' nedre')
    namnge(comp, ev, bas)
    for b in comp.bRepBodies: b.appearance = zink(des)
    comp.partNumber = 'DORRBESLAG'; comp.description = 'Gångjärn Wiberger GJ60 A2 100X100 (43,70 kr ex moms), kantreglar (bygghandel)'
    for s in comp.sketches: s.isVisible = False


def placeringar(ev):
    sb2, rt, L = ev('StolpeB') / 2, ev('DorrRamT'), ev('Langd')
    sh = ev('SyllH'); xh = ev('DorrSpel') / 2 + ev('DorrRamB') / 2
    zh, zo = sh + ev('HandtagZ'), sh + ev('OverfallZ')
    I3 = ((1, 0, 0), (0, 1, 0), (0, 0, 1)); Rz = ((-1, 0, 0), (0, -1, 0), (0, 0, 1)); Rx = ((1, 0, 0), (0, -1, 0), (0, 0, -1))
    return [
        ('handtag', 'Handtag ute fram', Rz, (xh, -sb2, zh)), ('handtag', 'Handtag inne fram', I3, (xh, -sb2 + rt, zh)),
        ('handtag', 'Handtag ute bak', I3, (xh, L + sb2, zh)), ('handtag', 'Handtag inne bak', Rz, (xh, L + sb2 - rt, zh)),
        ('las', 'Excenterlås ute fram', Rx, (10, -sb2, zo)), ('las', 'Excenterlås ute bak', I3, (10, L + sb2, zo)),
        ('storm', 'Stormhake inne fram', I3, (0, -sb2 + rt + 1, zo)), ('storm', 'Stormhake inne bak', Rz, (0, L + sb2 - rt - 1, zo)),
    ]


def bygg_kopdelar(des, comp, ev):
    im = app.importManager
    lib = {}
    tmp = []
    for k, (namn, fil) in STEG.items():
        n0 = comp.occurrences.count
        im.importToTarget(im.createSTEPImportOptions(fil), comp)
        o = comp.occurrences.item(comp.occurrences.count - 1)
        if comp.occurrences.count == n0: raise Exception('import misslyckades: ' + k)
        o.component.name = namn; o.component.partNumber = namn.split(' ')[0]
        lib[k] = o.component; tmp.append(o)
    for k, nm, R, o in placeringar(ev):
        oc = comp.occurrences.addExistingComponent(lib[k], M(R[0], R[1], R[2], o))
        log('placerad', nm, [round(v) for v in o])
    for o in tmp: o.deleteMe()
    for c in lib.values():
        for b in c.bRepBodies: b.appearance = zink(des)
        for oc in c.allOccurrences:
            for b in oc.component.bRepBodies: b.appearance = zink(des)
    comp.description = 'Wiberger: GN425 A2 200-M5 130,50 kr, EL2030-100-FZB 29 kr, EL1035-200-RF 23 kr (ex moms 2026-11-03). Placerade efter parametrarna vid byggtillfället.'


def run(_context: str):
    global FLEXMODE, kontroll
    _ns['skip_par'] = skip_par; kontroll = _ns['kontroll']
    keepalive()
    d = find_doc(TOPPNAMN)
    if d: d.close(False)
    d = app.documents.open(dfile(TOPPNAMN)); d.activate()
    des = adsk.fusion.Design.cast(d.products.itemByProductType('DesignProductType'))
    root = des.rootComponent; up = des.userParameters
    ev = lambda s: des.unitsManager.evaluateExpression(s, 'mm') * 10
    for o in list(root.occurrences):
        if o.component.name in ('Dörrbeslag', 'Köpdelar dörr'): o.deleteMe()
    for n, (e, c) in NYA8.items():
        p = up.itemByName(n)
        if p: p.expression = e; p.comment = c
        else: up.add(n, VI(e), 'mm', c).isFavorite = True
    I = adsk.core.Matrix3D.create()
    o = root.occurrences.addNewComponent(I); o.component.name = 'Dörrbeslag'
    bygg_dorrbeslag2(des, o.component); o.isGrounded = True
    log('Dörrbeslag', sorted(b.name for b in o.component.bRepBodies))
    for n in BORT:
        p = up.itemByName(n)
        try:
            if p: p.deleteMe()
        except Exception as e: log('kunde inte ta bort', n, str(e)[:60])
    o2 = root.occurrences.addNewComponent(I); o2.component.name = 'Köpdelar dörr'
    bygg_kopdelar(des, o2.component, ev); o2.isGrounded = True
    tg = des.timeline.timelineGroups      # STEP-importen lägger grupper (Group1-3) med varningsstatus utan text: lös upp dem
    for i in range(tg.count - 1, -1, -1):
        g = tg.item(i)
        if g.name.startswith('Group'):
            log('grupp', g.name, g.healthState, g.errorOrWarningMessage[:80]); g.deleteMe(False)
    gom(des)
    FLEXMODE = False
    alla = [kontroll(des, root, 'standard')]
    dw, sh = ev('DorrBredd') / 2, ev('SyllH'); L = ev('Langd')
    bild('v08_dummy.png', (600, -5000, 1500), (0, 0, 1150), 2600)
    bild('v08_dorr_ute.png', (600, -5000, 1500), (0, 0, 1150), 2600)
    bild('v08_dorr_inne.png', (-600, 4500, 1500), (0, 0, 1150), 2600)
    bild('v08_las.png', (250, -700, sh + 1450), (10, -60, sh + 1300), 450)
    bild('v08_handtag.png', (400, -800, sh + 1150), (40, -60, sh + 1000), 600)
    bild('v08_gangjarn.png', (dw + 350, -500, sh + 450), (dw - 2, -50, sh + 205), 400)
    bild('v08_inne_las.png', (-300, 600, sh + 1400), (0, 0, sh + 1250), 500)
    bild('v08_dorr_bak.png', (-600, L + 5000, 1500), (0, L, 1150), 2600)
    orig = {k: up.itemByName(k).expression for k in FLEX}
    try:
        FLEXMODE = True
        for k, v in FLEX.items(): up.itemByName(k).expression = v
        alla.append(kontroll(des, root, 'flex (köpdelar ej omplacerade)'))
    finally:
        for k, v in orig.items(): up.itemByName(k).expression = v
        FLEXMODE = False
    alla.append(kontroll(des, root, 'återställt'))
    json.dump(alla, open(os.path.expanduser('~/code/buttercup/vaxthus/fusion/v08_resultat.json'), 'w'), ensure_ascii=False, indent=1)
    try: os.remove(OUT + 'v08_dummy.png')
    except Exception: pass
    a0, a1, a2 = alla
    if a0['antal_krock'] or a2['fel'] or a2['antal_krock'] or a2['ej_last'] or a2['kroppar_totalt'] != a0['kroppar_totalt'] or a1['fel'] or a1['ej_last'] or a1['antal_krock']:
        raise Exception('kontroll underkänd, sparar inte')
    d.save('Steg 6d: Wiberger-köpdelar (GJ60 nativt, GN425, EL2030-100, EL1035-200); flextest OK')
    log('sparad', TOPPNAMN)
