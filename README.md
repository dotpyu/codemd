<div align="center">

```
   ___             _                    ___ 
  / __\  ___    __| |  ___    /\/\     /   \
 / /    / _ \  / _` | / _ \  /    \   / /\ /
/ /___ | (_) || (_| ||  __/ / /\/\ \ / /_// 
\____/  \___/  \__,_| \___| \/    \//___,' 

Ver. 0.0.2
````

# CodeMD

🚀 Transform code repositories into markdown-formatted strings ready for LLM prompting

[![Tests](https://github.com/dotpyu/codemd/actions/workflows/tests.yml/badge.svg)](https://github.com/dotpyu/codemd/actions/workflows/tests.yml)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

</div>

## 📝 Overview

CodeMD helps you convert your entire codebase into a format that's optimal for code-related prompts with Large Language Models (LLMs) like GPT-4, Claude, and others. It automatically processes your code files and outputs them in a clean, markdown-formatted structure that's perfect for LLM interactions.

## ✨ Features

- 🔍 **Smart Directory Scanning**: Recursively scans directories for code files
- 🎯 **Flexible Configuration**: 
  - Configurable file extensions
  - File and pattern exclusion support
  - Custom .gitignore support
- 📊 **Intelligent Output**:
  - Markdown-formatted code blocks
  - Preserved directory structure
  - Repository structure visualization
  - Token count estimation (with tiktoken)
- 📋 **Convenience**:
  - Simple command-line interface
  - Direct copy-to-clipboard support
  - Multiple output options

### 🎉 Recent Updates

- ⭐ **NEW**: Repository structure visualization (disable with `--no-structure`)
- ⭐ **NEW**: Automatic .gitignore support
  - Uses project's .gitignore by default
  - Custom .gitignore files via `--gitignore`
  - Disable with `--ignore-gitignore`

## 🚀 Installation
```bash
pip install codemd
```

or install from source!

```bash
git clone https://github.com/dotpyu/codemd.git
cd codemd
pip install -e .
```

## 📖 Usage

### Command Line Interface

**Basic Usage:**
```bash
codemd /path/to/your/code
```

**Custom Extensions and Output:**
```bash
codemd /path/to/your/code -e py,java,sql -o output.md
```

**Pattern Exclusion:**
```bash
codemd /path/to/your/code \
    --exclude-patterns "test_,debug_" \
    --exclude-extensions "test.py,spec.js"
```

**.gitignore Configuration:**
```bash
# Use custom gitignore files
codemd /path/to/your/code --gitignore .gitignore .custom-ignore

# Disable gitignore processing
codemd /path/to/your/code --ignore-gitignore
```

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

Distributed under the Apache 2.0 License. See `LICENSE` for more information.

---
<div align="center">
Made with ❤️ by Peilin
</div>
