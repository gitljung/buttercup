# Läsande sond: importera köpdels-STEP i ett skrapdokument, rapportera kroppar, bbox, största plana ytor. Sparar inget.
FILER = {
    'GN425 200': '~/code/buttercup/vaxthus/fusion/kopdelar/gn425a2-a4/Wiberger-GN425-NI-10-200-GS.step',
    'EL2030-100': '~/code/buttercup/vaxthus/fusion/kopdelar/el2030-100/Wiberger-el2030-100-fzb.step',
    'EL1035-200': '~/code/buttercup/vaxthus/fusion/kopdelar/el1035-200/Wiberger-el1035-200.STEP',
    'BPG-6': '~/code/buttercup/vaxthus/fusion/kopdelar/e_bpg-6step/Wiberger-e_bpg-6.STEP',
}


def run(_context: str):
    keepalive()
    res = {}
    d = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    des = adsk.fusion.Design.cast(d.products.itemByProductType('DesignProductType'))
    root = des.rootComponent
    im = app.importManager
    for nm, p in FILER.items():
        n0 = root.occurrences.count
        opt = im.createSTEPImportOptions(os.path.expanduser(p))
        im.importToTarget(opt, root)
        occs = [root.occurrences.item(i) for i in range(n0, root.occurrences.count)]
        info = []
        for o in occs:
            bodies = list(o.bRepBodies) + [b for c in o.childOccurrences for b in c.bRepBodies]
            for b in bodies:
                pl = [f for f in b.faces if f.geometry.objectType.endswith('Plane')]
                pl.sort(key=lambda f: -f.area)
                big = [(round(f.area * 100), [round(v, 3) for v in f.geometry.normal.asArray()], [round(v * 10, 1) for v in f.pointOnFace.asArray()]) for f in pl[:4]]
                cyl = [(round(f.geometry.radius * 10, 2), [round(v, 3) for v in f.geometry.axis.asArray()], [round(v * 10, 1) for v in f.geometry.origin.asArray()]) for f in b.faces if f.geometry.objectType.endswith('Cylinder')][:8]
                info.append({'occ': o.name, 'kropp': b.name, 'bbox': bbmm(b), 'vol_cm3': round(b.volume, 2), 'plan': big, 'cyl': cyl})
        res[nm] = info
        for o in occs: o.isLightBulbOn = False
    json.dump(res, open(os.path.expanduser('~/code/buttercup/vaxthus/fusion/kopdelar/sond.json'), 'w'), ensure_ascii=False, indent=1)
    for k, v in res.items():
        log(k, json.dumps([{a: x[a] for a in ('occ', 'kropp', 'bbox', 'vol_cm3')} for x in v], ensure_ascii=False))
    d.close(False)
