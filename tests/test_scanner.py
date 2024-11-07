import pytest
from pathlib import Path
from codemd import CodeScanner
import tempfile


class TestCodeScanner:
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory with some test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create some test files
            files = {
                'main.py': 'print("Hello")\n',
                'test_main.py': 'def test_hello(): pass\n',
                'lib.java': 'class Library {}\n',
                'debug_utils.py': 'def debug(): pass\n',
                'spec.js': 'describe("test", () => {})\n',
                'subdir/nested.py': 'def nested(): pass\n',
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

        assert '# main.py' in content
        assert 'test_main.py' not in content
        assert 'debug_utils.py' not in content

    def test_scan_directory_non_recursive(self, temp_dir):
        scanner = CodeScanner(extensions={'py'})
        content = scanner.scan_directory(temp_dir, recursive=False)

        assert '# main.py' in content
        assert 'nested.py' not in content

    def test_scan_directory_invalid_path(self):
        scanner = CodeScanner()
        with pytest.raises(ValueError):
            scanner.scan_directory('/nonexistent/path')

    def test_scan_directory_encoding_error(self, temp_dir):
        # Create a file with invalid encoding
        bad_file = Path(temp_dir) / 'bad.py'
        with open(bad_file, 'wb') as f:
            f.write(b'\x80invalid')

        scanner = CodeScanner()
        content = scanner.scan_directory(temp_dir)
        assert '# main.py' in content