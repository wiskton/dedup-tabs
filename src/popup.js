import { agruparRepetidos } from "./dedupe.js";

const abas = await chrome.tabs.query({});
const grupos = agruparRepetidos(abas);
const sobrando = grupos.reduce((n, g) => n + g.itens.length - 1, 0);
document.getElementById("resumo").textContent =
  sobrando ? `${sobrando} aba(s) repetida(s) em ${grupos.length} site(s), de ${abas.length} abertas.`
           : `Nenhuma aba repetida entre ${abas.length} abertas.`;

const abrir = (aba) => chrome.tabs.create({ url: chrome.runtime.getURL(`src/panel.html#${aba}`) });
document.getElementById("abas").onclick = () => abrir("abas");
document.getElementById("favs").onclick = () => abrir("favoritos");
