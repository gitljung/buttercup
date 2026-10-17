"""Svinjakten v4: syntetiserat WebAudio-ljud (inga ljudfiler) + ljud av/på-knapp.
python3 patch_v4_ljud.py
"""
import os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'index.html')
s = open(P, encoding='utf8').read()
assert 'const SFX=' not in s, 'redan patchad'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:80])
    s = s.replace(a, b)


SFX = r"""
const SFX=(()=>{let A=null,M=null,NB=null,on=localStorage.getItem('sj_mute')!=='1',lastPang=-1,lastGrunt=-1;
function init(){if(A){if(A.state==='suspended')A.resume();return}const C=window.AudioContext||window.webkitAudioContext;if(!C)return;A=new C();
 M=A.createGain();M.gain.value=on?.55:0;const cp=A.createDynamicsCompressor();cp.threshold.value=-14;cp.ratio.value=6;M.connect(cp);cp.connect(A.destination);
 NB=A.createBuffer(1,A.sampleRate,A.sampleRate);const d=NB.getChannelData(0);for(let i=0;i<d.length;i++)d[i]=Math.random()*2-1}
const now=()=>A.currentTime;
function env(g,t,a,peak,dec){g.gain.setValueAtTime(0.0001,t);g.gain.exponentialRampToValueAtTime(peak,t+a);g.gain.exponentialRampToValueAtTime(0.0001,t+a+dec)}
function noise(t,dur,f,q,peak,type='bandpass',a=.002){const n=A.createBufferSource();n.buffer=NB;n.playbackRate.value=.7+Math.random()*.6;
 const fl=A.createBiquadFilter();fl.type=type;fl.frequency.setValueAtTime(f,t);fl.Q.value=q;const g=A.createGain();env(g,t,a,peak,dur);
 n.connect(fl);fl.connect(g);g.connect(M);n.start(t,Math.random()*.5);n.stop(t+a+dur+.05);return fl}
function tone(t,type,f0,f1,dur,peak,a=.01,flt=0){const o=A.createOscillator();o.type=type;o.frequency.setValueAtTime(f0,t);
 if(f1!==f0)o.frequency.exponentialRampToValueAtTime(f1,t+dur);const g=A.createGain();env(g,t,a,peak,dur);let last=o;
 if(flt){const fl=A.createBiquadFilter();fl.type='lowpass';fl.frequency.value=flt;o.connect(fl);last=fl}last.connect(g);g.connect(M);o.start(t);o.stop(t+a+dur+.05);return o}
const P={
 pang(n){if(!A||!on)return;const t=now();if(t-lastPang<.085)return;lastPang=t;const k=Math.min(1,.35+n*.05);
  const u=t+.004;noise(u,.11,1500+Math.random()*900,.9,.5*k,'bandpass',.003);tone(u,'square',200,60,.09,.22*k,.002,1600)},
 grunt(boss){if(!A||!on)return;const t=now();if(!boss&&t-lastGrunt<.12)return;lastGrunt=t;const f=boss?62:95+Math.random()*40,d=boss?.7:.26;
  const o=tone(t,'sawtooth',f*1.25,f*.7,d,boss?.5:.32,.012,boss?500:850);const l=A.createOscillator(),lg=A.createGain();l.frequency.value=boss?18:28;lg.gain.value=f*.35;l.connect(lg);lg.connect(o.frequency);l.start(t);l.stop(t+d+.1);
  noise(t,d*.8,boss?260:420,2,boss?.35:.18,'bandpass',.02);if(boss)P.boom()},
 boom(){if(!A||!on)return;const t=now();tone(t,'sine',120,32,.9,.8,.004);noise(t,.6,600,.6,.45,'lowpass',.004)},
 bossWarn(){if(!A||!on)return;const t=now();for(let i=0;i<3;i++){tone(t+i*.42,'sawtooth',55,48,.36,.42,.02,320);tone(t+i*.42,'sine',41,38,.38,.5,.02)}},
 peacock(){if(!A||!on)return;const t=now();for(const s of [0,.42]){const o=A.createOscillator();o.type='sawtooth';
  o.frequency.setValueAtTime(620,t+s);o.frequency.exponentialRampToValueAtTime(1500,t+s+.12);o.frequency.exponentialRampToValueAtTime(820,t+s+.34);
  const v=A.createOscillator(),vg=A.createGain();v.frequency.value=38;vg.gain.value=55;v.connect(vg);vg.connect(o.frequency);
  const f1=A.createBiquadFilter();f1.type='bandpass';f1.frequency.value=1200;f1.Q.value=1.2;const g=A.createGain();env(g,t+s,.02,.9,.34);
  o.connect(f1);f1.connect(g);g.connect(M);o.start(t+s);v.start(t+s);o.stop(t+s+.42);v.stop(t+s+.42)}},
 flutter(dur=.5){if(!A||!on)return;const t=now();const fl=noise(t,dur,900,.8,.3,'bandpass',.01);const g=A.createGain();g.gain.value=0;
  const am=A.createOscillator(),ag=A.createGain();am.frequency.value=22;ag.gain.value=1;am.connect(ag);fl.disconnect();const out=A.createGain();out.gain.value=.5;
  fl.connect(out);ag.connect(out.gain);out.connect(M);am.start(t);am.stop(t+dur+.05)},
 fasan(){if(!A||!on)return;const t=now();P.flutter(.55);for(let i=0;i<4;i++)tone(t+.05+i*.09,'square',1900-i*120,1300-i*90,.06,.16,.004,3200)},
 birdIn(kind){if(!A||!on)return;if(kind==='peacock'){const t=now();tone(t,'triangle',900,1300,.18,.12,.02)}else P.flutter(.35)},
 gate(n=1){if(!A||!on)return;const t=now(),notes=[523,659,784,1046];for(let i=0;i<Math.min(4,1+n);i++)tone(t+i*.065,'triangle',notes[i],notes[i],.16,.34,.005)},
 power(){if(!A||!on)return;const t=now();tone(t,'square',300,1200,.35,.34,.01,2400);tone(t+.08,'triangle',600,2000,.3,.3,.01)},
 lose(){if(!A||!on)return;const t=now();[392,370,349,262].forEach((f,i)=>{const o=tone(t+i*.32,'sawtooth',f,f*(i===3?.9:1),i===3?.9:.28,.28,.02,900)})},
 win(){if(!A||!on)return;const t=now();[523,659,784,1046,784,1046].forEach((f,i)=>tone(t+i*.12,'square',f,f,i===5?.6:.11,.2,.005,3000));
  noise(t+.3,1.6,2400,.5,.12,'bandpass',.4)}
};
Object.defineProperty(P,'on',{get:()=>on});return Object.assign(P,{init,toggle(){on=!on;localStorage.setItem('sj_mute',on?'0':'1');if(M)M.gain.setTargetAtTime(on?.55:0,A.currentTime,.02);if(on)init();return on}});
})();
"""

# ljudmotor direkt efter assets-inläsningen
rep("const W=720,H=1080,assets={};", "const W=720,H=1080,assets={};" + SFX)

# start = användargest -> låt AudioContext starta
rep("startBtn.onclick=reset;", "startBtn.onclick=()=>{SFX.init();reset()};\n"
    "const sndBtn=document.getElementById('snd');const sndLbl=()=>sndBtn.textContent=SFX.on?'🔊':'🔇';sndLbl();"
    "sndBtn.onclick=e=>{e.stopPropagation();SFX.toggle();sndLbl()};")

# skott: en "pang" per salva
rep("fireTimer=fireRate}", "fireTimer=fireRate;SFX.pang(n)}")

# svin fällt
rep("if(o.hp<=0&&!o.dead){o.dead=true;score+=o.boss?500:35;",
    "if(o.hp<=0&&!o.dead){o.dead=true;SFX.grunt(o.boss);score+=o.boss?500:35;")
# vapenkort
rep("if(c.hp<=0&&!c.dead){c.dead=true;", "if(c.hp<=0&&!c.dead){c.dead=true;SFX.power();")
# port
rep("g.used=true;", "g.used=true;SFX.gate(g.typ==='x2'?3:1);")
# megasvin-varning
rep("if(boss)pop('MEGASVIN!','#8F1A00',64);", "if(boss){pop('MEGASVIN!','#8F1A00',64);SFX.bossWarn()}")
# fåglar
rep("if(f.kind==='kungsfasan'){power=", "if(f.kind==='kungsfasan'){SFX.fasan();power=")
rep("else{pop('+3 SKYTTAR!'", "else{SFX.peacock();pop('+3 SKYTTAR!'")
rep("pop(fas?'KUNGSFASAN! SKJUT DEN'", "SFX.birdIn(kind);pop(fas?'KUNGSFASAN! SKJUT DEN'")
# slut
rep("let gameOver=function(win){run=false;over=true;", "let gameOver=function(win){run=false;over=true;win?SFX.win():SFX.lose();")

# knapp i HUD (hud har pointer-events:none -> knappen får auto)
rep('class="hud">', 'class="hud"><button class="pill" id="snd" aria-label="Ljud av/på" '
    'style="pointer-events:auto;cursor:pointer;font-size:18px;padding:5px 9px">🔊</button>')

# debug-krok: exponera SFX
rep("window.__sj={st:", "window.__sfx=SFX;window.__sj={st:")
open(P, 'w', encoding='utf8').write(s)
print('ok', len(s))
