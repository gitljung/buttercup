# vendor/libredwg – DWG → DXF i webbläsaren

- `libredwg-web.js` + `libredwg-web.wasm` = mappen `wasm/` ur npm-paketet **@mlightcad/libredwg-web 0.9.0**
  (https://www.npmjs.com/package/@mlightcad/libredwg-web, källkod https://github.com/mlightcad/libredwg-web),
  som är **GNU LibreDWG 0.14.9000** (https://www.gnu.org/software/libredwg/) kompilerat med Emscripten.
- Licens: **GPL-3.0-or-later** (LibreDWG och bindningen). Används internt i granskningsvyn; källkoden finns på länkarna ovan.
  Filerna är oförändrade. Uppdatera: `npm pack @mlightcad/libredwg-web` → kopiera `package/wasm/*` hit.
- Används av `k2/webb/dwg_webb.js` (`dwg_write_dxf`), laddas först när en DWG släpps i sidan.
