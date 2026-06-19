"""Utility functions for the iOS Test Generator Agent."""

from __future__ import annotations

from .models import SwiftFile, SwiftType


def format_type_summary(swift_type: SwiftType, indent: int = 0) -> str:
    """Format a human-readable summary of a Swift type."""
    prefix = "  " * indent
    kind = swift_type.kind.value
    lines: list[str] = []

    inheritance = ""
    if swift_type.superclasses:
        inheritance += ": " + ", ".join(swift_type.superclasses)
    if swift_type.conformances:
        sep = ", " if swift_type.superclasses else ": "
        inheritance += sep + ", ".join(swift_type.conformances)

    lines.append(f"{prefix}{kind} {swift_type.name}{inheritance}")

    # Properties
    for prop in swift_type.properties:
        let_or_var = "let" if prop.is_let else "var"
        static = "static " if prop.is_static else ""
        computed = " { get }" if prop.is_computed else ""
        default = f" = {prop.default_value}" if prop.default_value else ""
        lines.append(f"{prefix}  {static}{let_or_var} {prop.name}: {prop.type}{computed}{default}")

    # Enum cases
    for case in swift_type.enum_cases:
        raw = f" = {case.raw_value}" if case.raw_value else ""
        assoc = ""
        if case.associated_values:
            params = ", ".join(f"{p.name}: {p.type}" for p in case.associated_values)
            assoc = f"({params})"
        lines.append(f"{prefix}  case {case.name}{assoc}{raw}")

    # Methods
    for method in swift_type.methods:
        static = "static " if method.kind.value == "static" else ""
        class_m = "class " if method.kind.value == "class" else ""
        async_m = "async " if method.is_async else ""
        throw_m = "throws " if method.is_throwing else ""
        ret = f" -> {method.return_type}" if method.return_type else ""

        if method.kind.value == "init":
            params = ", ".join(p.to_signature() for p in method.parameters)
            lines.append(f"{prefix}  init({params}){async_m}{throw_m}".rstrip())
        else:
            params = ", ".join(p.to_signature() for p in method.parameters)
            lines.append(
                f"{prefix}  {static}{class_m}func {method.name}({params}) "
                f"{async_m}{throw_m}{ret}".rstrip()
            )

    # Nested types
    for nested in swift_type.nested_types:
        lines.append(format_type_summary(nested, indent + 1))

    return "\n".join(lines)


def format_file_summary(swift_file: SwiftFile) -> str:
    """Format a human-readable summary of a parsed Swift file."""
    lines: list[str] = []

    rel_path = swift_file.path.name
    lines.append(f"📄 {rel_path}")

    if swift_file.imports:
        lines.append(f"  Imports: {', '.join(swift_file.imports)}")

    for swift_type in swift_file.types:
        lines.append(format_type_summary(swift_type, indent=1))

    if swift_file.top_level_functions:
        lines.append("  Top-level functions:")
        for func in swift_file.top_level_functions:
            params = ", ".join(p.to_signature() for p in func.parameters)
            ret = f" -> {func.return_type}" if func.return_type else ""
            lines.append(f"    func {func.name}({params}){ret}")

    return "\n".join(lines)


def count_testable_elements(swift_type: SwiftType) -> dict[str, int]:
    """Count the testable elements in a Swift type."""
    return {
        "methods": len(
            [
                m
                for m in swift_type.methods
                if m.access_control.value in ("public", "internal", "open")
            ]
        ),
        "properties": len(
            [
                p
                for p in swift_type.properties
                if p.access_control.value in ("public", "internal", "open")
            ]
        ),
        "enum_cases": len(swift_type.enum_cases),
    }
