"""iOS Test Generator Agent - Automatically generate XCTest cases for iOS projects."""

__version__ = "1.0.0"
__author__ = "iOS Test Generator Team"
__email__ = "support@ios-test-gen.dev"
__license__ = "MIT"

from .config import AgentConfig, load_config
from .generator import TestGenerator
from .models import TestCase, TestSuite, iOSProject
from .scanner import ProjectScanner

__all__ = [
    "__version__",
    "AgentConfig",
    "load_config",
    "TestGenerator",
    "TestCase",
    "TestSuite",
    "iOSProject",
    "ProjectScanner",
]
