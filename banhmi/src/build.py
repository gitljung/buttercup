"""Bygger banhmi/index.html från planuea-skalet (head/CSS) + innehållet nedan."""
import os, re
D = os.path.dirname(os.path.abspath(__file__))
s = open(os.path.join(D, '..', '..', 'planuea', 'index.html')).read()
head = s[:s.index('</style>')]
head = head.replace('family=Kanit:wght@500&', 'family=Kanit:wght@500&family=Noto+Sans+Lao:wght@500&')
head = head.replace('.card p.th{font-family:"Kanit",var(--label)', '.card p.th{font-family:"Kanit","Noto Sans Lao",var(--label)')

TITLE = "BAHN FAKKIN MI · LECHON & JEOW BÁNH MÌ"
DESC = ("Bánh mì med lechon belly – sidfläsk med krispig puffsvål, långkokt i 120 °C – och laotisk jeow som "
        "på kalamansi, fisksås, vitlök och chili. Efter Raymond Vera Cruz.")
head = re.sub(r'<title>.*?</title>', f'<title>{TITLE} · Buttercup</title>', head)
head = re.sub(r'(<meta name="description" content=")[^"]*', r'\g<1>' + DESC, head)
head = re.sub(r'(<meta property="og:description" content=")[^"]*', r'\g<1>' + DESC, head)
head = re.sub(r'(<meta property="og:title" content=")[^"]*', r'\g<1>' + TITLE, head)
head = head.replace('/planuea/', '/banhmi/')
assert 'planuea' not in head

CSS = """
.grp{display:flex;align-items:baseline;justify-content:center;gap:14px;flex-wrap:wrap;margin:38px 0 18px;text-align:center}
.grp:first-of-type{margin-top:8px}
.grp h3{font-family:var(--display);font-weight:400;text-transform:uppercase;color:var(--chili);font-size:clamp(34px,6vw,56px);line-height:1;margin:0;
  text-shadow:3px 3px 0 rgba(143,26,0,.25)}
.grp span{font-family:var(--label);font-weight:700;text-transform:uppercase;letter-spacing:.1em;font-size:14px;color:var(--oxblood)}
.grp b{font-family:"Kanit","Noto Sans Lao",sans-serif;font-weight:500;letter-spacing:0;text-transform:none;font-size:20px;color:var(--chili)}
@media (min-width:1000px){.grid{grid-template-columns:repeat(4,1fr)}}
.temps{display:flex;gap:10px;flex-wrap:wrap;margin:4px 0 2px}
.temps span{font-family:var(--display);font-size:19px;background:var(--chili);color:var(--cream);border-radius:12px;padding:6px 12px;box-shadow:3px 3px 0 var(--oxblood)}
"""

BODY = """
</style>
</head>
<body>
<div class="bc-bar"><a href="/">← Buttercup.nu</a><span>Kök · rätt</span><b>Plan B(lommeröd)</b></div>

<header>
  <p class="eyebrow">Lechon cebu · Jeow som · Bánh mì</p>
  <h1><span class="row">BAHN FAKKIN</span><span class="row">MI</span></h1>
  <p class="recipe">LECHON &amp; JEOW BÁNH MÌ</p>
  <p class="sub">3 delar · 24 kort · ca 4 baguetter</p>
  <span class="badge">2 dygn i kylen · värt varje minut</span>
</header>

<main>
  <p class="legend"><span><i class="est">~1 msk</i>Alla mängder är våra uppskattningar</span><span><i>Del 1</i>Hänvisar till en del ovan</span></p>

  <div class="grp"><h3>1 · Lechon</h3><span>Filippinsk rullad sidfläsk · <b>litson liempo</b></span></div>
  <ul class="grid" id="g1"></ul>

  <div class="grp"><h3>2 · Jeow som</h3><span>Laotisk sur chilisås · <b lang="lo">ແຈ່ວສົ້ມ</b></span></div>
  <ul class="grid" id="g2"></ul>

  <div class="grp"><h3>3 · Bánh mì</h3><span>Vietnamesisk baguette · <b lang="vi">bánh mì</b></span></div>
  <ul class="grid" id="g3"></ul>

  <section class="panel dish">
    <h3>Så gör du</h3>
    <div class="phase"><h4>1 · Lechon (2 dygn i förväg)</h4>
      <ol class="steps">
        <li><div>Stick hål i <b>svålen</b> över hela ytan, tätt. Han använder ett knippe grillpinnar som en spikmatta.</div></li>
        <li><div>Vänd. Skåra <b>köttsidan</b> i rutor, ner mot svålen men inte igenom.</div></li>
        <li><div>Gnid in rubben i alla skåror: <b>socker, salt, paprika, vitlökspulver och peppar</b>.</div></li>
        <li><div>Strö över <b>citrongräs</b> och hela pepparkorn. Lägg <b>salladslök</b> på längden, <b>lagerblad</b> ovanpå och en hel knippe <b>koriander</b>.</div></li>
        <li><div>Vik ihop till en rulle och <b>sy eller knyt den</b>. Tekniken lärde han sig av en sjuksköterska. Linda folie runt köttet så att bara svålen syns.</div></li>
        <li><div>Pensla svålen och <b>salta den</b>. Ställ den <b>otäckt i kylen i 2 dygn</b> så att svålen torkar och rubben drar in.</div></li>
      </ol></div>
    <div class="phase"><h4>2 · Ugnen</h4>
      <div class="temps"><span>120 °C → 90 °C inne · ca 3 h</span><span>230 °C · 15 min</span><span>Grill 230 °C · 10 min</span></div>
      <ol class="steps">
        <li><div>Låt den gå <b>lågt och länge i 120 °C (250 °F)</b> tills innertemperaturen är <b>90 °C (195 °F)</b>, ungefär 3 timmar.</div></li>
        <li><div>Höj till <b>230 °C (450 °F) i 15 minuter</b> och kör sedan <b>grillelementet på 230 °C i 10 minuter</b> tills svålen puffar upp till luftig crackling. Håll koll så att den inte bränns.</div></li>
        <li><div>Låt vila en stund och skiva i tjocka bitar, med svål på varje skiva.</div></li>
      </ol></div>
    <div class="phase"><h4>3 · Jeow som</h4>
      <ol class="steps">
        <li><div>Lägg <b>riven vitlök, krossad torkad chili och kandisocker</b> i en skål.</div></li>
        <li><div>Häll på <b>kalamansijuice</b> i stället för lime, sedan <b>fisksås</b>. Rör tills sockret har löst sig.</div></li>
        <li><div>Vänd ner massor av hackad <b>koriander</b>. Smaka av: surt först, sedan salt, sött och hett.</div></li>
      </ol></div>
    <div class="phase"><h4>4 · Bygg</h4>
      <ol class="steps">
        <li><div>Snitta baguetten längs ena sidan. Bred <b>pâté</b> på ena halvan och <b>majonnäs</b> på den andra.</div></li>
        <li><div>Lägg i skivorna med <b>lechon</b> och ringla <b>jeow som</b> över, gärna rikligt.</div></li>
        <li><div>Toppa med <b>gurkstavar, đồ chua och koriander</b>. Skär itu och ät direkt medan svålen knastrar.</div></li>
      </ol></div>
  </section>

  <div class="two">
    <section class="panel">
      <h3>Tips</h3>
      <div class="store"><span>Torr svål</span><span>Termometer</span><span>Đồ chua</span></div>
      <p>Det är de <b>två dygnen i kylen</b> som ger luftig crackling. Svålen ska kännas torr som papper innan den åker in. Använd en <b>stektermometer</b>: hela poängen är 90 °C inne före värmechocken.</p>
      <p>Đồ chua görs inte i videon. Så här gör vi: strimla morot och daikon, salta lätt i 10 minuter, skölj och lägg i lika delar ättika och vatten med socker efter smak. De är klara efter en timme.</p>
    </section>
    <section class="panel">
      <h3>Om receptet</h3>
      <p class="note">Källa: <a href="https://www.instagram.com/reel/DfD-HyJvgX8/">Raymond Vera Cruz (@raymondveracruz) på Instagram</a>, ”SỤBUẤY Sandwiches Vol. XII: Lechon &amp; Jeow Banh Mi”. Han har utvecklat sin lechon i tio år. Rubben, de två dygnen, alla temperaturer och att lime byts mot kalamansi kommer från hans text. <b>Inga mängder anges</b>, så de gula streckade lapparna är våra uppskattningar för ett ca 1,2 kg sidfläsk. Vad han penslar svålen med syns inte. Fyllningarna i baguetten och đồ chua-receptet har vi läst ut av bilderna. Namnen under korten är på filippinska, laotiska och vietnamesiska, efter var varje del kommer ifrån. Illustrationerna är tecknade med gpt-image efter bilder ur videon.</p>
    </section>
  </div>
</main>

<footer>Bahn fakkin mi · <a href="/planuea/">pla fakkin nuea</a> · <a href="/padnamprikpao/">pad fakkin prik</a> · <a href="/">buttercup.nu</a></footer>

<script>
const G={
 g1:[
  ["rawpork","Sidfläsk med svål","Ett helt stycke","~1,2 kg",true,"liempo"],
  ["sugar","Socker","Till rubben","~1 msk",true,"asukal"],
  ["salt","Kosher salt","Rubben + svålen","~2 msk",true,"asin"],
  ["paprika","Paprika","Till rubben","~1 msk",true,"paprika"],
  ["garlicpowder","Vitlökspulver","Till rubben","~2 tsk",true,"bawang"],
  ["pepper","Svartpeppar","Malen + hela korn","~2 tsk",true,"paminta"],
  ["lemongrass","Citrongräs","Tunt skivat","~2 stjälkar",true,"tanglad"],
  ["springonion","Salladslök","Hela, på längden","~3 st",true,"dahon ng sibuyas"],
  ["bay","Lagerblad","Mitt i rullen","~3 blad",true,"dahon ng laurel"],
  ["cilantro","Koriander","En hel knippe in","1 knippe",true,"wansoy"]
 ],
 g2:[
  ["garlic","Vitlök","Riven","~3 klyftor",true,"ກະທຽມ"],
  ["chiliflakes","Thaichili","Torkad, krossad","~2 tsk",true,"ໝາກເຜັດ"],
  ["rocksugar","Kandisocker","Rock sugar","~1 msk",true,"ນ້ຳຕານກ້ອນ"],
  ["calamansi","Kalamansijuice","I stället för lime","~4 msk",true,"kalamansi"],
  ["fish","Fisksås","Nam pa","~2 msk",true,"ນ້ຳປາ"],
  ["cilantro","Koriander","Hackad, rikligt","1 näve",true,"ຜັກຫອມປ້ອມ"]
 ],
 g3:[
  ["baguette","Baguette","Luftig, tunn skorpa","4 st",true,"bánh mì"],
  ["pate","Leverpastej","Pâté, ena halvan","~1 burk",true,"pa tê"],
  ["mayo","Majonnäs","Gul och smörig","~4 msk",true,"sốt bơ"],
  ["lechon","Lechon","Tjocka skivor","Del 1",false,"heo quay"],
  ["jeow","Jeow som","Ringla över","Del 2",false,"ແຈ່ວສົ້ມ"],
  ["dochua","Đồ chua","Morot + daikon","1 näve",true,"đồ chua"],
  ["cucumber","Gurka","Långa stavar","~½ st",true,"dưa leo"],
  ["cilantro","Koriander","Kvistar","1 näve",true,"ngò rí"]
 ]};
let n=0;
for(const [id,ING] of Object.entries(G)){
 const g=document.getElementById(id);
 ING.forEach(([k,name,sub,amt,est,th])=>{
  const lang=/[\\u0E80-\\u0EFF]/.test(th)?'lo':(id==='g1'||k==='calamansi'?'tl':'vi');
  g.insertAdjacentHTML('beforeend',
   `<li class="card" data-k="${k}">
      <span class="num">${String(++n).padStart(2,'0')}</span>
      <span class="amt${est?' est':''}" title="${est?'Uppskattning, videon anger ingen mängd':''}">${amt}</span>
      <div class="stage">
        <img src="img/${k}.webp" alt="${name}" width="520" height="780" loading="${n<5?'eager':'lazy'}">
      </div>
      <h2>${name}</h2><p>${sub}</p><p class="th" lang="${lang}">${th}</p>
    </li>`);
 });
}
</script>
</body>
</html>
"""
open(os.path.join(D, '..', 'index.html'), 'w').write(head + CSS + BODY)
print('ok')
