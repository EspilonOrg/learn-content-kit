# Authoring a wiki entry

A wiki entry is a reference page about one thing: a chip, a protocol, a bus, a
concept. It is bilingual, it links to the courses and gear that use it, and it
can carry one structured in-page diagram. It is standalone reading, not a lesson.

Template: `templates/wiki/` (`example-entry.md` and its `example-entry.fr.md`
twin). Copy both, rename them to your slug, and fill them in.

## The files

```
wiki/
  <slug>.md      EN: frontmatter + markdown body + optional diagram block
  <slug>.fr.md   FR: translates title and summary; body is the French markdown
```

The `.fr.md` sidecar translates only the `title` and `summary` from the
frontmatter; its body is the full French prose. A missing FR body falls back to
the English body, so a half-translated entry still renders, silently in English.

## The EN frontmatter

```
title, category, slug, order, summary, tags, terms, icon, published,
image, related_gear, related_courses, diagram
```

- `title`, `slug`: the display name and the unique identifier.
- `category`: groups the entry on the category index. Load-bearing.
- `summary`: one or two lines under the title and on the index.
- `tags`: free-text keywords. Quote anything that looks numeric (a bare `802154`
  parses as an integer).
- `terms`: the phrases that auto-link to this entry from lesson prose.
- `icon`: a short glyph or code.
- `published`: `true` to show it.
- `image`: the optional hero image (see the image rule below).
- `related_gear`, `related_courses`: slugs of the gear and courses that use this
  thing. They surface as cards on the page.
- `diagram`: an optional structured diagram (see the diagram rule below).

Everything in the frontmatter degrades safely, so a half-filled entry still
renders. `slug` and `category` are the two that must be right.

## The body

Open on a one-paragraph definition in bold-led prose, then adapt the section
skeleton the template ships: what it is, why it matters, how it works, attack
surface and how to assess one, pitfalls, further reading. Prefer a real runnable
command over prose where a command is clearer. Keep hardware and security jargon
in English inside both languages. Do not invent facts; draw them from entries
that already exist.

## Topology

```
  wiki entry
   |
   +-- <slug>.md       EN frontmatter + EN body + (optional) diagram: block
   |                                                 |
   |                                         fr: leaves inside diagram
   |                                         are the FR diagram labels
   +-- <slug>.fr.md    FR title + FR summary + FR body
                          |
                   falls back to EN body if absent
```

<!-- SVG PLACEHOLDER: replace with a diagram of the entry pair and its surfaces -->

## Image and diagram rule

Two separate things:

- `image`: one optional hero image, referenced as `img/wiki/<slug>.webp`, a 16:9
  webp. At most one per entry.
- `diagram`: one optional structured diagram declared in the EN frontmatter. The
  schema holds at most one, and it is typed: pick the type that fits the subject
  (`timing`, `wire`, `bus`, `tree` or `partition`). Its text leaves carry both
  `en` and `fr` labels. Prefer the structured diagram over a raster image where
  the subject is spatial; delete the block if a diagram does not help.

## Run the local checks

The wiki French-accent gate is corpus-coupled (it calibrates against the full
published corpus) and the related-reference check needs the full gear and course
catalogue, so both run on the maintainer side at ingestion and are not shippable
here. Before you submit, verify by hand:

- the FR sidecar carries real accents on the `title`, the `summary`, the body,
  and the `fr:` leaves of any `diagram:` block, asserted per word;
- `tags` that look numeric are quoted;
- the `diagram:` block, if present, is one known type;
- `related_gear` and `related_courses` name slugs that actually exist.

## How it reaches the platform

Submit both files through the member portal. On ingestion the maintainers upsert
the entry, run the corpus-wide French-accent gate over every FR surface, check
the related references against the live catalogue, and publish it under its
category.

## Traps that cost time

- A missing or empty FR body. The entry falls back to English without a word of
  warning, so "we translated it" and "the FR file is a stub" look identical on
  the page. Write the French body.
- Accents missing off the body. They have gone missing in the frontmatter
  `summary` and in the `fr:` leaves of the `diagram:` block, and inside French
  prose carried in fenced code comments. Assert every FR surface, not just the
  body.
- A numeric `tag` left unquoted. `802154` becomes an integer and the tag breaks.
- More than one diagram, or an unknown diagram type. The schema holds one typed
  diagram; a second is dropped.
- A dead `related_courses` or `related_gear` slug. It renders as a broken card.
  Name slugs that exist.
