# Steg 6c: dörrbeslag i dokumentet "Växthus" (efter steg 5).
#  - T-gångjärn 300: band på dörrbladets utsida + plåt på dörrstolpens utsida (samma plan), 2 per blad
#  - aktivt blad (höger sett utifrån): D-handtag ute (förenklad låda) + överfall för hänglås över mittspringan
#  - passivt blad (vänster): kantreglar på insidan, upptill och nedtill
#  Byggt vid främre gaveln, gångjärn speglade till båda bladen, allt speglat till bakre gaveln.
exec(open(os.path.expanduser('~/code/buttercup/vaxthus/fusion/v06_gavlar.py')).read().split('\ndef run(')[0])
NYA7 = [
    ('GangjarnL', '300 mm', 'mm', 'T-gångjärn: bandets längd'),
    ('GangjarnB', '40 mm', 'mm', 'T-gångjärn: bandets bredd'),
    ('GangjarnPlatB', '70 mm', 'mm', 'T-gångjärn: plåtens bredd på stolpen'),
    ('GangjarnPlatH', '150 mm', 'mm', 'T-gångjärn: plåtens höjd'),
    ('GangjarnZ', '250 mm', 'mm', 'T-gångjärn: mitt från dörrbladets över-/underkant'),
    ('BeslagT', '3 mm', 'mm', 'Dörrbeslag: godstjocklek'),
    ('HandtagZ', '1000 mm', 'mm', 'Handtag och överfall: höjd över syllens ovansida'),
    ('HandtagL', '200 mm', 'mm', 'D-handtag: längd'),
    ('HandtagB', '25 mm', 'mm', 'D-handtag: bredd'),
    ('HandtagD', '60 mm', 'mm', 'D-handtag: utstick från dörren'),
    ('OverfallZ', '1300 mm', 'mm', 'Överfall: mitt över syllens ovansida (ovanför handtaget)'),
    ('OverfallL', '150 mm', 'mm', 'Överfall: längd över mittspringan'),
    ('OverfallB', '40 mm', 'mm', 'Överfall: bredd'),
    ('KantregelL', '300 mm', 'mm', 'Kantregel: längd'),
    ('KantregelB', '20 mm', 'mm', 'Kantregel: bredd/djup'),
]


def box_xz(D, comp, name, x0, x1, z0, z1, ex0, ex1, ez0, ez1, ystart, ydist, ylo):
    sk = comp.sketches.add(comp.xZConstructionPlane); sk.name = 'Skiss ' + name
    S = Skiss(D, sk, 'x', 'z'); S.rect(x0, x1, z0, z1, ex0, ex1, ez0, ez1)
    rep = S.report()
    if not rep[1]: raise Exception('ej låst: ' + name)
    b = D.ext(S.biggest(), 'y', ystart, ydist, ylo, name).bodies.item(0); b.name = name
    return b


def bygg_dorrbeslag(des, comp):
    D = K(des, comp); ev = D.ev
    sb2, T = ev('StolpeB') / 2, ev('BeslagT')
    dw, sp, sh, dh = ev('DorrBredd') / 2, ev('DorrSpel'), ev('SyllH'), ev('DorrHojd')
    ut = ('StolpeB / 2', 'BeslagT', -sb2 - T)             # på utsidan (framför y = -StolpeB/2)
    gj = []
    for nm, zc, ezc in (('nedre', sh + sp + ev('GangjarnZ'), 'SyllH + DorrSpel + GangjarnZ'),
                        ('övre', sh + dh - sp - ev('GangjarnZ'), 'SyllH + DorrHojd - DorrSpel - GangjarnZ')):
        gb, gh = ev('GangjarnB') / 2, ev('GangjarnPlatH') / 2
        gj.append(box_xz(D, comp, 'Gångjärn band ' + nm, dw - sp - ev('GangjarnL'), dw - sp, zc - gb, zc + gb,
                         'DorrBredd / 2 - DorrSpel - GangjarnL', 'DorrBredd / 2 - DorrSpel', ezc + ' - GangjarnB / 2', ezc + ' + GangjarnB / 2', *ut))
        gj.append(box_xz(D, comp, 'Gångjärn plåt ' + nm, dw, dw + ev('GangjarnPlatB'), zc - gh, zc + gh,
                         'DorrBredd / 2', 'DorrBredd / 2 + GangjarnPlatB', ezc + ' - GangjarnPlatH / 2', ezc + ' + GangjarnPlatH / 2', *ut))
    mirror(comp, gj, comp.yZConstructionPlane, 'Gångjärn vänster blad (spegling)')
    # aktivt blad (x > 0): handtag + överfall
    zh = sh + ev('HandtagZ'); xh = sp / 2 + ev('DorrRamB') / 2
    box_xz(D, comp, 'D-handtag', xh - ev('HandtagB') / 2, xh + ev('HandtagB') / 2, zh - ev('HandtagL') / 2, zh + ev('HandtagL') / 2,
           'DorrSpel / 2 + DorrRamB / 2 - HandtagB / 2', 'DorrSpel / 2 + DorrRamB / 2 + HandtagB / 2', 'SyllH + HandtagZ - HandtagL / 2', 'SyllH + HandtagZ + HandtagL / 2',
           'StolpeB / 2', 'HandtagD', -sb2 - ev('HandtagD'))
    zo = sh + ev('OverfallZ')
    ol, ob = ev('OverfallL') / 2, ev('OverfallB') / 2
    box_xz(D, comp, 'Överfall hänglås', -ol, ol, zo - ob, zo + ob, 'OverfallL / 2', 'OverfallL / 2',
           'SyllH + OverfallZ - OverfallB / 2', 'SyllH + OverfallZ + OverfallB / 2', *ut)
    # passivt blad (x < 0): kantreglar på insidan (y = -StolpeB/2 + DorrRamT)
    xk = sp / 2 + ev('DorrRamB') / 2; kb = ev('KantregelB') / 2; kl = ev('KantregelL'); ins = ev('StolpeB') / 2 - ev('DorrRamT')
    inn = ('StolpeB / 2 - DorrRamT', 'KantregelB', -ins)
    box_xz(D, comp, 'Kantregel övre', -(xk + kb), -(xk - kb), sh + dh - sp - kl, sh + dh - sp,
           'DorrSpel / 2 + DorrRamB / 2 + KantregelB / 2', 'DorrSpel / 2 + DorrRamB / 2 - KantregelB / 2', 'SyllH + DorrHojd - DorrSpel - KantregelL', 'SyllH + DorrHojd - DorrSpel', *inn)
    box_xz(D, comp, 'Kantregel nedre', -(xk + kb), -(xk - kb), sh + sp, sh + sp + kl,
           'DorrSpel / 2 + DorrRamB / 2 + KantregelB / 2', 'DorrSpel / 2 + DorrRamB / 2 - KantregelB / 2', 'SyllH + DorrSpel', 'SyllH + DorrSpel + KantregelL', *inn)
    mirror(comp, [comp.bRepBodies.item(i) for i in range(comp.bRepBodies.count)], bak_plan(comp, ev), 'Bakre gaveln (spegling)')
    def bas(b, xm, ym):
        n = b.name
        for k in ('Gångjärn band', 'Gångjärn plåt', 'D-handtag', 'Överfall hänglås', 'Kantregel'):
            if n.startswith(k):
                zm = (b.boundingBox.minPoint.z + b.boundingBox.maxPoint.z) * 5
                if k.startswith('Gångjärn') or k == 'Kantregel': return k + (' övre' if zm > sh + dh / 2 else ' nedre')
                return k
        return n.split(' (')[0]
    namnge(comp, ev, bas)
    for b in comp.bRepBodies: b.appearance = zink(des)
    comp.partNumber = 'DORRBESLAG'; comp.description = 'T-gångjärn 300, D-handtag, överfall för hänglås, kantreglar (köpdelar, förenklade)'
    for s in comp.sketches: s.isVisible = False


def run(_context: str):
    keepalive()
    d = find_doc(TOPPNAMN)
    if d: d.close(False)
    d = app.documents.open(dfile(TOPPNAMN)); d.activate()
    des = adsk.fusion.Design.cast(d.products.itemByProductType('DesignProductType'))
    root = des.rootComponent; up = des.userParameters
    ev = lambda s: des.unitsManager.evaluateExpression(s, 'mm') * 10
    if not des.allComponents.itemByName('Dörrar'): raise Exception('steg 5 saknas i sparad modell')
    for n, e, u, c in NYA7:
        p = up.itemByName(n)
        if p: p.expression = e
        else: up.add(n, VI(e), u, c).isFavorite = True
    for o in list(root.occurrences):
        if o.component.name == 'Dörrbeslag': o.deleteMe()
    o = root.occurrences.addNewComponent(adsk.core.Matrix3D.create()); o.component.name = 'Dörrbeslag'
    bygg_dorrbeslag(des, o.component); o.isGrounded = True
    log('Dörrbeslag', sorted(b.name for b in o.component.bRepBodies))
    gom(des)
    alla = [kontroll(des, root, 'standard')]
    dw, sh = ev('DorrBredd') / 2, ev('SyllH')
    bild('v07_dummy.png', (0, -6000, 1300), (0, 0, 1200), 2600)
    bild('v07_dorr_ute.png', (600, -5000, 1500), (0, 0, 1150), 2600)
    bild('v07_dorr_inne.png', (-600, 4500, 1500), (0, 0, 1150), 2600)
    bild('v07_gangjarn.png', (dw + 500, -900, sh + 700), (dw, 0, sh + 260), 700)
    orig = {k: up.itemByName(k).expression for k in FLEX}
    try:
        for k, v in FLEX.items(): up.itemByName(k).expression = v
        alla.append(kontroll(des, root, 'flex'))
    finally:
        for k, v in orig.items(): up.itemByName(k).expression = v
    alla.append(kontroll(des, root, 'återställt'))
    json.dump(alla, open(os.path.expanduser('~/code/buttercup/vaxthus/fusion/v07_resultat.json'), 'w'), ensure_ascii=False, indent=1)
    try: os.remove(OUT + 'v07_dummy.png')
    except Exception: pass
    a0, a1, a2 = alla
    if a2['fel'] or a2['antal_krock'] or a2['ej_last'] or a2['kroppar_totalt'] != a0['kroppar_totalt'] or a1['fel'] or a1['ej_last'] or a1['antal_krock']:
        raise Exception('kontroll underkänd, sparar inte')
    d.save('Steg 6c: dörrbeslag (T-gångjärn, handtag, överfall, kantreglar); flextest OK')
    log('sparad', TOPPNAMN)
