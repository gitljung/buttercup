# Steg 2b: flextest av halvbågen. Ändra huvudmått i mastern -> uppdatera halvbågen -> kontrollera -> återställ.
# Halvbågen sparas bara i slutet (efter återställning), med dolda hjälpplan.
NAMN = 'Växthus - halvbåge'
FLEX = {'Bredd': '4800 mm', 'Nockhojd': '4000 mm', 'Spetsighet': '300 mm'}
LOGF = os.path.expanduser('~/code/buttercup/vaxthus/fusion/v02b_resultat.json')


def kontroll(des, r, tag):
    des.computeAll()
    tl = des.timeline
    fel = [(tl.item(i).name, tl.item(i).errorOrWarningMessage[:80]) for i in range(tl.count) if tl.item(i).healthState != 0]
    ej = [s.name for s in r.sketches if not s.isFullyConstrained]
    tb = adsk.fusion.TemporaryBRepManager.get()
    bl = [b for b in r.bRepBodies]
    krock = []
    for i in range(len(bl)):
        for j in range(i + 1, len(bl)):
            x = tb.copy(bl[i]); y = tb.copy(bl[j])
            try:
                tb.booleanOperation(x, y, adsk.fusion.BooleanTypes.IntersectionBooleanType); v = x.volume * 1000
            except Exception: v = 0
            if v > 1: krock.append((bl[i].name, bl[j].name, round(v)))
    P = lambda n: des.allParameters.itemByName(n + '_Ref').value
    lang = {b.name: round(b.volume * 1000 / (P('PlyT') * 10 * P('BagB') * 10)) for b in bl if b.name.startswith(('Ytter', 'Inner'))}
    bbs = [b.boundingBox for b in bl]
    tot = [round(min(bb.minPoint.x for bb in bbs) * 10), round(max(bb.maxPoint.x for bb in bbs) * 10), round(max(bb.maxPoint.z for bb in bbs) * 10)]
    res = {'tag': tag, 'BagR_Ref': round(P('BagR') * 10, 1), 'kroppar': len(bl), 'fel': fel, 'ej_last': ej, 'krock': krock,
           'remsor_mm': lang, 'for_langa': [k for k, v in lang.items() if v > P('SkivaL') * 10], 'x_min_max_z_max': tot,
           'klossar': sum(1 for b in bl if not b.name.startswith(('Ytter', 'Inner', 'Lask')))}
    log(json.dumps(res, ensure_ascii=False))
    return res


def bild(fn, eye, target, ext):
    vp = app.activeViewport
    cam = vp.camera; cam.isSmoothTransition = False
    cam.target = P3(*[v / 10 for v in target]); cam.eye = P3(*[v / 10 for v in eye]); cam.upVector = adsk.core.Vector3D.create(0, 0, 1)
    cam.isFitView = False; cam.viewExtents = ext / 10
    vp.camera = cam; vp.camera = cam; vp.camera = cam; adsk.doEvents()
    vp.saveAsImageFile(OUT + fn, 1600, 1000)


def gom(r):
    for i in range(r.constructionPlanes.count): r.constructionPlanes.item(i).isLightBulbOn = False
    for i in range(r.constructionAxes.count): r.constructionAxes.item(i).isLightBulbOn = False
    for s in r.sketches: s.isVisible = False


def run(_context: str):
    allt = []
    md = master_doc(); md.activate()
    mdes = adsk.fusion.Design.cast(md.products.itemByProductType('DesignProductType'))
    up = mdes.userParameters
    orig = {k: up.itemByName(k).expression for k in FLEX}
    log('original', orig)
    try:
        for k, v in FLEX.items(): up.itemByName(k).expression = v
        save_wait(md, 'Flextest (tillfälligt): ' + ', '.join('%s %s' % kv for kv in FLEX.items()))
        D = Ed(NAMN)
        allt.append(kontroll(D.des, D.r, 'flex ' + json.dumps(FLEX, ensure_ascii=False)))
        gom(D.r)
        bild('v02b_dummy.png', (1200, -12000, 2000), (1200, 0, 2000), 5200)
        bild('v02b_flex_sida.png', (1200, -12000, 2000), (1200, 0, 2000), 5200)
        D.d.close(False)
    finally:
        md = master_doc(); md.activate()
        mdes = adsk.fusion.Design.cast(md.products.itemByProductType('DesignProductType'))
        for k, v in orig.items(): mdes.userParameters.itemByName(k).expression = v
        save_wait(md, 'Flextest återställt')
        log('master återställd')
    D = Ed(NAMN)
    allt.append(kontroll(D.des, D.r, 'standard'))
    gom(D.r)
    bild('v02b_standard_sida.png', (1000, -12000, 1800), (1000, 0, 1800), 5200)
    json.dump(allt, open(LOGF, 'w'), ensure_ascii=False, indent=1)
    try: os.remove(OUT + 'v02b_dummy.png')
    except Exception: pass
    if allt[-1]['fel'] or allt[-1]['krock']: raise Exception('standardläget har fel, sparar inte')
    D.d.save('Steg 2b: flextest OK, hjälpplan dolda')
    log('sparad', NAMN)
