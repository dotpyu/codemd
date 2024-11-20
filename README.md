<div align="center">

```
   ___             _                    ___ 
  / __\  ___    __| |  ___    /\/\     /   \
 / /    / _ \  / _` | / _ \  /    \   / /\ /
/ /___ | (_) || (_| ||  __/ / /\/\ \ / /_// 
\____/  \___/  \__,_| \___| \/    \//___,' 

Ver. 0.0.3
```

# CodeMD

🚀 Transform code files and repositories into markdown-formatted strings ready for LLM prompting and automatically copy to your clipboard. Perfect for seamless code-to-prompt workflow with ChatGPT, Claude, and other LLMs.

[![Tests](https://github.com/dotpyu/codemd/actions/workflows/tests.yml/badge.svg)](https://github.com/dotpyu/codemd/actions/workflows/tests.yml)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

</div>

## 📝 Overview

Tired of copying code files one by one? CodeMD instantly collects all relevant code in Markdown format and copies it to your clipboard - ready for ChatGPT, Claude, or any LLM.

Whether you need to process a single script or an entire codebase, CodeMD automatically:
- Formats your code into LLM-friendly markdown
- Preserves file structure and syntax highlighting
- Estimates token usage for GPT models
- Copies everything to your clipboard

Perfect for developers who want to:
- Get AI assistance with code review
- Ask LLMs about specific implementations
- Document and explain codebases
- Debug complex issues with AI help

No more manual copying and pasting - just run CodeMD and start chatting with your favorite LLM!


## ✨ Features

- 🔍 **Flexible Processing**: 
  - Single file processing
  - Recursive directory scanning
- 🎯 **Configurable Options**: 
  - Configurable file extensions
  - File and pattern exclusion support
  - Custom .gitignore support
- 📊 **Smart Output**:
  - Markdown-formatted code blocks
  - Optional directory structure visualization
  - Token count estimation (with tiktoken)
  - Configurable output display
- 📋 **Convenience**:
  - Simple command-line interface
  - Direct copy-to-clipboard support
  - Multiple output options

### 🎉 Recent Updates (0.0.3)

- ⭐ **NEW**: Single file processing support
- ⭐ **NEW**: Configurable output display (use `--print` to show output)
- ⭐ **NEW**: Repository structure visualization (auto-disabled for single files, or use `--no-structure`)
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

**Single File Processing:**
```bash
# Process a single file (no output by default)
codemd /path/to/script.py

# Process and display output
codemd /path/to/script.py --print

# Save to file
codemd /path/to/script.py -o output.md
```

**Directory Processing:**
```bash
# Basic directory scanning (no output by default)
codemd /path/to/your/code

# Show output in terminal
codemd /path/to/your/code --print

# Custom extensions and output file
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
