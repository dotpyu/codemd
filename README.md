```
   ___             _                    ___ 
  / __\  ___    __| |  ___    /\/\     /   \
 / /    / _ \  / _` | / _ \  /    \   / /\ /
/ /___ | (_) || (_| ||  __/ / /\/\ \ / /_// 
\____/  \___/  \__,_| \___| \/    \//___,' 
```
# codemd

Transform code repositories into markdown-formatted strings ready for LLM prompting. Easily convert your entire codebase into a format that's optimal for code-related prompts with LLMs like GPT-4, Claude, etc.

[![Tests](https://github.com/dotpyu/codemd/actions/workflows/tests.yml/badge.svg)](https://github.com/dotpyu/codemd/actions/workflows/tests.yml)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)


## Features
- Recursively scans directories for code files
- Configurable file extensions
- File and pattern exclusion support
- Markdown-formatted output
- Preserves directory structure in headers
- Simple command-line interface
- Token count estimation (tiktoken package required)
- Direct copy to clipboard

## Installation
```bash
git clone https://github.com/dotpyu/codemd.git
cd codemd
pip install -e .
```

## Usage
Basic usage:
```bash
codemd /path/to/your/code
```

With custom extensions and output file:
```bash
codemd /path/to/your/code -e py,java,sql -o output.md
```

Exclude specific patterns or files:
```bash
codemd /path/to/your/code \
    --exclude-patterns "test_,debug_" \
    --exclude-extensions "test.py,spec.js"
```

As a Python package:
```python
from codemd import CodeScanner

scanner = CodeScanner(
    extensions={'py', 'java'},
    exclude_patterns={'test_'},
    exclude_extensions={'test.py'}
)
markdown_string = scanner.scan_directory('./my_project')
```


## License
Distributed under the Apache 2 License. See `LICENSE` for more information.