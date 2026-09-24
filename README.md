# No Duplicate Tab

Extensão (Manifest V3, Chrome / Edge / Brave / Chromium) que:

1. **Fecha abas repetidas** — antes de fechar mostra uma prévia com as abas marcadas em vermelho (FECHAR) e a que fica em verde (MANTER). Você pode desmarcar qualquer uma; clicar no título foca a aba para conferir. **Passar o mouse sobre uma aba abre uma prévia** com miniatura da página, título e URL.
2. **Analisa os favoritos** — lista todos os sites repetidos, quantas cópias existem e em qual **pasta** cada uma está, com exclusão individual ou em lote e backup em JSON.

## Instalar (modo desenvolvedor)

1. Abra `chrome://extensions` e ative **Modo do desenvolvedor**.
2. **Carregar sem compactação** → escolha esta pasta (`dedup-tabs`).
3. Fixe o ícone na barra, clique nele e abra o painel.

## Como decide o que é "repetido"

URLs são normalizadas antes de comparar: ignora `#âncora`, `www.`, barra final e parâmetros de rastreio (`utm_*`, `fbclid`, `gclid`…), e ordena os parâmetros restantes. A opção **Ignorar parâmetros da URL** compara só host + caminho. Só `http(s)` é considerado (abas `chrome://` e afins são ignoradas).

Aba mantida em cada grupo: **fixada > ativa > a mais antiga**. A extensão nunca fecha todas as cópias de um mesmo site.

Favoritos: você escolhe no painel se a marcação automática mantém o **favorito mais antigo** ou o **mais novo** de cada grupo (a escolha fica salva). Trocar a opção com duplicados já marcados reaplica a regra; dá para ajustar item a item antes de excluir.

## Prévia ao passar o mouse

O Chrome só deixa capturar a imagem da aba **visível**. Por isso um serviço em segundo plano (`src/background.js`) grava uma miniatura reduzida de cada aba quando você a visita, e o painel mostra a última gravada. Abas que você ainda não visitou depois de instalar a extensão aparecem sem imagem (só título e URL) até serem visitadas. As miniaturas ficam só no `chrome.storage.local` do navegador e são apagadas quando a aba fecha.

Se a aba ainda não tem foto gravada, a prévia **carrega o próprio site como miniatura** (um iframe reduzido, sem cliques, popups nem navegação). Para isso a extensão remove `X-Frame-Options` e o `frame-ancestors` do CSP **somente nos iframes abertos pela própria extensão** (regra `declarativeNetRequest` limitada ao domínio da extensão). Como o site realmente carrega, isso conta como uma visita (cookies, contadores, vídeos que tocam sozinho); o som do iframe é bloqueado pelo navegador enquanto o painel não é interagido.

## Permissões

`tabs` (ler/fechar abas), `bookmarks` (ler/excluir favoritos), `storage` e `unlimitedStorage` (miniaturas), `declarativeNetRequest` (liberar o iframe da prévia) e `<all_urls>` (necessária para o Chrome permitir a captura de tela das abas). Nada sai do navegador.

## Testes

```bash
node teste.mjs
```

## Estrutura

- `src/dedupe.js` — normalização e agrupamento (puro, testável)
- `icons/` — ícones (regenere com `python icons/gerar_icones.py`, requer Pillow)
- `src/background.js` — grava as miniaturas das abas
- `src/popup.*` — resumo rápido
- `src/panel.*` — painel de abas e favoritos
