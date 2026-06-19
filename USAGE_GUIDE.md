# 🚀 How to Use iOS Test Generator Agent in Your iOS Project

## Step-by-Step Guide

### Prerequisites

Before you start, ensure you have:
- ✅ Python 3.13 or higher installed
- ✅ An iOS project (Xcode project or Swift Package)
- ✅ OpenAI API key OR Anthropic API key

---

## 📦 Step 1: Install the Tool

### Option A: Install from this directory

```bash
# Navigate to the ios_Test_Generator_Agent directory
cd /path/to/ios_Test_Generator_Agent

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Install the package
pip install -e .
```

### Option B: Verify Installation

```bash
# Check if the tool is installed
ios-test-gen --version

# Should output: ios-test-gen, version 0.1.0
```

---

## 🔑 Step 2: Set Up Your API Key

Choose one of the following providers:

### For OpenAI (Default - Recommended)

```bash
export OPENAI_API_KEY="sk-your-openai-api-key-here"
```

### For Anthropic Claude

```bash
export ANTHROPIC_API_KEY="sk-ant-your-anthropic-api-key-here"
```

**💡 Tip:** Add this to your `~/.bashrc` or `~/.zshrc` to make it permanent:

```bash
echo 'export OPENAI_API_KEY="sk-your-key-here"' >> ~/.zshrc
source ~/.zshrc
```

---

## 📂 Step 3: Navigate to Your iOS Project

```bash
cd /path/to/your/ios-project
```

Your iOS project should have one of these structures:
- `YourApp.xcodeproj` (Xcode project)
- `Package.swift` (Swift Package)
- Source files in directories like `Sources/`, `YourApp/`, etc.

---

## 🔍 Step 4: Analyze Your Project (Optional but Recommended)

Before generating tests, analyze your project to see what will be tested:

```bash
ios-test-gen analyze . --verbose
```

This will show:
- ✅ Project structure
- ✅ Source files found
- ✅ Classes, structs, enums discovered
- ✅ Methods and properties to test
- ✅ Total testable elements

**Example Output:**
```
📊 Project Analysis
Project: /Users/you/MyApp

Project Info
Name: MyApp
Root: /Users/you/MyApp
Source Files: 25
Existing Tests: 10

📁 Source Files
├─ UserManager.swift
│  ├─ Imports: Foundation
│  └─ class UserManager (5m, 3p, 0ec)
├─ NetworkService.swift
│  └─ protocol NetworkService (2m, 0p, 0ec)
...
```

---

## 🧪 Step 5: Generate Tests

### Basic Usage (Generate for Entire Project)

```bash
ios-test-gen generate .
```

This will:
1. Scan your project
2. Parse all Swift files
3. Generate XCTest cases using AI
4. Save tests to `GeneratedTests/` directory

### Advanced Usage Examples

#### Generate tests for specific files only:

```bash
ios-test-gen generate . --files UserManager.swift --files NetworkService.swift
```

#### Generate tests for specific types/classes:

```bash
ios-test-gen generate . --types UserManager --types AuthService
```

#### Specify custom output directory:

```bash
ios-test-gen generate . -o ./MyAppTests
```

#### Use Anthropic Claude instead of OpenAI:

```bash
ios-test-gen generate . --provider anthropic --model claude-sonnet-4-20250514
```

#### Use a different OpenAI model:

```bash
ios-test-gen generate . --model gpt-4o-mini
```

#### Disable mock generation:

```bash
ios-test-gen generate . --no-mocks
```

#### Dry run (analyze without generating):

```bash
ios-test-gen generate . --dry-run --verbose
```

---

## 📋 Step 6: Review Generated Tests

After generation completes, you'll see output like:

```
✅ Done!
Generated 15 test files with 87 test methods.
Output: /Users/you/MyApp/GeneratedTests
```

Navigate to the output directory:

```bash
cd GeneratedTests
ls -la
```

You'll find files like:
- `UserManagerTests.swift`
- `NetworkServiceTests.swift`
- `AuthServiceTests.swift`
- etc.

---

## 🔧 Step 7: Add Tests to Your Xcode Project

### For Xcode Projects:

1. Open your Xcode project
2. Right-click on your test target (e.g., `MyAppTests`)
3. Select "Add Files to MyAppTests..."
4. Navigate to `GeneratedTests/` folder
5. Select all `.swift` files
6. ✅ Check "Copy items if needed"
7. ✅ Select your test target
8. Click "Add"

### For Swift Packages:

Add the test files to your `Package.swift`:

```swift
.testTarget(
    name: "MyAppTests",
    dependencies: ["MyApp"],
    path: "GeneratedTests"
)
```

---

## ▶️ Step 8: Run the Tests

### In Xcode:
- Press `⌘ + U` to run all tests
- Or click the diamond icon next to test methods

### From Command Line:
```bash
xcodebuild test -scheme YourApp -destination 'platform=iOS Simulator,name=iPhone 15'
```

---

## ⚙️ Step 9: Customize Configuration (Optional)

Create a configuration file for your project:

```bash
ios-test-gen init .
```

This creates `ios-test-gen.yml` in your project root. Edit it:

```yaml
# LLM Settings
llm_provider: openai          # "openai" or "anthropic"
model: gpt-4o                 # Model name
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

Now run without flags:

```bash
ios-test-gen generate .
```

---

## 🎯 Real-World Example

Let's say you have this iOS project structure:

```
MyShoppingApp/
├── MyShoppingApp.xcodeproj
├── MyShoppingApp/
│   ├── Models/
│   │   ├── Product.swift
│   │   └── Cart.swift
│   ├── Services/
│   │   ├── NetworkService.swift
│   │   └── PaymentService.swift
│   └── ViewModels/
│       ├── ProductListViewModel.swift
│       └── CartViewModel.swift
└── MyShoppingAppTests/
    └── (existing tests)
```

### Generate tests for the entire app:

```bash
cd MyShoppingApp
ios-test-gen generate . -o ./MyShoppingAppTests/Generated
```

### Generate tests only for Services:

```bash
ios-test-gen generate . \
  --files NetworkService.swift \
  --files PaymentService.swift \
  -o ./MyShoppingAppTests/ServiceTests
```

### Generate with verbose output:

```bash
ios-test-gen generate . --verbose
```

**Output:**
```
🧪 iOS Test Generator Agent
Analyzing project at: /Users/you/MyShoppingApp

Project Info
Name: MyShoppingApp
Source Files: 12
Existing Tests: 5

Parsing 12 Swift files...
  📄 Product.swift (1 type, 3 methods, 5 properties)
  📄 Cart.swift (1 type, 8 methods, 2 properties)
  ...

Generating tests for 12 files...
  ✓ Generated ProductTests (5 tests)
  ✓ Generated CartTests (12 tests)
  ✓ Generated NetworkServiceTests (8 tests)
  ...

✅ Done!
Generated 12 test files with 67 test methods.
Output: /Users/you/MyShoppingApp/MyShoppingAppTests/Generated
```

---

## 🐛 Troubleshooting

### Issue: "Command not found: ios-test-gen"

**Solution:**
```bash
# Make sure virtual environment is activated
source .venv/bin/activate

# Reinstall
pip install -e .
```

### Issue: "OPENAI_API_KEY environment variable is required"

**Solution:**
```bash
export OPENAI_API_KEY="sk-your-key-here"
```

### Issue: "No source files found to analyze"

**Solution:**
- Check you're in the correct directory
- Verify your project has `.swift` files
- Check exclude patterns in config

### Issue: Generated tests have compilation errors

**Solution:**
- Review the generated code
- Add missing imports manually
- Adjust the LLM temperature (lower = more conservative)
- Regenerate with `--no-mocks` if mock generation is problematic

---

## 📚 Additional Commands

### Get help:
```bash
ios-test-gen --help
ios-test-gen generate --help
ios-test-gen analyze --help
```

### Check version:
```bash
ios-test-gen --version
```

---

## 💡 Best Practices

1. **Start Small**: Generate tests for 1-2 files first to verify quality
2. **Review Generated Tests**: Always review and adjust generated tests
3. **Use Verbose Mode**: Use `--verbose` to understand what's being generated
4. **Customize Config**: Create `ios-test-gen.yml` for consistent settings
5. **Version Control**: Commit generated tests to git after review
6. **Iterate**: Regenerate tests as your code evolves
7. **Combine with Manual Tests**: Use generated tests as a starting point

---

## 🎓 Example Workflow

```bash
# 1. Set up (one-time)
cd /path/to/ios_Test_Generator_Agent
python -m venv .venv
source .venv/bin/activate
pip install -e .
export OPENAI_API_KEY="sk-..."

# 2. Navigate to your iOS project
cd /path/to/your/ios-project

# 3. Analyze first
ios-test-gen analyze . --verbose

# 4. Generate tests
ios-test-gen generate . -o ./MyAppTests/Generated

# 5. Add to Xcode and run tests
# (Use Xcode UI to add files)

# 6. Review and commit
git add MyAppTests/Generated/
git commit -m "Add generated unit tests"
```

---

## 🚀 You're Ready!

You now have everything you need to generate XCTest cases for your iOS project. Start with a small subset of files, review the quality, and then scale up to your entire codebase.

**Happy Testing! 🧪✨**