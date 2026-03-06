"""
Emare Katip - CSV Rapor Üretici
==================================
Analiz sonuçlarını Excel uyumlu CSV formatında kaydeder.
"""

import csv
from pathlib import Path
from datetime import datetime
from typing import List

from config import get_logger
from models.project import ProjectInfo
from analyzers.project_analyzer import ProjectAnalyzer
from exceptions import ReportError

logger = get_logger("reporters.csv")


class CsvReporter:
    """CSV formatında proje raporu üretir (Excel uyumlu)."""

    HEADERS = [
        "Proje Adı",
        "Yol",
        "Proje Türü",
        "Birincil Dil",
        "Kategori",
        "Olgunluk",
        "Toplam Dosya",
        "Kod Dosyası",
        "Doküman Dosyası",
        "Konfig Dosyası",
        "Toplam Satır",
        "Boyut (MB)",
        "Frameworkler",
        "AI Servisleri",
        "Bağımlılıklar",
        "Git",
        "Testler",
        "CI/CD",
        "En Büyük Dosya",
        "En Büyük Dosya Satır",
        "Diller",
        "Açıklama",
    ]

    def __init__(self, analyzer: ProjectAnalyzer, output_dir: Path):
        self.analyzer = analyzer
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _project_to_row(self, p: ProjectInfo) -> list:
        """ProjectInfo'yu CSV satırına dönüştürür."""
        lang_str = ", ".join(
            f"{lang} ({count})"
            for lang, count in sorted(
                p.stats.languages.items(), key=lambda x: x[1], reverse=True
            )
        )
        return [
            p.name,
            p.path,
            p.project_type,
            p.primary_language,
            p.category,
            p.maturity,
            p.stats.total_files,
            p.stats.code_files,
            p.stats.doc_files,
            p.stats.config_files,
            p.stats.total_lines,
            p.total_size_mb,
            "; ".join(p.frameworks),
            "; ".join(p.ai_services),
            "; ".join(p.dependencies),
            "Evet" if p.has_git else "Hayır",
            "Evet" if p.has_tests else "Hayır",
            "Evet" if p.has_ci else "Hayır",
            p.stats.largest_file or "",
            p.stats.largest_file_lines,
            lang_str,
            p.description[:200] if p.description else "",
        ]

    def generate(self) -> str:
        """CSV rapor üretir ve dosyaya yazar."""
        report = self.analyzer.generate_report()
        projects = sorted(report.projects, key=lambda p: p.stats.total_lines, reverse=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_file = self.output_dir / f"rapor_{timestamp}.csv"

        try:
            # BOM ile yaz (Excel UTF-8 uyumluluğu için)
            with open(output_file, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.writer(f, delimiter=";", quoting=csv.QUOTE_MINIMAL)
                writer.writerow(self.HEADERS)

                for p in projects:
                    writer.writerow(self._project_to_row(p))

                # Boş satır + özet
                writer.writerow([])
                writer.writerow(["ÖZET"])
                writer.writerow(["Toplam Proje", report.total_projects])
                writer.writerow(["Toplam Dosya", report.total_files])
                writer.writerow(["Toplam Satır", report.total_lines])
                writer.writerow(["Toplam Boyut (MB)", report.total_size_mb])
                writer.writerow(["AI Servisleri", "; ".join(report.ai_services_used)])

            # Son rapor kopyası
            latest_file = self.output_dir / "son_rapor.csv"
            with open(latest_file, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.writer(f, delimiter=";", quoting=csv.QUOTE_MINIMAL)
                writer.writerow(self.HEADERS)
                for p in projects:
                    writer.writerow(self._project_to_row(p))

        except (OSError, IOError) as e:
            raise ReportError(f"CSV dosyası yazılamadı: {e}", "csv") from e

        logger.info(f"CSV rapor yazıldı: {output_file}")
        return str(output_file)
