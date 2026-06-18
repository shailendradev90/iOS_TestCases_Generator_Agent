# 🧪 iOS Test Generator Agent

An AI-powered agent that automatically analyzes iOS/Swift projects and generates comprehensive XCTest unit test cases. Works with any iOS project — just point it at a codebase and it handles the rest.

## Features

- **Multi-project support** — works with any iOS project structure (Xcode projects, Swift Packages)
- **Intelligent code parsing** — extracts classes, structs, enums, protocols, methods, and properties from Swift files
- **AI-powered test generation** — uses LLMs (OpenAI GPT-4o, Anthropic Claude, or Groq) to generate high-quality test cases
- **Multiple LLM providers** — OpenAI, Anthropic, and Groq (ultra-fast & affordable)
- **Comprehensive coverage** — generates tests for happy paths, edge cases, error conditions, and async/throwing functions
- **Smart mock generation** — automatically creates mock implementations for protocols
- **Flexible configuration** — YAML config files, environment variables, and CLI options
- **XCTest & Swift Testing** — supports both testing frameworks
- **Selective generation** — target specific files or types for test generation

## Installation

### Prerequisites

- Python 3.13+
- An API key for OpenAI, Anthropic, or Groq

### Install

```bash
# Clone the repository
git clone <your-repo-url>
cd ios-test-generator-agent

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install in development mode
pip install -e .
```

### Set up API Key

```bash
# For OpenAI (default)
export OPENAI_API_KEY="sk-..."

# For Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."

# For Groq (fastest & most affordable)
export GROQ_API_KEY="gsk_..."
```

## Quick Start

### Generate tests for a project

```bash
# Generate tests for an iOS project (uses OpenAI GPT-4o by default)
ios-test-gen generate /path/to/your/ios-project

# Use Anthropic Claude
ios-test-gen generate /path/to/project --provider anthropic --model claude-sonnet-4-20250514

# Use Groq (fastest & most affordable)
ios-test-gen generate /path/to/project --provider groq --model llama-3.1-70b-versatile

# Generate with a specific model
ios-test-gen generate /path/to/project --model gpt-4o-mini

# Generate tests to a specific output directory
ios-test-gen generate /path/to/project -o /path/to/output

# Dry run (analyze without generating)
ios-test-gen generate /path/to/project --dry-run --verbose
```

### Analyze a project (no generation)

```bash
ios-test-gen analyze /path/to/your/ios-project --verbose
```

### Initialize configuration

```bash
ios-test-gen init /path/to/your/ios-project
```

## Usage

### Commands

| Command | Description |
|---------|-------------|
| `generate` | Analyze project and generate test cases |
| `analyze` | Analyze project structure without generating tests |
| `init` | Create a default configuration file |

### Generate Command Options

```bash
ios-test-gen generate [PROJECT_PATH] [OPTIONS]

Options:
  -o, --output PATH           Output directory for generated tests
  --provider [openai|anthropic|groq]  LLM provider
  --model TEXT                LLM model name (e.g., gpt-4o, claude-sonnet-4, llama-3.1-70b-versatile)
  --framework [XCTest|SwiftTesting]  Test framework
  --files TEXT                Specific files to generate tests for (repeatable)
  --types TEXT                Specific types to generate tests for (repeatable)
  --no-mocks                  Disable mock generation
  --no-setup                  Skip setUp/tearDown generation
  --dry-run                   Analyze without generating
  -v, --verbose               Verbose output
```

### Examples

```bash
# Generate tests for specific files only
ios-test-gen generate ./MyProject --files NetworkManager.swift --files UserService.swift

# Generate tests for specific types
ios-test-gen generate ./MyProject --types NetworkManager --types UserRepository

# Use Groq for ultra-fast generation
ios-test-gen generate ./MyProject --provider groq --model llama-3.1-70b-versatile

# Generate with Swift Testing framework
ios-test-gen generate ./MyProject --framework SwiftTesting

# Combine options
ios-test-gen generate ./MyProject --provider anthropic --model claude-sonnet-4-20250514 --no-mocks -o ./CustomTests
```

## Configuration

Create an `ios-test-gen.yml` file in your project root:

```yaml
# LLM Settings
llm_provider: openai          # "openai", "anthropic", or "groq"
model: gpt-4o                 # Model name (gpt-4o, claude-sonnet-4, llama-3.1-70b-versatile)
temperature: 0.2              # Lower = more deterministic
max_tokens: 4096              # Max response tokens

# Test Generation Settings
test_framework: XCTest        # "XCTest" or "SwiftTesting"
include_setup_teardown: true  # Generate setUp/tearDown
generate_mocks: true          # Generate mock implementations
mock_framework: manual        # "manual", "swift-mock", "mockingbird"

# File Filtering
include_patterns:
  - "*.swift"

exclude_patterns:
  - "*Tests*"
  - "*Test*"
  - "*/Pods/*"
  - "*/Carthage/*"
  - "*/.build/*"
  - "*/DerivedData/*"
```

### Environment Variables

All configuration options can be set via environment variables:

| Variable | Description |
|----------|-------------|
| `IOS_TEST_GEN_LLM_PROVIDER` | LLM provider (`openai`, `anthropic`, or `groq`) |
| `IOS_TEST_GEN_MODEL` | Model name |
| `IOS_TEST_GEN_TEMPERATURE` | Temperature |
| `IOS_TEST_GEN_MAX_TOKENS` | Max tokens |
| `IOS_TEST_GEN_TEST_FRAMEWORK` | Test framework |
| `IOS_TEST_GEN_GENERATE_MOCKS` | Generate mocks (`true`/`false`) |
| `IOS_TEST_GEN_OUTPUT_PATH` | Output directory |
| `OPENAI_API_KEY` | OpenAI API key |
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `GROQ_API_KEY` | Groq API key |

### Configuration Priority

1. CLI arguments (highest)
2. Environment variables
3. Config file (`ios-test-gen.yml`)
4. Defaults (lowest)

## Project Structure

```
ios_test_generator_agent/
├── __init__.py        # Package init
├── cli.py             # CLI interface (Click + Rich)
├── config.py          # Configuration management
├── models.py          # Data models (types, methods, properties, tests)
├── scanner.py         # iOS project scanner
├── parser.py          # Swift code parser
├── generator.py       # LLM-powered test generator
├── writer.py          # Test file writer
└── utils.py           # Utility functions
```

## How It Works

1. **Scan** — Discovers the iOS project structure, finds `.xcodeproj`, `Package.swift`, and source files
2. **Parse** — Parses Swift files using regex-based parsing to extract types, methods, properties, and relationships
3. **Generate** — Sends parsed code context to an LLM with a carefully crafted prompt to generate XCTest cases
4. **Write** — Formats and writes the generated test files to the output directory

## Supported Swift Features

- ✅ Classes, Structs, Enums, Protocols, Extensions
- ✅ Access control (open, public, internal, fileprivate, private)
- ✅ Instance, static, and class methods
- ✅ Initializers (init)
- ✅ Computed and stored properties
- ✅ Enum cases with raw values and associated values
- ✅ Async/await functions
- ✅ Throwing functions
- ✅ Nested types
- ✅ Protocol conformances and inheritance
- ✅ Import detection (UIKit, Combine, etc.)

## Example Output

Given this input:

```swift
class UserManager {
    private let networkService: NetworkService
    private(set) var currentUser: User?

    init(networkService: NetworkService) {
        self.networkService = networkService
    }

    func fetchUser(id: String) async throws -> User {
        let user = try await networkService.get("/users/\(id)")
        currentUser = user
        return user
    }
}
```

The agent generates:

```swift
import XCTest
import Foundation
@testable import YourModule

class UserManagerTests: XCTestCase {

    // MARK: - Properties
    var sut: UserManager!
    var mockNetworkService: MockNetworkService!

    // MARK: - Setup & Teardown
    override func setUp() {
        super.setUp()
        mockNetworkService = MockNetworkService()
        sut = UserManager(networkService: mockNetworkService)
    }

    override func tearDown() {
        sut = nil
        mockNetworkService = nil
        super.tearDown()
    }

    // MARK: - Tests
    func test_fetchUser_returnsUser() async throws {
        // Given
        let expectedUser = User(id: "123", name: "Test")
        mockNetworkService.mockResult = expectedUser

        // When
        let user = try await sut.fetchUser(id: "123")

        // Then
        XCTAssertEqual(user.id, expectedUser.id)
        XCTAssertEqual(sut.currentUser?.id, expectedUser.id)
    }

    func test_fetchUser_throwsOnNetworkError() async {
        // Given
        mockNetworkService.mockError = NetworkError.connectionFailed

        // When / Then
        do {
            _ = try await sut.fetchUser(id: "123")
            XCTFail("Expected error to be thrown")
        } catch {
            XCTAssertNotNil(error)
            XCTAssertNil(sut.currentUser)
        }
    }
}
```

## License

MIT