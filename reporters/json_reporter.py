"""
Emare Katip - JSON Rapor Üretici
==================================
Analiz sonuçlarını JSON formatında kaydeder.
"""

import json
from pathlib import Path
from datetime import datetime

from config import get_logger
from models.project import KingstonReport
from analyzers.project_analyzer import ProjectAnalyzer
from exceptions import ReportError

logger = get_logger("reporters.json")


class JsonReporter:
    """JSON formatında veri raporu üretir."""

    def __init__(self, analyzer: ProjectAnalyzer, output_dir: Path):
        self.analyzer = analyzer
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(self) -> str:
        """JSON rapor üretir ve dosyaya yazar."""
        report = self.analyzer.generate_report()
        data = report.to_dict()

        # Bağlantı bilgisi ekle
        data["connections"] = self.analyzer.find_connections()
        data["all_frameworks"] = self.analyzer.get_all_frameworks()

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_file = self.output_dir / f"rapor_{timestamp}.json"

        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            # Son rapor
            latest_file = self.output_dir / "son_rapor.json"
            with open(latest_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except (OSError, IOError) as e:
            raise ReportError(f"Dosya yazılamadı: {e}", "json") from e

        logger.info(f"JSON rapor yazıldı: {output_file}")
        return str(output_file)
