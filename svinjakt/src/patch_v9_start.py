"""Svinjakten v9: Kör-knappen direkt under rubriken, reglerna i en hopfälld "Så spelar du".
python3 patch_v9_start.py
"""
import os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'index.html')
s = open(P, encoding='utf8').read()
assert 'id="rules"' not in s, 'redan patchad'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


i = s.index('<div class="center" id="overlay"><div class="card">')
j = s.index('<button id="start">Kör</button></div>', i) + len('<button id="start">Kör</button></div>')
old = s[i:j]
lp0 = old.index('</h1><p>') + len('</h1><p>')
rules = old[lp0:old.index('</p><div class="legend">')]
legend = old[old.index('<div class="legend">'):old.index('<button id="start">')]
new = ('<div class="center" id="overlay"><div class="card"><p class="small">Blommeröd runner shooter</p><h1>SVIN<br>JAKTEN</h1>'
       '<p class="lead">Dra gänget i sidled, fäll svinen och tryck 🔥 när den lyser.</p>'
       '<button id="start">Kör</button>'
       '<details id="rules"><summary>Så spelar du</summary><p>' + rules + '</p>' + legend + '</details></div>')
s = s[:i] + new + s[j:]

# CSS: kortet får scrolla om det ändå blir högt, knappen stor och i fokus
rep("</style>",
    ".card{max-height:calc(100% - 20px);overflow:auto}.card .lead{margin:10px 0 14px}"
    "#start{font-size:38px;padding:14px 46px;margin:4px 0 6px;animation:startPulse 1s infinite alternate}"
    "@keyframes startPulse{from{transform:scale(1)}to{transform:scale(1.06)}}"
    "#rules{margin-top:14px;text-align:left}#rules summary{cursor:pointer;text-align:center;font-family:var(--label);font-weight:700;"
    "text-transform:uppercase;letter-spacing:.08em;color:var(--chili);font-size:17px}#rules p{font-size:15px;font-weight:700}"
    "</style>")

# slutskärmens text skrivs till ledet (inte till regeltexten)
rep("overlay.querySelector('p:nth-of-type(2)').innerHTML=", "overlay.querySelector('.lead').innerHTML=")
# rekordraden under knappen
rep("startBtn.before(r)", "startBtn.after(r)")
# MEGA-knappen syns bara under spel
rep('<button id="mega" aria-label="Mega fireball">', '<button id="mega" aria-label="Mega fireball" style="display:none">')
rep("megaBtn.style.setProperty('--c',mega.toFixed(3));", "megaBtn.style.display='';megaBtn.style.setProperty('--c',mega.toFixed(3));")
rep("let gameOver=function(win){run=false;", "let gameOver=function(win){run=false;megaBtn.style.display='none';document.getElementById('rules').open=false;")
open(P, 'w', encoding='utf8').write(s)
print('ok', len(s))
