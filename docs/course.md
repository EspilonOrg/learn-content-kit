# Authoring a course

A course is a bilingual sequence of lessons, grouped into modules, that teaches a
subject and ends by applying it to a real artifact (a static challenge or a lab).
A course is text and structure only; the platform renders it.

Template: `templates/course/`. Copy the whole folder and replace the example
values. The template is a three-lesson, two-module, EN plus FR course that
follows the house format exactly.

## The files

```
course/
  _modules.yaml              structure: module slugs, order, icons, archetype
  lesson-en/
    lessons.md               EN lessons (structural fields are read from here)
    module-text.yaml         EN module titles and descriptions
  lesson-fr/
    lessons.md               FR lessons (each writes a translation row)
    module-text.yaml         FR module titles and descriptions
```

Add a locale by adding a `lesson-<locale>/` directory with the same two files.
Structural fields are taken from `lesson-en` only; every other locale writes a
translation of the prose.

## _modules.yaml

The structural module spec: no display strings here. Each module has a `slug`,
`order` and `icon`. The top-level `archetype` drives the course shape:

- `project` (archetype A, the default): theory is motivated by a practical need
  and delivered just in time.
- `reference` (archetype B): a cookbook of independent recipes.
- `fundamentals` (archetype C): a bottom-up concept build.

## lessons.md

One `lessons.md` per locale. Lessons are blocks delimited by
`===== LESSON START =====` and `===== LESSON END =====`. Each block carries keyed
headers followed by a `CONTENT:` markdown body. The keys:

`ORDER`, `TITLE`, `TYPE`, `ARCHETYPE_ROLE`, `MODULE`, `TLDR`,
`ESTIMATED_MINUTES`, `LEARNING_OUTCOMES`, `FURTHER_READING`, `XP`, and the
optional `ARTIFACT`.

- `TYPE`: `theory` or `practical`.
- `ARCHETYPE_ROLE`: the lesson's role in the shape (`hook`, `theory`, `practice`,
  `deepdive`). The `TYPE` and `ARCHETYPE_ROLE` pair must be a known combination.
- `MODULE`: the module slug from `_modules.yaml`.
- `TLDR`: one line, shown in the outline. It is written to a `String(500)`
  column, so it must stay under 500 characters or the ingest aborts.
- `LEARNING_OUTCOMES`: a list, what the reader can do after the lesson.
- `FURTHER_READING`: `wiki:<slug>` references or `{kind: url, title, url}` entries
  that point at a primary source a reader can verify.
- `ARTIFACT`: wires the lesson to the thing it exercises. Syntax `<kind>:<slug>`
  where kind is `challenge`, `box` or `lab`.

The `CONTENT:` body is markdown: H2 headings, fenced code and tables all render.

## module-text.yaml

Per-locale module display strings, keyed by the slug declared in `_modules.yaml`:
a `title` and a `description` for each module, in that locale's language.

## Topology

How the pieces wire together:

```
  _modules.yaml  (archetype, module slugs + order)
        |
        +--> lesson-en/lessons.md     (structural truth + EN prose)
        +--> lesson-fr/lessons.md     (FR translation rows)
        +--> lesson-*/module-text.yaml (per-locale module titles)
        |
   lesson block  --- ARTIFACT: challenge:<slug> --->  static challenge
                 --- ARTIFACT: lab:<slug>       --->  Model-B lab
```

<!-- SVG PLACEHOLDER: replace with a diagram of the module-to-lesson-to-artifact wiring -->

The structural fields live once, in `lesson-en`. Every other locale carries the
same lesson blocks with translated `TITLE`, `TLDR`, outcomes and body, and the
platform stores them as translation rows against the English lesson.

## Image and diagram rule

A course carries no raster uploads. Where the model is spatial (a bus, a
topology, a packet layout), inline a hand-written `<svg>` directly in the lesson
markdown: it renders natively. Do not reference an uploaded image file. Keep the
SVG simple and readable; it is part of the lesson source.

## Run the local checks

The course format is ingested by platform tooling that needs a database, so there
is no standalone course validator in this kit. Before you submit, verify by hand:

- every `TLDR` is under 500 characters;
- every `TYPE` plus `ARCHETYPE_ROLE` pair is one of the known combinations;
- every `ARTIFACT` slug matches a challenge or lab you are also submitting;
- the FR locale carries real accents on every surface, asserted per word.

The French-accent and course-structure gates are corpus-coupled and run on the
maintainer side at ingestion. Reading the French is not a check; assert it.

## How it reaches the platform

Submit the course folder through the member portal. On ingestion the Espilon
maintainers create the course record, sync the lessons and modules, and resolve
each `ARTIFACT` to the matching challenge or lab. If a named artifact does not
exist yet the ingest warns and continues, so a typo in an `ARTIFACT` slug leaves
a lesson silently unwired. The maintainers also pin the bytes of any artifact a
lesson depends on, by sha256.

## Traps that cost time

- `TLDR` over 500 characters. It is a `String(500)` column; one long TLDR aborts
  the whole course sync. Count the characters.
- Structural drift between locales. Structural fields are read from `lesson-en`
  only. Putting a different `TYPE` or `MODULE` in the FR file does nothing and
  hides the mismatch.
- An unknown `TYPE` plus `ARCHETYPE_ROLE` pair. It is rejected at ingest, which
  is what keeps a lesson from rendering with the wrong badge.
- A typo'd `ARTIFACT` slug. The ingest warns rather than fails, so the lesson
  ships unwired. Read the warnings.
- A raster screenshot where an inline SVG belongs. Uploaded images are not part
  of the lesson source and are not supported here.
- French asserted by reading. Ship genuinely accented FR; a missing or empty FR
  body silently falls back to English.
