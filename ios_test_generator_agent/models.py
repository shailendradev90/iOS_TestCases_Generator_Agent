"""Data models for iOS project analysis and test generation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class SwiftAccessControl(Enum):
    """Swift access control levels."""

    OPEN = "open"
    PUBLIC = "public"
    INTERNAL = "internal"
    FILEPRIVATE = "fileprivate"
    PRIVATE = "private"


class SwiftDeclarationKind(Enum):
    """Types of Swift declarations."""

    CLASS = "class"
    STRUCT = "struct"
    ENUM = "enum"
    PROTOCOL = "protocol"
    EXTENSION = "extension"


class MethodKind(Enum):
    """Types of methods."""

    INSTANCE = "instance"
    STATIC = "static"
    CLASS = "class"
    INIT = "init"
    DEINIT = "deinit"


@dataclass
class SwiftParameter:
    """Represents a function/method parameter."""

    label: str  # external label
    name: str  # internal name
    type: str
    default_value: str | None = None
    is_optional: bool = False

    def to_signature(self) -> str:
        """Return the parameter as it appears in a function signature."""
        if self.label == self.name:
            result = f"{self.name}: {self.type}"
        else:
            result = f"{self.label} {self.name}: {self.type}"
        if self.default_value:
            result += f" = {self.default_value}"
        return result


@dataclass
class SwiftProperty:
    """Represents a property in a Swift type."""

    name: str
    type: str
    access_control: SwiftAccessControl = SwiftAccessControl.INTERNAL
    is_let: bool = False
    is_static: bool = False
    is_computed: bool = False
    default_value: str | None = None


@dataclass
class SwiftMethod:
    """Represents a method/function in a Swift type."""

    name: str
    return_type: str | None = None
    parameters: list[SwiftParameter] = field(default_factory=list)
    access_control: SwiftAccessControl = SwiftAccessControl.INTERNAL
    kind: MethodKind = MethodKind.INSTANCE
    is_async: bool = False
    is_throwing: bool = False
    body: str = ""
    raw_source: str = ""

    def signature(self) -> str:
        """Return the full method signature."""
        params = ", ".join(p.to_signature() for p in self.parameters)
        parts = ["func ", self.name, "(", params, ")"]
        if self.is_async:
            parts.append(" async")
        if self.is_throwing:
            parts.append(" throws")
        if self.return_type:
            parts.append(f" -> {self.return_type}")
        return "".join(parts)


@dataclass
class SwiftEnumCase:
    """Represents a case in a Swift enum."""

    name: str
    raw_value: str | None = None
    associated_values: list[SwiftParameter] = field(default_factory=list)


@dataclass
class SwiftType:
    """Represents a Swift type (class, struct, enum, protocol, extension)."""

    name: str
    kind: SwiftDeclarationKind
    access_control: SwiftAccessControl = SwiftAccessControl.INTERNAL
    superclasses: list[str] = field(default_factory=list)
    conformances: list[str] = field(default_factory=list)
    properties: list[SwiftProperty] = field(default_factory=list)
    methods: list[SwiftMethod] = field(default_factory=list)
    enum_cases: list[SwiftEnumCase] = field(default_factory=list)
    nested_types: list[SwiftType] = field(default_factory=list)
    raw_source: str = ""
    start_line: int = 0
    end_line: int = 0


@dataclass
class SwiftFile:
    """Represents a parsed Swift source file."""

    path: Path
    imports: list[str] = field(default_factory=list)
    types: list[SwiftType] = field(default_factory=list)
    top_level_functions: list[SwiftMethod] = field(default_factory=list)
    raw_source: str = ""


@dataclass
class iOSProject:
    """Represents an iOS project structure."""

    root_path: Path
    name: str = ""
    source_files: list[Path] = field(default_factory=list)
    test_files: list[Path] = field(default_factory=list)
    xcodeproj_path: Path | None = None
    xcworkspace_path: Path | None = None
    package_swift_path: Path | None = None
    parsed_files: list[SwiftFile] = field(default_factory=list)


@dataclass
class TestCase:
    """Represents a generated test case."""

    test_class_name: str
    source_type_name: str
    source_file_path: str
    imports: list[str] = field(default_factory=list)
    setup_method: str = ""
    teardown_method: str = ""
    test_methods: list[str] = field(default_factory=list)
    raw_source: str = ""


@dataclass
class TestSuite:
    """Represents a collection of generated test cases for a project."""

    project_name: str
    test_cases: list[TestCase] = field(default_factory=list)
    output_directory: Path | None = None


@dataclass
class AgentConfig:
    """Configuration for the test generator agent."""

    # LLM settings
    llm_provider: str = "groq"  # "openai", "anthropic", or "groq"
    model: str = "openai/gpt-oss-120b"  # "gpt-4o"
    temperature: float = 0.2
    max_tokens: int = 4096

    # Project settings
    project_path: str = ""
    output_path: str = ""
    test_target_name: str = ""

    # Generation settings
    test_framework: str = "XCTest"  # "XCTest" or "SwiftTesting"
    include_setup_teardown: bool = True
    generate_mocks: bool = True
    mock_framework: str = "manual"  # "manual", "swift-mock", "mockingbird"

    # File filtering
    include_patterns: list[str] = field(default_factory=lambda: ["*.swift"])
    exclude_patterns: list[str] = field(
        default_factory=lambda: [
            "*Tests*",
            "*Test*",
            "*/Pods/*",
            "*/Carthage/*",
            "*/.build/*",
            "*/DerivedData/*",
        ]
    )

    # Scope
    target_files: list[str] = field(default_factory=list)  # specific files to test
    target_types: list[str] = field(default_factory=list)  # specific types to test
