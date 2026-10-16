# Authoring a wiki entry

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

A reference page about one thing: a chip, a protocol, a bus, a concept. It is
bilingual, it links to the courses and gear that use it, and it can carry one
structured in-page diagram. It is standalone reading, not a lesson.

## Where it lives

Author it from `templates/wiki/`: `example-entry.md` and its `example-entry.fr.md`
twin. Copy both, rename them to your slug, fill them in, and submit both through
the Espilon Learn member portal. On ingestion the maintainers upsert the entry,
run the corpus-wide French-accent gate over every FR surface, check the related
references against the live catalogue, and publish it under its category.

## The template

```text
wiki/
  <slug>.md      EN: frontmatter + markdown body + optional diagram block
  <slug>.fr.md   FR: translates title and summary; body is the French markdown
```

The `.fr.md` sidecar translates only the `title` and `summary` from the
frontmatter; its body is the full French prose. A missing FR body falls back to
the English body, so a half-translated entry still renders, silently in English.

## Field reference

### Frontmatter

```text
title, category, slug, order, summary, tags, terms, icon, published,
image, related_gear, related_courses, diagram
```

| Field | Rule |
|---|---|
| `title`, `slug` | The display name and the unique identifier. |
| `category` | Groups the entry on the category index. Load-bearing. |
| `summary` | One or two lines under the title and on the index. |
| `tags` | Free-text keywords. Quote anything numeric-looking (a bare `802154` parses as an integer). |
| `terms` | The phrases that auto-link to this entry from lesson prose. |
| `icon` | A short glyph or code. |
| `published` | `true` to show the entry. |
| `image` | Optional hero image (see [Images](#images)). |
| `related_gear`, `related_courses` | Slugs of the gear and courses that use this thing; they surface as cards. Put a real platform slug. You do not have the full catalogue, so the maintainers validate these at ingestion and drop any that does not resolve rather than ship it broken. |
| `diagram` | Optional structured in-page diagram (see [Images](#images)). |

Everything in the frontmatter degrades safely, so a half-filled entry still
renders. `slug` and `category` are the two that must be right.

### The body

Open with a one-paragraph, bold-led definition, then adapt the section skeleton
the template ships: what it is, why it matters, how it works, attack surface and
how to assess one, pitfalls, further reading. Prefer a real runnable command over
prose where a command is clearer. Keep hardware and security jargon in English in
both languages. Do not invent facts; draw them from entries that already exist.

## Local checks

The wiki French-accent gate is corpus-coupled, and the related-reference check
needs the full gear and course catalogue, so both run on the maintainer side at
ingestion and are not shippable here. Before you submit, verify by hand:

- the FR sidecar carries real accents on the `title`, the `summary`, the body,
  and the `fr:` leaves of any `diagram:` block, asserted per word;
- `tags` that look numeric are quoted;
- the `diagram:` block, if present, is one known type;
- `related_gear` and `related_courses` hold real platform slugs.

## Topology

```text
  wiki entry
   |
   +-- <slug>.md       EN frontmatter + EN body + (optional) diagram: block
   |                                             |
   |                                     fr: leaves inside diagram
   |                                     are the FR diagram labels
   +-- <slug>.fr.md    FR title + FR summary + FR body
                          |
                   falls back to EN body if absent
```

## Images

Two separate things:

- **`image`**: one optional hero image. Reference it as `img/wiki/<slug>.webp` in
  the frontmatter, and submit the actual webp alongside the two markdown files
  through the member portal (a 16:9 webp, named for your slug). The maintainers
  place it at that path at ingestion; you do not commit a binary into a content
  submission. At most one per entry. With no image, drop the `image:` line and
  the entry still renders.
- **`diagram`**: one optional structured diagram declared in the EN frontmatter.
  The schema holds at most one, and it is typed: pick the type that fits the
  subject (`timing`, `wire`, `bus`, `tree` or `partition`). Its text leaves carry
  both `en` and `fr` labels. Prefer the structured diagram over a raster image
  where the subject is spatial; delete the block if a diagram does not help.

## Traps

- **A missing or empty FR body.** The entry falls back to English without a word
  of warning, so "we translated it" and "the FR file is a stub" look identical on
  the page. Write the French body.
- **Accents missing off the body.** They have gone missing in the frontmatter
  `summary`, in the `fr:` leaves of the `diagram:` block, and inside French prose
  carried in fenced code comments. Assert every FR surface, not just the body.
- **A numeric `tag` left unquoted.** `802154` becomes an integer and the tag
  breaks.
- **More than one diagram, or an unknown diagram type.** The schema holds one
  typed diagram; a second is dropped.
- **A placeholder left in `related_courses` or `related_gear`.** Replace it with a
  real platform slug; the maintainers validate these at ingestion and drop any
  that does not resolve, so a forgotten placeholder silently loses the card.

## Open gaps

The French-accent gate and the related-reference check are corpus- and
catalogue-coupled, so they run on the maintainer side at ingestion and cannot be
shipped here. Reading the French is not a check; assert it per word before you
submit.
