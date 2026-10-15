"""Gera o recorte do foguete e as versoes responsivas AVIF/WebP da hero.

Roda a partir da raiz do repositorio:  python scripts/build-assets.py
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent

# Larguras candidatas. So geramos as menores que a origem, mais a largura
# nativa - nao faz sentido ampliar: hero3.png tem 1704px e o recorte do
# foguete tem 850px.
CANDIDATES = (960, 1440)

# Recorte do foguete a partir da hero antiga.
# Caixa validada: ceu azul-escuro a esquerda (area de texto), coluna de
# ignicao dourada a direita, cidade acesa embaixo. O terno do Dudu comeca
# em x~985, entao 970 e o limite seguro.
ROCKET_BOX = (120, 330, 970, 941)


def emit(img: Image.Image, stem: str, write_png: bool) -> list[int]:
    """Gera as variantes AVIF/WebP. Devolve as larguras geradas."""
    if write_png:
        img.save(ROOT / f"{stem}.png", optimize=True)

    widths = [w for w in CANDIDATES if w < img.width] + [img.width]
    for w in widths:
        h = round(img.height * w / img.width)
        resized = img if w == img.width else img.resize((w, h), Image.LANCZOS)
        resized.save(ROOT / f"{stem}-{w}.avif", quality=58)
        resized.save(ROOT / f"{stem}-{w}.webp", quality=80, method=6)
    return widths


def main() -> None:
    rocket = Image.open(ROOT / "hero.png").convert("RGB").crop(ROCKET_BOX)
    rocket_widths = emit(rocket, "foguete", write_png=True)

    # hero3.png e arte entregue e serve de fallback: nao reescrever.
    hero = Image.open(ROOT / "hero3.png").convert("RGB")
    hero_widths = emit(hero, "hero3", write_png=False)

    for stem, widths in (("hero3", hero_widths), ("foguete", rocket_widths)):
        print(f"\n{stem}: larguras {widths}")
        for fmt in ("avif", "webp"):
            srcset = ", ".join(f"{stem}-{w}.{fmt} {w}w" for w in widths)
            print(f"  srcset {fmt}: {srcset}")

    print()
    for path in sorted(ROOT.glob("hero3-*.*")) + sorted(ROOT.glob("foguete-*.*")):
        print(f"{path.name:24} {path.stat().st_size / 1024:8.1f} KB")


if __name__ == "__main__":
    main()
