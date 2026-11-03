# Felsök det osparade v03-dokumentet: mönster/occurrences och vilka skissobjekt som blivit fria efter flextestet.
def run(_context: str):
    for x in app.documents:
        dx = adsk.fusion.Design.cast(x.products.itemByProductType('DesignProductType'))
        if x.isSaved or not dx or not dx.allComponents.itemByName('Båge'): continue
        root = dx.rootComponent
        log('dok', x.name)
        log('rootfeatures', [(f.name, f.objectType.split('::')[-1]) for f in root.features])
        rp = root.features.rectangularPatternFeatures
        for i in range(rp.count):
            f = rp.item(i)
            log('mönster', f.name, f.quantityOne.expression, f.distanceOne.expression)
        occs = [(o.name, round(o.transform2.translation.y * 10)) for o in root.occurrences]
        log('root.occurrences', len(occs), occs[:30])
        tl = dx.timeline
        log('tidslinje', [(tl.item(i).name, tl.item(i).entity.objectType.split('::')[-1] if tl.item(i).entity else '') for i in range(tl.count)][-12:])
        h = dx.allComponents.itemByName('Halvbåge')
        for s in h.sketches:
            if s.isFullyConstrained: continue
            fr = []
            for c in s.sketchCurves:
                if not c.isFullyConstrained:
                    fr.append((c.objectType.split('::')[-1], c.isReference, c.isConstruction))
            for p in s.sketchPoints:
                if not p.isFullyConstrained:
                    fr.append(('pt', round(p.geometry.x * 10), round(p.geometry.y * 10), p.connectedEntities.count if p.connectedEntities else 0))
            bad = []
            for g in s.geometricConstraints:
                try:
                    if not g.isValid: bad.append(g.objectType)
                except Exception: pass
            dims = [(dd.parameter.expression, round(dd.parameter.value, 4)) for dd in s.sketchDimensions]
            log('FRI', s.name, fr[:8], 'dims', dims)
