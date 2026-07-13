"""Split the official Codul Fiscal PDFs into retrieval-sized PDF sections.

The source PDFs overlap at pages 80 and 169.  Keep the first occurrence of
each page and create ten-page PDFs named with the original document pages.
"""

from pathlib import Path

from pypdf import PdfReader, PdfWriter


ROOT = Path(__file__).resolve().parent
SOURCES = (
    ("cod_fiscal-1-80.pdf", 0, 1),
    ("cod_fiscal-80-169.pdf", 1, 81),
    ("cod_fiscal-169-228.pdf", 1, 170),
)
CHUNK_SIZE = 10
OUTPUT = ROOT / "sources"


def main() -> None:
    pages: list[tuple[int, object]] = []
    for filename, skip, original_start in SOURCES:
        reader = PdfReader(str(ROOT / filename))
        for page_index, page in enumerate(reader.pages[skip:]):
            pages.append((original_start + page_index, page))

    expected_pages = list(range(1, 229))
    actual_pages = [original_page for original_page, _ in pages]
    if actual_pages != expected_pages:
        raise RuntimeError(
            f"Expected pages 1-228 once each, found {actual_pages[:3]}...{actual_pages[-3:]}."
        )

    OUTPUT.mkdir(exist_ok=True)
    for existing in OUTPUT.glob("cod_fiscal-p*.pdf"):
        existing.unlink()

    for start in range(0, len(pages), CHUNK_SIZE):
        chunk = pages[start : start + CHUNK_SIZE]
        first_page, _ = chunk[0]
        last_page, _ = chunk[-1]
        writer = PdfWriter()
        for _, page in chunk:
            writer.add_page(page)

        destination = OUTPUT / f"cod_fiscal-p{first_page:03d}-{last_page:03d}.pdf"
        with destination.open("wb") as output:
            writer.write(output)
        print(destination.name)


if __name__ == "__main__":
    main()
