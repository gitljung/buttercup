# Steg 3 (struktur A): ETT dokument "Växthus" med alla parametrar + komponentträd.
#   Växthus (topp)
#   └─ Båge  (delmontage, mönstrat AntalBagar st längs y med BagCC)
#       ├─ Halvbåge          (höger, byggd med skisser/relationer)
#       └─ Halvbåge (vänster) = samma komponent vriden 180° kring z
# Ändra en parameter (Ändra parametrar) -> allt följer direkt. Inga Derive-länkar.
exec(open(os.path.expanduser('~/code/buttercup/vaxthus/fusion/v01_master.py')).read().split('\ndef run(')[0])
exec(open(os.path.expanduser('~/code/buttercup/vaxthus/fusion/_halvbage.py')).read())
TOPPNAMN = 'Växthus'
FLEX = {'Bredd': '4800 mm', 'Nockhojd': '4000 mm', 'Spetsighet': '300 mm', 'Langd': '12000 mm', 'Bagavstand': '1000 mm'}
LOG3 = os.path.expanduser('~/code/buttercup/vaxthus/fusion/v03_resultat.json')


class K:
    """byggkontext för en komponent i samma dokument (parametrarna ligger i dokumentet)"""
    def __init__(self, des, comp):
        self.des, self.r = des, comp
        self.ef = comp.features.extrudeFeatures
    def E(self, s): return s
    def ev(self, s): return self.des.unitsManager.evaluateExpression(s, 'mm') * 10


def bodies_world(root):
    out = []
    for occ in root.allOccurrences:
        for b in occ.bRepBodies:
            out.append((occ.fullPathName + '/' + b.name, b))
    return out


def kontroll(des, root, tag):
    des.computeAll(); adsk.doEvents()
    tl = des.timeline
    fel = [(tl.item(i).name, tl.item(i).errorOrWarningMessage[:80]) for i in range(tl.count) if tl.item(i).healthState != 0]
    ej = []
    for c in des.allComponents:
        for s in c.sketches:
            if not s.isFullyConstrained: ej.append(c.name + '/' + s.name)
    bw = bodies_world(root)
    tb = adsk.fusion.TemporaryBRepManager.get()
    krock = []
    bbs = [b.boundingBox for _, b in bw]
    for i in range(len(bw)):
        for j in range(i + 1, len(bw)):
            if not bbs[i].intersects(bbs[j]): continue
            x = tb.copy(bw[i][1]); y = tb.copy(bw[j][1])
            try:
                tb.booleanOperation(x, y, adsk.fusion.BooleanTypes.IntersectionBooleanType); v = x.volume * 1000
            except Exception: v = 0
            if v > 1: krock.append((bw[i][0], bw[j][0], round(v)))
    P = lambda n: des.userParameters.itemByName(n).value * 10
    halv = des.allComponents.itemByName('Halvbåge')
    lang = {b.name: round(b.volume * 1000 / (P('PlyT') * P('BagB'))) for b in halv.bRepBodies if b.name.startswith(('Ytter', 'Inner'))}
    allbb = [b.boundingBox for _, b in bw]
    ext = [round(min(bb.minPoint.x for bb in allbb) * 10), round(max(bb.maxPoint.x for bb in allbb) * 10),
           round(min(bb.minPoint.y for bb in allbb) * 10), round(max(bb.maxPoint.y for bb in allbb) * 10),
           round(max(bb.maxPoint.z for bb in allbb) * 10)]
    bagar = sum(1 for o in root.allOccurrences if o.component.name == 'Båge')
    try:
        ax = halv.constructionAxes.itemByName('Bågens centrumaxel').geometry
        log(tag[:8], 'axel', [round(v * 10) for v in ax.origin.asArray()], [round(v, 3) for v in ax.direction.asArray()])
        for f in halv.features.circularPatternFeatures:
            log(tag[:8], f.name, f.totalAngle.expression, round(math.degrees(f.totalAngle.value), 2), [[round(v) for v in bbmm(b)] for b in f.bodies])
    except Exception as e: log('axellogg FEL', str(e)[:80])
    res = {'tag': tag, 'BagR': round(P('BagR'), 1), 'AntalBagar': des.userParameters.itemByName('AntalBagar').value,
           'bage_occ': bagar, 'kroppar_totalt': len(bw), 'kroppar_halvbage': halv.bRepBodies.count,
           'fel': fel, 'ej_last': ej, 'krock': krock[:10], 'antal_krock': len(krock), 'remsor_mm': lang,
           'for_langa': [k for k, v in lang.items() if v > P('SkivaL')], 'x0_x1_y0_y1_zmax': ext}
    log(json.dumps(res, ensure_ascii=False))
    return res


def bild(fn, eye, target, ext):
    vp = app.activeViewport
    cam = vp.camera; cam.isSmoothTransition = False
    cam.target = P3(*[v / 10 for v in target]); cam.eye = P3(*[v / 10 for v in eye]); cam.upVector = adsk.core.Vector3D.create(0, 0, 1)
    cam.isFitView = False; cam.viewExtents = ext / 10
    vp.camera = cam; vp.camera = cam; vp.camera = cam; adsk.doEvents()
    vp.saveAsImageFile(OUT + fn, 1600, 1000)


def gom(des):
    for c in des.allComponents:
        for i in range(c.constructionPlanes.count): c.constructionPlanes.item(i).isLightBulbOn = False
        for i in range(c.constructionAxes.count): c.constructionAxes.item(i).isLightBulbOn = False
        for s in c.sketches: s.isVisible = False


def run(_context: str):
    import time
    # gamla flerfilsförsöket (egna filer från i dag) bort
    for n in ('Växthus - derivtest', 'Växthus - halvbåge', 'Växthus - parametrar', TOPPNAMN):
        for x in list(app.documents):
            try:
                if bas(x.name) == n: x.close(False)
            except Exception: pass
        f = dfile(n)
        if f:
            f.deleteMe(); log('raderade', n)
    for _ in range(10):
        if not any(dfile(n) for n in ('Växthus - halvbåge', 'Växthus - parametrar', TOPPNAMN)): break
        time.sleep(2); adsk.doEvents()

    for x in list(app.documents):      # osparade rester från misslyckade försök (har komponenten Båge)
        try:
            dx = adsk.fusion.Design.cast(x.products.itemByProductType('DesignProductType'))
            if not x.isSaved and dx and dx.allComponents.itemByName('Båge'): x.close(False)
        except Exception: pass
    d = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    des = adsk.fusion.Design.cast(d.products.itemByProductType('DesignProductType'))
    des.designType = adsk.fusion.DesignTypes.ParametricDesignType
    root = des.rootComponent
    up = des.userParameters
    for n, e, u, c in PARAMS:
        up.add(n, VI(e), u, c).isFavorite = True
    log('parametrar', up.count)

    # delmontage Båge med Halvbåge
    I = adsk.core.Matrix3D.create()
    occB = root.occurrences.addNewComponent(I); compB = occB.component; compB.name = 'Båge'
    occH = compB.occurrences.addNewComponent(I); compH = occH.component; compH.name = 'Halvbåge'
    res_h = bygg_halvbage(K(des, compH))
    rot = adsk.core.Matrix3D.create(); rot.setToRotation(math.pi, adsk.core.Vector3D.create(0, 0, 1), P3(0, 0, 0))
    occV = compB.occurrences.addExistingComponent(compH, rot)
    occB.isGrounded = True
    log('delmontage Båge: höger + vänster')

    # mönster av bågar längs huset
    rp = root.features.rectangularPatternFeatures
    for sg in ('', '-'):
        inp = rp.createInput(coll([occB]), root.yConstructionAxis, VI('AntalBagar'), VI(sg + 'BagCC'), adsk.fusion.PatternDistanceType.SpacingPatternDistanceType)
        inp.setDirectionTwo(root.xConstructionAxis, VI('1'), VI('0 mm'))   # standard är 3 i riktning två!
        f = rp.add(inp)
        des.computeAll()
        ys = [o.transform2.translation.y * 10 for o in root.occurrences if o.component.name == 'Båge']
        if max(ys) > 100: f.name = 'Bågar längs huset'; break
        f.deleteMe()
    log('bågar y', sorted(round(y) for y in [o.transform2.translation.y * 10 for o in root.occurrences if o.component.name == 'Båge']))
    gom(des)
    os.makedirs(OUT, exist_ok=True)

    alla = [kontroll(des, root, 'standard')]
    bild('v03_dummy.png', (9000, -6000, 6000), (0, 5000, 1800), 9000)
    bild('v03_standard_iso.png', (9000, -6000, 6000), (0, 5000, 1800), 9000)
    bild('v03_standard_gavel.png', (0, -12000, 1800), (0, 0, 1800), 5200)

    orig = {k: up.itemByName(k).expression for k in FLEX}
    try:
        for k, v in FLEX.items(): up.itemByName(k).expression = v
        alla.append(kontroll(des, root, 'flex ' + json.dumps(FLEX, ensure_ascii=False)))
        bild('v03_flex_iso.png', (10000, -6000, 6500), (0, 6000, 2000), 11000)
        bild('v03_flex_gavel.png', (0, -14000, 2000), (0, 0, 2000), 6000)
    finally:
        for k, v in orig.items(): up.itemByName(k).expression = v
    alla.append(kontroll(des, root, 'återställt'))
    json.dump({'halvbage': {k: v for k, v in res_h.items() if k != 'lista'}, 'kontroller': alla}, open(LOG3, 'w'), ensure_ascii=False, indent=1)
    try: os.remove(OUT + 'v03_dummy.png')
    except Exception: pass
    a0, a2 = alla[0], alla[-1]
    if a2['fel'] or a2['antal_krock'] or a2['ej_last'] or a2['remsor_mm'] != a0['remsor_mm'] or a2['bage_occ'] != a2['AntalBagar']:
        raise Exception('standardläget efter flextest skiljer sig/har fel, sparar inte')
    d.saveAs(TOPPNAMN, folder(), 'Steg 3: ett dokument, parametrar + Båge (2 halvbågar) mönstrad längs huset; flextest OK', '')
    log('sparad', TOPPNAMN)
