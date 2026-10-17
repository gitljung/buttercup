"""Svinjakten v3: Wille, påfågel, kungsfasan, anslutnings-skyltar, megasvin-varning, '1 skytt'.
python3 patch_v3.py
"""
import os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'index.html')
s = open(P, encoding='utf8').read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:80])
    s = s.replace(a, b)


rep("const names=['peter','hugo','carl','jocke','borka'];",
    "const names=['peter','hugo','carl','jocke','borka','wille'];\n"
    "const JOIN={hugo:'HUGO ANSLUTER!',carl:'CARL TAR POSITION!',jocke:'JOCKE LADDAR OM!',borka:'BORKA KOMMER MED STJÄRNKEPSEN!',wille:'WILLE ÄR HÄR – FEST!'};")
rep("[...names,'boar','megaboar','gate_plus','gate_x2']", "[...names,'boar','megaboar','gate_plus','gate_x2','peacock','kungsfasan']")
rep("cardTimer=0,shake=0;", "cardTimer=0,shake=0,birds=[],popups=[],birdTimer=0,fasanTimer=0;")
rep("cardTimer=5.5;shake=0;", "cardTimer=5.5;shake=0;birds=[];popups=[];birdTimer=8;fasanTimer=rnd(16,24);")

# hjälpare: kompisar ansluter + skyltar + fåglar
rep("function spawnGate(){",
    "function pop(txt,col='#C8340A',size=46){popups.push({txt,col,size,life:1.7,max:1.7})}\n"
    "function addCrew(to){const b=crew;crew=Math.min(40,to);for(let i=b;i<crew&&i<names.length;i++){const k=names[i];if(JOIN[k])pop(JOIN[k])}}\n"
    "function spawnBird(kind){const left=Math.random()<.5,fas=kind==='kungsfasan';"
    "const hp=fas?6+wave*2:10+wave*3;"
    "birds.push({kind,x:left?-110:W+110,y:rnd(200,520),vx:(left?1:-1)*(fas?250+wave*8:120+wave*6),"
    "w:fas?190:160,h:fas?110:134,hp,max:hp,phase:rnd(0,9)});"
    "pop(fas?'KUNGSFASAN! ×2 ELD':'PÅFÅGEL! +3',fas?'#b8860b':'#1f5fd1',38)}\n"
    "function spawnGate(){")

# megasvin-varning
rep("boars.push({x:rnd(80,W-80),y:-80,w:boss?145:72",
    "if(boss)pop('MEGASVIN!','#8F1A00',64);boars.push({x:rnd(80,W-80),y:-80,w:boss?145:72")

# timers + rörelse
rep("if(cardTimer<=0){spawnCard();cardTimer=rnd(7.0,11.0)}",
    "if(cardTimer<=0){spawnCard();cardTimer=rnd(7.0,11.0)}"
    " birdTimer-=dt;fasanTimer-=dt;if(birdTimer<=0){spawnBird('peacock');birdTimer=rnd(10,15)} if(fasanTimer<=0){spawnBird('kungsfasan');fasanTimer=rnd(20,30)}")
rep("cards.forEach(c=>c.y+=c.vy*dt);",
    "cards.forEach(c=>c.y+=c.vy*dt);birds.forEach(f=>{f.x+=f.vx*dt;f.y+=Math.sin(t*(f.kind==='kungsfasan'?7:4)+f.phase)*40*dt});")

# träffar på fåglar
rep("   for(const c of cards){",
    "   for(const f of birds){if(!b.dead&&hit({...b,w:9,h:22},f)){b.dead=true;f.hp-=b.dam;boom(b.x,b.y,'#7fe0ff',3);"
    "if(f.hp<=0&&!f.dead){f.dead=true;boom(f.x,f.y,f.kind==='kungsfasan'?'#e8b630':'#1f9e7a',30);"
    "if(f.kind==='kungsfasan'){power=Math.min(4,power*1.6);score+=300;pop('ELDKRAFT ×2!','#b8860b',50)}"
    "else{addCrew(crew+3);score+=200}}}}\n"
    "   for(const c of cards){")
rep("cards=cards.filter(c=>!c.dead&&c.y<H+120);",
    "cards=cards.filter(c=>!c.dead&&c.y<H+120);birds=birds.filter(f=>!f.dead&&f.x>-160&&f.x<W+160);"
    "popups.forEach(p=>p.life-=dt);popups=popups.filter(p=>p.life>0);")

# portar via addCrew (så skyltarna kommer)
rep("if(g.typ==='plus')crew=Math.min(30,crew+1);else crew=Math.min(40,Math.max(crew+1,crew*2));",
    "if(g.typ==='plus')addCrew(Math.min(30,crew+1));else addCrew(Math.max(crew+1,crew*2));")

# singular
rep("crewEl.textContent=crew+' skyttar';", "crewEl.textContent=crew===1?'1 skytt':crew+' skyttar';")

# rita fåglar + skyltar
rep(" bullets.forEach(b=>{ctx.fillStyle='#ffe68a';",
    " birds.forEach(f=>{const flip=f.kind==='peacock'?f.vx<0:f.vx>0;drawImg(f.kind,f.x,f.y,f.w,f.h,flip);"
    "ctx.fillStyle='#8F1A00';ctx.fillRect(f.x-f.w*.35,f.y-f.h/2-12,f.w*.7,8);ctx.fillStyle='#7fe0ff';ctx.fillRect(f.x-f.w*.35,f.y-f.h/2-12,f.w*.7*(f.hp/f.max),8)});\n"
    " bullets.forEach(b=>{ctx.fillStyle='#ffe68a';")
rep("ctx.globalAlpha=1});ctx.restore();}",
    "ctx.globalAlpha=1});\n"
    " popups.forEach((p,i)=>{const k=p.life/p.max,a=Math.min(1,k*3),sc=1+(1-k)*.15;ctx.save();ctx.globalAlpha=a;"
    "ctx.translate(W/2,250+i*70-(1-k)*40);ctx.scale(sc,sc);ctx.font=p.size+'px Anton';ctx.textAlign='center';ctx.textBaseline='middle';"
    "ctx.lineWidth=10;ctx.strokeStyle='#FFF6DC';ctx.strokeText(p.txt,0,0);ctx.fillStyle=p.col;ctx.fillText(p.txt,0,0);ctx.restore()});"
    "ctx.restore();}")

# startskärmens text
rep("Skjut +1-portar så ansluter Hugo, Carl, Jocke och Borka en efter en.",
    "Ta +1-portar så ansluter Hugo, Carl, Jocke, Borka och Wille en efter en. Skjut påfågeln för +3 skyttar och den snabba kungsfasanen för dubbel eldkraft.")
rep("<span>Megasvin = boss</span>", "<span>Påfågel = +3</span><span>Kungsfasan = ×2 eld</span><span>Megasvin = boss</span>")
rep("Carl, Hugo, Peter, Jocke och Borka", "Carl, Hugo, Peter, Jocke, Borka och Wille", 2)
open(P, 'w', encoding='utf8').write(s)
print('ok', len(s))
