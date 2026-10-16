# Authoring a Model-B lab

A Model-B lab is a live, per-session target the player attacks from their own
machine. The lab ships only the target service or services; the player brings
their own tools (a Kali box, the `espilon-probe` client, whatever the protocol
needs). The flag travels over the protocol. There is no in-lab shell and no
in-lab file.

That delivery model is the whole point and it has a name: Model B. The player
brings the attacker side; you ship the target only.

Template: `templates/model-b-lab/` (`lab.yaml` next to `compose.yaml`). Copy both
files, fill them in, and submit through the Espilon Learn member portal. The
maintainers place the lab in the platform's labs repository when it is ingested.
You do not deploy it yourself.

There is no public validator for these fields yet, so this doc and the shipped
reference labs are the reference, not a gate. When this doc and a shipped lab
disagree, ask through the portal which is canonical. Do not guess.

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

1. Single static flag (the template default). Its value must equal the value
   `compose.yaml` injects at spawn, byte for byte.
2. Session-scoped generator: `flag_generator: uuid`, `wordlist`, or
   `hmac:<keyref>` for a per-session flag a grader can re-derive.
3. Multi-flag staged objectives: a `flags:` list, one entry per stage with its
   own `content`, `points`, `order` and `hint`. The running image must expose
   each `content` over the protocol at runtime.

## Fill in compose.yaml

The runtime parses `compose.yaml` as a STRICT subset of Compose. These fields are
rejected: `privileged`, `cap_add`, bind mounts (volumes to host paths), and host
network mode. Host ports are ignored because the runtime assigns one ephemeral
host port per session, so list the container port only. `build:` is the image
build context and is ignored at runtime; the runtime reads only `image:`.

The flag is injected here at spawn through the service environment, never baked
into the image. Its value must match `lab.yaml` byte for byte. The target reads
it from the environment and emits it over the protocol.

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

<!-- SVG PLACEHOLDER: replace with a diagram of the session network and flag path -->

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
live lab record, and wire any lesson that back-links the lab. There is no local
gate you can run against `lab.yaml`, so diff it against a shipped reference lab
and verify the compose runtime constraints by hand before you submit.

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
- Treating this doc as a gate. There is no validator here. The reference labs are
  the ground truth; when they and this doc differ, ask.
