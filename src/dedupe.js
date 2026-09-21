// Lógica pura de normalização e agrupamento (sem APIs do navegador, testável no Node).
const PARAMS_RASTREIO = /^(utm_|fbclid$|gclid$|mc_eid$|igshid$|ref_src$)/i;

export function normalizarUrl(bruta, { ignorarQuery = false } = {}) {
  let u;
  try { u = new URL(bruta); } catch { return null; }
  if (!/^https?:$/.test(u.protocol)) return null;
  u.hash = "";
  u.hostname = u.hostname.replace(/^www\./i, "").toLowerCase();
  if (ignorarQuery) {
    u.search = "";
  } else {
    const limpos = [...u.searchParams.entries()].filter(([k]) => !PARAMS_RASTREIO.test(k));
    limpos.sort(([a], [b]) => a.localeCompare(b));
    u.search = new URLSearchParams(limpos).toString();
  }
  let caminho = u.pathname.replace(/\/+$/, "");
  return `${u.protocol}//${u.host}${caminho}${u.search}`;
}

// Agrupa itens ({url, ...}) por URL normalizada; devolve só grupos com 2+ itens.
export function agruparRepetidos(itens, opcoes) {
  const mapa = new Map();
  for (const item of itens) {
    const chave = normalizarUrl(item.url, opcoes);
    if (!chave) continue;
    if (!mapa.has(chave)) mapa.set(chave, []);
    mapa.get(chave).push(item);
  }
  return [...mapa.entries()]
    .filter(([, lista]) => lista.length > 1)
    .map(([chave, lista]) => ({ chave, itens: lista }));
}

// Em cada grupo de abas escolhe qual manter: fixada > ativa > a mais antiga (menor id).
export function escolherAbaMantida(abas) {
  return [...abas].sort((a, b) =>
    (b.pinned - a.pinned) || (b.active - a.active) || (a.id - b.id))[0];
}

// Percorre a árvore de favoritos devolvendo cada link com o caminho da pasta.
export function achatarFavoritos(no, caminho = [], saida = []) {
  if (no.url) {
    saida.push({ id: no.id, title: no.title || no.url, url: no.url, pasta: caminho.join(" / ") || "(raiz)", dateAdded: no.dateAdded });
  } else if (no.children) {
    const proximo = no.title ? [...caminho, no.title] : caminho;
    no.children.forEach((f) => achatarFavoritos(f, proximo, saida));
  }
  return saida;
}
