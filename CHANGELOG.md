# Changelog

All notable changes to the iOS Test Generator Agent will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-06-19

### Added
- **Production-Ready Release**: First stable production release
- **Comprehensive Error Handling**: Custom exception hierarchy for better error management
- **Advanced Logging**: Rich console logging with file output support
- **Retry Logic**: Automatic retry with exponential backoff for LLM API calls
- **Rate Limiting**: Built-in rate limiting to prevent API throttling
- **Input Validation**: Robust validation for all user inputs and configurations
- **Multiple LLM Support**: OpenAI, Anthropic Claude, and Groq integration
- **Swift Code Parser**: Advanced parser for Swift classes, structs, enums, and protocols
- **Test Generation**: AI-powered XCTest generation with comprehensive coverage
- **CLI Interface**: User-friendly command-line interface with rich output
- **Configuration Management**: Flexible configuration via files, environment variables, and CLI args
- **Project Scanner**: Automatic iOS project structure detection
- **Documentation**: Complete usage guides and setup instructions

### Features
- Generate XCTest cases for Swift code automatically
- Support for async/await and throwing functions
- Mock generation for protocols and dependencies
- Setup/teardown method generation
- Comprehensive test coverage for edge cases
- Beautiful CLI output with progress indicators
- Dry-run mode for project analysis
- Selective test generation (specific files/types)
- Multiple test framework support (XCTest, SwiftTesting)

### Technical Improvements
- Type-safe configuration with Pydantic models
- Modular architecture for easy extension
- Comprehensive error messages with actionable guidance
- Performance optimizations for large projects
- Memory-efficient file processing
- Robust Swift code parsing with regex patterns
- Smart import detection and management

### Developer Experience
- Easy global installation via pip
- Environment variable support for API keys
- Configuration file support (ios-test-gen.yml)
- Verbose mode for debugging
- Detailed logging for troubleshooting
- Clear error messages with solutions

### Security
- Secure API key handling
- No sensitive data logging
- Input sanitization
- Safe file operations

## [0.1.0] - 2024-06-01

### Added
- Initial development release
- Basic test generation functionality
- OpenAI integration
- Simple CLI interface
- Project scanning capabilities

---

## Release Notes

### Upgrading to 1.0.0

This is the first production-ready release. If you're upgrading from 0.1.0:

1. **Install the new version**:
   ```bash
   pip install --upgrade ios-test-generator-agent
   ```

2. **Update your configuration**:
   - The configuration format has been enhanced
   - Run `ios-test-gen init` to generate a new config file
   - Review and update your API keys in environment variables

3. **New Features**:
   - Retry logic is now enabled by default
   - Logging is more comprehensive
   - Error messages are more helpful

### Breaking Changes

None - this is the first stable release.

### Migration Guide

For users of the 0.1.0 development version:
- Configuration files are backward compatible
- CLI commands remain the same
- API key environment variables are unchanged

---

For more information, visit: https://github.com/yourusername/ios-test-generator-agent