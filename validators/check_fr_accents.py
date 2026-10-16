#!/usr/bin/env python3
"""check_fr_accents.py - negative accent scan for the FR fields of a static meta.yml.

Why this exists
---------------
FR content has shipped accent-stripped more than once (wiki, box briefs, ROLLR):
the author typed flat ASCII and then asserted the accents were there. Reading the
text is not a check. This is.

What it does
------------
For every FR field of a static-challenge meta.yml (`description_fr`,
`technique_fr`, `hints_fr`, and any other `*_fr` string or list of strings), it:

  1. strips the parts of the text where flat ASCII is CORRECT and expected:
       - inline code spans between backticks (`bytes.fromhex(...)`)
       - fenced code blocks
       - URLs (http://, https://)
       - ALL-CAPS identifiers such as SEG_INDEX, CKSUM, VBAT, FSPL, ESPILON
       - anything inside {curly braces} (flag shapes and placeholders)
  2. scans what is left, word by word, against a dictionary of French words whose
     ONLY correct spelling carries an accent, and fails on the naked ASCII form.
  3. additionally asserts each FR field contains at least one accented character
     at all, which catches a wholesale accent strip that the word list missed.

It also scans the SHIPPED BILINGUAL DOCUMENTS a challenge declares under
`fr_docs:` in its meta.yml - the player-facing markdown that goes out inside
files/, such as a flash guide or a player note. Those files are the FR text a
player actually reads, and until they were declared here nothing checked them
at all: the meta.yml FR fields could be perfect while the downloaded document
was flat ASCII. Each entry is:

    fr_docs:
      - path: files/NOTE-JOUEUR.md
        require: [etape-with-its-accent, ...]

The document is split into its EN and FR halves by tools/bilingual_doc.py (one
rule, shared with tools/check_flash_instructions.py) and ONLY the FR half is
scanned - the word lists below are French words, and English prose legitimately
contains "cable" and "controle". A document with no FR half fails, which is
what makes "we forgot to translate it" and "the FR heading lost its cedilla"
both loud.

Usage
-----
    python3 tools/check_fr_accents.py challenges/static/satellite/cubesat-beacon
    python3 tools/check_fr_accents.py path/to/meta.yml [more...]
    python3 tools/check_fr_accents.py --all

Exit code is 0 only if every scanned FR field is clean.

Dependencies: stdlib + pyyaml (same as validate_static_meta.py).
"""
from __future__ import annotations

import os
import re
import sys
import unicodedata

# ---------------------------------------------------------------------------
# Words whose only correct French spelling carries an accent. If the naked
# ASCII form appears as a standalone word in an FR field, the text was stripped.
# Keep this list conservative: every entry must be a word that is NEVER correct
# without its accent in running French prose.
# ---------------------------------------------------------------------------
_WORDLIST = frozenset({
    # e-acute / e-grave / e-circumflex words
    "acces", "apres", "arrivee", "arrivees", "caractere", "caracteres",
    "cle", "cles", "completement", "consecutif", "consecutifs",
    "consecutive", "consecutives", "deja", "demarrage", "derniere",
    "dernieres", "desormais", "detaille", "detaillee", "different",
    "differente", "differentes", "differents", "donnee", "donnees",
    # NOT "dote": "doter" carries no diacritic in its root, so the present
    # "ce module dote la carte de..." and the imperative are correctly flat.
    # Only the participle "dotée" is always accented, and "dotee" stays listed.
    "dotee", "ecart", "ecarte", "ecartes", "echec", "echoue",
    "echouent", "ecrit", "ecrite", "ecrites", "ecrits", "electrique",
    "element", "elements", "eleve", "elevee", "emet", "emettre",
    "energie", "equipe", "etage", "etait", "etaient", "etape", "etapes",
    "etat", "etats", "extremite", "frequence", "frequences", "genere",
    # NOT "identifie": unlike "génère" or "spécifie", the root of "identifier"
    # carries no diacritic, so "il identifie" and the imperative "Identifie-le"
    # are correctly spelled flat. Only the participle "identifiée" is always
    # accented, and the é/e participle pair is what
    # tools/check_static_fr_parity.py judges from the corpus.
    "generee", "hexadecimal", "hexadecimale", "identifiee",
    "kilometre", "kilometres", "liee", "maniere", "materiel", "metre",
    "metres", "modele", "necessaire", "necessite", "numerique",
    "parametre", "parametres", "particuliere", "periode", "precis",
    "precise", "precisement", "premiere", "premieres", "presente",
    "presentes", "probleme", "problemes", "procede", "reference",
    # NOT "requiert": "requérir" moves its accent off the stem in this person
    # ("il requiert", like "il acquiert"), so no accented spelling of this exact
    # token exists at all and the entry could only ever fire on correct French.
    "repartie", "repartis", "reseau", "resultat", "resultats",
    "reussi", "securite", "separe", "separee", "specifie", "systeme",
    "systemes", "telemetrie", "temperature", "temperatures", "tres",
    "verifie", "verifier", "verification", "verifiee", "reception",
    "recepteur", "emetteur", "prevue", "prevu", "degre", "degres",
    "reel", "reelle", "reelles", "reels", "theorique", "theoriques",
    "bruitee", "bruite",
    # ---- orphan words: correct nowhere else in the repo -------------------
    # A corpus-derived rule (tools/check_course_fr_accents.py) can only forbid a
    # flat token when some OTHER course writes the accented spelling. These words
    # are written correctly in exactly one place each, so the corpus has nothing
    # to compare against and they are invisible to it. This curated list is the
    # documented floor for precisely that case, so they are added by hand.
    #
    # Each was judged individually against the rule at the top of this file: an
    # entry must be a word that is NEVER correct without its accent. Three
    # candidates were REJECTED for failing that test, and are recorded here so
    # the decision is not made again:
    #   boucle  - "la boucle principale" is the correct French noun (104 uses
    #             across 30 courses) and "il boucle" is the correct verb.
    #   stripe  - the jargon verb "striper" carries no diacritic in its root, so
    #             "stripe le binaire" is correctly flat, exactly like "identifie".
    #   stripes - same root, and elf-anatomy already ships the correct second
    #             person "Tu stripes un binaire", which this entry would fail.
    "decompileur", "emulant", "emulee", "evacuer", "genial", "gerees",
    "hashee", "menera", "penible", "similarite",
    # "re-" takes an accent before a vowel in French ("reimport" is only ever
    # "réimport"); a code identifier spelled this way belongs in backticks,
    # which are stripped before the scan.
    "reimport",
})

# Cedilla-only and circumflex-only losses: the naked form still looks like a
# plausible token, but in running French prose it is simply wrong.
_DIACRITIC_ONLY = frozenset({
    "recu", "recue", "recues", "recus", "concu", "concue", "lecon", "lecons",
    "francais", "francaise", "cablage", "cable", "cables", "controle",
    "controles", "interet", "interets", "meme", "memes", "etre", "entete",
    "cout", "couts", "plutot", "fenetre", "fenetres",
})

_CODE_SPAN = re.compile(r"`[^`]*`")
_CODE_FENCE = re.compile(r"```.*?```", re.DOTALL)
_URL = re.compile(r"https?://\S+")
_BRACED = re.compile(r"\{[^}]*\}")
_ALLCAPS = re.compile(r"\b[A-Z][A-Z0-9_\-]{1,}\b")
_WORD = re.compile(r"[A-Za-zÀ-ſ]+")


def _yaml():
    try:
        import yaml
    except ImportError:  # pragma: no cover - environment guard
        sys.exit("ERROR: pyyaml is not installed -- pip install pyyaml")
    return yaml


def strip_non_prose(text: str) -> str:
    """Remove the regions where flat ASCII is correct: code, URLs, identifiers."""
    text = _CODE_FENCE.sub(" ", text)
    text = _CODE_SPAN.sub(" ", text)
    text = _URL.sub(" ", text)
    text = _BRACED.sub(" ", text)
    text = _ALLCAPS.sub(" ", text)
    return text


def has_accent(text: str) -> bool:
    return any(unicodedata.combining(c) for c in unicodedata.normalize("NFD", text))


def is_non_ascii_french(text: str) -> bool:
    """True if the token cannot be typed in flat ASCII without losing something.

    Wider than has_accent on purpose: the ligatures oe and ae ('oeil', 'coeur',
    'soeur') carry no combining mark, so has_accent calls them plain, yet they
    are exactly the characters an ASCII-flattening editor destroys. Used only
    to judge whether an fr_accent_check entry asserts anything.
    """
    return has_accent(text) or any(ord(c) > 127 for c in text)


def scan_string(label: str, text: str) -> list[str]:
    """Return the accent problems found in one FR string."""
    errs: list[str] = []
    prose = strip_non_prose(text)

    if not has_accent(prose):
        errs.append(
            f"{label}: no accented character anywhere in the prose "
            f"-- this field looks accent-stripped"
        )

    seen: set[str] = set()
    for match in _WORD.finditer(prose):
        word = match.group(0)
        low = word.lower()
        if low in seen:
            continue
        if low in _WORDLIST or low in _DIACRITIC_ONLY:
            seen.add(low)
            errs.append(
                f"{label}: accent-stripped word {word!r} "
                f"(character {match.start()}) -- write it with its accent"
            )
    return errs


def _fr_fields(data: dict):
    """Yield (label, string) for every FR field, flattening lists."""
    for key in sorted(data):
        if not key.endswith("_fr"):
            continue
        val = data[key]
        if isinstance(val, str):
            yield key, val
        elif isinstance(val, list):
            for i, item in enumerate(val):
                if isinstance(item, str):
                    yield f"{key}[{i}]", item


def check_meta(meta_path: str) -> list[str]:
    yaml = _yaml()
    if not os.path.isfile(meta_path):
        return [f"{meta_path}  not found"]
    with open(meta_path, "r", encoding="utf-8") as fh:
        try:
            data = yaml.safe_load(fh)
        except yaml.YAMLError as exc:
            return [f"{meta_path}  YAML error: {exc}"]
    if not isinstance(data, dict):
        return [f"{meta_path}  top-level document is not a mapping"]

    fields = list(_fr_fields(data))
    if not fields:
        return [f"{meta_path}  no *_fr fields at all -- FR content is missing"]

    errs: list[str] = []
    for label, text in fields:
        errs.extend(f"{meta_path}  {e}" for e in scan_string(label, text))
    errs.extend(f"{meta_path}  {e}" for e in check_expected_words(data, fields))
    errs.extend(f"{meta_path}  {e}" for e in check_fr_docs(meta_path, data))
    return errs


def check_fr_docs(meta_path: str, data: dict) -> list[str]:
    """Scan every shipped bilingual document declared under `fr_docs:`.

    A meta.yml's *_fr fields are the platform's copy of the text. `fr_docs`
    covers the OTHER copy: the markdown that ships inside files/ and that the
    player opens after downloading. Same two assertions as for an FR field (a
    negative scan for accent-stripped words, plus a positive per-word list),
    applied to the FR half only.

    `require` is not optional. A document declared here with nothing required
    of it would pass on the word list alone, and the whole reason this repo
    has a positive assertion is that the negative scan only knows the words it
    already knows.
    """
    docs = data.get("fr_docs")
    if docs is None:
        return []
    if not isinstance(docs, list) or not docs:
        return ["fr_docs: must be a non-empty list of {path, require} mappings"]

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from bilingual_doc import BilingualError, split_bilingual

    chall_dir = os.path.dirname(os.path.abspath(meta_path))
    errs: list[str] = []
    for i, entry in enumerate(docs):
        label = f"fr_docs[{i}]"
        if not isinstance(entry, dict) or not entry.get("path"):
            errs.append(f"{label}: needs a `path` relative to the challenge directory")
            continue
        rel = entry["path"]
        label = f"fr_docs[{rel}]"
        path = os.path.join(chall_dir, rel)
        if not os.path.isfile(path):
            errs.append(f"{label}: declared but not on disk")
            continue
        text = open(path, "r", encoding="utf-8").read()
        try:
            _en, fr = split_bilingual(text)
        except BilingualError as exc:
            errs.append(f"{label}: {exc}")
            continue

        errs.extend(scan_string(label, fr))

        required = entry.get("require")
        if not isinstance(required, list) or not required:
            errs.append(
                f"{label}: needs a non-empty `require` list. Declaring a document "
                f"without asserting a single word in it proves nothing the "
                f"negative scan did not already try"
            )
            continue
        haystack = strip_non_prose(fr)
        for word in required:
            if not isinstance(word, str) or not word.strip():
                errs.append(f"{label}: require entries must be non-empty strings")
                continue
            word = word.strip()
            if not is_non_ascii_french(word):
                errs.append(
                    f"{label}: required word {word!r} is plain ASCII, so asserting "
                    f"it proves nothing -- list a word whose correct spelling needs "
                    f"an accent or a ligature"
                )
                continue
            if word not in haystack:
                errs.append(
                    f"{label}: required word {word!r} does not appear in the FR half "
                    f"-- either the accent was stripped or the text was reworded "
                    f"without updating the list"
                )
    return errs


def check_expected_words(data: dict, fields) -> list[str]:
    """Positive assertion driven by an optional `fr_accent_check` list.

    The negative scan above can only catch words it already knows. A brief with
    few accents, or one whose stripped words are not in the list, passes it
    while still reading as broken French. So a meta.yml may also declare the
    words that MUST appear, accented exactly as written, in its FR text -- the
    same convention tools/box_briefs.json uses. This is what makes the check
    per-string and specific rather than a bulk accent count.

    Each entry must (a) carry at least one accent itself, otherwise it asserts
    nothing, and (b) appear verbatim in the concatenated FR fields. Reword an FR
    field and this list has to be updated with it, which is the point.
    """
    expected = data.get("fr_accent_check")
    if expected is None:
        return []
    if not isinstance(expected, list):
        return ["fr_accent_check: must be a list of words"]

    haystack = "\n".join(text for _label, text in fields)
    errs: list[str] = []
    for word in expected:
        if not isinstance(word, str) or not word.strip():
            errs.append("fr_accent_check: entries must be non-empty strings")
            continue
        word = word.strip()
        if not is_non_ascii_french(word):
            errs.append(
                f"fr_accent_check: {word!r} is plain ASCII, so asserting it "
                f"proves nothing -- list a word whose correct spelling needs an "
                f"accent or a ligature"
            )
            continue
        if word not in haystack:
            errs.append(
                f"fr_accent_check: {word!r} is declared required but does not "
                f"appear in any *_fr field -- either the accent was stripped or "
                f"the text was reworded without updating the list"
            )
    return errs


def _resolve(target: str) -> str:
    return os.path.join(target, "meta.yml") if os.path.isdir(target) else target


def _iter_all(root: str):
    for dirpath, _dirs, files in os.walk(root):
        if "meta.yml" in files:
            yield os.path.join(dirpath, "meta.yml")


def main(argv: list[str]) -> int:
    args = argv[1:]
    if not args or args == ["--all"]:
        repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        root = os.path.join(repo, "challenges", "static")
        targets = sorted(_iter_all(root))
        # --all is a survey: only report challenges that HAVE FR fields.
        targets = [t for t in targets if _has_fr(t)]
        print(f"=== check_fr_accents: scanning {len(targets)} meta.yml with FR fields ===")
    else:
        targets = [_resolve(a) for a in args]

    failed = 0
    for meta_path in targets:
        errs = check_meta(meta_path)
        rel = os.path.relpath(meta_path)
        if errs:
            failed += 1
            print(f"FAIL  {rel}")
            for e in errs:
                print(f"        {e.split('  ', 1)[-1]}")
        else:
            print(f"PASS  {rel}")

    print(f"=== {len(targets) - failed}/{len(targets)} passed, {failed} failed ===")
    return 1 if failed else 0


def _has_fr(meta_path: str) -> bool:
    yaml = _yaml()
    try:
        with open(meta_path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except Exception:
        return False
    if not isinstance(data, dict):
        return False
    # `fr_docs` counts too: a challenge could ship a bilingual document with
    # no *_fr meta field at all, and skipping it would be a silent hole.
    return any(k.endswith("_fr") for k in data) or bool(data.get("fr_docs"))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
