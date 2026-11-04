# Steg 12 (monteringsanalysen + Victor "ja"):
#  1. Nocklask 12 mm plywood på bågarnas sidor över nocken (Norhage-princip) -> bågen blir en enhet som byggs på marken.
#     Gavelbågarna bara på insidan (utsidan har gavelbågens låsprofil). Överkanten NockLaskAvdrag under bågens yttersida
#     så att nockens låsprofil går fri.
#  2. Nockregeln i bitar mellan bågarna (BagCC - BagB - 2 * NockLaskT), mönstrad AntalBagar - 1. Vinklar nock utgår (lasken tar över).
#  3. Hanbjälke 45x120 på HanZ (2400) på bågarnas +y-sida, ändarna i bågens yttre kant vid överkanten. Inte på gavelbågarna
#     (där bär överliggare + stolpar). Mönstrad AntalBagar - 2.
#  4. Sidoregel 19 mm (2,5 mm spel per sida i facket, går att trä).
import builtins as _bi
_o = _bi.open
def open(f, m='r', *a, **k):
    if 'b' not in m and 'encoding' not in k and not a: k['encoding'] = 'utf-8'
    return _o(f, m, *a, **k)
exec(open(os.path.expanduser('~/code/buttercup/vaxthus/fusion/v11_nock.py'), encoding='utf-8').read().split('\ndef bygg_nock(')[0])
NYA12 = [
    ('NockLaskT', '12 mm', 'mm', 'Nocklask: plywoodtjocklek (samma skiva som lamellerna)'),
    ('NockLaskL', '600 mm', 'mm', 'Nocklask: längd (horisontellt, total)'),
    ('NockLaskAvdrag', 'ProfilH + 10 mm', 'mm', 'Nocklask: överkant under bågens yttersida (nockprofilen går fri)'),
    ('HanZ', '2400 mm', 'mm', 'Hanbjälke: höjd till mitten (beräknat 2,3-2,5 m bäst, högre hjälper inte)'),
    ('HanT', '45 mm', 'mm', 'Hanbjälke: tjocklek (längs huset)'),
    ('HanH', '120 mm', 'mm', 'Hanbjälke: höjd'),
    ('HanX', '-BagCx + sqrt( ( BagR + BagDjup / 2 ) * ( BagR + BagDjup / 2 ) - ( HanZ + HanH / 2 - BagCz ) * ( HanZ + HanH / 2 - BagCz ) )', 'mm',
     'Härledd: hanbjälkens halva längd (änden i bågens yttre kant vid överkanten)'),
]


def pat(comp, bodies, qty, dist, name, target):
    """mönster längs y; behåll riktningen där mönstrets kroppar når max y = target (mm)"""
    rp = comp.features.rectangularPatternFeatures
    for sg in ('', '-'):
        inp = rp.createInput(coll(bodies), comp.yConstructionAxis, VI(qty), VI(sg + dist), adsk.fusion.PatternDistanceType.SpacingPatternDistanceType)
        inp.setDirectionTwo(comp.xConstructionAxis, VI('1'), VI('0 mm'))
        f = rp.add(inp)
        ym = max(f.bodies.item(i).boundingBox.maxPoint.y * 10 for i in range(f.bodies.count)) if f.bodies.count else -1e9
        if abs(ym - target) < 0.5: f.name = name; return f
        log(name, 'fel riktning', round(ym, 1), round(target, 1)); f.deleteMe()
    raise Exception('mönster fel: ' + name)


def run(_context: str):
    global FLEXMODE
    keepalive()
    d = find_doc(TOPPNAMN)
    if d: d.close(False)
    d = app.documents.open(dfile(TOPPNAMN)); d.activate()
    des = adsk.fusion.Design.cast(d.products.itemByProductType('DesignProductType'))
    root = des.rootComponent; up = des.userParameters
    ev = lambda s: des.unitsManager.evaluateExpression(s, 'mm') * 10
    for n, e, u, c in NYA12:
        p = up.itemByName(n)
        if p: p.expression = e
        else: up.add(n, VI(e), u, c).isFavorite = True
    up.itemByName('SidoregelT').expression = '19 mm'
    up.itemByName('SidoregelT').comment = 'Sidoregel 19x95 (hyvlad): 2,5 mm spel per sida i facket så att den går att trä'
    # --- vinklar nock bort ---
    for o in list(root.occurrences):
        if o.component.name in ('Vinklar nock', 'Nocklask och hanbjälke'): log('tar bort', o.component.name); o.deleteMe()
    # --- nockregel i bitar ---
    nc = des.allComponents.itemByName('Nock och sidoreglar'); D = K(des, nc)
    f0 = [f for f in nc.features.extrudeFeatures if f.name == 'Nockregel']
    sk = nc.sketches.itemByName('Nockregel')
    if f0: f0[0].deleteMe()
    for ff in list(nc.features.extrudeFeatures):   # gamla hela nockregeln (oavsett featurenamn)
        try:
            for i in range(ff.bodies.count):
                bb = ff.bodies.item(i).boundingBox
                if (bb.maxPoint.y - bb.minPoint.y) * 10 > 3000 and abs((bb.maxPoint.x + bb.minPoint.x) * 5) < 1:
                    log('tar bort gammal nockregel-feature', ff.name); ff.deleteMe(); break
        except Exception as e: log('kollfel', str(e)[:80])
    for f in list(nc.features.rectangularPatternFeatures):
        if f.name == 'Nockregel bitar': f.deleteMe()
    prof = max([sk.profiles.item(i) for i in range(sk.profiles.count)], key=lambda p: p.areaProperties().area)
    lo = ev('BagB / 2 + NockLaskT')
    f = D.ext(prof, 'y', 'BagB / 2 + NockLaskT', 'BagCC - BagB - 2 * NockLaskT', lo, 'Nockregel bit')
    nb0 = f.bodies.item(0); nb0.name = 'Nockregel bit'
    L = ev('Langd')
    pat(nc, [nb0], 'AntalBagar - 1', 'BagCC', 'Nockregel bitar', L - ev('BagB / 2 + NockLaskT'))
    for b in nc.bRepBodies:
        if b.name.startswith(('Body', 'Nockregel')) and abs((b.boundingBox.maxPoint.x + b.boundingBox.minPoint.x) * 5) < 1: b.name = 'Nockregel bit'
    # --- ny komponent: nocklask + hanbjälke ---
    o = root.occurrences.addNewComponent(adsk.core.Matrix3D.create()); o.component.name = 'Nocklask och hanbjälke'
    c = o.component; D = K(des, c)
    ri, ro = 'BagR - BagDjup / 2', 'BagR + BagDjup / 2 - NockLaskAvdrag'
    p = band_x(D, c, ri, ro, 'NockLaskL / 2', 'Skiss Nocklask +y', full=True)
    f = D.ext(p, 'y', 'BagB / 2', 'NockLaskT', ev('BagB / 2'), 'Nocklask +y'); la = f.bodies.item(0); la.name = 'Nocklask'
    pat(c, [la], 'AntalBagar - 1', 'BagCC', 'Nocklask +y mönster', L - ev('BagCC') + ev('BagB / 2 + NockLaskT'))
    p = band_x(D, c, ri, ro, 'NockLaskL / 2', 'Skiss Nocklask -y', full=True)
    y1 = ev('BagCC - BagB / 2 - NockLaskT')
    f = D.ext(p, 'y', 'BagCC - BagB / 2 - NockLaskT', 'NockLaskT', y1, 'Nocklask -y'); lb = f.bodies.item(0); lb.name = 'Nocklask'
    n_las = c.bRepBodies.count
    pat(c, [lb], 'AntalBagar - 1', 'BagCC', 'Nocklask -y mönster', L - ev('BagB / 2'))
    # hanbjälke
    sk = c.sketches.add(c.xZConstructionPlane); sk.name = 'Skiss Hanbjälke'
    S = Skiss(D, sk, 'x', 'z'); hx, hz, hh = ev('HanX'), ev('HanZ'), ev('HanH')
    S.rect(-hx, hx, hz - hh / 2, hz + hh / 2, 'HanX', 'HanX', 'HanZ - HanH / 2', 'HanZ + HanH / 2'); log(S.report())
    if not S.report()[1]: raise Exception('ej låst hanbjälke')
    f = D.ext(S.biggest(), 'y', 'BagCC + BagB / 2', 'HanT', ev('BagCC + BagB / 2'), 'Hanbjälke'); hb0 = f.bodies.item(0); hb0.name = 'Hanbjälke'
    pat(c, [hb0], 'AntalBagar - 2', 'BagCC', 'Hanbjälke mönster', L - ev('BagCC') + ev('BagB / 2 + HanT'))
    for b in c.bRepBodies:
        dz = (b.boundingBox.maxPoint.z - b.boundingBox.minPoint.z) * 10
        b.name = 'Hanbjälke' if dz < hh + 1 else 'Nocklask'
        b.appearance = plywood(des) if b.name == 'Nocklask' else tra(des)
    for s in c.sketches: s.isVisible = False
    c.partNumber = 'VH-NOCKLASK-HAN'; c.description = 'Nocklask 12 mm plywood (båda sidor, gavelbågar insida) + hanbjälke 45x120 på HanZ, 2 x M10 per ände'
    o.isGrounded = True
    des.computeAll()
    log('kroppar komp', c.bRepBodies.count, 'nockregelbitar', sum(1 for b in nc.bRepBodies if b.name == 'Nockregel bit'))
    # antal + längder för listorna (samma format som v11)
    lg = langder(des, des.allComponents.itemByName('Låsprofiler'), ev)
    lg['Låsprofil nock'] = [round(ev('Langd + BagB'))]
    def pval(k):
        q = up.itemByName(k)
        return round(q.value, 3) if q.unit == '' else round(ev(k), 1)
    pv = {k: pval(k) for k in ('Bredd', 'Langd', 'Nockhojd', 'BagR', 'BagDjup', 'BagLangd', 'AntalBagar', 'BagCC', 'NedreMellan', 'OvreMellan',
                               'DorrBredd', 'DorrHojd', 'StolpeB', 'SyllUtstick', 'ProfilL', 'ProfilSkruvCC', 'FilmOverlapp', 'BagB',
                               'PlyT', 'Lameller', 'LamellT', 'KlossH', 'KlossL', 'FackKlossL', 'SidoregelT', 'SidoregelH', 'NockT', 'NockH',
                               'SyllB', 'SyllH', 'SkivaL', 'NockPlatB', 'NockPlatT', 'HalvBredd', 'NockLaskT', 'NockLaskL', 'HanZ', 'HanX', 'HanT', 'HanH')}
    gom(des)
    FLEXMODE = False
    alla = [kontroll(des, root, 'standard')]
    json.dump({'parametrar': pv, 'lasprofil_mm': lg, 'antal': antal_alla(des), 'remsor_mm': alla[0]['remsor_mm']},
              open(os.path.expanduser('~/code/buttercup/vaxthus/fusion/v11_antal.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    hb = ev('HalvBredd'); nk = ev('NockOK')
    bild('v12_dummy.png', (7000, -7000, 4500), (0, L / 2, 1700), 9000)
    bild('v12_iso.png', (7000, -7000, 4500), (0, L / 2, 1700), 9000)
    bild('v12_inifran.png', (hb - 600, -700, 1300), (0, L / 2, 2400), 5600)
    bild('v12_nock.png', (800, 1250 - 1100, nk + 300), (0, 1250 + 300, nk - 120), 900)
    bild('v12_han.png', (hb - 300, 2500 - 1500, 2100), (900, 2500, 2400), 1500)
    bild('v12_gavel.png', (1200, -9000, 1900), (0, 0, 1800), 4800)
    orig = {k: up.itemByName(k).expression for k in FLEX}
    try:
        FLEXMODE = True
        for k, v in FLEX.items(): up.itemByName(k).expression = v
        alla.append(kontroll(des, root, 'flex (köpdelar ej omplacerade)'))
        bild('v12_flex.png', (8000, -8000, 5000), (0, 6000, 1900), 10500)
    finally:
        for k, v in orig.items(): up.itemByName(k).expression = v
        FLEXMODE = False
    alla.append(kontroll(des, root, 'återställt'))
    json.dump(alla, open(os.path.expanduser('~/code/buttercup/vaxthus/fusion/v12_resultat.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    try: os.remove(OUT + 'v12_dummy.png')
    except Exception: pass
    a0, a1, a2 = alla
    if a0['antal_krock'] or a0['fel'] or a0['ej_last'] or a2['fel'] or a2['antal_krock'] or a2['ej_last'] or a2['kroppar_totalt'] != a0['kroppar_totalt'] or a1['fel'] or a1['ej_last'] or a1['antal_krock']:
        raise Exception('kontroll underkänd, sparar inte')
    d.save('Steg 12: nocklask + nockregel i bitar + hanbjälke HanZ 2400 + sidoregel 19 mm; flextest OK')
    log('sparad', TOPPNAMN)
    try:
        sp = os.path.expanduser('~/code/buttercup/vaxthus/fusion/export/Vaxthus.step')
        em = des.exportManager; ok = em.execute(em.createSTEPExportOptions(sp, root)); log('STEP', ok, os.path.getsize(sp))
    except Exception as e: log('STEP FEL', str(e)[:200])
