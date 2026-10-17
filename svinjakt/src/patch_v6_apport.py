"""Svinjakten v6: hunden heter Lego; skjutna fåglar faller och blir liggande, Lego apporterar dem.
Belöningen (+1 skytt / +50 % eld) kommer först när Lego lämnat fågeln hos gänget.
python3 patch_v6_apport.py
"""
import os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'index.html')
s = open(P, encoding='utf8').read()
assert 'drops=' not in s, 'redan patchad'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


# namn
rep("DOG_NAME='LEO'", "DOG_NAME='LEGO'")
s = s.replace("Hunden Leo är på er sida: han rusar fram och biter svinen.",
              "Hunden Lego är på er sida: han biter svinen och apporterar fåglarna ni skjuter.")
s = s.replace("låt Leo jobba", "låt Lego jobba").replace("<span>Leo = hund</span>", "<span>Lego = hund</span>")
assert 'Leo' not in s and 'LEO' not in s

# state
rep("liv=5,hurt=0,", "liv=5,hurt=0,drops=[],")
rep("liv=MAXLIV;hurt=0;", "liv=MAXLIV;hurt=0;drops=[];")

# fågel träffad: dör, faller och blir liggande (ingen belöning ännu)
rep("if(f.hp<=0&&!f.dead){f.dead=true;boom(f.x,f.y,f.kind==='kungsfasan'?'#e8b630':'#1f9e7a',30);"
    "if(f.kind==='kungsfasan'){SFX.fasan();power=Math.min(4,power*1.5);score+=300;pop('ELDKRAFT +50 %!','#b8860b',50)}"
    "else{SFX.peacock();pop('+1 SKYTT!','#1f5fd1',50);addCrew(Math.min(MAXCREW,crew+1));score+=200}}",
    "if(f.hp<=0&&!f.dead){f.dead=true;boom(f.x,f.y,f.kind==='kungsfasan'?'#e8b630':'#1f9e7a',30);"
    "f.kind==='kungsfasan'?SFX.fasan():SFX.peacock();score+=f.kind==='kungsfasan'?150:100;"
    "drops.push({kind:f.kind,x:clamp(f.x,110,W-110),y:f.y,w:f.w,h:f.h,vy:-160,gy:clamp(f.y+rnd(120,220),330,player.y-170),flip:f.kind==='peacock'?f.vx<0:f.vx>0,"
    "rot:0,st:'fall',life:14});pop('APPORT, LEGO!','#2A1206',44)}")

# fallande/liggande fåglar uppdateras
rep("popups.forEach(p=>p.life-=dt);popups=popups.filter(p=>p.life>0);",
    "popups.forEach(p=>p.life-=dt);popups=popups.filter(p=>p.life>0);"
    "for(const d of drops){if(d.st==='fall'){d.vy+=900*dt;d.y+=d.vy*dt;d.rot=Math.min(Math.PI*.94,d.rot+dt*7);if(d.y>=d.gy){d.y=d.gy;d.st='ground'}}"
    "else if(d.st==='ground'){d.life-=dt}}drops=drops.filter(d=>d.st==='carried'||d.life>0);")


def apport_reward():
    return ("if(d.kind==='kungsfasan'){power=Math.min(4,power*1.5);score+=150;pop('ELDKRAFT +50 %!','#b8860b',50);SFX.power()}"
            "else{pop('+1 SKYTT!','#1f5fd1',50);addCrew(Math.min(MAXCREW,crew+1));score+=100;SFX.gate(2)}")


# hunden: apport går före svinjakt
rep("  if(dog.cd<=0){let best=null,bd=1e9;",
    "  const dr=drops.find(d=>d.st==='ground');if(dr){dog.st='fetch';dog.tgt=dr;dog.bark=1.1;SFX.bark();return}\n"
    "  if(dog.cd<=0){let best=null,bd=1e9;")
rep(" else if(dog.st==='run'){",
    " else if(dog.st==='fetch'){const d=dog.tgt;if(!d||!drops.includes(d)){dog.st='back';return}"
    "const dx=d.x-dog.x,dy=d.y-dog.y,dd=Math.hypot(dx,dy),v=760*dt;"
    "if(dd<v+20){d.st='carried';dog.carry=d;dog.st='return';SFX.flutter(.25)}else{dog.x+=dx/dd*v;dog.y+=dy/dd*v}}\n"
    " else if(dog.st==='return'){const dx=hx-dog.x,dy=hy-dog.y,dd=Math.hypot(dx,dy),v=640*dt;const d=dog.carry;"
    "if(d){d.x=dog.x+(dx<0?-30:30)*.6;d.y=dog.y-18}"
    "if(dd<v+6){if(d){drops=drops.filter(q=>q!==d);boom(dog.x,dog.y-20,d.kind==='kungsfasan'?'#e8b630':'#1f9e7a',22);" + apport_reward() +
    "}dog.carry=null;dog.st='home';dog.cd=rnd(2,4)}else{dog.x+=dx/dd*v;dog.y+=dy/dd*v}}\n"
    " else if(dog.st==='run'){")
# hund vänd åt rätt håll även vid apport
rep("function dogDraw(){const flip=dog.st==='back';",
    "function dogDraw(){const flip=dog.st==='back'||dog.st==='return';")

# rita liggande/fallande/burna fåglar (före hunden så att han syns ovanpå)
rep("dogDraw();const n=Math.min(crew,18);",
    "drops.forEach(d=>{ctx.save();ctx.globalAlpha=d.st==='ground'?Math.min(1,d.life/2):1;ctx.translate(d.x,d.y);"
    "const sc=d.st==='carried'?.45:.75;ctx.rotate((d.flip?-1:1)*d.rot);ctx.scale(sc,sc);drawImg(d.kind,0,0,d.w,d.h,d.flip);ctx.restore();"
    "if(d.st==='ground'){ctx.save();ctx.font='14px Anton';ctx.textAlign='center';ctx.fillStyle='#FFF6DC';ctx.fillText('LEGO HÄMTAR',d.x,d.y+46);ctx.restore()}});\n"
    " dogDraw();const n=Math.min(crew,18);")

# skylt när fågeln dyker upp
rep("'PÅFÅGEL! +1 OM DU TRÄFFAR'", "'PÅFÅGEL! SKJUT – LEGO APPORTERAR'")
rep("'KUNGSFASAN! SKJUT DEN'", "'KUNGSFASAN! SKJUT – LEGO APPORTERAR'")
rep("window.__sj={liv:()=>liv,", "window.__sj={drops:()=>drops.map(d=>d.kind+':'+d.st),liv:()=>liv,")
open(P, 'w', encoding='utf8').write(s)
print('ok', len(s))
