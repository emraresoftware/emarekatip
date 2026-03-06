"""
Emare Katip - Birim Testleri: Proje Analizcisi
=================================================
ProjectAnalyzer sınıfı testleri.
"""

import pytest

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from models.project import ProjectInfo, ProjectStats
from analyzers.project_analyzer import ProjectAnalyzer


@pytest.fixture
def sample_projects():
    """Örnek proje listesi."""
    return [
        ProjectInfo(
            name="ghosty", path="/ghosty",
            primary_language="Python", category="AI / Yapay Zeka",
            maturity="Aktif Geliştirme",
            stats=ProjectStats(
                total_files=100, code_files=60, total_lines=8000,
                total_size_bytes=5 * 1024 * 1024,
                languages={"Python": 50, "JavaScript": 10},
            ),
            frameworks=["Flask", "Streamlit"],
            ai_services=["OpenAI", "Google Gemini"],
        ),
        ProjectInfo(
            name="Emare Finance", path="/emare_finance",
            primary_language="PHP", category="Web Uygulama",
            maturity="Aktif Geliştirme",
            stats=ProjectStats(
                total_files=200, code_files=150, total_lines=15000,
                total_size_bytes=10 * 1024 * 1024,
                languages={"PHP": 120, "JavaScript": 20, "Python": 10},
            ),
            frameworks=["Laravel", "Vite"],
            ai_services=["OpenAI"],
        ),
        ProjectInfo(
            name="Emare os", path="/emare_os",
            primary_language="Rust", category="Sistem",
            maturity="Erken Aşama",
            stats=ProjectStats(
                total_files=10, code_files=5, total_lines=500,
                total_size_bytes=100 * 1024,
                languages={"Rust": 5},
            ),
            frameworks=["Rust/Cargo"],
            ai_services=[],
        ),
        ProjectInfo(
            name="whatsapp asistan", path="/whatsapp",
            primary_language="Python", category="AI Bot",
            maturity="Prototip",
            stats=ProjectStats(
                total_files=8, code_files=4, total_lines=300,
                total_size_bytes=50 * 1024,
                languages={"Python": 4},
            ),
            frameworks=[],
            ai_services=["Google Gemini"],
        ),
    ]


@pytest.fixture
def analyzer(sample_projects):
    return ProjectAnalyzer(sample_projects)


class TestLanguageDistribution:
    def test_distribution(self, analyzer):
        dist = analyzer.get_language_distribution()
        assert "Python" in dist
        assert "PHP" in dist
        assert dist["Python"] == 64  # 50 + 10 + 4
        assert dist["PHP"] == 120

    def test_sorted_by_count(self, analyzer):
        dist = analyzer.get_language_distribution()
        values = list(dist.values())
        assert values == sorted(values, reverse=True)


class TestCategoryDistribution:
    def test_distribution(self, analyzer):
        dist = analyzer.get_category_distribution()
        assert dist["AI / Yapay Zeka"] == 1
        assert dist["Web Uygulama"] == 1
        assert dist["Sistem"] == 1
        assert dist["AI Bot"] == 1

    def test_total_count(self, analyzer, sample_projects):
        dist = analyzer.get_category_distribution()
        assert sum(dist.values()) == len(sample_projects)


class TestAIServices:
    def test_all_services(self, analyzer):
        services = analyzer.get_all_ai_services()
        assert "OpenAI" in services
        assert "Google Gemini" in services
        assert len(services) == 2

    def test_sorted(self, analyzer):
        services = analyzer.get_all_ai_services()
        assert services == sorted(services)


class TestFrameworks:
    def test_all_frameworks(self, analyzer):
        frameworks = analyzer.get_all_frameworks()
        assert "Flask" in frameworks
        assert "Laravel" in frameworks
        assert "Rust/Cargo" in frameworks

    def test_no_duplicates(self, analyzer):
        frameworks = analyzer.get_all_frameworks()
        assert len(frameworks) == len(set(frameworks))


class TestProjectGrouping:
    def test_by_category(self, analyzer):
        groups = analyzer.get_projects_by_category()
        assert "AI / Yapay Zeka" in groups
        assert len(groups["AI / Yapay Zeka"]) == 1

    def test_by_language(self, analyzer):
        groups = analyzer.get_projects_by_language()
        assert "Python" in groups
        assert len(groups["Python"]) == 2  # ghosty + whatsapp


class TestLargestProjects:
    def test_top_2(self, analyzer):
        top = analyzer.get_largest_projects(2)
        assert len(top) == 2
        assert top[0].name == "Emare Finance"  # 15000 lines
        assert top[1].name == "ghosty"  # 8000 lines

    def test_top_all(self, analyzer, sample_projects):
        top = analyzer.get_largest_projects(100)
        assert len(top) == len(sample_projects)


class TestConnections:
    def test_shared_ai_service(self, analyzer):
        connections = analyzer.find_connections()
        ai_conns = [c for c in connections if c["type"] == "shared_ai_service"]
        assert len(ai_conns) > 0
        # OpenAI ve Google Gemini paylaşılıyor
        openai_conn = [c for c in ai_conns if c.get("service") == "OpenAI"]
        assert len(openai_conn) == 1
        assert "ghosty" in openai_conn[0]["projects"]
        assert "Emare Finance" in openai_conn[0]["projects"]

    def test_emare_family(self, analyzer):
        connections = analyzer.find_connections()
        family_conns = [c for c in connections if c["type"] == "project_family"]
        assert len(family_conns) == 1
        assert "Emare" in family_conns[0]["family"]


class TestGenerateReport:
    def test_report_totals(self, analyzer, sample_projects):
        report = analyzer.generate_report()
        assert report.total_projects == 4
        assert report.total_files == 318
        assert report.total_lines == 23800

    def test_report_ai_services(self, analyzer):
        report = analyzer.generate_report()
        assert "OpenAI" in report.ai_services_used

    def test_report_languages(self, analyzer):
        report = analyzer.generate_report()
        assert "Python" in report.language_distribution
