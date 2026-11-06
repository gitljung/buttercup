#!/usr/bin/env python3
"""Bygger den fristående appen Hasses Hälsoresa (buttercup.nu/halsoresa/) ur STARK IGEN-koden.
Kör efter ändringar i Hasses pass i ../traning/index.html:  python3 halsoresa/build.py
Egen PWA: eget manifest, egen service worker (scope /halsoresa/), egna ikoner, egna localStorage-nycklar."""
import json, os, re, shutil, glob
R = os.path.dirname(os.path.abspath(__file__)); T = os.path.join(R, '..', 'traning')
s = open(os.path.join(T, 'index.html'), encoding='utf-8').read()

def rep(a, b, n=1):
    global s
    assert a in s, 'saknas: ' + a[:70]
    s = s.replace(a, b, n)

# läget: alltid Hälsoresan, ingen base-href (filerna ligger i egen mapp)
s = re.sub(r"<script>window\.HR = .*?</script>", "<script>window.HR = true; document.documentElement.classList.add('hr');</script>", s, count=1, flags=re.S)
# egna nycklar – ingen delning med STARK IGEN
s = s.replace('bc_traning_', 'bc_halsoresa_')
# head
rep('<title>STARK IGEN · Träning · Buttercup</title>', '<title>Hasses Hälsoresa · Buttercup</title>')
s = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="Hasses Hälsoresa – två kettlebellpass med Hasse. En klocka, 15 minuter, timern räknar och Hasse visar.">', s, 1)
s = re.sub(r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="Hasses Hälsoresa">', s, 1)
s = re.sub(r'<meta property="og:description" content="[^"]*">', '<meta property="og:description" content="En klocka. 15 minuter. Hallå gänget!">', s, 1)
s = s.replace('https://www.buttercup.nu/traning/og.jpg', 'https://www.buttercup.nu/halsoresa/og.jpg').replace('content="https://www.buttercup.nu/traning/"', 'content="https://www.buttercup.nu/halsoresa/"')
rep('<meta name="apple-mobile-web-app-title" content="Stark igen">', '<meta name="apple-mobile-web-app-title" content="Hälsoresan">')
rep('<span class="hide-m">Olistad · träning</span>', '<span class="hide-m">Hasses hälsoresa</span>')
# ingen länk tillbaka till STARK IGEN
s = re.sub(r'\s*<a class="hrlink" href="/traning/">[^<]*</a>', '', s, 1)
s = s.replace("if (hb) hb.textContent = 'Olistad · Hasses hälsoresa';", "")
open(os.path.join(R, 'index.html'), 'w', encoding='utf-8').write(s)

# tillgångar
os.makedirs(os.path.join(R, 'ex', 'hasse'), exist_ok=True); os.makedirs(os.path.join(R, 'hasse'), exist_ok=True)
for f in glob.glob(os.path.join(T, 'ex', 'hasse', '*.webp')): shutil.copy2(f, os.path.join(R, 'ex', 'hasse'))
for f in glob.glob(os.path.join(T, 'hasse', '*.mp3')): shutil.copy2(f, os.path.join(R, 'hasse'))
shutil.copy2(os.path.join(T, 'hasse.webp'), R)
m = json.load(open(os.path.join(T, 'ex', 'manifest.json')))
json.dump({'h': m['h'], 'hasse': m['hasse']}, open(os.path.join(R, 'ex', 'manifest.json'), 'w'), separators=(',', ':'))

# förcacha bara ark som används: 32-rutorsark (_x2) + övriga som nämns i koden och saknar _x2
X2 = set(re.findall(r"'([a-z0-9]+)'", re.search(r"const X2 = new Set\(\[(.*?)\]\)", s, re.S).group(1)))
HFILES = sorted(os.path.basename(f) for f in glob.glob(os.path.join(R, 'ex', 'hasse', '*.webp'))
                if f.endswith('_x2.webp') or (os.path.basename(f)[:-5] not in X2 and ("'" + os.path.basename(f)[:-5] + "'" in s or os.path.basename(f) in s)))
# service worker: version = innehållshash, så varje bygge med ändringar ger ny cache
import hashlib
h = hashlib.sha1(s.encode()).hexdigest()[:8]
core = ['./', './index.html', './manifest.webmanifest', './icon-192.png', './icon-512.png', './hasse.webp', './ex/manifest.json'] + \
       ['./ex/hasse/' + f for f in HFILES] + \
       ['./hasse/' + os.path.basename(f) for f in sorted(glob.glob(os.path.join(R, 'hasse', '*.mp3')))]
sw = open(os.path.join(T, 'sw.js'), encoding='utf-8').read()
sw = re.sub(r"const C = '[^']*';", f"const C = 'halsoresa-{h}';", sw)
sw = re.sub(r"const CORE = \[.*?\];", 'const CORE = ' + json.dumps(core) + ';', sw, flags=re.S)
sw = sw.replace('// Stark igen:', '// Hasses Hälsoresa:')
open(os.path.join(R, 'sw.js'), 'w', encoding='utf-8').write(sw)
print('byggt', len(s), 'tecken, cache', h, len(core), 'filer')
