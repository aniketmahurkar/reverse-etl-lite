"""Field mapping — transforms source columns to destination fields."""
from typing import Any


def apply_mapping(record: dict[str, Any], mapping: dict) -> dict[str, Any]:
    """Apply field mapping to a single record.

    Mapping config format:
        fields:
          source_col: destination_field
          another_col: another_field
        transforms:
          destination_field: "upper"  # optional transforms
        defaults:
          some_field: "default_value"
    """
    fields = mapping.get("fields", {})
    transforms = mapping.get("transforms", {})
    defaults = mapping.get("defaults", {})

    mapped = {}

    # Apply field mapping
    for src, dest in fields.items():
        value = record.get(src)
        if value is not None:
            mapped[dest] = _apply_transform(value, transforms.get(dest))
        elif dest in defaults:
            mapped[dest] = defaults[dest]

    return mapped


def _apply_transform(value: Any, transform: str | None) -> Any:
    """Apply a simple transform to a value."""
    if transform is None or value is None:
        return value
    if transform == "upper":
        return str(value).upper()
    if transform == "lower":
        return str(value).lower()
    if transform == "strip":
        return str(value).strip()
    if transform == "int":
        return int(value)
    if transform == "float":
        return float(value)
    if transform == "bool":
        return bool(value)
    return value
