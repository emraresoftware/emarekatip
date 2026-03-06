"""
Emare Katip - Birim Testleri: Scanner
=======================================
Scanner sınıfının metotlarını test eder.
"""

import pytest
import tempfile
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from scanner import Scanner
from models.project import FileInfo, ProjectStats


@pytest.fixture
def scanner():
    """Test Scanner instance'ı."""
    return Scanner(root=Path(tempfile.mkdtemp()))


@pytest.fixture
def mock_project(tmp_path):
    """Geçici dizinde sahte Python projesi oluşturur."""
    proj = tmp_path / "test_project"
    proj.mkdir()
    (proj / "main.py").write_text("print('hello')\nprint('world')\n", encoding="utf-8")
    (proj / "utils.py").write_text("def helper():\n    pass\n", encoding="utf-8")
    (proj / "requirements.txt").write_text("flask==2.0\nopenai==1.0\n", encoding="utf-8")
    (proj / "README.md").write_text("# Test Project\nBu bir test projesidir.\n", encoding="utf-8")
    (proj / "config.json").write_text('{"key": "value"}', encoding="utf-8")
    (proj / "data.csv").write_text("a,b,c\n1,2,3\n", encoding="utf-8")
    return proj


@pytest.fixture
def mock_node_project(tmp_path):
    """Geçici dizinde sahte Node.js projesi oluşturur."""
    proj = tmp_path / "node_app"
    proj.mkdir()
    (proj / "index.js").write_text("console.log('hello');\n", encoding="utf-8")
    (proj / "package.json").write_text('{"name": "test", "dependencies": {"express": "4.0"}}', encoding="utf-8")
    return proj


@pytest.fixture
def mock_empty_project(tmp_path):
    """Boş proje klasörü."""
    proj = tmp_path / "empty_project"
    proj.mkdir()
    return proj


class TestScannerExclusion:
    """Hariç tutma kuralları testleri."""

    def test_dotfile_excluded(self, scanner):
        assert scanner.is_excluded(".git") is True

    def test_dotds_store_excluded(self, scanner):
        assert scanner.is_excluded(".DS_Store") is True

    def test_node_modules_excluded(self, scanner):
        assert scanner.is_excluded("node_modules") is True

    def test_pycache_excluded(self, scanner):
        assert scanner.is_excluded("__pycache__") is True

    def test_normal_dir_not_excluded(self, scanner):
        assert scanner.is_excluded("my_project") is False

    def test_vendor_excluded(self, scanner):
        assert scanner.is_excluded("vendor") is True


class TestProjectTypeDetection:
    """Proje türü tespit testleri."""

    def test_python_project(self, scanner, mock_project):
        result = scanner.detect_project_type(mock_project)
        assert result == "python"

    def test_node_project(self, scanner, mock_node_project):
        result = scanner.detect_project_type(mock_node_project)
        assert result == "nodejs"

    def test_empty_project_general(self, scanner, mock_empty_project):
        result = scanner.detect_project_type(mock_empty_project)
        assert result == "general"

    def test_laravel_project(self, scanner, tmp_path):
        proj = tmp_path / "laravel_app"
        proj.mkdir()
        (proj / "artisan").write_text("#!/usr/bin/env php\n", encoding="utf-8")
        (proj / "composer.json").write_text("{}", encoding="utf-8")
        result = scanner.detect_project_type(proj)
        assert result == "php_laravel"

    def test_rust_project(self, scanner, tmp_path):
        proj = tmp_path / "rust_app"
        proj.mkdir()
        (proj / "Cargo.toml").write_text("[package]\nname='test'\n", encoding="utf-8")
        result = scanner.detect_project_type(proj)
        assert result == "rust"


class TestFileCategories:
    """Dosya kategorizasyon testleri."""

    def test_code_files(self, scanner):
        assert scanner.categorize_file(".py") == "code"
        assert scanner.categorize_file(".js") == "code"
        assert scanner.categorize_file(".ts") == "code"
        assert scanner.categorize_file(".php") == "code"
        assert scanner.categorize_file(".rs") == "code"
        assert scanner.categorize_file(".go") == "code"

    def test_doc_files(self, scanner):
        assert scanner.categorize_file(".md") == "doc"
        assert scanner.categorize_file(".txt") == "doc"
        assert scanner.categorize_file(".rst") == "doc"

    def test_config_files(self, scanner):
        assert scanner.categorize_file(".json") == "config"
        assert scanner.categorize_file(".yaml") == "config"
        assert scanner.categorize_file(".yml") == "config"
        assert scanner.categorize_file(".toml") == "config"

    def test_data_files(self, scanner):
        assert scanner.categorize_file(".csv") == "data"
        assert scanner.categorize_file(".sql") == "data"
        assert scanner.categorize_file(".db") == "data"

    def test_unknown_files(self, scanner):
        assert scanner.categorize_file(".xyz") == "other"
        assert scanner.categorize_file(".abc") == "other"


class TestLanguageDetection:
    """Dil tespit testleri."""

    def test_known_languages(self, scanner):
        assert scanner.get_language(".py") == "Python"
        assert scanner.get_language(".js") == "JavaScript"
        assert scanner.get_language(".ts") == "TypeScript"
        assert scanner.get_language(".rs") == "Rust"

    def test_unknown_language(self, scanner):
        assert scanner.get_language(".xyz") == "Diğer"


class TestLineCounter:
    """Satır sayma testleri."""

    def test_count_lines(self, scanner, tmp_path):
        f = tmp_path / "test.py"
        f.write_text("line1\nline2\nline3\n", encoding="utf-8")
        assert scanner.count_lines(f) == 3

    def test_empty_file(self, scanner, tmp_path):
        f = tmp_path / "empty.py"
        f.write_text("", encoding="utf-8")
        assert scanner.count_lines(f) == 0

    def test_nonexistent_file(self, scanner):
        result = scanner.count_lines(Path("/nonexistent/file.py"))
        assert result == 0


class TestDirectoryScanning:
    """Dizin tarama testleri."""

    def test_scan_mock_project(self, scanner, mock_project):
        files, dir_count = scanner.scan_directory(mock_project)
        assert len(files) > 0
        file_names = [f.name for f in files]
        assert "main.py" in file_names
        assert "utils.py" in file_names
        assert "README.md" in file_names

    def test_scan_empty_project(self, scanner, mock_empty_project):
        files, dir_count = scanner.scan_directory(mock_empty_project)
        assert len(files) == 0
        assert dir_count == 0


class TestBuildStats:
    """İstatistik oluşturma testleri."""

    def test_build_stats(self, scanner):
        files = [
            FileInfo(path="/a/main.py", name="main.py", extension=".py",
                     size_bytes=100, language="Python", line_count=10, category="code"),
            FileInfo(path="/a/utils.py", name="utils.py", extension=".py",
                     size_bytes=200, language="Python", line_count=20, category="code"),
            FileInfo(path="/a/README.md", name="README.md", extension=".md",
                     size_bytes=50, language="Markdown", line_count=5, category="doc"),
            FileInfo(path="/a/config.json", name="config.json", extension=".json",
                     size_bytes=30, language="JSON", line_count=3, category="config"),
        ]
        stats = scanner.build_stats(files, 2)
        assert stats.total_files == 4
        assert stats.total_dirs == 2
        assert stats.code_files == 2
        assert stats.doc_files == 1
        assert stats.config_files == 1
        assert stats.total_lines == 38
        assert stats.languages == {"Python": 2}
        assert stats.largest_file == "utils.py"
        assert stats.largest_file_lines == 20


class TestReadmeSummary:
    """README özet çıkarma testleri."""

    def test_extract_readme(self, scanner, mock_project):
        summary = scanner.extract_readme_summary(mock_project)
        assert "Test Project" in summary
        assert len(summary) > 0

    def test_no_readme(self, scanner, mock_empty_project):
        summary = scanner.extract_readme_summary(mock_empty_project)
        assert summary == ""


class TestFeatureDetection:
    """Özellik tespit testleri."""

    def test_detect_frameworks(self, scanner, mock_project):
        files, _ = scanner.scan_directory(mock_project)
        features = scanner.detect_features(mock_project, files)
        assert "Flask" in features["frameworks"]
        assert "OpenAI" in features["ai_services"]
        assert "requirements.txt" in features["dependencies"]

    def test_detect_git(self, scanner, tmp_path):
        proj = tmp_path / "git_project"
        proj.mkdir()
        (proj / ".git").mkdir()
        (proj / "main.py").write_text("pass\n", encoding="utf-8")
        files, _ = scanner.scan_directory(proj)
        features = scanner.detect_features(proj, files)
        assert features["has_git"] is True


class TestCategoryClassification:
    """Kategori sınıflandırma testleri."""

    def test_ai_project(self, scanner):
        features = {"ai_services": ["OpenAI"], "frameworks": []}
        assert scanner.classify_category("python", features, "Some project") == "AI / Yapay Zeka"

    def test_ai_bot(self, scanner):
        features = {"ai_services": ["OpenAI"], "frameworks": []}
        assert scanner.classify_category("python", features, "WhatsApp bot") == "AI Bot"

    def test_ai_assistant(self, scanner):
        features = {"ai_services": ["Gemini"], "frameworks": []}
        assert scanner.classify_category("python", features, "Kişisel asistan") == "AI Asistan"

    def test_web_app(self, scanner):
        features = {"ai_services": [], "frameworks": ["Laravel"]}
        assert scanner.classify_category("php_laravel", features, "CRM") == "Web Uygulama"

    def test_system_project(self, scanner):
        features = {"ai_services": [], "frameworks": []}
        assert scanner.classify_category("rust", features, "OS kernel") == "Sistem"

    def test_general_project(self, scanner):
        features = {"ai_services": [], "frameworks": []}
        assert scanner.classify_category("general", features, "Just stuff") == "Genel"


class TestMaturityEstimation:
    """Olgunluk seviyesi tahmin testleri."""

    def test_empty(self, scanner):
        stats = ProjectStats(total_files=0)
        assert scanner.estimate_maturity(stats, {}) == "Boş"

    def test_early_stage(self, scanner):
        stats = ProjectStats(total_files=2, code_files=1, total_lines=50)
        assert scanner.estimate_maturity(stats, {}) == "Erken Aşama"

    def test_production_ready(self, scanner):
        stats = ProjectStats(total_files=20, code_files=15, total_lines=5000)
        features = {"has_tests": True, "has_ci": True}
        assert scanner.estimate_maturity(stats, features) == "Üretim Hazır"

    def test_active_development(self, scanner):
        stats = ProjectStats(total_files=20, code_files=15, total_lines=5000)
        assert scanner.estimate_maturity(stats, {}) == "Aktif Geliştirme"

    def test_developing(self, scanner):
        stats = ProjectStats(total_files=8, code_files=7, total_lines=500)
        assert scanner.estimate_maturity(stats, {}) == "Geliştiriliyor"

    def test_prototype(self, scanner):
        stats = ProjectStats(total_files=5, code_files=4, total_lines=300)
        assert scanner.estimate_maturity(stats, {}) == "Prototip"
