"""LLM-powered test case generator - generates XCTest cases using AI."""

from __future__ import annotations

import json
import os
from pathlib import Path

from .models import (
    AgentConfig,
    SwiftDeclarationKind,
    SwiftFile,
    SwiftType,
    TestCase,
    TestSuite,
)


class LLMClient:
    """Unified LLM client supporting OpenAI, Anthropic, and Groq."""

    def __init__(self, config: AgentConfig) -> None:
        self.config = config
        self._client = None

    def _get_client(self):
        """Lazy-initialize the LLM client."""
        if self._client is not None:
            return self._client

        if self.config.llm_provider == "anthropic":
            import anthropic

            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                raise EnvironmentError(
                    "ANTHROPIC_API_KEY environment variable is required "
                    "when using the Anthropic provider."
                )
            self._client = anthropic.Anthropic(api_key=api_key)
        elif self.config.llm_provider == "groq":
            from groq import Groq

            api_key = os.environ.get("GROQ_API_KEY")
            if not api_key:
                raise EnvironmentError(
                    "GROQ_API_KEY environment variable is required "
                    "when using the Groq provider."
                )
            self._client = Groq(api_key=api_key)
        else:
            import openai

            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise EnvironmentError(
                    "OPENAI_API_KEY environment variable is required "
                    "when using the OpenAI provider."
                )
            self._client = openai.OpenAI(api_key=api_key)

        return self._client

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        """Send a chat request to the LLM."""
        client = self._get_client()

        if self.config.llm_provider == "anthropic":
            response = client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            return response.content[0].text
        elif self.config.llm_provider == "groq":
            # Groq uses OpenAI-compatible API
            response = client.chat.completions.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return response.choices[0].message.content or ""
        else:
            # OpenAI
            response = client.chat.completions.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return response.choices[0].message.content or ""


# System prompt for test generation
SYSTEM_PROMPT = """You are an expert iOS developer specializing in writing comprehensive unit tests.
Your task is to generate high-quality {framework} test cases for Swift code.

Guidelines:
1. Write thorough tests covering happy paths, edge cases, and error conditions.
2. Follow Apple's testing best practices and naming conventions.
3. Use descriptive test method names that explain what is being tested.
4. Include appropriate setup/teardown when needed.
5. Use meaningful assertions (XCTAssertEqual, XCTAssertTrue, XCTAssertThrowsError, etc.).
6. For async functions, use async/await testing patterns.
7. For throwing functions, test both success and failure paths.
8. Create test data that exercises boundary conditions.
9. When testing protocols, create minimal mock implementations.
10. Keep tests independent - each test should work in isolation.
11. Return ONLY valid Swift code, no explanations or markdown.
12. If the code uses protocols, generate mock implementations for dependency injection.
13. For enums, test all cases including associated values.
14. For computed properties, verify the computed logic.
"""


class TestGenerator:
    """Generates XCTest cases using LLM."""

    def __init__(self, config: AgentConfig) -> None:
        self.config = config
        self.llm = LLMClient(config)

    def generate_for_file(self, swift_file: SwiftFile) -> list[TestCase]:
        """Generate test cases for all types in a Swift file."""
        test_cases: list[TestCase] = []

        # Filter types by target if specified
        types_to_test = swift_file.types
        if self.config.target_types:
            types_to_test = [
                t for t in types_to_test
                if t.name in self.config.target_types
            ]

        for swift_type in types_to_test:
            # Skip protocols (they're tested through conforming types)
            if swift_type.kind == SwiftDeclarationKind.PROTOCOL:
                continue

            # Skip private/fileprivate types
            if swift_type.access_control.value in ("private", "fileprivate"):
                continue

            test_case = self._generate_test_case(swift_type, swift_file)
            if test_case:
                test_cases.append(test_case)

        return test_cases

    def _generate_test_case(
        self, swift_type: SwiftType, swift_file: SwiftFile
    ) -> TestCase | None:
        """Generate a test case for a single Swift type."""
        # Build the prompt with code context
        user_prompt = self._build_prompt(swift_type, swift_file)

        try:
            raw_response = self.llm.chat(
                system_prompt=SYSTEM_PROMPT.format(framework=self.config.test_framework),
                user_prompt=user_prompt,
            )
        except Exception as e:
            print(f"  ⚠ LLM error generating tests for {swift_type.name}: {e}")
            return None

        # Parse the response
        test_source = self._clean_response(raw_response)
        test_class_name = f"{swift_type.name}Tests"

        # Extract individual test methods from the response
        test_methods = self._extract_test_methods(test_source)

        # Extract setup/teardown
        setup = self._extract_setup_teardown(test_source, "setUp")
        teardown = self._extract_setup_teardown(test_source, "tearDown")

        # Determine imports needed
        imports = self._determine_imports(swift_file, swift_type)

        return TestCase(
            test_class_name=test_class_name,
            source_type_name=swift_type.name,
            source_file_path=str(swift_file.path),
            imports=imports,
            setup_method=setup,
            teardown_method=teardown,
            test_methods=test_methods,
            raw_source=test_source,
        )

    def _build_prompt(self, swift_type: SwiftType, swift_file: SwiftFile) -> str:
        """Build the LLM prompt for generating tests."""
        parts: list[str] = []

        parts.append("Generate comprehensive unit tests for the following Swift code.\n")
        parts.append(f"File: {swift_file.path.name}\n")

        # Add the type source code
        parts.append("```swift")
        parts.append(swift_type.raw_source)
        parts.append("```\n")

        # Add context about dependencies if available
        related_types = self._find_related_types(swift_type, swift_file)
        if related_types:
            parts.append("\nRelated types used in this code:\n")
            parts.append("```swift")
            for related in related_types:
                parts.append(related.raw_source)
                parts.append("")
            parts.append("```\n")

        # Add specific instructions
        parts.append("\nRequirements:")
        parts.append(f"- Generate a test class named: {swift_type.name}Tests")
        parts.append(f"- Use {self.config.test_framework} framework")

        if self.config.include_setup_teardown:
            parts.append("- Include setUp() and tearDown() methods if appropriate")

        if self.config.generate_mocks:
            parts.append("- Generate mock implementations for any protocols used")

        # List methods to test
        testable_methods = [
            m for m in swift_type.methods
            if m.access_control.value in ("public", "internal", "open")
        ]
        if testable_methods:
            parts.append(f"\nMethods to test ({len(testable_methods)}):")
            for method in testable_methods:
                sig = method.signature()
                parts.append(f"  - {sig}")

        # List properties to test
        testable_props = [
            p for p in swift_type.properties
            if p.access_control.value in ("public", "internal", "open")
        ]
        if testable_props:
            parts.append(f"\nProperties to test ({len(testable_props)}):")
            for prop in testable_props:
                parts.append(f"  - {prop.name}: {prop.type}")

        if swift_type.enum_cases:
            parts.append(f"\nEnum cases to test ({len(swift_type.enum_cases)}):")
            for case in swift_type.enum_cases:
                parts.append(f"  - {case.name}")

        parts.append("\nGenerate ONLY the Swift test code. No markdown fences or explanations.")

        return "\n".join(parts)

    def _find_related_types(
        self, target_type: SwiftType, swift_file: SwiftFile
    ) -> list[SwiftType]:
        """Find types referenced by the target type for context."""
        related: list[SwiftType] = []
        source = target_type.raw_source

        for file_type in swift_file.types:
            if file_type.name == target_type.name:
                continue
            # Check if this type is referenced in the target type's source
            if file_type.name in source:
                related.append(file_type)

        return related

    def _clean_response(self, response: str) -> str:
        """Clean the LLM response to extract pure Swift code."""
        # Remove markdown code fences
        lines = response.split("\n")
        cleaned: list[str] = []
        in_fence = False

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("```swift") or stripped.startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence or (not stripped.startswith("```")):
                cleaned.append(line)

        result = "\n".join(cleaned).strip()

        # If no fences were found, return as-is
        if not result or "import" not in result and "class" not in result:
            # Try to find Swift code directly
            import_idx = response.find("import ")
            if import_idx >= 0:
                return response[import_idx:].strip()
            return response.strip()

        return result

    def _extract_test_methods(self, source: str) -> list[str]:
        """Extract individual test method implementations from generated source."""
        import re

        # Match test method declarations: func testSomething()
        pattern = re.compile(
            r"((?:\s*///[^\n]*\n|\s*//[^\n]*\n)*"  # optional doc comments
            r"\s*func\s+test\w+\s*\([^)]*\)[^{]*\{)"  # method header
            r"(.*?)"  # body
            r"(?=\n\s*func\s+test|\n\s*\}$|\Z)",  # until next test or end
            re.DOTALL,
        )

        methods: list[str] = []
        for match in pattern.finditer(source):
            method = match.group(0).strip()
            if method:
                methods.append(method)

        return methods

    def _extract_setup_teardown(self, source: str, method_name: str) -> str:
        """Extract setUp or tearDown method from generated source."""
        import re

        pattern = re.compile(
            rf"(override\s+func\s+{method_name}\(\)\s*(?:async\s+)?(?:throws\s*)?\{{.*?\n\}})",
            re.DOTALL,
        )
        match = pattern.search(source)
        return match.group(1).strip() if match else ""

    def _determine_imports(
        self, swift_file: SwiftFile, swift_type: SwiftType
    ) -> list[str]:
        """Determine what imports are needed for the test file."""
        imports = ["XCTest"]

        # Add module imports from the source file
        for imp in swift_file.imports:
            if imp not in imports and imp != "Foundation":
                imports.append(imp)

        # Always import Foundation if not already present
        if "Foundation" not in imports:
            imports.insert(1, "Foundation")

        # Check if UIKit is likely needed
        source = swift_type.raw_source
        ui_indicators = ["UIView", "UIViewController", "UILabel", "UIButton",
                         "UITableView", "UICollectionView", "UIImage", "UIColor"]
        if any(indicator in source for indicator in ui_indicators):
            if "UIKit" not in imports:
                imports.append("UIKit")

        # Check for Combine
        combine_indicators = ["PassthroughSubject", "CurrentValueSubject",
                              "AnyCancellable", "Publisher", "@Published"]
        if any(indicator in source for indicator in combine_indicators):
            if "Combine" not in imports:
                imports.append("Combine")

        return imports