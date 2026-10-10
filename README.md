# Buttercup

Live: https://www.buttercup.nu (även buttercup-omega.vercel.app). Startsidan är Hugos "Plan B(lommeröd)"-sida från Claude desktop, med avsnittet **Pågående projekt** (`#projekt`) inlagt. Varje projekt har en `thumb.jpg` (800×600, chili på cream) och en röd tillbaka-list (`.bc-bar`).

Samlingsrepo för allt vi bygger. Statiska sidor, ingen build. Varje projekt ligger i en egen mapp med en `index.html`.

| Projekt | Mapp | Beskrivning |
|---|---|---|
| BAGL Box i 3D | [`bagl/`](bagl/) | Cateringlåda 6/12/24 bagels. **Olänkad** – nås bara via buttercup.nu/bagl (/baglbox redirectar) |
| Garibaldi-stallet i 3D | [`garibaldi/`](garibaldi/) | Stallet på Blommeröd: plan ur Wolfe-ritningen 1:100, exteriör + interiör, kvällsljus, GLB. **Olänkad**, noindex. Spec i `garibaldi/SPEC.md` |
| The Fire Pit (eldstaden) | [`garibaldi/eldstad/`](garibaldi/eldstad/) | Spisväggen som scenfond: vägg/golv/luckor/rökplåt/skorsten, spett + vildsvin, ved eller verktygsvägg, versioner, .md-export för Fusion. Kort på startsidan + knapp från stallet, noindex. Källa `~/code/garibaldi/eldstad/eldstad_3d.html` → `make_buttercup.py` |
| Shtickercat profil | [`stickercat/`](stickercat/) | StickerApp-maskotens grafiska profil, alla katter (PNG/SVG) och ChatGPT-promptar. **Olänkad**, noindex |
| Bågväxthus 4 × 10 m | [`vaxthus/`](vaxthus/) | Bågväxthus med byggsteg, gavelsektion och inköpslista |
| Hönshus i 3D | [`honshus/`](honshus/) | Parametrisk three.js-modell av ett hönshus med kompostgrop |
| Yamay utekök | [`utekok/`](utekok/) | Parametrisk köksö: bockad cortenstomme, ek TP1 i liv med 6 mm rostfri topp, rostfria luckor, wok i mitten, kapplista. Källa: ~/code/yamay_utekok (`make_buttercup.py`) |
| Foderautomat | [`foderautomat/`](foderautomat/) | Blommeröd foderautomat 200 L med skruvmatning (Hugos Claude-export), dosering + inköpslista. Källa: ~/code/foderautomat (`make_buttercup.py`) |
| Yamay Tizón, vedspis | [`tizon/`](tizon/) | Kort på startsidan. Sprängskiss ur Fusion (mesh.json från ~/code/yamay_tizon), varmvalsad gunmetal |

## Lägga till ett projekt
1. Skapa en ny mapp, t.ex. `mitt-projekt/`, med en `index.html`.
2. Lägg till ett `<li><a class="proj">`-kort under `#projekt` i rotens `index.html`, en `thumb.jpg` och en rad i tabellen ovan.

## Publicering
Repot är tänkt att kopplas till Vercel. Roten blir startsidan och varje mapp blir en egen sökväg, t.ex. `/honshus/`.
