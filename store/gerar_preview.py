# -*- coding: utf-8 -*-
"""Gera as imagens de divulgação (preview) da extensão para a Chrome Web Store
e a Firefox Add-ons (AMO), em vários idiomas. Reproduz a UI real do painel com
dados de exemplo e textos traduzidos.

Idiomas: pt, en, es, ru, ja, zh, hi, ko
Saídas: store/<lang>/screenshot-1-tabs.png, screenshot-2-bookmarks.png,
        marquee-1400x560.png, promo-440x280.png

Requer Pillow + fontes do Windows (Segoe UI, Yu Gothic, Microsoft YaHei,
Malgun Gothic, Nirmala UI). Rode da raiz do projeto: python store/gerar_preview.py
"""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
ICONE = os.path.join(RAIZ, "icons", "icon128.png")

# ── Paleta (mesma do src/style.css, tema claro) ──
CARD = (255, 255, 255); LINHA = (213, 220, 236); TXT = (24, 32, 51); DIM = (91, 103, 133)
OK = (21, 128, 61); PERIGO = (220, 38, 38); ACC = (2, 132, 199)
OK_BG = (223, 246, 230); PERIGO_BG = (250, 226, 226)
GRAD1 = (14, 165, 233); GRAD2 = (99, 102, 241)

FONTS = "C:/Windows/Fonts/"
# Cada idioma: (regular, semibold, bold)
FAMILIA = {
    "latin": (FONTS + "segoeui.ttf", FONTS + "seguisb.ttf", FONTS + "segoeuib.ttf"),
    "ja":    (FONTS + "YuGothR.ttc", FONTS + "YuGothM.ttc", FONTS + "YuGothB.ttc"),
    "zh":    (FONTS + "msyh.ttc",    FONTS + "msyh.ttc",    FONTS + "msyhbd.ttc"),
    "ko":    (FONTS + "malgun.ttf",  FONTS + "malgun.ttf",  FONTS + "malgunbd.ttf"),
    "hi":    (FONTS + "Nirmala.ttc", FONTS + "Nirmala.ttc", FONTS + "Nirmala.ttc"),
}

_cache_fonte = {}
def _f(path, tam):
    k = (path, tam)
    if k not in _cache_fonte:
        _cache_fonte[k] = ImageFont.truetype(path, tam)
    return _cache_fonte[k]

_cache_grad = {}
def gradiente(w, h):
    if (w, h) in _cache_grad:
        return _cache_grad[(w, h)].copy()
    base = Image.new("RGB", (w, h), GRAD1)
    top = Image.new("RGB", (w, h), GRAD2)
    mask = Image.new("L", (w, h))
    md = mask.load()
    for y in range(h):
        for x in range(w):
            md[x, y] = int(255 * (x + y) / (w + h))
    base.paste(top, (0, 0), mask)
    _cache_grad[(w, h)] = base
    return base.copy()


def rrect(d, box, r, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def sombra_card(img, box, r, blur=30, alpha=70, dy=16):
    x0, y0, x1, y1 = box
    camada = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(camada).rounded_rectangle([x0, y0 + dy, x1, y1 + dy], radius=r, fill=(15, 23, 42, alpha))
    img.alpha_composite(camada.filter(ImageFilter.GaussianBlur(blur)))


def txt(d, xy, s, fnt, fill, anchor="la"):
    d.text(xy, s, font=fnt, fill=fill, anchor=anchor)


def janela_app(w, h, L, fam, aba_sel, grupos, botao_txt):
    reg, sb, bd = fam
    im = Image.new("RGBA", (w, h), CARD + (255,))
    d = ImageDraw.Draw(im)
    pad = 34

    ic = Image.open(ICONE).convert("RGBA").resize((40, 40), Image.LANCZOS)
    im.alpha_composite(ic, (pad, pad - 4))
    txt(d, (pad + 54, pad + 18), "No Duplicate Tab", _f(bd, 30), TXT, anchor="lm")

    ny = pad + 56
    nx = pad
    for nome, sel in [(L["nav_tabs"], aba_sel == "tabs"), (L["nav_favs"], aba_sel == "favs")]:
        tw = int(d.textlength(nome, font=_f(sb, 20))) + 34
        rrect(d, [nx, ny, nx + tw, ny + 40], 9, fill=(ACC if sel else CARD),
              outline=LINHA, width=0 if sel else 2)
        txt(d, (nx + tw / 2, ny + 20), nome, _f(sb, 20), (255, 255, 255) if sel else TXT, anchor="mm")
        nx += tw + 10
    txt(d, (w - pad, ny + 20), L["ignore"], _f(reg, 17), DIM, anchor="rm")
    d.line([(pad, ny + 62), (w - pad, ny + 62)], fill=LINHA, width=2)

    y = ny + 92
    for g in grupos:
        gh = 46 + len(g["itens"]) * 62
        rrect(d, [pad, y, w - pad, y + gh], 12, fill=CARD, outline=LINHA, width=2)
        txt(d, (pad + 16, y + 23), g["titulo"], _f(sb, 19), TXT, anchor="lm")
        txt(d, (w - pad - 16, y + 23), g.get("dir", ""), _f(reg, 17), DIM, anchor="rm")
        d.line([(pad, y + 46), (w - pad, y + 46)], fill=LINHA, width=2)
        iy = y + 46
        for it in g["itens"]:
            manter = it["manter"]
            d.rectangle([pad + 2, iy + 1, w - pad - 2, iy + 61], fill=(OK_BG if manter else PERIGO_BG))
            cbx = pad + 18
            rrect(d, [cbx, iy + 22, cbx + 20, iy + 42], 4, outline=DIM, width=2, fill=CARD)
            if not manter:
                d.line([(cbx + 4, iy + 32), (cbx + 9, iy + 38), (cbx + 16, iy + 26)], fill=PERIGO, width=3, joint="curve")
            txt(d, (cbx + 34, iy + 18), it["tit"], _f(sb, 18), TXT, anchor="lm")
            txt(d, (cbx + 34, iy + 42), it["url"], _f(reg, 15), ACC if it.get("pasta") else DIM, anchor="lm")
            tag = L["keep"] if manter else L["close"]
            tcor, tbg = (OK, OK_BG) if manter else (PERIGO, PERIGO_BG)
            tw = int(d.textlength(tag, font=_f(bd, 15))) + 24
            rrect(d, [w - pad - 16 - tw, iy + 18, w - pad - 16, iy + 44], 12, fill=tbg)
            txt(d, (w - pad - 16 - tw / 2, iy + 31), tag, _f(bd, 15), tcor, anchor="mm")
            iy += 62
        y += gh + 16

    by = h - pad - 48
    bw = int(d.textlength(botao_txt, font=_f(bd, 19))) + 44
    rrect(d, [w - pad - bw, by, w - pad, by + 46], 9, fill=PERIGO)
    txt(d, (w - pad - bw / 2, by + 23), botao_txt, _f(bd, 19), (255, 255, 255), anchor="mm")

    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=20, fill=255)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.paste(im, (0, 0), mask)
    ImageDraw.Draw(out).rounded_rectangle([0, 0, w - 1, h - 1], radius=20, outline=LINHA, width=2)
    return out


def cena_screenshot(L, fam, titulo, sub, aba_sel, grupos, botao_txt, saida):
    W, H = 1280, 800
    bg = gradiente(W, H).convert("RGBA")
    d = ImageDraw.Draw(bg)
    reg, sb, bd = fam
    txt(d, (64, 76), titulo, _f(bd, 44), (255, 255, 255), anchor="lm")
    txt(d, (66, 128), sub, _f(reg, 25), (255, 255, 255, 235), anchor="lm")
    jw, jh = 1120, 520
    jx, jy = (W - jw) // 2, 215
    sombra_card(bg, [jx, jy, jx + jw, jy + jh], 20)
    bg.alpha_composite(janela_app(jw, jh, L, fam, aba_sel, grupos, botao_txt), (jx, jy))
    bg.convert("RGB").save(saida, "PNG")


def cena_marquee(L, fam, saida):
    W, H = 1400, 560
    bg = gradiente(W, H).convert("RGBA")
    d = ImageDraw.Draw(bg)
    reg, sb, bd = fam
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(gl).ellipse([-200, -400, W + 200, 260], fill=(255, 255, 255, 26))
    bg.alpha_composite(gl)
    sombra_card(bg, [150, 130, 450, 430], 66, blur=40, alpha=90, dy=18)
    bg.alpha_composite(Image.open(ICONE).convert("RGBA").resize((300, 300), Image.LANCZOS), (150, 130))
    txt(d, (520, 226), "No Duplicate Tab", _f(bd, 70), (255, 255, 255), anchor="lm")
    txt(d, (524, 320), L["marquee_sub"], _f(sb, 29), (255, 255, 255, 240), anchor="lm")
    bg.convert("RGB").save(saida, "PNG")


def cena_promo(L, fam, saida):
    W, H = 440, 280
    bg = gradiente(W, H).convert("RGBA")
    d = ImageDraw.Draw(bg)
    reg, sb, bd = fam
    bg.alpha_composite(Image.open(ICONE).convert("RGBA").resize((116, 116), Image.LANCZOS), ((W - 116) // 2, 40))
    txt(d, (W / 2, 196), "No Duplicate Tab", _f(bd, 29), (255, 255, 255), anchor="mm")
    txt(d, (W / 2, 234), L["promo_sub"], _f(reg, 17), (255, 255, 255, 230), anchor="mm")
    bg.convert("RGB").save(saida, "PNG")


def dados_tabs(L):
    return [
        {"titulo": "youtube.com/watch?v=dQw4w9WgXcQ", "dir": L["count"].format(n=3), "itens": [
            {"manter": True,  "tit": "Rick Astley - Never Gonna Give You Up", "url": "youtube.com/watch?v=dQw4w9WgXcQ"},
            {"manter": False, "tit": "Rick Astley - Never Gonna Give You Up", "url": "youtube.com/watch?v=dQw4w9WgXcQ&t=15s"},
            {"manter": False, "tit": "Rick Astley - Never Gonna Give You Up", "url": "youtube.com/watch?v=dQw4w9WgXcQ#comments"},
        ]},
    ]


def dados_favs(L):
    fo = L["folders"]
    return [
        {"titulo": "developer.mozilla.org/docs/Web/CSS", "dir": f"{fo['bar']} · {fo['dev']}/{fo['css']}", "itens": [
            {"manter": True,  "tit": "CSS: Cascading Style Sheets | MDN", "url": fo['bar'], "pasta": True},
            {"manter": False, "tit": "CSS: Cascading Style Sheets | MDN", "url": f"{fo['dev']} › {fo['css']}", "pasta": True},
            {"manter": False, "tit": "CSS: Cascading Style Sheets | MDN", "url": fo['read'], "pasta": True},
        ]},
    ]


# ── Traduções ──
LANGS = {
"pt": {"fam": "latin", "sub1": "Feche abas repetidas com prévia antes de fechar",
    "head2": "Favoritos duplicados", "sub2": "Veja a pasta de cada cópia e exclua com segurança",
    "nav_tabs": "Abas abertas", "nav_favs": "Favoritos", "ignore": "Ignorar parâmetros da URL",
    "keep": "MANTER", "close": "FECHAR", "btn_close": "Fechar abas marcadas", "btn_delete": "Excluir marcados",
    "count": "{n} abas", "marquee_sub": "Feche abas repetidas e limpe favoritos duplicados",
    "promo_sub": "abas & favoritos duplicados",
    "folders": {"bar": "Barra de favoritos", "read": "Ler depois", "dev": "Dev", "css": "CSS", "tech": "Tecnologia", "daily": "Diário"}},
"en": {"fam": "latin", "sub1": "Close duplicate tabs with a preview before closing",
    "head2": "Duplicate bookmarks", "sub2": "See each copy's folder and delete safely",
    "nav_tabs": "Open tabs", "nav_favs": "Bookmarks", "ignore": "Ignore URL parameters",
    "keep": "KEEP", "close": "CLOSE", "btn_close": "Close selected tabs", "btn_delete": "Delete selected",
    "count": "{n} tabs", "marquee_sub": "Close duplicate tabs and clean duplicate bookmarks",
    "promo_sub": "duplicate tabs & bookmarks",
    "folders": {"bar": "Bookmarks bar", "read": "Read later", "dev": "Dev", "css": "CSS", "tech": "Tech", "daily": "Daily"}},
"es": {"fam": "latin", "sub1": "Cierra pestañas repetidas con vista previa antes de cerrar",
    "head2": "Marcadores duplicados", "sub2": "Mira la carpeta de cada copia y elimina con seguridad",
    "nav_tabs": "Pestañas abiertas", "nav_favs": "Marcadores", "ignore": "Ignorar parámetros de la URL",
    "keep": "MANTENER", "close": "CERRAR", "btn_close": "Cerrar pestañas marcadas", "btn_delete": "Eliminar marcados",
    "count": "{n} pestañas", "marquee_sub": "Cierra pestañas repetidas y limpia marcadores duplicados",
    "promo_sub": "pestañas y marcadores duplicados",
    "folders": {"bar": "Barra de marcadores", "read": "Leer después", "dev": "Dev", "css": "CSS", "tech": "Tecnología", "daily": "Diario"}},
"ru": {"fam": "latin", "sub1": "Закрывайте повторяющиеся вкладки с предпросмотром",
    "head2": "Дубликаты закладок", "sub2": "Смотрите папку каждой копии и удаляйте безопасно",
    "nav_tabs": "Открытые вкладки", "nav_favs": "Закладки", "ignore": "Игнорировать параметры URL",
    "keep": "ОСТАВИТЬ", "close": "ЗАКРЫТЬ", "btn_close": "Закрыть отмеченные", "btn_delete": "Удалить отмеченные",
    "count": "{n} вкладки", "marquee_sub": "Закрывайте дубликаты вкладок и очищайте дубликаты закладок",
    "promo_sub": "дубликаты вкладок и закладок",
    "folders": {"bar": "Панель закладок", "read": "Прочитать позже", "dev": "Разработка", "css": "CSS", "tech": "Технологии", "daily": "Ежедневное"}},
"ja": {"fam": "ja", "sub1": "閉じる前にプレビューで重複タブを整理",
    "head2": "重複したブックマーク", "sub2": "各コピーのフォルダーを確認して安全に削除",
    "nav_tabs": "開いているタブ", "nav_favs": "ブックマーク", "ignore": "URLパラメータを無視",
    "keep": "残す", "close": "閉じる", "btn_close": "選択したタブを閉じる", "btn_delete": "選択を削除",
    "count": "{n} 個のタブ", "marquee_sub": "重複したタブを閉じ、重複したブックマークを整理",
    "promo_sub": "重複タブとブックマーク",
    "folders": {"bar": "ブックマークバー", "read": "後で読む", "dev": "開発", "css": "CSS", "tech": "テック", "daily": "デイリー"}},
"zh": {"fam": "zh", "sub1": "关闭前预览，清理重复标签页",
    "head2": "重复的书签", "sub2": "查看每个副本所在文件夹，安全删除",
    "nav_tabs": "打开的标签页", "nav_favs": "书签", "ignore": "忽略网址参数",
    "keep": "保留", "close": "关闭", "btn_close": "关闭选中标签页", "btn_delete": "删除选中项",
    "count": "{n} 个标签页", "marquee_sub": "关闭重复标签页，清理重复书签",
    "promo_sub": "重复标签页和书签",
    "folders": {"bar": "书签栏", "read": "稍后阅读", "dev": "开发", "css": "CSS", "tech": "科技", "daily": "每日"}},
"hi": {"fam": "hi", "sub1": "बंद करने से पहले प्रीव्यू के साथ डुप्लिकेट टैब बंद करें",
    "head2": "डुप्लिकेट बुकमार्क", "sub2": "हर कॉपी का फ़ोल्डर देखें और सुरक्षित रूप से हटाएँ",
    "nav_tabs": "खुले टैब", "nav_favs": "बुकमार्क", "ignore": "URL पैरामीटर अनदेखा करें",
    "keep": "रखें", "close": "बंद करें", "btn_close": "चयनित टैब बंद करें", "btn_delete": "चयनित हटाएँ",
    "count": "{n} टैब", "marquee_sub": "डुप्लिकेट टैब बंद करें और डुप्लिकेट बुकमार्क साफ़ करें",
    "promo_sub": "डुप्लिकेट टैब और बुकमार्क",
    "folders": {"bar": "बुकमार्क बार", "read": "बाद में पढ़ें", "dev": "डेव", "css": "CSS", "tech": "टेक", "daily": "रोज़ाना"}},
"ko": {"fam": "ko", "sub1": "닫기 전에 미리보기로 중복 탭 정리",
    "head2": "중복된 북마크", "sub2": "각 사본의 폴더를 확인하고 안전하게 삭제",
    "nav_tabs": "열린 탭", "nav_favs": "북마크", "ignore": "URL 매개변수 무시",
    "keep": "유지", "close": "닫기", "btn_close": "선택한 탭 닫기", "btn_delete": "선택 삭제",
    "count": "{n}개 탭", "marquee_sub": "중복 탭을 닫고 중복 북마크를 정리하세요",
    "promo_sub": "중복 탭 & 북마크",
    "folders": {"bar": "북마크바", "read": "나중에 읽기", "dev": "개발", "css": "CSS", "tech": "테크", "daily": "데일리"}},
}

if __name__ == "__main__":
    for code, L in LANGS.items():
        fam = FAMILIA[L["fam"]]
        d = os.path.join(AQUI, code)
        os.makedirs(d, exist_ok=True)
        cena_screenshot(L, fam, "No Duplicate Tab", L["sub1"], "tabs", dados_tabs(L),
                        L["btn_close"], os.path.join(d, "screenshot-1-tabs.png"))
        cena_screenshot(L, fam, L["head2"], L["sub2"], "favs", dados_favs(L),
                        L["btn_delete"], os.path.join(d, "screenshot-2-bookmarks.png"))
        cena_marquee(L, fam, os.path.join(d, "marquee-1400x560.png"))
        cena_promo(L, fam, os.path.join(d, "promo-440x280.png"))
        print("ok", code)
    print("Concluído:", ", ".join(LANGS))
