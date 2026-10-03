/* Buttercup STEP-export
   Skriver ISO 10303-21 (AP214, AUTOMOTIVE_DESIGN) med riktiga solider (ADVANCED_BREP):
   plana ytor, raka kanter, slutna skal. Enhet: millimeter. Z uppåt (three.js har Y uppåt).
   Fristående, inget beroende av three.js – tar emot matriser som .elements (kolumnordning). */
(function (global) {
  'use strict';

  function num(v, d) {
    if (!isFinite(v)) v = 0;
    if (Math.abs(v) < Math.pow(10, -d)) v = 0;
    var s = v.toFixed(d);
    if (s.indexOf('.') >= 0) s = s.replace(/0+$/, ''); else s += '.';
    if (s === '-0.') s = '0.';
    return s;
  }
  function ascii(s) {
    return String(s).normalize('NFD').replace(/[\u0300-\u036f]/g, '')
      .replace(/[^\x20-\x7e]/g, '_').replace(/\\/g, '\\\\').replace(/'/g, "''");
  }
  function sub(a, b) { return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]; }
  function dot(a, b) { return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]; }
  function len(a) { return Math.sqrt(dot(a, a)); }
  function nrm(a) { var l = len(a) || 1; return [a[0] / l, a[1] / l, a[2] / l]; }
  function newell(P, f) {
    var n = [0, 0, 0];
    for (var i = 0; i < f.length; i++) {
      var a = P[f[i]], b = P[f[(i + 1) % f.length]];
      n[0] += (a[1] - b[1]) * (a[2] + b[2]);
      n[1] += (a[2] - b[2]) * (a[0] + b[0]);
      n[2] += (a[0] - b[0]) * (a[1] + b[1]);
    }
    return n;
  }
  // three.js-meter (Y upp) -> CAD-millimeter (Z upp). Ren rotation, behåller handedness.
  function xf(e, x, y, z) {
    var X = e[0] * x + e[4] * y + e[8] * z + e[12];
    var Y = e[1] * x + e[5] * y + e[9] * z + e[13];
    var Z = e[2] * x + e[6] * y + e[10] * z + e[14];
    return [X * 1000, -Z * 1000, Y * 1000];
  }
  function det3(e) {
    return e[0] * (e[5] * e[10] - e[9] * e[6]) - e[4] * (e[1] * e[10] - e[9] * e[2]) + e[8] * (e[1] * e[6] - e[5] * e[2]);
  }
  function hex(c) {
    if (Array.isArray(c)) return c;
    c = String(c).replace('#', '');
    return [parseInt(c.substr(0, 2), 16) / 255, parseInt(c.substr(2, 2), 16) / 255, parseInt(c.substr(4, 2), 16) / 255];
  }

  var BOX_FACES = [[0, 4, 6, 2], [1, 3, 7, 5], [0, 1, 5, 4], [2, 6, 7, 3], [0, 2, 3, 1], [4, 5, 7, 6]];

  function Writer(name) {
    this.name = ascii(name || 'Modell');
    this.lines = []; this.n = 0; this.solids = []; this.styled = []; this.styles = {};
    var a = this;
    a.ctxApp = a.add("APPLICATION_CONTEXT('core data for automotive mechanical design processes')");
    a.add("APPLICATION_PROTOCOL_DEFINITION('international standard','automotive_design',2000," + a.ctxApp + ")");
    a.ctxProd = a.add("PRODUCT_CONTEXT(''," + a.ctxApp + ",'mechanical')");
    a.prod = a.add("PRODUCT('" + a.name + "','" + a.name + "','',(" + a.ctxProd + "))");
    a.add("PRODUCT_RELATED_PRODUCT_CATEGORY('part',$,(" + a.prod + "))");
    var pdf = a.add("PRODUCT_DEFINITION_FORMATION('',''," + a.prod + ")");
    var pdc = a.add("PRODUCT_DEFINITION_CONTEXT('part definition'," + a.ctxApp + ",'design')");
    var pd = a.add("PRODUCT_DEFINITION('design',''," + pdf + "," + pdc + ")");
    a.pds = a.add("PRODUCT_DEFINITION_SHAPE(''," + "''," + pd + ")");
    var lu = a.add("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))");
    var au = a.add("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))");
    var su = a.add("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())");
    var unc = a.add("UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.E-03)," + lu + ",'distance_accuracy_value','confusion accuracy')");
    a.ctx = a.add("(GEOMETRIC_REPRESENTATION_CONTEXT(3)GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((" + unc + "))GLOBAL_UNIT_ASSIGNED_CONTEXT((" + lu + "," + au + "," + su + "))REPRESENTATION_CONTEXT('Context #1','3D Context with UNIT and UNCERTAINTY'))");
    var o = a.add("CARTESIAN_POINT('',(0.,0.,0.))");
    a.origin = a.add("AXIS2_PLACEMENT_3D(''," + o + "," + a.add("DIRECTION('',(0.,0.,1.))") + "," + a.add("DIRECTION('',(1.,0.,0.))") + ")");
  }
  Writer.prototype.add = function (s) { this.n++; this.lines.push('#' + this.n + '=' + s + ';'); return '#' + this.n; };
  Writer.prototype.pt = function (p) { return this.add("CARTESIAN_POINT('',(" + num(p[0], 4) + ',' + num(p[1], 4) + ',' + num(p[2], 4) + '))'); };
  Writer.prototype.dir = function (d) { return this.add("DIRECTION('',(" + num(d[0], 10) + ',' + num(d[1], 10) + ',' + num(d[2], 10) + '))'); };
  Writer.prototype.style = function (rgb) {
    rgb = hex(rgb || '#b0b0b0'); var key = rgb.map(function (v) { return v.toFixed(3); }).join(',');
    if (this.styles[key]) return this.styles[key];
    var c = this.add("COLOUR_RGB(''," + num(rgb[0], 4) + ',' + num(rgb[1], 4) + ',' + num(rgb[2], 4) + ')');
    var fc = this.add("FILL_AREA_STYLE_COLOUR(''," + c + ')');
    var fa = this.add("FILL_AREA_STYLE('',(" + fc + '))');
    var sf = this.add('SURFACE_STYLE_FILL_AREA(' + fa + ')');
    var ss = this.add("SURFACE_SIDE_STYLE('',(" + sf + '))');
    var us = this.add('SURFACE_STYLE_USAGE(.BOTH.,' + ss + ')');
    return (this.styles[key] = this.add('PRESENTATION_STYLE_ASSIGNMENT((' + us + '))'));
  };

  // P: punkter i mm (Z upp). F: ytor som indexlistor, moturs sett utifrån.
  Writer.prototype.solid = function (P, F, name, color) {
    var a = this, cp = [], vp = [], edges = {}, faces = [];
    for (var i = 0; i < P.length; i++) { cp.push(null); vp.push(null); }
    function vtx(i) { if (!vp[i]) { cp[i] = a.pt(P[i]); vp[i] = a.add("VERTEX_POINT(''," + cp[i] + ')'); } return vp[i]; }
    for (var f = 0; f < F.length; f++) {
      var L = F[f], nn = newell(P, L);
      if (len(nn) < 1e-9) continue;
      var oes = [];
      for (var k = 0; k < L.length; k++) {
        var s = L[k], t = L[(k + 1) % L.length], key = s < t ? s + '_' + t : t + '_' + s, e = edges[key];
        if (!e) {
          var v1 = vtx(s), v2 = vtx(t);
          var ln = a.add("LINE(''," + cp[s] + ',' + a.add("VECTOR(''," + a.dir(nrm(sub(P[t], P[s]))) + ',1.)') + ')');
          e = edges[key] = { id: a.add("EDGE_CURVE(''," + v1 + ',' + v2 + ',' + ln + ',.T.)'), s: s };
        }
        oes.push(a.add("ORIENTED_EDGE('',*,*," + e.id + ',' + (e.s === s ? '.T.' : '.F.') + ')'));
      }
      var loop = a.add("EDGE_LOOP('',(" + oes.join(',') + '))');
      var bnd = a.add("FACE_OUTER_BOUND(''," + loop + ',.T.)');
      var n = nrm(nn), r = sub(P[L[1]], P[L[0]]), d = dot(r, n);
      r = nrm([r[0] - d * n[0], r[1] - d * n[1], r[2] - d * n[2]]);
      var ax = a.add("AXIS2_PLACEMENT_3D(''," + cp[L[0]] + ',' + a.dir(n) + ',' + a.dir(r) + ')');
      faces.push(a.add("ADVANCED_FACE('',(" + bnd + '),' + a.add("PLANE(''," + ax + ')') + ',.T.)'));
    }
    if (faces.length < 4) return false;
    var shell = a.add("CLOSED_SHELL('',(" + faces.join(',') + '))');
    var sol = a.add("MANIFOLD_SOLID_BREP('" + ascii(name || 'Solid') + "'," + shell + ')');
    a.solids.push(sol);
    a.styled.push(a.add("STYLED_ITEM('color',(" + a.style(color) + '),' + sol + ')'));
    return true;
  };

  // Rätblock: m = matrisens .elements, h = halva sidlängder i lokala koordinater.
  Writer.prototype.box = function (m, hx, hy, hz, name, color) {
    var P = [];
    for (var i = 0; i < 8; i++) P.push(xf(m, i & 1 ? hx : -hx, i & 2 ? hy : -hy, i & 4 ? hz : -hz));
    if (len(sub(P[1], P[0])) < .01 || len(sub(P[2], P[0])) < .01 || len(sub(P[4], P[0])) < .01) return false;
    var c = [0, 0, 0]; P.forEach(function (p) { c[0] += p[0] / 8; c[1] += p[1] / 8; c[2] += p[2] / 8; });
    var F = BOX_FACES.map(function (f) {
      var fc = [0, 0, 0]; f.forEach(function (i) { fc[0] += P[i][0] / 4; fc[1] += P[i][1] / 4; fc[2] += P[i][2] / 4; });
      return dot(newell(P, f), sub(fc, c)) < 0 ? f.slice().reverse() : f;
    });
    return this.solid(P, F, name, color);
  };
  Writer.prototype.unitBox = function (m, name, color) { return this.box(m, .5, .5, .5, name, color); };

  // Slutet triangelnät -> solid med triangelytor. Svetsar ihop dubblettpunkter.
  Writer.prototype.triMesh = function (m, pos, idx, name, color) {
    var map = {}, P = [], remap = [], flip = det3(m) < 0;
    for (var i = 0; i < pos.length / 3; i++) {
      var p = xf(m, pos[3 * i], pos[3 * i + 1], pos[3 * i + 2]);
      var key = p[0].toFixed(3) + ',' + p[1].toFixed(3) + ',' + p[2].toFixed(3);
      if (map[key] === undefined) { map[key] = P.length; P.push(p); }
      remap.push(map[key]);
    }
    var F = [], nt = idx ? idx.length / 3 : pos.length / 9;
    for (var t = 0; t < nt; t++) {
      var a = remap[idx ? idx[3 * t] : 3 * t], b = remap[idx ? idx[3 * t + 1] : 3 * t + 1], c = remap[idx ? idx[3 * t + 2] : 3 * t + 2];
      if (a === b || b === c || a === c) continue;
      if (len(newell(P, [a, b, c])) < 1e-6) continue;
      F.push(flip ? [a, c, b] : [a, b, c]);
    }
    return this.solid(P, F, name, color);
  };

  // three.js-mesh (duck typing). Plan och öppna ytor (nät, glas, film) hoppas över.
  Writer.prototype.threeMesh = function (o, name, color) {
    var g = o.geometry, m = o.matrixWorld.elements, pr = g.parameters || {};
    if (g.type === 'BoxGeometry') return this.box(m, pr.width / 2, pr.height / 2, pr.depth / 2, name, color);
    if (g.type === 'PlaneGeometry' || g.type === 'CircleGeometry' || g.type === 'ShapeGeometry') return false;
    if ((g.type === 'CylinderGeometry' || g.type === 'ConeGeometry') && pr.openEnded) return false;
    var pos = g.attributes.position.array, idx = g.index ? g.index.array : null;
    return this.triMesh(m, pos, idx, name, color);
  };

  Writer.prototype.count = function () { return this.solids.length; };
  Writer.prototype.toString = function (fileName) {
    var a = this, body = a.lines.slice();
    var n = a.n;
    function add(s) { n++; body.push('#' + n + '=' + s + ';'); return '#' + n; }
    var rep = add("ADVANCED_BREP_SHAPE_REPRESENTATION('" + a.name + "',(" + [a.origin].concat(a.solids).join(',') + '),' + a.ctx + ')');
    add('SHAPE_DEFINITION_REPRESENTATION(' + a.pds + ',' + rep + ')');
    if (a.styled.length) add("MECHANICAL_DESIGN_GEOMETRIC_PRESENTATION_REPRESENTATION('',(" + a.styled.join(',') + '),' + a.ctx + ')');
    var ts = new Date().toISOString().slice(0, 19);
    return ['ISO-10303-21;', 'HEADER;',
      "FILE_DESCRIPTION(('" + a.name + " - Buttercup'),'2;1');",
      "FILE_NAME('" + ascii(fileName || a.name + '.step') + "','" + ts + "',('Buttercup'),(''),'Buttercup STEP writer','Buttercup','');",
      "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 1 1 1 1 }'));", 'ENDSEC;', 'DATA;']
      .concat(body, ['ENDSEC;', 'END-ISO-10303-21;']).join('\n') + '\n';
  };

  global.StepExport = { create: function (name) { return new Writer(name); } };
})(typeof window !== 'undefined' ? window : globalThis);
