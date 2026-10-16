import hashlib
import json
import re
from pathlib import Path


def verify_bundle(root, manifest):
    root = Path(root).resolve(strict=True)
    spec = json.loads(Path(manifest).read_text(encoding="utf-8"))
    required = {"schema_version", "release_id", "components",
                "scope", "previous_release", "acceptance_report", "files"}
    if not isinstance(spec, dict) or set(spec) != required:
        raise ValueError("invalid manifest fields")
    if type(spec["schema_version"]) is not int or spec["schema_version"] != 1:
        raise ValueError("unsupported manifest version")
    for key in ("release_id", "previous_release", "acceptance_report"):
        if not isinstance(spec[key], str) or not spec[key]:
            raise ValueError("invalid manifest identifier")
    scope = spec["scope"]
    if not isinstance(scope, dict) or set(scope) != {"products", "deadline_ms"}:
        raise ValueError("invalid scope")
    if (not isinstance(scope["products"], list) or not scope["products"]
            or any(not isinstance(x, str) or not x for x in scope["products"])
            or type(scope["deadline_ms"]) is not int or scope["deadline_ms"] <= 0):
        raise ValueError("invalid scope values")
    components = spec["components"]
    if (not isinstance(components, dict)
            or set(components) != {"model", "preprocess", "thresholds", "runtime"}):
        raise ValueError("invalid components")
    files = spec["files"]
    if not isinstance(files, dict) or not files:
        raise ValueError("empty file manifest")
    needed = list(components.values()) + [spec["acceptance_report"]]
    if any(not isinstance(x, str) or x not in files for x in needed):
        raise ValueError("unlisted component")
    for relative, expected in files.items():
        if not isinstance(relative, str) or not relative:
            raise ValueError("invalid file path")
        if not isinstance(expected, str) or re.fullmatch(r"[0-9a-fA-F]{64}", expected) is None:
            raise ValueError("invalid SHA-256 value")
        source = (root / relative).resolve()
        if Path(relative).is_absolute() or not source.is_relative_to(root):
            raise ValueError("path outside bundle")
        if not source.is_file():
            raise ValueError("missing bundle file")
        digest = hashlib.sha256()
        with source.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
        if digest.hexdigest() != expected.lower():
            raise ValueError("digest mismatch")
    return True
