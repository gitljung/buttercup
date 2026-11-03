# Test: följer en Derive med när mastern ändras, om mastern är öppnad SYNLIG när Derive skapas?
TEST = 'Växthus - derivtest'


def run(_context: str):
    import time
    if dfile(TEST): dfile(TEST).deleteMe(); time.sleep(3)
    for x in list(app.documents):
        try:
            if bas(x.name) in (MASTER, TEST): x.close(False)
        except Exception: pass
    md = app.documents.open(dfile(MASTER), True)      # synlig
    mdes = adsk.fusion.Design.cast(md.products.itemByProductType('DesignProductType'))
    d = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    des = adsk.fusion.Design.cast(d.products.itemByProductType('DesignProductType'))
    des.designType = adsk.fusion.DesignTypes.ParametricDesignType
    di = des.rootComponent.features.deriveFeatures.createInput(mdes)
    di.isIncludeFavoriteParameters = True
    des.rootComponent.features.deriveFeatures.add(di)
    d.saveAs(TEST, folder(), 'derivtest', '')
    for _ in range(40):
        adsk.doEvents(); time.sleep(0.5)
    log('test refs', d.documentReferences.count, 'Bredd_Ref', round(des.allParameters.itemByName('Bredd_Ref').value * 10))
    try:
        md.activate()
        mdes.userParameters.itemByName('Bredd').expression = '4800 mm'
        save_wait(md, 'derivtest tillfälligt Bredd 4800')
        d.activate(); md.close(False)
        for _ in range(60):
            adsk.doEvents(); time.sleep(0.5)
        log('refs efter masterändring', [(r.version, r.dataFile.latestVersionNumber, r.isOutOfDate) for r in d.documentReferences])
        try: log('updateAllReferences', d.updateAllReferences())
        except Exception as e: log('updateAll FEL', str(e)[:80])
        des.computeAll()
        log('refs efter update', [(r.version, r.dataFile.latestVersionNumber, r.isOutOfDate) for r in d.documentReferences])
        log('Bredd_Ref efter uppdatering (öppen)', round(des.allParameters.itemByName('Bredd_Ref').value * 10))
        d.close(False)
        d2 = app.documents.open(dfile(TEST)); d2.activate()
        des2 = adsk.fusion.Design.cast(d2.products.itemByProductType('DesignProductType'))
        log('nyöppnad refs', [(r.version, r.dataFile.latestVersionNumber, r.isOutOfDate) for r in d2.documentReferences])
        d2.updateAllReferences(); des2.computeAll()
        log('Bredd_Ref nyöppnad + update', round(des2.allParameters.itemByName('Bredd_Ref').value * 10))
        d2.close(False)
    finally:
        md = find_doc(MASTER) or app.documents.open(dfile(MASTER), True)
        mdes = adsk.fusion.Design.cast(md.products.itemByProductType('DesignProductType'))
        md.activate()
        mdes.userParameters.itemByName('Bredd').expression = '4000 mm'
        save_wait(md, 'derivtest återställd')
        log('master återställd')
