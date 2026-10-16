#!/usr/bin/env python3
"""check_lab_yaml.py - offline field check for a Model-B lab.yaml (+ compose.yaml).

Run it before you submit a lab. It checks the field rules a contributor can
verify without the platform: required keys, the two closed enums, exactly one of
flag / flag_generator / flags, the success_criteria shape, and the compose
strict-subset rules (no privileged, no cap_add, no host-path bind mounts, no host
network mode; the injected FLAG matches lab.yaml). It needs only the Python
standard library and PyYAML.

It is a field linter, not the platform's own gate: the runtime applies the same
compose rules when it spawns the lab. A green run here means your files are
well-formed, not that the lab is pedagogically done.

Usage
-----
    python3 -I validators/check_lab_yaml.py templates/model-b-lab
    python3 -I validators/check_lab_yaml.py path/to/your-lab

Exit code is 0 only if lab.yaml (and compose.yaml, if present) is clean.

Dependencies: Python 3 standard library + PyYAML.
"""
from __future__ import annotations

import os
import re
import sys

_FLAG_RE = re.compile(r"^ESPILON\{[^{}]+\}$")
_CATEGORIES = (
    "hardware", "firmware", "iot", "ot-ics", "esp32", "wifi",
    "bluetooth", "drone", "camera", "misc",
)
_DIFFICULTIES = ("easy", "medium", "hard", "insane")
_FLAG_GENERATORS = ("uuid", "wordlist")  # plus hmac:<keyref>, handled separately
_REQUIRED = ("slug", "title", "category", "difficulty", "description", "success_criteria")

_USAGE = (
    "usage: check_lab_yaml.py <lab-folder>\n"
    "\n"
    "Pass the folder holding lab.yaml (and compose.yaml), or a path to a lab.yaml.\n"
    "For example:\n"
    "       python3 -I validators/check_lab_yaml.py templates/model-b-lab"
)


def _yaml():
    try:
        import yaml
    except ImportError:  # pragma: no cover - environment guard
        sys.exit("ERROR: PyYAML is not installed -- pip install pyyaml")
    return yaml


def _format_yaml_error(path: str, exc) -> str:
    """Turn a PyYAML exception into a terse file:line:col message, the same way
    validate_static_meta.py does, so a malformed value never dumps a traceback."""
    mark = getattr(exc, "problem_mark", None) or getattr(exc, "context_mark", None)
    reason = getattr(exc, "problem", None) or str(exc).splitlines()[0]
    if mark is not None:
        loc = f"{path}:{mark.line + 1}:{mark.column + 1}"
        hint = ""
        if reason and "mapping values are not allowed" in reason:
            hint = (
                "  (an unquoted multi-line value contains ': ' or a trailing ':' "
                "-- use a '>' block scalar or quote the string)"
            )
        elif reason and "could not find expected ':'" in reason:
            hint = (
                "  (a plain scalar broke into what looks like a mapping -- "
                "use a '>' block scalar or quote the string)"
            )
        return f"{loc}  YAML syntax error: {reason}{hint}"
    return f"{path}  YAML syntax error: {reason}"


def _load(path: str):
    """Return (data, errors). On a YAML syntax error data is None and errors
    holds a single clean 'file:line:col  reason' string."""
    yaml = _yaml()
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh), []
    except yaml.YAMLError as exc:
        return None, [_format_yaml_error(path, exc)]


def _check_flag_shape(label: str, value) -> list[str]:
    if not isinstance(value, str) or not _FLAG_RE.match(value.strip()):
        return [f"{label} does not match ESPILON{{...}} shape: {value!r}"]
    return []


def check_lab_yaml(lab_path: str) -> list[str]:
    errs: list[str] = []
    data, load_errs = _load(lab_path)
    if load_errs:
        return load_errs
    if not isinstance(data, dict):
        return [f"{lab_path}: top-level document is not a mapping"]

    for key in _REQUIRED:
        val = data.get(key)
        if key not in data:
            errs.append(f"missing required key: '{key}'")
        elif val is None or (isinstance(val, str) and not val.strip()):
            errs.append(f"required key '{key}' is empty")

    slug = data.get("slug")
    if isinstance(slug, str) and not slug.startswith("lab-"):
        errs.append(f"slug {slug!r} must start with 'lab-'")

    category = data.get("category")
    if isinstance(category, str) and category not in _CATEGORIES:
        errs.append(
            f"category {category!r} is not in the enum ({'/'.join(_CATEGORIES)})"
        )

    difficulty = data.get("difficulty")
    if isinstance(difficulty, str) and difficulty not in _DIFFICULTIES:
        errs.append(
            f"difficulty {difficulty!r} is not in the enum "
            f"({'/'.join(_DIFFICULTIES)})"
        )

    points = data.get("points")
    if points is not None and (isinstance(points, bool) or not isinstance(points, int)):
        errs.append(f"points must be an integer, got {points!r}")

    # Exactly one of flag / flag_generator / flags.
    present = [k for k in ("flag", "flag_generator", "flags") if k in data and data.get(k) not in (None, "")]
    if len(present) == 0:
        errs.append("declare exactly one of 'flag', 'flag_generator' or 'flags'; none found")
    elif len(present) > 1:
        errs.append(f"declare exactly ONE of 'flag'/'flag_generator'/'flags', found {present}")
    else:
        which = present[0]
        if which == "flag":
            errs.extend(_check_flag_shape("flag", data["flag"]))
        elif which == "flag_generator":
            gen = data["flag_generator"]
            ok = isinstance(gen, str) and (
                gen in _FLAG_GENERATORS or gen.startswith("hmac:")
            )
            if not ok:
                errs.append(
                    f"flag_generator {gen!r} must be 'uuid', 'wordlist' or "
                    f"'hmac:<keyref>'"
                )
            if isinstance(gen, str) and gen.startswith("hmac:") and not gen[len("hmac:"):].strip():
                errs.append("flag_generator 'hmac:<keyref>' needs a non-empty keyref")
        elif which == "flags":
            flags = data["flags"]
            if not isinstance(flags, list) or not flags:
                errs.append("'flags' must be a non-empty list of stage mappings")
            else:
                for i, f in enumerate(flags):
                    if not isinstance(f, dict):
                        errs.append(f"flags[{i}] must be a mapping")
                        continue
                    for req in ("slug", "label", "content", "points", "order"):
                        if req not in f:
                            errs.append(f"flags[{i}] missing '{req}'")
                    if "content" in f:
                        errs.extend(_check_flag_shape(f"flags[{i}].content", f["content"]))

    # success_criteria shape.
    sc = data.get("success_criteria")
    if isinstance(sc, dict):
        if sc.get("type") != "flag_submit":
            errs.append(
                f"success_criteria.type should be 'flag_submit', got {sc.get('type')!r}"
            )
        if not (isinstance(sc.get("hint"), str) and sc["hint"].strip()):
            errs.append("success_criteria.hint must be a non-empty string")
    elif sc is not None:
        errs.append("success_criteria must be a mapping with 'type' and 'hint'")

    return [f"{lab_path}: {e}" for e in errs]


def check_compose(compose_path: str, lab_data: dict) -> list[str]:
    errs: list[str] = []
    data, load_errs = _load(compose_path)
    if load_errs:
        return load_errs
    if not isinstance(data, dict):
        return [f"{compose_path}: top-level document is not a mapping"]
    services = data.get("services")
    if not isinstance(services, dict) or not services:
        return [f"{compose_path}: no 'services' mapping"]

    injected_flags: set[str] = set()
    for name, svc in services.items():
        if not isinstance(svc, dict):
            errs.append(f"service '{name}' is not a mapping")
            continue
        if svc.get("privileged"):
            errs.append(f"service '{name}': 'privileged' is rejected by the runtime")
        if svc.get("cap_add"):
            errs.append(f"service '{name}': 'cap_add' is rejected by the runtime")
        if str(svc.get("network_mode", "")).strip() == "host":
            errs.append(f"service '{name}': host network mode is rejected")
        for vol in svc.get("volumes", []) or []:
            src = vol.split(":", 1)[0] if isinstance(vol, str) else str(vol)
            if src.startswith((".", "/", "~")):
                errs.append(
                    f"service '{name}': volume {vol!r} is a host-path bind mount, "
                    f"which is rejected (use a named volume or an internal service)"
                )
        env = svc.get("environment")
        pairs: dict[str, str] = {}
        if isinstance(env, list):
            for item in env:
                if isinstance(item, str) and "=" in item:
                    k, v = item.split("=", 1)
                    pairs[k.strip()] = v.strip()
        elif isinstance(env, dict):
            pairs = {str(k): str(v) for k, v in env.items()}
        if "FLAG" in pairs:
            injected_flags.add(pairs["FLAG"])

    # For a single-flag lab the injected FLAG must match lab.yaml exactly.
    declared = lab_data.get("flag")
    if isinstance(declared, str):
        if not injected_flags:
            errs.append(
                f"{compose_path}: lab.yaml declares a single 'flag' but no service "
                f"injects a FLAG env var; the flag must be injected at spawn"
            )
        elif declared not in injected_flags:
            errs.append(
                f"{compose_path}: injected FLAG {sorted(injected_flags)!r} does not "
                f"match lab.yaml flag {declared!r} (they must be byte-for-byte equal)"
            )
    return [f"{compose_path.rsplit('/', 1)[-1]}: {e.split(': ', 1)[-1]}" if e.startswith(compose_path) else e for e in errs]


def main(argv: list[str]) -> int:
    args = argv[1:]
    if not args:
        print(_USAGE, file=sys.stderr)
        return 2
    target = args[0]
    if os.path.isdir(target):
        lab_path = os.path.join(target, "lab.yaml")
        compose_path = os.path.join(target, "compose.yaml")
    else:
        lab_path = target
        compose_path = os.path.join(os.path.dirname(target), "compose.yaml")

    if not os.path.isfile(lab_path):
        print(f"{lab_path}  not found\n{_USAGE}", file=sys.stderr)
        return 2

    errs = check_lab_yaml(lab_path)
    lab_data, _lab_load_errs = _load(lab_path)
    # Only reach into compose when lab.yaml itself parsed; otherwise the lab
    # errors above already carry the clean YAML message.
    if not _lab_load_errs and os.path.isfile(compose_path) and isinstance(lab_data, dict):
        errs += check_compose(compose_path, lab_data)

    rel = os.path.relpath(lab_path)
    if errs:
        print(f"FAIL  {rel}")
        for e in errs:
            print(f"        {e}")
        print("=== 0/1 passed, 1 failed ===")
        return 1
    print(f"PASS  {rel}")
    print("=== 1/1 passed, 0 failed ===")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
