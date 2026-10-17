"""Svinjakten v7: ammo-nivåer (gult -> blått -> rosa, större skott) + svinen blir starkare (argare/pansar) längre in.
python3 patch_v7_ammo.py
"""
import os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'index.html')
s = open(P, encoding='utf8').read()
assert 'AMMO=' not in s, 'redan patchad'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


# --- nivåer ---
rep("let lastBoss=0,lastWave=1;",
    "let lastBoss=0,lastWave=1,lastTier=0;\n"
    "const AMMO=[{at:0,n:'GUL',c:'#ffe68a',g:'rgba(252,194,34,.35)',rx:5,ry:14},"
    "{at:1.8,n:'BLÅ',c:'#8fd8ff',g:'rgba(31,111,255,.38)',rx:8,ry:19},"
    "{at:3.0,n:'ROSA',c:'#ffa6e2',g:'rgba(255,47,168,.42)',rx:11,ry:25}];\n"
    "const tierOf=p=>p>=AMMO[2].at?2:p>=AMMO[1].at?1:0;\n"
    "const PIG=[{n:'',aura:null,bar:'#FCC222',sc:1},{n:'ARGA SVIN!',aura:'rgba(255,120,0,.40)',bar:'#ff8a00',sc:1.12},"
    "{n:'PANSARSVIN!',aura:'rgba(220,0,70,.48)',bar:'#e0003c',sc:1.25}];\n"
    "const pigTier=w=>w>=8?2:w>=4?1:0;")
rep("lastWave=1;lastBoss=0;", "lastWave=1;lastBoss=0;lastTier=0;")

# skott: bär sin nivå
rep("bullets.push({x:laneX(i,n),y:player.y-52,vx:(i-(n-1)/2)*4,vy:-720,dam:1.0*power})",
    "bullets.push({x:laneX(i,n),y:player.y-52,vx:(i-(n-1)/2)*4,vy:-720,dam:1.0*power,tr:tierOf(power)})")
# större träffyta för större skott
for tgt in ("o", "c", "f"):
    rep("hit({...b,w:9,h:22}," + tgt + ")", "hit({...b,w:AMMO[b.tr].rx*2,h:AMMO[b.tr].ry*1.6}," + tgt + ")")
# rita skott med färg + glöd
rep("bullets.forEach(b=>{ctx.fillStyle='#ffe68a';ctx.beginPath();ctx.ellipse(b.x,b.y,5,14,0,0,7);ctx.fill()});",
    "bullets.forEach(b=>{const a=AMMO[b.tr];ctx.fillStyle=a.g;ctx.beginPath();ctx.ellipse(b.x,b.y+4,a.rx*2.1,a.ry*1.5,0,0,7);ctx.fill();"
    "ctx.fillStyle=a.c;ctx.beginPath();ctx.ellipse(b.x,b.y,a.rx,a.ry,0,0,7);ctx.fill();"
    "ctx.fillStyle='rgba(255,255,255,.75)';ctx.beginPath();ctx.ellipse(b.x-a.rx*.25,b.y-a.ry*.3,a.rx*.35,a.ry*.45,0,0,7);ctx.fill()});")
# träffgnistor i ammots färg
rep("b.dead=true;o.hp-=b.dam;boom(b.x,b.y,'#ffd15a',3);", "b.dead=true;o.hp-=b.dam;boom(b.x,b.y,AMMO[b.tr].c,3+b.tr*2);")
# skylt + ljud när ammo går upp en nivå (kollas varje bildruta)
rep("if(wave>lastWave){lastWave=wave;if(wave>1){pop('VÅG '+wave+'!','#C8340A',60);SFX.gate(3)}}",
    "{const tr=tierOf(power);if(tr>lastTier){lastTier=tr;pop(AMMO[tr].n+' AMMO! STÖRRE SKOTT',tr===1?'#1f6fff':'#e0168f',46);SFX.power();boom(player.x,player.y-60,AMMO[tr].c,40)}}"
    "if(wave>lastWave){lastWave=wave;if(wave>1){const pt=pigTier(wave);if(pt>pigTier(wave-1)){pop(PIG[pt].n,'#8F1A00',58);SFX.bossWarn()}"
    "else{pop('VÅG '+wave+'!','#C8340A',60);SFX.gate(3)}}}")

# --- svinen blir starkare ---
# ta bort att eldkraft gör svinen SVAGARE; hp växer snabbare per våg; arga/pansar-svin större
rep("const hp=(boss?80+wave*35:5+wave*2.6)*power**-.08;",
    "const pt=pigTier(wave),hp=(boss?90+wave*45:5+wave*3.2)*(1+wave*.05)*(1+pt*.35);")
rep("boars.push({x:rnd(80,W-80),y:-80,w:boss?145:72,h:boss?110:58,hp,",
    "boars.push({pt,x:rnd(80,W-80),y:-80,w:(boss?145:72)*PIG[pt].sc,h:(boss?110:58)*PIG[pt].sc,hp,")
# rita aura + färgad hälsostapel
rep("boars.forEach(o=>{drawImg(o.img,o.x,o.y,o.w,o.h,true);ctx.fillStyle='#8F1A00';ctx.fillRect(o.x-o.w/2,o.y-o.h/2-14,o.w,8);ctx.fillStyle='#FCC222';",
    "boars.forEach(o=>{const pg=PIG[o.pt||0];if(pg.aura){ctx.fillStyle=pg.aura;ctx.beginPath();ctx.ellipse(o.x,o.y+4,o.w*.62+Math.sin(t*8+o.phase)*3,o.h*.62,0,0,7);ctx.fill()}"
    "drawImg(o.img,o.x,o.y,o.w,o.h,true);ctx.fillStyle='#8F1A00';ctx.fillRect(o.x-o.w/2,o.y-o.h/2-14,o.w,8);ctx.fillStyle=pg.bar;")

# starttext
rep("Skjut påfågeln för en extra skytt och den snabba kungsfasanen för mer eldkraft.",
    "Skjut påfågeln för en extra skytt och den snabba kungsfasanen för mer eldkraft – skotten går från gult till blått till rosa. Men svinen blir argare: orange från våg 4, pansarsvin från våg 8.")
rep("window.__sj={drops:", "window.__sj={setKills:v=>{kills=v},setPower:v=>{power=v},drops:")
open(P, 'w', encoding='utf8').write(s)
print('ok', len(s))

# balans (efter bot-test): långsammare eldkraft
s = open(P, encoding='utf8').read()
for a, b in (("power=Math.min(4,power+.25)", "power=Math.min(4,power+.1)"),
             ("power=Math.min(4,power*1.5);score+=150;pop('ELDKRAFT +50 %!'", "power=Math.min(4,power+.35);score+=150;pop('ELDKRAFT UPP!'"),
             ("<span>Kungsfasan = +50 % eld</span>", "<span>Kungsfasan = mer eld</span>")):
    s = s.replace(a, b)
open(P, 'w', encoding='utf8').write(s)
