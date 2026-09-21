import { agruparRepetidos, escolherAbaMantida, achatarFavoritos } from "./dedupe.js";

const $ = (id) => document.getElementById(id);
const opcoes = () => ({ ignorarQuery: $("ignorarQuery").checked });
const el = (tag, cls, txt) => { const e = document.createElement(tag); if (cls) e.className = cls; if (txt != null) e.textContent = txt; return e; };

// ---------------------------------------------------------------- navegação
function mostrar(qual) {
  const abas = qual === "abas";
  $("secAbas").classList.toggle("oculto", !abas);
  $("secFavs").classList.toggle("oculto", abas);
  $("tabAbas").classList.toggle("sel", abas);
  $("tabFavs").classList.toggle("sel", !abas);
  history.replaceState(null, "", `#${qual}`);
  (abas ? carregarAbas : carregarFavs)();
}
$("tabAbas").onclick = () => mostrar("abas");
$("tabFavs").onclick = () => mostrar("favoritos");
$("ignorarQuery").onchange = () => mostrar(location.hash === "#favoritos" ? "favoritos" : "abas");
try { $("ignorarQuery").checked = localStorage.getItem("dedup_ignorar_query") === "1"; } catch {}
$("ignorarQuery").addEventListener("change", () => { try { localStorage.setItem("dedup_ignorar_query", $("ignorarQuery").checked ? "1" : "0"); } catch {} });

// ---------------------------------------------------------------- prévia ao passar o mouse
const previa = $("previa");
let tokenPrevia = 0;

async function mostrarPrevia(t, ev) {
  const meu = ++tokenPrevia;
  previa.replaceChildren();
  const cab = el("div", "cab");
  if (t.favIconUrl) { const ic = el("img"); ic.src = t.favIconUrl; ic.onerror = () => ic.remove(); cab.append(ic); }
  cab.append(el("span", null, t.title || t.url));
  const moldura = el("div", "moldura", "Carregando prévia...");
  previa.append(cab, moldura, el("div", "url", t.url));
  previa.classList.remove("oculto");
  posicionarPrevia(ev);

  const guardado = (await chrome.storage.local.get(`thumb:${t.id}`))[`thumb:${t.id}`];
  if (meu !== tokenPrevia) return;
  if (guardado && guardado.url === t.url) {
    const im = el("img", "thumb"); im.src = guardado.img;
    moldura.replaceChildren(im);
  } else {
    moldura.textContent = "Sem prévia ainda — ela é gravada quando você visita a aba. Clique no título para ir até ela.";
  }
}
function posicionarPrevia(ev) {
  const w = previa.offsetWidth || 340, h = previa.offsetHeight || 260;
  let x = ev.clientX + 18, y = ev.clientY + 14;
  if (x + w > innerWidth - 8) x = ev.clientX - w - 18;
  if (y + h > innerHeight - 8) y = Math.max(8, innerHeight - h - 8);
  previa.style.left = `${Math.max(8, x)}px`;
  previa.style.top = `${y}px`;
}
function esconderPrevia() { tokenPrevia++; previa.classList.add("oculto"); }

// ---------------------------------------------------------------- abas
let gruposAbas = [];
const marcadasAbas = new Set(); // ids das abas que serão fechadas

async function carregarAbas() {
  const todas = (await chrome.tabs.query({})).filter((t) => t.id !== undefined);
  gruposAbas = agruparRepetidos(todas, opcoes());
  marcadasAbas.clear();
  for (const g of gruposAbas) {
    const manter = escolherAbaMantida(g.itens);
    g.mantida = manter.id;
    g.itens.forEach((t) => { if (t.id !== manter.id) marcadasAbas.add(t.id); });
  }
  desenharAbas(todas.length);
}

function desenharAbas(total) {
  esconderPrevia();
  const lista = $("listaAbas");
  lista.replaceChildren();
  if (!gruposAbas.length) lista.append(el("div", "vazio", "Nenhuma aba repetida. 🎉"));
  for (const g of gruposAbas) {
    const box = el("div", "grupo");
    box.append(el("h3", null, g.chave));
    for (const t of g.itens) {
      const fechar = marcadasAbas.has(t.id);
      const row = el("label", `item ${fechar ? "fechar" : "manter"}`);
      const cb = el("input"); cb.type = "checkbox"; cb.checked = fechar;
      cb.onchange = () => { cb.checked ? marcadasAbas.add(t.id) : marcadasAbas.delete(t.id); desenharAbas(total); };
      const info = el("div", "info");
      info.append(el("div", "tit", t.title || t.url), el("div", "dim", `Janela ${t.windowId} · posição ${t.index + 1}${t.pinned ? " · fixada" : ""}${t.active ? " · ativa" : ""}`));
      row.append(cb, info, el("span", `tag ${fechar ? "x" : "k"}`, fechar ? "FECHAR" : "MANTER"));
      // Clicar no título foca a aba para conferir antes de fechar.
      info.onclick = (e) => { e.preventDefault(); chrome.tabs.update(t.id, { active: true }); chrome.windows.update(t.windowId, { focused: true }); };
      info.style.cursor = "pointer";
      row.addEventListener("mouseenter", (e) => mostrarPrevia(t, e));
      row.addEventListener("mousemove", posicionarPrevia);
      row.addEventListener("mouseleave", esconderPrevia);
      box.append(row);
    }
    lista.append(box);
  }
  const n = marcadasAbas.size;
  $("resAbas").textContent = `${total} abertas · ${gruposAbas.length} site(s) repetido(s) · ${n} marcada(s) para fechar`;
  $("btnFecharAbas").disabled = !n;
  $("btnFecharAbas").textContent = `Fechar ${n} aba(s) marcada(s)`;
}

$("btnAtualizarAbas").onclick = carregarAbas;
$("btnFecharAbas").onclick = async () => {
  const ids = [...marcadasAbas];
  if (!ids.length) return;
  // Nunca fecha todas as abas de um grupo: garante que a mantida continue viva.
  const seguras = ids.filter((id) => !gruposAbas.some((g) => g.itens.every((t) => marcadasAbas.has(t.id)) && g.itens.some((t) => t.id === id)));
  const bloqueadas = ids.length - seguras.length;
  if (bloqueadas && !confirm(`${bloqueadas} aba(s) ficariam sem nenhuma cópia aberta e serão preservadas. Continuar com as demais?`)) return;
  if (!seguras.length) return carregarAbas();
  await chrome.tabs.remove(seguras);
  carregarAbas();
};

// ---------------------------------------------------------------- favoritos
let gruposFavs = [];
const marcadosFavs = new Set();

async function carregarFavs() {
  const [raiz] = await chrome.bookmarks.getTree();
  const todos = achatarFavoritos(raiz);
  gruposFavs = agruparRepetidos(todos, opcoes());
  gruposFavs.forEach((g) => g.itens.sort((a, b) => (a.dateAdded || 0) - (b.dateAdded || 0)));
  marcadosFavs.clear();
  desenharFavs(todos.length);
}

function desenharFavs(total) {
  const lista = $("listaFavs");
  lista.replaceChildren();
  if (!gruposFavs.length) lista.append(el("div", "vazio", "Nenhum favorito repetido. 🎉"));
  const sobra = gruposFavs.reduce((n, g) => n + g.itens.length - 1, 0);
  for (const g of gruposFavs) {
    const box = el("div", "grupo");
    const h = el("h3", null, g.chave);
    h.append(el("span", "dim", `${g.itens.length} cópias`));
    box.append(h);
    for (const f of g.itens) {
      const marcado = marcadosFavs.has(f.id);
      const row = el("label", `item ${marcado ? "fechar" : ""}`);
      const cb = el("input"); cb.type = "checkbox"; cb.checked = marcado;
      cb.onchange = () => { cb.checked ? marcadosFavs.add(f.id) : marcadosFavs.delete(f.id); desenharFavs(total); };
      const info = el("div", "info");
      const link = el("a", "tit", f.title); link.href = f.url; link.target = "_blank"; link.style.color = "inherit";
      info.append(link, el("div", "pasta", `📁 ${f.pasta}`));
      const del = el("button", null, "Excluir");
      del.onclick = async (e) => { e.preventDefault(); await excluirFavoritos([f.id], false); };
      row.append(cb, info, del);
      box.append(row);
    }
    lista.append(box);
  }
  const n = marcadosFavs.size;
  $("resFavs").textContent = `${total} favoritos · ${gruposFavs.length} site(s) repetido(s) · ${sobra} cópia(s) sobrando · ${n} marcado(s)`;
  $("btnExcluirFavs").disabled = !n;
  $("btnExcluirFavs").textContent = `Excluir ${n} marcado(s)`;
}

$("btnMarcarFavs").onclick = () => {
  marcadosFavs.clear();
  gruposFavs.forEach((g) => g.itens.slice(1).forEach((f) => marcadosFavs.add(f.id)));
  desenharFavs(gruposFavs.reduce((n, g) => n + g.itens.length, 0));
};
$("btnExcluirFavs").onclick = () => excluirFavoritos([...marcadosFavs], true);

async function excluirFavoritos(ids, confirmar) {
  if (!ids.length) return;
  if (confirmar && !confirm(`Excluir ${ids.length} favorito(s)? Isso não pode ser desfeito (exporte um backup antes se quiser).`)) return;
  for (const id of ids) { try { await chrome.bookmarks.remove(id); } catch (e) { console.warn(e); } }
  carregarFavs();
}

$("btnBackup").onclick = async () => {
  const arvore = await chrome.bookmarks.getTree();
  const blob = new Blob([JSON.stringify(arvore, null, 2)], { type: "application/json" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = `favoritos-backup-${new Date().toISOString().slice(0, 10)}.json`;
  a.click();
  URL.revokeObjectURL(a.href);
};

mostrar(location.hash === "#favoritos" ? "favoritos" : "abas");
