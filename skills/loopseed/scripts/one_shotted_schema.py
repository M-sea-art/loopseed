"""Small dependency-free validator for the JSON Schema subset used by LoopSeed."""

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
    """Validate the schema keywords used by LoopSeed's committed contracts."""

    errors: list[str] = []
    declared = schema.get("type")
    allowed_types = declared if isinstance(declared, list) else [declared] if declared else []
    if allowed_types and not any(_matches_type(value, str(item)) for item in allowed_types):
        errors.append(f"{location} must have type {' or '.join(str(item) for item in allowed_types)}")
        return errors

    if "const" in schema and value != schema["const"]:
        errors.append(f"{location} must equal {schema['const']!r}")

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
        additional = schema.get("additionalProperties")
        if isinstance(properties, dict):
            extra_names = sorted(set(value) - set(properties))
        else:
            extra_names = sorted(value)
        if additional is False:
            for name in extra_names:
                errors.append(f"{location} contains unsupported property {name!r}")
        elif isinstance(additional, dict):
            for name in extra_names:
                errors.extend(
                    validate_json_schema(value[name], additional, f"{location}.{name}")
                )

    return errors
