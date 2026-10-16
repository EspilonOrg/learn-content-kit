# Authoring a static challenge

Français: [static-challenge.fr.md](static-challenge.fr.md)

A static challenge is a self-contained puzzle: one or more downloadable files and
a flag the player recovers from those files alone. No server, no session, no
network. If the answer can be recomputed from the artifact on the player's own
machine, it is a static challenge.

Template: `templates/static-challenge/`. Copy the whole folder, keep it passing
the local checks, and replace the example values with yours.

## The files

```
static-challenge/
  meta.yml        the challenge record: flag, category, level, hints, bilingual brief
  generate.py     builds files/ deterministically; the artifact ENCODES the answer
  solve.py        the reference solver: recovers the flag from files/ alone
  files/          exactly what the player downloads (pinned by meta.yml `files:`)
```

`generate.py` and `solve.py` never ship to the player. Only the contents of
`files/` do, and only the entries named in `meta.yml` under `files:`.

## Fill in meta.yml, field by field

Required (the meta validator rejects the file without them): `slug`, `title`,
`category`, `level`, `flag`, `description`, `hints`. Expected for a bilingual,
wiki-linked challenge: `tags`, `files`, `technique`, `description_fr`,
`technique_fr`, `hints_fr`, `max_attempts`.

- `slug`: lowercase kebab-case identifier, unique.
- `category`: lowercase kebab-case only. A stray capital or underscore silently
  splits the group in the UI. This is NOT the difficulty axis.
- `level`: the CTF difficulty grid, a closed set. Exactly one of `very-easy`,
  `easy`, `medium`, `hard`, `insane`.
- `flag`: must match the `ESPILON{...}` shape (literal `ESPILON`, one `{...}`
  block, at least one character, no nested braces). Make it concrete, never a
  placeholder pattern. For a static challenge the flag is derived from the
  artifact; `solve.py` proves it is recoverable from `files/` alone.
- `tags`: drive the related-wiki card. Quote any tag that looks numeric (a bare
  `802154` parses as an integer).
- `files`: pin the exact player-facing downloads. Without this key every regular
  file under `files/` is attached, so a stray scratch file leaks.
- `description`: the player-facing brief. State the task and the exact answer
  format. Use a folded `>` block to avoid the `': '` YAML trap. It states; it
  does not interpret.
- `technique`: the private design note. State the intended solve path and why
  shortcuts fail, so a reviewer can judge difficulty.
- `hints`: a non-empty list of non-empty strings, a rung ladder that teaches the
  how without handing over the answer. The last rung must not print the flag or
  the exploit verbatim.
- `description_fr`, `technique_fr`, `hints_fr`: the French twin. Natural
  technical French with real accents; keep tool and protocol names in English. A
  missing FR field falls back to EN, so ship FR when the challenge is bilingual.

## Topology

How the three scripts and the flag relate:

```
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

The invariant to hold: the artifact encodes the answer, the build is
deterministic, and `solve.py` reproduces `meta.yml`'s flag exactly. Break any one
and the challenge is unproven.

## Image and asset rule

A static challenge has no hero image. Player-facing assets are the downloads in
`files/`, and they are offered to the player exactly as pinned by `files:`. Do
not drop a decorative image into `files/`: it would be served as a download.
Illustrations belong in the related wiki entry or the course that teaches the
challenge, not in the artifact folder.

## Run the local checks

From the kit root, offline, no platform and no database:

```bash
# 1. Build the artifact (deterministic; safe to rerun).
python3 -I templates/static-challenge/generate.py

# 2. Prove the challenge is solvable from the artifact alone and the flag matches.
python3 -I templates/static-challenge/solve.py

# 3. Validate the meta record.
python3 -I validators/validate_static_meta.py templates/static-challenge

# 4. Scan the French fields for stripped accents.
python3 -I validators/check_fr_accents.py templates/static-challenge
```

Point these at your own challenge folder instead of `templates/static-challenge`.
All four must exit 0.

## How it reaches the platform

You do not seed or deploy. Submit the folder through the Espilon Learn member
portal. When your submission is ingested, the Espilon maintainers create the
challenge record, attach the files you pinned, and wire any course lesson that
names the challenge by slug. Artifact bytes a course depends on are pinned by
sha256 on the maintainer side, which is why `generate.py` must stay
deterministic.

## Traps that cost time

- The `': '` YAML trap. A plain multi-line `description` or hint that contains
  `': '` or a trailing `:` breaks the parse. Use a folded `>` block or quote the
  string. This is the single most common real-world break.
- A flag that is a placeholder pattern, not a concrete value. The flag must be
  the exact string the solver yields.
- No runnable reference solver. A static challenge whose `solve.py` does not run
  stdlib-only (or with a pinned dependency) is unproven. Do not ship it.
- `category` is not `level`. `category` groups the challenge; `level` is the
  closed CTF grid. Mixing them splits the UI group or fails validation.
- An un-pinned `files:`. Every file under `files/` ships unless you pin the list.
- French asserted by reading. FR has shipped accent-stripped more than once.
  Run the FR-accent check; do not eyeball it.
- A drifting artifact. If `generate.py` is not deterministic, every byte-level
  pin a course makes against the artifact goes stale silently.
