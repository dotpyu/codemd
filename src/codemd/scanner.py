import argparse
import sys
from pathlib import Path
from typing import Set, Optional, List

import pathspec

DEFAULT_CODE_EXTENSIONS = {
    # Systems Programming
    'c', 'h',              # C
    'cpp', 'hpp', 'cc',    # C++
    'rs', 'rlib',          # Rust
    'go',                  # Go

    # Web Development
    'js', 'jsx', 'ts', 'tsx',  # JavaScript/TypeScript
    'html', 'htm',         # HTML
    'css', 'scss', 'sass', # CSS and preprocessors
    'php',                 # PHP
    'vue',                 # Web Frameworks

    # General Purpose
    'py',                  # Python
    'java',                # Java
    'cs',                  # C#
    'rb',                  # Ruby
    'kt', 'kts',           # Kotlin
    'swift',               # Swift
    'scala',               # Scala

    # Shell/Scripts
    'sh', 'bash',          # Shell scripts
    'ps1',                 # PowerShell
    'bat', 'cmd',          # Windows Batch

    # Data/Config
    'sql',                 # SQL
    'r', 'R',              # R
    'json', 'yaml', 'yml', # Data formats
    'xml',                 # XML
    'toml',                # TOML

    # Others
    'pl', 'pm',           # Perl
    'dart',               # Dart
    'hs',                 # Haskell
    'lua',                # Lua
    'ml', 'mli'           # OCaml
}



class CodeScanner:
    def __init__(self,
                 extensions: Optional[Set[str]] = None,
                 exclude_patterns: Optional[Set[str]] = None,
                 exclude_extensions: Optional[Set[str]] = None,
                 gitignore_files: Optional[List[str]] = None,
                 ignore_gitignore: bool = False):
        """Initialize the CodeScanner with optional file extensions to filter."""
        self.extensions = extensions or DEFAULT_CODE_EXTENSIONS
        self.exclude_patterns = exclude_patterns or set()
        self.exclude_extensions = exclude_extensions or set()
        self.no_structure = False
        self.gitspec = None
        self.base_dir = None

        if not ignore_gitignore:
            self.load_gitignore(gitignore_files)

    def load_gitignore(self, gitignore_files: Optional[List[str]] = None):
        """Load gitignore patterns from specified files or default .gitignore"""
        patterns = []

        if gitignore_files:
            for gitignore_path in gitignore_files:
                try:
                    with open(gitignore_path, 'r') as f:
                        patterns.extend(f.readlines())
                except Exception as e:
                    print(f"Warning: Could not read gitignore file {gitignore_path}: {str(e)}",
                          file=sys.stderr)

        elif Path('.gitignore').exists():
            try:
                with open('.gitignore', 'r') as f:
                    patterns.extend(f.readlines())
            except Exception as e:
                print(f"Warning: Could not read default .gitignore: {str(e)}",
                      file=sys.stderr)

        if patterns:
            self.gitspec = pathspec.PathSpec.from_lines('gitwildmatch', patterns)

    def should_include_file(self, file_path: Path) -> bool:
        """Check if a file should be included based on extensions and exclusion patterns."""
        if self.gitspec is not None and self.base_dir is not None:
            try:
                rel_path = str(file_path.relative_to(self.base_dir))
                if self.gitspec.match_file(rel_path):
                    return False
            except ValueError:
                if self.gitspec.match_file(str(file_path)):
                    return False

        if file_path.suffix.lstrip('.') not in self.extensions:
            return False

        for pattern in self.exclude_patterns:
            if pattern in str(file_path):
                return False

        for ext_pattern in self.exclude_extensions:
            if str(file_path).endswith(ext_pattern):
                return False

        return True

    def generate_structure(self, path: Path, depth: int = 0) -> str:
        """
        Generate a tree-like structure of the codebase, respecting gitignore patterns.
        """
        structure = []

        try:
            items = sorted(path.iterdir())
            for item in items:
                if item.name.startswith('.'):
                    continue

                if self.gitspec is not None:
                    try:
                        rel_path = str(item.relative_to(self.base_dir))
                        if self.gitspec.match_file(rel_path):
                            continue
                    except ValueError:
                        if self.gitspec.match_file(str(item)):
                            continue

                indent = "  " * depth
                safe_name = item.name.replace('*', '\\*').replace('_', '\\_')

                if item.is_dir():
                    substructure = self.generate_structure(item, depth + 1)
                    if substructure:
                        structure.append(f"{indent}* **{safe_name}/**")
                        structure.extend(substructure.split('\n'))
                elif self.should_include_file(item):
                    structure.append(f"{indent}* {safe_name}")

        except PermissionError:
            pass

        return '\n'.join(structure)

    def scan_directory(self, directory: str, recursive: bool = True) -> str:
        """Scan a directory for code files and merge them into a markdown-formatted string."""
        directory_path = Path(directory)
        if not directory_path.exists():
            raise ValueError(f"Directory {directory} does not exist")

        self.base_dir = directory_path.resolve()

        merged_content = []

        if not self.no_structure:
            structure = ["# Repository Structure"]
            dir_structure = self.generate_structure(directory_path)
            if dir_structure:
                structure.append(dir_structure)
            structure.append("")
            merged_content.extend(structure)

        if recursive:
            files = list(directory_path.rglob("*"))
        else:
            files = list(directory_path.glob("*"))

        code_files = sorted(
            [f for f in files
             if f.is_file() and self.should_include_file(f)]
        )

        for file_path in code_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                relative_path = file_path.relative_to(directory_path)

                merged_content.extend([
                    f"# {relative_path}",
                    "```" + file_path.suffix.lstrip('.'),
                    content,
                    "```",
                    ""
                ])
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}", file=sys.stderr)

        return "\n".join(merged_content)

    def scan_file(self, file_path: Path) -> str:
        """Scan a single file and return its markdown-formatted content."""
        if not file_path.is_file():
            raise ValueError(f"Path {file_path} is not a file")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            merged_content = [
                f"# {file_path.name}",
                "```" + file_path.suffix.lstrip('.'),
                content,
                "```",
                ""
            ]
            return "\n".join(merged_content)
        except Exception as e:
            raise ValueError(f"Error processing {file_path}: {str(e)}")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Scan file or directory and create a markdown-formatted output'
    )
    parser.add_argument(
        'path',
        help='File or directory to scan'
    )
    parser.add_argument(
        '-e', '--extensions',
        help='Comma-separated list of file extensions to include (without dots)',
        default='py,java,js,cpp,c,h,hpp'
    )
    parser.add_argument(
        '--exclude-patterns',
        help='Comma-separated list of patterns to exclude (e.g., test_,debug_)',
        default=''
    )
    parser.add_argument(
        '--exclude-extensions',
        help='Comma-separated list of file patterns to exclude (e.g., test.py,spec.js)',
        default=''
    )
    parser.add_argument(
        '-o', '--output',
        help='Output file path (if not specified, no output is printed)',
        default=None,
    )
    parser.add_argument(
        '--no-recursive',
        action='store_true',
        help='Disable recursive directory scanning'
    )
    parser.add_argument(
        '--print',
        action='store_true',
        help='Print the markdown output'
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    extensions = {ext.strip() for ext in args.extensions.split(',') if ext.strip()}
    exclude_patterns = {pat.strip() for pat in args.exclude_patterns.split(',') if pat.strip()}
    exclude_extensions = {ext.strip() for ext in args.exclude_extensions.split(',') if ext.strip()}

    try:
        scanner = CodeScanner(
            extensions=extensions,
            exclude_patterns=exclude_patterns,
            exclude_extensions=exclude_extensions
        )

        path = Path(args.path)
        if not path.exists():
            raise ValueError(f"Path does not exist: {path}")

        print(f"Scanning {'file' if path.is_file() else 'directory'}: {args.path}")
        print(f"Including extensions: {', '.join(sorted(extensions))}")
        if exclude_patterns:
            print(f"Excluding patterns: {', '.join(sorted(exclude_patterns))}")
        if exclude_extensions:
            print(f"Excluding extensions: {', '.join(sorted(exclude_extensions))}")

        if path.is_file():
            merged_content = scanner.scan_file(path)
        else:
            merged_content = scanner.scan_directory(
                args.path,
                recursive=not args.no_recursive
            )

        if args.output is not None:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(merged_content)
            print(f"\nSuccess! Output written to: {args.output}")
            print(f"Total characters: {len(merged_content)}")
        elif args.print:
            print(merged_content)
        else:
            print(f"Total characters: {len(merged_content)}")
            print("Use --print to display the output or -o to save to a file")

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
