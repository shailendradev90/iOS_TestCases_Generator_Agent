"""Swift code parser - extracts types, methods, properties, and structure from Swift files."""

from __future__ import annotations

import re
from pathlib import Path

from .models import (
    MethodKind,
    SwiftAccessControl,
    SwiftDeclarationKind,
    SwiftEnumCase,
    SwiftFile,
    SwiftMethod,
    SwiftParameter,
    SwiftProperty,
    SwiftType,
)

# Regex patterns for Swift declarations
_ACCESS_MODIFIERS = r"(?:open|public|internal|fileprivate|private)"
_STATIC_MODIFIERS = r"(?:static|class)"
_SWIFT_TYPE_KEYWORDS = r"(?:class|struct|enum|protocol|extension)"

# Matches: [access] [static] class/struct/enum/protocol/extension Name [: SuperClass, Protocol1, ...] {
_TYPE_DECL_PATTERN = re.compile(
    rf"^\s*({_ACCESS_MODIFIERS}\s+)?({_STATIC_MODIFIERS}\s+)?({_SWIFT_TYPE_KEYWORDS})\s+"
    rf"(\w+)"
    rf"(?:\s*:\s*([^\{{]+))?"
    rf"\s*\{{",
    re.MULTILINE,
)

# Matches: [access] [static] func name(params) [async] [throws] [-> ReturnType]
_FUNC_PATTERN = re.compile(
    rf"^\s*({_ACCESS_MODIFIERS}\s+)?(static\s+|class\s+)?"
    rf"func\s+(\w+)\s*\(([^)]*)\)"
    rf"(\s+async)?(\s+throws)?"
    rf"(?:\s*->\s*([^\{{]+))?",
    re.MULTILINE,
)

# Matches: [access] [static] var/let name: Type [= value]
_PROPERTY_PATTERN = re.compile(
    rf"^\s*({_ACCESS_MODIFIERS}\s+)?(static\s+|class\s+)?"
    rf"(var|let)\s+(\w+)\s*:\s*([^\s=]+)"
    rf"(?:\s*=\s*(.+))?",
    re.MULTILINE,
)

# Matches computed properties: var name: Type { get ... }
_COMPUTED_PROPERTY_PATTERN = re.compile(
    rf"^\s*({_ACCESS_MODIFIERS}\s+)?(static\s+|class\s+)?"
    rf"var\s+(\w+)\s*:\s*([^\{{\n]+)\s*\{{\s*get",
    re.MULTILINE,
)

# Matches: [access] init(params)
_INIT_PATTERN = re.compile(
    rf"^\s*({_ACCESS_MODIFIERS}\s+)?init\s*\(([^)]*)\)"
    rf"(\s+async)?(\s+throws)?",
    re.MULTILINE,
)

# Matches: import ModuleName
_IMPORT_PATTERN = re.compile(r"^\s*import\s+(\w+(?:\.\w+)*)", re.MULTILINE)

# Matches enum case: case name [= value] or case name(associated)
_ENUM_CASE_PATTERN = re.compile(
    r"^\s*case\s+(\w+)(?:\s*=\s*(.+?))?(?:\s*\(([^)]*)\))?\s*$",
    re.MULTILINE,
)

# Pattern to match parameter: [label] name: Type [,]
_PARAM_PATTERN = re.compile(
    r"(\w+\s+)?(\w+)\s*:\s*([^,=]+?)(?:\s*=\s*([^,]+))?"
    r"(?:\s*,\s*|$)"
)

# Property wrapper pattern
_PROPERTY_WRAPPER_PATTERN = re.compile(r"^\s*@\w+(?:\([^)]*\))?\s*$", re.MULTILINE)


class SwiftParser:
    """Parses Swift source files and extracts code structure."""

    def __init__(self, target_types: list[str] | None = None) -> None:
        """Initialize parser with optional type filtering.

        Args:
            target_types: If provided, only extract these specific type names.
        """
        self.target_types = set(target_types) if target_types else None

    def parse_file(self, file_path: Path) -> SwiftFile:
        """Parse a single Swift file and return its structure."""
        try:
            source = file_path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            return SwiftFile(path=file_path, raw_source="", imports=[])

        swift_file = SwiftFile(
            path=file_path,
            imports=self._extract_imports(source),
            raw_source=source,
        )

        # Extract top-level types
        swift_file.types = self._extract_types(source)

        # Extract top-level functions
        swift_file.top_level_functions = self._extract_top_level_functions(source)

        return swift_file

    def _extract_imports(self, source: str) -> list[str]:
        """Extract import statements from source."""
        return _IMPORT_PATTERN.findall(source)

    def _extract_types(self, source: str) -> list[SwiftType]:
        """Extract all type declarations from source."""
        types: list[SwiftType] = []
        source.split("\n")

        for match in _TYPE_DECL_PATTERN.finditer(source):
            access_str = (match.group(1) or "").strip()
            (match.group(2) or "").strip()
            kind_str = match.group(3).strip()
            name = match.group(4).strip()
            inheritance_str = (match.group(5) or "").strip()

            # Filter by target types if specified
            if self.target_types and name not in self.target_types:
                continue

            kind = SwiftDeclarationKind(kind_str)
            access = (
                SwiftAccessControl(access_str)
                if access_str
                else SwiftAccessControl.INTERNAL
            )

            # Parse inheritance
            superclasses, conformances = self._parse_inheritance(
                inheritance_str, kind
            )

            # Find the body of this type
            body_start = match.end()
            body, body_end = self._extract_brace_block(source, body_start - 1)

            start_line = source[:match.start()].count("\n") + 1
            end_line = source[:body_end].count("\n") + 1

            # Parse members from body
            properties = self._extract_properties(body)
            methods = self._extract_methods(body)
            enum_cases = self._extract_enum_cases(body) if kind == SwiftDeclarationKind.ENUM else []
            nested_types = self._extract_types(body)

            swift_type = SwiftType(
                name=name,
                kind=kind,
                access_control=access,
                superclasses=superclasses,
                conformances=conformances,
                properties=properties,
                methods=methods,
                enum_cases=enum_cases,
                nested_types=nested_types,
                raw_source=source[match.start():body_end],
                start_line=start_line,
                end_line=end_line,
            )
            types.append(swift_type)

        return types

    def _parse_inheritance(
        self, inheritance_str: str, kind: SwiftDeclarationKind
    ) -> tuple[list[str], list[str]]:
        """Parse inheritance string into superclasses and conformances."""
        if not inheritance_str:
            return [], []

        items = [item.strip() for item in inheritance_str.split(",") if item.strip()]

        superclasses: list[str] = []
        conformances: list[str] = []

        for item in items:
            # Remove generic constraints etc.
            clean_item = item.split(":")[0].split("where")[0].strip()
            if not clean_item:
                continue

            if kind == SwiftDeclarationKind.CLASS and self._is_likely_class(clean_item):
                superclasses.append(clean_item)
            else:
                conformances.append(clean_item)

        return superclasses, conformances

    def _is_likely_class(self, name: str) -> bool:
        """Heuristic to determine if an inherited type is likely a class."""
        # Common class suffixes/prefixes
        class_indicators = [
            "Controller", "ViewController", "View", "Manager",
            "Service", "ViewModel", "Presenter", "Interactor",
            "Router", "Coordinator", "Cell", "Collection",
            "NSObject", "UIView", "UIViewController", "UITableViewCell",
            "UICollectionViewCell", "UIButton", "UILabel",
        ]
        return any(indicator in name for indicator in class_indicators)

    def _extract_brace_block(
        self, source: str, start_brace_pos: int
    ) -> tuple[str, int]:
        """Extract content between matching braces."""
        if start_brace_pos >= len(source) or source[start_brace_pos] != "{":
            return "", start_brace_pos

        depth = 0
        i = start_brace_pos
        in_string = False
        in_line_comment = False
        in_block_comment = False
        escape_next = False

        while i < len(source):
            char = source[i]

            if escape_next:
                escape_next = False
                i += 1
                continue

            if in_line_comment:
                if char == "\n":
                    in_line_comment = False
                i += 1
                continue

            if in_block_comment:
                if char == "*" and i + 1 < len(source) and source[i + 1] == "/":
                    in_block_comment = False
                    i += 2
                    continue
                i += 1
                continue

            if in_string:
                if char == "\\":
                    escape_next = True
                elif char == '"':
                    in_string = False
                i += 1
                continue

            # Check for comments
            if char == "/" and i + 1 < len(source):
                if source[i + 1] == "/":
                    in_line_comment = True
                    i += 2
                    continue
                elif source[i + 1] == "*":
                    in_block_comment = True
                    i += 2
                    continue

            if char == '"':
                in_string = True
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return source[start_brace_pos + 1 : i], i + 1

            i += 1

        # If we reach here, braces are unbalanced
        return source[start_brace_pos + 1 :], len(source)

    def _extract_properties(self, body: str) -> list[SwiftProperty]:
        """Extract property declarations from a type body."""
        properties: list[SwiftProperty] = []

        # First, find computed properties to exclude them from regular parsing
        computed_names = set()
        for match in _COMPUTED_PROPERTY_PATTERN.finditer(body):
            computed_names.add(match.group(3))

        for match in _PROPERTY_PATTERN.finditer(body):
            access_str = (match.group(1) or "").strip()
            static_str = (match.group(2) or "").strip()
            let_or_var = match.group(3).strip()
            name = match.group(4).strip()
            type_str = match.group(5).strip()
            default_value = (match.group(6) or "").strip() or None

            # Skip if it's actually a computed property
            if name in computed_names:
                properties.append(
                    SwiftProperty(
                        name=name,
                        type=type_str.rstrip(),
                        access_control=self._parse_access(access_str),
                        is_let=(let_or_var == "let"),
                        is_static=bool(static_str),
                        is_computed=True,
                    )
                )
                continue

            # Skip local variables (inside function bodies) - heuristic:
            # Properties are typically at the start of lines with consistent indentation
            properties.append(
                SwiftProperty(
                    name=name,
                    type=type_str.rstrip(),
                    access_control=self._parse_access(access_str),
                    is_let=(let_or_var == "let"),
                    is_static=bool(static_str),
                    default_value=default_value,
                )
            )

        return properties

    def _extract_methods(self, body: str) -> list[SwiftMethod]:
        """Extract method declarations from a type body."""
        methods: list[SwiftMethod] = []

        # Extract regular functions
        for match in _FUNC_PATTERN.finditer(body):
            access_str = (match.group(1) or "").strip()
            static_str = (match.group(2) or "").strip()
            name = match.group(3).strip()
            params_str = match.group(4).strip()
            is_async = bool(match.group(5))
            is_throwing = bool(match.group(6))
            return_type = (match.group(7) or "").strip() or None

            kind = MethodKind.INSTANCE
            if static_str == "static":
                kind = MethodKind.STATIC
            elif static_str == "class":
                kind = MethodKind.CLASS

            parameters = self._parse_parameters(params_str)

            # Extract method body
            body_start = match.end()
            method_body = ""
            if body_start < len(body):
                # Look for opening brace
                brace_search = body[body_start:].lstrip()
                if brace_search.startswith("{"):
                    actual_pos = body_start + (len(body[body_start:]) - len(brace_search))
                    method_body, _ = self._extract_brace_block(body, actual_pos)

            methods.append(
                SwiftMethod(
                    name=name,
                    return_type=return_type,
                    parameters=parameters,
                    access_control=self._parse_access(access_str),
                    kind=kind,
                    is_async=is_async,
                    is_throwing=is_throwing,
                    body=method_body,
                    raw_source=body[match.start():body_start],
                )
            )

        # Extract initializers
        for match in _INIT_PATTERN.finditer(body):
            access_str = (match.group(1) or "").strip()
            params_str = (match.group(2) or "").strip()
            is_async = bool(match.group(3))
            is_throwing = bool(match.group(4))

            parameters = self._parse_parameters(params_str)

            # Extract init body
            body_start = match.end()
            init_body = ""
            if body_start < len(body):
                brace_search = body[body_start:].lstrip()
                if brace_search.startswith("{"):
                    actual_pos = body_start + (len(body[body_start:]) - len(brace_search))
                    init_body, _ = self._extract_brace_block(body, actual_pos)

            methods.append(
                SwiftMethod(
                    name="init",
                    return_type=None,
                    parameters=parameters,
                    access_control=self._parse_access(access_str),
                    kind=MethodKind.INIT,
                    is_async=is_async,
                    is_throwing=is_throwing,
                    body=init_body,
                    raw_source=body[match.start():body_start],
                )
            )

        return methods

    def _extract_top_level_functions(self, source: str) -> list[SwiftMethod]:
        """Extract top-level functions (not inside any type)."""
        # Simple heuristic: functions at indentation level 0
        functions: list[SwiftMethod] = []

        for match in _FUNC_PATTERN.finditer(source):
            # Check that this function is at the top level (not inside a type)
            line_start = source.rfind("\n", 0, match.start()) + 1
            line_end = source.find("\n", match.start())
            if line_end == -1:
                line_end = len(source)
            line = source[line_start:line_end]

            # If the line is indented, it's inside a type body
            indent = len(line) - len(line.lstrip())
            if indent > 0:
                continue

            access_str = (match.group(1) or "").strip()
            (match.group(2) or "").strip()
            name = match.group(3).strip()
            params_str = match.group(4).strip()
            is_async = bool(match.group(5))
            is_throwing = bool(match.group(6))
            return_type = (match.group(7) or "").strip() or None

            parameters = self._parse_parameters(params_str)

            functions.append(
                SwiftMethod(
                    name=name,
                    return_type=return_type,
                    parameters=parameters,
                    access_control=self._parse_access(access_str),
                    kind=MethodKind.INSTANCE,
                    is_async=is_async,
                    is_throwing=is_throwing,
                )
            )

        return functions

    def _extract_enum_cases(self, body: str) -> list[SwiftEnumCase]:
        """Extract enum cases from an enum body."""
        cases: list[SwiftEnumCase] = []

        for match in _ENUM_CASE_PATTERN.finditer(body):
            name = match.group(1).strip()
            raw_value = (match.group(2) or "").strip() or None
            associated_str = (match.group(3) or "").strip()

            associated_values: list[SwiftParameter] = []
            if associated_str:
                associated_values = self._parse_parameters(associated_str)

            cases.append(
                SwiftEnumCase(
                    name=name,
                    raw_value=raw_value,
                    associated_values=associated_values,
                )
            )

        return cases

    def _parse_parameters(self, params_str: str) -> list[SwiftParameter]:
        """Parse a parameter list string into SwiftParameter objects."""
        if not params_str.strip():
            return []

        parameters: list[SwiftParameter] = []
        # Split by comma, being careful about nested types (e.g. [String: Int])
        parts = self._smart_split(params_str, ",")

        for part in parts:
            part = part.strip()
            if not part:
                continue

            param = self._parse_single_parameter(part)
            if param:
                parameters.append(param)

        return parameters

    def _parse_single_parameter(self, param_str: str) -> SwiftParameter | None:
        """Parse a single parameter string."""
        param_str = param_str.strip()

        # Handle _ (wildcard) external label
        # e.g., "_ name: String"
        if param_str.startswith("_ "):
            param_str = param_str[2:].strip()
            # Parse: name: Type
            match = re.match(r"(\w+)\s*:\s*(.+?)(?:\s*=\s*(.+))?$", param_str)
            if match:
                return SwiftParameter(
                    label="_",
                    name=match.group(1).strip(),
                    type=match.group(2).strip(),
                    default_value=(match.group(3) or "").strip() or None,
                    is_optional=match.group(2).strip().endswith("?"),
                )

        # Match: [label ]name: Type [= default]
        match = re.match(
            r"(\w+)\s+(\w+)\s*:\s*(.+?)(?:\s*=\s*(.+))?$", param_str
        )
        if match:
            return SwiftParameter(
                label=match.group(1).strip(),
                name=match.group(2).strip(),
                type=match.group(3).strip(),
                default_value=(match.group(4) or "").strip() or None,
                is_optional=match.group(3).strip().endswith("?"),
            )

        # Match: name: Type [= default]
        match = re.match(
            r"(\w+)\s*:\s*(.+?)(?:\s*=\s*(.+))?$", param_str
        )
        if match:
            return SwiftParameter(
                label=match.group(1).strip(),
                name=match.group(1).strip(),
                type=match.group(2).strip(),
                default_value=(match.group(3) or "").strip() or None,
                is_optional=match.group(2).strip().endswith("?"),
            )

        return None

    def _smart_split(self, text: str, delimiter: str) -> list[str]:
        """Split text by delimiter, respecting nested brackets and generics."""
        parts: list[str] = []
        current: list[str] = []
        depth = 0
        in_string = False

        for char in text:
            if in_string:
                current.append(char)
                if char == '"':
                    in_string = False
                continue

            if char == '"':
                in_string = True
                current.append(char)
                continue

            if char in ("(", "[", "<"):
                depth += 1
            elif char in (")", "]", ">"):
                depth -= 1

            if char == delimiter and depth == 0:
                parts.append("".join(current))
                current = []
            else:
                current.append(char)

        if current:
            parts.append("".join(current))

        return parts

    def _parse_access(self, access_str: str) -> SwiftAccessControl:
        """Parse access control string."""
        access_str = access_str.strip()
        if not access_str:
            return SwiftAccessControl.INTERNAL
        try:
            return SwiftAccessControl(access_str)
        except ValueError:
            return SwiftAccessControl.INTERNAL
