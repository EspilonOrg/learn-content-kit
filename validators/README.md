# Local validators

These are the checks a contributor can run offline, with no platform and no
database, before submitting content. They need Python 3 and PyYAML:

```bash
pip install pyyaml
```

Run them with `-I` (isolated mode) so they load only their own code and the
standard library, never a stray module from the working directory.

## What each one checks

### validate_static_meta.py

Validates a static challenge `meta.yml`: that it is valid YAML (the number one
real-world break is a `': '` inside an unquoted hint), that every required key is
present and well-formed, that the flag matches the `ESPILON{...}` shape, that
`category` is lowercase kebab-case, that `level` is one of the closed CTF grid
values, and that `hints` is a non-empty ladder.

```bash
python3 -I validators/validate_static_meta.py templates/static-challenge
```

Point it at your own challenge directory. Exit 0 means pass.

### check_fr_accents.py

A negative accent scan over the French fields of a static challenge `meta.yml`
(`description_fr`, `technique_fr`, `hints_fr`, and any other `*_fr` field). It
strips the parts where flat ASCII is correct (code spans, URLs, all-caps
identifiers, flag braces), then checks what remains word by word against a list
of French words whose only correct spelling carries an accent, and asserts each
French field carries at least one accent. Reading the French is not a check; this
is.

```bash
python3 -I validators/check_fr_accents.py templates/static-challenge
```

It depends on `bilingual_doc.py` in this directory. Exit 0 means pass.

### bilingual_doc.py

Not a check you run directly. It is the shared rule that splits a bilingual
document into its English and French halves, imported by `check_fr_accents.py`.

## What is NOT here, and why

Some checks cannot run without the platform or the full content corpus, so they
run on the maintainer side when your submission is ingested. Do not expect a
green light from this directory for them:

- The course sync and its structural gates (TLDR length, the TYPE and
  ARCHETYPE_ROLE allowlist, artifact resolution) need a database.
- The course and wiki French-accent gates calibrate against the whole published
  corpus, so they cannot judge a single submission in isolation.
- The wiki related-reference check needs the live gear and course catalogue.
- A Model-B lab has no field validator yet; diff `lab.yaml` against a shipped
  reference lab and verify the compose constraints by hand.

The per-type docs under `docs/` say, for each type, exactly which checks you run
here and which are maintainer-side.
