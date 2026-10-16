#!/usr/bin/env python3
"""validate_static_meta.py - authoring QA gate for static-challenge meta.yml.

This is the guard that stops a malformed meta.yml from ever reaching main.
It is intentionally strict and fails LOUDLY with a file+line pointer, because
the whole point is that an author (or CI) catches the problem *before* push.

What it checks, per meta.yml
----------------------------
  1. It is valid YAML. `yaml.safe_load` must not raise. The #1 real-world bug
     is an unquoted plain multi-line scalar that contains a ': ' (colon+space)
     or a trailing ':', which pyyaml reads as a mapping and rejects with a
     ScannerError. We surface that as `file:line:col  <reason>`.
  2. The document is a mapping (dict), not a list/scalar.
  3. Required keys are present and non-empty:
       slug, title, category, level, flag, description, hints
  4. `hints` is a non-empty list of non-empty strings.
  5. `flag` matches the ESPILON{...} shape.
  6. `level` is one of the five CTF-grid values. The grid is a closed
     vocabulary, not a free-text label: the catalogue sorts and filters on it,
     and an off-grid value like 'medium-hard' silently lands in no bucket.
     Note this is a DIFFERENT vocabulary from Course.difficulty, which is
     beginner/intermediate/advanced -- do not mix the two.
  7. `max_attempts`, when present, is an integer >= 1. Optional: omitting it
     is how a challenge gets unlimited submissions, which is what all of them
     had before the key existed. It is checked here because the failure is
     otherwise invisible until prod -- CTFd reads 0 as UNLIMITED, so the one
     value an author is most likely to type for "no attempts" silently grants
     the opposite of a cap, on exactly the challenges that asked for one.
     A negative or a float is rejected for the same reason: MySQL would
     coerce or reject it far from the file that caused it.
  8. `category` is lowercase kebab-case. It is written to the CTFd challenge
     row and groups challenges in the UI, so 'ESP32' sitting next to twenty
     lowercase categories silently splits a group. Deliberately a FORMAT rule
     and not a closed list, because new categories are expected. --all also
     prints a category census, since no mechanical rule separates a genuine
     new category from a variant spelling of an existing one ('ot-ics' vs
     'ics'); a count of one is the usual tell.

Rescued challenges, and why the exemption is a baseline and not a flag
---------------------------------------------------------------------
`hints` is required of a challenge somebody is AUTHORING. It cannot be
required of a challenge that is being RECORDED as it already exists: 31 of the
challenges rescued out of the production database in
quartermaster/rescue-db-only-challenges genuinely have no hint ladder in
production, and inventing rungs to satisfy this gate would have put made-up
teaching in front of players and destroyed the proof that the export was
faithful.

So the gate learns that distinction, from tools/static_meta_rescue_baseline.json:
a path listed there is not required to carry `hints`, and NOTHING ELSE about it
is relaxed. Every other required key, the flag shape, the level grid, the
category format and the whole artifact-surface check still apply in full.

It is a baseline file and not a `rescued: true` key in the meta on purpose. A
marker inside the file is a licence the author of the excused file issues to
themselves, with nothing outside the file corroborating it, and it travels by
copy-paste: duplicate a rescued meta.yml as the starting point for new work and
the new challenge is silently exempt too. A baseline entry cannot travel that
way, because a copy lands at a path nobody listed. Adding an entry is a
separate, named line in a reviewed diff, it has to carry a written reason, and
it has to name the production challenge id, which a reviewer can check in one
command (tools/prod_drift.py --challenge <title>).

Be clear about the limit: this is an offline authoring gate with no database,
so it cannot verify that a listed challenge really lacks a ladder in
production. An author determined to skip hints can still add themselves to the
baseline. What the design buys is that doing so is deliberate, visible and
argued in writing, instead of one word typed into the file being excused.

The entries expire by themselves. If a rescued challenge later gains a `hints`
list, or its meta.yml moves or is deleted, the entry is reported STALE and the
run FAILS, so the file cannot rot into a permanent excuse. Listed challenges
are printed on every run as RESCUED, so they never quietly disappear either.

What it checks, per challenge artifact surface (files/)
-------------------------------------------------------
  1. No file under files/ is swallowed by a .gitignore rule. This is the second
     real-world bug: the repo-wide `*.log` / `*.pem` rules silently kept nine
     shipped artifacts untracked, so they existed only in one working tree and
     in prod, and a fresh clone could not seed the challenge. Skipped (not
     failed) when git is unavailable or the tree is not a checkout.
  2. No dotfile under files/. seed_static._find_artifacts falls back to every
     regular file under files/ when meta.yml has no `files:` key, and that
     fallback uses os.listdir, so a stray .gitignore or .DS_Store gets attached
     as a player download. This FAILS only when the key is absent, since that
     is the case where the dotfile actually reaches a player; with the key
     pinned it is a warning, because it still leaks if the list is ever
     dropped.
  3. Advisory only (never fails the run): a challenge with several files under
     files/ but no explicit `files:` list is relying on that fallback, so any
     scratch file dropped in the directory becomes a download.

Usage
-----
  # Validate one challenge (dir or its meta.yml):
  python3 tools/validate_static_meta.py challenges/static/firmware-reverse/mips-firmware-reverse

  # Regression scan: validate every meta.yml under challenges/static/:
  python3 tools/validate_static_meta.py --all
  python3 tools/validate_static_meta.py            # (no args == --all)

Exit code is 0 only if every validated meta.yml is clean; non-zero otherwise.

Dependencies: stdlib + pyyaml (same as seed_static.py).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys

# ESPILON{...} : literal ESPILON, a single {...} block with at least one char
# and no nested braces. Anchored, so no leading/trailing junk is tolerated.
_FLAG_RE = re.compile(r"^ESPILON\{[^{}]+\}$")

_REQUIRED_KEYS = ("slug", "title", "category", "level", "flag", "description", "hints")

# The ONLY key a rescue baseline entry can excuse. Kept as a one-element tuple
# rather than inlined so that widening it is a visible edit here, next to the
# reasoning above, and not a quiet condition buried in the checker.
_RESCUABLE_KEYS = ("hints",)

_RESCUE_BASELINE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "static_meta_rescue_baseline.json")

# The CTF difficulty grid, easiest first. Closed vocabulary: anything else is
# an error, including plausible-looking hyphenations ('medium-hard') and the
# course vocabulary ('beginner'/'intermediate'/'advanced'), which belongs to
# Course.difficulty and not here.
_LEVELS = ("very-easy", "easy", "medium", "hard", "insane")

# `category` is written straight to the CTFd challenge row and is what groups
# challenges in the UI, so two spellings of the same thing silently split a
# group. Unlike `level` this is deliberately NOT a closed list -- new
# categories are expected -- so the rule is a FORMAT rule: lowercase
# kebab-case. That catches the real failure ('ESP32' next to every other
# category in lowercase) without blocking growth. Near-duplicates that are
# both well-formed ('ics' vs 'ot-ics') cannot be caught mechanically, so
# --all prints a census instead and leaves the judgement to a human.
_CATEGORY_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def _yaml():
    try:
        import yaml
    except ImportError:  # pragma: no cover - environment guard
        sys.exit("ERROR: pyyaml is not installed -- pip install pyyaml")
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
    """Turn a pyyaml exception into a terse file:line:col message."""
    mark = getattr(exc, "problem_mark", None) or getattr(exc, "context_mark", None)
    reason = getattr(exc, "problem", None) or str(exc).splitlines()[0]
    if mark is not None:
        # pyyaml marks are 0-based.
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


def _repo_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_rescue_baseline() -> dict:
    """{challenge dir relative to the repo root: entry}. Missing file is an
    empty baseline, i.e. nothing is excused, which is the safe direction."""
    if not os.path.exists(_RESCUE_BASELINE):
        return {}
    with open(_RESCUE_BASELINE, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    entries = raw.get("hints_absent_in_production") or {}
    return {k.strip("/"): v for k, v in entries.items()}


def _rel_challenge_dir(meta_path: str) -> str | None:
    """The challenge directory, relative to the repo root, in posix form.

    None when the meta.yml is outside this checkout: a temp fixture or a file
    passed by absolute path from elsewhere can then never match a baseline
    entry, so the exemption fails closed for anything the repo does not own.
    """
    challenge_dir = os.path.dirname(os.path.abspath(meta_path))
    rel = os.path.relpath(challenge_dir, _repo_root())
    if rel.startswith("..") or os.path.isabs(rel):
        return None
    return rel.replace(os.sep, "/")


def _rescue_status(meta_path: str, data, baseline: dict) -> tuple[bool, list[str]]:
    """(hints_excused, errors).

    An entry only excuses anything if it is complete AND still true:
      * it carries a non-empty reason, so the diff that added it said why;
      * it names a prod_challenge_id and the meta.yml carries the same one, so
        the entry is bound to one recorded production row rather than to a
        path that anything could be moved into;
      * the meta.yml still has no `hints`. The moment it gains one the entry
        is obsolete and saying so is a FAILURE, not a note, because a baseline
        that cannot expire is just a permanent hole with a comment on it.
    """
    rel = _rel_challenge_dir(meta_path)
    if rel is None or rel not in baseline:
        return False, []

    entry = baseline[rel] if isinstance(baseline[rel], dict) else {}
    errs: list[str] = []

    reason = (entry.get("reason") or "").strip() if isinstance(entry, dict) else ""
    if not reason:
        errs.append(
            f"{meta_path}  rescue baseline entry for {rel!r} has no 'reason'; "
            f"an entry that does not say why it exists cannot be reviewed"
        )

    want_id = entry.get("prod_challenge_id") if isinstance(entry, dict) else None
    got_id = data.get("prod_challenge_id") if isinstance(data, dict) else None
    if want_id is None:
        errs.append(
            f"{meta_path}  rescue baseline entry for {rel!r} names no "
            f"'prod_challenge_id'; the entry must be bound to the production "
            f"row it records"
        )
    elif got_id is None:
        errs.append(
            f"{meta_path}  is in the rescue baseline but carries no "
            f"'prod_challenge_id'; only a challenge recorded FROM production "
            f"can be excused, and this file does not say which one it is"
        )
    elif got_id != want_id:
        errs.append(
            f"{meta_path}  rescue baseline names prod_challenge_id {want_id!r} "
            f"but meta.yml says {got_id!r}; the entry does not describe this file"
        )

    if isinstance(data, dict) and data.get("hints"):
        errs.append(
            f"{meta_path}  STALE rescue baseline entry: this challenge now has "
            f"a 'hints' ladder, so it is no longer excused. Delete the entry "
            f"for {rel!r} from tools/static_meta_rescue_baseline.json"
        )

    return (not errs), errs


def validate_artifact_surface(challenge_dir: str) -> tuple[list[str], list[str]]:
    """Check the player-facing files/ directory. Return (errors, warnings)."""
    errs: list[str] = []
    warns: list[str] = []
    files_dir = os.path.join(challenge_dir, "files")
    if not os.path.isdir(files_dir):
        # Not this checker's business: seed_static is where a missing files/
        # directory is fatal, and some challenge dirs are staged before build.
        return errs, warns

    entries = sorted(
        e for e in os.listdir(files_dir)
        if os.path.isfile(os.path.join(files_dir, e))
    )
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    shown = os.path.relpath(files_dir, repo_root)

    # An explicit `files:` list is what decides whether a stray dotfile can
    # actually reach a player: _find_artifacts prefers that list and only falls
    # back to scanning the directory when the key is absent. So a dotfile is a
    # real leak without the key and merely untidy with it. A meta.yml that will
    # not parse counts as "no key", which is the safe direction.
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
                f"{shown}  dotfile '{name}' sits in the player-facing "
                f"artifact directory; seed_static would attach it as a download"
            )

    # Only ask git about files that would actually be attached: the pinned list
    # if there is one, otherwise every non-dotfile entry. Asking about a
    # dotfile produces the exactly-backwards advice "add a negation so your
    # .DS_Store survives a fresh clone", when the right answer is to delete it
    # -- which the dotfile check above already says.
    if pinned:
        shipped = [n for n in declared if isinstance(n, str)]
    else:
        shipped = [n for n in entries if not n.startswith(".")]
    rel_paths = [
        os.path.relpath(os.path.join(files_dir, n), repo_root)
        for n in shipped
        if os.path.isfile(os.path.join(files_dir, n))
    ]
    ignored = _git_ignored(rel_paths, repo_root)
    if ignored:
        for path in sorted(ignored):
            errs.append(
                f"{path}  is a shipped artifact but git IGNORES it, so it would "
                f"be missing from a fresh clone; add a scoped negation in "
                f".gitignore (see the challenges/static block)"
            )

    if len(entries) > 1:
        if not pinned:
            warns.append(
                f"{shown}  has {len(entries)} files but meta.yml declares no "
                f"'files:' list, so seed_static attaches all of them "
                f"({', '.join(entries)}); declare the list to pin the downloads"
            )
    return errs, warns


def validate_meta_file(meta_path: str, baseline: dict | None = None) -> list[str]:
    """Validate a single meta.yml. Return a list of human-readable errors.

    `baseline` is the rescue baseline (see load_rescue_baseline); it is loaded
    here when not supplied so a single-file run behaves exactly like --all.
    """
    if not os.path.isfile(meta_path):
        return [f"{meta_path}  not found"]

    data, errors = load_meta(meta_path)
    if errors:
        return errors  # YAML did not even parse; nothing more to say.

    if not isinstance(data, dict):
        return [f"{meta_path}  top-level document is not a mapping (got {type(data).__name__})"]

    errs: list[str] = []

    if baseline is None:
        baseline = load_rescue_baseline()
    excused, rescue_errs = _rescue_status(meta_path, data, baseline)
    errs.extend(rescue_errs)
    # Only `hints`, only when the entry is complete and still true, and only
    # for the presence check. A `hints` list that IS there is checked in full
    # below whatever the baseline says.
    exempt = set(_RESCUABLE_KEYS) if excused else set()

    # Required keys present and non-empty.
    for key in _REQUIRED_KEYS:
        if key in exempt and key not in data:
            continue
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
    #
    # These become CTFd Tags rows, and espilon_learn/routes.py intersects them
    # with the wiki to build the challenge page's related-wiki card, falling
    # back to the CATEGORY when there are none. An untagged challenge therefore
    # renders every wiki page of its protocol family, and that has included the
    # companion page documenting the exact technique the paid hint ladder
    # sells. Which tags are SAFE is a content judgement and lives in
    # tools/check_challenge_wiki_tags.py; this is only the shape check, plus
    # the one trap YAML lays here: an unquoted numeric-looking tag such as
    # 802154 parses as an int, not a string.
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
    #
    # seed_static.py writes this straight to CTFd's Challenges.max_attempts,
    # where 0 means UNLIMITED. That inversion is the whole reason this is
    # checked offline: an author who wants a cap and types 0 gets the opposite
    # of one, on precisely the challenge that needed it, and nothing anywhere
    # says so. Unlimited is expressed by leaving the key out, and nothing else
    # expresses it. bool is checked before int because it is an int subclass,
    # so a stray `max_attempts: true` would otherwise pass as the cap 1.
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
                f"{meta_path}  'max_attempts' is 0; CTFd reads 0 as UNLIMITED, "
                f"so this grants the opposite of the cap it looks like -- omit "
                f"the key entirely for unlimited submissions"
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


def _static_root() -> str:
    # tools/ -> repo root -> challenges/static
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(repo_root, "challenges", "static")


def main(argv: list[str]) -> int:
    args = argv[1:]
    targets: list[str]

    if not args or args == ["--all"]:
        root = _static_root()
        if not os.path.isdir(root):
            print(f"ERROR: {root} not found", file=sys.stderr)
            return 2
        targets = sorted(_iter_all_metas(root))
        print(f"=== validate_static_meta: scanning {len(targets)} meta.yml under {root} ===")
    else:
        targets = [_resolve_meta_path(a) for a in args]

    scanning_all = not args or args == ["--all"]
    baseline = load_rescue_baseline()
    total_fail = 0
    rescued = 0
    categories: dict[str, int] = {}
    all_warns: list[str] = []
    for meta_path in targets:
        errs = validate_meta_file(meta_path, baseline)
        # The artifact surface is checked even when the YAML itself is broken:
        # a swallowed download is a separate failure mode from a bad meta.yml.
        surface_errs, surface_warns = validate_artifact_surface(
            os.path.dirname(os.path.abspath(meta_path))
        )
        errs = errs + surface_errs
        all_warns.extend(surface_warns)
        rel = os.path.relpath(meta_path)
        if scanning_all:
            data, load_errs = load_meta(meta_path)
            if not load_errs and isinstance(data, dict):
                cat = data.get("category")
                if isinstance(cat, str) and cat.strip():
                    categories[cat.strip()] = categories.get(cat.strip(), 0) + 1
        rescue_key = _rel_challenge_dir(meta_path)
        if errs:
            total_fail += 1
            print(f"FAIL  {rel}")
            for e in errs:
                print(f"        {e}")
        elif rescue_key in baseline:
            # Printed every run, never silently absent, so an excused challenge
            # stays visible for as long as it is excused.
            rescued += 1
            entry = baseline[rescue_key]
            print(f"RESCUED  {rel}")
            print(f"        no 'hints' required: "
                  f"{(entry.get('reason') or '').strip()}")
        else:
            print(f"PASS  {rel}")

    for w in all_warns:
        print(f"WARN  {w}")

    # Stale sweep. Per-file staleness (the challenge gained a ladder) is caught
    # in _rescue_status; this catches the other shape, an entry pointing at a
    # meta.yml that no longer exists because it was deleted or moved. Only on a
    # full scan, since a single-target run has no business judging entries it
    # was not asked to look at.
    stale = 0
    if scanning_all:
        for rel_dir in sorted(baseline):
            if not os.path.isfile(os.path.join(_repo_root(), rel_dir, "meta.yml")):
                stale += 1
                print(f"STALE rescue baseline entry: {rel_dir}/meta.yml does not "
                      f"exist; delete the entry from "
                      f"{os.path.relpath(_RESCUE_BASELINE, _repo_root())}")

    if scanning_all and categories:
        # No mechanical check can tell 'ics' from 'ot-ics', so show the whole
        # list and let a human spot the split. Singletons are listed first
        # because a category of one is the usual shape of an accidental
        # variant spelling.
        print(f"--- category census ({len(categories)} distinct) ---")
        for cat, n in sorted(categories.items(), key=lambda kv: (kv[1], kv[0])):
            mark = "  <- only one, check it is not a variant" if n == 1 else ""
            print(f"      {n:3d}  {cat}{mark}")

    print(
        f"=== {len(targets) - total_fail}/{len(targets)} passed, "
        f"{total_fail} failed ==="
    )
    if rescued:
        print(f"    of which {rescued} rescued from production and excused the "
              f"'hints' key only, per "
              f"{os.path.relpath(_RESCUE_BASELINE, _repo_root())}")
    if stale:
        print(f"    {stale} STALE rescue baseline entry(ies): the baseline "
              f"describes challenges that are not there any more")
    return 1 if (total_fail or stale) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
