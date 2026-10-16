# Contributing

Thank you for wanting to add content to Espilon Learn. This file is the house
rules and how to propose content. The step-by-step for each content type is in
`docs/`; this is what applies to all of them.

## House rules

These are not style preferences; the platform and its gates enforce them.

- **No em dash and no en dash, anywhere.** Use a plain hyphen. This applies to
  every file: prose, code comments, YAML, commit messages.
- **No emoji, anywhere.**
- **Bilingual, English and French.** Content ships in both languages. The
  structural truth is English; the French is a real translation of the prose.
- **Real French accents, asserted per word.** French content has shipped
  accent-stripped more than once, always because someone typed flat ASCII and
  then asserted the accents were there by reading. Reading is not a check. Where
  a validator exists, run it; where one does not, assert each French surface word
  by word. Keep tool and protocol names in English inside both languages.
- **No mention of any AI vendor or assistant** in content, commits, or docs.
- **Conventional Commits.** For example `feat(course): add the LoRaWAN join
  course` or `fix(wiki): restore the accent on the DNP3 summary`.

## How to propose content

1. Pick the content type and read its doc under `docs/`.
2. Copy the matching template from `templates/` into a working folder and fill it
   in. Keep the example structure; replace the example values with yours.
3. Run every local check the doc lists for that type (see `validators/README.md`).
   A check that did not run is not a check that passed; a check that is red is not
   ready to submit.
4. Submit through the Espilon Learn member portal. The maintainers review,
   ingest, and publish accepted submissions. You do not deploy anything yourself.

## When something is ambiguous

If this kit and a published example disagree, or a convention was never written
down, ask through the portal before you guess. Picking one quietly and shipping it
is how a wrong convention spreads. It is always cheaper to ask.
