"""Anexa a capa (capa.png) como primeira página do PDF gerado pelo Jupyter Book.

Uso, depois de `jb build . --builder pdflatex`:

    python3 adiciona_capa.py [entrada.pdf] [saida.pdf]

Por padrão lê _build/latex/book.pdf e grava o PDF publicado em docs/.
A capa ocupa a folha inteira. O ideal é capa.png já vir na proporção da
página (Carta a 300 dpi: 2550 x 3300 px); se não vier, a imagem é cortada
levemente no topo e na base e esticada na largura até essa proporção.
Requer pillow e pypdf.
"""

import io
import sys
from pathlib import Path

from PIL import Image
from pypdf import PdfReader, PdfWriter

RAIZ = Path(__file__).resolve().parent
CAPA = RAIZ / "capa.png"
ENTRADA = RAIZ / "_build/latex/book.pdf"
SAIDA = RAIZ / "docs/TMBuriol_Métodos_Numéricos_em_Python.pdf"

CORTE = 24  # pixels removidos no topo e na base da imagem


def pagina_da_capa(largura_pt, altura_pt):
    """Gera um PDF de uma página com a capa ocupando largura_pt x altura_pt."""
    img = Image.open(CAPA).convert("RGB")
    w, h = img.size
    if abs(w / h - largura_pt / altura_pt) > 0.005:
        # proporção diferente da página: corta topo e base e estica na largura
        img = img.crop((0, CORTE, w, h - CORTE))
        h = img.size[1]
        img = img.resize((round(h * largura_pt / altura_pt), h), Image.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, format="PDF", resolution=72 * img.size[1] / altura_pt, quality=92)
    pagina = PdfReader(buf).pages[0]
    pagina.scale_to(largura_pt, altura_pt)  # elimina erros de arredondamento
    return pagina


def main():
    entrada = Path(sys.argv[1]) if len(sys.argv) > 1 else ENTRADA
    saida = Path(sys.argv[2]) if len(sys.argv) > 2 else SAIDA

    # clone_from preserva sumário lateral, destinos e links internos
    livro = PdfWriter(clone_from=entrada)
    caixa = livro.pages[0].mediabox
    livro.insert_page(pagina_da_capa(float(caixa.width), float(caixa.height)), 0)

    with open(saida, "wb") as f:
        livro.write(f)
    print(f"{saida}: {len(livro.pages)} páginas (capa + {len(livro.pages) - 1})")


if __name__ == "__main__":
    main()
