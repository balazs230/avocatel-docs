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


if __name__ == "__main__":
    main()
