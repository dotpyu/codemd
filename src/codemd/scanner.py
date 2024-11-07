import argparse
import sys
from pathlib import Path
from typing import Set, Optional


class CodeScanner:
    def __init__(self,
                 extensions: Optional[Set[str]] = None,
                 exclude_patterns: Optional[Set[str]] = None,
                 exclude_extensions: Optional[Set[str]] = None):
        """
        Initialize the CodeScanner with optional file extensions to filter.

        Args:
            extensions: Set of file extensions to include (without dots), e.g. {'py', 'java'}
            exclude_patterns: Set of filename patterns to exclude, e.g. {'test_', 'debug_'}
            exclude_extensions: Set of file extensions to exclude (without dots), e.g. {'test.py', 'spec.js'}
        """
        self.extensions = extensions or {'py', 'java', 'js', 'cpp', 'c', 'h', 'hpp'}
        self.exclude_patterns = exclude_patterns or set()
        self.exclude_extensions = exclude_extensions or set()

    def should_include_file(self, file_path: Path) -> bool:
        """
        Check if a file should be included based on extensions and exclusion patterns.
        """
        if file_path.suffix.lstrip('.') not in self.extensions:
            return False

        for pattern in self.exclude_patterns:
            if pattern in str(file_path):
                return False

        for ext_pattern in self.exclude_extensions:
            if str(file_path).endswith(ext_pattern):
                return False

        return True

    def scan_directory(self, directory: str, recursive: bool = True) -> str:
        """
        Scan a directory for code files and merge them into a markdown-formatted string.

        Args:
            directory: Path to the directory to scan
            recursive: Whether to scan subdirectories recursively

        Returns:
            A markdown-formatted string containing all code files
        """
        directory_path = Path(directory)
        if not directory_path.exists():
            raise ValueError(f"Directory {directory} does not exist")

        merged_content = []

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


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Scan directory for code files and create a markdown-formatted output'
    )
    parser.add_argument(
        'directory',
        help='Directory to scan'
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
        help='Output file path (defaults to print out unless specified)',
        default=None,
    )
    parser.add_argument(
        '--no-recursive',
        action='store_true',
        help='Disable recursive directory scanning'
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

        print(f"Scanning directory: {args.directory}")
        print(f"Including extensions: {', '.join(sorted(extensions))}")
        if exclude_patterns:
            print(f"Excluding patterns: {', '.join(sorted(exclude_patterns))}")
        if exclude_extensions:
            print(f"Excluding extensions: {', '.join(sorted(exclude_extensions))}")

        merged_content = scanner.scan_directory(
            args.directory,
            recursive=not args.no_recursive
        )

        if args.output is not None:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(merged_content)
            print(f"\nSuccess! Output written to: {args.output}")
            print(f"Total characters: {len(merged_content)}")
        else:
            print(merged_content)


    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
