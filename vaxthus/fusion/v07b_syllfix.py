# Rättning: bakre vänstra gavelsyllen saknas (speglingen i steg 4 fick samma kropp två gånger).
exec(open(os.path.expanduser('~/code/buttercup/vaxthus/fusion/v06_gavlar.py')).read().split('\ndef run(')[0])


def run(_context: str):
    keepalive()
    d = find_doc(TOPPNAMN)
    if d: d.close(False)
    d = app.documents.open(dfile(TOPPNAMN)); d.activate()
    des = adsk.fusion.Design.cast(d.products.itemByProductType('DesignProductType'))
    root = des.rootComponent
    ev = lambda s: des.unitsManager.evaluateExpression(s, 'mm') * 10
    sc = des.allComponents.itemByName('Syllram')
    gav = [b for b in sc.bRepBodies if b.name.startswith('Syll gavel')]
    log('gavelsyllar före', [b.name for b in gav])
    if len(gav) == 3:
        Lm = ev('Langd') / 2
        fv = [b for b in gav if (b.boundingBox.minPoint.x + b.boundingBox.maxPoint.x) < 0 and (b.boundingBox.minPoint.y + b.boundingBox.maxPoint.y) * 5 < Lm][0]
        mid = sc.constructionPlanes.itemByName('Mittplan längs (Langd / 2)')
        mirror(sc, [fv], mid, 'Syll gavel bak vänster (spegling)')
        ratta_namn(des, ev)
    log('Syllram efter', sorted(b.name for b in sc.bRepBodies))
    if sum(1 for b in sc.bRepBodies if b.name.startswith('Syll gavel')) != 4: raise Exception('fortfarande fel antal gavelsyllar')
    gom(des)
    hb = ev('HalvBredd'); L = ev('Langd')
    bild('v07b_dummy.png', (-hb - 1500, L + 1500, 900), (-hb + 500, L, 100), 2200)
    bild('v07b_syllhorn_bak.png', (-hb - 1500, L + 1500, 900), (-hb + 500, L, 100), 2200)
    alla = [kontroll(des, root, 'standard')]
    orig = {k: des.userParameters.itemByName(k).expression for k in FLEX}
    try:
        for k, v in FLEX.items(): des.userParameters.itemByName(k).expression = v
        alla.append(kontroll(des, root, 'flex'))
    finally:
        for k, v in orig.items(): des.userParameters.itemByName(k).expression = v
    alla.append(kontroll(des, root, 'återställt'))
    try: os.remove(OUT + 'v07b_dummy.png')
    except Exception: pass
    a0, a1, a2 = alla
    if a2['fel'] or a2['antal_krock'] or a2['ej_last'] or a2['kroppar_totalt'] != a0['kroppar_totalt'] or a1['fel'] or a1['antal_krock']:
        raise Exception('kontroll underkänd, sparar inte')
    d.save('Rättning: bakre vänstra gavelsyllen tillagd')
    log('sparad', TOPPNAMN)
