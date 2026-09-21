// Guarda uma miniatura de cada aba quando ela fica visível. O Chrome só permite capturar
// a aba ativa de uma janela, então a prévia mostrada no painel é a última vez que a aba foi vista.
const LARGURA = 560;

const chave = (tabId) => `thumb:${tabId}`;

async function reduzir(dataUrl) {
  const blob = await (await fetch(dataUrl)).blob();
  const img = await createImageBitmap(blob);
  const esc = Math.min(1, LARGURA / img.width);
  const c = new OffscreenCanvas(Math.round(img.width * esc), Math.round(img.height * esc));
  c.getContext("2d").drawImage(img, 0, 0, c.width, c.height);
  const saida = await c.convertToBlob({ type: "image/jpeg", quality: 0.6 });
  const bytes = new Uint8Array(await saida.arrayBuffer());
  let bin = "";
  for (let i = 0; i < bytes.length; i += 0x8000) bin += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
  return `data:image/jpeg;base64,${btoa(bin)}`;
}

async function capturar(tabId) {
  try {
    const aba = await chrome.tabs.get(tabId);
    if (!aba.active || !/^https?:/.test(aba.url || "")) return;
    const bruto = await chrome.tabs.captureVisibleTab(aba.windowId, { format: "jpeg", quality: 60 });
    const img = await reduzir(bruto);
    await chrome.storage.local.set({ [chave(tabId)]: { img, url: aba.url, em: Date.now() } });
  } catch {
    // aba fechou, janela minimizada ou página protegida: sem miniatura
  }
}

// Espera a página desenhar antes de capturar.
const agendar = (tabId, ms = 700) => setTimeout(() => capturar(tabId), ms);

chrome.tabs.onActivated.addListener(({ tabId }) => agendar(tabId));
chrome.tabs.onUpdated.addListener((tabId, info, aba) => {
  if (info.status === "complete" && aba.active) agendar(tabId, 1200);
});
chrome.tabs.onRemoved.addListener((tabId) => chrome.storage.local.remove(chave(tabId)));

async function capturarAtivas() {
  const ativas = await chrome.tabs.query({ active: true });
  ativas.forEach((t) => agendar(t.id, 300));
}
chrome.runtime.onInstalled.addListener(capturarAtivas);
chrome.runtime.onStartup.addListener(async () => {
  // Ids de abas mudam entre sessões: descarta miniaturas antigas.
  const tudo = await chrome.storage.local.get(null);
  await chrome.storage.local.remove(Object.keys(tudo).filter((k) => k.startsWith("thumb:")));
  capturarAtivas();
});

// Permite que o painel da extensão carregue qualquer site em um iframe (miniatura ao vivo):
// remove X-Frame-Options e o frame-ancestors do CSP, só nas requisições feitas pela própria extensão.
async function liberarIframesDaExtensao() {
  await chrome.declarativeNetRequest.updateDynamicRules({
    removeRuleIds: [1],
    addRules: [{
      id: 1,
      priority: 1,
      action: {
        type: "modifyHeaders",
        responseHeaders: [
          { header: "x-frame-options", operation: "remove" },
          { header: "content-security-policy", operation: "remove" },
          { header: "content-security-policy-report-only", operation: "remove" },
        ],
      },
      condition: { resourceTypes: ["sub_frame"], initiatorDomains: [chrome.runtime.id] },
    }],
  });
}
chrome.runtime.onInstalled.addListener(liberarIframesDaExtensao);
chrome.runtime.onStartup.addListener(liberarIframesDaExtensao);
