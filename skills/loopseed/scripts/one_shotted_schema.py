"""Dependency-free validation for the JSON Schema subset used by LoopSeed."""

from __future__ import annotations

from typing import Any


def _matches_type(value: Any, expected: str) -> bool:
    checks = {
        "object": lambda item: isinstance(item, dict),
        "array": lambda item: isinstance(item, list),
        "string": lambda item: isinstance(item, str),
        "integer": lambda item: isinstance(item, int) and not isinstance(item, bool),
        "number": lambda item: isinstance(item, (int, float)) and not isinstance(item, bool),
        "boolean": lambda item: isinstance(item, bool),
        "null": lambda item: item is None,
    }
    check = checks.get(expected)
    return bool(check and check(value))


def validate_json_schema(value: Any, schema: dict[str, Any], location: str = "$") -> list[str]:
    errors: list[str] = []
    declared = schema.get("type")
    allowed = declared if isinstance(declared, list) else [declared] if declared else []
    if allowed and not any(_matches_type(value, str(item)) for item in allowed):
        return [f"{location} must have type {' or '.join(str(item) for item in allowed)}"]
    if "const" in schema and value != schema["const"]:
        errors.append(f"{location} must equal {schema['const']!r}")
    enum = schema.get("enum")
    if isinstance(enum, list) and value not in enum:
        errors.append(f"{location} must be one of {enum!r}")
    if isinstance(value, str):
        minimum = schema.get("minLength")
        if isinstance(minimum, int) and len(value) < minimum:
            errors.append(f"{location} must contain at least {minimum} characters")
    if isinstance(value, list):
        minimum = schema.get("minItems")
        maximum = schema.get("maxItems")
        if isinstance(minimum, int) and len(value) < minimum:
            errors.append(f"{location} must contain at least {minimum} items")
        if isinstance(maximum, int) and len(value) > maximum:
            errors.append(f"{location} must contain at most {maximum} items")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                errors.extend(validate_json_schema(item, item_schema, f"{location}[{index}]"))
    if isinstance(value, dict):
        required = schema.get("required", [])
        if isinstance(required, list):
            for name in required:
                if name not in value:
                    errors.append(f"{location} is missing required property {name!r}")
        properties = schema.get("properties", {})
        if isinstance(properties, dict):
            for name, child_schema in properties.items():
                if name in value and isinstance(child_schema, dict):
                    errors.extend(validate_json_schema(value[name], child_schema, f"{location}.{name}"))
            extras = sorted(set(value) - set(properties))
            additional = schema.get("additionalProperties")
            if additional is False:
                errors.extend(f"{location} has unexpected property {name!r}" for name in extras)
            elif isinstance(additional, dict):
                for name in extras:
                    errors.extend(validate_json_schema(value[name], additional, f"{location}.{name}"))
    return errors
