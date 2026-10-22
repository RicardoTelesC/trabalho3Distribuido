#!/usr/bin/env python3
"""Gera arquivos para os três cenários de teste (tamanhos aproximados)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "conteudo-teste"
OUT.mkdir(exist_ok=True)


def write_blob(path: Path, size_bytes: int, chunk: bytes = b"x") -> None:
    with path.open("wb") as f:
        remaining = size_bytes
        block = chunk * 65536
        while remaining > 0:
            n = min(remaining, len(block))
            f.write(block[:n])
            remaining -= n
    actual = path.stat().st_size
    print(f"{path.name}: {actual / 1024:.1f} KB ({actual} bytes)")


def write_text_400kb(path: Path) -> None:
    paragraph = (
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
        "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.\n"
    )
    target = 400 * 1024
    with path.open("w", encoding="utf-8") as f:
        while f.tell() < target:
            f.write(paragraph)
    actual = path.stat().st_size
    print(f"{path.name}: {actual / 1024:.1f} KB ({actual} bytes)")


def main() -> None:
    # JPEG mínimo válido (cabecalho) + padding para atingir o tamanho alvo
    jpeg_header = bytes(
        [
            0xFF,
            0xD8,
            0xFF,
            0xE0,
            0x00,
            0x10,
            0x4A,
            0x46,
            0x49,
            0x46,
            0x00,
            0x01,
            0x01,
            0x00,
            0x00,
            0x01,
            0x00,
            0x01,
            0x00,
            0x00,
            0xFF,
            0xD9,
        ]
    )
    img_1mb = OUT / "imagem_1mb.jpg"
    img_300kb = OUT / "imagem_300kb.jpg"
    write_blob(img_1mb, 1024 * 1024, jpeg_header)
    write_blob(img_300kb, 300 * 1024, jpeg_header)
    write_text_400kb(OUT / "texto_400kb.txt")
    print(f"\nArquivos em: {OUT}")
    print("Faça upload das imagens e cole o texto nos posts do WordPress (veja README-TRABALHO3.md).")


if __name__ == "__main__":
    main()
