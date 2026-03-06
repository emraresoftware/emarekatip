"""
Emare Katip - Tarama Karşılaştırıcı (Diff)
=============================================
İki farklı tarama sonucunu karşılaştırarak değişiklikleri raporlar.
Yeni/silinen projeler, büyüme, dil dağılımı değişimi vb.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from config import get_logger, DATA_DIR

logger = get_logger("diff")


@dataclass
class ProjectDiff:
    """İki tarama arasındaki tek proje değişimi."""
    name: str
    status: str  # "new", "removed", "changed", "unchanged"
    old_lines: int = 0
    new_lines: int = 0
    old_files: int = 0
    new_files: int = 0
    old_size_mb: float = 0.0
    new_size_mb: float = 0.0
    old_category: str = ""
    new_category: str = ""
    old_maturity: str = ""
    new_maturity: str = ""

    @property
    def line_diff(self) -> int:
        return self.new_lines - self.old_lines

    @property
    def file_diff(self) -> int:
        return self.new_files - self.old_files

    @property
    def size_diff_mb(self) -> float:
        return round(self.new_size_mb - self.old_size_mb, 2)

    @property
    def line_growth_pct(self) -> float:
        if self.old_lines == 0:
            return 100.0 if self.new_lines > 0 else 0.0
        return round((self.line_diff / self.old_lines) * 100, 1)


@dataclass
class ScanDiff:
    """İki tarama arasındaki genel farklar."""
    old_date: str = ""
    new_date: str = ""
    new_projects: List[ProjectDiff] = field(default_factory=list)
    removed_projects: List[ProjectDiff] = field(default_factory=list)
    changed_projects: List[ProjectDiff] = field(default_factory=list)
    unchanged_projects: List[ProjectDiff] = field(default_factory=list)
    old_total_projects: int = 0
    new_total_projects: int = 0
    old_total_lines: int = 0
    new_total_lines: int = 0
    old_total_files: int = 0
    new_total_files: int = 0


class ScanComparator:
    """İki tarama sonucunu karşılaştırır."""

    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or DATA_DIR

    def list_scans(self) -> List[Path]:
        """Mevcut tarama dosyalarını tarih sırasıyla listeler."""
        if not self.data_dir.exists():
            return []
        scans = sorted(self.data_dir.glob("scan_*.json"))
        return scans

    def load_scan(self, scan_path: Path) -> Optional[dict]:
        """Tarama verisini yükler."""
        try:
            with open(scan_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Tarama dosyası okunamadı: {scan_path} — {e}")
            return None

    def _extract_project_map(self, scan_data: dict) -> Dict[str, dict]:
        """Tarama verisinden proje haritası oluşturur (ad → veri)."""
        return {p["name"]: p for p in scan_data.get("projects", [])}

    def compare(self, old_path: Path, new_path: Path) -> Optional[ScanDiff]:
        """İki taramayı karşılaştırır.

        Args:
            old_path: Eski tarama dosyası
            new_path: Yeni tarama dosyası

        Returns:
            ScanDiff: Farklar veya None
        """
        old_data = self.load_scan(old_path)
        new_data = self.load_scan(new_path)

        if not old_data or not new_data:
            logger.error("Tarama verileri yüklenemedi.")
            return None

        old_map = self._extract_project_map(old_data)
        new_map = self._extract_project_map(new_data)

        diff = ScanDiff(
            old_date=old_data.get("scan_date", ""),
            new_date=new_data.get("scan_date", ""),
            old_total_projects=old_data.get("project_count", 0),
            new_total_projects=new_data.get("project_count", 0),
        )

        # Genel istatistikler
        for p in old_data.get("projects", []):
            diff.old_total_lines += p.get("stats", {}).get("total_lines", 0)
            diff.old_total_files += p.get("stats", {}).get("total_files", 0)
        for p in new_data.get("projects", []):
            diff.new_total_lines += p.get("stats", {}).get("total_lines", 0)
            diff.new_total_files += p.get("stats", {}).get("total_files", 0)

        all_names = set(old_map.keys()) | set(new_map.keys())

        for name in sorted(all_names):
            old_p = old_map.get(name)
            new_p = new_map.get(name)

            if old_p and not new_p:
                # Silinen proje
                diff.removed_projects.append(ProjectDiff(
                    name=name, status="removed",
                    old_lines=old_p.get("stats", {}).get("total_lines", 0),
                    old_files=old_p.get("stats", {}).get("total_files", 0),
                    old_size_mb=old_p.get("stats", {}).get("total_size_mb", 0),
                    old_category=old_p.get("category", ""),
                    old_maturity=old_p.get("maturity", ""),
                ))

            elif new_p and not old_p:
                # Yeni proje
                diff.new_projects.append(ProjectDiff(
                    name=name, status="new",
                    new_lines=new_p.get("stats", {}).get("total_lines", 0),
                    new_files=new_p.get("stats", {}).get("total_files", 0),
                    new_size_mb=new_p.get("stats", {}).get("total_size_mb", 0),
                    new_category=new_p.get("category", ""),
                    new_maturity=new_p.get("maturity", ""),
                ))

            else:
                # Her ikisinde de var — karşılaştır
                old_stats = old_p.get("stats", {})
                new_stats = new_p.get("stats", {})

                pd = ProjectDiff(
                    name=name,
                    status="changed",
                    old_lines=old_stats.get("total_lines", 0),
                    new_lines=new_stats.get("total_lines", 0),
                    old_files=old_stats.get("total_files", 0),
                    new_files=new_stats.get("total_files", 0),
                    old_size_mb=old_stats.get("total_size_mb", 0),
                    new_size_mb=new_stats.get("total_size_mb", 0),
                    old_category=old_p.get("category", ""),
                    new_category=new_p.get("category", ""),
                    old_maturity=old_p.get("maturity", ""),
                    new_maturity=new_p.get("maturity", ""),
                )

                if pd.line_diff == 0 and pd.file_diff == 0:
                    pd.status = "unchanged"
                    diff.unchanged_projects.append(pd)
                else:
                    diff.changed_projects.append(pd)

        return diff

    def compare_latest(self) -> Optional[ScanDiff]:
        """Son iki taramayı karşılaştırır."""
        scans = self.list_scans()
        if len(scans) < 2:
            logger.warning("Karşılaştırma için en az 2 tarama gerekli.")
            return None

        return self.compare(scans[-2], scans[-1])

    def format_diff_report(self, diff: ScanDiff) -> str:
        """Fark raporunu okunabilir metin olarak döndürür."""
        lines = []
        lines.append("=" * 60)
        lines.append("📊 EMARE KATİP — TARAMA KARŞILAŞTIRMA RAPORU")
        lines.append("=" * 60)
        lines.append(f"  📅 Eski tarama : {diff.old_date[:19]}")
        lines.append(f"  📅 Yeni tarama : {diff.new_date[:19]}")
        lines.append("")

        # Genel değişim
        proj_diff = diff.new_total_projects - diff.old_total_projects
        line_diff = diff.new_total_lines - diff.old_total_lines
        file_diff = diff.new_total_files - diff.old_total_files

        lines.append(f"  📁 Projeler: {diff.old_total_projects} → {diff.new_total_projects} ({'+' if proj_diff >= 0 else ''}{proj_diff})")
        lines.append(f"  📄 Dosyalar: {diff.old_total_files:,} → {diff.new_total_files:,} ({'+' if file_diff >= 0 else ''}{file_diff:,})")
        lines.append(f"  📝 Satırlar: {diff.old_total_lines:,} → {diff.new_total_lines:,} ({'+' if line_diff >= 0 else ''}{line_diff:,})")
        lines.append("")

        if diff.new_projects:
            lines.append(f"  🆕 Yeni Projeler ({len(diff.new_projects)}):")
            for p in diff.new_projects:
                lines.append(f"      + {p.name:30s} {p.new_lines:>8,} satır  [{p.new_category}]")
            lines.append("")

        if diff.removed_projects:
            lines.append(f"  🗑️  Silinen Projeler ({len(diff.removed_projects)}):")
            for p in diff.removed_projects:
                lines.append(f"      - {p.name:30s} {p.old_lines:>8,} satır  [{p.old_category}]")
            lines.append("")

        if diff.changed_projects:
            lines.append(f"  🔄 Değişen Projeler ({len(diff.changed_projects)}):")
            for p in sorted(diff.changed_projects, key=lambda x: abs(x.line_diff), reverse=True):
                sign = "+" if p.line_diff >= 0 else ""
                lines.append(f"      ~ {p.name:30s} {sign}{p.line_diff:>8,} satır ({sign}{p.line_growth_pct}%)")
                if p.old_maturity != p.new_maturity:
                    lines.append(f"        Olgunluk: {p.old_maturity} → {p.new_maturity}")
            lines.append("")

        lines.append(f"  ✅ Değişmeyen Projeler: {len(diff.unchanged_projects)}")
        lines.append("=" * 60)

        return "\n".join(lines)
