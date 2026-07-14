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
CIVIL_STRUCTURE = re.compile(
    r"^(?:(?P<book>(?i:CARTEA\s+(?:A\s+)?(?:I|II|III|IV|V|VI|VII)"
    r"(?:\s*-\s*A)?))"
    r"|(?P<title>TITLUL\s+.+)"
    r"|(?P<chapter>CAPITOLUL\s+.+)"
    r"|(?P<section>Sec[\u0162\u0163\u021a\u021bT]iunea\s+.+))$"
)
CIVIL_INLINE_ARTICLE = re.compile(
    r"Art\.\s*(?P<number>\d(?:[\d. ]*?\d)?)\s*\.?\s*[\u2013-]\s*"
)
CIVIL_MARKDOWN_ARTICLE = re.compile(
    r"(?m)^###### Art\.\s+(?P<number>[\d.]+)(?: — .*)?$"
)
CIVIL_PARAGRAPH = re.compile(r"^\u00a7\s*\d+\.\s*.+$")

ADMINISTRATIVE_SOURCE = ROOT / "codul_administrativ.md"
ADMINISTRATIVE_LEGACY_TEXT_SOURCES = (
    ROOT / "cod_administrativ.txt",
    ROOT / "codul_administrativ.txt",
)
ADMINISTRATIVE_LEGACY_SOURCE = ROOT / "codul_administrativ.pdf"
ADMINISTRATIVE_PART = re.compile(
    r"^PARTEA\s+(?:A\s+)?(?:I|II|III|IV|V|VI|VII|VIII|IX|X)"
    r"(?:\s*-\s*A)?$",
    re.IGNORECASE,
)
ADMINISTRATIVE_TITLE = re.compile(r"^TITLUL\s+.+$")
ADMINISTRATIVE_CHAPTER = re.compile(r"^CAPITOLUL\s+.+$")
ADMINISTRATIVE_SECTION = re.compile(
    r"^SEC[\u0162\u0163\u021a\u021bT]IUNEA\s+.+$", re.IGNORECASE
)
ADMINISTRATIVE_ANNEX = re.compile(
    r"^ANEXA\s+Nr\.\s*(?P<number>\d+)(?:\s+(?P<note>.*))?$",
    re.IGNORECASE,
)
ADMINISTRATIVE_ARTICLE = re.compile(
    r"^ARTICOLUL\s+(?P<number>\d+)\s*(?P<body>.*)$"
)
ADMINISTRATIVE_SPECIAL_ARTICLE = re.compile(
    r"^Art\.\s*(?P<number>63|598)\.\s*[\u2013-]\s*(?P<body>.*)$"
)
ADMINISTRATIVE_MARKDOWN_ARTICLE = re.compile(
    r"(?m)^###### Articolul (?P<number>\d+(?:\^\d+)?)$"
)
ADMINISTRATIVE_MARKDOWN_ANNEX = re.compile(
    r"(?m)^## ANEXA Nr\. (?P<number>\d+(?:\^\d+)?)$"
)
ADMINISTRATIVE_INSERTED_ARTICLES = (
    "91^1",
    "91^2",
    "91^3",
    "91^4",
    "91^5",
    "91^6",
    "292^1",
    "292^2",
    "292^3",
    "300^1",
    "364^1",
    "374^1",
    "398^1",
    "411^1",
    "465^1",
    "467^1",
    "485^1",
    "494^1",
    "534^1",
    "534^2",
    "610^1",
)

ROAD_SOURCE = ROOT / "codul_rutier.md"
ROAD_LEGACY_TEXT_SOURCES = (ROOT / "cod_rutier.txt", ROOT / "codul_rutier.txt")
ROAD_LEGACY_SOURCE = ROOT / "cod_rutier.pdf"
ROAD_CHAPTER = re.compile(
    r"^Capitolul\s+(?P<number>[IVXLCDM]+)\s*[\u2013-]\s*(?P<title>.*)$",
    re.IGNORECASE,
)
ROAD_SECTION = re.compile(
    r"^(?P<label>SEC[\u0162\u0163\u021a\u021bT]IUNEA\s+(?:a\s+)?\d+(?:-a)?)"
    r"\s*(?P<title>.*)$",
    re.IGNORECASE,
)
ROAD_ANNEX = re.compile(
    r"^ANEXA\s+(?P<number>\d+)\s*[\u2013-]\s*(?P<title>.*)$",
    re.IGNORECASE,
)
ROAD_ARTICLE = re.compile(
    r"^Art\.\s*(?P<number>\d+(?:\.\d+)*)\.?\s*(?P<body>.*)$"
)
ROAD_MARKDOWN_ARTICLE = re.compile(
    r"(?m)^#### Articolul (?P<number>\d+(?:\^\d+)?)$"
)
ROAD_MARKDOWN_ANNEX = re.compile(r"(?m)^## ANEXA (?P<number>\d+)(?:\s|$)")
ROAD_INSERTED_ARTICLES = (
    "11^1",
    "11^2",
    "11^3",
    "11^4",
    "11^5",
    "11^6",
    "11^7",
    "22^1",
    "22^2",
    "23^1",
    "24^1",
    "28^1",
    "54^1",
    "64^1",
    "80^1",
    "80^2",
    "104^1",
    "106^1",
    "106^2",
    "109^1",
    "109^2",
    "109^3",
    "114^1",
    "120^1",
    "133^1",
)

PENAL_SOURCE = ROOT / "codul_penal.md"
PENAL_LEGACY_TEXT_SOURCES = (ROOT / "cod_penal.txt", ROOT / "codul_penal.txt")
PENAL_LEGACY_SOURCE = ROOT / "cod_penal.pdf"
PENAL_PART = re.compile(r"^PARTEA\s+.+$")
PENAL_TITLE = re.compile(r"^TITLUL\s+[IVXLCDM]+$")
PENAL_CHAPTER = re.compile(
    r"^(?P<label>CAPITOLUL\s+[IVXLCDM]+)\s*(?P<title>.*)$"
)
PENAL_SECTION = re.compile(
    r"^(?P<label>Sec[\u0162\u0163\u021a\u021bT]iunea\s+(?:a\s+)?\d+(?:-a)?)"
    r"\s*(?P<title>.*)$",
    re.IGNORECASE,
)
PENAL_ARTICLE = re.compile(
    r"^Art\.\s*(?P<number>\d+)\.?\s*(?P<title>.+)$"
)
PENAL_MARKDOWN_ARTICLE = re.compile(
    r"(?m)^###### Articolul (?P<number>\d+) — .+$"
)

CONSTITUTION_SOURCE = ROOT / "constitutia_romaniei.md"
CONSTITUTION_LEGACY_TEXT_SOURCES = (
    ROOT / "constitutie.txt",
    ROOT / "constitutia_romaniei.txt",
)
CONSTITUTION_LEGACY_SOURCE = ROOT / "constitutia_romaniei.pdf"
CONSTITUTION_TITLE = re.compile(
    r"^(?P<label>TITLUL\s+[IVXLCDM]+)\s*[\u2013-]\s*(?P<title>.+)$"
)
CONSTITUTION_CHAPTER = re.compile(
    r"^(?P<label>CAPITOLUL\s+[IVXLCDM]+)\s*[\u2013-]\s*(?P<title>.+)$"
)
CONSTITUTION_SECTION = re.compile(
    r"^(?P<label>SEC[\u0162\u0163\u021a\u021bT]IUNEA\s+(?:a\s+)?\d+(?:-a)?)"
    r"\s*[\u2013-]\s*(?P<title>.+)$",
    re.IGNORECASE,
)
CONSTITUTION_ARTICLE = re.compile(
    r"^Art\.\s*(?P<number>\d+)\s*[\u2013-]\s*(?P<title>.+)$"
)
CONSTITUTION_MARKDOWN_ARTICLE = re.compile(
    r"(?m)^##### Articolul (?P<number>\d+) — .+$"
)

PROCEDURE_CIVIL_SOURCE = ROOT / "codul_de_procedura_civila.md"
PROCEDURE_CIVIL_LEGACY_TEXT_SOURCES = (
    ROOT / "procedura_civila.txt",
    ROOT / "cod_procedura_civila.txt",
)
PROCEDURE_CIVIL_LEGACY_SOURCE = ROOT / "cod_procedura_civila.pdf"
PROCEDURE_CIVIL_FOOTER = re.compile(
    r"(?m)^Codul de Procedura Civila din 2010 - forma sintetica pentru data "
    r"2020-05-25\n?"
    r"|^pag\.\s*\d+\s+5/25/2020\s*:\s*lex@snppc\.ro\n?"
)
PROCEDURE_CIVIL_BOOK = re.compile(
    r"^(?P<label>CARTEA\s+[IVXLCDM]+):\s*(?P<title>.*)$"
)
PROCEDURE_CIVIL_TITLE = re.compile(
    r"^(?P<label>TITLUL\s+(?:PRELIMINAR|[IVXLCDM]+)):\s*(?P<title>.*)$"
)
PROCEDURE_CIVIL_CHAPTER = re.compile(
    r"^(?P<label>CAPITOLUL\s+(?:[IVXLCDM]+|0))"
    r"(?::\s*|\s+)(?P<title>.*?)(?::)?$"
)
PROCEDURE_CIVIL_SECTION = re.compile(
    r"^(?P<label>SEC[\u0162\u0163\u021a\u021bT]IUNEA\s+"
    r"(?:\d+|a\s+\d+-a)):\s*(?P<title>.*)$",
    re.IGNORECASE,
)
PROCEDURE_CIVIL_SUBSECTION = re.compile(
    r"^(?P<label>SUBSEC[\u0162\u0163\u021a\u021bT]IUNEA\s+\d+)"
    r"(?::\s*(?P<title>.*))?$",
    re.IGNORECASE,
)
PROCEDURE_CIVIL_ARTICLE = re.compile(
    r"^Art\.\s*(?P<number>\d+(?:\^\d+)?)\s*:\s*(?P<title>.*)$"
)
PROCEDURE_CIVIL_MARKDOWN_ARTICLE = re.compile(
    r"(?m)^###### Articolul (?P<number>\d+(?:\^\d+)?)"
    r"(?: — .+)?$"
)
PROCEDURE_CIVIL_EXTRACT_ARTICLE = re.compile(
    r"^- Art\.\s*(?P<number>[IVXLCDM]+|\d+)(?:\s|$)"
)

FISCAL_SOURCE = ROOT / "codul_fiscal.md"
FISCAL_LEGACY_TEXT_SOURCES = (ROOT / "cod_fiscal.txt", ROOT / "codul_fiscal.txt")
FISCAL_TITLE = re.compile(
    r"^(?P<label>TITLUL\s+(?P<roman>[IVXLCDM]+)(?P<inserted>\d+)?)"
    r"(?:\s*-\s*(?P<title>.*))?$"
)
FISCAL_CHAPTER = re.compile(
    r"^(?P<label>CAPITOLUL\s+[^-]+?)(?:\s*-\s*(?P<title>.*))?$"
)
FISCAL_SECTION = re.compile(
    r"^(?P<label>SEC[\u0162\u0163\u021a\u021bT]IUNEA\s+[^-]+?)"
    r"(?:\s*-\s*(?P<title>.*))?$",
)
FISCAL_SUBSECTION = re.compile(
    r"^(?P<label>SUBSEC[\u0162\u0163\u021a\u021bT]IUNEA\s+[^-]+?)"
    r"(?:\s*-\s*(?P<title>.*))?$",
)
FISCAL_ARTICLE = re.compile(
    r"^ART\.\s*(?P<raw_number>\d+)\s*(?:\*)?\s*"
    r"(?:-\s*(?P<title>.*))?$"
)
FISCAL_MARKDOWN_ARTICLE = re.compile(
    r"(?m)^###### Articolul (?P<number>\d+(?:\^\d+)?)"
    r"(?: \u2014 .+)?$"
)
FISCAL_ANNEX = re.compile(r"^ANEXA\s+(?P<label>.+)$")

PROCEDURE_FISCAL_SOURCE = ROOT / "codul_de_procedura_fiscala.md"
PROCEDURE_FISCAL_LEGACY_TEXT_SOURCES = (
    ROOT / "procedura_fiscala.txt",
    ROOT / "cod_procedura_fiscala.txt",
)
PROCEDURE_FISCAL_TITLE = re.compile(
    r"^(?P<label>TITLUL\s+[IVXLCDM]+)\s+(?P<title>.+)$"
)
PROCEDURE_FISCAL_CHAPTER = re.compile(
    r"^(?P<label>CAPITOLUL\s+(?P<roman>[IVXLCDM]+)"
    r"(?P<inserted>\d+)?)"
    r"(?:\s+(?P<title>.+))?$"
)
PROCEDURE_FISCAL_SECTION = re.compile(
    r"^(?P<label>(?:SEC[\u0162\u0163\u021a\u021bT]IUNEA|"
    r"Sec[\u0162\u0163\u021a\u021bT]iunea)\s+"
    r"(?:(?:a\s+)?(?:\d+|[IVXLCDM]+)(?:-a)?))"
    r"(?:\s*-?\s*(?P<title>.*))?$"
)
PROCEDURE_FISCAL_ARTICLE = re.compile(
    r"^ART\.\s*(?P<raw_number>\d+(?:\s+\d+)?)\s*(?:\*)?\s*"
    r"(?P<title>.*)$"
)
PROCEDURE_FISCAL_MARKDOWN_ARTICLE = re.compile(
    r"(?m)^###### Articolul (?P<number>\d+(?:\^\d+)?)"
    r"(?: \u2014 .+)?$"
)
PROCEDURE_FISCAL_ANNEX = re.compile(
    r"^ANEXA\s+(?P<number>\d+)\s*(?:-\s*(?P<title>.*))?$"
)
PROCEDURE_FISCAL_PART = re.compile(
    r"^(?P<label>Partea\s+(?:a\s+)?[IVXLCDM]+(?:-a)?)$"
)

OUG34_SOURCE = ROOT / "oug_34_2014.md"
OUG34_LEGACY_TEXT_SOURCES = (
    ROOT / "oug34_2014.txt",
    ROOT / "oug_34_2014.txt",
)
OUG34_CHAPTER = re.compile(r"^CAPITOLUL\s+(?P<number>[IVXLCDM]+)$")
OUG34_ARTICLE = re.compile(r"^ARTICOLUL\s+(?P<number>\d+)$")
OUG34_MARKDOWN_ARTICLE = re.compile(
    r"(?m)^### Articolul (?P<number>\d+)(?: — .+)?$"
)

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
        109,
        "legea civilă, aplicarea și interpretarea ei, publicitatea "
        "drepturilor, persoana fizică, capacitatea, drepturile personalității "
        "și starea civilă",
    ),
    CivilChunk(
        110,
        204,
        "ocrotirea persoanei fizice, tutela minorului, consiliul de familie, "
        "curatela și înființarea persoanei juridice",
    ),
    CivilChunk(
        205,
        289,
        "capacitatea, organele, reorganizarea și încetarea persoanei "
        "juridice; apărarea drepturilor nepatrimoniale, familia, logodna și "
        "începutul căsătoriei",
    ),
    CivilChunk(
        290,
        384,
        "încheierea și nulitatea căsătoriei, drepturile soților, regimurile "
        "matrimoniale și începutul divorțului",
    ),
    CivilChunk(
        385,
        486,
        "divorțul și efectele sale, rudenia, filiația, reproducerea asistată "
        "medical și adopția",
    ),
    CivilChunk(
        487,
        586,
        "încetarea adopției, autoritatea părintească, obligația de "
        "întreținere, bunurile și începutul proprietății private",
    ),
    CivilChunk(
        587,
        686,
        "accesiunea, limitele proprietății private, proprietatea comună, "
        "coproprietatea, condominiul și partajul",
    ),
    CivilChunk(
        687,
        791,
        "proprietatea periodică, superficia, uzufructul, uzul, abitația, "
        "servituțile și începutul fiduciei",
    ),
    CivilChunk(
        792,
        884,
        "fiducia și administrarea bunurilor altuia",
    ),
    CivilChunk(
        885,
        956,
        "proprietatea publică, cartea funciară, înscrierea și rectificarea "
        "drepturilor tabulare și începutul posesiei",
    ),
    CivilChunk(
        957,
        1050,
        "dobândirea proprietății prin posesie, acțiunile posesorii, "
        "deschiderea moștenirii, moștenirea legală și începutul "
        "liberalităților",
    ),
    CivilChunk(
        1051,
        1140,
        "donațiile, testamentele, legatele, dezmoștenirea, rezerva "
        "succesorală și reducțiunea liberalităților",
    ),
    CivilChunk(
        1141,
        1249,
        "opțiunea succesorală, moștenirea vacantă, partajul succesoral, "
        "raportul donațiilor și începutul obligațiilor",
    ),
    CivilChunk(
        1250,
        1371,
        "formarea și validitatea contractului, consimțământul, obiectul, "
        "cauza, forma, nulitatea, interpretarea și efectele contractului",
    ),
    CivilChunk(
        1372,
        1479,
        "reprezentarea, cesiunea contractului, actul juridic unilateral, "
        "faptul juridic licit, răspunderea civilă și condiția",
    ),
    CivilChunk(
        1480,
        1586,
        "termenul, obligațiile complexe, plata, punerea în întârziere și "
        "începutul executării silite",
    ),
    CivilChunk(
        1587,
        1670,
        "executarea silită, daunele-interese, rezoluțiunea, măsurile "
        "conservatorii, cesiunea de creanță și stingerea obligațiilor",
    ),
    CivilChunk(
        1671,
        1771,
        "contractul de vânzare: obligațiile părților, garanțiile și "
        "varietățile vânzării; schimbul",
    ),
    CivilChunk(
        1772,
        1873,
        "furnizarea, reportul, locațiunea, închirierea locuințelor, arendarea "
        "și începutul antreprizei",
    ),
    CivilChunk(
        1874,
        1954,
        "contractul de antrepriză și contractul de societate",
    ),
    CivilChunk(
        1955,
        2038,
        "contractul de societate, asocierea în participație și contractul "
        "de transport",
    ),
    CivilChunk(
        2039,
        2126,
        "contractul de mandat, mandatul fără reprezentare și contractul de "
        "agenție",
    ),
    CivilChunk(
        2127,
        2226,
        "intermedierea, depozitul, împrumutul, contul curent, contul bancar "
        "și începutul asigurării",
    ),
    CivilChunk(
        2227,
        2342,
        "asigurarea, renta viageră, întreținerea, jocul și pariul, tranzacția "
        "și începutul garanțiilor personale",
    ),
    CivilChunk(
        2343,
        2463,
        "fideiusiunea, garanțiile autonome, privilegiile și ipoteca "
        "imobiliară și mobiliară",
    ),
    CivilChunk(
        2464,
        2556,
        "rangul și executarea ipotecilor, gajul, dreptul de retenție și "
        "începutul prescripției extinctive",
    ),
    CivilChunk(
        2557,
        2664,
        "dreptul internațional privat privind persoanele, familia, bunurile, "
        "moștenirea, obligațiile, titlurile de credit, fiducia și prescripția; "
        "dispoziții finale",
    ),
)


@dataclass(frozen=True)
class AdministrativeChunk:
    filename: str
    range_label: str
    description: str
    first_article: str | None = None
    last_article: str | None = None


ADMINISTRATIVE_CHUNKS = (
    AdministrativeChunk(
        "codul_administrativ-art001-054.md",
        "Art. 1-54",
        "dispoziții generale, definiții și principii; Guvernul, organizarea "
        "ministerelor și începutul administrației publice centrale de specialitate",
        "1",
        "54",
    ),
    AdministrativeChunk(
        "codul_administrativ-art055-083.md",
        "Art. 55-83",
        "miniștrii, organizarea ministerelor, celelalte organe centrale și "
        "autoritățile administrative autonome; descentralizarea",
        "55",
        "83",
    ),
    AdministrativeChunk(
        "codul_administrativ-art084-094.md",
        "Art. 84-94, inclusiv art. 91^1-91^6",
        "principiile și regimul general al autonomiei locale, raporturile dintre "
        "autorități și folosirea limbii minorităților naționale",
        "84",
        "94",
    ),
    AdministrativeChunk(
        "codul_administrativ-art095-127.md",
        "Art. 95-127",
        "unitățile administrativ-teritoriale, competențele autorităților locale, "
        "constituirea și organizarea consiliului local",
        "95",
        "127",
    ),
    AdministrativeChunk(
        "codul_administrativ-art128-147.md",
        "Art. 128-147",
        "mandatul și atribuțiile consiliului local, ședințele și adoptarea "
        "hotărârilor, delegatul sătesc și dizolvarea consiliului",
        "128",
        "147",
    ),
    AdministrativeChunk(
        "codul_administrativ-art148-176.md",
        "Art. 148-176",
        "primarul și viceprimarul, administrația municipiului București și "
        "începutul reglementării consiliului județean",
        "148",
        "176",
    ),
    AdministrativeChunk(
        "codul_administrativ-art177-205.md",
        "Art. 177-205",
        "funcționarea și actele consiliului județean, președintele și "
        "vicepreședinții acestuia, actele autorităților locale și începutul "
        "regimului aleșilor locali",
        "177",
        "205",
    ),
    AdministrativeChunk(
        "codul_administrativ-art206-243.md",
        "Art. 206-243",
        "mandatul, drepturile, obligațiile, incompatibilitățile, conflictele de "
        "interese și răspunderea aleșilor locali; secretarul general al unității "
        "administrativ-teritoriale",
        "206",
        "243",
    ),
    AdministrativeChunk(
        "codul_administrativ-art244-283.md",
        "Art. 244-283",
        "administratorul public, inițiativa și adunările cetățenești, instituția "
        "prefectului și serviciile publice deconcentrate",
        "244",
        "283",
    ),
    AdministrativeChunk(
        "codul_administrativ-art284-301.md",
        "Art. 284-301, inclusiv art. 292^1-292^3 și 300^1",
        "domeniul public, inventarierea și transferul bunurilor și modalitățile "
        "de exercitare a dreptului de proprietate publică",
        "284",
        "301",
    ),
    AdministrativeChunk(
        "codul_administrativ-art302-331.md",
        "Art. 302-331",
        "concesionarea bunurilor proprietate publică: inițierea, documentația, "
        "licitația, atribuirea și contractul de concesiune",
        "302",
        "331",
    ),
    AdministrativeChunk(
        "codul_administrativ-art332-364bis.md",
        "Art. 332-364^1",
        "încetarea concesiunii, închirierea și folosința gratuită a bunurilor "
        "publice și proprietatea privată a statului și a unităților "
        "administrativ-teritoriale",
        "332",
        "364^1",
    ),
    AdministrativeChunk(
        "codul_administrativ-art365-399.md",
        "Art. 365-399, inclusiv art. 374^1 și 398^1",
        "principiile și clasificarea funcțiilor publice, categoriile de "
        "funcționari, înalții funcționari publici, ocuparea funcțiilor și evaluarea",
        "365",
        "399",
    ),
    AdministrativeChunk(
        "codul_administrativ-art400-429.md",
        "Art. 400-429, inclusiv art. 411^1",
        "managementul funcției publice, gestiunea resurselor umane și a "
        "posturilor și drepturile funcționarilor publici",
        "400",
        "429",
    ),
    AdministrativeChunk(
        "codul_administrativ-art430-463.md",
        "Art. 430-463",
        "îndatoririle și conduita funcționarilor publici, consilierea etică, "
        "formarea profesională, incompatibilitățile și conflictele de interese",
        "430",
        "463",
    ),
    AdministrativeChunk(
        "codul_administrativ-art464-489.md",
        "Art. 464-489, inclusiv art. 465^1, 467^1 și 485^1",
        "dobândirea calității și cariera funcționarilor publici, recrutarea, "
        "numirea, promovarea, evaluarea, acordurile colective și comisiile paritare",
        "464",
        "489",
    ),
    AdministrativeChunk(
        "codul_administrativ-art490-511.md",
        "Art. 490-511, inclusiv art. 494^1",
        "răspunderea disciplinară și sancțiunile; modificarea raportului de "
        "serviciu, mobilitatea, delegarea, detașarea și exercitarea temporară",
        "490",
        "511",
    ),
    AdministrativeChunk(
        "codul_administrativ-art512-537.md",
        "Art. 512-537, inclusiv art. 534^1 și 534^2",
        "suspendarea și încetarea raporturilor de serviciu, corpul de rezervă, "
        "actele administrative privind cariera și contravențiile",
        "512",
        "537",
    ),
    AdministrativeChunk(
        "codul_administrativ-art538-596.md",
        "Art. 538-596",
        "personalul contractual, cabinetele demnitarilor, răspunderea "
        "administrativă și administrativ-patrimonială și regimul serviciilor publice",
        "538",
        "596",
    ),
    AdministrativeChunk(
        "codul_administrativ-art597-638.md",
        "Art. 597-638, inclusiv art. 610^1",
        "dispoziții tranzitorii și finale, termene și măsuri de aplicare, "
        "modificarea altor acte normative și abrogări",
        "597",
        "638",
    ),
    AdministrativeChunk(
        "codul_administrativ-anexe01-05bis.md",
        "Anexele nr. 1-5 și 5^1",
        "Monitorul Oficial Local, listele bunurilor din domeniul public, funcțiile "
        "publice și echivalarea funcțiilor publice specifice cu cele generale",
    ),
    AdministrativeChunk(
        "codul_administrativ-anexa06-part1.md",
        "Anexa nr. 6, partea 1",
        "metodologia evaluării funcționarilor publici: dispoziții generale și "
        "evaluarea înalților funcționari publici",
    ),
    AdministrativeChunk(
        "codul_administrativ-anexa06-part2.md",
        "Anexa nr. 6, partea 2",
        "evaluarea performanțelor funcționarilor publici și a activității "
        "funcționarilor publici debutanți, plus criteriile și formularele aferente",
    ),
    AdministrativeChunk(
        "codul_administrativ-anexa07-part1.md",
        "Anexa nr. 7, partea 1",
        "constituirea, componența, organizarea, funcționarea și atribuțiile "
        "comisiilor de disciplină",
    ),
    AdministrativeChunk(
        "codul_administrativ-anexe07-part2-10.md",
        "Anexa nr. 7, partea 2; anexele nr. 8-10",
        "procedura disciplinară; cadrele de competențe, proiectul-pilot pentru "
        "concursuri și normele privind organizarea și dezvoltarea carierei",
    ),
)


@dataclass(frozen=True)
class RoadChunk:
    first_article: str
    last_article: str
    description: str
    includes_annex: bool = False

    @property
    def filename(self) -> str:
        def filename_label(article: str) -> str:
            base, *inserted = article.split("^", 1)
            suffix = f"bis{inserted[0]}" if inserted else ""
            return f"{int(base):03d}{suffix}"

        return (
            f"cod_rutier-art{filename_label(self.first_article)}-"
            f"{filename_label(self.last_article)}.md"
        )

    @property
    def range_label(self) -> str:
        label = f"Art. {self.first_article}-{self.last_article}"
        if self.includes_annex:
            label += "; anexa nr. 1"
        return label


ROAD_CHUNKS = (
    RoadChunk(
        "1",
        "11^7",
        "dispoziții generale, condițiile tehnice pentru circulația vehiculelor, "
        "înmatricularea și înregistrarea, inclusiv serviciile electronice aferente",
    ),
    RoadChunk(
        "12",
        "28^1",
        "înmatricularea, înregistrarea și radierea vehiculelor; condițiile pentru "
        "conducători, permisul de conducere, examinarea și recunoașterea permiselor",
    ),
    RoadChunk(
        "29",
        "73",
        "semnalizarea rutieră, obligațiile participanților la trafic, regulile "
        "pentru vehicule și regulile aplicabile celorlalți participanți",
    ),
    RoadChunk(
        "74",
        "102",
        "circulația pe autostrăzi și drumuri expres, accidentele, traficul "
        "internațional, infracțiunile și clasele de contravenții",
    ),
    RoadChunk(
        "103",
        "110",
        "punctele-amendă și de penalizare, suspendarea dreptului de a conduce, "
        "testarea, reducerea suspendării și măsurile tehnico-administrative",
    ),
    RoadChunk(
        "111",
        "137",
        "reținerea și restituirea documentelor, retragerea permisului, "
        "imobilizarea și confiscarea, căile de atac, atribuțiile autorităților, "
        "dispozițiile finale și categoriile de permis",
        True,
    ),
)


@dataclass(frozen=True)
class PenalChunk:
    first_article: int
    last_article: int
    description: str

    @property
    def filename(self) -> str:
        return (
            f"cod_penal-art{self.first_article:03d}-"
            f"{self.last_article:03d}.md"
        )

    @property
    def range_label(self) -> str:
        return f"Art. {self.first_article}-{self.last_article}"


PENAL_CHUNKS = (
    PenalChunk(
        1,
        73,
        "principiile și aplicarea legii penale, infracțiunea, cauzele "
        "justificative și de neimputabilitate, tentativa, pluralitatea, "
        "participanții și categoriile și calculul pedepselor",
    ),
    PenalChunk(
        74,
        124,
        "individualizarea pedepselor, circumstanțele, renunțarea, amânarea și "
        "suspendarea, liberarea condiționată, măsurile de siguranță și măsurile "
        "educative neprivative de libertate",
    ),
    PenalChunk(
        125,
        196,
        "măsurile educative privative de libertate, răspunderea persoanei "
        "juridice, cauzele care înlătură răspunderea, executarea sau consecințele "
        "condamnării, termenii legali și infracțiunile contra vieții și integrității",
    ),
    PenalChunk(
        197,
        263,
        "infracțiunile asupra unui membru de familie, contra libertății, libertății "
        "sexuale și vieții private, contra patrimoniului, autorității și frontierei",
    ),
    PenalChunk(
        264,
        345,
        "infracțiunile contra înfăptuirii justiției, de corupție și de serviciu, "
        "împotriva intereselor financiare europene, falsurile și infracțiunile "
        "privind siguranța feroviară, rutieră și regimul armelor",
    ),
    PenalChunk(
        346,
        437,
        "infracțiunile privind explozivii, activitățile reglementate, sănătatea și "
        "ordinea publică, familia, libertatea religioasă, alegerile, securitatea "
        "națională, capacitatea de luptă, genocidul și crimele de război; "
        "dispoziția finală",
    ),
)


@dataclass(frozen=True)
class ConstitutionChunk:
    first_article: int
    last_article: int
    description: str

    @property
    def filename(self) -> str:
        return (
            f"constitutia_romaniei-art{self.first_article:03d}-"
            f"{self.last_article:03d}.md"
        )

    @property
    def range_label(self) -> str:
        return f"Art. {self.first_article}-{self.last_article}"


CONSTITUTION_CHUNKS = (
    ConstitutionChunk(
        1,
        79,
        "principiile generale, drepturile, libertățile și îndatoririle "
        "fundamentale, Avocatul Poporului și organizarea, statutul membrilor și "
        "legiferarea în Parlament",
    ),
    ConstitutionChunk(
        80,
        156,
        "Președintele României, Guvernul, raporturile cu Parlamentul, "
        "administrația publică, autoritatea judecătorească, economia și finanțele, "
        "Curtea Constituțională, integrarea euroatlantică, revizuirea și "
        "dispozițiile finale",
    ),
)


@dataclass(frozen=True)
class ProcedureCivilChunk:
    first_article: int
    last_article: int
    description: str
    includes_application_extracts: bool = False

    @property
    def filename(self) -> str:
        return (
            f"cod_procedura_civila-art{self.first_article:04d}-"
            f"{self.last_article:04d}.md"
        )

    @property
    def range_label(self) -> str:
        def display(article: int) -> str:
            return f"{article:,}".replace(",", ".")

        label = f"Art. {display(self.first_article)}-{display(self.last_article)}"
        if self.first_article <= 471 <= self.last_article:
            label += ", inclusiv art. 471^1"
        if self.includes_application_extracts:
            label += "; extrase de aplicare și tranziție"
        return label


PROCEDURE_CIVIL_CHUNKS = (
    ProcedureCivilChunk(
        1,
        79,
        "domeniul și principiile procesului civil, aplicarea legii procesuale, "
        "acțiunea civilă, incompatibilitatea judecătorului și începutul regimului "
        "părților",
    ),
    ProcedureCivilChunk(
        80,
        139,
        "intervenția și reprezentarea părților, asistența judiciară, participarea "
        "Ministerului Public și competența materială și teritorială",
    ),
    ProcedureCivilChunk(
        140,
        186,
        "competența teritorială specială, necompetența, conflictele, "
        "litispendența, conexitatea, strămutarea și actele de procedură",
    ),
    ProcedureCivilChunk(
        187,
        236,
        "citarea și comunicarea actelor, nulitatea, termenele, amenzile judiciare "
        "și sesizarea și pregătirea judecății în primă instanță",
    ),
    ProcedureCivilChunk(
        237,
        309,
        "judecata în primă instanță, cercetarea procesului, excepțiile și regulile "
        "generale privind probele și înscrisurile",
    ),
    ProcedureCivilChunk(
        310,
        394,
        "înscrisurile, martorii, prezumțiile, expertiza, cercetarea la fața "
        "locului, interogatoriul, asigurarea probelor și dezbaterea fondului",
    ),
    ProcedureCivilChunk(
        395,
        465,
        "deliberarea, incidentele procedurale, hotărârile judecătorești, "
        "executarea provizorie, cheltuielile de judecată și regulile generale "
        "privind căile de atac",
    ),
    ProcedureCivilChunk(
        466,
        513,
        "apelul, recursul, contestația în anulare și începutul revizuirii",
    ),
    ProcedureCivilChunk(
        514,
        574,
        "revizuirea, unificarea practicii judiciare, contestația privind "
        "tergiversarea, procedura necontencioasă și începutul arbitrajului",
    ),
    ProcedureCivilChunk(
        575,
        643,
        "procedura și hotărârea arbitrală, arbitrajul instituționalizat și "
        "începutul executării silite, inclusiv scopul și titlurile executorii",
    ),
    ProcedureCivilChunk(
        644,
        689,
        "titlurile executorii, participanții, instanța de executare, "
        "încuviințarea și efectuarea actelor de executare silită",
    ),
    ProcedureCivilChunk(
        690,
        730,
        "executarea împotriva moștenitorilor, intervenția creditorilor, "
        "perimarea, suspendarea și încetarea executării, prescripția și "
        "contestația la executare",
    ),
    ProcedureCivilChunk(
        731,
        780,
        "urmărirea bunurilor mobile, sechestrarea, valorificarea și vânzarea "
        "bunurilor urmărite",
    ),
    ProcedureCivilChunk(
        781,
        828,
        "poprirea, urmărirea fructelor și veniturilor imobilelor și începutul "
        "urmăririi imobiliare",
    ),
    ProcedureCivilChunk(
        829,
        878,
        "vânzarea imobilelor la licitație, adjudecarea și distribuirea sumelor "
        "rezultate din urmărirea silită",
    ),
    ProcedureCivilChunk(
        879,
        951,
        "distribuirea sumelor, executarea silită directă, predarea bunurilor și "
        "minorilor și începutul procedurilor speciale, inclusiv divorțul",
    ),
    ProcedureCivilChunk(
        952,
        1025,
        "declararea morții, măsurile asigurătorii și provizorii, partajul, "
        "ordonanța președințială, cererile posesorii, oferta și ordonanța de plată",
    ),
    ProcedureCivilChunk(
        1026,
        1082,
        "ordonanța de plată, cererile cu valoare redusă, evacuarea, uzucapiunea, "
        "refacerea dosarelor, cauțiunea și începutul procesului civil internațional",
    ),
    ProcedureCivilChunk(
        1083,
        1134,
        "legea aplicabilă procesului civil internațional, recunoașterea și "
        "executarea hotărârilor străine, arbitrajul internațional și dispozițiile "
        "finale și tranzitorii",
        True,
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
    """Remove standalone source page numbers and normalize a split article label."""
    text = text.removeprefix("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(
        r"(?m)^(Art\.\s*[\d. ]+\.)\s*\n\s*([\u2013-])",
        r"\1 \2",
        text,
    )
    lines = [
        line for line in text.splitlines() if not re.fullmatch(r"\s*\d{1,3}\s*", line)
    ]
    try:
        preliminary_title = lines.index("TITLUL PRELIMINAR")
    except ValueError as error:
        raise RuntimeError("Could not locate the start of Codul civil") from error

    preamble = [
        "Codul civil",
        "Legea nr. 287/2009",
        "Forma adoptată la 25 iunie 2009",
    ]
    return "\n".join(preamble + lines[preliminary_title:]).rstrip() + "\n"


def format_civil_markdown(text: str) -> str:
    """Apply Markdown levels to the hierarchy found in Codul civil."""
    if text.startswith("# Codul civil\n"):
        return normalize_heading_spacing(text)

    lines = text.splitlines()
    if not lines or lines[0] != "Codul civil":
        raise RuntimeError("Unexpected Codul civil document heading")

    rendered = ["# Codul civil"]
    for line in lines[1:]:
        structure = CIVIL_STRUCTURE.fullmatch(line)
        if structure:
            if structure.group("book"):
                level = 2
            elif structure.group("title"):
                level = 3
            elif structure.group("chapter"):
                level = 4
            else:
                level = 5
            rendered.append(f"{'#' * level} {line}")
        elif CIVIL_PARAGRAPH.fullmatch(line):
            rendered.append(f"##### {line}")
        else:
            article = CIVIL_INLINE_ARTICLE.search(line)
            if not article:
                rendered.append(line)
                continue

            rubric = line[: article.start()].rstrip()
            body = line[article.end() :].lstrip()
            number = civil_article_number(article.group("number"))
            if rubric:
                rendered.append(rubric)
            rendered.append(f"###### Art. {format_civil_article(number)}")
            if body:
                rendered.append(body)

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
    return int(label.replace(".", "").replace(" ", ""))


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
            "- Codul civil (Legea nr. 287/2009, forma adoptată la 25 iunie "
            f"2009) — {chunk.description}. {civil_range_label(chunk)}.\n"
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


def clean_administrative_source(text: str) -> str:
    """Normalize extraction artifacts without discarding substantive lines."""
    text = text.removeprefix("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("Error! Hyperlink reference not valid.", "")
    text = re.sub(r"(ARTICOLUL\s+534)\n(2\s+)", r"\1\2", text)
    return text.rstrip() + "\n"


def administrative_structure(line: str) -> tuple[int, str] | None:
    if ADMINISTRATIVE_PART.fullmatch(line):
        return 2, line
    if ADMINISTRATIVE_TITLE.fullmatch(line):
        return 3, line
    if ADMINISTRATIVE_CHAPTER.fullmatch(line):
        return 4, line
    if ADMINISTRATIVE_SECTION.fullmatch(line):
        return 5, line
    return None


def administrative_inserted_label(raw_number: str, current_article: int) -> str:
    current = str(current_article)
    if not raw_number.startswith(current) or len(raw_number) == len(current):
        raise RuntimeError(
            f"Unexpected article {raw_number} after article {current_article}"
        )
    return f"{current_article}^{raw_number[len(current):]}"


def format_administrative_markdown(text: str) -> str:
    """Render parts, titles, chapters, sections, articles and annexes as headings."""
    if text.startswith("# Codul administrativ\n"):
        return normalize_heading_spacing(text)

    lines = text.splitlines()
    try:
        first_part = next(
            index
            for index, line in enumerate(lines)
            if ADMINISTRATIVE_PART.fullmatch(line.strip())
        )
    except StopIteration as error:
        raise RuntimeError("Could not locate the start of Codul administrativ") from error

    rendered = ["# Codul administrativ"]
    rendered.extend(line.strip() for line in lines[:first_part] if line.strip())
    current_article = 0
    annex_mode = False
    index = first_part

    while index < len(lines):
        raw_line = lines[index].rstrip()
        line = raw_line.strip()
        annex = ADMINISTRATIVE_ANNEX.fullmatch(line)
        if current_article == 638 and annex:
            annex_mode = True
            raw_number = annex.group("number")
            number = "5^1" if raw_number == "51" else raw_number
            rendered.append(f"## ANEXA Nr. {number}")
            if annex.group("note"):
                rendered.append(annex.group("note"))
            index += 1
            continue

        if not annex_mode:
            article = ADMINISTRATIVE_ARTICLE.fullmatch(line)
            if article:
                raw_number = article.group("number")
                numeric_number = int(raw_number)
                if numeric_number == current_article + 1:
                    current_article = numeric_number
                    number = raw_number
                else:
                    number = administrative_inserted_label(
                        raw_number, current_article
                    )
                rendered.append(f"###### Articolul {number}")
                if article.group("body"):
                    rendered.append(article.group("body"))
                index += 1
                continue

            special_article = ADMINISTRATIVE_SPECIAL_ARTICLE.fullmatch(line)
            if special_article:
                numeric_number = int(special_article.group("number"))
                if numeric_number != current_article + 1:
                    raise RuntimeError(
                        f"Unexpected article {numeric_number} after "
                        f"article {current_article}"
                    )
                current_article = numeric_number
                rendered.append(f"###### Articolul {numeric_number}")
                if special_article.group("body"):
                    rendered.append(special_article.group("body"))
                index += 1
                continue
        else:
            annex_article = re.fullmatch(
                r"Art\.\s*(\d+)\.\s*[\u2013-]\s*(.*)", line
            )
            if annex_article:
                rendered.append(f"###### Articol anexă {annex_article.group(1)}")
                if annex_article.group(2):
                    rendered.append(annex_article.group(2))
                index += 1
                continue

        structure = administrative_structure(line)
        if structure:
            level, label = structure
            subtitle = ""
            if index + 1 < len(lines):
                candidate = lines[index + 1].strip()
                is_amendment = re.match(r"^\d{2}/\d{2}/\d{4}\s+-", candidate)
                if (
                    candidate
                    and not administrative_structure(candidate)
                    and not ADMINISTRATIVE_ARTICLE.fullmatch(candidate)
                    and not ADMINISTRATIVE_SPECIAL_ARTICLE.fullmatch(candidate)
                    and not ADMINISTRATIVE_ANNEX.fullmatch(candidate)
                    and not is_amendment
                ):
                    subtitle = candidate
                    index += 1
            suffix = f" — {subtitle}" if subtitle else ""
            rendered.append(f"{'#' * level} {label}{suffix}")
        else:
            rendered.append(raw_line)
        index += 1

    if current_article != 638:
        raise RuntimeError(
            f"Administrative Code ended at article {current_article}, expected 638"
        )
    return normalize_heading_spacing("\n".join(rendered))


def administrative_chunk_boundaries(markdown: str) -> list[int]:
    headings = [
        (match.start(), len(match.group(1)))
        for match in re.finditer(r"(?m)^(#{2,6}) .+$", markdown)
    ]
    if not headings:
        raise RuntimeError("No Codul administrativ structural headings found")

    boundaries = [headings[0][0]]
    position = boundaries[0]
    while len(markdown) - position > MAX_CHUNK_CHARACTERS:
        remaining = len(markdown) - position
        target = remaining / 2 if remaining <= 2 * MAX_CHUNK_CHARACTERS else 46_000
        candidates = [
            heading
            for heading in headings
            if position + MIN_CHUNK_CHARACTERS
            <= heading[0]
            <= position + MAX_CHUNK_CHARACTERS
            and heading[1] <= 5
            and (
                remaining > 2 * MAX_CHUNK_CHARACTERS
                or len(markdown) - heading[0] >= MIN_CHUNK_CHARACTERS
            )
        ]
        if not candidates:
            candidates = [
                heading
                for heading in headings
                if position + MIN_CHUNK_CHARACTERS
                <= heading[0]
                <= position + MAX_CHUNK_CHARACTERS
                and (
                    remaining > 2 * MAX_CHUNK_CHARACTERS
                    or len(markdown) - heading[0] >= MIN_CHUNK_CHARACTERS
                )
            ]
        if candidates:
            next_position, _ = min(
                candidates,
                key=lambda heading: abs((heading[0] - position) - target)
                + (heading[1] - 2) * 900,
            )
        else:
            paragraphs = [
                match.start()
                for match in re.finditer(r"(?m)^\S", markdown)
                if position + MIN_CHUNK_CHARACTERS
                <= match.start()
                <= position + MAX_CHUNK_CHARACTERS
                and (
                    remaining > 2 * MAX_CHUNK_CHARACTERS
                    or len(markdown) - match.start() >= MIN_CHUNK_CHARACTERS
                )
            ]
            if not paragraphs:
                raise RuntimeError(
                    f"No administrative-code boundary near character {position:,}"
                )
            next_position = min(
                paragraphs,
                key=lambda paragraph: abs((paragraph - position) - target),
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


def validate_administrative_articles(markdown: str) -> None:
    labels = [
        match.group("number")
        for match in ADMINISTRATIVE_MARKDOWN_ARTICLE.finditer(markdown)
    ]
    base_articles = [int(label) for label in labels if "^" not in label]
    inserted_articles = tuple(label for label in labels if "^" in label)
    if base_articles != list(range(1, 639)):
        raise RuntimeError("Codul administrativ base articles are incomplete or reordered")
    if inserted_articles != ADMINISTRATIVE_INSERTED_ARTICLES:
        raise RuntimeError(
            "Unexpected inserted articles: " + ", ".join(inserted_articles)
        )

    annexes = tuple(
        match.group("number")
        for match in ADMINISTRATIVE_MARKDOWN_ANNEX.finditer(markdown)
    )
    if annexes != ("1", "2", "3", "4", "5", "5^1", "6", "7", "8", "9", "10"):
        raise RuntimeError("Unexpected administrative-code annex sequence")


def build_administrative_chunks(markdown: str) -> list[Path]:
    validate_administrative_articles(markdown)
    boundaries = administrative_chunk_boundaries(markdown)
    if len(boundaries) - 1 != len(ADMINISTRATIVE_CHUNKS):
        raise RuntimeError(
            f"Expected {len(ADMINISTRATIVE_CHUNKS)} administrative-code chunks, "
            f"generated {len(boundaries) - 1}"
        )

    preamble = markdown[: boundaries[0]].rstrip()
    expected_names = {chunk.filename for chunk in ADMINISTRATIVE_CHUNKS}
    for stale in OUTPUT.glob("codul_administrativ-*.md"):
        if stale.name not in expected_names:
            stale.unlink()

    built = []
    for start, end, chunk in zip(
        boundaries, boundaries[1:], ADMINISTRATIVE_CHUNKS
    ):
        body = markdown[start:end].strip() + "\n"
        articles = [
            match.group("number")
            for match in ADMINISTRATIVE_MARKDOWN_ARTICLE.finditer(body)
        ]
        if chunk.first_article is not None:
            if not articles or (
                articles[0] != chunk.first_article
                or articles[-1] != chunk.last_article
            ):
                found = f"{articles[0]}-{articles[-1]}" if articles else "none"
                raise RuntimeError(
                    f"{chunk.filename} expected {chunk.first_article}-"
                    f"{chunk.last_article}, found {found}"
                )
        elif articles:
            raise RuntimeError(f"Unexpected code articles in {chunk.filename}")

        content = (
            f"{preamble}\n"
            f"**Fragment:** {chunk.range_label}\n"
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


def administrative_catalog_block(built: list[Path]) -> bytes:
    filenames = {path.name for path in built}
    entries = []
    for chunk in ADMINISTRATIVE_CHUNKS:
        if chunk.filename not in filenames:
            raise RuntimeError(f"Missing generated chunk: {chunk.filename}")
        entries.append(
            "- Codul administrativ (OUG nr. 57/2019, consolidare la 8 aprilie "
            f"2024) — {chunk.description}. {chunk.range_label}.\n"
            f"  {PUBLIC_BASE_URL}/{chunk.filename}\n"
        )
    return ("\n".join(entries) + "\n").encode("utf-8")


def update_administrative_catalog(built: list[Path]) -> None:
    data = CATALOG.read_bytes()
    entry_pattern = re.compile(
        rb"- Codul administrativ[^\r\n]*\r?\n"
        rb"  https://[^\r\n]*/sources/codul_administrativ-[^\r\n]*\r?\n(?:\r?\n)?"
    )
    matches = list(entry_pattern.finditer(data))
    if not matches:
        raise RuntimeError("No existing Codul administrativ catalog entries found")

    start, end = matches[0].start(), matches[-1].end()
    unmatched = entry_pattern.sub(b"", data[start:end])
    if unmatched.strip():
        raise RuntimeError("Administrative Code catalog entries are not contiguous")
    replacement = administrative_catalog_block(built)
    CATALOG.write_bytes(data[:start] + replacement + data[end:])


def build_administrative_document(raw_source: str) -> None:
    markdown = format_administrative_markdown(
        clean_administrative_source(raw_source)
    )
    ADMINISTRATIVE_SOURCE.write_text(markdown, encoding="utf-8", newline="\n")
    built = build_administrative_chunks(markdown)
    update_administrative_catalog(built)

    for legacy_chunk in OUTPUT.glob("codul_administrativ-p*.pdf"):
        legacy_chunk.unlink()
    if ADMINISTRATIVE_LEGACY_SOURCE.exists():
        ADMINISTRATIVE_LEGACY_SOURCE.unlink()
    for legacy_text in ADMINISTRATIVE_LEGACY_TEXT_SOURCES:
        if legacy_text.exists():
            legacy_text.unlink()


def clean_road_source(text: str) -> str:
    text = text.removeprefix("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    return text.rstrip() + "\n"


def road_source_marker(line: str) -> bool:
    return bool(
        ROAD_CHAPTER.fullmatch(line)
        or ROAD_SECTION.fullmatch(line)
        or ROAD_ANNEX.fullmatch(line)
        or ROAD_ARTICLE.fullmatch(line)
    )


def road_article_label(raw_number: str, current_article: int) -> tuple[str, int]:
    parts = raw_number.split(".")
    base = int(parts[0])
    if len(parts) == 1:
        if base != current_article + 1:
            raise RuntimeError(
                f"Unexpected road-code article {raw_number} after {current_article}"
            )
        return raw_number, base
    if base != current_article or len(parts) != 2:
        raise RuntimeError(
            f"Unexpected inserted road-code article {raw_number} after "
            f"{current_article}"
        )
    return f"{base}^{parts[1]}", current_article


def format_road_markdown(text: str) -> str:
    """Format the Road Code hierarchy and normalize two duplicated chapter labels."""
    if text.startswith("# Codul rutier\n"):
        return normalize_heading_spacing(text)

    lines = text.splitlines()
    if not lines or not lines[0].lower().startswith("codul rutier"):
        raise RuntimeError("Unexpected Codul rutier document heading")

    rendered = [
        "# Codul rutier",
        "OUG nr. 195/2002",
        "Actualizat la 5 februarie 2025",
    ]
    expected_chapters = ("I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X")
    chapter_index = 0
    current_article = 0
    index = 1

    while index < len(lines):
        raw_line = lines[index].rstrip()
        line = raw_line.strip()
        article = ROAD_ARTICLE.fullmatch(line)
        if article:
            label, current_article = road_article_label(
                article.group("number"), current_article
            )
            rendered.append(f"#### Articolul {label}")
            if article.group("body"):
                rendered.append(article.group("body"))
            index += 1
            continue

        chapter = ROAD_CHAPTER.fullmatch(line)
        if chapter:
            if chapter_index >= len(expected_chapters):
                raise RuntimeError("Too many Codul rutier chapters")
            title = chapter.group("title").strip()
            if index + 1 < len(lines):
                continuation = lines[index + 1].strip()
                if continuation and not road_source_marker(continuation):
                    title = f"{title} {continuation}".strip()
                    index += 1
            number = expected_chapters[chapter_index]
            rendered.append(f"## CAPITOLUL {number} — {title}")
            chapter_index += 1
            index += 1
            continue

        section = ROAD_SECTION.fullmatch(line)
        if section:
            title = section.group("title").strip()
            if not title and index + 1 < len(lines):
                continuation = lines[index + 1].strip()
                if continuation and not road_source_marker(continuation):
                    title = continuation
                    index += 1
            suffix = f" — {title}" if title else ""
            rendered.append(f"### {section.group('label').upper()}{suffix}")
            index += 1
            continue

        annex = ROAD_ANNEX.fullmatch(line)
        if annex:
            title = annex.group("title").strip().replace(
                "eliberrează", "eliberează"
            )
            if index + 1 < len(lines):
                continuation = lines[index + 1].strip()
                if continuation and not road_source_marker(continuation):
                    title = f"{title} {continuation}".strip()
                    index += 1
            rendered.append(f"## ANEXA {annex.group('number')} — {title}")
            index += 1
            continue

        rendered.append(raw_line)
        index += 1

    if chapter_index != len(expected_chapters):
        raise RuntimeError(
            f"Found {chapter_index} road-code chapters, expected "
            f"{len(expected_chapters)}"
        )
    if current_article != 137:
        raise RuntimeError(
            f"Codul rutier ended at article {current_article}, expected 137"
        )
    return normalize_heading_spacing("\n".join(rendered))


def validate_road_articles(markdown: str) -> None:
    labels = [
        match.group("number") for match in ROAD_MARKDOWN_ARTICLE.finditer(markdown)
    ]
    base_articles = [int(label) for label in labels if "^" not in label]
    inserted_articles = tuple(label for label in labels if "^" in label)
    if base_articles != list(range(1, 138)):
        raise RuntimeError("Codul rutier base articles are incomplete or reordered")
    if inserted_articles != ROAD_INSERTED_ARTICLES:
        raise RuntimeError("Unexpected inserted road-code articles")
    annexes = tuple(
        match.group("number") for match in ROAD_MARKDOWN_ANNEX.finditer(markdown)
    )
    if annexes != ("1",):
        raise RuntimeError(f"Unexpected road-code annex sequence: {annexes}")


def road_chunk_boundaries(markdown: str) -> list[int]:
    structural = [
        (match.start(), len(match.group(1)))
        for match in re.finditer(r"(?m)^(#{2,3}) .+$", markdown)
    ]
    articles = [
        match.start()
        for match in ROAD_MARKDOWN_ARTICLE.finditer(markdown)
        if "^" not in match.group("number")
    ]
    if not structural:
        raise RuntimeError("No Codul rutier structural headings found")

    boundaries = [structural[0][0]]
    position = boundaries[0]
    while len(markdown) - position > MAX_CHUNK_CHARACTERS:
        remaining = len(markdown) - position
        target = remaining / 2 if remaining <= 2 * MAX_CHUNK_CHARACTERS else 46_000
        candidates = [
            heading
            for heading in structural
            if position + MIN_CHUNK_CHARACTERS
            <= heading[0]
            <= position + MAX_CHUNK_CHARACTERS
            and (
                remaining > 2 * MAX_CHUNK_CHARACTERS
                or len(markdown) - heading[0] >= MIN_CHUNK_CHARACTERS
            )
        ]
        if candidates:
            next_position, _ = min(
                candidates,
                key=lambda heading: abs((heading[0] - position) - target)
                + (heading[1] - 2) * 900,
            )
        else:
            article_candidates = [
                article
                for article in articles
                if position + MIN_CHUNK_CHARACTERS
                <= article
                <= position + MAX_CHUNK_CHARACTERS
                and (
                    remaining > 2 * MAX_CHUNK_CHARACTERS
                    or len(markdown) - article >= MIN_CHUNK_CHARACTERS
                )
            ]
            if not article_candidates:
                raise RuntimeError(
                    f"No road-code boundary near character {position:,}"
                )
            next_position = min(
                article_candidates,
                key=lambda article: abs((article - position) - target),
            )
        boundaries.append(next_position)
        position = next_position
    boundaries.append(len(markdown))
    return boundaries


def build_road_chunks(markdown: str) -> list[Path]:
    validate_road_articles(markdown)
    boundaries = road_chunk_boundaries(markdown)
    if len(boundaries) - 1 != len(ROAD_CHUNKS):
        raise RuntimeError(
            f"Expected {len(ROAD_CHUNKS)} road-code chunks, "
            f"generated {len(boundaries) - 1}"
        )

    preamble = markdown[: boundaries[0]].rstrip()
    expected_names = {chunk.filename for chunk in ROAD_CHUNKS}
    for stale in OUTPUT.glob("cod_rutier-*.md"):
        if stale.name not in expected_names:
            stale.unlink()

    built = []
    for start, end, chunk in zip(boundaries, boundaries[1:], ROAD_CHUNKS):
        body = markdown[start:end].strip() + "\n"
        articles = [
            match.group("number") for match in ROAD_MARKDOWN_ARTICLE.finditer(body)
        ]
        if not articles or (
            articles[0] != chunk.first_article or articles[-1] != chunk.last_article
        ):
            found = f"{articles[0]}-{articles[-1]}" if articles else "none"
            raise RuntimeError(
                f"{chunk.filename} expected {chunk.first_article}-"
                f"{chunk.last_article}, found {found}"
            )
        has_annex = bool(ROAD_MARKDOWN_ANNEX.search(body))
        if has_annex != chunk.includes_annex:
            raise RuntimeError(f"Unexpected annex placement in {chunk.filename}")

        content = (
            f"{preamble}\n"
            f"**Fragment:** {chunk.range_label}\n"
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


def road_catalog_block(built: list[Path]) -> bytes:
    filenames = {path.name for path in built}
    entries = []
    for chunk in ROAD_CHUNKS:
        if chunk.filename not in filenames:
            raise RuntimeError(f"Missing generated chunk: {chunk.filename}")
        entries.append(
            "- Codul rutier (OUG nr. 195/2002, actualizată la 5 februarie "
            f"2025) — {chunk.description}. {chunk.range_label}.\n"
            f"  {PUBLIC_BASE_URL}/{chunk.filename}\n"
        )
    return ("\n".join(entries) + "\n").encode("utf-8")


def update_road_catalog(built: list[Path]) -> None:
    data = CATALOG.read_bytes()
    entry_pattern = re.compile(
        rb"- Codul rutier[^\r\n]*\r?\n"
        rb"  https://[^\r\n]*/sources/cod_rutier-[^\r\n]*\r?\n(?:\r?\n)?"
    )
    matches = list(entry_pattern.finditer(data))
    if not matches:
        raise RuntimeError("No existing Codul rutier catalog entries found")
    start, end = matches[0].start(), matches[-1].end()
    unmatched = entry_pattern.sub(b"", data[start:end])
    if unmatched.strip():
        raise RuntimeError("Road Code catalog entries are not contiguous")
    CATALOG.write_bytes(data[:start] + road_catalog_block(built) + data[end:])


def build_road_document(raw_source: str) -> None:
    markdown = format_road_markdown(clean_road_source(raw_source))
    ROAD_SOURCE.write_text(markdown, encoding="utf-8", newline="\n")
    built = build_road_chunks(markdown)
    update_road_catalog(built)

    for legacy_chunk in OUTPUT.glob("cod_rutier-p*.pdf"):
        legacy_chunk.unlink()
    if ROAD_LEGACY_SOURCE.exists():
        ROAD_LEGACY_SOURCE.unlink()
    for legacy_text in ROAD_LEGACY_TEXT_SOURCES:
        if legacy_text.exists():
            legacy_text.unlink()


def clean_penal_source(text: str) -> str:
    """Drop the duplicated table of contents and recurring PDF page numbers."""
    text = text.removeprefix("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    if text.startswith("# Codul penal\n"):
        return text.rstrip() + "\n"

    lines = text.splitlines()
    starts = [
        index for index, line in enumerate(lines) if line.startswith("PARTEA GENERAL")
    ]
    if len(starts) != 2:
        raise RuntimeError(
            f"Expected a contents and a body occurrence of PARTEA GENERALĂ, "
            f"found {len(starts)}"
        )
    body = [
        line
        for line in lines[starts[1] :]
        if not re.fullmatch(r"\s*\d{1,3}\s*", line)
    ]
    return "\n".join(body).rstrip() + "\n"


def penal_structure_kind(line: str) -> str | None:
    if PENAL_PART.fullmatch(line):
        return "part"
    if PENAL_TITLE.fullmatch(line):
        return "title"
    if PENAL_CHAPTER.fullmatch(line):
        return "chapter"
    if PENAL_SECTION.fullmatch(line):
        return "section"
    if PENAL_ARTICLE.fullmatch(line):
        return "article"
    return None


def format_penal_markdown(text: str) -> str:
    """Apply the full part/title/chapter/section/article Markdown hierarchy."""
    if text.startswith("# Codul penal\n"):
        return normalize_heading_spacing(text)

    lines = text.splitlines()
    if not lines or not lines[0].startswith("PARTEA GENERAL"):
        raise RuntimeError("Unexpected Codul penal body heading")

    rendered = [
        "# Codul penal",
        "Legea nr. 286/2009",
        "Actualizată până la 1 februarie 2014",
    ]
    index = 0
    while index < len(lines):
        raw_line = lines[index].rstrip()
        line = raw_line.strip()
        kind = penal_structure_kind(line)

        if kind == "part":
            rendered.append(f"## {line}")
            index += 1
            continue
        if kind in {"title", "chapter", "section"}:
            if kind == "title":
                label, title, level = line, "", 3
            elif kind == "chapter":
                match = PENAL_CHAPTER.fullmatch(line)
                assert match is not None
                label, title, level = match.group("label"), match.group("title"), 4
            else:
                match = PENAL_SECTION.fullmatch(line)
                assert match is not None
                label, title, level = match.group("label"), match.group("title"), 5

            index += 1
            continuation = []
            while index < len(lines):
                candidate = lines[index].strip()
                if penal_structure_kind(candidate):
                    break
                if candidate:
                    continuation.append(candidate)
                index += 1
            full_title = " ".join(
                part for part in [title.strip(), *continuation] if part
            )
            if not full_title:
                raise RuntimeError(f"Missing heading title after {label}")
            rendered.append(f"{'#' * level} {label} — {full_title}")
            continue
        if kind == "article":
            article = PENAL_ARTICLE.fullmatch(line)
            assert article is not None
            rendered.append(
                f"###### Articolul {article.group('number')} — "
                f"{article.group('title').strip()}"
            )
            index += 1
            continue

        rendered.append(raw_line)
        index += 1

    return normalize_heading_spacing("\n".join(rendered))


def validate_penal_document(markdown: str) -> None:
    articles = [
        int(match.group("number"))
        for match in PENAL_MARKDOWN_ARTICLE.finditer(markdown)
    ]
    if articles != list(range(1, 438)):
        raise RuntimeError("Codul penal articles are incomplete or reordered")

    expected_structure = {
        r"(?m)^## PARTEA ": 2,
        r"(?m)^### TITLUL ": 23,
        r"(?m)^#### CAPITOLUL ": 56,
        r"(?m)^##### Sec": 13,
    }
    for pattern, expected in expected_structure.items():
        actual = len(re.findall(pattern, markdown))
        if actual != expected:
            raise RuntimeError(
                f"Unexpected Codul penal structure count for {pattern}: "
                f"{actual}, expected {expected}"
            )
    if re.search(r"(?m)^\s*\d{1,3}\s*$", markdown):
        raise RuntimeError("Standalone PDF page number remains in Codul penal")


def penal_chunk_boundaries(markdown: str) -> list[int]:
    structural = [
        (match.start(), len(match.group(1)))
        for match in re.finditer(r"(?m)^(#{2,5}) .+$", markdown)
    ]
    articles = [match.start() for match in PENAL_MARKDOWN_ARTICLE.finditer(markdown)]
    if not structural:
        raise RuntimeError("No Codul penal structural headings found")

    boundaries = [structural[0][0]]
    position = boundaries[0]
    while len(markdown) - position > MAX_CHUNK_CHARACTERS:
        remaining = len(markdown) - position
        target = remaining / 2 if remaining <= 2 * MAX_CHUNK_CHARACTERS else 46_000
        candidates = [
            heading
            for heading in structural
            if position + MIN_CHUNK_CHARACTERS
            <= heading[0]
            <= position + MAX_CHUNK_CHARACTERS
            and (
                remaining > 2 * MAX_CHUNK_CHARACTERS
                or len(markdown) - heading[0] >= MIN_CHUNK_CHARACTERS
            )
        ]
        if candidates:
            next_position, _ = min(
                candidates,
                key=lambda heading: abs((heading[0] - position) - target)
                + (heading[1] - 2) * 900,
            )
        else:
            article_candidates = [
                article
                for article in articles
                if position + MIN_CHUNK_CHARACTERS
                <= article
                <= position + MAX_CHUNK_CHARACTERS
                and (
                    remaining > 2 * MAX_CHUNK_CHARACTERS
                    or len(markdown) - article >= MIN_CHUNK_CHARACTERS
                )
            ]
            if not article_candidates:
                raise RuntimeError(
                    f"No penal-code boundary near character {position:,}"
                )
            next_position = min(
                article_candidates,
                key=lambda article: abs((article - position) - target),
            )
        boundaries.append(next_position)
        position = next_position
    boundaries.append(len(markdown))
    return boundaries


def build_penal_chunks(markdown: str) -> list[Path]:
    validate_penal_document(markdown)
    boundaries = penal_chunk_boundaries(markdown)
    if len(boundaries) - 1 != len(PENAL_CHUNKS):
        raise RuntimeError(
            f"Expected {len(PENAL_CHUNKS)} penal-code chunks, "
            f"generated {len(boundaries) - 1}"
        )

    preamble = markdown[: boundaries[0]].rstrip()
    expected_names = {chunk.filename for chunk in PENAL_CHUNKS}
    for stale in OUTPUT.glob("cod_penal-*.md"):
        if stale.name not in expected_names:
            stale.unlink()

    built = []
    for start, end, chunk in zip(boundaries, boundaries[1:], PENAL_CHUNKS):
        body = markdown[start:end].strip() + "\n"
        articles = [
            int(match.group("number"))
            for match in PENAL_MARKDOWN_ARTICLE.finditer(body)
        ]
        if not articles or (
            articles[0] != chunk.first_article or articles[-1] != chunk.last_article
        ):
            found = f"{articles[0]}-{articles[-1]}" if articles else "none"
            raise RuntimeError(
                f"{chunk.filename} expected {chunk.first_article}-"
                f"{chunk.last_article}, found {found}"
            )

        content = (
            f"{preamble}\n"
            f"**Fragment:** {chunk.range_label}\n"
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


def penal_catalog_block(built: list[Path]) -> bytes:
    filenames = {path.name for path in built}
    entries = []
    for chunk in PENAL_CHUNKS:
        if chunk.filename not in filenames:
            raise RuntimeError(f"Missing generated chunk: {chunk.filename}")
        entries.append(
            "- Codul penal (Legea nr. 286/2009, actualizată până la 1 februarie "
            f"2014) — {chunk.description}. {chunk.range_label}.\n"
            f"  {PUBLIC_BASE_URL}/{chunk.filename}\n"
        )
    return ("\n".join(entries) + "\n").encode("utf-8")


def update_penal_catalog(built: list[Path]) -> None:
    data = CATALOG.read_bytes()
    entry_pattern = re.compile(
        rb"- Codul penal[^\r\n]*\r?\n"
        rb"  https://[^\r\n]*/sources/cod_penal-[^\r\n]*\r?\n(?:\r?\n)?"
    )
    matches = list(entry_pattern.finditer(data))
    if not matches:
        raise RuntimeError("No existing Codul penal catalog entries found")
    start, end = matches[0].start(), matches[-1].end()
    unmatched = entry_pattern.sub(b"", data[start:end])
    if unmatched.strip():
        raise RuntimeError("Penal Code catalog entries are not contiguous")
    CATALOG.write_bytes(data[:start] + penal_catalog_block(built) + data[end:])


def build_penal_document(raw_source: str) -> None:
    markdown = format_penal_markdown(clean_penal_source(raw_source))
    PENAL_SOURCE.write_text(markdown, encoding="utf-8", newline="\n")
    built = build_penal_chunks(markdown)
    update_penal_catalog(built)

    for legacy_chunk in OUTPUT.glob("cod_penal-p*.pdf"):
        legacy_chunk.unlink()
    if PENAL_LEGACY_SOURCE.exists():
        PENAL_LEGACY_SOURCE.unlink()
    for legacy_text in PENAL_LEGACY_TEXT_SOURCES:
        if legacy_text.exists():
            legacy_text.unlink()


def clean_constitution_source(text: str) -> str:
    """Keep the constitutional text and discard the scraped website tail."""
    text = text.removeprefix("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    if text.startswith("# Constituția României\n"):
        return text.rstrip() + "\n"

    lines = text.splitlines()
    if not lines or lines[0] != "Textul integral":
        raise RuntimeError("Unexpected Constitution source heading")
    try:
        end = lines.index("Search")
    except ValueError as error:
        raise RuntimeError("Could not locate the end of the constitutional text") from error

    body = [
        line for line in lines[1:end] if line.strip() != "Constituția României"
    ]
    if not any(line.startswith("Art. 156 ") for line in body):
        raise RuntimeError("Constitution source ends before article 156")
    return "\n".join(body).rstrip() + "\n"


def format_constitution_markdown(text: str) -> str:
    if text.startswith("# Constituția României\n"):
        return normalize_heading_spacing(text)

    lines = text.splitlines()
    if not lines or not CONSTITUTION_TITLE.fullmatch(lines[0].strip()):
        raise RuntimeError("Unexpected start of the constitutional text")

    rendered = [
        "# Constituția României",
        "Forma revizuită și republicată în Monitorul Oficial nr. 767/2003",
    ]
    for raw_line in lines:
        line = raw_line.strip()
        title = CONSTITUTION_TITLE.fullmatch(line)
        chapter = CONSTITUTION_CHAPTER.fullmatch(line)
        section = CONSTITUTION_SECTION.fullmatch(line)
        article = CONSTITUTION_ARTICLE.fullmatch(line)
        if title:
            rendered.append(
                f"## {title.group('label')} — {title.group('title').strip()}"
            )
        elif chapter:
            rendered.append(
                f"### {chapter.group('label')} — {chapter.group('title').strip()}"
            )
        elif section:
            rendered.append(
                f"#### {section.group('label').upper()} — "
                f"{section.group('title').strip()}"
            )
        elif article:
            rendered.append(
                f"##### Articolul {article.group('number')} — "
                f"{article.group('title').strip()}"
            )
        else:
            rendered.append(raw_line.rstrip())
    return normalize_heading_spacing("\n".join(rendered))


def validate_constitution_document(markdown: str) -> None:
    articles = [
        int(match.group("number"))
        for match in CONSTITUTION_MARKDOWN_ARTICLE.finditer(markdown)
    ]
    if articles != list(range(1, 157)):
        raise RuntimeError("Constitution articles are incomplete or reordered")

    expected_structure = {
        r"(?m)^## TITLUL ": 8,
        r"(?m)^### CAPITOLUL ": 10,
        r"(?m)^#### SEC": 8,
    }
    for pattern, expected in expected_structure.items():
        actual = len(re.findall(pattern, markdown))
        if actual != expected:
            raise RuntimeError(
                f"Unexpected Constitution structure count for {pattern}: "
                f"{actual}, expected {expected}"
            )
    for artifact in ("Search", "Ultimele comentarii", "Constituția României\n\n#####"):
        if artifact in markdown:
            raise RuntimeError(f"Scraped website artifact remains: {artifact}")


def constitution_chunk_boundaries(markdown: str) -> list[int]:
    structural = [
        (match.start(), len(match.group(1)))
        for match in re.finditer(r"(?m)^(#{2,4}) .+$", markdown)
    ]
    articles = [
        match.start() for match in CONSTITUTION_MARKDOWN_ARTICLE.finditer(markdown)
    ]
    if not structural:
        raise RuntimeError("No Constitution structural headings found")

    boundaries = [structural[0][0]]
    position = boundaries[0]
    while len(markdown) - position > MAX_CHUNK_CHARACTERS:
        remaining = len(markdown) - position
        target = remaining / 2 if remaining <= 2 * MAX_CHUNK_CHARACTERS else 46_000
        candidates = [
            heading
            for heading in structural
            if position + MIN_CHUNK_CHARACTERS
            <= heading[0]
            <= position + MAX_CHUNK_CHARACTERS
            and len(markdown) - heading[0] >= MIN_CHUNK_CHARACTERS
        ]
        if candidates:
            next_position, _ = min(
                candidates,
                key=lambda heading: abs((heading[0] - position) - target)
                + (heading[1] - 2) * 900,
            )
        else:
            article_candidates = [
                article
                for article in articles
                if position + MIN_CHUNK_CHARACTERS
                <= article
                <= position + MAX_CHUNK_CHARACTERS
                and len(markdown) - article >= MIN_CHUNK_CHARACTERS
            ]
            if not article_candidates:
                raise RuntimeError(
                    f"No Constitution boundary near character {position:,}"
                )
            next_position = min(
                article_candidates,
                key=lambda article: abs((article - position) - target),
            )
        boundaries.append(next_position)
        position = next_position
    boundaries.append(len(markdown))
    return boundaries


def build_constitution_chunks(markdown: str) -> list[Path]:
    validate_constitution_document(markdown)
    boundaries = constitution_chunk_boundaries(markdown)
    if len(boundaries) - 1 != len(CONSTITUTION_CHUNKS):
        raise RuntimeError(
            f"Expected {len(CONSTITUTION_CHUNKS)} Constitution chunks, "
            f"generated {len(boundaries) - 1}"
        )

    preamble = markdown[: boundaries[0]].rstrip()
    expected_names = {chunk.filename for chunk in CONSTITUTION_CHUNKS}
    for stale in OUTPUT.glob("constitutia_romaniei-*.md"):
        if stale.name not in expected_names:
            stale.unlink()

    built = []
    for start, end, chunk in zip(boundaries, boundaries[1:], CONSTITUTION_CHUNKS):
        body = markdown[start:end].strip() + "\n"
        articles = [
            int(match.group("number"))
            for match in CONSTITUTION_MARKDOWN_ARTICLE.finditer(body)
        ]
        if not articles or (
            articles[0] != chunk.first_article or articles[-1] != chunk.last_article
        ):
            found = f"{articles[0]}-{articles[-1]}" if articles else "none"
            raise RuntimeError(
                f"{chunk.filename} expected {chunk.first_article}-"
                f"{chunk.last_article}, found {found}"
            )

        content = (
            f"{preamble}\n"
            f"**Fragment:** {chunk.range_label}\n"
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


def constitution_catalog_block(built: list[Path]) -> bytes:
    filenames = {path.name for path in built}
    entries = []
    for chunk in CONSTITUTION_CHUNKS:
        if chunk.filename not in filenames:
            raise RuntimeError(f"Missing generated chunk: {chunk.filename}")
        entries.append(
            "- Constituția României (forma revizuită și republicată în M.Of. "
            f"nr. 767/2003) — {chunk.description}. {chunk.range_label}.\n"
            f"  {PUBLIC_BASE_URL}/{chunk.filename}\n"
        )
    return ("\n".join(entries) + "\n").encode("utf-8")


def update_constitution_catalog(built: list[Path]) -> None:
    data = CATALOG.read_bytes()
    entry_pattern = re.compile(
        rb"- Constitu\xc8\x9bia Rom\xc3\xa2niei[^\r\n]*\r?\n"
        rb"  https://[^\r\n]*/sources/constitutia_romaniei-[^\r\n]*\r?\n(?:\r?\n)?"
    )
    matches = list(entry_pattern.finditer(data))
    if not matches:
        raise RuntimeError("No existing Constitution catalog entries found")
    start, end = matches[0].start(), matches[-1].end()
    unmatched = entry_pattern.sub(b"", data[start:end])
    if unmatched.strip():
        raise RuntimeError("Constitution catalog entries are not contiguous")
    CATALOG.write_bytes(data[:start] + constitution_catalog_block(built) + data[end:])


def build_constitution_document(raw_source: str) -> None:
    markdown = format_constitution_markdown(clean_constitution_source(raw_source))
    CONSTITUTION_SOURCE.write_text(markdown, encoding="utf-8", newline="\n")
    built = build_constitution_chunks(markdown)
    update_constitution_catalog(built)

    for legacy_chunk in OUTPUT.glob("constitutia_romaniei-p*.pdf"):
        legacy_chunk.unlink()
    if CONSTITUTION_LEGACY_SOURCE.exists():
        CONSTITUTION_LEGACY_SOURCE.unlink()
    for legacy_text in CONSTITUTION_LEGACY_TEXT_SOURCES:
        if legacy_text.exists():
            legacy_text.unlink()


def clean_procedure_civil_source(text: str) -> str:
    text = text.removeprefix("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    if text.startswith("# Codul de procedură civilă\n"):
        return text.rstrip() + "\n"
    text = PROCEDURE_CIVIL_FOOTER.sub("", text)
    text = text.replace(
        "Codul de Procedura Civila din 2010 - forma sintetica pentru data "
        "2020-05-25",
        "",
    )
    text = re.sub(
        r"(?m)^pag\.\s*\d+\s+5/25/2020\s*:\s*lex@snppc\.ro\n?",
        "",
        text,
    )
    text = text.replace("buna\ncredinţă", "buna-credinţă")
    text = text.replace("teza a II\na sunt", "teza a II-a sunt")
    text = re.sub(r"(?m)^Art\. 471\s*\n1:", "Art. 471^1:", text)
    return text.rstrip() + "\n"


def procedure_civil_structure(line: str) -> tuple[str, re.Match[str]] | None:
    patterns = (
        ("book", PROCEDURE_CIVIL_BOOK),
        ("title", PROCEDURE_CIVIL_TITLE),
        ("chapter", PROCEDURE_CIVIL_CHAPTER),
        ("section", PROCEDURE_CIVIL_SECTION),
        ("subsection", PROCEDURE_CIVIL_SUBSECTION),
        ("article", PROCEDURE_CIVIL_ARTICLE),
    )
    for kind, pattern in patterns:
        match = pattern.fullmatch(line)
        if match:
            return kind, match
    return None


def format_procedure_civil_markdown(text: str) -> str:
    if text.startswith("# Codul de procedură civilă\n"):
        return normalize_heading_spacing(text)

    lines = text.splitlines()
    try:
        first_title = next(
            index
            for index, line in enumerate(lines)
            if PROCEDURE_CIVIL_TITLE.fullmatch(line.strip())
        )
    except StopIteration as error:
        raise RuntimeError("Could not locate Codul de procedură civilă") from error

    rendered = [
        "# Codul de procedură civilă",
        "Legea nr. 134/2010, republicată în Monitorul Oficial nr. 247/2015",
        "Forma consolidată la 25 mai 2020",
    ]
    rendered.extend(line.strip() for line in lines[1:first_title] if line.strip())
    current_article = 0
    application_extracts = False
    index = first_title

    while index < len(lines):
        raw_line = lines[index].rstrip()
        line = raw_line.strip()
        structure = procedure_civil_structure(line)

        if structure and structure[0] == "article":
            article = structure[1]
            label = article.group("number")
            base = int(label.split("^", 1)[0])
            if "^" in label:
                if base != current_article:
                    raise RuntimeError(
                        f"Unexpected inserted article {label} after {current_article}"
                    )
            else:
                if base != current_article + 1:
                    raise RuntimeError(
                        f"Unexpected article {label} after {current_article}"
                    )
                current_article = base
            title = article.group("title").strip()
            suffix = f" — {title}" if title else ""
            rendered.append(f"###### Articolul {label}{suffix}")
            index += 1
            continue

        if structure:
            kind, match = structure
            label = match.group("label")
            title = (
                (match.group("title") or "").strip()
                if "title" in match.groupdict()
                else ""
            )

            if kind in {"chapter", "section"} and label.endswith(" 0"):
                index += 1
                continue
            if kind == "subsection" and not title:
                index += 1
                continue
            if kind == "chapter" and current_article == 1134 and not title:
                rendered.append("## Dispoziții de aplicare și tranziție")
                application_extracts = True
                index += 1
                continue

            levels = {
                "book": 2,
                "title": 2 if "PRELIMINAR" in label else 3,
                "chapter": 4,
                "section": 5,
                "subsection": 6,
            }
            index += 1
            continuation = []
            while index < len(lines):
                candidate = lines[index].strip()
                if procedure_civil_structure(candidate):
                    break
                if candidate.startswith(
                    ("(la data", "[textul", "NOTĂ:", "___", "*)")
                ):
                    break
                if candidate:
                    continuation.append(candidate)
                index += 1
            full_title = " ".join(
                part for part in [title, *continuation] if part
            )
            if not full_title:
                raise RuntimeError(f"Missing title after {label}")
            rendered.append(f"{'#' * levels[kind]} {label} — {full_title}")
            continue

        if application_extracts:
            extract = PROCEDURE_CIVIL_EXTRACT_ARTICLE.match(
                line.lstrip('"«')
            )
            if extract:
                rendered.append(f"#### Extras — Art. {extract.group('number')}")
                index += 1
                continue

        rendered.append(raw_line)
        index += 1

    if current_article != 1134:
        raise RuntimeError(
            f"Codul de procedură civilă ended at article {current_article}"
        )
    return normalize_heading_spacing("\n".join(rendered))


def validate_procedure_civil_document(markdown: str) -> None:
    labels = [
        match.group("number")
        for match in PROCEDURE_CIVIL_MARKDOWN_ARTICLE.finditer(markdown)
    ]
    base_articles = [int(label) for label in labels if "^" not in label]
    inserted_articles = tuple(label for label in labels if "^" in label)
    if base_articles != list(range(1, 1135)):
        raise RuntimeError(
            "Codul de procedură civilă articles are incomplete or reordered"
        )
    if inserted_articles != ("471^1",):
        raise RuntimeError(f"Unexpected inserted articles: {inserted_articles}")

    expected_structure = {
        r"(?m)^## CARTEA ": 7,
        r"(?m)^#{2,3} TITLUL ": 41,
        r"(?m)^#### CAPITOLUL ": 60,
        r"(?m)^##### SEC": 57,
        r"(?m)^###### SUBSEC": 19,
    }
    for pattern, expected in expected_structure.items():
        actual = len(re.findall(pattern, markdown))
        if actual != expected:
            raise RuntimeError(
                f"Unexpected civil-procedure structure count for {pattern}: "
                f"{actual}, expected {expected}"
            )
    if "## Dispoziții de aplicare și tranziție" not in markdown:
        raise RuntimeError("Missing application and transition extracts")
    for artifact in (
        "Codul de Procedura Civila din 2010 - forma sintetica",
        "5/25/2020 : lex@snppc.ro",
        "SECŢIUNEA 0",
        "CAPITOLUL 0",
    ):
        if artifact in markdown:
            raise RuntimeError(f"Extraction artifact remains: {artifact}")


def procedure_civil_chunk_boundaries(markdown: str) -> list[int]:
    structural = [
        (match.start(), len(match.group(1)))
        for match in re.finditer(r"(?m)^(#{2,5}) .+$", markdown)
    ]
    articles = [
        match.start()
        for match in PROCEDURE_CIVIL_MARKDOWN_ARTICLE.finditer(markdown)
        if "^" not in match.group("number")
    ]
    if not structural:
        raise RuntimeError("No civil-procedure structural headings found")

    boundaries = [structural[0][0]]
    position = boundaries[0]
    while len(markdown) - position > MAX_CHUNK_CHARACTERS:
        remaining = len(markdown) - position
        target = remaining / 2 if remaining <= 2 * MAX_CHUNK_CHARACTERS else 46_000
        candidates = [
            heading
            for heading in structural
            if position + MIN_CHUNK_CHARACTERS
            <= heading[0]
            <= position + MAX_CHUNK_CHARACTERS
            and (
                remaining > 2 * MAX_CHUNK_CHARACTERS
                or len(markdown) - heading[0] >= MIN_CHUNK_CHARACTERS
            )
        ]
        if candidates:
            next_position, _ = min(
                candidates,
                key=lambda heading: abs((heading[0] - position) - target)
                + (heading[1] - 2) * 900,
            )
        else:
            article_candidates = [
                article
                for article in articles
                if position + MIN_CHUNK_CHARACTERS
                <= article
                <= position + MAX_CHUNK_CHARACTERS
                and (
                    remaining > 2 * MAX_CHUNK_CHARACTERS
                    or len(markdown) - article >= MIN_CHUNK_CHARACTERS
                )
            ]
            if not article_candidates:
                raise RuntimeError(
                    f"No civil-procedure boundary near character {position:,}"
                )
            next_position = min(
                article_candidates,
                key=lambda article: abs((article - position) - target),
            )
        boundaries.append(next_position)
        position = next_position
    boundaries.append(len(markdown))
    return boundaries


def build_procedure_civil_chunks(markdown: str) -> list[Path]:
    validate_procedure_civil_document(markdown)
    boundaries = procedure_civil_chunk_boundaries(markdown)
    if len(boundaries) - 1 != len(PROCEDURE_CIVIL_CHUNKS):
        raise RuntimeError(
            f"Expected {len(PROCEDURE_CIVIL_CHUNKS)} civil-procedure chunks, "
            f"generated {len(boundaries) - 1}"
        )

    preamble = markdown[: boundaries[0]].rstrip()
    expected_names = {chunk.filename for chunk in PROCEDURE_CIVIL_CHUNKS}
    for stale in OUTPUT.glob("cod_procedura_civila-*.md"):
        if stale.name not in expected_names:
            stale.unlink()

    built = []
    for start, end, chunk in zip(
        boundaries, boundaries[1:], PROCEDURE_CIVIL_CHUNKS
    ):
        body = markdown[start:end].strip() + "\n"
        labels = [
            match.group("number")
            for match in PROCEDURE_CIVIL_MARKDOWN_ARTICLE.finditer(body)
        ]
        base_articles = [int(label) for label in labels if "^" not in label]
        if not base_articles or (
            base_articles[0] != chunk.first_article
            or base_articles[-1] != chunk.last_article
        ):
            found = (
                f"{base_articles[0]}-{base_articles[-1]}"
                if base_articles
                else "none"
            )
            raise RuntimeError(
                f"{chunk.filename} expected {chunk.first_article}-"
                f"{chunk.last_article}, found {found}"
            )
        has_extracts = "## Dispoziții de aplicare și tranziție" in body
        if has_extracts != chunk.includes_application_extracts:
            raise RuntimeError(f"Unexpected application extracts in {chunk.filename}")

        content = (
            f"{preamble}\n"
            f"**Fragment:** {chunk.range_label}\n"
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


def procedure_civil_catalog_block(built: list[Path]) -> bytes:
    filenames = {path.name for path in built}
    entries = []
    for chunk in PROCEDURE_CIVIL_CHUNKS:
        if chunk.filename not in filenames:
            raise RuntimeError(f"Missing generated chunk: {chunk.filename}")
        entries.append(
            "- Codul de procedură civilă (Legea nr. 134/2010, republicată în "
            "M.Of. nr. 247/2015; forma consolidată la 25.05.2020) — "
            f"{chunk.description}. {chunk.range_label}.\n"
            f"  {PUBLIC_BASE_URL}/{chunk.filename}\n"
        )
    return ("\n".join(entries) + "\n").encode("utf-8")


def update_procedure_civil_catalog(built: list[Path]) -> None:
    data = CATALOG.read_bytes()
    entry_pattern = re.compile(
        rb"- Codul de procedur\xc4\x83 civil\xc4\x83[^\r\n]*\r?\n"
        rb"  https://[^\r\n]*/sources/cod_procedura_civila-[^\r\n]*"
        rb"\r?\n(?:\r?\n)?"
    )
    matches = list(entry_pattern.finditer(data))
    if not matches:
        raise RuntimeError("No existing civil-procedure catalog entries found")
    start, end = matches[0].start(), matches[-1].end()
    unmatched = entry_pattern.sub(b"", data[start:end])
    if unmatched.strip():
        raise RuntimeError("Civil-procedure catalog entries are not contiguous")
    replacement = procedure_civil_catalog_block(built)
    CATALOG.write_bytes(data[:start] + replacement + data[end:])


def build_procedure_civil_document(raw_source: str) -> None:
    markdown = format_procedure_civil_markdown(
        clean_procedure_civil_source(raw_source)
    )
    PROCEDURE_CIVIL_SOURCE.write_text(markdown, encoding="utf-8", newline="\n")
    built = build_procedure_civil_chunks(markdown)
    update_procedure_civil_catalog(built)

    for legacy_chunk in OUTPUT.glob("cod_procedura_civila-p*.pdf"):
        legacy_chunk.unlink()
    if PROCEDURE_CIVIL_LEGACY_SOURCE.exists():
        PROCEDURE_CIVIL_LEGACY_SOURCE.unlink()
    for legacy_text in PROCEDURE_CIVIL_LEGACY_TEXT_SOURCES:
        if legacy_text.exists():
            legacy_text.unlink()


@dataclass(frozen=True)
class FiscalBuiltChunk:
    path: Path
    kind: str
    description: str
    first_article: str | None = None
    last_article: str | None = None
    part: int | None = None


def reverse_mojibake_line(line: str) -> str | None:
    encoded = bytearray()
    for character in line:
        try:
            encoded.extend(character.encode("cp1252"))
        except UnicodeEncodeError:
            if ord(character) <= 255:
                encoded.append(ord(character))
            else:
                return None
    try:
        return encoded.decode("utf-8")
    except UnicodeDecodeError:
        return None


def repair_fiscal_mojibake(line: str) -> str:
    replacements = {
        "È™": "ș",
        "È˜": "Ș",
        "È›": "ț",
        "Èš": "Ț",
        "Äƒ": "ă",
        "Ä‚": "Ă",
        "Ã®": "î",
        "ÃŽ": "Î",
        "Ã¢": "â",
        "Ã‚": "Â",
        "ÅŸ": "ş",
        "Åž": "Ş",
        "Å£": "ţ",
        "Å¢": "Ţ",
        "Â«": "«",
        "Â»": "»",
        "â€ž": "„",
        "â€œ": "“",
        "â€": "”",
        "â€™": "’",
        "â€“": "–",
        "â€”": "—",
        "â€¦": "…",
    }
    for damaged, repaired in replacements.items():
        line = line.replace(damaged, repaired)
    for _ in range(2):
        candidate = reverse_mojibake_line(line)
        if candidate is None or candidate == line:
            break
        line = candidate
    return line


def clean_fiscal_source(text: str) -> str:
    text = text.removeprefix("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    if text.startswith("# Codul fiscal\n"):
        return text.rstrip() + "\n"
    lines = []
    for raw_line in text.splitlines():
        line = repair_fiscal_mojibake(raw_line)
        line = re.sub(
            r"^(SEC[\u0162\u0163\u021a\u021bT]IUNEA\s+\d+)([A-Z].+)$",
            r"\1 - \2",
            line,
        )
        if (
            lines
            and line.strip().startswith("ART.")
            and line.strip() == lines[-1].strip()
        ):
            continue
        lines.append(line)
    return "\n".join(lines).rstrip() + "\n"


def fiscal_structure(line: str) -> tuple[str, re.Match[str]] | None:
    for kind, pattern in (
        ("title", FISCAL_TITLE),
        ("chapter", FISCAL_CHAPTER),
        ("section", FISCAL_SECTION),
        ("subsection", FISCAL_SUBSECTION),
    ):
        match = pattern.fullmatch(line)
        if match:
            return kind, match
    return None


def fiscal_heading_continuation_stops(line: str, norms: bool) -> bool:
    stripped = line.strip()
    if not stripped:
        return True
    if fiscal_structure(stripped) or FISCAL_ARTICLE.fullmatch(stripped):
        return True
    if FISCAL_ANNEX.fullmatch(stripped) or stripped.startswith("ART. II"):
        return True
    if stripped.startswith(("(", "[", "*)", "---------------")):
        return True
    if re.match(r"^[a-zăâîșț]\)\s", stripped, re.IGNORECASE):
        return True
    if norms and (
        re.match(r"^\d+(?:\.\d+)*\.\s", stripped)
        or re.match(r"^[\d ]+\.\s", stripped)
        or re.fullmatch(r"\d+", stripped)
    ):
        return True
    return False


def format_fiscal_markdown(text: str) -> str:
    if text.startswith("# Codul fiscal\n"):
        return normalize_heading_spacing(text)

    lines = text.splitlines()
    title_starts = [
        index
        for index, line in enumerate(lines)
        if line.startswith("TITLUL I - Dispozi")
    ]
    if len(title_starts) < 2:
        raise RuntimeError("Could not locate the start of Codul fiscal")
    start = title_starts[1]
    try:
        norms_start = next(
            index
            for index in range(start, len(lines))
            if lines[index].startswith("NORME METODOLOGICE")
            and lines[index].isupper()
        )
    except StopIteration as error:
        raise RuntimeError("Could not locate the methodological norms") from error

    rendered = [
        "# Codul fiscal",
        "Legea nr. 227/2015 privind Codul fiscal",
        "Forma consolidată: O.U.G. nr. 8/2026",
        "Ediție adnotată cu Normele metodologice aprobate prin H.G. nr. 1/2016",
        "Norme actualizate prin H.G. nr. 602/2025",
        "Text furnizat în scop documentar; nu reprezintă o republicare oficială.",
    ]
    current_article = 0
    inserted_articles: list[str] = []
    index = start
    norms = False

    while index < len(lines):
        raw_line = lines[index].rstrip()
        line = raw_line.strip()

        if index == norms_start:
            subtitle = lines[index + 1].strip() if index + 1 < len(lines) else ""
            rendered.append(
                "## Norme metodologice"
                + (f" — {subtitle}" if subtitle else "")
            )
            norms = True
            index += 2 if subtitle else 1
            continue

        if not norms and line in {"ACTE", "NORMATIVE", "Norme metodologice"}:
            index += 1
            continue

        article = FISCAL_ARTICLE.fullmatch(line) if not norms else None
        if article:
            raw_number = article.group("raw_number")
            number = int(raw_number)
            if number == current_article + 1:
                label = raw_number
                current_article = number
            elif (
                current_article
                and raw_number.startswith(str(current_article))
                and len(raw_number) > len(str(current_article))
            ):
                label = f"{current_article}^{raw_number[len(str(current_article)):]}"
                inserted_articles.append(label)
            elif current_article < number <= 503:
                for missing in range(current_article + 1, number):
                    rendered.append(f"###### Articolul {missing}")
                    rendered.append("_Articol omis din ediția consolidată furnizată._")
                label = raw_number
                current_article = number
            else:
                raise RuntimeError(
                    f"Unexpected fiscal article {raw_number} after {current_article}"
                )

            title = (article.group("title") or "").strip()
            if not title and index + 1 < len(lines):
                continued = lines[index + 1].strip()
                if continued.startswith("-"):
                    title = continued[1:].strip()
                    index += 1
            rendered.append(
                f"###### Articolul {label}" + (f" — {title}" if title else "")
            )
            index += 1
            continue

        structure = fiscal_structure(line)
        if structure:
            kind, match = structure
            label = match.group("label").strip()
            title = (match.group("title") or "").strip()
            if kind == "title" and match.group("inserted"):
                label = (
                    f"TITLUL {match.group('roman')}^{match.group('inserted')}"
                )
            if not title and index + 1 < len(lines):
                continued = lines[index + 1].strip()
                if continued.startswith("-"):
                    title = continued[1:].strip()
                    index += 1

            continuations = []
            while index + 1 < len(lines) and len(continuations) < 6:
                candidate = lines[index + 1].strip()
                if fiscal_heading_continuation_stops(candidate, norms):
                    break
                continuations.append(candidate)
                index += 1
            full_title = " ".join(
                part for part in [title, *continuations] if part
            )
            if not full_title:
                raise RuntimeError(f"Missing fiscal heading title after {label}")
            chapter_inserted = re.fullmatch(
                r"CAPITOLUL\s+([IVXLCDM]+)(\d+)", label
            )
            if kind == "chapter" and chapter_inserted:
                label = (
                    f"CAPITOLUL {chapter_inserted.group(1)}^"
                    f"{chapter_inserted.group(2)}"
                )
            ordinal = re.fullmatch(
                r"(?P<prefix>(?:SUB)?SEC[\u0162\u0163\u021a\u021bT]IUNEA)"
                r"\s+a\s+(?P<number>\d+)",
                label,
            )
            if ordinal and re.match(r"^a\s*-\s*", full_title):
                label = (
                    f"{ordinal.group('prefix')} a {ordinal.group('number')}-a"
                )
                full_title = re.sub(r"^a\s*-\s*", "", full_title)
            if norms:
                levels = {"title": 3, "chapter": 4, "section": 5, "subsection": 6}
            else:
                levels = {"title": 2, "chapter": 3, "section": 4, "subsection": 5}
            rendered.append(
                f"{'#' * levels[kind]} {label} — {full_title}"
            )
            index += 1
            continue

        annex = FISCAL_ANNEX.fullmatch(line)
        if annex:
            level = 4 if norms else 3
            rendered.append(f"{'#' * level} ANEXA {annex.group('label').strip()}")
            index += 1
            continue

        if norms and line == "ART. II":
            rendered.append("### Articolul II — Dispoziție tranzitorie")
            index += 1
            continue

        if line == "---------------":
            index += 1
            continue
        rendered.append(raw_line)
        index += 1

    if current_article != 503:
        raise RuntimeError(f"Codul fiscal ended at article {current_article}")
    if len(inserted_articles) != 118:
        raise RuntimeError(
            f"Expected 118 inserted fiscal articles, found {len(inserted_articles)}"
        )
    return normalize_heading_spacing("\n".join(rendered))


def validate_fiscal_document(markdown: str) -> None:
    marker = "## Norme metodologice"
    if marker not in markdown:
        raise RuntimeError("Missing methodological norms")
    code, norms = markdown.split(marker, 1)
    labels = [
        match.group("number") for match in FISCAL_MARKDOWN_ARTICLE.finditer(code)
    ]
    base_articles = [int(label) for label in labels if "^" not in label]
    inserted = [label for label in labels if "^" in label]
    if base_articles != list(range(1, 504)):
        raise RuntimeError("Codul fiscal articles are incomplete or reordered")
    if len(inserted) != 118 or len(set(inserted)) != 118:
        raise RuntimeError("Unexpected inserted fiscal articles")
    if code.count("_Articol omis din ediția consolidată furnizată._") != 4:
        raise RuntimeError("Unexpected count of omitted-article markers")

    expected_code = {
        r"(?m)^## TITLUL ": 13,
        r"(?m)^### CAPITOLUL ": 74,
        r"(?m)^#### SEC": 54,
        r"(?m)^##### SUBSEC": 5,
        r"(?m)^### ANEXA ": 6,
    }
    expected_norms = {
        r"(?m)^### TITLUL ": 10,
        r"(?m)^#### CAPITOLUL ": 59,
        r"(?m)^##### SEC": 233,
        r"(?m)^###### SUBSEC": 75,
        r"(?m)^#### ANEXA ": 60,
    }
    for part, expected in ((code, expected_code), (norms, expected_norms)):
        for pattern, count in expected.items():
            actual = len(re.findall(pattern, part))
            if actual != count:
                raise RuntimeError(
                    f"Unexpected fiscal structure count for {pattern}: "
                    f"{actual}, expected {count}"
                )
    for artifact in ("È™", "È›", "Äƒ", "Ã®", "Ã¢"):
        if artifact in markdown:
            raise RuntimeError(f"Encoding artifact remains: {artifact}")


def fiscal_part_boundaries(part: str) -> list[int]:
    headings = [
        (match.start(), len(match.group(1)))
        for match in re.finditer(r"(?m)^(#{2,6}) .+$", part)
    ]
    point_boundaries = [
        match.start() for match in re.finditer(r"(?m)^\d+(?:\.\d+)*\.\s", part)
    ]
    if not headings or headings[0][0] != 0:
        raise RuntimeError("Fiscal document part does not start with a heading")

    minimum = 30_500
    maximum = 58_800
    boundaries = [0]
    position = 0
    while len(part) - position > maximum:
        remaining = len(part) - position
        target = remaining / 2 if remaining <= 2 * maximum else 56_000

        preferred = [
            heading
            for heading in headings
            if heading[1] <= 5
            and position + minimum <= heading[0] <= position + maximum
            and (
                remaining > 2 * maximum
                or len(part) - heading[0] >= minimum
            )
        ]
        candidates = preferred or [
            heading
            for heading in headings
            if position + minimum <= heading[0] <= position + maximum
            and (
                remaining > 2 * maximum
                or len(part) - heading[0] >= minimum
            )
        ]
        if candidates:
            next_position, _ = min(
                candidates,
                key=lambda heading: abs((heading[0] - position) - target)
                + max(0, heading[1] - 3) * 650,
            )
        else:
            points = [
                point
                for point in point_boundaries
                if position + minimum <= point <= position + maximum
                and (
                    remaining > 2 * maximum
                    or len(part) - point >= minimum
                )
            ]
            if not points:
                raise RuntimeError(
                    f"No fiscal chunk boundary near character {position:,}"
                )
            next_position = min(
                points, key=lambda point: abs((point - position) - target)
            )
        boundaries.append(next_position)
        position = next_position
    boundaries.append(len(part))
    return boundaries


def fiscal_chunk_description(body: str, kind: str) -> str:
    headings = []
    for match in re.finditer(r"(?m)^#{2,6} (.+)$", body):
        heading = match.group(1).strip()
        if heading.startswith("Norme metodologice"):
            continue
        if heading.startswith("Articolul") and headings:
            continue
        if heading not in headings:
            headings.append(heading)
        if len(headings) == 3:
            break
    if not headings:
        return "continuarea dispozițiilor fiscale" if kind == "code" else "continuarea normelor metodologice"
    description = "; ".join(headings)
    return description if len(description) <= 280 else description[:277].rstrip() + "..."


def build_fiscal_chunks(markdown: str) -> list[FiscalBuiltChunk]:
    validate_fiscal_document(markdown)
    first_heading = markdown.index("## TITLUL ")
    norms_heading = markdown.index("## Norme metodologice")
    preamble = markdown[:first_heading].rstrip()
    parts = (
        ("code", markdown[first_heading:norms_heading]),
        ("norms", markdown[norms_heading:]),
    )
    expected_names: set[str] = set()
    built: list[FiscalBuiltChunk] = []

    for kind, part_text in parts:
        boundaries = fiscal_part_boundaries(part_text)
        for ordinal, (start, end) in enumerate(
            zip(boundaries, boundaries[1:]), 1
        ):
            body = part_text[start:end].strip() + "\n"
            description = fiscal_chunk_description(body, kind)
            if kind == "code":
                labels = [
                    match.group("number")
                    for match in FISCAL_MARKDOWN_ARTICLE.finditer(body)
                ]
                if not labels:
                    raise RuntimeError("Fiscal code chunk contains no article")
                first_article, last_article = labels[0], labels[-1]

                def filename_label(label: str) -> str:
                    base, *inserted = label.split("^", 1)
                    suffix = f"bis{inserted[0]}" if inserted else ""
                    return f"{int(base):04d}{suffix}"

                filename = (
                    f"cod_fiscal-art{filename_label(first_article)}-"
                    f"{filename_label(last_article)}.md"
                )
                fragment = f"Art. {first_article}-{last_article}"
                record = FiscalBuiltChunk(
                    OUTPUT / filename,
                    kind,
                    description,
                    first_article,
                    last_article,
                )
            else:
                filename = f"cod_fiscal-norme-part{ordinal:02d}.md"
                fragment = f"Norme metodologice — partea {ordinal}"
                record = FiscalBuiltChunk(
                    OUTPUT / filename,
                    kind,
                    description,
                    part=ordinal,
                )

            content = (
                f"{preamble}\n"
                f"**Fragment:** {fragment}\n"
                f"**Cuprins:** {description}.\n\n"
                f"{body}"
            )
            if not MIN_CHUNK_CHARACTERS <= len(content) <= MAX_CHUNK_CHARACTERS:
                raise RuntimeError(
                    f"{filename} has {len(content):,} characters; expected "
                    f"{MIN_CHUNK_CHARACTERS:,}-{MAX_CHUNK_CHARACTERS:,}"
                )
            record.path.write_text(content, encoding="utf-8", newline="\n")
            expected_names.add(filename)
            built.append(record)
            print(f"{filename}: {record.path.stat().st_size:,} bytes")

    for stale in OUTPUT.glob("cod_fiscal-*.md"):
        if stale.name not in expected_names:
            stale.unlink()
    return built


def fiscal_catalog_block(built: list[FiscalBuiltChunk]) -> str:
    entries = []
    for chunk in built:
        if chunk.kind == "code":
            prefix = (
                "- Codul fiscal (Legea nr. 227/2015; actualizat prin O.U.G. "
                "nr. 8/2026)"
            )
            range_label = f"Art. {chunk.first_article}-{chunk.last_article}."
        else:
            prefix = (
                "- Codul fiscal — Normele metodologice aprobate prin H.G. "
                "nr. 1/2016, actualizate prin H.G. nr. 602/2025"
            )
            range_label = f"Partea {chunk.part}."
        entries.append(
            f"{prefix} — {chunk.description}. {range_label}\n"
            f"  {PUBLIC_BASE_URL}/{chunk.path.name}\n"
        )
    return "\n".join(entries) + "\n"


def update_fiscal_catalog(built: list[FiscalBuiltChunk]) -> None:
    data = CATALOG.read_text(encoding="utf-8")
    entry_pattern = re.compile(
        r"(?m)^- Codul fiscal [^\n]*\n"
        r"  https://[^\n]*/sources/cod_fiscal-[^\n]*\n(?:\n)?"
    )
    matches = list(entry_pattern.finditer(data))
    if not matches:
        raise RuntimeError("No existing Codul fiscal catalog entries found")
    start, end = matches[0].start(), matches[-1].end()
    if entry_pattern.sub("", data[start:end]).strip():
        raise RuntimeError("Codul fiscal catalog entries are not contiguous")
    CATALOG.write_text(
        data[:start] + fiscal_catalog_block(built) + data[end:],
        encoding="utf-8",
        newline="\n",
    )


def build_fiscal_document(raw_source: str) -> None:
    markdown = format_fiscal_markdown(clean_fiscal_source(raw_source))
    FISCAL_SOURCE.write_text(markdown, encoding="utf-8", newline="\n")
    built = build_fiscal_chunks(markdown)
    update_fiscal_catalog(built)

    for legacy_chunk in OUTPUT.glob("cod_fiscal-p*.pdf"):
        legacy_chunk.unlink()
    for legacy_source in ROOT.glob("cod_fiscal-*.pdf"):
        legacy_source.unlink()
    for legacy_text in FISCAL_LEGACY_TEXT_SOURCES:
        if legacy_text.exists():
            legacy_text.unlink()


@dataclass(frozen=True)
class ProcedureFiscalBuiltChunk:
    path: Path
    kind: str
    description: str
    first_article: str | None = None
    last_article: str | None = None
    part: int | None = None


def clean_procedure_fiscal_source(text: str) -> str:
    text = text.removeprefix("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    if text.startswith("# Codul de procedură fiscală\n"):
        return text.rstrip() + "\n"
    lines = []
    for raw_line in text.splitlines():
        line = repair_fiscal_mojibake(raw_line)
        line = re.sub(r"^\d+>ART\.", "ART.", line)
        lines.append(line)
    return "\n".join(lines).rstrip() + "\n"


def procedure_fiscal_structure(
    line: str,
) -> tuple[str, re.Match[str]] | None:
    for kind, pattern in (
        ("title", PROCEDURE_FISCAL_TITLE),
        ("chapter", PROCEDURE_FISCAL_CHAPTER),
        ("section", PROCEDURE_FISCAL_SECTION),
    ):
        match = pattern.fullmatch(line)
        if match:
            return kind, match
    return None


def procedure_fiscal_heading_stop(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return True
    if procedure_fiscal_structure(stripped):
        return True
    if PROCEDURE_FISCAL_ARTICLE.fullmatch(stripped):
        return True
    if PROCEDURE_FISCAL_ANNEX.fullmatch(stripped):
        return True
    if PROCEDURE_FISCAL_PART.fullmatch(stripped):
        return True
    if stripped.startswith(("(", "[", "*")):
        return True
    if re.match(r"^(?:\d+|[A-ZĂÂÎȘȚ])\.\s*", stripped):
        return True
    return False


def procedure_fiscal_full_heading(
    lines: list[str],
    index: int,
    label: str,
    title: str,
    conservative: bool = False,
) -> tuple[str, int]:
    continuations = []
    while index + 1 < len(lines) and len(continuations) < 5:
        candidate = lines[index + 1].strip()
        if procedure_fiscal_heading_stop(candidate):
            break
        current = continuations[-1] if continuations else title
        if conservative and current:
            if re.match(
                r"^(?:Prezenta|Următoarele|În sensul|Entitatea|Un utilizator|"
                r"O entitate|A\. |B\. |C\. )",
                candidate,
                re.IGNORECASE,
            ):
                break
            connector = current.rstrip().split()[-1].lower() in {
                "a",
                "al",
                "ale",
                "cu",
                "de",
                "în",
                "la",
                "pentru",
                "privește",
                "privind",
                "și",
            }
            if not (candidate[0].islower() or connector or len(candidate) < 30):
                break
        continuations.append(candidate)
        index += 1
    full_title = " ".join(part for part in [title, *continuations] if part)
    if not full_title:
        raise RuntimeError(f"Missing fiscal-procedure heading title after {label}")
    return full_title, index


def format_procedure_fiscal_markdown(text: str) -> str:
    if text.startswith("# Codul de procedură fiscală\n"):
        return normalize_heading_spacing(text)

    lines = text.splitlines()
    try:
        start = next(
            index
            for index, line in enumerate(lines)
            if line.startswith("TITLUL I Dispozi")
        )
        annex_start = next(
            index
            for index in range(start, len(lines))
            if re.match(r"^ANEXA\s+1\b", lines[index])
        )
    except StopIteration as error:
        raise RuntimeError("Could not locate Codul de procedură fiscală") from error

    rendered = [
        "# Codul de procedură fiscală",
        "Legea nr. 207/2015 privind Codul de procedură fiscală",
        "Forma consolidată: O.U.G. nr. 7/2026",
        "Text furnizat în scop documentar; nu reprezintă o republicare oficială.",
    ]
    current_article = 0
    inserted_articles: list[str] = []
    index = start

    while index < len(lines):
        raw_line = lines[index].rstrip()
        line = raw_line.strip()
        if line in {"Ordine de", "aplicare"}:
            index += 1
            continue

        article = PROCEDURE_FISCAL_ARTICLE.fullmatch(line)
        if article and index < annex_start:
            raw_number = article.group("raw_number").replace(" ", "")
            number = int(raw_number)
            if number == current_article + 1:
                label = raw_number
                current_article = number
            else:
                candidates = [
                    base
                    for base in range(1, current_article + 1)
                    if raw_number.startswith(str(base))
                    and len(raw_number) > len(str(base))
                ]
                if not candidates:
                    raise RuntimeError(
                        f"Unexpected fiscal-procedure article {raw_number} "
                        f"after {current_article}"
                    )
                base = max(candidates, key=lambda value: len(str(value)))
                label = f"{base}^{raw_number[len(str(base)):]}"
                inserted_articles.append(label)

            title = article.group("title").strip().lstrip("- ")
            if not title and index + 1 < len(lines):
                candidate = lines[index + 1].strip().lstrip("- ")
                if candidate and not procedure_fiscal_heading_stop(candidate):
                    title = candidate
                    index += 1
            rendered.append(
                f"###### Articolul {label}" + (f" — {title}" if title else "")
            )
            index += 1
            continue

        structure = procedure_fiscal_structure(line)
        if structure:
            kind, match = structure
            label = match.group("label").strip()
            title = (match.group("title") or "").strip()
            if kind == "chapter" and match.group("inserted"):
                label = (
                    f"CAPITOLUL {match.group('roman')}^"
                    f"{match.group('inserted')}"
                )
            full_title, index = procedure_fiscal_full_heading(
                lines,
                index,
                label,
                title,
                conservative=index >= annex_start,
            )
            levels = {"title": 2, "chapter": 3, "section": 4}
            if index >= annex_start and kind == "section":
                levels["section"] = 3
            rendered.append(f"{'#' * levels[kind]} {label} — {full_title}")
            index += 1
            continue

        annex = PROCEDURE_FISCAL_ANNEX.fullmatch(line)
        if annex:
            label = f"ANEXA {annex.group('number')}"
            title = (annex.group("title") or "").strip()
            full_title, index = procedure_fiscal_full_heading(
                lines, index, label, title, conservative=True
            )
            rendered.append(f"## {label} — {full_title}")
            index += 1
            continue

        part = PROCEDURE_FISCAL_PART.fullmatch(line)
        if part and index >= annex_start:
            label = part.group("label")
            title = ""
            if index + 1 < len(lines):
                candidate = lines[index + 1].strip()
                if candidate and not procedure_fiscal_heading_stop(candidate):
                    title = candidate
                    index += 1
            rendered.append(f"### {label}" + (f" — {title}" if title else ""))
            index += 1
            continue

        rendered.append(raw_line)
        index += 1

    if current_article != 354:
        raise RuntimeError(
            f"Codul de procedură fiscală ended at article {current_article}"
        )
    if len(inserted_articles) != 74 or len(set(inserted_articles)) != 74:
        raise RuntimeError(
            f"Expected 74 inserted fiscal-procedure articles, found "
            f"{len(inserted_articles)}"
        )
    return normalize_heading_spacing("\n".join(rendered))


def validate_procedure_fiscal_document(markdown: str) -> None:
    marker = "## ANEXA 1"
    if marker not in markdown:
        raise RuntimeError("Missing fiscal-procedure annexes")
    code, annexes = markdown.split(marker, 1)
    labels = [
        match.group("number")
        for match in PROCEDURE_FISCAL_MARKDOWN_ARTICLE.finditer(code)
    ]
    base_articles = [int(label) for label in labels if "^" not in label]
    inserted = [label for label in labels if "^" in label]
    if base_articles != list(range(1, 355)):
        raise RuntimeError(
            "Codul de procedură fiscală articles are incomplete or reordered"
        )
    if len(inserted) != 74 or len(set(inserted)) != 74:
        raise RuntimeError("Unexpected inserted fiscal-procedure articles")

    expected_code = {
        r"(?m)^## TITLUL ": 12,
        r"(?m)^### CAPITOLUL ": 48,
        r"(?m)^#### SEC": 27,
    }
    expected_annexes = {
        r"(?m)^## ANEXA ": 6,
        r"(?m)^### (?:SEC|Sec)": 21,
        r"(?m)^### Partea ": 2,
    }
    for part, expected in ((code, expected_code), (annexes, expected_annexes)):
        for pattern, count in expected.items():
            actual = len(re.findall(pattern, part))
            if actual != count:
                raise RuntimeError(
                    f"Unexpected fiscal-procedure structure count for {pattern}: "
                    f"{actual}, expected {count}"
                )
    for artifact in ("Ordine de\naplicare", ">ART.", "Ã", "Ä", "Å", "È", "â€"):
        if artifact in markdown:
            raise RuntimeError(f"Extraction artifact remains: {artifact}")


def build_procedure_fiscal_chunks(
    markdown: str,
) -> list[ProcedureFiscalBuiltChunk]:
    validate_procedure_fiscal_document(markdown)
    first_heading = markdown.index("## TITLUL ")
    annex_heading = markdown.index("## ANEXA 1")
    preamble = markdown[:first_heading].rstrip()
    parts = (
        ("code", markdown[first_heading:annex_heading]),
        ("annexes", markdown[annex_heading:]),
    )
    expected_names: set[str] = set()
    built: list[ProcedureFiscalBuiltChunk] = []

    for kind, part_text in parts:
        boundaries = fiscal_part_boundaries(part_text)
        for ordinal, (start, end) in enumerate(
            zip(boundaries, boundaries[1:]), 1
        ):
            body = part_text[start:end].strip() + "\n"
            description = fiscal_chunk_description(body, kind)
            if kind == "code":
                labels = [
                    match.group("number")
                    for match in PROCEDURE_FISCAL_MARKDOWN_ARTICLE.finditer(body)
                ]
                if not labels:
                    raise RuntimeError(
                        "Fiscal-procedure code chunk contains no article"
                    )

                def article_key(label: str) -> tuple[int, int]:
                    base, *inserted = label.split("^", 1)
                    return int(base), int(inserted[0]) if inserted else 0

                first_article = min(labels, key=article_key)
                last_article = max(labels, key=article_key)

                def filename_label(label: str) -> str:
                    base, *inserted = label.split("^", 1)
                    suffix = f"bis{inserted[0]}" if inserted else ""
                    return f"{int(base):04d}{suffix}"

                filename = (
                    f"cod_procedura_fiscala-art{filename_label(first_article)}-"
                    f"{filename_label(last_article)}.md"
                )
                fragment = f"Art. {first_article}-{last_article}"
                record = ProcedureFiscalBuiltChunk(
                    OUTPUT / filename,
                    kind,
                    description,
                    first_article,
                    last_article,
                )
            else:
                filename = f"cod_procedura_fiscala-anexe-part{ordinal:02d}.md"
                fragment = f"Anexele Codului — partea {ordinal}"
                record = ProcedureFiscalBuiltChunk(
                    OUTPUT / filename,
                    kind,
                    description,
                    part=ordinal,
                )

            content = (
                f"{preamble}\n"
                f"**Fragment:** {fragment}\n"
                f"**Cuprins:** {description}.\n\n"
                f"{body}"
            )
            if not MIN_CHUNK_CHARACTERS <= len(content) <= MAX_CHUNK_CHARACTERS:
                raise RuntimeError(
                    f"{filename} has {len(content):,} characters; expected "
                    f"{MIN_CHUNK_CHARACTERS:,}-{MAX_CHUNK_CHARACTERS:,}"
                )
            record.path.write_text(content, encoding="utf-8", newline="\n")
            expected_names.add(filename)
            built.append(record)
            print(f"{filename}: {record.path.stat().st_size:,} bytes")

    for stale in OUTPUT.glob("cod_procedura_fiscala-*.md"):
        if stale.name not in expected_names:
            stale.unlink()
    return built


def procedure_fiscal_catalog_block(
    built: list[ProcedureFiscalBuiltChunk],
) -> str:
    entries = []
    for chunk in built:
        if chunk.kind == "code":
            range_label = f"Art. {chunk.first_article}-{chunk.last_article}."
        else:
            range_label = f"Anexe — partea {chunk.part}."
        entries.append(
            "- Codul de procedură fiscală (Legea nr. 207/2015; actualizat prin "
            f"O.U.G. nr. 7/2026) — {chunk.description}. {range_label}\n"
            f"  {PUBLIC_BASE_URL}/{chunk.path.name}\n"
        )
    return "\n".join(entries) + "\n"


def update_procedure_fiscal_catalog(
    built: list[ProcedureFiscalBuiltChunk],
) -> None:
    data = CATALOG.read_text(encoding="utf-8")
    entry_pattern = re.compile(
        r"(?m)^- Codul de procedură fiscală [^\n]*\n"
        r"  https://[^\n]*/sources/cod_procedura_fiscala-[^\n]*"
        r"\n(?:\n)?"
    )
    matches = list(entry_pattern.finditer(data))
    if not matches:
        raise RuntimeError(
            "No existing Codul de procedură fiscală catalog entries found"
        )
    start, end = matches[0].start(), matches[-1].end()
    if entry_pattern.sub("", data[start:end]).strip():
        raise RuntimeError(
            "Codul de procedură fiscală catalog entries are not contiguous"
        )
    CATALOG.write_text(
        data[:start] + procedure_fiscal_catalog_block(built) + data[end:],
        encoding="utf-8",
        newline="\n",
    )


def build_procedure_fiscal_document(raw_source: str) -> None:
    markdown = format_procedure_fiscal_markdown(
        clean_procedure_fiscal_source(raw_source)
    )
    PROCEDURE_FISCAL_SOURCE.write_text(markdown, encoding="utf-8", newline="\n")
    built = build_procedure_fiscal_chunks(markdown)
    update_procedure_fiscal_catalog(built)

    for legacy_chunk in OUTPUT.glob("cod_procedura_fiscala-p*.pdf"):
        legacy_chunk.unlink()
    legacy_pdf = ROOT / "cod_procedura_fiscala.pdf"
    if legacy_pdf.exists():
        legacy_pdf.unlink()
    for legacy_text in PROCEDURE_FISCAL_LEGACY_TEXT_SOURCES:
        if legacy_text.exists():
            legacy_text.unlink()


@dataclass(frozen=True)
class Oug34BuiltChunk:
    path: Path
    first_article: int
    last_article: int
    description: str
    includes_annex: bool = False


def clean_oug34_source(text: str) -> str:
    text = text.removeprefix("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    if text.startswith("# O.U.G. nr. 34/2014\n"):
        return text.rstrip() + "\n"
    romanian_diacritics = str.maketrans("şŞţŢ", "șȘțȚ")
    return (
        "\n".join(
            repair_fiscal_mojibake(line).translate(romanian_diacritics).strip()
            for line in text.splitlines()
        )
        .rstrip()
        + "\n"
    )


def oug34_heading_title(lines: list[str], index: int) -> tuple[str, int]:
    """Read a heading title, including a lowercase wrapped continuation."""
    index += 1
    while index < len(lines) and not lines[index].strip():
        index += 1
    if index >= len(lines) or not lines[index].strip():
        raise RuntimeError("Missing O.U.G. nr. 34/2014 heading title")
    title_parts = [lines[index].strip()]
    index += 1
    while index < len(lines):
        candidate = lines[index].strip()
        if not candidate or not candidate[0].islower():
            break
        title_parts.append(candidate)
        index += 1
    return " ".join(title_parts), index


def format_oug34_markdown(text: str) -> str:
    if text.startswith("# O.U.G. nr. 34/2014\n"):
        return normalize_heading_spacing(text)

    lines = text.splitlines()
    try:
        preamble_start = next(
            index
            for index, line in enumerate(lines)
            if line.strip().startswith("Având în vedere că transpunerea")
        )
        chapter_start = next(
            index
            for index, line in enumerate(lines)
            if line.strip() == "CAPITOLUL I"
        )
    except StopIteration as error:
        raise RuntimeError("Could not locate O.U.G. nr. 34/2014 body") from error

    rendered = [
        "# O.U.G. nr. 34/2014",
        "Ordonanța de urgență nr. 34/2014 privind drepturile consumatorilor în cadrul contractelor încheiate cu profesioniștii, precum și pentru modificarea și completarea unor acte normative",
        "Publicată în Monitorul Oficial, Partea I, nr. 427 din 11 iunie 2014",
        "Forma inițială; intrată în vigoare la 13 iunie 2014.",
        "Text furnizat în scop documentar; nu reprezintă o republicare oficială.",
        "",
        "## Preambul",
        *[line.rstrip() for line in lines[preamble_start:chapter_start]],
    ]

    index = chapter_start
    while index < len(lines):
        raw_line = lines[index].rstrip()
        line = raw_line.strip()

        chapter = OUG34_CHAPTER.fullmatch(line)
        if chapter:
            title, index = oug34_heading_title(lines, index)
            rendered.append(f"## {line} — {title}")
            continue

        article = OUG34_ARTICLE.fullmatch(line)
        if article:
            title, index = oug34_heading_title(lines, index)
            rendered.append(
                f"### Articolul {article.group('number')} — {title}"
            )
            continue

        if line == "ANEXĂ":
            title, index = oug34_heading_title(lines, index)
            rendered.append(f"## ANEXĂ — {title}")
            continue

        if re.fullmatch(r"[AB]\. .+", line):
            rendered.append(f"### {line}")
            index += 1
            continue

        if line in {
            "Dreptul de retragere",
            "Consecințele retragerii",
            "Instrucțiuni de completare",
        }:
            rendered.append(f"#### {line}")
            index += 1
            continue

        rendered.append(raw_line)
        index += 1

    return normalize_heading_spacing("\n".join(rendered))


def validate_oug34_document(markdown: str) -> None:
    articles = [
        int(match.group("number"))
        for match in OUG34_MARKDOWN_ARTICLE.finditer(markdown)
    ]
    if articles != list(range(1, 33)):
        raise RuntimeError("O.U.G. nr. 34/2014 articles are incomplete or reordered")
    if len(re.findall(r"(?m)^## CAPITOLUL [IVXLCDM]+ — ", markdown)) != 7:
        raise RuntimeError("Unexpected O.U.G. nr. 34/2014 chapter count")
    if len(re.findall(r"(?m)^## ANEXĂ — ", markdown)) != 1:
        raise RuntimeError("Missing O.U.G. nr. 34/2014 annex")
    for artifact in ("Ã", "Â", "Å", "Ä", "È"):
        if artifact in markdown:
            raise RuntimeError(f"Encoding artifact remains: {artifact}")


def build_oug34_chunks(markdown: str) -> list[Oug34BuiltChunk]:
    validate_oug34_document(markdown)
    body_start = markdown.index("## Preambul")
    split = markdown.index("## CAPITOLUL VI —")
    preamble = markdown[:body_start].rstrip()
    specs = (
        (
            1,
            26,
            markdown[body_start:split],
            "preambulul; obiectul, definițiile și domeniul de aplicare; informarea și dreptul de retragere; celelalte drepturi ale consumatorilor și dispozițiile generale",
            False,
        ),
        (
            27,
            32,
            markdown[split:],
            "competența, sesizarea, controlul și sancțiunile; dispozițiile finale, intrarea în vigoare și abrogările; instrucțiunile și formularul-model de retragere",
            True,
        ),
    )
    built = []
    expected_names = set()
    for first, last, body, description, includes_annex in specs:
        suffix = "-anexa" if includes_annex else ""
        filename = f"oug_34_2014-art{first:03d}-{last:03d}{suffix}.md"
        fragment = f"Art. {first}-{last}" + (" și anexa" if includes_annex else "")
        content = (
            f"{preamble}\n"
            f"**Fragment:** {fragment}.\n"
            f"**Cuprins:** {description}.\n\n"
            f"{body.strip()}\n"
        )
        labels = [
            int(match.group("number"))
            for match in OUG34_MARKDOWN_ARTICLE.finditer(content)
        ]
        if labels != list(range(first, last + 1)):
            raise RuntimeError(f"Unexpected article range in {filename}")
        if not MIN_CHUNK_CHARACTERS <= len(content) <= MAX_CHUNK_CHARACTERS:
            raise RuntimeError(
                f"{filename} has {len(content):,} characters; expected "
                f"{MIN_CHUNK_CHARACTERS:,}-{MAX_CHUNK_CHARACTERS:,}"
            )
        path = OUTPUT / filename
        path.write_text(content, encoding="utf-8", newline="\n")
        built.append(
            Oug34BuiltChunk(path, first, last, description, includes_annex)
        )
        expected_names.add(filename)
        print(f"{filename}: {path.stat().st_size:,} bytes")

    for stale in OUTPUT.glob("oug_34_2014-*.md"):
        if stale.name not in expected_names:
            stale.unlink()
    return built


def oug34_catalog_block(built: list[Oug34BuiltChunk]) -> str:
    entries = []
    prefix = (
        "- OUG nr. 34/2014 privind drepturile consumatorilor în contractele "
        "încheiate cu profesioniștii (forma inițială, M.Of. nr. 427/2014)"
    )
    for chunk in built:
        range_label = f"Art. {chunk.first_article}-{chunk.last_article}"
        if chunk.includes_annex:
            range_label += " și anexa"
        entries.append(
            f"{prefix} — {chunk.description}. {range_label}.\n"
            f"  {PUBLIC_BASE_URL}/{chunk.path.name}\n"
        )
    return "\n".join(entries) + "\n"


def update_oug34_catalog(built: list[Oug34BuiltChunk]) -> None:
    data = CATALOG.read_text(encoding="utf-8")
    entry_pattern = re.compile(
        r"(?m)^- OUG nr\. 34/2014 [^\n]*\n"
        r"  https://[^\n]*/sources/oug_34_2014-[^\n]*\n(?:\n)?"
    )
    matches = list(entry_pattern.finditer(data))
    if not matches:
        raise RuntimeError("No existing O.U.G. nr. 34/2014 catalog entries found")
    start, end = matches[0].start(), matches[-1].end()
    if entry_pattern.sub("", data[start:end]).strip():
        raise RuntimeError("O.U.G. nr. 34/2014 catalog entries are not contiguous")
    CATALOG.write_text(
        data[:start] + oug34_catalog_block(built) + data[end:],
        encoding="utf-8",
        newline="\n",
    )


def build_oug34_document(raw_source: str) -> None:
    markdown = format_oug34_markdown(clean_oug34_source(raw_source))
    OUG34_SOURCE.write_text(markdown, encoding="utf-8", newline="\n")
    built = build_oug34_chunks(markdown)
    update_oug34_catalog(built)

    for legacy_chunk in OUTPUT.glob("oug_34_2014-p*.pdf"):
        legacy_chunk.unlink()
    legacy_pdf = ROOT / "oug_34_2014.pdf"
    if legacy_pdf.exists():
        legacy_pdf.unlink()
    for legacy_text in OUG34_LEGACY_TEXT_SOURCES:
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
    parser.add_argument(
        "--import-administrative-source",
        type=Path,
        help="import a supplied Codul administrativ TXT before building",
    )
    parser.add_argument(
        "--import-road-source",
        type=Path,
        help="import a supplied Codul rutier TXT before building",
    )
    parser.add_argument(
        "--import-penal-source",
        type=Path,
        help="import a supplied Codul penal TXT before building",
    )
    parser.add_argument(
        "--import-constitution-source",
        type=Path,
        help="import a supplied Romanian Constitution TXT before building",
    )
    parser.add_argument(
        "--import-civil-procedure-source",
        type=Path,
        help="import a supplied Codul de procedură civilă TXT before building",
    )
    parser.add_argument(
        "--import-fiscal-source",
        type=Path,
        help="import a supplied Codul fiscal TXT before building",
    )
    parser.add_argument(
        "--import-fiscal-procedure-source",
        type=Path,
        help="import a supplied Codul de procedură fiscală TXT before building",
    )
    parser.add_argument(
        "--import-oug34-source",
        type=Path,
        help="import a supplied O.U.G. nr. 34/2014 TXT before building",
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

    administrative_raw_source = None
    if args.import_administrative_source:
        if not args.import_administrative_source.is_file():
            raise FileNotFoundError(args.import_administrative_source)
        administrative_raw_source = args.import_administrative_source.read_text(
            encoding="utf-8-sig"
        )
    elif ADMINISTRATIVE_SOURCE.is_file():
        administrative_raw_source = ADMINISTRATIVE_SOURCE.read_text(
            encoding="utf-8-sig"
        )
    else:
        administrative_legacy = next(
            (
                path
                for path in ADMINISTRATIVE_LEGACY_TEXT_SOURCES
                if path.is_file()
            ),
            None,
        )
        if administrative_legacy:
            administrative_raw_source = administrative_legacy.read_text(
                encoding="utf-8-sig"
            )

    if administrative_raw_source is not None:
        build_administrative_document(administrative_raw_source)

    road_raw_source = None
    if args.import_road_source:
        if not args.import_road_source.is_file():
            raise FileNotFoundError(args.import_road_source)
        road_raw_source = args.import_road_source.read_text(encoding="utf-8-sig")
    elif ROAD_SOURCE.is_file():
        road_raw_source = ROAD_SOURCE.read_text(encoding="utf-8-sig")
    else:
        road_legacy = next(
            (path for path in ROAD_LEGACY_TEXT_SOURCES if path.is_file()), None
        )
        if road_legacy:
            road_raw_source = road_legacy.read_text(encoding="utf-8-sig")

    if road_raw_source is not None:
        build_road_document(road_raw_source)

    penal_raw_source = None
    if args.import_penal_source:
        if not args.import_penal_source.is_file():
            raise FileNotFoundError(args.import_penal_source)
        penal_raw_source = args.import_penal_source.read_text(encoding="utf-8-sig")
    elif PENAL_SOURCE.is_file():
        penal_raw_source = PENAL_SOURCE.read_text(encoding="utf-8-sig")
    else:
        penal_legacy = next(
            (path for path in PENAL_LEGACY_TEXT_SOURCES if path.is_file()), None
        )
        if penal_legacy:
            penal_raw_source = penal_legacy.read_text(encoding="utf-8-sig")

    if penal_raw_source is not None:
        build_penal_document(penal_raw_source)

    constitution_raw_source = None
    if args.import_constitution_source:
        if not args.import_constitution_source.is_file():
            raise FileNotFoundError(args.import_constitution_source)
        constitution_raw_source = args.import_constitution_source.read_text(
            encoding="utf-8-sig"
        )
    elif CONSTITUTION_SOURCE.is_file():
        constitution_raw_source = CONSTITUTION_SOURCE.read_text(encoding="utf-8-sig")
    else:
        constitution_legacy = next(
            (
                path
                for path in CONSTITUTION_LEGACY_TEXT_SOURCES
                if path.is_file()
            ),
            None,
        )
        if constitution_legacy:
            constitution_raw_source = constitution_legacy.read_text(
                encoding="utf-8-sig"
            )

    if constitution_raw_source is not None:
        build_constitution_document(constitution_raw_source)

    procedure_civil_raw_source = None
    if args.import_civil_procedure_source:
        if not args.import_civil_procedure_source.is_file():
            raise FileNotFoundError(args.import_civil_procedure_source)
        procedure_civil_raw_source = args.import_civil_procedure_source.read_text(
            encoding="utf-8-sig"
        )
    elif PROCEDURE_CIVIL_SOURCE.is_file():
        procedure_civil_raw_source = PROCEDURE_CIVIL_SOURCE.read_text(
            encoding="utf-8-sig"
        )
    else:
        procedure_civil_legacy = next(
            (
                path
                for path in PROCEDURE_CIVIL_LEGACY_TEXT_SOURCES
                if path.is_file()
            ),
            None,
        )
        if procedure_civil_legacy:
            procedure_civil_raw_source = procedure_civil_legacy.read_text(
                encoding="utf-8-sig"
            )

    if procedure_civil_raw_source is not None:
        build_procedure_civil_document(procedure_civil_raw_source)

    fiscal_raw_source = None
    if args.import_fiscal_source:
        if not args.import_fiscal_source.is_file():
            raise FileNotFoundError(args.import_fiscal_source)
        fiscal_raw_source = args.import_fiscal_source.read_text(encoding="utf-8-sig")
    elif FISCAL_SOURCE.is_file():
        fiscal_raw_source = FISCAL_SOURCE.read_text(encoding="utf-8-sig")
    else:
        fiscal_legacy = next(
            (path for path in FISCAL_LEGACY_TEXT_SOURCES if path.is_file()), None
        )
        if fiscal_legacy:
            fiscal_raw_source = fiscal_legacy.read_text(encoding="utf-8-sig")

    if fiscal_raw_source is not None:
        build_fiscal_document(fiscal_raw_source)

    procedure_fiscal_raw_source = None
    if args.import_fiscal_procedure_source:
        if not args.import_fiscal_procedure_source.is_file():
            raise FileNotFoundError(args.import_fiscal_procedure_source)
        procedure_fiscal_raw_source = args.import_fiscal_procedure_source.read_text(
            encoding="utf-8-sig"
        )
    elif PROCEDURE_FISCAL_SOURCE.is_file():
        procedure_fiscal_raw_source = PROCEDURE_FISCAL_SOURCE.read_text(
            encoding="utf-8-sig"
        )
    else:
        procedure_fiscal_legacy = next(
            (
                path
                for path in PROCEDURE_FISCAL_LEGACY_TEXT_SOURCES
                if path.is_file()
            ),
            None,
        )
        if procedure_fiscal_legacy:
            procedure_fiscal_raw_source = procedure_fiscal_legacy.read_text(
                encoding="utf-8-sig"
            )

    if procedure_fiscal_raw_source is not None:
        build_procedure_fiscal_document(procedure_fiscal_raw_source)

    oug34_raw_source = None
    if args.import_oug34_source:
        if not args.import_oug34_source.is_file():
            raise FileNotFoundError(args.import_oug34_source)
        oug34_raw_source = args.import_oug34_source.read_text(encoding="utf-8-sig")
    elif OUG34_SOURCE.is_file():
        oug34_raw_source = OUG34_SOURCE.read_text(encoding="utf-8-sig")
    else:
        oug34_legacy = next(
            (path for path in OUG34_LEGACY_TEXT_SOURCES if path.is_file()), None
        )
        if oug34_legacy:
            oug34_raw_source = oug34_legacy.read_text(encoding="utf-8-sig")

    if oug34_raw_source is not None:
        build_oug34_document(oug34_raw_source)


if __name__ == "__main__":
    main()
