"""ScanComparator (diff_analyzer) testleri."""

import json
import pytest
from pathlib import Path
from analyzers.diff_analyzer import ScanComparator, ScanDiff, ProjectDiff


# ── Fixtures ──────────────────────────────────────────────────

def _make_scan(projects, date="2025-06-01T10:00:00"):
    return {
        "scan_date": date,
        "scan_root": "/Volumes/KINGSTON",
        "project_count": len(projects),
        "projects": projects,
    }


def _make_project(name, lines=100, files=5, size_mb=1.0, category="Genel", maturity="Aktif"):
    return {
        "name": name,
        "path": f"/Volumes/KINGSTON/{name}",
        "project_type": "python",
        "primary_language": "Python",
        "category": category,
        "maturity": maturity,
        "stats": {
            "total_lines": lines,
            "total_files": files,
            "total_size_mb": size_mb,
        },
    }


@pytest.fixture
def tmp_data_dir(tmp_path):
    return tmp_path


@pytest.fixture
def comparator(tmp_data_dir):
    return ScanComparator(data_dir=tmp_data_dir)


# ── ProjectDiff testleri ────────────────────────────────────

class TestProjectDiff:
    def test_line_diff(self):
        pd = ProjectDiff(name="a", status="changed", old_lines=100, new_lines=150)
        assert pd.line_diff == 50

    def test_file_diff(self):
        pd = ProjectDiff(name="a", status="changed", old_files=5, new_files=8)
        assert pd.file_diff == 3

    def test_size_diff_mb(self):
        pd = ProjectDiff(name="a", status="changed", old_size_mb=1.5, new_size_mb=2.3)
        assert pd.size_diff_mb == 0.8

    def test_line_growth_pct_normal(self):
        pd = ProjectDiff(name="a", status="changed", old_lines=100, new_lines=150)
        assert pd.line_growth_pct == 50.0

    def test_line_growth_pct_from_zero(self):
        pd = ProjectDiff(name="a", status="new", old_lines=0, new_lines=200)
        assert pd.line_growth_pct == 100.0

    def test_line_growth_pct_zero_to_zero(self):
        pd = ProjectDiff(name="a", status="unchanged", old_lines=0, new_lines=0)
        assert pd.line_growth_pct == 0.0


# ── ScanComparator testleri ─────────────────────────────────

class TestScanComparator:
    def test_list_scans_empty(self, comparator):
        assert comparator.list_scans() == []

    def test_list_scans_sorted(self, comparator, tmp_data_dir):
        (tmp_data_dir / "scan_20250601_100000.json").write_text("{}")
        (tmp_data_dir / "scan_20250602_100000.json").write_text("{}")
        (tmp_data_dir / "scan_20250603_100000.json").write_text("{}")
        scans = comparator.list_scans()
        assert len(scans) == 3
        assert scans[0].name < scans[1].name < scans[2].name

    def test_load_scan_valid(self, comparator, tmp_data_dir):
        scan_file = tmp_data_dir / "scan_test.json"
        scan_file.write_text(json.dumps({"projects": []}))
        data = comparator.load_scan(scan_file)
        assert data is not None
        assert "projects" in data

    def test_load_scan_invalid_json(self, comparator, tmp_data_dir):
        bad_file = tmp_data_dir / "bad.json"
        bad_file.write_text("{invalid")
        assert comparator.load_scan(bad_file) is None

    def test_compare_new_project(self, comparator, tmp_data_dir):
        old = _make_scan([_make_project("A", lines=100)])
        new = _make_scan([_make_project("A", lines=100), _make_project("B", lines=200)], date="2025-06-02T10:00:00")

        old_file = tmp_data_dir / "scan_old.json"
        new_file = tmp_data_dir / "scan_new.json"
        old_file.write_text(json.dumps(old))
        new_file.write_text(json.dumps(new))

        diff = comparator.compare(old_file, new_file)
        assert diff is not None
        assert len(diff.new_projects) == 1
        assert diff.new_projects[0].name == "B"

    def test_compare_removed_project(self, comparator, tmp_data_dir):
        old = _make_scan([_make_project("A"), _make_project("B")])
        new = _make_scan([_make_project("A")], date="2025-06-02T10:00:00")

        old_file = tmp_data_dir / "scan_old.json"
        new_file = tmp_data_dir / "scan_new.json"
        old_file.write_text(json.dumps(old))
        new_file.write_text(json.dumps(new))

        diff = comparator.compare(old_file, new_file)
        assert len(diff.removed_projects) == 1
        assert diff.removed_projects[0].name == "B"

    def test_compare_changed_project(self, comparator, tmp_data_dir):
        old = _make_scan([_make_project("A", lines=100, files=5)])
        new = _make_scan([_make_project("A", lines=200, files=8)], date="2025-06-02T10:00:00")

        old_file = tmp_data_dir / "scan_old.json"
        new_file = tmp_data_dir / "scan_new.json"
        old_file.write_text(json.dumps(old))
        new_file.write_text(json.dumps(new))

        diff = comparator.compare(old_file, new_file)
        assert len(diff.changed_projects) == 1
        assert diff.changed_projects[0].line_diff == 100

    def test_compare_unchanged_project(self, comparator, tmp_data_dir):
        old = _make_scan([_make_project("A", lines=100, files=5)])
        new = _make_scan([_make_project("A", lines=100, files=5)], date="2025-06-02T10:00:00")

        old_file = tmp_data_dir / "scan_old.json"
        new_file = tmp_data_dir / "scan_new.json"
        old_file.write_text(json.dumps(old))
        new_file.write_text(json.dumps(new))

        diff = comparator.compare(old_file, new_file)
        assert len(diff.unchanged_projects) == 1

    def test_compare_latest_insufficient_scans(self, comparator):
        assert comparator.compare_latest() is None

    def test_format_diff_report(self, comparator):
        diff = ScanDiff(
            old_date="2025-06-01T10:00:00",
            new_date="2025-06-02T10:00:00",
            new_projects=[ProjectDiff(name="Yeni", status="new", new_lines=500, new_category="Web")],
            removed_projects=[ProjectDiff(name="Eski", status="removed", old_lines=300, old_category="CLI")],
            changed_projects=[ProjectDiff(name="Degisen", status="changed", old_lines=100, new_lines=200)],
            unchanged_projects=[],
            old_total_projects=2,
            new_total_projects=2,
            old_total_lines=400,
            new_total_lines=700,
            old_total_files=20,
            new_total_files=30,
        )
        report = comparator.format_diff_report(diff)
        assert "KARŞILAŞTIRMA" in report
        assert "Yeni" in report
        assert "Eski" in report
        assert "Degisen" in report
        assert "700" in report
