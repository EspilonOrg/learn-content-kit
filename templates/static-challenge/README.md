# Authoring a static challenge

Français: [README.fr.md](README.fr.md)

This README is the guide for filling the template. It is not part of the
submitted artifact; the maintainers ignore it on ingestion.

## Contents

- [What it is](#what-it-is)
- [Where it lives](#where-it-lives)
- [The template](#the-template)
- [Field reference](#field-reference)
- [Local checks](#local-checks)
- [Topology](#topology)
- [Images](#images)
- [Traps](#traps)
- [Open gaps](#open-gaps)

## What it is

A self-contained puzzle: one or more downloadable files and a flag the player
recovers from those files alone. No server, no session, no network. If the answer
can be recomputed from the artifact on the player's own machine, it is a static
challenge.

## Where it lives

Author it from `templates/static-challenge/`. Copy the whole folder, replace the
example values, keep it passing the local checks, and submit through the Espilon
Learn member portal. On ingestion the maintainers create the challenge record,
attach the files you pinned, and wire any course lesson that names the challenge
by slug. They pin the artifact bytes by sha256, so `generate.py` must stay
deterministic. You never seed or deploy.

## The template

```text
static-challenge/
  meta.yml        the challenge record: flag, category, level, hints, bilingual brief
  generate.py     builds files/ deterministically; the artifact ENCODES the answer
  solve.py        the reference solver: recovers the flag from files/ alone
  files/          exactly what the player downloads (pinned by meta.yml `files:`)
```

`generate.py` and `solve.py` never ship to the player. Only the contents of
`files/` do, and only the entries listed in `meta.yml` under `files:`.

## Field reference

Required (the validator rejects the file without them): `slug`, `title`,
`category`, `level`, `flag`, `description`, `hints`. Expected for a bilingual,
wiki-linked challenge: `tags`, `files`, `technique`, `description_fr`,
`technique_fr`, `hints_fr`, `max_attempts`.

| Field | Rule |
|---|---|
| `slug` | Lowercase kebab-case, unique. |
| `category` | Lowercase kebab-case only. A stray capital or underscore splits the group in the UI. This is not the difficulty axis. |
| `level` | The CTF difficulty grid, a closed set: `very-easy`, `easy`, `medium`, `hard`, `insane`. |
| `flag` | Must match `ESPILON{...}` (literal `ESPILON`, one `{...}` block, at least one character, no nested braces). Concrete, never a placeholder. Derived from the artifact; `solve.py` proves it is recoverable from `files/` alone. |
| `tags` | Drive the related-wiki card. Quote anything numeric-looking (a bare `802154` parses as an integer). |
| `files` | Pin the exact player-facing downloads. Without it, every regular file under `files/` is attached, so a stray scratch file leaks. |
| `description` | Player-facing brief. State the task and the exact answer format. Use a folded `>` block to avoid the `': '` YAML trap. State; do not interpret. |
| `technique` | Private design note. State the intended solve path and why shortcuts fail, so a reviewer can judge difficulty. |
| `hints` | Non-empty list of non-empty strings, a rung ladder that teaches the method without giving the answer. The last rung must not print the flag or the exploit verbatim. |
| `description_fr`, `technique_fr`, `hints_fr` | The French twin. Natural technical French with real accents; keep tool and protocol names in English. A missing FR field falls back to EN. |

## Local checks

Run from the kit root, offline, with no platform and no database.

```bash
# 1. Build the artifact (deterministic; safe to rerun).
python3 -I templates/static-challenge/generate.py

# 2. Prove it is solvable from the artifact alone and the flag matches.
python3 -I templates/static-challenge/solve.py

# 3. Validate the meta record.
python3 -I validators/validate_static_meta.py templates/static-challenge

# 4. Scan the French fields for stripped accents.
python3 -I validators/check_fr_accents.py templates/static-challenge
```

Point them at your own challenge folder instead of `templates/static-challenge`.
All four must exit 0.

## Topology

```text
  TOKEN (constant in generate.py)
         |
         |  generate.py  (deterministic build)
         v
  files/sample.bin  ---- what the player downloads ----
         |                                             |
         |  solve.py (reference)        player's own analysis
         v                                             |
  ESPILON{TOKEN}  <===== must be byte-for-byte equal ==+
         ^
  meta.yml `flag:`  (solve.py asserts its output equals this)
```

The artifact encodes the answer, the build is deterministic, and `solve.py`
reproduces the `meta.yml` flag exactly. Break any one and the challenge is
unproven.

## Images

A static challenge has no hero image. The player-facing assets are the downloads
in `files/`, served exactly as pinned by `files:`. Do not drop a decorative image
into `files/`: it would be served as a download. Illustrations belong in the
related wiki entry or the course that teaches the challenge.

## Traps

- **The `': '` YAML trap.** A plain multi-line `description` or hint containing
  `': '` or a trailing `:` breaks the parse. Use a folded `>` block or quote the
  string. This is the most common real-world break.
- **A placeholder flag.** The flag must be the exact string the solver yields,
  not a pattern.
- **No runnable solver.** A `solve.py` that does not run stdlib-only (or with a
  pinned dependency) leaves the challenge unproven. Do not ship it.
- **`category` used as `level`.** `category` groups the challenge; `level` is the
  closed CTF grid. Mixing them splits the UI group or fails validation.
- **An un-pinned `files:`.** Every file under `files/` ships until you pin the
  list.
- **French asserted by reading.** Run the FR-accent check; do not eyeball it.
- **A drifting artifact.** If `generate.py` is not deterministic, every sha256
  pin a course makes against the artifact goes stale silently.

## Open gaps

The validators check format and solvability. Whether the challenge is interesting
and fairly rated is a human call at review. Artifact pinning by sha256 and lesson
wiring happen on the maintainer side at ingestion.
