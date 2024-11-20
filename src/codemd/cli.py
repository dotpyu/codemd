import argparse
import platform
import subprocess
import sys
from pathlib import Path
from typing import Set, Tuple

from .scanner import CodeScanner

try:
    import tiktoken

    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False

BANNER = r"""
   ___             _                    ___ 
  / __\  ___    __| |  ___    /\/\     /   \
 / /    / _ \  / _` | / _ \  /    \   / /\ /
/ /___ | (_) || (_| ||  __/ / /\/\ \ / /_// 
\____/  \___/  \__,_| \___| \/    \//___,' 
"""

EPILOG = """
Examples:
  # Basic usage (file or directory, no output by default)
  codemd /path/to/code
  codemd /path/to/file.py

  # Print output to stdout
  codemd /path/to/code --print
  codemd /path/to/file.py --print

  # Custom extensions
  codemd /path/to/code -e py,java,sql

  # Save to file
  codemd /path/to/code -o output.md

  # Exclude patterns and specific files
  codemd /path/to/code --exclude-patterns test_,debug_ --exclude-extensions test.py,spec.js

  # Non-recursive scan with custom output
  codemd /path/to/code --no-recursive -o custom.md

  # Disable structure output (auto-disabled for single files)
  codemd /path/to/code --no-structure

  # Use specific gitignore files
  codemd /path/to/code --gitignore .gitignore .custom-ignore

  # Disable gitignore processing
  codemd /path/to/code --ignore-gitignore

  # Process single file and print output
  codemd /path/to/script.py --print -o script.md
"""


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog='codemd',
        description='Transform code repositories or files into markdown-formatted strings ready for LLM prompting',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=EPILOG
    )

    parser.add_argument('path', type=str, help='File or directory to scan')
    parser.add_argument('-e', '--extensions', type=str, default=None,
                        help='Comma-separated list of file extensions to include (without dots)')
    parser.add_argument('--exclude-patterns', type=str, default='',
                        help='Comma-separated list of patterns to exclude (e.g., test_,debug_)')
    parser.add_argument('--exclude-extensions', type=str, default='',
                        help='Comma-separated list of file patterns to exclude (e.g., test.py,spec.js)')
    parser.add_argument('-o', '--output', type=str, default=None,
                        help='Output file path (if not specified, prints to stdout)')
    parser.add_argument('--no-recursive', action='store_true',
                        help='Disable recursive directory scanning')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Enable verbose output')
    parser.add_argument('--no-structure', action='store_true',
                        help='Disable repository structure output')
    parser.add_argument('--print', action='store_true',
                        help='Print the markdown output (disabled by default)')

    parser.add_argument(
        '--gitignore',
        type=str,
        nargs='+',
        help='Specify one or more .gitignore files to use'
    )

    parser.add_argument(
        '--ignore-gitignore',
        action='store_true',
        help='Disable .gitignore processing'
    )

    return parser.parse_args()


def str_to_set(s: str) -> Set[str]:
    """Convert comma-separated string to set of strings."""
    if s is None: return None
    return {item.strip() for item in s.split(',') if item.strip()}


def copy_to_clipboard(text: str) -> bool:
    """
    Copy text to system clipboard. Works on Windows, macOS, and Linux.
    Returns True if successful, False otherwise.
    """
    platform_system = platform.system().lower()

    try:
        if platform_system == 'darwin':  # macOS
            process = subprocess.Popen(
                ['pbcopy'],
                stdin=subprocess.PIPE,
                close_fds=True
            )
            process.communicate(text.encode('utf-8'))
            return True

        elif platform_system == 'linux':
            try:
                process = subprocess.Popen(
                    ['xclip', '-selection', 'clipboard'],
                    stdin=subprocess.PIPE,
                    close_fds=True
                )
                process.communicate(text.encode('utf-8'))
                return True
            except FileNotFoundError:
                try:
                    process = subprocess.Popen(
                        ['xsel', '--clipboard', '--input'],
                        stdin=subprocess.PIPE,
                        close_fds=True
                    )
                    process.communicate(text.encode('utf-8'))
                    return True
                except FileNotFoundError:
                    return False

        elif platform_system == 'windows':
            process = subprocess.Popen(
                ['powershell', '-command', 'Set-Clipboard'],
                stdin=subprocess.PIPE,
                close_fds=True
            )
            process.communicate(text.encode('utf-8'))
            return True

        return False
    except Exception:
        return False


def prompt_for_copy(text: str) -> None:
    """Prompt user to copy content to clipboard."""
    try:
        response = input("\nWould you like to copy the content to clipboard? [y/N] ").lower().strip()
        if response and response[0] == 'y':
            if copy_to_clipboard(text):
                print("Content copied to clipboard!")
            else:
                system = platform.system()
                if system == 'Linux':
                    print("Error: Could not copy to clipboard. Please install xclip or xsel:")
                    print("  Ubuntu/Debian: sudo apt-get install xclip")
                    print("  Fedora: sudo dnf install xclip")
                    print("  Arch: sudo pacman -S xclip")
                else:
                    print("Error: Could not copy to clipboard.")
    except KeyboardInterrupt:
        print("\nSkipping clipboard copy.")
    except Exception:
        print("Error: Could not copy to clipboard.")


def estimate_tokens(text: str) -> Tuple[int, str]:
    """
    Estimate the number of tokens in the text using different models.
    Returns tuple of (token_count, model_name) or (0, "unavailable") if tiktoken is not installed.
    """
    if not TIKTOKEN_AVAILABLE:
        return 0, "unavailable"
    try:
        encoder = tiktoken.get_encoding("cl100k_base")
        tokens = len(encoder.encode(text, disallowed_special=()))
        return tokens, "GPT-4"
    except Exception:
        try:
            encoder = tiktoken.get_encoding("p50k_base")
            tokens = len(encoder.encode(text), disallowed_special=())
            return tokens, "GPT-3.5"
        except Exception:
            return 0, "error"


def format_token_info(token_count: int, model_name: str) -> str:
    """Format token count information. TODO: add cost estimates; load default model from .cfg."""
    if model_name == "unavailable":
        return "\nNote: Install 'tiktoken' for token estimation: pip install tiktoken"
    elif model_name == "error":
        return "\nError: Could not estimate tokens"

    info = [f"\nEstimated tokens: {token_count:,} ({model_name} encoding)"]

    return "\n".join(info)


def main() -> int:
    print(BANNER)
    print("Version 0.0.3b")
    print("Transform your code into LLM-ready prompts and automatically copy them to your clipboard!\n")

    try:
        args = parse_arguments()
        path = Path(args.path)
        output_file = Path(args.output) if args.output else None

        if not path.exists():
            print(f"Error: Path '{path}' does not exist", file=sys.stderr)
            return 1

        extensions = str_to_set(args.extensions)
        exclude_patterns = str_to_set(args.exclude_patterns)
        exclude_extensions = str_to_set(args.exclude_extensions)

        scanner = CodeScanner(
            extensions=extensions,
            exclude_patterns=exclude_patterns,
            exclude_extensions=exclude_extensions,
            gitignore_files=args.gitignore,
            ignore_gitignore=args.ignore_gitignore
        )

        scanner.no_structure = args.no_structure or path.is_file()

        try:
            if path.is_file():
                content = scanner.scan_file(path)
            else:
                content = scanner.scan_directory(
                    path,
                    recursive=not args.no_recursive
                )
        except Exception as e:
            print(f"Error scanning path: {str(e)}", file=sys.stderr)
            return 1

        files = content.count('```') // 2
        chars = len(content)
        tokens, model = estimate_tokens(content)
        token_info = format_token_info(tokens, model)

        if output_file:
            try:
                output_file.parent.mkdir(parents=True, exist_ok=True)
                output_file.write_text(content, encoding='utf-8')
                print(f"\nSuccess! Processed {files} files ({chars:,} characters)")
                print(f"Output written to: {output_file}")
                print(token_info)
                prompt_for_copy(content)
            except Exception as e:
                print(f"Error writing output file: {str(e)}", file=sys.stderr)
                return 1
        else:
            if args.verbose:
                print(f"\nProcessed {files} files ({chars:,} characters)")
                print(token_info + "\n")
            if args.print:  # Only print content if --print flag is set
                print(content)
            print(token_info)
            prompt_for_copy(content)

        return 0

    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Unexpected error: {str(e)}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
