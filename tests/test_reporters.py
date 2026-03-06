"""
Emare Katip - Birim Testleri: Reporter'lar
=============================================
MarkdownReporter ve JsonReporter testleri.
"""

import pytest
import json

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from models.project import ProjectInfo, ProjectStats
from analyzers.project_analyzer import ProjectAnalyzer
from reporters.markdown_reporter import MarkdownReporter
from reporters.json_reporter import JsonReporter


@pytest.fixture
def sample_projects():
    return [
        ProjectInfo(
            name="test_proj", path="/test",
            primary_language="Python", category="AI / Yapay Zeka",
            maturity="Aktif Geliştirme", description="Test açıklaması",
            stats=ProjectStats(
                total_files=10, code_files=7, total_lines=500,
                total_size_bytes=1024 * 100,
                languages={"Python": 7},
            ),
            frameworks=["Flask"],
            ai_services=["OpenAI"],
            has_git=True,
        ),
    ]


@pytest.fixture
def analyzer(sample_projects):
    return ProjectAnalyzer(sample_projects)


class TestMarkdownReporter:

    def test_generate_creates_files(self, analyzer, tmp_path):
        reporter = MarkdownReporter(analyzer, tmp_path)
        result = reporter.generate()

        assert Path(result).exists()
        assert (tmp_path / "son_rapor.md").exists()

    def test_report_contains_project_name(self, analyzer, tmp_path):
        reporter = MarkdownReporter(analyzer, tmp_path)
        reporter.generate()
        content = (tmp_path / "son_rapor.md").read_text(encoding="utf-8")
        assert "test_proj" in content

    def test_report_contains_sections(self, analyzer, tmp_path):
        reporter = MarkdownReporter(analyzer, tmp_path)
        reporter.generate()
        content = (tmp_path / "son_rapor.md").read_text(encoding="utf-8")
        assert "Genel Özet" in content
        assert "Dil Dağılımı" in content
        assert "Proje Detayları" in content

    def test_report_contains_stats(self, analyzer, tmp_path):
        reporter = MarkdownReporter(analyzer, tmp_path)
        reporter.generate()
        content = (tmp_path / "son_rapor.md").read_text(encoding="utf-8")
        assert "500" in content  # total lines
        assert "Python" in content
        assert "Flask" in content
        assert "OpenAI" in content


class TestJsonReporter:

    def test_generate_creates_files(self, analyzer, tmp_path):
        reporter = JsonReporter(analyzer, tmp_path)
        result = reporter.generate()

        assert Path(result).exists()
        assert (tmp_path / "son_rapor.json").exists()

    def test_valid_json(self, analyzer, tmp_path):
        reporter = JsonReporter(analyzer, tmp_path)
        reporter.generate()
        content = (tmp_path / "son_rapor.json").read_text(encoding="utf-8")
        data = json.loads(content)
        assert isinstance(data, dict)

    def test_json_contains_projects(self, analyzer, tmp_path):
        reporter = JsonReporter(analyzer, tmp_path)
        reporter.generate()
        content = (tmp_path / "son_rapor.json").read_text(encoding="utf-8")
        data = json.loads(content)
        assert "projects" in data
        assert len(data["projects"]) == 1
        assert data["projects"][0]["name"] == "test_proj"

    def test_json_contains_connections(self, analyzer, tmp_path):
        reporter = JsonReporter(analyzer, tmp_path)
        reporter.generate()
        content = (tmp_path / "son_rapor.json").read_text(encoding="utf-8")
        data = json.loads(content)
        assert "connections" in data
        assert "all_frameworks" in data

    def test_json_stats(self, analyzer, tmp_path):
        reporter = JsonReporter(analyzer, tmp_path)
        reporter.generate()
        content = (tmp_path / "son_rapor.json").read_text(encoding="utf-8")
        data = json.loads(content)
        assert data["total_projects"] == 1
        assert data["total_lines"] == 500
