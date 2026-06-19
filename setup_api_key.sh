#!/bin/bash

# Setup script for iOS Test Generator Agent
# This script sets up your OpenAI API key

echo "🔑 Setting up OpenAI API Key..."

# Set the API key
export OPENAI_API_KEY=""

echo "✅ OpenAI API Key has been set for this session"
echo ""
echo "To make this permanent, add this line to your shell profile:"
echo ""
echo "export OPENAI_API_KEY=\"\""
echo ""
echo "Add it to:"
echo "  - ~/.zshrc (if using zsh)"
echo "  - ~/.bashrc (if using bash)"
echo ""
echo "Then run: source ~/.zshrc (or ~/.bashrc)"
echo ""
echo "🚀 You can now use the iOS Test Generator Agent!"

# Made with Bob
