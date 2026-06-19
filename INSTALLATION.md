# Installation Guide

Complete guide for installing and deploying the iOS Test Generator Agent globally.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Global Installation](#global-installation)
- [Development Installation](#development-installation)
- [Configuration](#configuration)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [Uninstallation](#uninstallation)

## Prerequisites

### System Requirements

- **Python**: 3.9 or higher
- **Operating System**: macOS, Linux, or Windows
- **Disk Space**: ~50 MB for installation
- **Internet**: Required for LLM API calls

### API Keys

You'll need at least one of the following API keys:

- **OpenAI API Key**: For GPT models (recommended)
- **Anthropic API Key**: For Claude models
- **Groq API Key**: For fast, open-source models

Get your API keys:
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/
- Groq: https://console.groq.com/

## Global Installation

### Method 1: Install from PyPI (Recommended)

Once published to PyPI:

```bash
# Install globally
pip install ios-test-generator-agent

# Or with pipx (recommended for CLI tools)
pipx install ios-test-generator-agent
```

### Method 2: Install from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/ios-test-generator-agent.git
cd ios-test-generator-agent

# Install globally
pip install .

# Or install in editable mode for development
pip install -e .
```

### Method 3: Install with pipx (Isolated Environment)

```bash
# Install pipx if you don't have it
python3 -m pip install --user pipx
python3 -m pipx ensurepath

# Install the tool
pipx install ios-test-generator-agent

# Or from source
pipx install .
```

## Development Installation

For contributors and developers:

```bash
# Clone the repository
git clone https://github.com/yourusername/ios-test-generator-agent.git
cd ios-test-generator-agent

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install with development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check .
black --check .
mypy ios_test_generator_agent
```

## Configuration

### 1. Set Up API Keys

Choose one of these methods:

#### Option A: Environment Variables (Recommended)

```bash
# Add to your shell profile (~/.bashrc, ~/.zshrc, etc.)
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export GROQ_API_KEY="your-groq-api-key"

# Reload your shell
source ~/.bashrc  # or ~/.zshrc
```

#### Option B: .env File

Create a `.env` file in your project directory:

```bash
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
GROQ_API_KEY=your-groq-api-key
```

#### Option C: Use the Setup Script

```bash
# Run the provided setup script
chmod +x setup_api_key.sh
./setup_api_key.sh
```

### 2. Create Configuration File (Optional)

Generate a default configuration:

```bash
cd your-ios-project
ios-test-gen init
```

This creates `ios-test-gen.yml` with default settings. Customize as needed:

```yaml
llm_provider: openai
model: gpt-4o
temperature: 0.2
max_tokens: 4096
test_framework: XCTest
include_setup_teardown: true
generate_mocks: true
mock_framework: manual
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

## Verification

### Test the Installation

```bash
# Check version
ios-test-gen --version

# Should output: ios-test-gen, version 1.0.0

# View help
ios-test-gen --help

# Test with a sample project
ios-test-gen analyze /path/to/ios/project
```

### Verify API Keys

```bash
# Test OpenAI
echo $OPENAI_API_KEY

# Test Anthropic
echo $ANTHROPIC_API_KEY

# Test Groq
echo $GROQ_API_KEY
```

### Run a Quick Test

```bash
# Navigate to an iOS project
cd /path/to/your/ios/project

# Analyze the project (dry run)
ios-test-gen generate --dry-run

# Generate tests for a specific file
ios-test-gen generate --files UserManager.swift
```

## Troubleshooting

### Common Issues

#### 1. Command Not Found

```bash
# Error: ios-test-gen: command not found

# Solution: Ensure pip bin directory is in PATH
python3 -m site --user-base
# Add the bin directory to your PATH

# Or reinstall with pipx
pipx install ios-test-generator-agent
```

#### 2. API Key Errors

```bash
# Error: API key for openai is not configured

# Solution: Set the environment variable
export OPENAI_API_KEY="your-key-here"

# Or check if it's set
echo $OPENAI_API_KEY
```

#### 3. Import Errors

```bash
# Error: ModuleNotFoundError: No module named 'tenacity'

# Solution: Reinstall with all dependencies
pip install --force-reinstall ios-test-generator-agent
```

#### 4. Permission Errors

```bash
# Error: Permission denied

# Solution: Install with --user flag
pip install --user ios-test-generator-agent

# Or use pipx
pipx install ios-test-generator-agent
```

#### 5. Python Version Issues

```bash
# Error: Requires Python >=3.9

# Solution: Check your Python version
python3 --version

# Install Python 3.9+ if needed
# macOS: brew install python@3.11
# Ubuntu: sudo apt install python3.11
# Windows: Download from python.org
```

### Getting Help

If you encounter issues:

1. **Check the logs**: Use `--verbose` flag for detailed output
   ```bash
   ios-test-gen generate --verbose
   ```

2. **Review documentation**: See [USAGE_GUIDE.md](USAGE_GUIDE.md)

3. **Report bugs**: https://github.com/yourusername/ios-test-generator-agent/issues

4. **Community support**: Join our discussions

## Uninstallation

### Remove the Package

```bash
# If installed with pip
pip uninstall ios-test-generator-agent

# If installed with pipx
pipx uninstall ios-test-generator-agent
```

### Clean Up Configuration

```bash
# Remove configuration files (optional)
rm ios-test-gen.yml

# Remove environment variables from shell profile
# Edit ~/.bashrc or ~/.zshrc and remove the export lines
```

## Upgrading

### Upgrade to Latest Version

```bash
# With pip
pip install --upgrade ios-test-generator-agent

# With pipx
pipx upgrade ios-test-generator-agent

# Check new version
ios-test-gen --version
```

### View Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and breaking changes.

## Next Steps

After installation:

1. **Quick Start**: Follow [QUICK_START.md](QUICK_START.md)
2. **Usage Guide**: Read [USAGE_GUIDE.md](USAGE_GUIDE.md)
3. **Configure LLM**: See [GROQ_SETUP.md](GROQ_SETUP.md) for Groq setup
4. **Generate Tests**: Start with `ios-test-gen generate`

## Support

- **Documentation**: https://ios-test-generator-agent.readthedocs.io
- **Issues**: https://github.com/yourusername/ios-test-generator-agent/issues
- **Discussions**: https://github.com/yourusername/ios-test-generator-agent/discussions

---

**Happy Testing! 🧪**