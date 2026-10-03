/* Tiny dependency-free SVG charts (no CDN, no internet needed). */
(function () {
  const COLORS = ['#ea580c', '#991b1b', '#78350f', '#f59e0b', '#16a34a', '#c2410c', '#a16207', '#dc2626', '#92400e', '#fb923c'];
  const NS = 'http://www.w3.org/2000/svg';

  function svg(tag, attrs, parent) {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }
  function text(parent, x, y, str, attrs) {
    const t = svg('text', Object.assign({ x, y, 'font-size': 11, style: 'fill:var(--muted)' }, attrs || {}), parent);
    t.textContent = str;
    return t;
  }
  function fmt(n, o) {
    const p = (o && o.prefix) || '';
    return p + Number(n).toLocaleString('en-IN', { maximumFractionDigits: 0 });
  }
  function empty(box, msg) {
    box.innerHTML = '<div class="chart-empty">' + (msg || 'No data yet') + '</div>';
  }
  function niceMax(v) {
    if (v <= 0) return 10;
    const pow = Math.pow(10, Math.floor(Math.log10(v)));
    const n = v / pow;
    return (n <= 1 ? 1 : n <= 2 ? 2 : n <= 5 ? 5 : 10) * pow;
  }

  function line(id, labels, values, opts) {
    const box = document.getElementById(id);
    if (!box) return;
    if (!values.length) return empty(box);
    box.innerHTML = '';
    const W = 600, H = 260, L = 54, R = 16, T = 16, B = 34;
    const s = svg('svg', { viewBox: `0 0 ${W} ${H}`, width: '100%', preserveAspectRatio: 'xMidYMid meet' }, box);
    const defs = svg('defs', {}, s);
    const g = svg('linearGradient', { id: id + '-g', x1: 0, y1: 0, x2: 0, y2: 1 }, defs);
    svg('stop', { offset: '0%', 'stop-color': COLORS[0], 'stop-opacity': 0.35 }, g);
    svg('stop', { offset: '100%', 'stop-color': COLORS[0], 'stop-opacity': 0 }, g);
    const max = niceMax(Math.max.apply(null, values));
    const iw = W - L - R, ih = H - T - B;
    const X = i => L + (values.length === 1 ? iw / 2 : (i * iw) / (values.length - 1));
    const Y = v => T + ih - (v / max) * ih;
    for (let i = 0; i <= 4; i++) {
      const y = T + (ih * i) / 4;
      svg('line', { x1: L, x2: W - R, y1: y, y2: y, style: 'stroke:var(--border)', 'stroke-dasharray': '4 4' }, s);
      text(s, L - 8, y + 4, fmt(max - (max * i) / 4, opts), { 'text-anchor': 'end' });
    }
    labels.forEach((l, i) => text(s, X(i), H - 10, l, { 'text-anchor': 'middle' }));
    let d = values.map((v, i) => (i ? 'L' : 'M') + X(i) + ' ' + Y(v)).join(' ');
    svg('path', { d: d + ` L${X(values.length - 1)} ${T + ih} L${X(0)} ${T + ih} Z`, fill: `url(#${id}-g)` }, s);
    svg('path', { d, fill: 'none', stroke: COLORS[0], 'stroke-width': 3, 'stroke-linejoin': 'round', 'stroke-linecap': 'round' }, s);
    values.forEach((v, i) => {
      const c = svg('circle', { cx: X(i), cy: Y(v), r: 4.5, fill: '#fff', stroke: COLORS[0], 'stroke-width': 2.5 }, s);
      svg('title', {}, c).textContent = labels[i] + ': ' + fmt(v, opts);
    });
  }

  function hbar(id, labels, values, opts) {
    const box = document.getElementById(id);
    if (!box) return;
    if (!values.length) return empty(box);
    box.innerHTML = '';
    const rowH = 38, W = 600, L = 150, R = 60, H = labels.length * rowH + 10;
    const s = svg('svg', { viewBox: `0 0 ${W} ${H}`, width: '100%' }, box);
    const max = Math.max.apply(null, values) || 1;
    labels.forEach((l, i) => {
      const y = i * rowH + 6;
      const w = Math.max(4, ((W - L - R) * values[i]) / max);
      text(s, L - 10, y + 18, l.length > 20 ? l.slice(0, 19) + '…' : l, { 'text-anchor': 'end', 'font-size': 12, style: 'fill:var(--text)' });
      svg('rect', { x: L, y: y + 4, width: W - L - R, height: 20, rx: 10, style: 'fill:var(--border)', opacity: 0.5 }, s);
      const r = svg('rect', { x: L, y: y + 4, width: w, height: 20, rx: 10, fill: COLORS[i % COLORS.length] }, s);
      svg('title', {}, r).textContent = l + ': ' + fmt(values[i], opts);
      text(s, L + w + 8, y + 19, fmt(values[i], opts), { 'font-size': 12, 'font-weight': 600, style: 'fill:var(--text)' });
    });
  }

  function donut(id, labels, values, opts) {
    const box = document.getElementById(id);
    if (!box) return;
    const total = values.reduce((a, b) => a + b, 0);
    if (!total) return empty(box);
    box.innerHTML = '<div class="donut-wrap"><div class="donut-svg"></div><ul class="legend"></ul></div>';
    const holder = box.querySelector('.donut-svg'), legend = box.querySelector('.legend');
    const s = svg('svg', { viewBox: '0 0 200 200', width: '100%' }, holder);
    const r = 70, C = 2 * Math.PI * r;
    let offset = 0;
    values.forEach((v, i) => {
      const len = (v / total) * C;
      const c = svg('circle', {
        cx: 100, cy: 100, r, fill: 'none', stroke: COLORS[i % COLORS.length], 'stroke-width': 28,
        'stroke-dasharray': `${len} ${C - len}`, 'stroke-dashoffset': -offset, transform: 'rotate(-90 100 100)'
      }, s);
      svg('title', {}, c).textContent = labels[i] + ': ' + fmt(v, opts) + ' (' + Math.round((v / total) * 100) + '%)';
      offset += len;
      const li = document.createElement('li');
      li.innerHTML = `<span class="dot" style="background:${COLORS[i % COLORS.length]}"></span>${labels[i]}<b>${fmt(v, opts)}</b>`;
      legend.appendChild(li);
    });
    text(s, 100, 98, fmt(total, opts), { 'text-anchor': 'middle', 'font-size': 20, 'font-weight': 700, style: 'fill:var(--text)' });
    text(s, 100, 116, (opts && opts.center) || 'Total', { 'text-anchor': 'middle', 'font-size': 10 });
  }

  window.Charts = { line, hbar, donut };
})();
