"""Split Romanian legal texts into retrieval-sized PDF sections.

The Codul fiscal source PDFs overlap at pages 80 and 169, so the duplicate
pages are skipped.  Source pages beyond a document's configured final page are
also excluded.  Each document is emitted as ten-page PDFs named with the
original document page numbers.
"""

from pathlib import Path

from pypdf import PdfReader, PdfWriter


ROOT = Path(__file__).resolve().parent
DOCUMENTS = (
    (
        "cod_fiscal",
        (
            ("cod_fiscal-1-80.pdf", 0, 1),
            ("cod_fiscal-80-169.pdf", 1, 81),
            ("cod_fiscal-169-228.pdf", 1, 170),
        ),
        228,
    ),
    (
        "codul_muncii",
        (("codul_muncii.pdf", 0, 1),),
        95,
    ),
    (
        "codul_administrativ",
        (("codul_administrativ.pdf", 0, 1),),
        468,
    ),
    (
        "codul_civil",
        (("codul_civil.pdf", 0, 1),),
        843,
    ),
    (
        "cod_rutier",
        (("cod_rutier.pdf", 0, 1),),
        80,
    ),
    (
        "cod_penal",
        (("cod_penal.pdf", 0, 1),),
        105,
    ),
    (
        "constitutia_romaniei",
        (("constitutia_romaniei.pdf", 0, 1),),
        40,
    ),
    (
        "aplicare_cod_fiscal",
        (("aplicare_cod_fiscal.pdf", 0, 1),),
        41,
    ),
    (
        "cod_procedura_civila",
        (("cod_procedura_civila.pdf", 0, 1),),
        134,
    ),
    (
        "cod_procedura_fiscala",
        (("cod_procedura_fiscala.pdf", 0, 1),),
        167,
    ),
    (
        "oug_34_2014",
        (("oug_34_2014.pdf", 0, 1),),
        27,
    ),
    (
        "legea_31_1990",
        (("legea_31_1990.pdf", 0, 1),),
        120,
    ),
    (
        "legea_265_2022",
        (("L_265_2022.pdf", 0, 1),),
        57,
    ),
)
CHUNK_SIZE = 10
OUTPUT = ROOT / "sources"


def build_document(
    prefix: str, source_files: tuple[tuple[str, int, int], ...], expected_end: int
) -> None:
    pages: list[tuple[int, object]] = []
    for filename, skip, original_start in source_files:
        reader = PdfReader(str(ROOT / filename))
        for page_index, page in enumerate(reader.pages[skip:]):
            original_page = original_start + page_index
            if original_page > expected_end:
                break
            pages.append((original_page, page))

    expected_pages = list(range(1, expected_end + 1))
    actual_pages = [original_page for original_page, _ in pages]
    if actual_pages != expected_pages:
        raise RuntimeError(
            f"Expected {prefix} pages 1-{expected_end} once each, "
            f"found {actual_pages[:3]}...{actual_pages[-3:]}."
        )

    OUTPUT.mkdir(exist_ok=True)
    for existing in OUTPUT.glob(f"{prefix}-p*.pdf"):
        existing.unlink()

    for start in range(0, len(pages), CHUNK_SIZE):
        chunk = pages[start : start + CHUNK_SIZE]
        first_page, _ = chunk[0]
        last_page, _ = chunk[-1]
        writer = PdfWriter()
        for _, page in chunk:
            writer.add_page(page)

        destination = OUTPUT / f"{prefix}-p{first_page:03d}-{last_page:03d}.pdf"
        with destination.open("wb") as output:
            writer.write(output)
        print(destination.name)


def main() -> None:
    for prefix, source_files, expected_end in DOCUMENTS:
        missing = [
            filename
            for filename, _, _ in source_files
            if not (ROOT / filename).is_file()
        ]
        if missing:
            print(f"Skipping {prefix}: missing source file(s): {', '.join(missing)}")
            continue
        build_document(prefix, source_files, expected_end)


if __name__ == "__main__":
    main()
