#!/usr/bin/env python3
"""Requirements registry validator (CI schema gate, GOV-001).

Loads docs/req/requirements.yaml and validates it against docs/req/req-schema.json
using a small dependency-free JSON Schema draft-07 subset validator.

Exit code 0 = valid; 1 = invalid (details printed to stderr).
"""
from __future__ import annotations

import io
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print("ERROR: PyYAML is required to validate the registry.", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "docs" / "req" / "requirements.yaml"
SCHEMA = ROOT / "docs" / "req" / "req-schema.json"


class ValidationError(Exception):
    pass


def _resolve(ref: str, schema: dict) -> dict:
    # Only local "#/definitions/..." references are used in this schema.
    assert ref.startswith("#/"), f"unsupported ref: {ref}"
    node: object = schema
    for part in ref.lstrip("#/").split("/"):
        node = node[part]  # type: ignore[index]
    return node  # type: ignore[return-value]


def validate(instance: object, schema: dict, root: dict, path: str) -> None:
    if "$ref" in schema:
        validate(instance, _resolve(schema["$ref"], root), root, path)
        return

    expected = schema.get("type")
    if expected == "object":
        if not isinstance(instance, dict):
            raise ValidationError(f"{path}: expected object, got {type(instance).__name__}")
        for req in schema.get("required", []):
            if req not in instance:
                raise ValidationError(f"{path}: missing required field '{req}'")
        props = schema.get("properties", {})
        additional = schema.get("additionalProperties", True)
        for key, value in instance.items():
            if key in props:
                validate(value, props[key], root, f"{path}.{key}")
            elif not additional:
                raise ValidationError(f"{path}: additional property '{key}' not allowed")
    elif expected == "array":
        if not isinstance(instance, list):
            raise ValidationError(f"{path}: expected array, got {type(instance).__name__}")
        item_schema = schema.get("items")
        if item_schema:
            for i, item in enumerate(instance):
                validate(item, item_schema, root, f"{path}[{i}]")
    elif expected == "string":
        if not isinstance(instance, str):
            raise ValidationError(f"{path}: expected string, got {type(instance).__name__}")
        if "minLength" in schema and len(instance) < schema["minLength"]:
            raise ValidationError(f"{path}: string shorter than {schema['minLength']}")
        if "pattern" in schema and not re.match(schema["pattern"], instance):
            raise ValidationError(f"{path}: '{instance}' does not match {schema['pattern']}")
    elif expected == "integer":
        if not isinstance(instance, int):
            raise ValidationError(f"{path}: expected integer")

    if "enum" in schema and instance not in schema["enum"]:
        raise ValidationError(f"{path}: '{instance}' not in {schema['enum']}")


def main() -> int:
    registry = yaml.safe_load(io.open(REGISTRY, encoding="utf-8"))
    schema = json.load(io.open(SCHEMA, encoding="utf-8"))
    try:
        validate(registry, schema, schema, "$")
    except ValidationError as exc:
        print(f"SCHEMA GATE FAILED: {exc}", file=sys.stderr)
        return 1

    ids = [r["id"] for r in registry["requirements"]]
    if len(ids) != len(set(ids)):
        print("SCHEMA GATE FAILED: duplicate requirement IDs", file=sys.stderr)
        return 1

    print(f"SCHEMA GATE PASSED: {len(ids)} requirements valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
