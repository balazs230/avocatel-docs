"""Build retrieval-sized Markdown chunks for migrated legal sources.

The chunks follow legal structure rather than the page grid of the former PDF
sources.  Each chunk is validated by article range, and its catalog entry is
rendered from the same metadata so filenames, ranges, and descriptions cannot
drift independently.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "sources"
CATALOG = ROOT / "catalog.txt"
SOURCE = ROOT / "codul_muncii.md"
LEGACY_TEXT_SOURCE = ROOT / "codul_muncii.txt"
LEGACY_SOURCE = ROOT / "codul_muncii.pdf"
PUBLIC_BASE_URL = "https://balazs230.github.io/avocatel-docs/sources"
MIN_CHUNK_CHARACTERS = 30_000
MAX_CHUNK_CHARACTERS = 60_000

CIVIL_SOURCE = ROOT / "codul_civil.md"
CIVIL_LEGACY_TEXT_SOURCES = (ROOT / "cod_civil.txt", ROOT / "codul_civil.txt")
CIVIL_LEGACY_SOURCE = ROOT / "codul_civil.pdf"
CIVIL_NOISE_LINES = {
    "Actul este reprodus în forma publicată în Monitorul Oficial al",
    "României şi nu include posibile modificări ulterioare.",
    "Cumpăraţi documentul în formă actualizată sau alegeţi un",
    "abonament Lege5 care permite accesul la orice formă",
    "actualizată, fără mesaje publicitare.",
}
CIVIL_STRUCTURE = re.compile(
    r"^(?P<kind>CARTEA|TITLUL|CAPITOLUL|SEC[\u0162\u021aT]IUNEA)\s+.+$"
)
CIVIL_ARTICLE = re.compile(
    r"^Art\.\s+(?P<number>\d{1,3}(?:\.\d{3})?)\.?\s*"
    r"(?:-\s*)?(?P<title>.*)$"
)
CIVIL_MARKDOWN_ARTICLE = re.compile(
    r"(?m)^###### Art\.\s+(?P<number>[\d.]+)(?: — .*)?$"
)
CIVIL_PARAGRAPH = re.compile(r"^\u00a7\s*\d+\.\s*.+$")

PAGE_FOOTER = re.compile(
    r"(?m)^Codul Muncii actualizat Legislatie Protectia Muncii\r?\n\d+\r?\n?"
)
ARTICLE_HEADING = re.compile(r"(?m)^##### Articolul\s+(\d+(?:\^\d+)?)\s*$")
PLAIN_STRUCTURE = re.compile(
    r"^(?P<kind>TITLUL|CAPITOLUL|SECTIUNEA)\s+(?P<number>[IVXLCDM]+|\d+)$"
)
PLAIN_ARTICLE = re.compile(r"^Articolul\s+\d+(?:\^\d+)?$")


@dataclass(frozen=True)
class Chunk:
    first_article: int
    last_article: int
    start_heading: str
    end_heading: str | None
    description: str

    @property
    def filename(self) -> str:
        return (
            f"codul_muncii-art{self.first_article:03d}-"
            f"{self.last_article:03d}.md"
        )


CHUNKS = (
    Chunk(
        1,
        48,
        "## TITLUL I — Dispozitii generale",
        "### CAPITOLUL IV — Suspendarea contractului individual de munca",
        "Titlul I: dispoziții generale și principii fundamentale; "
        "Titlul II, cap. I-III: încheierea, executarea și modificarea "
        "contractului individual de muncă",
    ),
    Chunk(
        49,
        110,
        "### CAPITOLUL IV — Suspendarea contractului individual de munca",
        "## TITLUL III — Timpul de munca si timpul de odihna",
        "Titlul II, cap. IV-IX: suspendarea și încetarea contractului; "
        "contractele pe durată determinată, munca temporară, cu timp "
        "parțial și la domiciliu",
    ),
    Chunk(
        111,
        174,
        "## TITLUL III — Timpul de munca si timpul de odihna",
        "## TITLUL V — Sanatatea si securitatea in munca",
        "Titlurile III-IV: timpul de muncă și de odihnă, repausuri, "
        "concedii, salarizare, plata și protecția salariului",
    ),
    Chunk(
        175,
        240,
        "## TITLUL V — Sanatatea si securitatea in munca",
        "## TITLUL XI — Raspunderea juridica",
        "Titlurile V-X: sănătatea și securitatea în muncă, formarea "
        "profesională, dialogul social, contractele colective, conflictele "
        "de muncă și Inspecția Muncii",
    ),
    Chunk(
        241,
        281,
        "## TITLUL XI — Raspunderea juridica",
        None,
        "Titlurile XI-XIII: regulamentul intern, răspunderea juridică, "
        "jurisdicția muncii, dispozițiile tranzitorii și finale și "
        "directivele europene transpuse",
    ),
)


@dataclass(frozen=True)
class CivilChunk:
    first_article: int
    last_article: int
    description: str
    includes_implementation_law: bool = False

    @property
    def filename(self) -> str:
        return (
            f"codul_civil-art{self.first_article:04d}-"
            f"{self.last_article:04d}.md"
        )


CIVIL_CHUNKS = (
    CivilChunk(
        1,
        103,
        "legea civilă, aplicarea și interpretarea ei, publicitatea "
        "drepturilor, persoana fizică, capacitatea, drepturile personalității "
        "și starea civilă",
    ),
    CivilChunk(
        104,
        199,
        "ocrotirea persoanei fizice, tutela minorului, consiliul de familie, "
        "curatela și înființarea persoanei juridice",
    ),
    CivilChunk(
        200,
        277,
        "capacitatea, organele, reorganizarea și încetarea persoanei "
        "juridice; apărarea drepturilor nepatrimoniale, familia, logodna și "
        "începutul căsătoriei",
    ),
    CivilChunk(
        278,
        374,
        "încheierea și nulitatea căsătoriei, drepturile soților, regimurile "
        "matrimoniale și începutul divorțului",
    ),
    CivilChunk(
        375,
        474,
        "divorțul și efectele sale, rudenia, filiația, reproducerea asistată "
        "medical și adopția",
    ),
    CivilChunk(
        475,
        580,
        "încetarea adopției, autoritatea părintească, obligația de "
        "întreținere, bunurile și începutul proprietății private",
    ),
    CivilChunk(
        581,
        668,
        "accesiunea, limitele proprietății private, proprietatea comună, "
        "coproprietatea, condominiul și partajul",
    ),
    CivilChunk(
        669,
        772,
        "proprietatea periodică, superficia, uzufructul, uzul, abitația, "
        "servituțile și începutul fiduciei",
    ),
    CivilChunk(
        773,
        857,
        "fiducia și administrarea bunurilor altuia",
    ),
    CivilChunk(
        858,
        934,
        "proprietatea publică, cartea funciară, înscrierea și rectificarea "
        "drepturilor tabulare și începutul posesiei",
    ),
    CivilChunk(
        935,
        1019,
        "dobândirea proprietății prin posesie, acțiunile posesorii, "
        "deschiderea moștenirii, moștenirea legală și începutul "
        "liberalităților",
    ),
    CivilChunk(
        1020,
        1105,
        "donațiile, testamentele, legatele, dezmoștenirea, rezerva "
        "succesorală și reducțiunea liberalităților",
    ),
    CivilChunk(
        1106,
        1181,
        "opțiunea succesorală, moștenirea vacantă, partajul succesoral, "
        "raportul donațiilor și începutul obligațiilor",
    ),
    CivilChunk(
        1182,
        1294,
        "formarea și validitatea contractului, consimțământul, obiectul, "
        "cauza, forma, nulitatea, interpretarea și efectele contractului",
    ),
    CivilChunk(
        1295,
        1410,
        "reprezentarea, cesiunea contractului, actul juridic unilateral, "
        "faptul juridic licit, răspunderea civilă și condiția",
    ),
    CivilChunk(
        1411,
        1526,
        "termenul, obligațiile complexe, plata, punerea în întârziere și "
        "începutul executării silite",
    ),
    CivilChunk(
        1527,
        1634,
        "executarea silită, daunele-interese, rezoluțiunea, măsurile "
        "conservatorii, cesiunea de creanță și stingerea obligațiilor",
    ),
    CivilChunk(
        1635,
        1729,
        "restituirea prestațiilor și contractul de vânzare: formare, preț, "
        "predare și garanții",
    ),
    CivilChunk(
        1730,
        1835,
        "varietățile vânzării, dreptul de preempțiune, schimbul, furnizarea "
        "și locațiunea",
    ),
    CivilChunk(
        1836,
        1924,
        "închirierea locuințelor, arendarea, contractul de antrepriză și "
        "începutul contractului de societate",
    ),
    CivilChunk(
        1925,
        2008,
        "contractul de societate, asocierea în participație și contractul "
        "de transport",
    ),
    CivilChunk(
        2009,
        2095,
        "contractul de mandat, mandatul fără reprezentare și contractul de "
        "agenție",
    ),
    CivilChunk(
        2096,
        2198,
        "intermedierea, depozitul, împrumutul, contul curent, contul bancar "
        "și începutul asigurării",
    ),
    CivilChunk(
        2199,
        2304,
        "asigurarea, renta viageră, întreținerea, jocul și pariul, tranzacția "
        "și începutul garanțiilor personale",
    ),
    CivilChunk(
        2305,
        2419,
        "fideiusiunea, garanțiile autonome, privilegiile și ipoteca "
        "imobiliară și mobiliară",
    ),
    CivilChunk(
        2420,
        2522,
        "rangul și executarea ipotecilor, gajul, dreptul de retenție și "
        "începutul prescripției extinctive",
    ),
    CivilChunk(
        2523,
        2604,
        "cursul și împlinirea prescripției, decăderea, calculul termenelor și "
        "dreptul internațional privat privind persoanele și familia",
    ),
    CivilChunk(
        2605,
        2664,
        "dreptul internațional privat privind bunurile, moștenirea, "
        "obligațiile, titlurile de credit, fiducia și prescripția; "
        "dispoziții finale și de punere în aplicare",
        includes_implementation_law=True,
    ),
)


def clean_source(text: str) -> str:
    """Remove recurring PDF headers/page numbers without altering legal text."""
    text = text.removeprefix("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    text = PAGE_FOOTER.sub("", text)
    return text.rstrip() + "\n"


def format_markdown(text: str) -> str:
    """Convert the plain legal hierarchy into stable Markdown headings."""
    if text.startswith("# Codul muncii\n") and "## TITLUL I —" in text:
        return normalize_heading_spacing(text)

    lines = text.splitlines()
    if not lines or lines[0] != "Codul muncii":
        raise RuntimeError("Unexpected Codul muncii document heading")

    rendered = ["# Codul muncii"]
    index = 1
    heading_levels = {"TITLUL": 2, "CAPITOLUL": 3, "SECTIUNEA": 4}
    while index < len(lines):
        line = lines[index]
        structure = PLAIN_STRUCTURE.fullmatch(line)
        if structure:
            subtitle_lines = []
            index += 1
            while index < len(lines):
                candidate = lines[index]
                if PLAIN_STRUCTURE.fullmatch(candidate) or PLAIN_ARTICLE.fullmatch(
                    candidate
                ):
                    break
                subtitle_lines.append(candidate.strip())
                index += 1
            subtitle = " ".join(part for part in subtitle_lines if part)
            if not subtitle:
                raise RuntimeError(f"Missing subtitle after {line}")
            level = heading_levels[structure.group("kind")]
            rendered.append(f"{'#' * level} {line} — {subtitle}")
            continue
        if PLAIN_ARTICLE.fullmatch(line):
            rendered.append(f"##### {line}")
        else:
            rendered.append(line)
        index += 1

    return normalize_heading_spacing("\n".join(rendered))


def normalize_heading_spacing(text: str) -> str:
    """Surround ATX headings with blank lines for portable Markdown parsing."""
    rendered: list[str] = []
    for line in text.splitlines():
        if re.match(r"^#{1,6} ", line):
            if rendered and rendered[-1] != "":
                rendered.append("")
            rendered.append(line)
            rendered.append("")
        else:
            rendered.append(line)

    compacted: list[str] = []
    for line in rendered:
        if line or not compacted or compacted[-1] != "":
            compacted.append(line)
    return "\n".join(compacted).rstrip() + "\n"


def locate_once(text: str, marker: str) -> int:
    positions = [match.start() for match in re.finditer(re.escape(marker), text)]
    if len(positions) != 1:
        raise RuntimeError(f"Expected marker once, found {len(positions)}: {marker!r}")
    return positions[0]


def chunk_header(preamble: str, chunk: Chunk) -> str:
    return (
        f"{preamble.rstrip()}\n"
        f"Fragment: articolele {chunk.first_article}-{chunk.last_article}\n"
        f"Cuprins: {chunk.description}.\n\n"
    )


def validate_config() -> None:
    for current, following in zip(CHUNKS, CHUNKS[1:]):
        if current.last_article + 1 != following.first_article:
            raise RuntimeError("Chunk article ranges are not contiguous")
        if current.end_heading != following.start_heading:
            raise RuntimeError("Chunk heading boundaries are not contiguous")
    if CHUNKS[-1].end_heading is not None:
        raise RuntimeError("The final chunk must extend to the end of the source")


def build_chunks(text: str) -> list[Path]:
    OUTPUT.mkdir(exist_ok=True)
    first_title = locate_once(text, CHUNKS[0].start_heading)
    preamble = text[:first_title]
    expected_names = {chunk.filename for chunk in CHUNKS}

    for pattern in ("codul_muncii-art*.txt", "codul_muncii-art*.md"):
        for stale in OUTPUT.glob(pattern):
            if stale.name not in expected_names:
                stale.unlink()

    built = []
    for chunk in CHUNKS:
        start = locate_once(text, chunk.start_heading)
        end = len(text) if chunk.end_heading is None else locate_once(text, chunk.end_heading)
        if end <= start:
            raise RuntimeError(f"Invalid boundaries for {chunk.filename}")

        body = text[start:end].strip() + "\n"
        articles = ARTICLE_HEADING.findall(body)
        if not articles:
            raise RuntimeError(f"No article headings found in {chunk.filename}")
        if articles[0] != str(chunk.first_article) or articles[-1] != str(
            chunk.last_article
        ):
            raise RuntimeError(
                f"{chunk.filename} expected art. {chunk.first_article}-{chunk.last_article}, "
                f"found {articles[0]}-{articles[-1]}"
            )

        content = chunk_header(preamble, chunk) + body
        if not MIN_CHUNK_CHARACTERS <= len(content) <= MAX_CHUNK_CHARACTERS:
            raise RuntimeError(
                f"{chunk.filename} has {len(content):,} characters; expected "
                f"{MIN_CHUNK_CHARACTERS:,}-{MAX_CHUNK_CHARACTERS:,}"
            )

        destination = OUTPUT / chunk.filename
        destination.write_text(content, encoding="utf-8", newline="\n")
        built.append(destination)
        print(f"{destination.name}: {destination.stat().st_size:,} bytes")

    return built


def catalog_block(built: list[Path]) -> bytes:
    filenames = {path.name for path in built}
    entries = []
    for chunk in CHUNKS:
        if chunk.filename not in filenames:
            raise RuntimeError(f"Missing generated chunk: {chunk.filename}")
        entries.append(
            f"- Codul muncii (Legea nr. 53/2003, actualizată la 17 octombrie "
            f"2022) — {chunk.description}. Art. {chunk.first_article}-"
            f"{chunk.last_article}.\n"
            f"  {PUBLIC_BASE_URL}/{chunk.filename}\n"
        )
    return ("\n".join(entries) + "\n").encode("utf-8")


def update_catalog(built: list[Path]) -> None:
    data = CATALOG.read_bytes()
    entry_pattern = re.compile(
        rb"- Codul muncii[^\r\n]*\r?\n"
        rb"  https://[^\r\n]*/sources/codul_muncii-[^\r\n]*\r?\n(?:\r?\n)?"
    )
    matches = list(entry_pattern.finditer(data))
    replacement = catalog_block(built)

    if matches:
        start, end = matches[0].start(), matches[-1].end()
        unmatched = entry_pattern.sub(b"", data[start:end])
        if unmatched.strip():
            raise RuntimeError("Labor Code catalog entries are not contiguous")
        data = data[:start] + replacement + data[end:]
    else:
        data = data.rstrip() + b"\n\n" + replacement

    CATALOG.write_bytes(data)


def clean_civil_source(text: str) -> str:
    """Remove Lege5 page furniture and restore the first article's ordering."""
    text = text.removeprefix("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    lines = [line for line in text.splitlines() if line not in CIVIL_NOISE_LINES]

    try:
        article_title = lines.index("Izvoarele dreptului civil")
        preliminary_title = lines.index("TITLUL PRELIMINAR")
    except ValueError as error:
        raise RuntimeError("Could not locate the start of Codul civil") from error
    if article_title >= preliminary_title:
        raise RuntimeError("Unexpected ordering at the start of Codul civil")

    misplaced_article_text = lines[article_title:preliminary_title]
    legal_text = lines[preliminary_title:]
    try:
        after_article_one = legal_text.index("Art. 1. -") + 1
    except ValueError as error:
        raise RuntimeError("Could not locate Codul civil art. 1") from error
    legal_text[after_article_one:after_article_one] = misplaced_article_text

    preamble = [
        "Codul civil",
        "Legea nr. 287/2009",
        "Republicată în Monitorul Oficial, Partea I, nr. 505 din 15 iulie 2011",
        "În vigoare de la 1 octombrie 2011",
        "Forma publicată nu include posibile modificări ulterioare.",
    ]
    return "\n".join(preamble + legal_text).rstrip() + "\n"


def format_civil_markdown(text: str) -> str:
    """Apply Markdown levels to the hierarchy found in Codul civil."""
    if text.startswith("# Codul civil\n"):
        rendered = []
        for line in text.splitlines():
            article = CIVIL_ARTICLE.fullmatch(line)
            if article:
                heading = f"###### Art. {article.group('number')}"
                if article.group("title"):
                    heading += f" — {article.group('title')}"
                rendered.append(heading)
            else:
                rendered.append(line)
        return normalize_heading_spacing("\n".join(rendered))

    lines = text.splitlines()
    if not lines or lines[0] != "Codul civil":
        raise RuntimeError("Unexpected Codul civil document heading")

    rendered = ["# Codul civil"]
    for line in lines[1:]:
        structure = CIVIL_STRUCTURE.fullmatch(line)
        article = CIVIL_ARTICLE.fullmatch(line)
        if structure:
            kind = structure.group("kind")
            if kind == "CARTEA":
                level = 2
            elif kind == "TITLUL":
                level = 3
            elif kind == "CAPITOLUL":
                level = 4
            else:
                level = 5
            rendered.append(f"{'#' * level} {line}")
        elif CIVIL_PARAGRAPH.fullmatch(line):
            rendered.append(f"##### {line}")
        elif article:
            heading = f"###### Art. {article.group('number')}"
            if article.group("title"):
                heading += f" — {article.group('title')}"
            rendered.append(heading)
        else:
            rendered.append(line)

    return normalize_heading_spacing("\n".join(rendered))


def civil_chunk_boundaries(markdown: str) -> list[int]:
    structural = [
        (match.start(), len(match.group(1)))
        for match in re.finditer(r"(?m)^(#{2,5}) .+$", markdown)
    ]
    if not structural:
        raise RuntimeError("No Codul civil structural headings found")

    boundaries = [structural[0][0]]
    position = boundaries[0]
    while len(markdown) - position > MAX_CHUNK_CHARACTERS:
        candidates = [
            candidate
            for candidate in structural
            if position + MIN_CHUNK_CHARACTERS
            <= candidate[0]
            <= position + MAX_CHUNK_CHARACTERS
        ]
        if not candidates:
            candidates = [
                (match.start(), 6)
                for match in CIVIL_MARKDOWN_ARTICLE.finditer(markdown)
                if position + MIN_CHUNK_CHARACTERS
                <= match.start()
                <= position + MAX_CHUNK_CHARACTERS
            ]
        if not candidates:
            raise RuntimeError(f"No Civil Code boundary near character {position:,}")

        target = 46_000
        next_position, _ = min(
            candidates,
            key=lambda candidate: abs((candidate[0] - position) - target)
            + (candidate[1] - 2) * 900,
        )
        boundaries.append(next_position)
        position = next_position

    boundaries.append(len(markdown))
    if (
        len(boundaries) > 2
        and boundaries[-1] - boundaries[-2] < 25_000
        and boundaries[-1] - boundaries[-3] <= 65_000
    ):
        boundaries.pop(-2)
    return boundaries


def civil_article_number(label: str) -> int:
    return int(label.replace(".", ""))


def civil_article_groups(markdown: str) -> tuple[list[int], list[int]]:
    numbers = [
        civil_article_number(match.group("number"))
        for match in CIVIL_MARKDOWN_ARTICLE.finditer(markdown)
    ]
    reset = next(
        (
            index
            for index in range(1, len(numbers))
            if numbers[index - 1] > 2600 and numbers[index] < 1000
        ),
        len(numbers),
    )
    return numbers[:reset], numbers[reset:]


def format_civil_article(article: int) -> str:
    return f"{article:,}".replace(",", ".")


def civil_range_label(chunk: CivilChunk) -> str:
    label = (
        f"Art. {format_civil_article(chunk.first_article)}-"
        f"{format_civil_article(chunk.last_article)}"
    )
    if chunk.includes_implementation_law:
        label += "; Legea nr. 71/2011, art. 211-230"
    return label


def build_civil_chunks(markdown: str) -> list[Path]:
    boundaries = civil_chunk_boundaries(markdown)
    if len(boundaries) - 1 != len(CIVIL_CHUNKS):
        raise RuntimeError(
            f"Expected {len(CIVIL_CHUNKS)} Civil Code chunks, "
            f"generated {len(boundaries) - 1}"
        )

    first_structure = boundaries[0]
    preamble = markdown[:first_structure].rstrip()
    expected_names = {chunk.filename for chunk in CIVIL_CHUNKS}
    for pattern in ("codul_civil-art*.txt", "codul_civil-art*.md"):
        for stale in OUTPUT.glob(pattern):
            if stale.name not in expected_names:
                stale.unlink()

    built = []
    for index, (start, end, chunk) in enumerate(
        zip(boundaries, boundaries[1:], CIVIL_CHUNKS)
    ):
        body = markdown[start:end].strip() + "\n"
        code_articles, implementation_articles = civil_article_groups(body)
        if not code_articles:
            raise RuntimeError(f"No articles found in {chunk.filename}")
        if min(code_articles) != chunk.first_article or max(code_articles) != chunk.last_article:
            raise RuntimeError(
                f"{chunk.filename} expected art. {chunk.first_article}-{chunk.last_article}, "
                f"found {min(code_articles)}-{max(code_articles)}"
            )
        if chunk.includes_implementation_law:
            if not implementation_articles or (
                min(implementation_articles) != 211
                or max(implementation_articles) != 230
            ):
                raise RuntimeError("Unexpected Legea nr. 71/2011 article range")
        elif implementation_articles:
            raise RuntimeError(f"Unexpected implementation-law text in chunk {index + 1}")

        content = (
            f"{preamble}\n"
            f"**Fragment:** {civil_range_label(chunk)}\n"
            f"**Cuprins:** {chunk.description}.\n\n"
            f"{body}"
        )
        if not MIN_CHUNK_CHARACTERS <= len(content) <= MAX_CHUNK_CHARACTERS:
            raise RuntimeError(
                f"{chunk.filename} has {len(content):,} characters; expected "
                f"{MIN_CHUNK_CHARACTERS:,}-{MAX_CHUNK_CHARACTERS:,}"
            )

        destination = OUTPUT / chunk.filename
        destination.write_text(content, encoding="utf-8", newline="\n")
        built.append(destination)
        print(f"{destination.name}: {destination.stat().st_size:,} bytes")
    return built


def civil_catalog_block(built: list[Path]) -> bytes:
    filenames = {path.name for path in built}
    entries = []
    for chunk in CIVIL_CHUNKS:
        if chunk.filename not in filenames:
            raise RuntimeError(f"Missing generated chunk: {chunk.filename}")
        entries.append(
            "- Codul civil (Legea nr. 287/2009, forma republicată în M.Of. "
            f"nr. 505/2011) — {chunk.description}. {civil_range_label(chunk)}.\n"
            f"  {PUBLIC_BASE_URL}/{chunk.filename}\n"
        )
    return ("\n".join(entries) + "\n").encode("utf-8")


def update_civil_catalog(built: list[Path]) -> None:
    data = CATALOG.read_bytes()
    entry_pattern = re.compile(
        rb"- Codul civil[^\r\n]*\r?\n"
        rb"  https://[^\r\n]*/sources/codul_civil-[^\r\n]*\r?\n(?:\r?\n)?"
    )
    matches = list(entry_pattern.finditer(data))
    replacement = civil_catalog_block(built)
    if not matches:
        raise RuntimeError("No existing Codul civil catalog entries found")

    start, end = matches[0].start(), matches[-1].end()
    unmatched = entry_pattern.sub(b"", data[start:end])
    if unmatched.strip():
        raise RuntimeError("Civil Code catalog entries are not contiguous")
    CATALOG.write_bytes(data[:start] + replacement + data[end:])


def build_civil_document(raw_source: str) -> None:
    if raw_source.startswith("# Codul civil\n"):
        markdown = format_civil_markdown(raw_source)
    else:
        markdown = format_civil_markdown(clean_civil_source(raw_source))
    CIVIL_SOURCE.write_text(markdown, encoding="utf-8", newline="\n")
    built = build_civil_chunks(markdown)
    update_civil_catalog(built)

    for legacy_chunk in OUTPUT.glob("codul_civil-p*.pdf"):
        legacy_chunk.unlink()
    if CIVIL_LEGACY_SOURCE.exists():
        CIVIL_LEGACY_SOURCE.unlink()
    for legacy_text in CIVIL_LEGACY_TEXT_SOURCES:
        if legacy_text.exists():
            legacy_text.unlink()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--import-source",
        type=Path,
        help="copy a supplied Codul muncii TXT into the repository before building",
    )
    parser.add_argument(
        "--import-civil-source",
        type=Path,
        help="import a supplied Codul civil TXT before building",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    validate_config()
    if args.import_source:
        if not args.import_source.is_file():
            raise FileNotFoundError(args.import_source)
        raw_source = args.import_source.read_text(encoding="utf-8-sig")
    elif SOURCE.is_file():
        raw_source = SOURCE.read_text(encoding="utf-8-sig")
    elif LEGACY_TEXT_SOURCE.is_file():
        raw_source = LEGACY_TEXT_SOURCE.read_text(encoding="utf-8-sig")
    else:
        raise FileNotFoundError(
            f"Missing {SOURCE.name}; provide it with --import-source first"
        )

    markdown = format_markdown(clean_source(raw_source))
    SOURCE.write_text(markdown, encoding="utf-8", newline="\n")
    built = build_chunks(markdown)
    update_catalog(built)

    for legacy_chunk in OUTPUT.glob("codul_muncii-p*.pdf"):
        legacy_chunk.unlink()
    if LEGACY_SOURCE.exists():
        LEGACY_SOURCE.unlink()
    if LEGACY_TEXT_SOURCE.exists():
        LEGACY_TEXT_SOURCE.unlink()

    civil_raw_source = None
    if args.import_civil_source:
        if not args.import_civil_source.is_file():
            raise FileNotFoundError(args.import_civil_source)
        civil_raw_source = args.import_civil_source.read_text(encoding="utf-8-sig")
    elif CIVIL_SOURCE.is_file():
        civil_raw_source = CIVIL_SOURCE.read_text(encoding="utf-8-sig")
    else:
        civil_legacy = next(
            (path for path in CIVIL_LEGACY_TEXT_SOURCES if path.is_file()), None
        )
        if civil_legacy:
            civil_raw_source = civil_legacy.read_text(encoding="utf-8-sig")

    if civil_raw_source is not None:
        build_civil_document(civil_raw_source)


if __name__ == "__main__":
    main()
