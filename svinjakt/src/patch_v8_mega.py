"""Svinjakten v8: MEGA FIREBALL – knapp som laddas av kills, röjer allt i sin väg.
python3 patch_v8_mega.py
"""
import os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'index.html')
s = open(P, encoding='utf8').read()
assert 'megaFire' not in s, 'redan patchad'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


# CSS för knappen
rep("</style>",
    "#mega{position:absolute;right:14px;bottom:110px;z-index:5;width:92px;height:92px;border-radius:50%;border:4px solid var(--chili);"
    "background:conic-gradient(#ff6a00 calc(var(--c,0)*1turn),rgba(255,246,220,.85) 0);box-shadow:4px 4px 0 var(--chili);"
    "font-family:var(--display);color:var(--ink);font-size:15px;line-height:1;padding:0;cursor:pointer;touch-action:none;"
    "display:grid;place-items:center;text-align:center;opacity:.8;transition:transform .1s}"
    "#mega span{display:block;font-size:30px;line-height:1}"
    "#mega.ready{opacity:1;color:#fff;background:radial-gradient(circle,#ffe14d,#ff6a00 55%,#c8340a);animation:megaPulse .7s infinite alternate}"
    "#mega:active{transform:scale(.92)}"
    "@keyframes megaPulse{from{box-shadow:0 0 0 0 rgba(255,106,0,.8),4px 4px 0 var(--chili)}to{box-shadow:0 0 0 16px rgba(255,106,0,0),4px 4px 0 var(--chili)}}"
    "</style>")
rep("</canvas>", "</canvas><button id=\"mega\" aria-label=\"Mega fireball\"><div><span>🔥</span>MEGA</div></button>")

# state
rep("liv=5,hurt=0,drops=[],", "liv=5,hurt=0,drops=[],mega=0,megaK=0,megaReady=false,fballs=[],")
rep("lastWave=1;lastBoss=0;lastTier=0;", "lastWave=1;lastBoss=0;lastTier=0;mega=0;megaK=0;megaReady=false;fballs=[];")

MEGA = r"""
const MEGA_KILLS=35,megaBtn=document.getElementById('mega');
function megaFire(){if(!run||mega<1)return;mega=0;megaReady=false;SFX.mega();shake=.45;
 fballs.push({x:player.x,y:player.y-70,r:34,vy:-140,hit:new Set()});pop('MEGA FIREBALL!','#ff6a00',62);
 for(let i=0;i<40;i++)particles.push({x:player.x+rnd(-60,60),y:player.y-40,vx:rnd(-240,240),vy:rnd(-320,-40),life:rnd(.3,.8),c:Math.random()<.5?'#ffcf33':'#ff5a00',r:rnd(5,12)})}
megaBtn.addEventListener('pointerdown',e=>{e.preventDefault();e.stopPropagation();megaFire()});
addEventListener('keydown',e=>{if(e.code==='Space'||e.key==='f'||e.key==='F'){e.preventDefault();megaFire()}});
function megaUpdate(dt){
 if(kills>megaK){mega=Math.min(1,mega+(kills-megaK)/MEGA_KILLS);megaK=kills}
 if(mega>=1&&!megaReady){megaReady=true;pop('MEGA FIREBALL REDO!','#ff6a00',42);SFX.power()}
 megaBtn.style.setProperty('--c',mega.toFixed(3));megaBtn.classList.toggle('ready',megaReady);
 for(const f of fballs){if(f.boom){f.R+=1500*dt;f.y=f.by;}else{f.vy=Math.max(-900,f.vy-1400*dt);f.y+=f.vy*dt;f.r=Math.min(125,f.r+260*dt);if(f.y<380){f.boom=true;f.by=f.y;f.R=f.r;shake=.6;SFX.boom();for(let i=0;i<70;i++){const a=rnd(0,7),v=rnd(200,700);particles.push({x:f.x,y:f.y,vx:Math.cos(a)*v,vy:Math.sin(a)*v,life:rnd(.4,1),c:Math.random()<.5?'#ffcf33':'#ff5a00',r:rnd(6,16)})}}}const rad=f.boom?f.R:f.r;
  if(!f.boom)for(let i=0;i<4;i++)particles.push({x:f.x+rnd(-f.r*.6,f.r*.6),y:f.y+f.r*.5,vx:rnd(-60,60),vy:rnd(40,200),life:rnd(.2,.5),c:Math.random()<.5?'#ffb000':'#ff4a00',r:rnd(6,14)});
  for(const o of boars){if(o.dead||f.hit.has(o))continue;const d=Math.hypot(o.x-f.x,o.y-f.y);if(d<rad+o.w*.45){f.hit.add(o);
   if(o.boss){o.hp-=o.max*.55}else o.hp=0;boom(o.x,o.y,'#ff6a00',o.boss?30:14);
   if(o.hp<=0){o.dead=true;SFX.grunt(o.boss);score+=o.boss?500:35;kills++;megaK=kills}}}
  for(const c of cards){if(!c.dead&&Math.hypot(c.x-f.x,c.y-f.y)<rad+50){c.dead=true;SFX.power();power=Math.min(4,power+.1);score+=120;boom(c.x,c.y,'#FCC222',25)}}}
 fballs=fballs.filter(f=>f.boom?f.R<1500:f.y>-200)}
function megaDraw(){for(const f of fballs){if(f.boom){const a=Math.max(0,1-f.R/1500);ctx.save();ctx.globalAlpha=a;ctx.fillStyle='rgba(255,140,0,.18)';ctx.beginPath();ctx.arc(f.x,f.y,f.R,0,7);ctx.fill();ctx.lineWidth=40*a+6;ctx.strokeStyle='#ffcf33';ctx.beginPath();ctx.arc(f.x,f.y,f.R,0,7);ctx.stroke();ctx.lineWidth=14*a+2;ctx.strokeStyle='#ff4a00';ctx.beginPath();ctx.arc(f.x,f.y,f.R*.86,0,7);ctx.stroke();ctx.restore();if(f.R>f.r*3)continue}const g=ctx.createRadialGradient(f.x,f.y,f.r*.1,f.x,f.y,f.r*1.5);
 g.addColorStop(0,'rgba(255,255,220,1)');g.addColorStop(.3,'rgba(255,214,60,.95)');g.addColorStop(.62,'rgba(255,100,0,.8)');g.addColorStop(1,'rgba(200,52,10,0)');
 ctx.fillStyle=g;ctx.beginPath();ctx.arc(f.x,f.y,f.r*1.5,0,7);ctx.fill();
 ctx.strokeStyle='rgba(255,240,180,.7)';ctx.lineWidth=5;for(let i=0;i<6;i++){const a=t*9+i*1.05;ctx.beginPath();ctx.arc(f.x,f.y,f.r*(.75+.12*Math.sin(t*20+i)),a,a+.6);ctx.stroke()}}}
"""
rep("function pop(txt,", MEGA + "function pop(txt,")
rep("dogUpdate(dt);for(const o of boars)", "dogUpdate(dt);megaUpdate(dt);boars=boars.filter(o=>!o.dead);for(const o of boars)")
rep("if(hurt>0){ctx.fillStyle", "megaDraw();\n if(hurt>0){ctx.fillStyle")

# ljud: dånande eldklot
rep(" bark(){",
    " mega(){if(!A||!on)return;const t=now();tone(t,'sawtooth',90,30,1.3,.6,.01,700);tone(t,'sine',60,25,1.4,.8,.005);"
    "noise(t,1.4,500,.5,.6,'lowpass',.02);noise(t+.05,1,2600,.7,.3,'bandpass',.05)},\n bark(){")

# texter
rep("Vågorna tar aldrig slut: hur länge håller ni?",
    "Vågorna tar aldrig slut: hur länge håller ni? 🔥-knappen laddas av varje svin ni fäller – när den lyser, tryck för en MEGA FIREBALL som röjer allt i sin väg (eller mellanslag).")
rep("window.__sj={setKills:", "window.__sj={megaFire,setMega:v=>{mega=v},mega:()=>mega,fb:()=>fballs.length,setKills:")
open(P, 'w', encoding='utf8').write(s)
print('ok', len(s))
