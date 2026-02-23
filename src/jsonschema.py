from __future__ import annotations

from typing import Any


class ValidationError(Exception):
    pass


def validate(*, instance: Any, schema: dict[str, Any]) -> None:
    _validate_node(instance, schema, path="$")


def _validate_node(value: Any, schema: dict[str, Any], path: str) -> None:
    expected_type = schema.get("type")
    if expected_type is not None:
        _check_type(value, expected_type, path)

    if expected_type == "object":
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        additional = schema.get("additionalProperties", True)

        for key in required:
            if key not in value:
                raise ValidationError(f"{path}: missing required property '{key}'")

        for key, child in value.items():
            if key in properties:
                _validate_node(child, properties[key], f"{path}.{key}")
            elif not additional:
                raise ValidationError(f"{path}: additional property '{key}' not allowed")

    if expected_type == "array":
        item_schema = schema.get("items")
        if item_schema is not None:
            for idx, item in enumerate(value):
                _validate_node(item, item_schema, f"{path}[{idx}]")


def _check_type(value: Any, expected_type: str, path: str) -> None:
    mapping = {
        "object": dict,
        "string": str,
        "number": (int, float),
        "integer": int,
        "boolean": bool,
        "array": list,
        "null": type(None),
    }
    py_type = mapping.get(expected_type)
    if py_type is None:
        return
    if expected_type == "number" and isinstance(value, bool):
        raise ValidationError(f"{path}: expected number, got bool")
    if not isinstance(value, py_type):
        raise ValidationError(f"{path}: expected {expected_type}, got {type(value).__name__}")
