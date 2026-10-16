# Authoring a course

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

A bilingual sequence of lessons, grouped into modules, that teaches a subject and
ends by applying it to a real artifact (a static challenge or a lab). A course is
text and structure only; the platform renders it.

## Where it lives

Author it from `templates/course/`. Copy the whole folder and replace the example
values; the template is a three-lesson, two-module, EN plus FR course that
follows the house format. Submit the folder through the Espilon Learn member
portal. On ingestion the maintainers create the course record, sync the lessons
and modules, and resolve each `ARTIFACT` to the matching challenge or lab. A
named artifact that does not exist yet is a warning, not a failure, so a typo in
an `ARTIFACT` slug leaves a lesson silently unwired. The maintainers pin the
bytes of any artifact a lesson depends on, by sha256.

## The template

```text
course/
  course.yaml                course identity: title, slug, difficulty, summary, track
  _modules.yaml              structure: module slugs, order, icons, archetype
  _artifacts.yaml            pins the challenge artifact bytes by sha256
  lesson-en/
    lessons.md               EN lessons (structural fields are read from here)
    module-text.yaml         EN module titles and descriptions
  lesson-fr/
    lessons.md               FR lessons (each writes a translation row)
    module-text.yaml         FR module titles and descriptions
```

Add a locale with a `lesson-<locale>/` directory holding the same two files. The
structural fields are read from `lesson-en` only; every other locale carries a
translation of the prose.

## Field reference

### course.yaml

The course identity, read by the maintainers to create the course record. All
five fields are required.

| Field | Rule |
|---|---|
| `title` | Display name, in English. |
| `slug` | Unique lowercase kebab-case identifier. |
| `difficulty` | The course difficulty axis, a closed set: `beginner`, `intermediate`, `advanced`. A different vocabulary from a static challenge's `level` (the CTF grid); do not mix them. |
| `summary` | One or two sentences for the catalogue card. Lead with the concrete scenario the course teaches. |
| `track` | The curriculum track slug this course belongs to. The maintainers map it to a live track at ingestion; if you are unsure which track fits, say so when you submit rather than guessing. |

### _modules.yaml

The structural module spec: no display strings here. Each module has a `slug`,
`order` and `icon`. The top-level `archetype` drives the course shape:

- `project` (archetype A, the default): theory is motivated by a practical need
  and delivered just in time.
- `reference` (archetype B): a cookbook of independent recipes.
- `fundamentals` (archetype C): a bottom-up concept build.

### lessons.md

One `lessons.md` per locale. Lessons are blocks delimited by
`===== LESSON START =====` and `===== LESSON END =====`, each carrying keyed
headers then a `CONTENT:` markdown body. The keys are `ORDER`, `TITLE`, `TYPE`,
`ARCHETYPE_ROLE`, `MODULE`, `TLDR`, `ESTIMATED_MINUTES`, `LEARNING_OUTCOMES`,
`FURTHER_READING`, `XP`, and the optional `ARTIFACT`.

| Key | Rule |
|---|---|
| `TYPE` | One of `theory`, `practical`, `challenge`, `quiz`, `lab`, `hands-on`. |
| `ARCHETYPE_ROLE` | The lesson's role in the shape. One of `hook`, `theory`, `setup`, `attempt`, `practice`, `deepdive`, `recipe`, `quiz`, `lab`. |
| `MODULE` | The module slug from `_modules.yaml`. |
| `TLDR` | One line, shown in the outline. Written to a `String(500)` column, so it must stay under 500 characters or the ingest aborts. |
| `LEARNING_OUTCOMES` | A list: what the reader can do after the lesson. |
| `FURTHER_READING` | `wiki:<slug>` references or `{kind: url, title, url}` entries that point at a primary source a reader can verify. |
| `ARTIFACT` | Wires the lesson to the thing it exercises. Syntax `<kind>:<slug>` where kind is `challenge` or `lab`. |

The `CONTENT:` body is markdown: H2 headings, fenced code and tables all render.

### TYPE and ARCHETYPE_ROLE allowlist

These are two separate allowlists joined by an OR: a lesson is accepted if its
`TYPE` is in the TYPE list OR its `ARCHETYPE_ROLE` is in the ROLE list. It is
rejected at ingest only when neither field is recognised, because it would
otherwise render with the wrong badge in the outline.

- Accepted `TYPE`: `theory`, `practical`, `challenge`, `quiz`, `lab`, `hands-on`.
- Accepted `ARCHETYPE_ROLE`: `hook`, `theory`, `setup`, `attempt`, `practice`,
  `deepdive`, `recipe`, `quiz`, `lab`.

One pairing constraint beyond the OR: a lesson whose `ARCHETYPE_ROLE` is `lab`
should wire to a `lab:` artifact, and a lesson whose role is `challenge` should
not wire to a `lab:` artifact. A mismatch is warned at ingest, not rejected.

### module-text.yaml

Per-locale module display strings, keyed by the slug from `_modules.yaml`: a
`title` and a `description` for each module, in that locale's language.

### _artifacts.yaml

Pins the exact bytes of every challenge artifact the lessons depend on, by
sha256, so a regenerated or drifted artifact is caught before a reader hits a
lesson whose baked facts (offsets, lengths, frame counts) no longer match.

```yaml
artifacts:
  - slug: <challenge-slug>        # matches an ARTIFACT: challenge:<slug> line
    path: <where the challenge lives in your submission>
    files:
      <filename>: sha256:<hex>    # one line per pinned player-facing file
```

The shipped `_artifacts.yaml` in this folder pins the companion
static-challenge template's `sample.bin`. Its hash is the real sha256 of that
file as `generate.py` produces it, so you can verify it:

```bash
python3 -c "import hashlib;print(hashlib.sha256(open('templates/static-challenge/files/sample.bin','rb').read()).hexdigest())"
```

A course that exercises no downloadable artifact (theory-only, or one that drives
only a live lab) needs no `_artifacts.yaml`; delete the file.

## Local checks

The course format is ingested by platform tooling that needs a database, so there
is no standalone course validator in this kit. Before you submit, verify by hand:

- every `TLDR` is under 500 characters;
- every lesson's `TYPE` or `ARCHETYPE_ROLE` is on the allowlist above;
- every `ARTIFACT` slug matches a challenge or lab you are also submitting, and
  every file it depends on is pinned in `_artifacts.yaml`;
- the FR locale carries real accents on every surface, asserted per word.

## Topology

```text
  _modules.yaml  (archetype, module slugs + order)
        |
        +--> lesson-en/lessons.md     (structural truth + EN prose)
        +--> lesson-fr/lessons.md     (FR translation rows)
        +--> lesson-*/module-text.yaml (per-locale module titles)
        |
   lesson block  --- ARTIFACT: challenge:<slug> --->  static challenge
                 --- ARTIFACT: lab:<slug>       --->  Model-B lab
```

The structural fields live once, in `lesson-en`. Every other locale carries the
same lesson blocks with translated `TITLE`, `TLDR`, outcomes and body, stored as
translation rows against the English lesson.

## Images

A course carries no raster uploads. Where the model is spatial (a bus, a
topology, a packet layout), inline a hand-written `<svg>` directly in the lesson
markdown: it renders natively. Do not reference an uploaded image file. Keep the
SVG simple and readable; it is part of the lesson source.

## Traps

- **A `TLDR` over 500 characters.** It is a `String(500)` column; one long TLDR
  aborts the whole course sync. Count the characters.
- **Structural drift between locales.** Structural fields are read from
  `lesson-en` only. A different `TYPE` or `MODULE` in the FR file does nothing and
  hides the mismatch.
- **A lesson where neither `TYPE` nor `ARCHETYPE_ROLE` is on the allowlist.** This
  is the only case rejected at ingest (the rule is an OR, not a pair match), and
  the rejection is what stops a lesson rendering with the wrong badge.
- **A typo'd `ARTIFACT` slug.** The ingest warns rather than fails, so the lesson
  ships unwired. Read the warnings.
- **A raster screenshot where an inline SVG belongs.** Uploaded images are not
  part of the lesson source and are not supported here.
- **French asserted by reading.** Ship genuinely accented FR; a missing or empty
  FR body silently falls back to English.

## Open gaps

The French-accent and course-structure gates are corpus-coupled and run on the
maintainer side at ingestion, so no standalone validator in this kit can judge a
single course. Reading the French is not a check; assert it per word. If you are
unsure which track a course belongs to, ask rather than guess.
