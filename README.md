# <img src="assets/espilon-logo.png" alt="Espilon" width="48" align="top"> Espilon Learn content-authoring kit

Français: [README.fr.md](README.fr.md)

Templates and documentation for contributing content to Espilon Learn, the
cybersecurity learning platform at [learn.espilon.net](https://learn.espilon.net),
run by the Espilon association. Copy a template, fill it in, run the local
checks, and submit through the member portal. You never deploy; the maintainers
ingest and publish accepted submissions.

## Contents

- [What you can build](#what-you-can-build)
- [How it works](#how-it-works)
- [Run the local checks](#run-the-local-checks)
- [House rules](#house-rules)
- [License](#license)

## What you can build

| Content type | Template to copy | Guide |
|---|---|---|
| A static challenge | [`templates/static-challenge/`](templates/static-challenge) | [`docs/static-challenge.md`](docs/static-challenge.md) |
| A Model-B lab | [`templates/model-b-lab/`](templates/model-b-lab) | [`docs/model-b-lab.md`](docs/model-b-lab.md) |
| A course | [`templates/course/`](templates/course) | [`docs/course.md`](docs/course.md) |
| A wiki entry | [`templates/wiki/`](templates/wiki) | [`docs/wiki-entry.md`](docs/wiki-entry.md) |

Each template is a real, working example, not a sketch. The static-challenge
template passes the shipped validators as-is.

- A **static challenge** is a self-contained puzzle: downloadable files and a
  flag the player recovers from them alone. No server.
- A **Model-B lab** is a live, per-session target the player attacks from their
  own machine. The lab ships only the target; the flag travels over the protocol.
- A **course** is a bilingual sequence of lessons that teaches a subject and ends
  by applying it to a challenge or a lab.
- A **wiki entry** is a bilingual reference page about one thing: a chip, a
  protocol, a bus, a concept.

## How it works

1. Copy the template for your content type into a working folder.
2. Fill it in, following its guide under [`docs/`](docs).
3. Run the local checks (see [`validators/README.md`](validators/README.md) and
   the guide).
4. Submit through the Espilon Learn member portal.

Each guide states exactly which checks you run locally and which the maintainers
run at ingestion.

## Run the local checks

```bash
pip install pyyaml

# Static challenge: build the artifact, prove it solves, validate, scan FR.
python3 -I templates/static-challenge/generate.py
python3 -I templates/static-challenge/solve.py
python3 -I validators/validate_static_meta.py templates/static-challenge
python3 -I validators/check_fr_accents.py templates/static-challenge

# Model-B lab: field and compose check.
python3 -I validators/check_lab_yaml.py templates/model-b-lab
```

Point the validators at your own folder instead of the template. Courses and
wiki entries carry checks that need the platform or the full content corpus;
those run on the maintainer side at ingestion.

## House rules

Content is bilingual (English and French), carries real French accents, and uses
no emoji and no em dash or en dash. The full rules and how to propose content are
in [`CONTRIBUTING.md`](CONTRIBUTING.md).

## License

MIT. See [`LICENSE`](LICENSE).

The Espilon name and logo are trademarks of the Espilon association and are not
covered by the MIT license. The MIT license applies to the templates, scripts
and documentation in this repository, not to the Espilon marks.
