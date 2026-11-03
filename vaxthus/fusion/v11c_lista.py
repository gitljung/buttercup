# Läsande: dumpar alla kroppar (komponent, kropp, sorterade bbox-mått, volym) till v11_kroppar.json för inköpslistan. Sparar inget.
exec(open(os.path.expanduser('~/code/buttercup/vaxthus/fusion/v03_topp.py')).read().split('\ndef run(')[0])


def run(_context: str):
    keepalive()
    d = find_doc(TOPPNAMN)
    if d: d.close(False)
    d = app.documents.open(dfile(TOPPNAMN)); d.activate()
    des = adsk.fusion.Design.cast(d.products.itemByProductType('DesignProductType'))
    root = des.rootComponent
    out = []
    for occ in root.allOccurrences:
        for b in occ.bRepBodies:
            bb = b.boundingBox
            dims = sorted(round((getattr(bb.maxPoint, k) - getattr(bb.minPoint, k)) * 10, 1) for k in 'xyz')
            out.append(dict(komp=occ.component.name, kropp=b.name, mått=dims, vol_cm3=round(b.volume, 2),
                            fysisk_area_cm2=round(b.area, 1)))
    for b in root.bRepBodies:
        bb = b.boundingBox
        out.append(dict(komp='(rot)', kropp=b.name, mått=sorted(round((getattr(bb.maxPoint, k) - getattr(bb.minPoint, k)) * 10, 1) for k in 'xyz'), vol_cm3=round(b.volume, 2)))
    json.dump(out, open(os.path.expanduser('~/code/buttercup/vaxthus/fusion/v11_kroppar.json'), 'w'), ensure_ascii=False, indent=1)
    log('kroppar', len(out))
