from PIL import Image, ImageDraw, ImageFilter
S = 1024

def gradiente(w, h, c1, c2):
    g = Image.new("RGB", (w, h))
    px = g.load()
    for y in range(h):
        for x in range(w):
            t = (x + y) / (w + h)
            px[x, y] = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
    return g

def cartao(cor, caixa, tab_w, r):
    """Aba de navegador: retângulo arredondado com 'orelha' no topo esquerdo."""
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = caixa
    d.rounded_rectangle([x0, y0 + 70, x1, y1], radius=r, fill=cor)
    d.rounded_rectangle([x0, y0, x0 + tab_w, y0 + 150], radius=r, fill=cor)
    return im

base = gradiente(S, S, (14, 165, 233), (99, 102, 241)).convert("RGBA")
mask = Image.new("L", (S, S), 0)
ImageDraw.Draw(mask).rounded_rectangle([0, 0, S - 1, S - 1], radius=230, fill=255)

# brilho suave no topo
brilho = Image.new("RGBA", (S, S), (0, 0, 0, 0))
ImageDraw.Draw(brilho).ellipse([-200, -520, S + 200, 380], fill=(255, 255, 255, 38))
base = Image.alpha_composite(base, brilho)

# cartão de trás (a "cópia" repetida)
tras = cartao((255, 255, 255, 120), (250, 210, 800, 700), 300, 60)
base = Image.alpha_composite(base, tras)

# sombra + cartão da frente
frente = cartao((255, 255, 255, 255), (170, 300, 720, 820), 320, 60)
sombra = Image.new("RGBA", (S, S), (0, 0, 0, 0))
sombra.putalpha(frente.getchannel("A").filter(ImageFilter.GaussianBlur(28)).point(lambda v: int(v * 0.35)))
base = Image.alpha_composite(base, sombra.transform(sombra.size, Image.AFFINE, (1, 0, 0, 0, 1, -18)))
base = Image.alpha_composite(base, frente)

# linhas de "conteúdo" do cartão da frente
d = ImageDraw.Draw(base)
for i, larg in enumerate((420, 300)):
    d.rounded_rectangle([250, 470 + i * 90, 250 + larg, 520 + i * 90], radius=25, fill=(203, 213, 225, 255))

# selo verde com check (duplicata resolvida)
cx, cy, rr = 770, 770, 190
d.ellipse([cx - rr - 26, cy - rr - 26, cx + rr + 26, cy + rr + 26], fill=(255, 255, 255, 255))
d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=(34, 197, 94, 255))
d.line([(cx - 88, cy + 5), (cx - 22, cy + 72), (cx + 96, cy - 70)], fill=(255, 255, 255, 255), width=54, joint="curve")
for px_, py_ in [(cx - 88, cy + 5), (cx + 96, cy - 70)]:
    d.ellipse([px_ - 27, py_ - 27, px_ + 27, py_ + 27], fill=(255, 255, 255, 255))

final = Image.new("RGBA", (S, S), (0, 0, 0, 0))
final.paste(base, (0, 0), mask)
for t in (16, 32, 48, 128):
    final.resize((t, t), Image.LANCZOS).save(f"icons/icon{t}.png")

print("ok")
