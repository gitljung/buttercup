NAMN = 'Växthus - halvbåge'


def run(_context: str):
    d = find_doc(NAMN) or app.documents.open(dfile(NAMN))
    des = adsk.fusion.Design.cast(d.products.itemByProductType('DesignProductType'))
    df = des.rootComponent.features.deriveFeatures.item(0)
    log('namn', df.name, 'parametric', df.isParametric, 'fav', df.isIncludeFavoriteParameters)
    try:
        rf = df.documentReference
        log('docref', rf)
        if rf: log('ver', rf.version, 'senaste', rf.dataFile.latestVersionNumber, 'ood', rf.isOutOfDate, rf.dataFile.name)
    except Exception as e: log('docref FEL', str(e)[:150])
    try: log('sourceDesign', df.sourceDesign.parentDocument.name)
    except Exception as e: log('sourceDesign FEL', str(e)[:150])
    log('docrefs', d.documentReferences.count, 'datafile refs', [x.name for x in d.dataFile.childReferences] if d.dataFile else None)
    try: log('parentRefs master', [x.name for x in dfile(MASTER).parentReferences])
    except Exception as e: log('parentRefs FEL', str(e)[:100])
    log('master ver', dfile(MASTER).latestVersionNumber, 'halvbage ver', dfile(NAMN).latestVersionNumber)
