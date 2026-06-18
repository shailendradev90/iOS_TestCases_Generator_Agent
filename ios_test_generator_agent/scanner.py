"""iOS project scanner - discovers and analyzes iOS project structure."""

from __future__ import annotations

import fnmatch
from pathlib import Path

from .models import AgentConfig, iOSProject


class ProjectScanner:
    """Scans an iOS project directory to discover source files and structure."""

    def __init__(self, config: AgentConfig) -> None:
        self.config = config
        self.project_path = Path(config.project_path).resolve()

    def scan(self) -> iOSProject:
        """Scan the project directory and return an iOSProject model."""
        if not self.project_path.exists():
            raise FileNotFoundError(
                f"Project path does not exist: {self.project_path}"
            )

        project = iOSProject(
            root_path=self.project_path,
            name=self._detect_project_name(),
        )

        # Find Xcode project files
        project.xcodeproj_path = self._find_first("*.xcodeproj")
        project.xcworkspace_path = self._find_first("*.xcworkspace")
        project.package_swift_path = self._find_file("Package.swift")

        # Discover source files
        project.source_files = self._discover_source_files()
        project.test_files = self._discover_existing_tests()

        return project

    def _detect_project_name(self) -> str:
        """Detect the project name from Xcode project or directory."""
        xcodeproj = self._find_first("*.xcodeproj")
        if xcodeproj:
            return xcodeproj.stem

        pkg = self._find_file("Package.swift")
        if pkg:
            # Try to extract name from Package.swift
            try:
                content = pkg.read_text()
                for line in content.splitlines():
                    if "name:" in line and "Package" not in line:
                        # Extract name from: .package(name: "MyApp", ...)
                        parts = line.split('"')
                        if len(parts) >= 2:
                            return parts[1]
            except Exception:
                pass

        return self.project_path.name

    def _find_first(self, pattern: str) -> Path | None:
        """Find first matching file/directory in project."""
        for path in self.project_path.rglob(pattern):
            # Exclude common non-project directories
            if not self._is_excluded(path):
                return path
        return None

    def _find_file(self, filename: str) -> Path | None:
        """Find a specific file in the project root or immediate subdirectories."""
        candidate = self.project_path / filename
        if candidate.exists():
            return candidate
        return None

    def _discover_source_files(self) -> list[Path]:
        """Discover all Swift/Objective-C source files in the project."""
        source_extensions = {".swift", ".m", ".mm"}
        source_files: list[Path] = []

        for ext in source_extensions:
            for path in self.project_path.rglob(f"*{ext}"):
                if not self._is_excluded(path):
                    if self._matches_include_patterns(path):
                        source_files.append(path)

        source_files.sort()
        return source_files

    def _discover_existing_tests(self) -> list[Path]:
        """Discover existing test files."""
        test_files: list[Path] = []
        test_indicators = ["Tests", "Test", "UITests"]

        for path in self.project_path.rglob("*Test*.swift"):
            if any(indicator in str(path) for indicator in test_indicators):
                test_files.append(path)

        test_files.sort()
        return test_files

    def _is_excluded(self, path: Path) -> bool:
        """Check if a path matches any exclude pattern."""
        # Always match against the relative path to avoid false positives
        # from parent directory names
        try:
            rel = str(path.relative_to(self.project_path))
        except ValueError:
            rel = path.name

        for pattern in self.config.exclude_patterns:
            # Match against filename only
            if fnmatch.fnmatch(path.name, pattern):
                return True
            # Match against relative path
            if fnmatch.fnmatch(rel, pattern):
                return True
        return False

    def _matches_include_patterns(self, path: Path) -> bool:
        """Check if a path matches any include pattern."""
        for pattern in self.config.include_patterns:
            if fnmatch.fnmatch(path.name, pattern):
                return True
            if fnmatch.fnmatch(str(path), pattern):
                return True
        return False

    def get_files_to_analyze(self, project: iOSProject) -> list[Path]:
        """Filter project source files to only those targeted for analysis."""
        if self.config.target_files:
            target_set = set(self.config.target_files)
            return [
                f for f in project.source_files
                if f.name in target_set or str(f) in target_set
            ]
        return project.source_files