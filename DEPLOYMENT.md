# Deployment Guide

Complete guide for deploying the iOS Test Generator Agent to production and distributing it globally.

## Table of Contents

- [Pre-Deployment Checklist](#pre-deployment-checklist)
- [Building the Package](#building-the-package)
- [Testing the Build](#testing-the-build)
- [Publishing to PyPI](#publishing-to-pypi)
- [Post-Deployment](#post-deployment)
- [Continuous Deployment](#continuous-deployment)
- [Rollback Procedures](#rollback-procedures)

## Pre-Deployment Checklist

Before deploying, ensure:

### 1. Code Quality
- [ ] All tests pass: `pytest tests/`
- [ ] Code is linted: `ruff check .`
- [ ] Code is formatted: `black .`
- [ ] Type checking passes: `mypy ios_test_generator_agent`
- [ ] No security vulnerabilities: `bandit -r ios_test_generator_agent`

### 2. Documentation
- [ ] README.md is up to date
- [ ] CHANGELOG.md includes all changes
- [ ] Version number is updated in `__init__.py`
- [ ] All documentation files are current

### 3. Configuration
- [ ] pyproject.toml has correct metadata
- [ ] Dependencies are pinned with version ranges
- [ ] LICENSE file is present
- [ ] MANIFEST.in includes all necessary files

### 4. Version Management
- [ ] Version follows semantic versioning (MAJOR.MINOR.PATCH)
- [ ] Git tag matches the version number
- [ ] CHANGELOG.md has entry for this version

## Building the Package

### 1. Clean Previous Builds

```bash
# Remove old build artifacts
rm -rf build/ dist/ *.egg-info/

# Clean Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

### 2. Update Version

Update version in `ios_test_generator_agent/__init__.py`:

```python
__version__ = "1.0.0"  # Update this
```

### 3. Build the Distribution

```bash
# Install build tools
pip install --upgrade build twine

# Build source distribution and wheel
python -m build

# This creates:
# - dist/ios_test_generator_agent-1.0.0.tar.gz (source)
# - dist/ios_test_generator_agent-1.0.0-py3-none-any.whl (wheel)
```

### 4. Verify the Build

```bash
# Check the package
twine check dist/*

# Should output: Checking dist/... PASSED
```

## Testing the Build

### 1. Test in a Clean Environment

```bash
# Create a test virtual environment
python3 -m venv test_env
source test_env/bin/activate

# Install from the built wheel
pip install dist/ios_test_generator_agent-1.0.0-py3-none-any.whl

# Test the installation
ios-test-gen --version
ios-test-gen --help

# Test basic functionality
cd /path/to/test/ios/project
ios-test-gen analyze --dry-run

# Deactivate and clean up
deactivate
rm -rf test_env
```

### 2. Test with Different Python Versions

```bash
# Test with Python 3.9
python3.9 -m venv test_env_39
source test_env_39/bin/activate
pip install dist/ios_test_generator_agent-1.0.0-py3-none-any.whl
ios-test-gen --version
deactivate

# Test with Python 3.11
python3.11 -m venv test_env_311
source test_env_311/bin/activate
pip install dist/ios_test_generator_agent-1.0.0-py3-none-any.whl
ios-test-gen --version
deactivate

# Clean up
rm -rf test_env_*
```

## Publishing to PyPI

### 1. Set Up PyPI Account

1. Create account at https://pypi.org/account/register/
2. Enable 2FA for security
3. Generate API token at https://pypi.org/manage/account/token/
4. Save token securely

### 2. Configure Credentials

```bash
# Option 1: Use environment variable
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your-api-token-here

# Option 2: Use .pypirc file
cat > ~/.pypirc << EOF
[pypi]
username = __token__
password = pypi-your-api-token-here
EOF

chmod 600 ~/.pypirc
```

### 3. Test on TestPyPI First

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ ios-test-generator-agent

# Verify it works
ios-test-gen --version
```

### 4. Publish to Production PyPI

```bash
# Upload to PyPI
twine upload dist/*

# Verify on PyPI
# Visit: https://pypi.org/project/ios-test-generator-agent/

# Test installation
pip install ios-test-generator-agent

# Verify
ios-test-gen --version
```

### 5. Create GitHub Release

```bash
# Tag the release
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# Create release on GitHub
# Go to: https://github.com/yourusername/ios-test-generator-agent/releases/new
# - Tag: v1.0.0
# - Title: v1.0.0 - Production Ready Release
# - Description: Copy from CHANGELOG.md
# - Attach: dist/ios_test_generator_agent-1.0.0.tar.gz
```

## Post-Deployment

### 1. Verify Installation

```bash
# Test global installation
pip install ios-test-generator-agent

# Verify version
ios-test-gen --version

# Test with real project
cd /path/to/ios/project
ios-test-gen generate --dry-run
```

### 2. Update Documentation

- [ ] Update README.md with installation instructions
- [ ] Update documentation website
- [ ] Announce release on social media/forums
- [ ] Update project status badges

### 3. Monitor

- [ ] Check PyPI download statistics
- [ ] Monitor GitHub issues for bug reports
- [ ] Watch for security vulnerabilities
- [ ] Review user feedback

## Continuous Deployment

### GitHub Actions Workflow

The project includes a CI/CD pipeline (`.github/workflows/ci.yml`) that:

1. **On Push/PR**: Runs tests, linting, and security scans
2. **On Release**: Automatically builds and publishes to PyPI

### Automated Release Process

```bash
# 1. Update version and changelog
vim ios_test_generator_agent/__init__.py
vim CHANGELOG.md

# 2. Commit changes
git add .
git commit -m "Bump version to 1.0.0"
git push origin main

# 3. Create and push tag
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# 4. Create GitHub release
# GitHub Actions will automatically:
# - Run all tests
# - Build the package
# - Publish to PyPI
```

### Required GitHub Secrets

Set these in GitHub repository settings:

- `PYPI_API_TOKEN`: Your PyPI API token
- `CODECOV_TOKEN`: (Optional) For code coverage

## Rollback Procedures

### If Issues Are Found After Release

#### 1. Yank the Release on PyPI

```bash
# This prevents new installations but doesn't break existing ones
# Go to: https://pypi.org/manage/project/ios-test-generator-agent/release/1.0.0/
# Click "Options" → "Yank release"
```

#### 2. Release a Patch Version

```bash
# Fix the issue
git checkout -b hotfix/1.0.1

# Make fixes
# ...

# Update version
vim ios_test_generator_agent/__init__.py  # Change to 1.0.1

# Update changelog
vim CHANGELOG.md

# Commit and release
git commit -am "Fix critical bug - v1.0.1"
git push origin hotfix/1.0.1

# Create PR and merge
# Then tag and release v1.0.1
git tag -a v1.0.1 -m "Hotfix v1.0.1"
git push origin v1.0.1
```

#### 3. Notify Users

- Post on GitHub releases
- Update documentation
- Send notifications if possible

## Best Practices

### Version Numbering

Follow Semantic Versioning (SemVer):

- **MAJOR** (1.0.0): Breaking changes
- **MINOR** (1.1.0): New features, backward compatible
- **PATCH** (1.0.1): Bug fixes, backward compatible

### Release Frequency

- **Patch releases**: As needed for critical bugs
- **Minor releases**: Monthly or when features are ready
- **Major releases**: Annually or for breaking changes

### Security

- Never commit API keys or secrets
- Use environment variables for sensitive data
- Enable 2FA on PyPI account
- Regularly update dependencies
- Run security scans before release

### Testing

- Test on multiple Python versions (3.9-3.13)
- Test on multiple OS (Linux, macOS, Windows)
- Test installation from PyPI
- Test with real iOS projects
- Get beta testers for major releases

## Troubleshooting

### Build Fails

```bash
# Check for syntax errors
python -m py_compile ios_test_generator_agent/*.py

# Verify dependencies
pip check

# Clean and rebuild
rm -rf build/ dist/ *.egg-info/
python -m build
```

### Upload Fails

```bash
# Check credentials
twine check dist/*

# Verify token
echo $TWINE_PASSWORD

# Try with verbose output
twine upload --verbose dist/*
```

### Installation Issues

```bash
# Check package on PyPI
pip index versions ios-test-generator-agent

# Test installation
pip install --no-cache-dir ios-test-generator-agent

# Check for conflicts
pip check
```

## Support

For deployment issues:

- **GitHub Issues**: https://github.com/yourusername/ios-test-generator-agent/issues
- **PyPI Support**: https://pypi.org/help/
- **Documentation**: https://ios-test-generator-agent.readthedocs.io

---

**Ready to Deploy! 🚀**