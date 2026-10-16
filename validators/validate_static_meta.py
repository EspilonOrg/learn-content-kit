#!/usr/bin/env python3
"""validate_static_meta.py - offline QA gate for a static-challenge meta.yml.

Run it before you submit a static challenge. It is intentionally strict and
fails LOUDLY with a file+line pointer, so you catch a problem on your own
machine rather than at review. It needs only the Python standard library and
PyYAML, no platform and no database.

What it checks, per meta.yml
----------------------------
  1. It is valid YAML. `yaml.safe_load` must not raise. The number one
     real-world bug is an unquoted plain multi-line scalar that contains a ': '
     (colon+space) or a trailing ':', which YAML reads as a mapping and rejects.
     It is surfaced as `file:line:col  <reason>`.
  2. The document is a mapping (dict), not a list or scalar.
  3. Required keys are present and non-empty:
       slug, title, category, level, flag, description, hints
  4. `hints` is a non-empty list of non-empty strings.
  5. `flag` matches the ESPILON{...} shape.
  6. `level` is one of the five CTF-grid values. The grid is a closed
     vocabulary, not a free-text label: the catalogue sorts and filters on it,
     and an off-grid value like 'medium-hard' silently lands in no bucket.
     Note this is a DIFFERENT vocabulary from a course's difficulty, which is
     beginner/intermediate/advanced. Do not mix the two.
  7. `max_attempts`, when present, is an integer >= 1. Omitting it is how a
     challenge gets unlimited submissions. It is checked here because the
     failure is otherwise invisible until it is live: the platform reads 0 as
     UNLIMITED, so the one value an author is most likely to type for "no
     attempts" silently grants the opposite of a cap. A negative or a float is
     rejected for the same reason.
  8. `category` is lowercase kebab-case. It groups challenges in the UI, so
     'ESP32' sitting next to twenty lowercase categories silently splits a
     group. Deliberately a FORMAT rule and not a closed list, because new
     categories are expected. A recursive scan also prints a category census,
     since no mechanical rule separates a genuine new category from a variant
     spelling of an existing one ('ot-ics' vs 'ics'); a count of one is the
     usual tell.

What it checks, per challenge artifact surface (files/)
-------------------------------------------------------
  1. No file under files/ is swallowed by a .gitignore rule, which would leave
     a shipped artifact missing from a fresh clone. Skipped (not failed) when
     git is unavailable or the tree is not a checkout.
  2. No dotfile under files/. When meta.yml has no `files:` key the ingestion
     attaches every regular file under files/, so a stray dotfile would be
     served as a player download. This FAILS only when the key is absent (the
     case where the dotfile actually reaches a player); with the key pinned it
     is a warning, because it still leaks if the list is ever dropped.
  3. Advisory only (never fails the run): several files under files/ with no
     explicit `files:` list relies on that fallback, so any scratch file
     dropped in the directory becomes a download.

Usage
-----
  # Validate the shipped template:
  python3 -I validators/validate_static_meta.py templates/static-challenge

  # Validate your own challenge (a directory or a direct path to its meta.yml):
  python3 -I validators/validate_static_meta.py path/to/your-challenge

  # Validate several, or recurse under a directory:
  python3 -I validators/validate_static_meta.py chall-a chall-b
  python3 -I validators/validate_static_meta.py --all path/to/a/folder

Exit code is 0 only if every validated meta.yml is clean; non-zero otherwise.

Dependencies: Python 3 standard library + PyYAML.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys

# ESPILON{...} : literal ESPILON, a single {...} block with at least one char
# and no nested braces. Anchored, so no leading/trailing junk is tolerated.
_FLAG_RE = re.compile(r"^ESPILON\{[^{}]+\}$")

_REQUIRED_KEYS = ("slug", "title", "category", "level", "flag", "description", "hints")

# The CTF difficulty grid, easiest first. Closed vocabulary: anything else is
# an error, including plausible-looking hyphenations ('medium-hard') and the
# course vocabulary ('beginner'/'intermediate'/'advanced'), which belongs to a
# course and not here.
_LEVELS = ("very-easy", "easy", "medium", "hard", "insane")

# `category` groups challenges in the UI, so two spellings of the same thing
# silently split a group. Unlike `level` this is deliberately NOT a closed list
# (new categories are expected), so the rule is a FORMAT rule: lowercase
# kebab-case. Near-duplicates that are both well-formed ('ics' vs 'ot-ics')
# cannot be caught mechanically, so a recursive scan prints a census instead and
# leaves the judgement to a human.
_CATEGORY_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def _yaml():
    try:
        import yaml
    except ImportError:  # pragma: no cover - environment guard
        sys.exit("ERROR: PyYAML is not installed -- pip install pyyaml")
    return yaml


def load_meta(meta_path: str):
    """Return (data, errors).

    On a YAML syntax error, data is None and errors holds a single
    'file:line:col  reason' string. On success errors is empty.
    """
    yaml = _yaml()
    try:
        with open(meta_path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except yaml.YAMLError as exc:
        return None, [_format_yaml_error(meta_path, exc)]
    return data, []


def _format_yaml_error(meta_path: str, exc) -> str:
    """Turn a PyYAML exception into a terse file:line:col message."""
    mark = getattr(exc, "problem_mark", None) or getattr(exc, "context_mark", None)
    reason = getattr(exc, "problem", None) or str(exc).splitlines()[0]
    if mark is not None:
        # PyYAML marks are 0-based.
        loc = f"{meta_path}:{mark.line + 1}:{mark.column + 1}"
        hint = ""
        if reason and "mapping values are not allowed" in reason:
            hint = (
                "  (an unquoted multi-line hint/description contains ': ' or a "
                "trailing ':' -- use a '>' block scalar or quote the string)"
            )
        elif reason and "could not find expected ':'" in reason:
            hint = (
                "  (a plain scalar broke into what looks like a mapping -- "
                "use a '>' block scalar or quote the string)"
            )
        return f"{loc}  YAML syntax error: {reason}{hint}"
    return f"{meta_path}  YAML syntax error: {reason}"


def _git_ignored(paths: list[str], cwd: str) -> list[str] | None:
    """Return the subset of `paths` that git would ignore, or None if the
    question cannot be answered here (no git binary, not a checkout).

    `git check-ignore --stdin` exits 0 when at least one path is ignored, 1 when
    none is, and 128 on a real error, so 1 is a success case for us.
    """
    if not paths:
        return []
    try:
        proc = subprocess.run(
            ["git", "check-ignore", "--stdin"],
            input="\n".join(paths) + "\n",
            cwd=cwd,
            capture_output=True,
            text=True,
        )
    except (OSError, ValueError):  # git missing, or exec failed
        return None
    if proc.returncode not in (0, 1):
        return None  # not a git checkout, or git complained: stay silent
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def validate_artifact_surface(challenge_dir: str) -> tuple[list[str], list[str]]:
    """Check the player-facing files/ directory. Return (errors, warnings)."""
    errs: list[str] = []
    warns: list[str] = []
    files_dir = os.path.join(challenge_dir, "files")
    if not os.path.isdir(files_dir):
        # Not this checker's business: some challenge dirs are staged before the
        # artifact is built, and a missing files/ directory is caught elsewhere.
        return errs, warns

    entries = sorted(
        e for e in os.listdir(files_dir)
        if os.path.isfile(os.path.join(files_dir, e))
    )
    cwd = os.path.abspath(challenge_dir)
    shown = os.path.relpath(files_dir, cwd)

    # An explicit `files:` list decides whether a stray dotfile can actually
    # reach a player: the ingestion prefers that list and only falls back to
    # scanning the directory when the key is absent. So a dotfile is a real leak
    # without the key and merely untidy with it. A meta.yml that will not parse
    # counts as "no key", which is the safe direction.
    meta_data, meta_load_errs = load_meta(os.path.join(challenge_dir, "meta.yml"))
    declared = meta_data.get("files") if isinstance(meta_data, dict) else None
    pinned = bool(declared) and not meta_load_errs

    for name in entries:
        if not name.startswith("."):
            continue
        if pinned:
            warns.append(
                f"{shown}  dotfile '{name}' sits in the player-facing artifact "
                f"directory; meta.yml pins 'files:' so it is not attached, but "
                f"it will leak the moment that list is dropped -- remove it"
            )
        else:
            errs.append(
                f"{shown}  dotfile '{name}' sits in the player-facing artifact "
                f"directory; with no 'files:' list it would be attached as a "
                f"player download"
            )

    # Only ask git about files that would actually be attached: the pinned list
    # if there is one, otherwise every non-dotfile entry.
    if pinned:
        shipped = [n for n in declared if isinstance(n, str)]
    else:
        shipped = [n for n in entries if not n.startswith(".")]
    rel_paths = [
        os.path.relpath(os.path.join(files_dir, n), cwd)
        for n in shipped
        if os.path.isfile(os.path.join(files_dir, n))
    ]
    ignored = _git_ignored(rel_paths, cwd)
    if ignored:
        for path in sorted(ignored):
            errs.append(
                f"{path}  is a shipped artifact but git IGNORES it, so it would "
                f"be missing from a fresh clone; add a scoped negation in "
                f".gitignore so the file is tracked"
            )

    if len(entries) > 1 and not pinned:
        warns.append(
            f"{shown}  has {len(entries)} files but meta.yml declares no "
            f"'files:' list, so all of them would be attached as downloads "
            f"({', '.join(entries)}); declare the list to pin the downloads"
        )
    return errs, warns


def validate_meta_file(meta_path: str) -> list[str]:
    """Validate a single meta.yml. Return a list of human-readable errors."""
    if not os.path.isfile(meta_path):
        return [f"{meta_path}  not found"]

    data, errors = load_meta(meta_path)
    if errors:
        return errors  # YAML did not even parse; nothing more to say.

    if not isinstance(data, dict):
        return [f"{meta_path}  top-level document is not a mapping (got {type(data).__name__})"]

    errs: list[str] = []

    # Required keys present and non-empty.
    for key in _REQUIRED_KEYS:
        if key not in data:
            errs.append(f"{meta_path}  missing required key: '{key}'")
            continue
        val = data[key]
        if val is None:
            errs.append(f"{meta_path}  required key '{key}' is empty/null")
        elif isinstance(val, str) and not val.strip():
            errs.append(f"{meta_path}  required key '{key}' is an empty string")
        elif isinstance(val, (list, dict)) and len(val) == 0:
            errs.append(f"{meta_path}  required key '{key}' is empty")

    # hints: non-empty list of non-empty strings.
    hints = data.get("hints")
    if hints is not None:
        if not isinstance(hints, list):
            errs.append(
                f"{meta_path}  'hints' must be a list, got {type(hints).__name__}"
            )
        elif len(hints) == 0:
            errs.append(f"{meta_path}  'hints' is an empty list (need at least one)")
        else:
            for i, hint in enumerate(hints):
                if not isinstance(hint, str):
                    errs.append(
                        f"{meta_path}  hints[{i}] must be a string, "
                        f"got {type(hint).__name__}"
                    )
                elif not hint.strip():
                    errs.append(f"{meta_path}  hints[{i}] is empty/blank")

    # tags: optional, but if present it must be a list of non-empty strings.
    # Tags drive the related-wiki card on the challenge page, matched against the
    # wiki by exact lowercased value. The one trap YAML lays here is an unquoted
    # numeric-looking tag such as 802154, which parses as an int, not a string.
    tags = data.get("tags")
    if tags is not None:
        if not isinstance(tags, list):
            errs.append(
                f"{meta_path}  'tags' must be a list, got {type(tags).__name__}"
            )
        elif len(tags) == 0:
            errs.append(
                f"{meta_path}  'tags' is an empty list; omit the key entirely or "
                f"give it tags (an empty list reads as deliberate and is not)"
            )
        else:
            for i, tag in enumerate(tags):
                if isinstance(tag, str):
                    if not tag.strip():
                        errs.append(f"{meta_path}  tags[{i}] is empty/blank")
                    elif tag != tag.strip():
                        errs.append(
                            f"{meta_path}  tags[{i}] {tag!r} has leading or "
                            f"trailing whitespace; it is matched against the "
                            f"wiki by exact lowercased value"
                        )
                else:
                    errs.append(
                        f"{meta_path}  tags[{i}] must be a string, got "
                        f"{type(tag).__name__} ({tag!r}); quote it -- a bare "
                        f"802154 is an int to YAML"
                    )

    # level: on the CTF grid.
    level = data.get("level")
    if isinstance(level, str) and level.strip() not in _LEVELS:
        errs.append(
            f"{meta_path}  level {level.strip()!r} is not on the CTF grid "
            f"({'/'.join(_LEVELS)})"
        )

    # category: lowercase kebab-case, so one group never splits in two.
    category = data.get("category")
    if isinstance(category, str) and not _CATEGORY_RE.match(category.strip()):
        errs.append(
            f"{meta_path}  category {category.strip()!r} is not lowercase "
            f"kebab-case; it groups challenges in the UI, so a stray capital "
            f"or underscore silently splits the group"
        )

    # flag: ESPILON{...} shape.
    flag = data.get("flag")
    if isinstance(flag, str) and not _FLAG_RE.match(flag.strip()):
        errs.append(
            f"{meta_path}  flag does not match ESPILON{{...}} shape: {flag!r}"
        )

    # max_attempts: optional submission cap, integer >= 1 when present.
    # The platform reads 0 as UNLIMITED, so an author who wants a cap and types 0
    # gets the opposite of one. Unlimited is expressed by leaving the key out,
    # and nothing else expresses it. bool is checked before int because it is an
    # int subclass, so a stray `max_attempts: true` would otherwise pass as 1.
    if "max_attempts" in data:
        cap = data["max_attempts"]
        if cap is None:
            errs.append(
                f"{meta_path}  'max_attempts' is empty/null; omit the key "
                f"entirely for unlimited submissions"
            )
        elif isinstance(cap, bool) or not isinstance(cap, int):
            errs.append(
                f"{meta_path}  'max_attempts' must be an integer, got "
                f"{cap!r} ({type(cap).__name__}); omit the key for unlimited"
            )
        elif cap == 0:
            errs.append(
                f"{meta_path}  'max_attempts' is 0; the platform reads 0 as "
                f"UNLIMITED, so this grants the opposite of the cap it looks "
                f"like -- omit the key entirely for unlimited submissions"
            )
        elif cap < 0:
            errs.append(
                f"{meta_path}  'max_attempts' must be >= 1, got {cap}; a "
                f"negative cap is meaningless -- omit the key for unlimited"
            )

    return errs


def _resolve_meta_path(target: str) -> str:
    """Accept either a challenge dir or a direct path to a meta.yml."""
    if os.path.isdir(target):
        return os.path.join(target, "meta.yml")
    return target


def _iter_all_metas(root: str):
    for dirpath, _dirnames, filenames in os.walk(root):
        if "meta.yml" in filenames:
            yield os.path.join(dirpath, "meta.yml")


_USAGE = (
    "usage: validate_static_meta.py <challenge-folder> [more folders...]\n"
    "       validate_static_meta.py --all <folder-to-recurse>\n"
    "\n"
    "Pass a challenge folder (the directory holding meta.yml) or a path to a\n"
    "meta.yml. For example:\n"
    "       python3 -I validators/validate_static_meta.py templates/static-challenge"
)


def main(argv: list[str]) -> int:
    args = argv[1:]
    if not args:
        print(_USAGE, file=sys.stderr)
        return 2

    recurse = False
    if args and args[0] == "--all":
        recurse = True
        roots = args[1:] or ["."]
        targets = sorted(m for root in roots for m in _iter_all_metas(root))
        if not targets:
            print(
                f"no meta.yml found under: {', '.join(roots)}\n{_USAGE}",
                file=sys.stderr,
            )
            return 2
        print(f"=== validate_static_meta: scanning {len(targets)} meta.yml ===")
    else:
        targets = [_resolve_meta_path(a) for a in args]

    total_fail = 0
    categories: dict[str, int] = {}
    all_warns: list[str] = []
    for meta_path in targets:
        errs = validate_meta_file(meta_path)
        # The artifact surface is checked even when the YAML itself is broken:
        # a swallowed download is a separate failure mode from a bad meta.yml.
        surface_errs, surface_warns = validate_artifact_surface(
            os.path.dirname(os.path.abspath(meta_path))
        )
        errs = errs + surface_errs
        all_warns.extend(surface_warns)
        rel = os.path.relpath(meta_path)
        if recurse:
            data, load_errs = load_meta(meta_path)
            if not load_errs and isinstance(data, dict):
                cat = data.get("category")
                if isinstance(cat, str) and cat.strip():
                    categories[cat.strip()] = categories.get(cat.strip(), 0) + 1
        if errs:
            total_fail += 1
            print(f"FAIL  {rel}")
            for e in errs:
                print(f"        {e}")
        else:
            print(f"PASS  {rel}")

    for w in all_warns:
        print(f"WARN  {w}")

    if recurse and categories:
        # No mechanical check can tell 'ics' from 'ot-ics', so show the whole
        # list and let a human spot the split. Singletons are listed first
        # because a category of one is the usual shape of a variant spelling.
        print(f"--- category census ({len(categories)} distinct) ---")
        for cat, n in sorted(categories.items(), key=lambda kv: (kv[1], kv[0])):
            mark = "  <- only one, check it is not a variant" if n == 1 else ""
            print(f"      {n:3d}  {cat}{mark}")

    print(
        f"=== {len(targets) - total_fail}/{len(targets)} passed, "
        f"{total_fail} failed ==="
    )
    return 1 if total_fail else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
