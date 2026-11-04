# Läsande: dumpa alla userParameters (värde i mm / enhetslöst) -> v13_param.json. Sparar inget.
import builtins as _bi
_o = _bi.open
def open(f, m='r', *a, **k):
    if 'b' not in m and 'encoding' not in k and not a: k['encoding'] = 'utf-8'
    return _o(f, m, *a, **k)
exec(open(os.path.expanduser('~/code/buttercup/vaxthus/fusion/v08b_kopdelar.py')).read().split('\ndef run(')[0])
def run(_context: str):
    d = find_doc(TOPPNAMN)
    if not d: d = app.documents.open(dfile(TOPPNAMN))
    d.activate()
    des = adsk.fusion.Design.cast(d.products.itemByProductType('DesignProductType')); up = des.userParameters
    out = {}
    for i in range(up.count):
        p = up.item(i); out[p.name] = round(p.value * (10 if p.unit == 'mm' else 1), 3)
    json.dump(out, open(os.path.expanduser('~/code/buttercup/vaxthus/fusion/v13_param.json'), 'w'), ensure_ascii=False, indent=1)
    log('param', len(out))
