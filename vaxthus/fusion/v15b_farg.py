# Nockbalken fick standardfärg i v15 -> trä. Inget geometriskt ändras. Nya bilder.
import builtins as _bi
_o = _bi.open
def open(f, m='r', *a, **k):
    if 'b' not in m and 'encoding' not in k and not a: k['encoding'] = 'utf-8'
    return _o(f, m, *a, **k)
exec(open(os.path.expanduser('~/code/buttercup/vaxthus/fusion/v15_nockbalk.py'), encoding='utf-8').read().split('\ndef run(')[0])
def run(_context: str):
    d = find_doc(TOPPNAMN)
    if d: d.close(False)
    d = app.documents.open(dfile(TOPPNAMN)); d.activate()
    des = adsk.fusion.Design.cast(d.products.itemByProductType('DesignProductType'))
    ev = lambda s: des.unitsManager.evaluateExpression(s, 'mm') * 10
    nc = des.allComponents.itemByName('Nock och sidoreglar'); n = 0
    for b in nc.bRepBodies:
        if b.name.startswith('Nockbalk'): b.appearance = tra(des); n += 1
    log('nockbalk färg', n)
    gom(des)
    L = ev('Langd'); nk = ev('NockOK')
    bild('v15_dummy.png', (7000, -7000, 4500), (0, L / 2, 1700), 9000)
    bild('v15_iso.png', (7000, -7000, 4500), (0, L / 2, 1700), 9000)
    bild('v15_nock.png', (700, 1250 - 1000, nk - 700), (0, 1250 + 200, nk - 60), 800)
    bild('v15_gavel.png', (900, -1600, nk - 400), (0, 0, nk - 200), 1400)
    try: os.remove(OUT + 'v15_dummy.png')
    except Exception: pass
    d.save('Steg 15b: nockbalk trä-utseende')
    log('sparad')
