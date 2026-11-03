# Experiment: varför ger komponentmönstret 3x occurrences? Skrapdokument, sparas inte.
def bygg(variant):
    d = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    des = adsk.fusion.Design.cast(d.products.itemByProductType('DesignProductType'))
    des.designType = adsk.fusion.DesignTypes.ParametricDesignType
    root = des.rootComponent
    des.userParameters.add('AntalX', VI('4'), '', '')
    des.userParameters.add('AvstX', VI('100 mm'), 'mm', '')
    I = adsk.core.Matrix3D.create()
    oB = root.occurrences.addNewComponent(I); cB = oB.component; cB.name = 'B'
    target = cB
    if variant.get('sub'):
        oH = cB.occurrences.addNewComponent(I); target = oH.component; target.name = 'H'
    sk = target.sketches.add(target.xYConstructionPlane)
    sk.sketchCurves.sketchLines.addTwoPointRectangle(P3(0, 0, 0), P3(1, 1, 0))
    target.features.extrudeFeatures.addSimple(sk.profiles.item(0), VI('1 cm'), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    if variant.get('sub2'):
        rot = adsk.core.Matrix3D.create(); rot.setToRotation(math.pi, adsk.core.Vector3D.create(0, 0, 1), P3(0, 0, 0))
        cB.occurrences.addExistingComponent(target, rot)
    if variant.get('ground'): oB.isGrounded = True
    n0 = root.occurrences.count
    rp = root.features.rectangularPatternFeatures
    inp = rp.createInput(coll([oB]), root.yConstructionAxis, VI('AntalX'), VI('AvstX'), adsk.fusion.PatternDistanceType.SpacingPatternDistanceType)
    if variant.get('fix'): inp.setDirectionTwo(root.xConstructionAxis, VI('1'), VI('0 mm'))
    try: log('qty2 före', inp.quantityTwo.expression if inp.quantityTwo else None)
    except Exception as e: log('qty2 FEL', str(e)[:60])
    f = rp.add(inp)
    log('feature qty2', f.quantityTwo.expression)
    n1 = root.occurrences.count
    des.computeAll()
    n2 = root.occurrences.count
    log(json.dumps(variant), 'före', n0, 'efter add', n1, 'efter computeAll', n2, [o.name for o in root.occurrences])
    d.close(False)


def run(_context: str):
    keepalive()
    for v in ({}, {'fix': 1}, {'sub': 1, 'sub2': 1, 'ground': 1, 'fix': 1}):
        bygg(v)
