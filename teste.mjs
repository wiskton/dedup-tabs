import assert from "node:assert/strict";
import { normalizarUrl as n, agruparRepetidos, escolherAbaMantida, achatarFavoritos } from "./src/dedupe.js";

assert.equal(n("https://www.Example.com/a/?utm_source=x&b=2&a=1#topo"), "https://example.com/a?a=1&b=2");
assert.equal(n("https://example.com/a/?x=1", { ignorarQuery: true }), "https://example.com/a");
assert.equal(n("chrome://settings"), null);
assert.equal(n("nao é url"), null);

const g = agruparRepetidos([
  { url: "https://a.com/x/" }, { url: "https://www.a.com/x#h" }, { url: "https://b.com" }, { url: "about:blank" },
]);
assert.equal(g.length, 1);
assert.equal(g[0].itens.length, 2);

const abas = [{ id: 5, pinned: false, active: false }, { id: 3, pinned: false, active: false }, { id: 9, pinned: false, active: true }];
assert.equal(escolherAbaMantida(abas).id, 9);
assert.equal(escolherAbaMantida([...abas.slice(0, 2)]).id, 3);
assert.equal(escolherAbaMantida([...abas, { id: 20, pinned: true, active: false }]).id, 20);

const arvore = { title: "", children: [{ title: "Barra", children: [{ id: "1", title: "A", url: "https://a.com" }, { title: "Dev", children: [{ id: "2", title: "A2", url: "https://a.com/" }] }] }] };
const flat = achatarFavoritos(arvore);
assert.deepEqual(flat.map((f) => f.pasta), ["Barra", "Barra / Dev"]);
console.log("todos os testes passaram");
