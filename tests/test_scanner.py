import tempfile
from pathlib import Path

import pytest

from codemd import CodeScanner


class TestCodeScanner:
    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            files = {
                'main.py': 'print("Hello")\n',
                'test_main.py': 'def test_hello(): pass\n',
                'lib.java': 'class Library {}\n',
                'debug_utils.py': 'def debug(): pass\n',
                'spec.js': 'describe("test", () => {})\n',
                'subdir/nested.py': 'def nested(): pass\n',
                'venv/lib/site-packages/pkg.py': 'package code\n',
                '__pycache__/cache.pyc': 'cache\n',
            }

            for file_path, content in files.items():
                full_path = Path(tmpdir) / file_path
                full_path.parent.mkdir(exist_ok=True, parents=True)
                full_path.write_text(content)

            yield tmpdir

    def test_init_default_extensions(self):
        scanner = CodeScanner()
        assert 'py' in scanner.extensions
        assert 'java' in scanner.extensions
        assert len(scanner.exclude_patterns) == 0
        assert len(scanner.exclude_extensions) == 0

    def test_init_custom_extensions(self):
        scanner = CodeScanner(extensions={'py', 'rb'})
        assert scanner.extensions == {'py', 'rb'}

    def test_should_include_file(self):
        scanner = CodeScanner(
            extensions={'py', 'java'},
            exclude_patterns={'test_'},
            exclude_extensions={'spec.js'}
        )

        assert scanner.should_include_file(Path('main.py')) == True
        assert scanner.should_include_file(Path('test_main.py')) == False
        assert scanner.should_include_file(Path('lib.java')) == True
        assert scanner.should_include_file(Path('script.rb')) == False
        assert scanner.should_include_file(Path('test.spec.js')) == False

    def test_scan_directory_basic(self, temp_dir):
        scanner = CodeScanner(extensions={'py'})
        content = scanner.scan_directory(temp_dir)

        expected_structure = """# Repository Structure
* debug\_utils.py
* main.py
* **subdir/**
  * nested.py
* test\_main.py"""

        lines = content.split('\n')
        structure_start = lines.index('# Repository Structure')
        structure_end = next(i for i, line in enumerate(lines[structure_start:]) if not line) + structure_start
        actual_structure = '\n'.join(lines[structure_start:structure_end])

        assert actual_structure == expected_structure
        assert '# main.py' in content
        assert 'print("Hello")' in content
        assert '# subdir/nested.py' in content
        assert 'def nested(): pass' in content

    def test_scan_directory_exclusions(self, temp_dir):
        scanner = CodeScanner(
            extensions={'py'},
            exclude_patterns={'test_', 'debug_'}
        )
        content = scanner.scan_directory(temp_dir)

        expected_structure = """# Repository Structure
* main.py
* **subdir/**
  * nested.py"""

        lines = content.split('\n')
        structure_start = lines.index('# Repository Structure')
        structure_end = next(i for i, line in enumerate(lines[structure_start:]) if not line) + structure_start
        actual_structure = '\n'.join(lines[structure_start:structure_end])

        assert actual_structure == expected_structure
        assert '# main.py' in content
        assert 'test_main.py' not in content
        assert 'debug_utils.py' not in content

    def test_scan_directory_no_structure(self, temp_dir):
        scanner = CodeScanner(extensions={'py'})
        scanner.no_structure = True
        content = scanner.scan_directory(temp_dir)

        assert '# Repository Structure' not in content
        assert content.split('\n')[0].startswith('# ')
        assert '.py' in content.split('\n')[0]

    def test_scan_directory_gitignore(self, temp_dir):
        gitignore_content = """
venv/
__pycache__/
*.pyc
"""
        gitignore_path = Path(temp_dir) / '.gitignore'
        gitignore_path.write_text(gitignore_content)

        scanner = CodeScanner(extensions={'py'})
        content = scanner.scan_directory(temp_dir)

        expected_structure = """# Repository Structure
* debug\_utils.py
* main.py
* **subdir/**
  * nested.py
* test\_main.py"""

        lines = content.split('\n')
        structure_start = lines.index('# Repository Structure')
        structure_end = next(i for i, line in enumerate(lines[structure_start:]) if not line) + structure_start
        actual_structure = '\n'.join(lines[structure_start:structure_end])

        assert actual_structure == expected_structure
        assert 'venv' not in content
        assert '__pycache__' not in content
        assert '.pyc' not in content

    def test_scan_directory_custom_gitignore(self, temp_dir):
        custom_ignore = """
*.py
!main.py
!nested.py
"""
        custom_ignore_path = Path(temp_dir) / '.custom-ignore'
        custom_ignore_path.write_text(custom_ignore)

        scanner = CodeScanner(
            extensions={'py'},
            gitignore_files=[str(custom_ignore_path)]
        )
        content = scanner.scan_directory(temp_dir)

        expected_structure = """# Repository Structure
* main.py
* **subdir/**
  * nested.py"""

        lines = content.split('\n')
        structure_start = lines.index('# Repository Structure')
        structure_end = next(i for i, line in enumerate(lines[structure_start:]) if not line) + structure_start
        actual_structure = '\n'.join(lines[structure_start:structure_end])

        assert actual_structure == expected_structure
        assert 'test_main.py' not in content
        assert 'debug_utils.py' not in content

    def test_scan_directory_invalid_path(self):
        scanner = CodeScanner()
        with pytest.raises(ValueError):
            scanner.scan_directory('/nonexistent/path')

    def test_scan_directory_encoding_error(self, temp_dir):
        bad_file = Path(temp_dir) / 'bad.py'
        with open(bad_file, 'wb') as f:
            f.write(b'\x80invalid')

        scanner = CodeScanner()
        content = scanner.scan_directory(temp_dir)

        assert '# main.py' in content
        assert 'bad.py' in content
        assert b'\x80invalid' not in content.encode()
