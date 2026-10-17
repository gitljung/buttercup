"""Svinjakten v5: längre spel, svårare att växa (bara +1, inga ×2), hunden Leo som biter svin och skäller 'SKIT! SKIT! SKIT!'.
python3 patch_v5.py
"""
import os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'index.html')
s = open(P, encoding='utf8').read()
assert 'DOG_NAME' not in s, 'redan patchad'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


# ---------- balans ----------
# inga ×2-portar: bara +1, och glesare
rep("const typ=Math.random()<.68?'plus':'x2'", "const typ='plus'")
rep("gateTimer=rnd(5.5,8.0)", "gateTimer=rnd(13,19)")
rep("if(g.typ==='plus')addCrew(Math.min(30,crew+1));else addCrew(Math.max(crew+1,crew*2));",
    "addCrew(Math.min(MAXCREW,crew+1));")
# startportarna: bara en +1 (ingen ×2)
rep("gates.push({x:570,y:520,w:120,h:95,typ:'x2',img:'gate_x2',vy:86});", "")
# påfågel ger +1 (inte +3)
rep("else{SFX.peacock();pop('+3 SKYTTAR!','#1f5fd1',50);addCrew(crew+3)",
    "else{SFX.peacock();pop('+1 SKYTT!','#1f5fd1',50);addCrew(Math.min(MAXCREW,crew+1))")
rep("pop(fas?'KUNGSFASAN! SKJUT DEN':'PÅFÅGEL! SKJUT DEN'", "pop(fas?'KUNGSFASAN! SKJUT DEN':'PÅFÅGEL! +1 OM DU TRÄFFAR'")
# kungsfasan: +50 % eldkraft i stället för ×2
rep("power=Math.min(4,power*2);score+=300;pop('ELDKRAFT ×2!','#b8860b',50)",
    "power=Math.min(4,power*1.5);score+=300;pop('ELDKRAFT +50 %!','#b8860b',50)")
rep("'KUNGSFASAN! SKJUT DEN'", "'KUNGSFASAN! SKJUT DEN'")
# vapenkort lite mindre
rep("power=Math.min(4,power+.35)", "power=Math.min(4,power+.25)")
# längre spel: långsammare vågor, fler kills, megasvin var 30:e
rep("wave=1+Math.floor(kills/16)", "wave=1+Math.floor(kills/28)")
rep("spawnBoar(kills>0&&kills%18===0)", "spawnBoar(kills>0&&kills%30===0&&kills!==lastBoss&&(lastBoss=kills))")
rep("spawnTimer=Math.max(.22,1.0-wave*.045)", "spawnTimer=Math.max(.2,1.15-wave*.11)")
rep("if(kills>=55)gameOver(true);", "if(kills>=WIN_KILLS)gameOver(true);")
# fåglar: något glesare påfåglar
rep("birdTimer=rnd(10,15)", "birdTimer=rnd(14,20)")

# ---------- hunden ----------
rep("const names=['peter','hugo','carl','jocke','borka','wille'];",
    "const names=['peter','hugo','carl','jocke','borka','wille'];\n"
    "const MAXCREW=12,WIN_KILLS=150,DOG_NAME='LEO';let lastBoss=0;")
rep("[...names,'boar','megaboar','gate_plus','gate_x2','peacock','kungsfasan']",
    "[...names,'boar','megaboar','gate_plus','gate_x2','peacock','kungsfasan','hund']")
rep("birdTimer=0,fasanTimer=0;", "birdTimer=0,fasanTimer=0,dog={x:0,y:0,st:'home',t:0,cd:4,tgt:null,bark:0};")
rep("birdTimer=8;fasanTimer=rnd(16,24);",
    "birdTimer=10;fasanTimer=rnd(18,26);dog={x:player.x-150,y:player.y+20,st:'home',t:0,cd:4,tgt:null,bark:0};")

DOG = r"""
function dogUpdate(dt){const hx=clamp(player.x-Math.min(190,60+crew*16),60,W-60),hy=player.y+22;dog.bark=Math.max(0,dog.bark-dt);
 if(dog.st==='home'){dog.x+=(hx-dog.x)*Math.min(1,dt*8);dog.y+=(hy-dog.y)*Math.min(1,dt*8);dog.cd-=dt;
  if(dog.cd<=0){let best=null,bd=1e9;for(const o of boars){if(o.y<120||o.dead)continue;const d=player.y-o.y+(o.boss?200:0);if(d<bd){bd=d;best=o}}
   if(best){dog.st='run';dog.tgt=best;dog.bark=1.4;SFX.bark()}else dog.cd=1}}
 else if(dog.st==='run'){const o=dog.tgt;if(!o||o.dead||!boars.includes(o)){dog.st='back';return}
  const dx=o.x-dog.x,dy=o.y-dog.y,d=Math.hypot(dx,dy),v=720*dt;if(d<v+30){o.hp-=o.boss?6+wave*2:4+wave*1.5;boom(o.x,o.y,'#2A1206',10);
   if(o.hp<=0&&!o.dead){o.dead=true;SFX.grunt(o.boss);score+=o.boss?500:35;kills++;boom(o.x,o.y,'#8F1A00',12)}
   else{o.y-=40}dog.st='back'}else{dog.x+=dx/d*v;dog.y+=dy/d*v}}
 else{const dx=hx-dog.x,dy=hy-dog.y,d=Math.hypot(dx,dy),v=620*dt;if(d<v+4){dog.st='home';dog.cd=rnd(5.5,8)}else{dog.x+=dx/d*v;dog.y+=dy/d*v}}}
function dogDraw(){const flip=dog.st==='back';const bob=Math.sin(t*16)*4;drawImg('hund',dog.x,dog.y+bob,96,71,flip);
 if(dog.bark>0){ctx.save();ctx.globalAlpha=Math.min(1,dog.bark*2);const bx=clamp(dog.x+40,150,W-150),by=dog.y-82;ctx.fillStyle='#FFF6DC';ctx.strokeStyle='#2A1206';ctx.lineWidth=4;
  roundRect(bx-108,by-28,216,50,18,true,true);ctx.beginPath();ctx.moveTo(dog.x+10,by+22);ctx.lineTo(dog.x-4,dog.y-38);ctx.lineTo(dog.x+28,by+22);ctx.fill();ctx.stroke();
  ctx.fillStyle='#2A1206';ctx.font='26px Anton';ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText('SKIT! SKIT! SKIT!',bx,by-2);ctx.restore()}
 ctx.save();ctx.font='16px Anton';ctx.textAlign='center';ctx.fillStyle='#FCC222';ctx.fillText(DOG_NAME,dog.x,dog.y+52);ctx.restore()}
"""
rep("function pop(txt,", DOG + "function pop(txt,")
# kör hunden i update (innan game-over-kollen) och rita den bredvid gänget
rep("for(const o of boars){if(o.y>player.y-35){gameOver(false);return}}",
    "dogUpdate(dt);for(const o of boars){if(o.y>player.y-35){gameOver(false);return}}")
rep("const n=Math.min(crew,18);for(let i=0;i<n;i++){const k=names[i%names.length];",
    "dogDraw();const n=Math.min(crew,18);for(let i=0;i<n;i++){const k=names[i%names.length];")

# skall-ljud
rep(" grunt(boss){",
    " bark(){if(!A||!on)return;const t=now();for(let i=0;i<3;i++){const u=t+i*.2;tone(u,'sawtooth',520,260,.11,.4,.004,1800);"
    "noise(u,.08,1400,1.5,.25,'bandpass',.003)}},\n grunt(boss){")

# texter
rep("Ta +1-portar så ansluter Hugo, Carl, Jocke, Borka och Wille en efter en. Skjut påfågeln för +3 skyttar och den snabba kungsfasanen för dubbel eldkraft.",
    "Ta +1-portar så ansluter Hugo, Carl, Jocke, Borka och Wille en efter en – men de är sällsynta. Skjut påfågeln för en extra skytt och den snabba kungsfasanen för mer eldkraft. Hunden Leo är på er sida: han rusar fram och biter svinen.")
rep("<span>×2 gäng</span>", "<span>Leo = hund</span>")
rep("<span>Påfågel = +3</span><span>Kungsfasan = ×2 eld</span>", "<span>Påfågel = +1</span><span>Kungsfasan = +50 % eld</span>")
rep("Försök få fler +1 och ×2 innan bossen.", "Ta varje +1 du hinner och låt Leo jobba.")

# debug-krok: hunden + kills
rep("window.__sj={st:()=>({crew,", "window.__sj={dog:()=>dog,bo:()=>boars.map(o=>[Math.round(o.x),Math.round(o.y),o.boss?1:0]),ga:()=>gates.map(g=>[Math.round(g.x),Math.round(g.y)]),st:()=>({kills,wave,crew,")
open(P, 'w', encoding='utf8').write(s)
print('ok', len(s))
