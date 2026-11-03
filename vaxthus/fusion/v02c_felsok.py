# Felsökning: varför följer inte halvbågens _Ref med mastern? Ändrar Bredd tillfälligt, provar uppdateringsvägar, återställer.
NAMN = 'Växthus - halvbåge'


def refs(d, tag):
    out = []
    for i in range(d.documentReferences.count):
        rf = d.documentReferences.item(i)
        try: out.append((rf.dataFile.name, rf.version, rf.dataFile.latestVersionNumber, rf.isOutOfDate))
        except Exception as e: out.append(str(e)[:60])
    log(tag, 'refs', out)


def val(des, tag):
    p = des.allParameters
    log(tag, 'Bredd_Ref', round(p.itemByName('Bredd_Ref').value * 10, 1), 'BagR_Ref', round(p.itemByName('BagR_Ref').value * 10, 1))


def run(_context: str):
    md = master_doc(); md.activate()
    mdes = adsk.fusion.Design.cast(md.products.itemByProductType('DesignProductType'))
    up = mdes.userParameters
    log('master före', md.dataFile.latestVersionNumber, round(up.itemByName('Bredd').value * 10), round(up.itemByName('BagR').value * 10, 1))
    try:
        up.itemByName('Bredd').expression = '4800 mm'
        log('master BagR efter ändring', round(up.itemByName('BagR').value * 10, 1))
        v = save_wait(md, 'Felsökning (tillfälligt): Bredd 4800')
        log('master sparad version', v)
        for x in list(app.documents):
            try:
                if bas(x.name) == NAMN: x.close(False)
            except Exception: pass
        d = app.documents.open(dfile(NAMN)); d.activate()
        des = adsk.fusion.Design.cast(d.products.itemByProductType('DesignProductType'))
        refs(d, 'öppnad'); val(des, 'öppnad')
        for i in range(d.documentReferences.count):
            rf = d.documentReferences.item(i)
            try:
                if rf.isOutOfDate or rf.version < rf.dataFile.latestVersionNumber:
                    rf.getLatestVersion(); log('getLatestVersion OK')
            except Exception as e: log('getLatestVersion FEL', str(e)[:100])
        des.computeAll(); adsk.doEvents()
        refs(d, 'efter getLatest'); val(des, 'efter getLatest')
        try: log('updateAllReferences', d.updateAllReferences())
        except Exception as e: log('updateAllReferences FEL', str(e)[:100])
        des.computeAll(); adsk.doEvents()
        refs(d, 'efter updateAll'); val(des, 'efter updateAll')
        df = des.rootComponent.features.deriveFeatures.item(0)
        log('derive', df.name, [m for m in dir(df) if not m.startswith('_')][:60])
        tl = des.timeline
        log('fel', [(tl.item(i).name, tl.item(i).errorOrWarningMessage[:80]) for i in range(tl.count) if tl.item(i).healthState != 0])
        b = [x for x in des.rootComponent.bRepBodies if x.name == 'Ytterremsa 1'][0]
        log('Ytterremsa 1 bbox', bbmm(b))
        d.close(False)
    finally:
        md = master_doc(); md.activate()
        mdes = adsk.fusion.Design.cast(md.products.itemByProductType('DesignProductType'))
        mdes.userParameters.itemByName('Bredd').expression = '4000 mm'
        save_wait(md, 'Felsökning återställd')
        log('master återställd', round(mdes.userParameters.itemByName('Bredd').value * 10))
