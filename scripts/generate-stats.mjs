// Builds assets/stats.svg from the public GitHub API: repo count, stars, followers, contributions in
// the last 12 months, and a language breakdown. A GitHub Action runs this every day, so the card on
// the profile stays current without any third-party image service.
import { mkdirSync, writeFileSync } from 'node:fs';

const USER = process.env.GH_USER || 'gravityyyy99';
const TOKEN = process.env.GITHUB_TOKEN;
const headers = {
  'User-Agent': 'profile-stats-generator',
  Accept: 'application/vnd.github+json',
  ...(TOKEN ? { Authorization: `Bearer ${TOKEN}` } : {}),
};

async function api(url) {
  const res = await fetch(url, { headers });
  if (!res.ok) throw new Error(`${url} -> ${res.status}`);
  return res.json();
}

const user = await api(`https://api.github.com/users/${USER}`);
const repos = (await api(`https://api.github.com/users/${USER}/repos?per_page=100&type=owner`)).filter((r) => !r.fork);
const stars = repos.reduce((sum, r) => sum + r.stargazers_count, 0);

// Language bytes across all public, non-fork repositories.
const bytes = {};
for (const repo of repos) {
  try {
    const langs = await api(repo.languages_url);
    for (const [name, size] of Object.entries(langs)) bytes[name] = (bytes[name] || 0) + size;
  } catch {
    /* skip a repo whose languages can't be read */
  }
}
const totalBytes = Object.values(bytes).reduce((a, b) => a + b, 0) || 1;
const topLangs = Object.entries(bytes)
  .sort((a, b) => b[1] - a[1])
  .slice(0, 6)
  .map(([name, size]) => ({ name, pct: (size / totalBytes) * 100 }));

// Contributions in the last 12 months (needs the GraphQL API; skipped if unavailable).
let contributions = null;
if (TOKEN) {
  try {
    const res = await fetch('https://api.github.com/graphql', {
      method: 'POST',
      headers: { ...headers, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: `query($login:String!){ user(login:$login){ contributionsCollection{ contributionCalendar{ totalContributions } } } }`,
        variables: { login: USER },
      }),
    });
    const json = await res.json();
    contributions = json?.data?.user?.contributionsCollection?.contributionCalendar?.totalContributions ?? null;
  } catch {
    contributions = null;
  }
}

const COLORS = {
  JavaScript: '#f1e05a', TypeScript: '#3178c6', HTML: '#e34c26', CSS: '#a855f7', Python: '#3572a5',
  Java: '#b07219', C: '#9ca3af', 'C++': '#f34b7d', Shell: '#89e051', SCSS: '#c6538c', Dockerfile: '#384d54',
};
const colorOf = (name) => COLORS[name] || '#8b949e';
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

const tiles = [
  { label: 'Public repos', value: repos.length },
  { label: 'Stars earned', value: stars },
  { label: 'Followers', value: user.followers },
  { label: 'Contributions (12 mo)', value: contributions ?? '-' },
];

const W = 900;
const H = 290;
const tileW = 196;
const gap = 12;
const startX = 36;

const tileSvg = tiles
  .map((t, i) => {
    const x = startX + i * (tileW + gap);
    return `
    <g transform="translate(${x},78)">
      <rect width="${tileW}" height="86" rx="12" fill="#161b22" stroke="#30363d"/>
      <text x="${tileW / 2}" y="44" text-anchor="middle" font-size="34" font-weight="800" fill="url(#num)">${esc(t.value)}</text>
      <text x="${tileW / 2}" y="68" text-anchor="middle" font-size="13" fill="#8b949e">${esc(t.label)}</text>
    </g>`;
  })
  .join('');

// Stacked language bar.
const barX = 36;
const barW = W - 72;
let cursor = barX;
const barSvg = topLangs
  .map((l, i) => {
    const w = i === topLangs.length - 1 ? barX + barW - cursor : (l.pct / topLangs.reduce((s, x) => s + x.pct, 0)) * barW;
    const rect = `<rect x="${cursor.toFixed(1)}" y="196" width="${w.toFixed(1)}" height="14" fill="${colorOf(l.name)}"/>`;
    cursor += w;
    return rect;
  })
  .join('');

const legendSvg = topLangs
  .map((l, i) => {
    const col = i % 3;
    const row = Math.floor(i / 3);
    const x = 36 + col * 280;
    const y = 238 + row * 24;
    return `
    <circle cx="${x + 5}" cy="${y - 4}" r="5" fill="${colorOf(l.name)}"/>
    <text x="${x + 18}" y="${y}" font-size="14" fill="#e6edf3">${esc(l.name)} <tspan fill="#8b949e">${l.pct.toFixed(1)}%</tspan></text>`;
  })
  .join('');

const updated = new Date().toISOString().slice(0, 10);

const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" role="img" aria-label="GitHub statistics for ${esc(USER)}">
  <defs>
    <linearGradient id="card" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#0d1117"/>
      <stop offset="1" stop-color="#111a2e"/>
    </linearGradient>
    <linearGradient id="num" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#7dd3fc"/>
      <stop offset="1" stop-color="#c4b5fd"/>
    </linearGradient>
    <clipPath id="barclip"><rect x="${barX}" y="196" width="${barW}" height="14" rx="7"/></clipPath>
  </defs>
  <g font-family="'Segoe UI', Inter, Arial, sans-serif">
    <rect width="${W}" height="${H}" rx="16" fill="url(#card)" stroke="#30363d"/>
    <text x="36" y="44" font-size="20" font-weight="700" fill="#e6edf3">GitHub at a glance</text>
    <text x="${W - 36}" y="44" text-anchor="end" font-size="12" fill="#6e7681">${esc(USER)} | updated ${updated}</text>
    <rect x="36" y="56" width="120" height="3" rx="1.5" fill="url(#num)"/>
    ${tileSvg}
    <text x="36" y="188" font-size="13" font-weight="600" fill="#8b949e">Most used languages</text>
    <g clip-path="url(#barclip)">${barSvg}</g>
    ${legendSvg}
  </g>
</svg>
`;

mkdirSync('assets', { recursive: true });
writeFileSync('assets/stats.svg', svg);
console.log(`stats.svg written: ${repos.length} repos, ${stars} stars, ${user.followers} followers, contributions=${contributions}`);
console.log('languages:', topLangs.map((l) => `${l.name} ${l.pct.toFixed(1)}%`).join(', '));
