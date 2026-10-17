"""Svinjakten v5c: ändlöst spel med stigande vågor, rekord i localStorage, våg-skyltar.
python3 patch_v5c_endless.py
"""
import os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'index.html')
s = open(P, encoding='utf8').read()
assert 'sj_best' not in s, 'redan patchad'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


# ingen fast vinst; våg-skylt när vågen ökar
rep("if(kills>=WIN_KILLS)gameOver(true);",
    "if(wave>lastWave){lastWave=wave;if(wave>1){pop('VÅG '+wave+'!','#C8340A',60);SFX.gate(3)}}")
rep("let lastBoss=0;", "let lastBoss=0,lastWave=1;")
rep("liv=MAXLIV;hurt=0;", "liv=MAXLIV;hurt=0;lastWave=1;lastBoss=0;")
# vågor: var 25:e kill, svinen blir fler/snabbare/tåligare utan tak på farten
rep("wave=1+Math.floor(kills/28)", "wave=1+Math.floor(kills/25)")
# slutskärm: alltid förlust, men visa våg + rekord
rep("let gameOver=function(win){run=false;over=true;win?SFX.win():SFX.lose();",
    "let gameOver=function(win){run=false;over=true;const best=+localStorage.getItem('sj_best')||0,nyttRek=score>best;"
    "if(nyttRek){localStorage.setItem('sj_best',score);win=true}win?SFX.win():SFX.lose();")
rep("overlay.querySelector('h1').innerHTML=win?'MEGA<br>FÄLLT':'SVINEN<br>VANN';",
    "overlay.querySelector('h1').innerHTML=nyttRek?'NYTT<br>REKORD':'SVINEN<br>VANN';")
rep("win?`Blommeröd räddat! Poäng: <b>${score}</b>. Kör igen och se om du kan få större gäng.`:`Svinen bröt igenom gärdsgården. Poäng: <b>${score}</b>. Ta varje +1 du hinner och låt Leo jobba.`",
    "`Ni höll Blommeröd till <b>våg ${wave}</b> och fällde <b>${kills}</b> svin. Poäng: <b>${score}</b>`+"
    "(nyttRek?(best?` – förra rekordet var ${best}!`:'!'):`. Rekord: <b>${best}</b>.`)+' Ta varje +1 du hinner och låt Leo jobba.'")
# startskärm: visa rekord om det finns
rep("startBtn.onclick=()=>{SFX.init();reset()};",
    "startBtn.onclick=()=>{SFX.init();reset()};{const b=+localStorage.getItem('sj_best')||0;if(b){const r=document.createElement('p');"
    "r.className='small';r.innerHTML='Ditt rekord: <b>'+b+'</b>';startBtn.before(r)}}")
rep("Fem liv – varje svin som smiter förbi kostar ett, megasvinet tre.",
    "Fem liv – varje svin som smiter förbi kostar ett, megasvinet tre. Vågorna tar aldrig slut: hur länge håller ni?")
open(P, 'w', encoding='utf8').write(s)
print('ok', len(s))
