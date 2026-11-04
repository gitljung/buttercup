# Steg 16 (Victor 2026-11-04): plywood 12 x 2500 x 1200 i stället för 15. Fläns 1 x 12 x 95, nocklask 12 (= LamellT), kloss 45 kvar -> djup 69.
import builtins as _bi
_o = _bi.open
def open(f, m='r', *a, **k):
    if 'b' not in m and 'encoding' not in k and not a: k['encoding'] = 'utf-8'
    return _o(f, m, *a, **k)
exec(open(os.path.expanduser('~/code/buttercup/vaxthus/fusion/v15_nockbalk.py'), encoding='utf-8').read().split('\ndef run(')[0])
def run(_context: str):
    global FLEXMODE
    keepalive()
    d = find_doc(TOPPNAMN)
    if d: d.close(False)
    d = app.documents.open(dfile(TOPPNAMN)); d.activate()
    des = adsk.fusion.Design.cast(d.products.itemByProductType('DesignProductType'))
    root = des.rootComponent; up = des.userParameters
    ev = lambda s: des.unitsManager.evaluateExpression(s, 'mm') * 10
    for n in ('PlyT', 'LamellT', 'Lameller', 'NockLaskT', 'BagDjup'): log('före', n, up.itemByName(n).expression)
    up.itemByName('LamellT').expression = '12 mm'
    if 'LamellT' not in up.itemByName('PlyT').expression: up.itemByName('PlyT').expression = 'Lameller * LamellT'
    up.itemByName('LamellT').comment = 'Plywoodtjocklek (Byggmax 12 x 2500 x 1200)'
    des.computeAll()
    for n in ('PlyT', 'LamellT', 'NockLaskT', 'BagDjup', 'HanZ', 'HanXu', 'NockOK'): log('efter', n, up.itemByName(n).expression, round(ev(n), 1) if n != 'x' else '')
    L = ev('Langd')
    lg = langder(des, des.allComponents.itemByName('Låsprofiler'), ev)
    lg['Låsprofil nock'] = [round(ev('Langd + BagB'))]
    def pval(k):
        q = up.itemByName(k)
        return round(q.value * 10, 1) if q.unit == 'mm' else round(q.value, 4)
    pv = {up.item(i).name: pval(up.item(i).name) for i in range(up.count)}
    gom(des)
    FLEXMODE = False
    alla = [kontroll(des, root, 'standard')]
    json.dump({'parametrar': pv, 'lasprofil_mm': lg, 'antal': antal_alla(des), 'remsor_mm': alla[0].get('remsor_mm')},
              open(os.path.expanduser('~/code/buttercup/vaxthus/fusion/v11_antal.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump(pv, open(os.path.expanduser('~/code/buttercup/vaxthus/fusion/v13_param.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    nk = ev('NockOK')
    bild('v16_dummy.png', (7000, -7000, 4500), (0, L / 2, 1700), 9000)
    bild('v16_iso.png', (7000, -7000, 4500), (0, L / 2, 1700), 9000)
    bild('v16_nock.png', (700, 1250 - 1000, nk - 700), (0, 1250 + 200, nk - 60), 800)
    bild('v16_bage_nara.png', (1600, 1250 - 900, 1500), (1900, 1250, 1100), 900)
    orig = {k: up.itemByName(k).expression for k in FLEX}
    try:
        FLEXMODE = True
        for k, v in FLEX.items(): up.itemByName(k).expression = v
        alla.append(kontroll(des, root, 'flex (köpdelar ej omplacerade)'))
    finally:
        for k, v in orig.items(): up.itemByName(k).expression = v
        FLEXMODE = False
    alla.append(kontroll(des, root, 'återställt'))
    json.dump(alla, open(os.path.expanduser('~/code/buttercup/vaxthus/fusion/v16_resultat.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    try: os.remove(OUT + 'v16_dummy.png')
    except Exception: pass
    a0, a1, a2 = alla
    if any(a[k] for a in alla for k in ('antal_krock', 'fel', 'ej_last')) or a2['kroppar_totalt'] != a0['kroppar_totalt']:
        raise Exception('kontroll underkänd, sparar inte')
    d.save('Steg 16: plywood 12 mm (fläns 1x12x95, nocklask 12)')
    log('sparad', TOPPNAMN)
    try:
        sp = os.path.expanduser('~/code/buttercup/vaxthus/fusion/export/Vaxthus.step')
        em = des.exportManager; ok = em.execute(em.createSTEPExportOptions(sp, root)); log('STEP', ok, os.path.getsize(sp))
    except Exception as e: log('STEP FEL', str(e)[:200])
