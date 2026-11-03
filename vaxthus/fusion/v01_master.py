# Steg 1: projekt 'vaxthus' + masterfilen "Växthus - parametrar".
# Alla mått som namngivna favoritparametrar med kommentar. Härledda värden som uttryck,
# så att en människa ändrar ett huvudmått och resten följer med.
# Koordinater: x tvärs (mitt 0), y längs huset (0 = främre gavelbågen), z upp (0 = mark).
# Mått längs bågen (…S) räknas på bågens mittlinje från foten (syllens ovansida).
PARAMS = [
    # --- huvudmått (ändra dessa) ---
    ('Bredd', '4000 mm', 'mm', 'Bredd c/c bågfötter (bågens mittlinje vid syllen)'),
    ('Langd', '10000 mm', 'mm', 'Längd c/c gavelbågar'),
    ('Nockhojd', '3500 mm', 'mm', 'Mark till bågens mittlinje i nocken'),
    ('Spetsighet', '0 mm', 'mm', 'Radiecentrum under syllens ovansida. 0 = rund båge, större = spetsigare nock'),
    ('Bagavstand', '2000 mm', 'mm', 'Största c/c mellan bågar (antal bågar räknas fram)'),
    ('DorrBredd', '2000 mm', 'mm', 'Dörröppning bredd (mellan dörrstolparna), båda gavlarna'),
    ('DorrHojd', '2000 mm', 'mm', 'Dörröppning höjd från syllens ovansida'),
    ('Overljus', '450 mm', 'mm', 'Överljus höjd ovanför dörröppningen'),
    ('SidoregelZ', '1900 mm', 'mm', 'Sidoregelns mitt över mark'),
    # --- virke ---
    ('SyllB', '120 mm', 'mm', 'Syll bredd (tryckimpregnerat 120x120)'),
    ('SyllH', '120 mm', 'mm', 'Syll höjd'),
    ('PlyT', '15 mm', 'mm', 'Plywoodremsa tjocklek (ytter- och innerbåge, laskar)'),
    ('BagB', '70 mm', 'mm', 'Bågens bredd längs huset (remsor och klossar)'),
    ('KlossH', '70 mm', 'mm', 'Kloss mellan remsorna, radiellt (bågens fack)'),
    ('KlossL', '120 mm', 'mm', 'Vanlig kloss längd längs bågen'),
    ('KlossCCmax', '550 mm', 'mm', 'Största c/c mellan klossar (antal räknas fram)'),
    ('FackKlossL', '250 mm', 'mm', 'Klossarna på var sida om sidoregelns fack (bär skarvarna)'),
    ('NockT', '45 mm', 'mm', 'Nockregel tjocklek (står på högkant i nocken)'),
    ('NockH', '120 mm', 'mm', 'Nockregel höjd'),
    ('SidoregelT', '34 mm', 'mm', 'Sidoregel tjocklek (ligger flatt mot innerremsan)'),
    ('SidoregelH', '145 mm', 'mm', 'Sidoregel bredd längs bågen'),
    ('FackSpel', '2.5 mm', 'mm', 'Spel per sida mellan sidoregel och kloss'),
    ('StolpeB', '95 mm', 'mm', 'Gavelvirke 95x95 (dörrstolpar, överliggare, nockstolpe, gavelstag)'),
    ('DorrRamT', '45 mm', 'mm', 'Dörrblad ram tjocklek'),
    ('DorrRamB', '70 mm', 'mm', 'Dörrblad ram bredd'),
    ('DorrSpel', '5 mm', 'mm', 'Spel runt dörrbladen'),
    ('SkivaL', '2440 mm', 'mm', 'Plywoodskivans längd = längsta remsa'),
    ('LaskL', '400 mm', 'mm', 'Lask över skarv (15 mm plywood, på remsans utsida)'),
    ('FilmT', '0.2 mm', 'mm', 'Polyetenfilm tjocklek (info, filmen är ytor)'),
    # --- härledda (ändra normalt inte) ---
    ('HalvBredd', 'Bredd / 2', 'mm', 'Härledd: halva bredden'),
    ('BagHojd', 'Nockhojd - SyllH', 'mm', 'Härledd: bågens höjd över syllen'),
    ('BagCx', '( BagHojd * BagHojd - HalvBredd * HalvBredd + 2 * BagHojd * Spetsighet ) / ( 2 * HalvBredd )', 'mm', 'Härledd: radiecentrum i sidled, på motsatta sidan om mitten'),
    ('BagCz', 'SyllH - Spetsighet', 'mm', 'Härledd: radiecentrums höjd över mark'),
    ('BagR', 'sqrt( ( BagCx + HalvBredd ) * ( BagCx + HalvBredd ) + Spetsighet * Spetsighet )', 'mm', 'Härledd: bågradie (mittlinjen)'),
    ('BagDjup', '2 * PlyT + KlossH', 'mm', 'Härledd: bågens djup (remsa + kloss + remsa)'),
    ('FotVinkel', 'asin( Spetsighet / BagR )', 'deg', 'Härledd: vinkel vid foten (från radiecentrum)'),
    ('NockVinkel', 'acos( ( NockT / 2 + BagCx ) / BagR )', 'deg', 'Härledd: vinkel där halvbågen möter nockregeln'),
    ('BagLangd', 'BagR * ( NockVinkel - FotVinkel ) / 1 rad', 'mm', 'Härledd: halvbågens längd längs mittlinjen'),
    ('AntalBagar', 'ceil( Langd / Bagavstand ) + 1', '', 'Härledd: antal bågar inkl. gavelbågar'),
    ('BagCC', 'Langd / ( AntalBagar - 1 )', 'mm', 'Härledd: verkligt c/c mellan bågar'),
    ('FackS', 'BagR * ( asin( ( SidoregelZ - BagCz ) / BagR ) - FotVinkel ) / 1 rad', 'mm', 'Härledd: sidoregelns fack, mitt, längs bågen'),
    ('FackGap', 'SidoregelH + 2 * FackSpel', 'mm', 'Härledd: fackets längd längs bågen'),
    ('FotKlossS', 'KlossL / 2', 'mm', 'Fotklossens mitt längs bågen'),
    ('FackNedreS', 'FackS - FackGap / 2 - FackKlossL / 2', 'mm', 'Nedre fackklossens mitt längs bågen'),
    ('FackOvreS', 'FackS + FackGap / 2 + FackKlossL / 2', 'mm', 'Övre fackklossens mitt längs bågen'),
    ('NockKlossS', 'BagLangd - KlossL / 2', 'mm', 'Nockklossens mitt längs bågen'),
    ('NedreMellan', 'max( 1 ; ceil( ( FackNedreS - FackKlossL / 2 - FotKlossS - KlossL / 2 ) / KlossCCmax ) - 1 )', '', 'Härledd: vanliga klossar mellan fotkloss och nedre fackkloss'),
    ('NedrePitch', '( FackNedreS - FotKlossS - ( FackKlossL - KlossL ) / 2 ) / ( NedreMellan + 1 )', 'mm', 'Härledd: c/c vanliga klossar, nedre raden'),
    ('OvreMellan', 'max( 1 ; ceil( ( NockKlossS - KlossL / 2 - FackOvreS - FackKlossL / 2 ) / KlossCCmax ) - 1 )', '', 'Härledd: vanliga klossar mellan övre fackkloss och nockkloss'),
    ('OvrePitch', '( NockKlossS - FackOvreS - ( FackKlossL - KlossL ) / 2 ) / ( OvreMellan + 1 )', 'mm', 'Härledd: c/c vanliga klossar, övre raden'),
    ('SkarvYtterS', 'FackOvreS', 'mm', 'Ytterbågens skarv längs bågen (på en fackkloss; ändra om en bit blir > SkivaL)'),
    ('SkarvInnerS', 'FackNedreS', 'mm', 'Innerbågens skarv längs bågen (förskjuten mot ytterbågens)'),
]
NAMES = [p[0] for p in PARAMS]


def run(_context: str):
    pr = project(); log('projekt', pr.name)
    f = dfile(MASTER)
    if f:
        d = find_doc(MASTER) or app.documents.open(f); d.activate(); ny = False
    else:
        d = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType); ny = True
    des = adsk.fusion.Design.cast(d.products.itemByProductType('DesignProductType'))
    des.designType = adsk.fusion.DesignTypes.ParametricDesignType
    up = des.userParameters
    fel = []
    for n, e, u, c in PARAMS:
        p = up.itemByName(n)
        alts = [e]
        if ';' in e: alts.append(e.replace(' ; ', ' , '))
        if '/ 1 rad' in e: alts += [e.replace('/ 1 rad', '/ ( 1 rad )'), e.replace(' / 1 rad', '')]
        ok = None
        for ee in alts:
            try:
                if p:
                    p.expression = ee; p.comment = c
                else:
                    p = up.add(n, VI(ee), u, c)
                p.isFavorite = True; ok = ee; break
            except Exception as ex:
                last = str(ex)[:120]
        if ok is None: fel.append((n, e, last))
        elif ok != e: log('ALTERNATIV', n, ok)
    if fel:
        log('FEL', json.dumps(fel, ensure_ascii=False))
        raise Exception('parametrar misslyckades')
    um = des.unitsManager
    res = {}
    for n in NAMES:
        p = up.itemByName(n)
        v = p.value
        u = p.unit
        res[n] = round(v * 10, 2) if u == 'mm' else (round(math.degrees(v), 3) if u == 'deg' else round(v, 3))
    log('VARDEN', json.dumps(res, ensure_ascii=False))
    log('kommentar test', up.itemByName('Langd').comment)
    if ny:
        d.saveAs(MASTER, folder(), 'Steg 1: masterparametrar (alla favoriter, Derive i detaljfiler)', '')
        log('sparad', MASTER)
    else:
        d.save('Steg 1: parametrar uppdaterade'); log('sparad (ny version)', MASTER)
    log('filer', [x.name for x in folder().dataFiles])
