"""Svinjakten v10: SISTA BOSS – Bisse fast i Bloggträsket, omringad av pansarvildsvin. Skjut henne fri.
python3 patch_v10_bisse.py
"""
import os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'index.html')
s = open(P, encoding='utf8').read()
assert 'swamp' not in s, 'redan patchad'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("[...names,'boar','megaboar',", "[...names,'bisse','boar','megaboar',")
rep("liv=5,hurt=0,drops=[],", "liv=5,hurt=0,drops=[],swamp=null,saved=false,")
rep("lastWave=1;lastBoss=0;lastTier=0;", "lastWave=1;lastBoss=0;lastTier=0;swamp=null;saved=false;")

BOSS = r"""
const BOSS_WAVE=10,GUARDS=10;
function startSwamp(){swamp={x:W/2,y:-170,vy:9,ang:0,t:0,done:false};boars=boars.filter(o=>!o.guard);
 const hp=(5+BOSS_WAVE*3.2)*(1+BOSS_WAVE*.05)*1.7*9;
 for(let i=0;i<GUARDS;i++)boars.push({pt:2,guard:true,gi:i,x:W/2,y:-170,w:72*1.3,h:58*1.3,hp,max:hp,spd:0,boss:false,img:'boar',phase:rnd(0,9)});
 pop('SISTA BOSS!','#8F1A00',64);pop('BISSE SITTER FAST I BLOGGTRÄSKET!','#2A1206',32);pop('SKJUT HENNE FRI!','#C8340A',44);SFX.bossWarn()}
function swampUpdate(dt){if(!swamp){if(wave>=BOSS_WAVE&&!saved)startSwamp();return}
 const sw=swamp;sw.t+=dt;sw.y=Math.min(player.y-150,sw.y+(sw.y<230?120:sw.vy)*dt);sw.x=W/2+Math.sin(sw.t*.35)*110;sw.ang+=dt*.55;
 const g=boars.filter(o=>o.guard&&!o.dead),n=g.length;
 g.forEach((o,k)=>{const a=sw.ang+k/Math.max(1,n)*Math.PI*2,rx=215+Math.sin(sw.t*1.3+k)*12,ry=118;o.x=sw.x+Math.cos(a)*rx;o.y=sw.y+10+Math.sin(a)*ry});
 if(n===0&&!sw.done){sw.done=true;saved=true;score+=5000;pop('BISSE RÄDDAD!','#1f9e7a',66);SFX.power();
  for(let i=0;i<90;i++){const a=rnd(0,7),v=rnd(150,600);particles.push({x:sw.x,y:sw.y-40,vx:Math.cos(a)*v,vy:Math.sin(a)*v-200,life:rnd(.5,1.4),c:['#FCC222','#ff6ac1','#29a7ff','#FFF6DC'][i%4],r:rnd(5,12)})}
  sw.endT=sw.t+2.6}
 if(sw.done&&sw.t>=sw.endT){gameOver(true);return}
 if(!sw.done&&sw.y>=player.y-150){liv=0;hurt=.8;pop('BLOGGTRÄSKET SVALDE ER!','#2A1206',40);gameOver(false)}}
function swampHit(b){const sw=swamp;if(!sw||sw.done)return false;if(Math.abs(b.x-sw.x)<80&&b.y>sw.y-160&&b.y<sw.y+30){b.dead=true;boom(b.x,b.y,'#5a4a2a',4);return true}return false}
function swampDraw(){const sw=swamp;if(!sw)return;const lift=sw.done?Math.min(1,(sw.t-sw.doneT||0)):0;
 ctx.save();ctx.fillStyle='rgba(60,70,30,.55)';ctx.beginPath();ctx.ellipse(sw.x,sw.y+18,240,120,0,0,7);ctx.fill();
 const g=ctx.createRadialGradient(sw.x,sw.y+10,20,sw.x,sw.y+10,220);g.addColorStop(0,'#5b4a2c');g.addColorStop(.7,'#3d3a1f');g.addColorStop(1,'rgba(40,45,20,.0)');
 ctx.fillStyle=g;ctx.beginPath();ctx.ellipse(sw.x,sw.y+14,225,108,0,0,7);ctx.fill();
 ctx.fillStyle='rgba(150,170,90,.5)';for(let i=0;i<7;i++){const a=sw.t*.7+i*.9,bx=sw.x+Math.cos(a*1.3)*150,by=sw.y+14+Math.sin(a)*60,r=5+3*Math.sin(sw.t*3+i);ctx.beginPath();ctx.arc(bx,by,Math.max(1,r),0,7);ctx.fill()}
 ctx.restore()}
function bisseDraw(){const sw=swamp;if(!sw)return;ctx.save();ctx.font='24px Anton';ctx.textAlign='center';ctx.fillStyle='#FFF6DC';ctx.strokeStyle='#2A1206';ctx.lineWidth=6;
 ctx.strokeText('BLOGGTRÄSKET',sw.x,sw.y+128);ctx.fillText('BLOGGTRÄSKET',sw.x,sw.y+128);ctx.restore();
 const bob=Math.sin(sw.t*1.6)*5,up=sw.done?Math.min(90,(sw.t-(sw.tDone||(sw.tDone=sw.t)))*120):0;
 drawImg('bisse',sw.x,sw.y-55+bob-up,185,206);
 if(!sw.done){const n=boars.filter(o=>o.guard&&!o.dead).length;ctx.save();ctx.font='20px Anton';ctx.textAlign='center';
  const txt='RÄDDA BISSE! '+n+' PANSARSVIN KVAR';ctx.lineWidth=5;ctx.strokeStyle='#FFF6DC';ctx.strokeText(txt,sw.x,sw.y-185);ctx.fillStyle='#C8340A';ctx.fillText(txt,sw.x,sw.y-185);ctx.restore()}}
"""
rep("function pop(txt,", BOSS + "function pop(txt,")

# guards rör sig inte själva
rep("boars.forEach(o=>{o.y+=o.spd*dt;", "boars.forEach(o=>{if(o.guard)return;o.y+=o.spd*dt;")
# kulor som träffar Bisse fastnar i träsket (hon skyddas)
rep("for(const b of bullets){for(const o of boars){", "for(const b of bullets){if(swampHit(b))continue;for(const o of boars){if(o.guard&&swamp&&swamp.y<200)continue;")
# under bossen: glesare vanliga svin, inga megasvin, inga portar
rep("if(spawnTimer<=0){spawnBoar(kills>0&&kills%30===0&&kills!==lastBoss&&(lastBoss=kills));spawnTimer=Math.max(.2,1.15-wave*.11)}",
    "if(spawnTimer<=0){spawnBoar(!swamp&&kills>0&&kills%30===0&&kills!==lastBoss&&(lastBoss=kills));spawnTimer=swamp?2.6:Math.max(.2,1.15-wave*.11)}")
# mega: vakterna tar 40 % i stället för att dö direkt
rep("if(o.boss){o.hp-=o.max*.55}else o.hp=0;", "if(o.boss){o.hp-=o.max*.55}else if(o.guard){o.hp-=o.max*.4}else o.hp=0;")
# vakter räknas inte som 'smet förbi'
rep("for(const o of boars){if(!o.dead&&o.y>player.y-35){", "swampUpdate(dt);if(!run)return;for(const o of boars){if(!o.guard&&!o.dead&&o.y>player.y-35){")
# rita träsket under svinen
rep("boars.forEach(o=>{const pg=PIG[o.pt||0];", "swampDraw();\n boars.forEach(o=>{const pg=PIG[o.pt||0];")
# slutskärm
rep("overlay.querySelector('h1').innerHTML=nyttRek?'NYTT<br>REKORD':'SVINEN<br>VANN';",
    "overlay.querySelector('h1').innerHTML=saved?'BISSE<br>RÄDDAD!':nyttRek?'NYTT<br>REKORD':'SVINEN<br>VANN';")
rep("overlay.querySelector('.lead').innerHTML=`Ni höll Blommeröd till",
    "overlay.querySelector('.lead').innerHTML=(saved?'Ni sköt Bisse fri ur Bloggträsket – Blommeröd är räddat! 🎉 ':'')+`Ni höll Blommeröd till")
# regler
rep("Vågorna tar aldrig slut: hur länge håller ni?",
    "På våg 10 väntar sista bossen: Bisse sitter fast i Bloggträsket, omringad av pansarvildsvin. Skjut svinen runt henne (inte henne!) innan träsket når er.")
rep("window.__sj={megaFire,", "window.__sj={swamp:()=>swamp&&{y:Math.round(swamp.y),done:swamp.done,g:boars.filter(o=>o.guard&&!o.dead).length},startSwamp,saved:()=>saved,megaFire,")
open(P, 'w', encoding='utf8').write(s)
print('ok', len(s))

s = open(P, encoding='utf8').read()
s = s.replace("megaDraw();\n if(hurt>0)", "bisseDraw();megaDraw();\n if(hurt>0)", 1)
s = s.replace("+' Ta varje +1 du hinner och låt Lego jobba.'", "+(saved?'':' Ta varje +1 du hinner och låt Lego jobba.')", 1)
open(P, 'w', encoding='utf8').write(s)

# rensa distraktioner under bossen + rekordrad
s = open(P, encoding="utf8").read()
for a, b in [('if(gateTimer<=0){spawnGate();', 'if(gateTimer<=0&&!swamp){spawnGate();'), ('if(cardTimer<=0){spawnCard();', 'if(cardTimer<=0&&!swamp){spawnCard();'), ("if(birdTimer<=0){spawnBird('peacock');", "if(birdTimer<=0&&!swamp){spawnBird('peacock');"), ("if(fasanTimer<=0){spawnBird('kungsfasan');", "if(fasanTimer<=0&&!swamp){spawnBird('kungsfasan');"), ("startBtn.textContent='Kör igen'", "startBtn.textContent='Kör igen';{const b=+localStorage.getItem('sj_best')||0;let r=document.getElementById('rek');if(!r){r=document.createElement('p');r.id='rek';r.className='small';startBtn.after(r)}r.innerHTML='Ditt rekord: <b>'+b+'</b>'}"), ("r.className='small';r.innerHTML='Ditt rekord: <b>'+b+'</b>';startBtn.after(r)", "r.id='rek';r.className='small';r.innerHTML='Ditt rekord: <b>'+b+'</b>';startBtn.after(r)"), ('function startSwamp(){swamp={', 'function startSwamp(){gates=[];cards=[];birds=[];swamp={')]:
    s = s.replace(a, b, 1)
open(P, "w", encoding="utf8").write(s)
