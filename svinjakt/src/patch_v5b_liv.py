"""Svinjakten v5b: liv (gärdsgård) i stället för direkt game over, lugnare start.
python3 patch_v5b_liv.py
"""
import os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'index.html')
s = open(P, encoding='utf8').read()
assert 'MAXLIV' not in s, 'redan patchad'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("const MAXCREW=12,", "const MAXLIV=5,MAXCREW=12,")
rep("birdTimer=0,fasanTimer=0,", "birdTimer=0,fasanTimer=0,liv=5,hurt=0,")
# lugnare start: 2 svin i mitten, långsammare grundfart
rep("for(let i=0;i<4;i++){spawnBoar(false);boars[i].y=70+i*115;boars[i].x=160+i*105}",
    "liv=MAXLIV;hurt=0;for(let i=0;i<2;i++){spawnBoar(false);boars[i].y=60+i*140;boars[i].x=300+i*120}")
rep("spd:boss?32+wave*2:72+wave*5", "spd:boss?30+wave*4:52+wave*11")
rep("spawnTimer=.8;", "spawnTimer=1.6;")
# svin som tar sig förbi: kostar liv i stället för direkt förlust
rep("for(const o of boars){if(o.y>player.y-35){gameOver(false);return}}",
    "for(const o of boars){if(!o.dead&&o.y>player.y-35){o.dead=true;liv-=o.boss?3:1;hurt=.5;shake=.25;SFX.grunt(o.boss);"
    "boom(o.x,player.y-20,'#C8340A',18);pop(o.boss?'MEGASVINET BRÖT IGENOM!':'ETT SVIN SMET FÖRBI!','#8F1A00',36);"
    "if(liv<=0){gameOver(false);return}}}boars=boars.filter(o=>!o.dead);hurt=Math.max(0,hurt-dt);")
# HUD: liv i våg-pillret
rep("waveEl.textContent='Våg '+wave;", "waveEl.textContent='Våg '+wave+' · '+'♥'.repeat(Math.max(0,liv))+'♡'.repeat(Math.max(0,MAXLIV-liv));")
rep('id="wave">Våg 1</div>', 'id="wave">Våg 1 · ♥♥♥♥♥</div>')
# röd blink när man tappar liv
rep("ctx.globalAlpha=1});\n popups.forEach(",
    "ctx.globalAlpha=1});\n if(hurt>0){ctx.fillStyle='rgba(200,52,10,'+(hurt*.5)+')';ctx.fillRect(0,0,W,H)}\n popups.forEach(")
# texter
rep("Megasvinet nådde scenen.", "Svinen bröt igenom gärdsgården.")
rep("Hunden Leo är på er sida: han rusar fram och biter svinen.",
    "Hunden Leo är på er sida: han rusar fram och biter svinen. Fem liv – varje svin som smiter förbi kostar ett, megasvinet tre.")
rep("window.__sj={dog:()=>dog,", "window.__sj={liv:()=>liv,dog:()=>dog,")
open(P, 'w', encoding='utf8').write(s)
print('ok', len(s))
