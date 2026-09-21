# Dedup Tabs & Favoritos

Extensão (Manifest V3, Chrome / Edge / Brave / Chromium) que:

1. **Fecha abas repetidas** — antes de fechar mostra uma prévia com as abas marcadas em vermelho (FECHAR) e a que fica em verde (MANTER). Você pode desmarcar qualquer uma; clicar no título foca a aba para conferir.
2. **Analisa os favoritos** — lista todos os sites repetidos, quantas cópias existem e em qual **pasta** cada uma está, com exclusão individual ou em lote e backup em JSON.

## Instalar (modo desenvolvedor)

1. Abra `chrome://extensions` e ative **Modo do desenvolvedor**.
2. **Carregar sem compactação** → escolha esta pasta (`dedup-tabs`).
3. Fixe o ícone na barra, clique nele e abra o painel.

## Como decide o que é "repetido"

URLs são normalizadas antes de comparar: ignora `#âncora`, `www.`, barra final e parâmetros de rastreio (`utm_*`, `fbclid`, `gclid`…), e ordena os parâmetros restantes. A opção **Ignorar parâmetros da URL** compara só host + caminho. Só `http(s)` é considerado (abas `chrome://` e afins são ignoradas).

Aba mantida em cada grupo: **fixada > ativa > a mais antiga**. A extensão nunca fecha todas as cópias de um mesmo site.

Favoritos: a marcação automática mantém o **mais antigo** de cada grupo.

## Permissões

`tabs` (ler/fechar abas), `bookmarks` (ler/excluir favoritos), `storage`. Nada sai do navegador.

## Testes

```bash
node teste.mjs
```

## Estrutura

- `src/dedupe.js` — normalização e agrupamento (puro, testável)
- `src/popup.*` — resumo rápido
- `src/panel.*` — painel de abas e favoritos
