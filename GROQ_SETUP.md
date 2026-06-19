# 🚀 Using Groq with iOS Test Generator Agent

## What is Groq?

Groq provides ultra-fast LLM inference with models like:
- **Llama 3.1 70B** - High quality, fast inference
- **Llama 3.1 8B** - Lightweight and extremely fast
- **Mixtral 8x7B** - Excellent for code generation
- **Gemma 2 9B** - Google's efficient model

**Benefits:**
- ⚡ **Much faster** than OpenAI/Anthropic (up to 10x)
- 💰 **More affordable** pricing
- 🆓 **Free tier** available
- 🎯 **Great for code generation**

---

## 📋 Setup Instructions

### Step 1: Get Your Groq API Key

1. Go to [https://console.groq.com](https://console.groq.com)
2. Sign up for a free account
3. Navigate to API Keys section
4. Create a new API key
5. Copy your API key (starts with `gsk_...`)

### Step 2: Install Groq Support

```bash
# Make sure you're in the project directory
cd /Users/shailendrasingh/Documents/Agentic\ AI\ Projects/ios_Test_Generator_Agent

# Activate virtual environment
source .venv/bin/activate

# Reinstall with Groq support
pip install -e .
```

### Step 3: Set Your Groq API Key

Choose one of these methods:

#### Option A: For Current Session Only
```bash
export GROQ_API_KEY="gsk_your_groq_api_key_here"
```

#### Option B: Make it Permanent (Recommended)
```bash
# For zsh (macOS default)
echo 'export GROQ_API_KEY="gsk_your_groq_api_key_here"' >> ~/.zshrc
source ~/.zshrc

# For bash
echo 'export GROQ_API_KEY="gsk_your_groq_api_key_here"' >> ~/.bashrc
source ~/.bashrc
```

#### Option C: Create a Setup Script
```bash
# Create groq_setup.sh
cat > groq_setup.sh << 'EOF'
#!/bin/bash
export GROQ_API_KEY="gsk_your_groq_api_key_here"
echo "✅ Groq API Key set for this session"
EOF

chmod +x groq_setup.sh
source ./groq_setup.sh
```

---

## 🎯 Usage Examples

### Basic Usage with Groq

```bash
# Use Groq with default model (llama-3.1-70b-versatile)
ios-test-gen generate /path/to/project --provider groq

# Specify a Groq model
ios-test-gen generate /path/to/project --provider groq --model llama-3.1-70b-versatile
```

### Recommended Groq Models for Test Generation

#### 1. **Llama 3.1 70B Versatile** (Best Quality)
```bash
ios-test-gen generate . --provider groq --model llama-3.1-70b-versatile
```
- **Best for:** Complex test scenarios, comprehensive coverage
- **Speed:** Fast
- **Quality:** Excellent

#### 2. **Llama 3.1 8B Instant** (Fastest)
```bash
ios-test-gen generate . --provider groq --model llama-3.1-8b-instant
```
- **Best for:** Quick iterations, simple tests
- **Speed:** Extremely fast
- **Quality:** Good

#### 3. **Mixtral 8x7B** (Balanced)
```bash
ios-test-gen generate . --provider groq --model mixtral-8x7b-32768
```
- **Best for:** Code generation, balanced performance
- **Speed:** Very fast
- **Quality:** Very good

#### 4. **Gemma 2 9B** (Efficient)
```bash
ios-test-gen generate . --provider groq --model gemma2-9b-it
```
- **Best for:** Efficient test generation
- **Speed:** Very fast
- **Quality:** Good

---

## 📊 Groq vs OpenAI vs Anthropic

| Feature | Groq | OpenAI | Anthropic |
|---------|------|--------|-----------|
| **Speed** | ⚡⚡⚡ Fastest | ⚡ Fast | ⚡⚡ Very Fast |
| **Cost** | 💰 Cheapest | 💰💰 Moderate | 💰💰 Moderate |
| **Quality** | ⭐⭐⭐⭐ Very Good | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐⭐ Excellent |
| **Free Tier** | ✅ Yes | ❌ No | ❌ No |
| **Best For** | Speed & Cost | Quality | Quality & Context |

---

## 🔧 Configuration File with Groq

Create or update `ios-test-gen.yml`:

```yaml
# LLM Settings
llm_provider: groq                    # Use Groq
model: llama-3.1-70b-versatile       # Groq model
temperature: 0.2                      # Lower = more deterministic
max_tokens: 4096                      # Max response tokens

# Test Generation Settings
test_framework: XCTest
include_setup_teardown: true
generate_mocks: true
mock_framework: manual

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

Then simply run:
```bash
ios-test-gen generate /path/to/project
```

---

## 💡 Real-World Examples

### Example 1: Fast Test Generation for Large Project

```bash
# Use fastest model for quick iteration
ios-test-gen generate ~/MyApp \
  --provider groq \
  --model llama-3.1-8b-instant \
  -o ~/MyApp/Tests/Generated \
  --verbose
```

### Example 2: High-Quality Tests for Critical Code

```bash
# Use best model for important code
ios-test-gen generate ~/MyApp \
  --provider groq \
  --model llama-3.1-70b-versatile \
  --files UserManager.swift \
  --files PaymentService.swift \
  -o ~/MyApp/Tests/Critical
```

### Example 3: Batch Generation with Different Models

```bash
# Quick pass with fast model
ios-test-gen generate ~/MyApp --provider groq --model llama-3.1-8b-instant

# Review and regenerate critical files with better model
ios-test-gen generate ~/MyApp \
  --provider groq \
  --model llama-3.1-70b-versatile \
  --files CriticalService.swift
```

---

## 🎓 Complete Workflow with Groq

```bash
# 1. Set up Groq API key
export GROQ_API_KEY="gsk_your_key_here"

# 2. Navigate to your iOS project
cd /path/to/your/ios-project

# 3. Analyze project first
ios-test-gen analyze . --verbose

# 4. Generate tests with Groq (fast model for initial pass)
ios-test-gen generate . \
  --provider groq \
  --model llama-3.1-8b-instant \
  -o ./Tests/Generated

# 5. Review generated tests

# 6. Regenerate specific files with better model if needed
ios-test-gen generate . \
  --provider groq \
  --model llama-3.1-70b-versatile \
  --files ImportantClass.swift \
  -o ./Tests/Generated

# 7. Add to Xcode and run tests
```

---

## 🔄 Switching Between Providers

You can easily switch between providers:

```bash
# Use OpenAI
ios-test-gen generate . --provider openai --model gpt-4o

# Use Anthropic
ios-test-gen generate . --provider anthropic --model claude-sonnet-4-20250514

# Use Groq
ios-test-gen generate . --provider groq --model llama-3.1-70b-versatile
```

Or set via environment variable:
```bash
export IOS_TEST_GEN_LLM_PROVIDER=groq
export IOS_TEST_GEN_MODEL=llama-3.1-70b-versatile
ios-test-gen generate .
```

---

## 📈 Performance Comparison

Based on typical iOS project test generation:

| Provider | Model | Speed | Cost (1000 tests) | Quality |
|----------|-------|-------|-------------------|---------|
| Groq | llama-3.1-8b-instant | ~2 min | ~$0.50 | Good |
| Groq | llama-3.1-70b-versatile | ~5 min | ~$2.00 | Excellent |
| OpenAI | gpt-4o | ~15 min | ~$10.00 | Excellent |
| OpenAI | gpt-4o-mini | ~10 min | ~$3.00 | Very Good |
| Anthropic | claude-sonnet-4 | ~12 min | ~$8.00 | Excellent |

*Estimates based on average project with 50 classes*

---

## 🐛 Troubleshooting

### Issue: "GROQ_API_KEY environment variable is required"

**Solution:**
```bash
export GROQ_API_KEY="gsk_your_key_here"
```

### Issue: "Import groq could not be resolved"

**Solution:**
```bash
pip install -e .
# or
pip install groq>=0.4.0
```

### Issue: Rate limit errors

**Solution:**
- Groq has generous rate limits on free tier
- If you hit limits, wait a few seconds or upgrade to paid tier
- Use `--files` to generate tests for fewer files at once

---

## 💰 Groq Pricing (as of 2024)

**Free Tier:**
- 14,400 requests per day
- 30 requests per minute
- Perfect for most development needs

**Paid Tier:**
- Pay-as-you-go pricing
- Much cheaper than OpenAI/Anthropic
- No monthly minimums

---

## ✅ Best Practices with Groq

1. **Start Fast:** Use `llama-3.1-8b-instant` for initial generation
2. **Refine Critical:** Use `llama-3.1-70b-versatile` for important code
3. **Batch Wisely:** Generate tests in batches to stay within rate limits
4. **Compare Results:** Try different models and compare quality
5. **Cache Results:** Save generated tests to avoid regeneration

---

## 🎯 Recommended Setup

For the best experience, set up all three providers:

```bash
# Add to ~/.zshrc or ~/.bashrc
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GROQ_API_KEY="gsk_..."

# Set default to Groq for speed
export IOS_TEST_GEN_LLM_PROVIDER=groq
export IOS_TEST_GEN_MODEL=llama-3.1-70b-versatile
```

Then switch as needed:
```bash
# Use Groq (default)
ios-test-gen generate .

# Use OpenAI for critical code
ios-test-gen generate . --provider openai --files CriticalClass.swift

# Use Anthropic for complex logic
ios-test-gen generate . --provider anthropic --files ComplexAlgorithm.swift
```

---

## 🚀 You're Ready to Use Groq!

Groq provides the fastest and most cost-effective way to generate iOS tests. Start with the free tier and scale as needed.

**Quick Start:**
```bash
export GROQ_API_KEY="gsk_your_key_here"
ios-test-gen generate /path/to/project --provider groq
```

**Happy Testing with Groq! ⚡🧪**