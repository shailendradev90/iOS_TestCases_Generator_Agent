# 🚀 Quick Start Guide - iOS Test Generator Agent

## ⚡ Fast Setup (5 Minutes)

### Step 1: Install Dependencies

```bash
# Navigate to the project directory
cd /Users/shailendrasingh/Documents/Agentic\ AI\ Projects/ios_Test_Generator_Agent

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Install the package
pip install -e .
```

### Step 2: Set Up API Key (Already Configured!)

Your OpenAI API key is ready to use. Choose one of these methods:

#### Option A: Use the Setup Script (Recommended)
```bash
source ./setup_api_key.sh
```

#### Option B: Set Manually for Current Session
```bash
export OPENAI_API_KEY="YOUR OPEN API KEY "
```

#### Option C: Make it Permanent (Add to ~/.zshrc or ~/.bashrc)
```bash
echo 'export OPENAI_API_KEY="YOUR OPEN KEY"' >> ~/.zshrc
source ~/.zshrc
```

### Step 3: Test with Sample Project

```bash
# Test the tool with the included sample project
ios-test-gen analyze ./sample_ios_project --verbose

# Generate tests for the sample
ios-test-gen generate ./sample_ios_project -o ./sample_tests
```

### Step 4: Use with Your iOS Project

```bash
# Navigate to your iOS project
cd /path/to/your/ios-project

# Analyze your project
ios-test-gen analyze . --verbose

# Generate tests
ios-test-gen generate . -o ./GeneratedTests
```

---

## 📋 Common Commands

### Analyze Project
```bash
ios-test-gen analyze /path/to/project --verbose
```

### Generate Tests (Basic)
```bash
ios-test-gen generate /path/to/project
```

### Generate Tests (Advanced)
```bash
# Specific files
ios-test-gen generate . --files UserManager.swift --files NetworkService.swift

# Custom output directory
ios-test-gen generate . -o ./MyTests

# Use different model
ios-test-gen generate . --model gpt-4o-mini

# Dry run (no generation)
ios-test-gen generate . --dry-run --verbose
```

---

## 🎯 Example: Generate Tests for Sample Project

```bash
# 1. Make sure you're in the project directory
cd /Users/shailendrasingh/Documents/Agentic\ AI\ Projects/ios_Test_Generator_Agent

# 2. Activate virtual environment
source .venv/bin/activate

# 3. Set API key (if not already set)
source ./setup_api_key.sh

# 4. Generate tests for sample project
ios-test-gen generate ./sample_ios_project -o ./sample_tests --verbose
```

**Expected Output:**
```
🧪 iOS Test Generator Agent
Analyzing project at: ./sample_ios_project

Project Info
Name: sample_ios_project
Source Files: 1

Parsing 1 Swift files...
  📄 UserManager.swift (4 types, 3 methods, 3 properties)

Generating tests for 1 files...
  ✓ Generated UserManagerTests (8 tests)

✅ Done!
Generated 1 test files with 8 test methods.
Output: ./sample_tests
```

---

## 🔍 Verify Installation

```bash
# Check version
ios-test-gen --version

# Get help
ios-test-gen --help

# Test with sample project
ios-test-gen analyze ./sample_ios_project
```

---

## ✅ You're All Set!

Your OpenAI API key is configured and the tool is ready to use. 

**Next Steps:**
1. ✅ Test with the sample project (see example above)
2. ✅ Navigate to your iOS project
3. ✅ Run `ios-test-gen generate .`
4. ✅ Review generated tests
5. ✅ Add to Xcode and run

For detailed documentation, see **USAGE_GUIDE.md**

---

## 🐛 Troubleshooting

### "Command not found: ios-test-gen"
```bash
source .venv/bin/activate
pip install -e .
```

### "API key not set"
```bash
source ./setup_api_key.sh
```

### "No source files found"
Make sure you're in the correct directory with Swift files.

---

## 📚 More Information

- **Full Guide**: See `USAGE_GUIDE.md`
- **README**: See `README.md`
- **Sample Project**: Check `sample_ios_project/Sources/UserManager.swift`

**Happy Testing! 🧪✨**