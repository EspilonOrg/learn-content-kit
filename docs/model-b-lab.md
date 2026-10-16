# Authoring a Model-B lab

Français: [model-b-lab.fr.md](model-b-lab.fr.md)

A Model-B lab is a live, per-session target the player attacks from their own
machine. The lab ships only the target service or services; the player brings
their own tools (a Kali box, the `espilon-probe` client, whatever the protocol
needs). The flag travels over the protocol. There is no in-lab shell and no
in-lab file.

That delivery model is the whole point and it has a name: Model B. The player
brings the attacker side; you ship the target only.

Template: `templates/model-b-lab/` (`lab.yaml` next to `compose.yaml`). Copy both
files, fill them in, run the local field check, and submit through the Espilon
Learn member portal. The maintainers place the lab in the platform's labs
repository when it is ingested. You do not deploy it yourself.

The field checklist below is the contract. A local checker, `check_lab_yaml.py`,
verifies the parts of it that can be checked offline (the enums, the flag shape,
the exactly-one-of rule, the success_criteria shape, and the compose
strict-subset rules). It is a field linter, not the platform's own gate: the
runtime applies the same compose rules when it spawns the lab.

## The files

```
model-b-lab/
  lab.yaml       metadata: slug, category, difficulty, points, flag(s), success criteria
  compose.yaml   the runtime: the target service(s), the flag injected at spawn
```

A real lab also carries the image build context (a `target/` directory with a
Dockerfile) referenced by `compose.yaml`'s `build:`. That is yours to build; the
template shows the two declarative files the platform reads.

## Fill in lab.yaml

- `slug`: `lab-` prefix. The maintainers reconcile this slug with the live lab
  record at ingestion, so keep it stable once submitted.
- `category`: a closed enum, independent of any folder name:
  `hardware firmware iot ot-ics esp32 wifi bluetooth drone camera misc`.
- `difficulty`: closed enum `easy medium hard insane`, tied loosely to `points`
  (easy up to 200, hard from 300).
- `description`: the player-facing brief. State the protocol, the objective, and
  the attack class, then restate the Model-B contract so expectations are set.
- `archetype`: a front-end hint that selects which viewer renders beside the
  session panel (for example `iot-mqtt`).
- `radios_required`, `caps_required`, `duration_minutes`: runtime requests. Caps
  off the allowlist are denied; `duration_minutes` is the auto-destroy TTL.
- `success_criteria`: `type: flag_submit` with an always-available `hint`. Keep
  the real method in the course and the paid hint rungs, not here.

### The flag, pick exactly one shape

Declare exactly one of `flag`, `flag_generator` or `flags`.

1. Single static flag (`flag:`, the template default). Its value must equal the
   value `compose.yaml` injects at spawn, byte for byte.
2. Session-scoped generator (`flag_generator:`), one of:
   - `uuid`: the flag is `ESPILON{<uuid4 hex>}`, a fresh random value per
     session.
   - `wordlist`: the flag is a random entry per session drawn from a
     `flags/wordlist.txt` you ship beside `lab.yaml`, one candidate flag per
     line. Use it when you want human-readable per-session flags.
   - `hmac:<keyref>`: the flag is `ESPILON{<hmac(secret, session_id)>}`.
     `<keyref>` names a secret the maintainers hold on the platform (you do not
     ship the secret); the grader re-derives the expected flag from the secret
     and the session id. Use it when a flag must be verifiable server-side
     without storing it.
3. Multi-flag staged objectives (`flags:`), a list with one entry per stage,
   each carrying `slug`, `label`, `content` (an `ESPILON{...}` flag), `points`,
   `order` and `hint`. The running image must expose each `content` over the
   protocol at runtime. Example:

   ```yaml
   flags:
     - slug: stage-1
       label: What the player achieved to earn this flag
       content: ESPILON{stage_one_fl4g}
       points: 100
       order: 1
       hint: |
         Rung guidance for this specific stage.
     - slug: stage-2
       label: The deeper objective
       content: ESPILON{stage_two_fl4g}
       points: 100
       order: 2
       hint: |
         Rung guidance for stage two.
   ```

## Fill in compose.yaml

The runtime parses `compose.yaml` as a STRICT subset of Compose. These fields are
rejected: `privileged`, `cap_add`, bind mounts (volumes to host paths), and host
network mode. Host ports are ignored because the runtime assigns one ephemeral
host port per session, so list the container port only. `build:` is the image
build context and is ignored at runtime; the runtime reads only `image:`.

The flag is injected here at spawn through the service environment, never baked
into the image. Its value must match `lab.yaml` byte for byte. The target reads
it from the environment and emits it over the protocol.

## Field checklist

Everything the local checker enforces, so you can see the whole contract at once:

- `lab.yaml` has `slug` (with the `lab-` prefix), `title`, `category`,
  `difficulty`, `description` and `success_criteria`.
- `category` is one of:
  `hardware firmware iot ot-ics esp32 wifi bluetooth drone camera misc`.
- `difficulty` is one of: `easy medium hard insane`.
- exactly one of `flag`, `flag_generator`, `flags` is declared.
  - `flag` matches the `ESPILON{...}` shape.
  - `flag_generator` is `uuid`, `wordlist`, or `hmac:<keyref>` with a non-empty
    keyref.
  - `flags` is a non-empty list, each entry carrying `slug`, `label`, `content`
    (an `ESPILON{...}` flag), `points` and `order`.
- `success_criteria` is a mapping with `type: flag_submit` and a non-empty
  `hint`.
- `compose.yaml` has no `privileged`, no `cap_add`, no host-path bind mounts and
  no host network mode.
- for a single-flag lab, a service injects `FLAG=<the lab.yaml flag>` in its
  environment, byte for byte.

## Run the local check

```bash
pip install pyyaml
python3 -I validators/check_lab_yaml.py templates/model-b-lab
```

Point it at your own lab folder instead of the template. Exit 0 means the fields
are well-formed. It does not and cannot judge whether the lab teaches well or
whether the target actually emits the flag at runtime; that is on you and on the
maintainer review.

## Topology

```
   player's own machine (Kali, espilon-probe, ...)
            |
            |  ephemeral host port, assigned per session
            v
   +--------------------+        internal network (internal: true)
   |  target service    | -----------------------------+
   |  FLAG from env      |                              |
   |  emits over proto   |                        +-----------+
   +--------------------+                         | broker/db |
            ^                                     | internal   |
            |  no shell, no file, no ttyd         +-----------+
   flag reaches the player ONLY over the protocol
```

A second service (a database, a broker) is allowed. Put shared services on a
Compose network with `internal: true` and address them by service name. They
must have no host-side address.

## Image and asset rule

A lab ships no uploaded image. The `archetype` field selects the built-in viewer
that renders beside the session panel. Do not put screenshots or decorative
assets inside the target image. Any illustration belongs in the course that
teaches the lab.

## How it reaches the platform

Submit `lab.yaml`, `compose.yaml` and your image build context through the member
portal. The maintainers build and register the image, reconcile the slug with the
live lab record, and wire any lesson that back-links the lab. Run the local field
check first (see above) so the fields and compose constraints are clean before
you submit.

## Traps that cost time

- A flag baked into the image instead of injected at spawn. It must come from
  the environment and match `lab.yaml` exactly.
- A flag on the filesystem. A single-container lab leaks the flag through `grep`,
  `env` or a readable file. Model B forbids an in-lab shell and file for exactly
  this reason: the flag must only ever arrive over the protocol.
- A rejected compose field. `privileged`, `cap_add`, host-path volumes and host
  networking are refused; the lab will not start.
- A verification harness that lies depending on where it runs. An internal
  service (a broker behind `internal: true`) has no host-side address, so a check
  run from outside the session network reports false defects against a healthy
  lab. Run any check from inside the session network, never from the host.
- `category` confused with a folder name. It is a closed enum; pick the enum
  value, not the directory the lab is filed under.
- Declaring more than one of `flag` / `flag_generator` / `flags`. Exactly one.
  The local checker flags this, but it is worth stating: a stray `flag:` left
  above a `flags:` list is the common slip.
- Assuming a green local check means the lab is done. It means the fields are
  well-formed. Whether the target emits the flag over the protocol at runtime,
  and whether the lab teaches, is on you and the maintainer review. When a rule
  here is genuinely unclear for your protocol, ask through the portal rather
  than guessing.
