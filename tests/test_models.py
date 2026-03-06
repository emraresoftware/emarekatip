"""
Emare Katip - Birim Testleri: Veri Modelleri
===============================================
ProjectInfo, ProjectStats, FileInfo, KingstonReport testleri.
"""

import pytest
from datetime import datetime

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from models.project import FileInfo, ProjectStats, ProjectInfo, KingstonReport


class TestFileInfo:
    """FileInfo dataclass testleri."""

    def test_creation(self):
        fi = FileInfo(path="/a/b.py", name="b.py", extension=".py", size_bytes=100)
        assert fi.path == "/a/b.py"
        assert fi.name == "b.py"
        assert fi.language == "Bilinmeyen"
        assert fi.line_count == 0
        assert fi.category == "other"

    def test_with_all_fields(self):
        fi = FileInfo(
            path="/x/y.js", name="y.js", extension=".js",
            size_bytes=500, language="JavaScript",
            line_count=42, category="code",
            last_modified="2026-01-01T00:00:00",
        )
        assert fi.language == "JavaScript"
        assert fi.line_count == 42
        assert fi.category == "code"


class TestProjectStats:
    """ProjectStats dataclass testleri."""

    def test_defaults(self):
        stats = ProjectStats()
        assert stats.total_files == 0
        assert stats.total_lines == 0
        assert stats.languages == {}
        assert stats.largest_file is None

    def test_with_values(self):
        stats = ProjectStats(
            total_files=10, code_files=7,
            total_lines=1000, languages={"Python": 5, "JS": 2},
            largest_file="big.py", largest_file_lines=500,
        )
        assert stats.total_files == 10
        assert stats.code_files == 7
        assert stats.languages["Python"] == 5


class TestProjectInfo:
    """ProjectInfo dataclass testleri."""

    def test_creation(self):
        pi = ProjectInfo(name="test", path="/test")
        assert pi.name == "test"
        assert pi.project_type == "Bilinmeyen"
        assert pi.has_git is False
        assert pi.frameworks == []
        assert pi.ai_services == []
        assert pi.git_info == {}

    def test_total_size_mb(self):
        stats = ProjectStats(total_size_bytes=5 * 1024 * 1024)
        pi = ProjectInfo(name="test", path="/test", stats=stats)
        assert pi.total_size_mb == 5.0

    def test_total_size_mb_zero(self):
        pi = ProjectInfo(name="test", path="/test")
        assert pi.total_size_mb == 0.0

    def test_to_dict(self):
        stats = ProjectStats(
            total_files=5, total_lines=200,
            code_files=3, languages={"Python": 3},
        )
        pi = ProjectInfo(
            name="myproj", path="/myproj",
            project_type="python", primary_language="Python",
            category="AI / Yapay Zeka", maturity="Aktif Geliştirme",
            frameworks=["Flask"], ai_services=["OpenAI"],
            has_git=True, stats=stats,
            git_info={"total_commits": 42},
        )
        d = pi.to_dict()
        assert d["name"] == "myproj"
        assert d["project_type"] == "python"
        assert d["stats"]["total_files"] == 5
        assert d["stats"]["code_files"] == 3
        assert d["frameworks"] == ["Flask"]
        assert d["ai_services"] == ["OpenAI"]
        assert d["has_git"] is True
        assert d["git_info"]["total_commits"] == 42

    def test_to_dict_file_categories(self):
        stats = ProjectStats(code_files=3, doc_files=2, config_files=1, data_files=0)
        pi = ProjectInfo(name="t", path="/t", stats=stats)
        d = pi.to_dict()
        assert d["file_count_by_category"]["code"] == 3
        assert d["file_count_by_category"]["doc"] == 2


class TestKingstonReport:
    """KingstonReport dataclass testleri."""

    def test_defaults(self):
        report = KingstonReport()
        assert report.total_projects == 0
        assert report.total_files == 0
        assert report.projects == []
        assert report.language_distribution == {}

    def test_to_dict(self):
        report = KingstonReport(
            total_projects=5, total_files=100,
            total_size_mb=50.0, total_lines=10000,
            language_distribution={"Python": 60, "JS": 30},
            ai_services_used=["OpenAI"],
        )
        d = report.to_dict()
        assert d["total_projects"] == 5
        assert d["total_files"] == 100
        assert d["language_distribution"]["Python"] == 60
        assert "OpenAI" in d["ai_services_used"]
