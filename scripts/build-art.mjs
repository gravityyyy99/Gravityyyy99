// Generates the animated SVG art used by the profile README (header, terminal intro, skills orbit,
// certificates, journey timeline, footer). Pure SVG + SMIL, so it animates inside GitHub's <img> tags
// with no JavaScript and no third-party service. Run: node scripts/build-art.mjs
import { writeFileSync, mkdirSync } from 'node:fs';

mkdirSync('assets', { recursive: true });
const FONT = "font-family=\"'Segoe UI', Inter, Arial, sans-serif\"";
const MONO = "font-family=\"'Cascadia Code', 'Fira Code', Consolas, 'Courier New', monospace\"";
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
// deterministic pseudo-random so the output is stable between runs
let seed = 7;
const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);

const DEFS = `
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0b1020"/><stop offset="0.55" stop-color="#101a36"/><stop offset="1" stop-color="#1a1038"/></linearGradient>
  <linearGradient id="ink" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#22d3ee"/><stop offset="0.5" stop-color="#a78bfa"/><stop offset="1" stop-color="#f472b6"/></linearGradient>
  <filter id="glow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="3.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>`;

/* ---------------------------------------------------------------- header */
function header() {
  const W = 1000, H = 320;
  const glyphs = ['0', '1', '{', '}', ';', '<', '/>', '=>', '[]', '()', '&&', '||', '++', '#', 'fn', 'if'];
  let rain = '';
  for (let i = 0; i < 34; i++) {
    const x = 14 + i * 29.5;
    const len = 7 + Math.floor(rnd() * 8);
    const dur = (7 + rnd() * 9).toFixed(1);
    const begin = (-rnd() * 14).toFixed(1);
    let spans = '';
    for (let k = 0; k < len; k++) spans += `<tspan x="${x.toFixed(1)}" dy="${k === 0 ? 0 : 20}">${esc(glyphs[Math.floor(rnd() * glyphs.length)])}</tspan>`;
    rain += `<text ${MONO} font-size="15" fill="#22d3ee" opacity="${(0.1 + rnd() * 0.22).toFixed(2)}" y="-220">${spans}<animateTransform attributeName="transform" type="translate" from="0 0" to="0 ${H + 260}" dur="${dur}s" begin="${begin}s" repeatCount="indefinite"/></text>`;
  }
  const taglines = ['Full-stack developer + visual storyteller', 'Shipping features, framing shots', "git commit -m 'code meets cinema'", 'while (alive) { learn(); build(); ship(); }'];
  const tl = taglines.map((t, i) => `<text x="500" y="196" text-anchor="middle" ${MONO} font-size="19" fill="#e2e8f0" opacity="0">${esc(t)}<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;0.05;0.21;0.25;1" dur="12s" begin="${i * 3}s" repeatCount="indefinite"/></text>`).join('');
  const floats = [['</>', 90, 70, '#22d3ee', 0], ['{ }', 905, 80, '#a78bfa', 1.2], ['npm i', 120, 270, '#34d399', 2.1], ['git push', 835, 268, '#f472b6', 0.6], ['async', 52, 170, '#fbbf24', 1.7], ['=>', 950, 175, '#22d3ee', 2.6]]
    .map(([t, x, y, c, d]) => `<g><text x="${x}" y="${y}" ${MONO} font-size="17" font-weight="700" fill="${c}" filter="url(#glow)" text-anchor="middle">${esc(t)}</text><animateTransform attributeName="transform" type="translate" values="0 0;0 -12;0 0" dur="${(4 + d).toFixed(1)}s" begin="${-d}s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.55 1;0.45 0 0.55 1" keyTimes="0;0.5;1"/></g>`).join('');
  const rings = `
    <g transform="translate(500 150)" opacity="0.55">
      <ellipse rx="330" ry="105" fill="none" stroke="url(#ink)" stroke-width="1.2" stroke-dasharray="3 9"><animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="40s" repeatCount="indefinite"/></ellipse>
      <ellipse rx="250" ry="78" fill="none" stroke="#22d3ee" stroke-width="1" stroke-dasharray="2 12"><animateTransform attributeName="transform" type="rotate" from="360" to="0" dur="30s" repeatCount="indefinite"/></ellipse>
    </g>`;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" role="img" aria-label="Dibyajyoti Pradhan, computer science engineer and full-stack developer">
  <defs>${DEFS}<clipPath id="hclip"><rect width="${W}" height="${H}" rx="18"/></clipPath>
    <radialGradient id="halo" cx="0.5" cy="0.45" r="0.5"><stop offset="0" stop-color="#7c3aed" stop-opacity="0.35"/><stop offset="1" stop-color="#7c3aed" stop-opacity="0"/></radialGradient></defs>
  <g clip-path="url(#hclip)">
    <rect width="${W}" height="${H}" fill="url(#bg)"/>
    ${rain}
    <ellipse cx="500" cy="140" rx="430" ry="150" fill="url(#halo)"><animate attributeName="opacity" values="0.6;1;0.6" dur="6s" repeatCount="indefinite"/></ellipse>
    ${rings}
    ${floats}
    <text x="500" y="52" text-anchor="middle" ${MONO} font-size="14" fill="#94a3b8" letter-spacing="3">&lt;hello_world /&gt;</text>
    <text x="500" y="132" text-anchor="middle" ${FONT} font-size="60" font-weight="800" fill="url(#ink)" filter="url(#glow)">Dibyajyoti Pradhan
      <animate attributeName="opacity" values="0;1" dur="1.4s" fill="freeze"/></text>
    <line x1="400" y1="150" x2="600" y2="150" stroke="url(#ink)" stroke-width="3" stroke-linecap="round"><animate attributeName="x1" values="500;400" dur="1.2s" fill="freeze"/><animate attributeName="x2" values="500;600" dur="1.2s" fill="freeze"/></line>
    ${tl}
    <text x="500" y="262" text-anchor="middle" ${MONO} font-size="14" fill="#64748b">// just a silly coder, chasing semicolons</text>
    <text x="500" y="292" text-anchor="middle" ${MONO} font-size="15" fill="#34d399">$ <tspan fill="#e2e8f0">mail pradhandj07@gmail.com</tspan><tspan fill="#e2e8f0">_<animate attributeName="opacity" values="1;1;0;0" dur="1s" repeatCount="indefinite"/></tspan></text>
  </g>
  <rect x="1" y="1" width="${W - 2}" height="${H - 2}" rx="18" fill="none" stroke="#334155"/>
</svg>
`;
}

/* ------------------------------------------------------- terminal intro */
function terminal() {
  const W = 1000;
  const C = { kw: '#c084fc', ty: '#22d3ee', fn: '#60a5fa', st: '#34d399', cm: '#64748b', pl: '#e2e8f0', nu: '#fbbf24', pr: '#f472b6' };
  // each line: [spans], seconds into the loop it starts typing
  const lines = [
    [[['~/dibya', C.st], [' $ ', C.pl], ['whoami', C.fn]]],
    [[['> Dibyajyoti Pradhan', C.pl], [' // aka Dibya, aka gravityyyy99', C.cm]]],
    [[['~/dibya', C.st], [' $ ', C.pl], ['cat about.js', C.fn]]],
    [[['class ', C.kw], ['Dibya ', C.ty], ['extends ', C.kw], ['Engineer ', C.ty], ['{', C.pl]]],
    [[['  stack', C.pr], [' = [', C.pl], ["'React'", C.st], [', ', C.pl], ["'MongoDB'", C.st], [', ', C.pl], ["'SQL'", C.st], [', ', C.pl], ["'Firebase'", C.st], ['];', C.pl]]],
    [[['  bugs', C.pr], [' = [];  ', C.pl], ['// O(n) in the morning, O(n log n) after coffee', C.cm]]],
    [[['  async ', C.kw], ['build', C.fn], ['(idea) {', C.pl]]],
    [[['    while ', C.kw], ['(!idea.shipped) { ', C.pl], ['code', C.fn], ['(); ', C.pl], ['debug', C.fn], ['(); ', C.pl], ['coffee', C.fn], ['(); }  ', C.pl], ['// infinite loop, by design', C.cm]]],
    [[['    return ', C.kw], ['deploy', C.fn], ['(idea);  ', C.pl], ['// works on my machine, and on Render', C.cm]]],
    [[['  }', C.pl]]],
    [[['  get ', C.kw], ['hobbies', C.fn], ['() { ', C.pl], ['return ', C.kw], ["['photography', 'cinematography', 'game QA']", C.st], ['; }', C.pl]]],
    [[['}', C.pl]]],
    [[['~/dibya', C.st], [' $ ', C.pl], ['git status', C.fn]]],
    [[['On branch ', C.pl], ['main', C.st], [': 99 problems, but a segfault ain\'t one', C.cm]]],
    [[['~/dibya', C.st], [' $ ', C.pl], ['./hire --me', C.fn], ['   # 404: sleep not found', C.cm]]],
  ];
  const LH = 24, top = 76;
  const H = top + lines.length * LH + 36;
  const LOOP = 22;
  let clips = '', body = '';
  lines.forEach((spans, i) => {
    const y = top + i * LH;
    const start = 0.8 + i * 1.15;
    const dur = Math.min(1.1, 0.5 + spans.reduce((n, s) => n + s.reduce((m, p) => m + p[0].length, 0), 0) * 0.012);
    const a = (start / LOOP).toFixed(4), b = ((start + dur) / LOOP).toFixed(4);
    clips += `<clipPath id="l${i}"><rect x="30" y="${y - 18}" width="0" height="${LH}"><animate attributeName="width" values="0;0;940;940;0" keyTimes="0;${a};${b};0.97;1" dur="${LOOP}s" repeatCount="indefinite"/></rect></clipPath>`;
    const text = spans[0].map(([t, c]) => `<tspan fill="${c}">${esc(t)}</tspan>`).join('');
    body += `<text x="36" y="${y}" ${MONO} font-size="15" xml:space="preserve" clip-path="url(#l${i})">${text}</text>`;
  });
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" role="img" aria-label="Terminal showing a JavaScript class that describes Dibya">
  <defs>${DEFS}${clips}</defs>
  <rect x="0.5" y="0.5" width="${W - 1}" height="${H - 1}" rx="14" fill="#0d1117" stroke="#30363d"/>
  <path d="M0.5 14.5a14 14 0 0 1 14-14h971a14 14 0 0 1 14 14V40H0.5z" fill="#161b22"/>
  <circle cx="26" cy="22" r="6" fill="#ff5f56"/><circle cx="48" cy="22" r="6" fill="#ffbd2e"/><circle cx="70" cy="22" r="6" fill="#27c93f"/>
  <text x="500" y="27" text-anchor="middle" ${MONO} font-size="13" fill="#8b949e">dibya@portfolio: ~/about.js</text>
  ${body}
  <rect x="36" y="${H - 30}" width="9" height="17" fill="#34d399"><animate attributeName="opacity" values="1;1;0;0" dur="1s" repeatCount="indefinite"/></rect>
</svg>
`;
}

/* --------------------------------------------------------- skills orbit */
function orbit() {
  const W = 1000, H = 460, cx = 500, cy = 230, tilt = -9;
  const rings = [
    { rx: 150, ry: 58, dur: 18, color: '#fbbf24', items: ['JavaScript', 'Java', 'Python', 'TypeScript (learning)'] },
    { rx: 275, ry: 105, dur: 30, color: '#22d3ee', items: ['React', 'HTML', 'CSS', 'Tailwind CSS'] },
    { rx: 410, ry: 160, dur: 44, color: '#a78bfa', items: ['MongoDB', 'SQL', 'Firebase', 'Git', 'GitHub', 'Vercel'] },
  ];
  const rad = (tilt * Math.PI) / 180;
  const rot = (x, y) => [cx + x * Math.cos(rad) - y * Math.sin(rad), cy + x * Math.sin(rad) + y * Math.cos(rad)];
  let svg = '';
  let stars = '';
  for (let i = 0; i < 70; i++) stars += `<circle cx="${(rnd() * W).toFixed(0)}" cy="${(rnd() * H).toFixed(0)}" r="${(0.5 + rnd() * 1.3).toFixed(1)}" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;0.8;0" dur="${(2 + rnd() * 4).toFixed(1)}s" begin="${(-rnd() * 6).toFixed(1)}s" repeatCount="indefinite"/></circle>`;
  for (const r of rings) {
    const [x1, y1] = rot(-r.rx, 0), [x2, y2] = rot(r.rx, 0);
    const path = `M ${x1.toFixed(1)} ${y1.toFixed(1)} A ${r.rx} ${r.ry} ${tilt} 1 0 ${x2.toFixed(1)} ${y2.toFixed(1)} A ${r.rx} ${r.ry} ${tilt} 1 0 ${x1.toFixed(1)} ${y1.toFixed(1)}`;
    svg += `<path d="${path}" fill="none" stroke="${r.color}" stroke-opacity="0.35" stroke-width="1.2" stroke-dasharray="4 7"/>`;
    r.items.forEach((name, i) => {
      const w = name.length * 8.6 + 26;
      const begin = (-(r.dur / r.items.length) * i).toFixed(2);
      svg += `<g><rect x="${(-w / 2).toFixed(1)}" y="-15" width="${w.toFixed(1)}" height="30" rx="15" fill="#0d1117" stroke="${r.color}" stroke-width="1.5" filter="url(#glow)"/>
        <text x="0" y="5" text-anchor="middle" ${FONT} font-size="13" font-weight="700" fill="#f1f5f9">${esc(name)}</text>
        <animateMotion dur="${r.dur}s" begin="${begin}s" repeatCount="indefinite" path="${path}"/></g>`;
    });
  }
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" role="img" aria-label="Animated orbit of technologies: JavaScript, Java, Python, TypeScript, React, HTML, CSS, Tailwind, MongoDB, SQL, Firebase, Git">
  <defs>${DEFS}<radialGradient id="core" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#a78bfa"/><stop offset="1" stop-color="#4c1d95"/></radialGradient>
    <clipPath id="oclip"><rect width="${W}" height="${H}" rx="18"/></clipPath></defs>
  <g clip-path="url(#oclip)">
    <rect width="${W}" height="${H}" fill="url(#bg)"/>
    ${stars}
    <circle cx="${cx}" cy="${cy}" r="62" fill="#7c3aed" opacity="0.25"><animate attributeName="r" values="56;76;56" dur="4s" repeatCount="indefinite"/></circle>
    ${svg}
    <circle cx="${cx}" cy="${cy}" r="44" fill="url(#core)" filter="url(#glow)"/>
    <text x="${cx}" y="${cy - 2}" text-anchor="middle" ${MONO} font-size="20" font-weight="800" fill="#fff">&lt;/&gt;</text>
    <text x="${cx}" y="${cy + 18}" text-anchor="middle" ${FONT} font-size="12" font-weight="700" fill="#e9d5ff" letter-spacing="2">DIBYA</text>
  </g>
  <rect x="1" y="1" width="${W - 2}" height="${H - 2}" rx="18" fill="none" stroke="#334155"/>
</svg>
`;
}

/* --------------------------------------------------------- certificates */
function certs() {
  const items = [
    ['Namaste JavaScript', 'NamasteDev', 'Closures, event loop, async JS', '#fbbf24'],
    ['React and Redux', 'KnowledgeGate', 'Scored 98%  |  Sep 2026', '#22d3ee'],
    ['Prompt Engineering with OpenAI', 'Columbia+', 'Jul 2026', '#a78bfa'],
    ['Machine Learning I', 'Columbia+', 'Jul 2026', '#a78bfa'],
    ['Gen AI Engineering Mastermind', 'Outskill', 'LLMs, prompt design, AI tools', '#34d399'],
    ['Generative AI Mastermind', 'Outskill', 'Applied GenAI workflows', '#34d399'],
    ['Generative AI Fundamentals', 'Databricks', 'Exam  |  Oct 2026', '#f87171'],
    ['AI Skills Passport', 'EY and Microsoft', 'General + employability', '#60a5fa'],
    ['Young Turks 2026', 'Naukri Campus', 'Rank 1224, top 3000 | 99.69 percentile', '#f472b6'],
    ['Introduction to IoT', 'NPTEL, IIT Kharagpur', 'Jul-Oct 2025  |  58%', '#fb923c'],
  ];
  const cols = 2, cw = 480, ch = 92, gap = 16, pad = 20, head = 64;
  const rows = Math.ceil(items.length / cols);
  const W = pad * 2 + cols * cw + (cols - 1) * gap, H = head + rows * (ch + gap) + pad - gap + 6;
  const cards = items.map(([t, who, note, c], i) => {
    const x = pad + (i % cols) * (cw + gap), y = head + Math.floor(i / cols) * (ch + gap);
    const delay = (i * 0.18).toFixed(2);
    return `<g opacity="0">
      <animate attributeName="opacity" values="0;1" dur="0.6s" begin="${delay}s" fill="freeze"/>
      <animateTransform attributeName="transform" type="translate" values="0 18;0 0" dur="0.6s" begin="${delay}s" fill="freeze"/>
      <rect x="${x}" y="${y}" width="${cw}" height="${ch}" rx="14" fill="#111827" stroke="${c}" stroke-opacity="0.55"/>
      <rect x="${x}" y="${y}" width="6" height="${ch}" rx="3" fill="${c}"/>
      <circle cx="${x + 44}" cy="${y + ch / 2}" r="22" fill="${c}" fill-opacity="0.15" stroke="${c}"/>
      <path d="M${x + 34} ${y + ch / 2 + 1} l7 7 l13 -15" fill="none" stroke="${c}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"><animate attributeName="stroke-dasharray" values="0 40;40 0" dur="0.7s" begin="${(i * 0.18 + 0.4).toFixed(2)}s" fill="freeze"/></path>
      <text x="${x + 82}" y="${y + 33}" ${FONT} font-size="17" font-weight="700" fill="#f1f5f9">${esc(t)}</text>
      <text x="${x + 82}" y="${y + 56}" ${FONT} font-size="14" font-weight="600" fill="${c}">${esc(who)}</text>
      <text x="${x + 82}" y="${y + 76}" ${MONO} font-size="12" fill="#94a3b8">${esc(note)}</text>
    </g>`;
  }).join('');
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" role="img" aria-label="Certifications earned">
  <defs>${DEFS}</defs>
  <rect width="${W}" height="${H}" rx="18" fill="url(#bg)"/>
  <text x="${pad + 4}" y="40" ${MONO} font-size="15" fill="#64748b">const certifications = [ <tspan fill="#34d399">// ${items.length} and counting</tspan></text>
  ${cards}
  <rect x="1" y="1" width="${W - 2}" height="${H - 2}" rx="18" fill="none" stroke="#334155"/>
</svg>
`;
}

/* -------------------------------------------------------------- journey */
function journey() {
  const W = 1000, H = 330;
  const nodes = [
    ['11-12', 'Class 11 and 12', 'Prabhujee English School', 'Physics, Chem, Maths, CS', '#fbbf24'],
    ['2023', 'B.Tech CSE', 'Gandhi Engineering College', 'Where the debugging began', '#22d3ee'],
    ['QA', 'Game Beta Tester', 'UGW, FAU-G, Indus', 'Hunting bugs in game builds', '#34d399'],
    ['23-26', 'Media Club President', 'PRATIBIMBA, GEC', 'Led it for 3 years, then passed it on', '#a78bfa'],
    ['2026', 'International Photo Win', 'Won an international event', 'One photo got featured', '#f472b6'],
    ['Oct', 'Naukri Young Turks', 'Rank 1224, top 3000', '99.69 percentile', '#fbbf24'],
    ['Now', 'Final-year student', 'B.Tech CSE, CGPA 8.21', 'Building and learning', '#fb923c'],
  ];
  const x0 = 95, step = 135, y = 130;
  const pts = nodes.map((_, i) => x0 + i * step);
  const els = nodes.map(([tag, t, a, b, c], i) => {
    const x = pts[i];
    const up = i % 2 === 0;
    const ty = up ? y - 36 : y + 52;
    const d = (0.5 + i * 0.9).toFixed(1);
    return `<g opacity="0"><animate attributeName="opacity" values="0;1" dur="0.5s" begin="${d}s" fill="freeze"/>
      <circle cx="${x}" cy="${y}" r="15" fill="#0d1117" stroke="${c}" stroke-width="3" filter="url(#glow)"><animate attributeName="r" values="15;19;15" dur="2.6s" begin="${d}s" repeatCount="indefinite"/></circle>
      <text x="${x}" y="${y + 4}" text-anchor="middle" ${MONO} font-size="10" font-weight="800" fill="${c}">${esc(tag)}</text>
      <line x1="${x}" y1="${y + (up ? -16 : 16)}" x2="${x}" y2="${ty + (up ? 8 : -22)}" stroke="${c}" stroke-opacity="0.5" stroke-dasharray="3 4"/>
      <text x="${x}" y="${ty - (up ? 52 : -2)}" text-anchor="middle" ${FONT} font-size="17" font-weight="700" fill="#f1f5f9">${esc(t)}</text>
      <text x="${x}" y="${ty - (up ? 32 : -22)}" text-anchor="middle" ${FONT} font-size="13" font-weight="600" fill="${c}">${esc(a)}</text>
      <text x="${x}" y="${ty - (up ? 14 : -40)}" text-anchor="middle" ${MONO} font-size="12" fill="#94a3b8">${esc(b)}</text></g>`;
  }).join('');
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" role="img" aria-label="Education and experience timeline">
  <defs>${DEFS}</defs>
  <rect width="${W}" height="${H}" rx="18" fill="url(#bg)"/>
  <line x1="40" y1="${y}" x2="${W - 40}" y2="${y}" stroke="#334155" stroke-width="3" stroke-linecap="round"/>
  <line x1="40" y1="${y}" x2="${W - 40}" y2="${y}" stroke="url(#ink)" stroke-width="3" stroke-linecap="round" stroke-dasharray="${W}" stroke-dashoffset="${W}"><animate attributeName="stroke-dashoffset" values="${W};0" dur="3.6s" fill="freeze"/></line>
  <circle r="5" cy="${y}" fill="#fff" filter="url(#glow)"><animate attributeName="cx" values="40;${W - 40};40" dur="7s" repeatCount="indefinite"/></circle>
  ${els}
  <text x="500" y="${H - 22}" text-anchor="middle" ${MONO} font-size="13" fill="#64748b">git log --oneline --graph  # the story so far</text>
  <rect x="1" y="1" width="${W - 2}" height="${H - 2}" rx="18" fill="none" stroke="#334155"/>
</svg>
`;
}

/* --------------------------------------------------------------- footer */
function footer() {
  const W = 1000, H = 150;
  const wave = (amp, off, dur, color, op) => {
    let d = `M0 ${off}`;
    for (let x = 0; x <= 2000; x += 250) d += ` Q ${x + 125} ${off - amp} ${x + 250} ${off}`;
    d += ` V${H} H0 Z`;
    return `<path d="${d}" fill="${color}" fill-opacity="${op}"><animateTransform attributeName="transform" type="translate" from="0 0" to="-500 0" dur="${dur}s" repeatCount="indefinite"/></path>`;
  };
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" role="img" aria-label="Thanks for visiting">
  <defs>${DEFS}<clipPath id="fclip"><rect width="${W}" height="${H}" rx="18"/></clipPath></defs>
  <g clip-path="url(#fclip)">
    <rect width="${W}" height="${H}" fill="url(#bg)"/>
    ${wave(26, 96, 14, '#22d3ee', 0.25)}${wave(20, 110, 9, '#a78bfa', 0.3)}${wave(14, 124, 6, '#f472b6', 0.35)}
    <text x="500" y="52" text-anchor="middle" ${FONT} font-size="26" font-weight="800" fill="url(#ink)">Thanks for stopping by</text>
    <text x="500" y="78" text-anchor="middle" ${MONO} font-size="14" fill="#cbd5e1">return 0;  // exit code 0: no errors, only features</text>
  </g>
  <rect x="1" y="1" width="${W - 2}" height="${H - 2}" rx="18" fill="none" stroke="#334155"/>
</svg>
`;
}

const files = { header, terminal, orbit, certs, journey, footer };
for (const [name, fn] of Object.entries(files)) {
  writeFileSync(`assets/${name}.svg`, fn());
  console.log('wrote assets/' + name + '.svg');
}
