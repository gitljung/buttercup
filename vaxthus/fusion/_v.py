# ---- Växthus: overrides ovanpa yakitori50/native/_n.py (kopia av Horno _h.py) ----
# Best practice (fran Asado-nativ): en designfil per tillverkad detalj, Derive fran masterparametrar,
# relationsbaserade skisser (H/V, symmetri, matt fran origo via uttryck), plat (sheet metal) + utvikning,
# montage med lankade filer och joints. Allt modelleras i montagets koordinater (lankas med identitet).
# Koordinater: x = tvars (mitt 0), y = langs huset (0 = framre gavelbagen, +y bakat), z = upp (0 = mark/syllens underkant).
import re
def bas(n):
    """dokument-/komponentnamn utan versionssuffix ' v12' (OBS: split(' v') klipper 'vanster')"""
    return re.sub(r' v\d+$', '', n)
def keepalive():
    """Fusion kraschar (ASM exception, NEUTRON_BUG_ALERT) nar SISTA dokumentet stangs och startsidan oppnas.
    Hall alltid ett tomt osparat dokument oppet i bakgrunden."""
    try:
        if not any(not d.isSaved and d.products.count and adsk.fusion.Design.cast(d.products.itemByProductType('DesignProductType')).rootComponent.bRepBodies.count == 0
                   and adsk.fusion.Design.cast(d.products.itemByProductType('DesignProductType')).rootComponent.features.deriveFeatures.count == 0 for d in app.documents):
            try: act = app.activeDocument
            except Exception: act = None
            app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
            if act: act.activate()
    except Exception: pass
keepalive()
def close_vaxthus(only=None):
    """Stang Horno-dokument utan att Fusion blir utan aktivt dokument (krasch 'There is no active document').
    Aktivera forst keepalive-dokumentet, stang sedan ett i taget med doEvents."""
    keepalive()
    for x in list(app.documents):
        try:
            if not x.isSaved and bas(x.name).startswith('Untitled'): x.activate(); break
        except Exception: pass
    for x in list(app.documents):
        try:
            n = bas(x.name)
            if (n == only) if only else n.startswith('Växthus'):
                x.close(False); adsk.doEvents()
        except Exception: pass
PROJ = 'vaxthus'
MASTER = 'Växthus - parametrar'
TOPP = 'Växthus'
OUT = os.path.expanduser('~/code/buttercup/vaxthus/fusion/bilder/')
NEWB = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
CUT = adsk.fusion.FeatureOperations.CutFeatureOperation
JOIN = adsk.fusion.FeatureOperations.JoinFeatureOperation

def project():
    ps = [p for p in app.data.dataProjects if p.name == PROJ]
    return ps[0] if ps else app.data.dataProjects.add(PROJ)
def tra(des):
    return appearance(des, 'Tra (gran)', 'Paint - Enamel Glossy (Yellow)', (214, 178, 122))
def tryck(des):
    return appearance(des, 'Tryckimpregnerat', 'Paint - Enamel Glossy (Yellow)', (150, 140, 95))
def plywood(des):
    return appearance(des, 'Plywood', 'Paint - Enamel Glossy (Yellow)', (226, 196, 140))
def folder():
    return project().rootFolder
def dfile(name):
    import time
    for k in range(6):      # dataFiles-iterationen kastar ibland 'InternalValidationError : item' strax efter omdopningar
        try:
            fs = [f for f in folder().dataFiles if f.name == name]
            return fs[0] if fs else None
        except RuntimeError:
            time.sleep(3); adsk.doEvents()
    fs = []
    df = folder().dataFiles
    for i in range(df.count):
        try:
            f = df.item(i)
            if f.name == name: return f
        except Exception: pass
    return None
def find_doc(name):
    for d in app.documents:
        try:
            if bas(d.name) == name or d.name == name: return d
        except Exception: pass
    return None
def bbmm(b):
    bb = b.boundingBox
    return [round(v * 10, 3) for v in (bb.minPoint.x, bb.minPoint.y, bb.minPoint.z, bb.maxPoint.x, bb.maxPoint.y, bb.maxPoint.z)]

def appearance(des, nm, base, rgb):
    a = des.appearances.itemByName(nm)
    if a: return a
    lib = [app.materialLibraries.item(i) for i in range(app.materialLibraries.count) if app.materialLibraries.item(i).name.startswith('Fusion Appearance')][0]
    a = des.appearances.addByCopy(lib.appearances.itemByName(base), nm)
    for j in range(a.appearanceProperties.count):
        pr = a.appearanceProperties.item(j)
        if pr.objectType.endswith('ColorProperty'):
            try: pr.value = adsk.core.Color.create(rgb[0], rgb[1], rgb[2], 255)
            except Exception: pass
    return a

def master_doc():
    d = find_doc(MASTER)
    return d if d else app.documents.open(dfile(MASTER), False)

class Del:
    """En tillverkad detalj = en designfil med Derive fran mastern."""
    def __init__(self, namn):
        self.namn = namn
        if dfile(namn): raise Exception('filen finns redan: ' + namn)
        for x in list(app.documents):     # rester fran misslyckade forsok (osparade, med Derive fran Horno-mastern)
            try:
                dx = adsk.fusion.Design.cast(x.products.itemByProductType('DesignProductType'))
                if not x.isSaved and dx and any(f.name.startswith('Parametrar fran ' + MASTER) for f in dx.rootComponent.features.deriveFeatures): x.close(False)
            except Exception: pass
        d = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        des = adsk.fusion.Design.cast(d.products.itemByProductType('DesignProductType'))
        des.designType = adsk.fusion.DesignTypes.ParametricDesignType
        self.d, self.des, self.r = d, des, des.rootComponent
        src = master_doc()
        di = self.r.features.deriveFeatures.createInput(adsk.fusion.Design.cast(src.products.itemByProductType('DesignProductType')))
        di.isIncludeFavoriteParameters = True
        self.r.features.deriveFeatures.add(di).name = 'Parametrar fran ' + MASTER
        d.activate()
        self.ef = self.r.features.extrudeFeatures
        self.PL = {'xy': self.r.xYConstructionPlane, 'xz': self.r.xZConstructionPlane, 'yz': self.r.yZConstructionPlane}
    def E(self, s):
        AP = self.des.allParameters
        def rep(m):
            n = m.group(1)
            for c in (n + '_Ref', n):
                if AP.itemByName(c): return c
            return n
        return re.sub(r'\b([A-Z][A-Za-z0-9_]*)\b', rep, s)
    def ev(self, s): return self.des.unitsManager.evaluateExpression(self.E(s), 'mm') * 10

    def sketch(self, plane, au, av, name):
        sk = self.r.sketches.add(self.PL[plane]); sk.name = name
        return Skiss(self, sk, au, av)

    def ext(self, prof, axis, start, dist, lo, name, op=NEWB, parts=None):
        """extrudera fran offsetstart 'start' (belopp-uttryck) med 'dist'; behaller lage dar kroppens min langs axis = lo (mm)"""
        i = 'xyz'.index(axis)
        for st in (start, '-( %s )' % start):
            for dd in (dist, '-( %s )' % dist):
                inp = self.ef.createInput(prof, op)
                if start not in ('0', '0 mm'):
                    inp.startExtent = adsk.fusion.OffsetStartDefinition.create(VI(self.E(st)))
                inp.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(VI(self.E(dd))), adsk.fusion.ExtentDirections.PositiveExtentDirection)
                if parts: inp.participantBodies = parts
                try: f = self.ef.add(inp)
                except Exception: continue
                b = f.bodies.item(0) if f.bodies.count else None
                if b and abs(bbmm(b)[i] - lo) < 1e-3: f.name = name; return f
                f.deleteMe()
            if start in ('0', '0 mm'): break
        raise Exception('ext hittade inte ratt lage: ' + name)
    def cut(self, profs, body, name):
        inp = self.ef.createInput(coll(profs) if isinstance(profs, list) else profs, CUT)
        inp.setTwoSidesExtent(adsk.fusion.ThroughAllExtentDefinition.create(), adsk.fusion.ThroughAllExtentDefinition.create())
        inp.participantBodies = [body]
        f = self.ef.add(inp); f.name = name; return f
    def fillet_edges(self, edges, rexpr, name):
        fi = self.r.features.filletFeatures.createInput()
        fi.edgeSetInputs.addConstantRadiusEdgeSet(coll(edges), VI(self.E(rexpr)), False)
        f = self.r.features.filletFeatures.add(fi); f.name = name; return f

    def sheet(self, body, rule, t):
        face = max([f for f in body.faces if f.geometry.objectType.endswith('Plane')], key=lambda f: f.area)
        try: rule0 = self.r.activeSheetMetalRule
        except Exception: rule0 = None
        body.convertToSheetMetal(face, rule0 if rule0 else self.des.librarySheetMetalRules.itemByName('Steel (mm)'))
        ar = self.r.activeSheetMetalRule
        tt = '%g mm' % self.ev(t)   # platregler tar inte parameteruttryck
        ar.name = rule; ar.thickness.expression = tt; ar.bendRadius.expression = tt; ar.kFactor = 0.44
        return self.r.bRepBodies.item(0)
    def finish(self, partnr, desc, material='corten', flat=True, note=''):
        r = self.r; body = r.bRepBodies.item(0); body.name = partnr
        if material == 'corten': body.appearance = appearance(self.des, 'Corten (obehandlad)', 'Paint - Metallic (Dark Grey)', (110, 70, 48))
        elif material == 'rostfritt': body.appearance = appearance(self.des, 'Rostfritt 304', 'Paint - Metallic (Silver)', (200, 204, 208))
        r.partNumber = partnr; r.description = desc
        res = {'namn': self.namn, 'kroppar': r.bRepBodies.count, 'lumps': body.lumps.count, 'plat': body.isSheetMetal}
        if flat and body.isSheetMetal:
            try:
                fpf = max([f for f in body.faces if f.geometry.objectType.endswith('Plane')], key=lambda f: f.area)
                fp = r.flatPattern or r.createFlatPattern(fpf)
                fb = fp.bodies.item(0).boundingBox
                res['utvikt'] = sorted([round(v * 10, 2) for v in (fb.maxPoint.x - fb.minPoint.x, fb.maxPoint.y - fb.minPoint.y, fb.maxPoint.z - fb.minPoint.z)])
            except Exception as e_: res['utvikt'] = 'FEL ' + str(e_)[:100]
            try: self.des.activateRootComponent()
            except Exception: pass
        res['bbox'] = bbmm(body); res['kg'] = round(body.volume * 7.85 / 1000, 2)
        tl = self.des.timeline
        res['fel'] = [(tl.item(i).name, tl.item(i).errorOrWarningMessage[:60]) for i in range(tl.count) if tl.item(i).healthState != 0]
        res['ej_last'] = [(sk.name, free_report(sk)[:4]) for sk in r.sketches if not sk.isFullyConstrained]
        log(json.dumps(res, ensure_ascii=False))
        self.d.saveAs(self.namn, folder(), note or 'Nativ detalj', '')
        return res

class Skiss:
    """Skiss pa origoplan med modellaxlar (au, av). Uttryck = avstand fran origo (belopp); '0' -> pa axeln."""
    def __init__(self, D, sk, au, av):
        self.D, self.sk, self.au, self.av = D, sk, au, av
        self.o = sk.originPoint; self.gc = sk.geometricConstraints; self.ax = {}
    def axis(self, a):
        if a not in self.ax: self.ax[a] = proj_axis(self.sk, self.D.r, a)
        return self.ax[a]
    def p(self, u, v):
        c = {'x': 0, 'y': 0, 'z': 0}; c[self.au] = u; c[self.av] = v
        return SP(self.sk, c['x'], c['y'], c['z'])
    def at(self, u, v):
        c = {'x': 0, 'y': 0, 'z': 0}; c[self.au] = u; c[self.av] = v
        return (c['x'], c['y'], c['z'])
    def place(self, pt, eu, ev, u, v):
        if eu is not None:
            if eu in ('0', '0 mm'): self.gc.addCoincident(pt, self.axis(self.av))
            else: dimx(self.sk, self.o, pt, self.au, self.D.E(eu), self.at(u / 2, v + 8))
        if ev is not None:
            if ev in ('0', '0 mm'): self.gc.addCoincident(pt, self.axis(self.au))
            else: dimx(self.sk, self.o, pt, self.av, self.D.E(ev), self.at(u + 8, v / 2))
    def poly(self, pts):
        """ortogonal sluten polygon, pts = [(u, v, eu, ev)] (mm + belopp-uttryck). Fullt last utan overbestamning:
        1) symmetri for spegelpar som ar grannar, 2) H/V pa ovriga linjer om de inte redan ar bundna,
        3) symmetri for ovriga spegelpar om helt obundna, 4) ett matt per u-grupp och v-grupp."""
        LS = self.sk.sketchCurves.sketchLines
        n = len(pts); L = []
        for i in range(n):
            a, b = pts[i], pts[(i + 1) % n]
            if i == 0: l = LS.addByTwoPoints(self.p(a[0], a[1]), self.p(b[0], b[1]))
            elif i == n - 1: l = LS.addByTwoPoints(L[-1].endSketchPoint, L[0].startSketchPoint)
            else: l = LS.addByTwoPoints(L[-1].endSketchPoint, self.p(b[0], b[1]))
            L.append(l)
        V = [L[i].startSketchPoint for i in range(n)]
        pu = list(range(n)); su = [1] * n; pv = list(range(n))
        def fu(i):
            if pu[i] == i: return i, 1
            r, sg = fu(pu[i]); pu[i] = r; su[i] *= sg; return r, su[i]
        def uu(i, j, sg):          # u_i = sg * u_j
            (ri, si), (rj, sj) = fu(i), fu(j)
            if ri == rj: return False
            pu[ri] = rj; su[ri] = si * sg * sj; return True
        def fv(i):
            while pv[i] != i: i = pv[i]
            return i
        def uv(i, j):
            ri, rj = fv(i), fv(j)
            if ri == rj: return False
            pv[ri] = rj; return True
        eq = lambda x, y: abs(x - y) < 1e-6
        mirror = lambda i, j: abs(pts[i][0]) > 1e-6 and eq(pts[i][0], -pts[j][0]) and eq(pts[i][1], pts[j][1])
        done = set()
        for i in range(n):                       # 1) grannpar
            j = (i + 1) % n
            if mirror(i, j):
                k, m = (i, j) if pts[i][0] > 0 else (j, i)
                self.gc.addSymmetry(V[k], V[m], self.axis(self.av)); uu(i, j, -1); uv(i, j); done.add(i)
        for i in range(n):                       # 2) H/V
            if i in done: continue
            j = (i + 1) % n; a, b = pts[i], pts[j]
            if eq(a[1], b[1]):
                if uv(i, j): along(self.sk, L[i], self.au)
            elif eq(a[0], b[0]):
                if uu(i, j, 1): along(self.sk, L[i], self.av)
        for i in range(n):                       # 3) ovriga spegelpar
            for j in range(n):
                if pts[i][0] > 0 and mirror(i, j) and fu(i)[0] != fu(j)[0] and fv(i) != fv(j):
                    self.gc.addSymmetry(V[i], V[j], self.axis(self.av)); uu(i, j, -1); uv(i, j)
        gu, gv = {}, {}
        for i in range(n):
            r = fu(i)[0]
            if r not in gu or (pts[i][0] > 0 and pts[gu[r]][0] <= 0): gu[r] = i
            gv.setdefault(fv(i), i)
        for i in gu.values(): self.place(V[i], pts[i][2], None, pts[i][0], pts[i][1])
        for i in gv.values(): self.place(V[i], None, pts[i][3], pts[i][0], pts[i][1])
        return L
    def rect(self, u0, u1, v0, v1, eu0, eu1, ev0, ev1):
        return self.poly([(u0, v0, eu0, ev0), (u1, v0, eu1, ev0), (u1, v1, eu1, ev1), (u0, v1, eu0, ev1)])
    def hole(self, u, v, eu, ev, dia='Hal_M6', mirror_of=None):
        c = self.sk.sketchCurves.sketchCircles.addByCenterRadius(self.p(u + 1e-3, v + 1e-3), self.D.ev(dia) / 20)
        self.sk.sketchDimensions.addDiameterDimension(c, self.p(u + 6, v + 6)).parameter.expression = self.D.E(dia)
        if mirror_of is not None: self.gc.addSymmetry(c.centerSketchPoint, mirror_of.centerSketchPoint, self.axis(self.av))
        else: self.place(c.centerSketchPoint, eu, ev, u, v)
        return c
    def holes_sym(self, u, v, eu, ev, dia='Hal_M6'):
        """hal i (u, v) + spegelhal i (-u, v); u = 0 -> ett hal pa axeln"""
        if abs(u) < 1e-6: return [self.hole(0, v, '0', ev, dia)]
        a = self.hole(abs(u), v, eu, ev, dia)
        return [a, self.hole(-abs(u), v, None, None, dia, mirror_of=a)]
    def report(self):
        return self.sk.name, self.sk.isFullyConstrained, self.sk.profiles.count, free_report(self.sk)[:6]
    def biggest(self):
        return max([self.sk.profiles.item(i) for i in range(self.sk.profiles.count)], key=lambda p: p.areaProperties().area)

def edges_along(body, axis, targets, tol=0.05):
    """raka kanter parallella med axis vars ovriga tva koordinater (mm) ligger i targets [(a, b)]"""
    i = 'xyz'.index(axis); o = [k for k in range(3) if k != i]; res = []
    for e in body.edges:
        if not e.geometry.objectType.endswith('Line3D'): continue
        s, t = e.startVertex.geometry.asArray(), e.endVertex.geometry.asArray()
        if abs(t[o[0]] - s[o[0]]) > 1e-6 or abs(t[o[1]] - s[o[1]]) > 1e-6: continue
        if any(abs(s[o[0]] * 10 - x) < tol and abs(s[o[1]] * 10 - y) < tol for x, y in targets): res.append(e)
    return res

class Ed(Del):
    """Andra en befintlig detaljfil: oppna, uppdatera Derive mot senaste mastern."""
    def __init__(self, namn):
        self.namn = namn
        for x in list(app.documents):
            try:
                if bas(x.name) == namn: x.close(False)
            except Exception: pass
        df = None
        for _ in range(8):      # dataFiles-listan ar ibland ofullstandig direkt efter sparningar -> 'invalid argument dataFile'
            df = dfile(namn)
            if df: break
            import time; time.sleep(2); adsk.doEvents()
        self.d = app.documents.open(df); self.d.activate()
        self.des = adsk.fusion.Design.cast(self.d.products.itemByProductType('DesignProductType')); self.r = self.des.rootComponent
        try: self.d.updateAllReferences()
        except Exception as e: log('updateAllReferences', str(e)[:80])
        self.des.computeAll()
        self.ef = self.r.features.extrudeFeatures
        self.PL = {'xy': self.r.xYConstructionPlane, 'xz': self.r.xZConstructionPlane, 'yz': self.r.yZConstructionPlane}
    def save(self, note):
        tl = self.des.timeline
        fel = [(tl.item(i).name, tl.item(i).errorOrWarningMessage[:60]) for i in range(tl.count) if tl.item(i).healthState != 0]
        ej = [sk.name for sk in self.r.sketches if not sk.isFullyConstrained]
        log(self.namn, 'fel', fel, 'ej last', ej, 'kg', round(self.r.bRepBodies.item(0).volume * 7.85 / 1000, 2))
        if fel: raise Exception('sparar inte, tidslinjefel')
        self.d.save(note)
