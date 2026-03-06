"""
Emare Katip - Markdown Rapor Üretici
======================================
Analiz sonuçlarını güzel biçimlendirilmiş Markdown raporu olarak yazar.
"""

from pathlib import Path
from datetime import datetime
from typing import List, Dict

from config import get_logger
from models.project import ProjectInfo, KingstonReport
from analyzers.project_analyzer import ProjectAnalyzer
from exceptions import ReportError

logger = get_logger("reporters.markdown")


class MarkdownReporter:
    """Markdown formatında proje raporu üretir."""

    MATURITY_EMOJI = {
        "Boş": "⚫",
        "Erken Aşama": "🔴",
        "Prototip": "🟠",
        "Geliştiriliyor": "🟡",
        "Aktif Geliştirme": "🟢",
        "Üretim Hazır": "🔵",
    }

    CATEGORY_EMOJI = {
        "AI / Yapay Zeka": "🧠",
        "AI Asistan": "🤖",
        "AI Bot": "💬",
        "Web Uygulama": "🌐",
        "Web Servis": "🔌",
        "Sistem": "⚙️",
        "Bot": "🤖",
        "Yönetim Paneli": "📊",
        "Genel": "📁",
    }

    def __init__(self, analyzer: ProjectAnalyzer, output_dir: Path):
        self.analyzer = analyzer
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _header(self) -> str:
        now = datetime.now().strftime("%d %B %Y, %H:%M")
        return f"""# 📋 Emare Katip — KINGSTON Veri Raporu

> **Tarama Tarihi:** {now}
> **Emare Katip** tarafından otomatik oluşturulmuştur.

---

"""

    def _summary_section(self, report: KingstonReport) -> str:
        return f"""## 📊 Genel Özet

| Metrik | Değer |
|--------|-------|
| **Toplam Proje** | {report.total_projects} |
| **Toplam Dosya** | {report.total_files:,} |
| **Toplam Boyut** | {report.total_size_mb:.1f} MB |
| **Toplam Kod Satırı** | {report.total_lines:,} |
| **Kullanılan AI Servisleri** | {', '.join(report.ai_services_used) if report.ai_services_used else 'Yok'} |

---

"""

    def _language_section(self, report: KingstonReport) -> str:
        lines = ["## 🗣️ Dil Dağılımı\n\n"]
        lines.append("| Dil | Dosya Sayısı |\n|-----|-------------|\n")
        for lang, count in sorted(report.language_distribution.items(),
                                   key=lambda x: x[1], reverse=True):
            bar = "█" * min(count, 40)
            lines.append(f"| **{lang}** | {count} {bar} |\n")
        lines.append("\n---\n\n")
        return "".join(lines)

    def _category_section(self, report: KingstonReport) -> str:
        lines = ["## 🏷️ Kategori Dağılımı\n\n"]
        for cat, count in sorted(report.category_distribution.items(),
                                  key=lambda x: x[1], reverse=True):
            emoji = self.CATEGORY_EMOJI.get(cat, "📁")
            lines.append(f"- {emoji} **{cat}**: {count} proje\n")
        lines.append("\n---\n\n")
        return "".join(lines)

    def _project_detail(self, p: ProjectInfo) -> str:
        maturity_emoji = self.MATURITY_EMOJI.get(p.maturity, "⚪")
        cat_emoji = self.CATEGORY_EMOJI.get(p.category, "📁")

        lines = [f"### {cat_emoji} {p.name}\n\n"]
        lines.append(f"| Özellik | Değer |\n|---------|-------|\n")
        lines.append(f"| **Yol** | `{p.path}` |\n")
        lines.append(f"| **Tür** | {p.project_type} |\n")
        lines.append(f"| **Birincil Dil** | {p.primary_language} |\n")
        lines.append(f"| **Kategori** | {cat_emoji} {p.category} |\n")
        lines.append(f"| **Olgunluk** | {maturity_emoji} {p.maturity} |\n")
        lines.append(f"| **Dosya Sayısı** | {p.stats.total_files} |\n")
        lines.append(f"| **Kod Dosyası** | {p.stats.code_files} |\n")
        lines.append(f"| **Kod Satırı** | {p.stats.total_lines:,} |\n")
        lines.append(f"| **Boyut** | {p.total_size_mb} MB |\n")

        if p.frameworks:
            lines.append(f"| **Frameworkler** | {', '.join(p.frameworks)} |\n")
        if p.ai_services:
            lines.append(f"| **AI Servisleri** | {', '.join(p.ai_services)} |\n")
        if p.has_git:
            lines.append(f"| **Git** | ✅ |\n")
        if p.has_tests:
            lines.append(f"| **Testler** | ✅ |\n")
        if p.has_ci:
            lines.append(f"| **CI/CD** | ✅ |\n")

        if p.stats.largest_file:
            lines.append(f"| **En Büyük Dosya** | {p.stats.largest_file} ({p.stats.largest_file_lines:,} satır) |\n")

        if p.stats.languages:
            lang_str = ", ".join(f"{l} ({c})" for l, c in
                                 sorted(p.stats.languages.items(), key=lambda x: x[1], reverse=True))
            lines.append(f"| **Diller** | {lang_str} |\n")

        if p.description:
            lines.append(f"\n> {p.description[:300]}\n")

        lines.append("\n")
        return "".join(lines)

    def _projects_section(self, projects: List[ProjectInfo]) -> str:
        lines = ["## 📁 Proje Detayları\n\n"]

        # Kategoriye göre grupla
        groups: Dict[str, List[ProjectInfo]] = {}
        for p in projects:
            groups.setdefault(p.category, []).append(p)

        for category in sorted(groups.keys()):
            cat_emoji = self.CATEGORY_EMOJI.get(category, "📁")
            lines.append(f"---\n\n#### {cat_emoji} {category}\n\n")
            for p in sorted(groups[category], key=lambda x: x.stats.total_lines, reverse=True):
                lines.append(self._project_detail(p))

        return "".join(lines)

    def _connections_section(self, analyzer: ProjectAnalyzer) -> str:
        connections = analyzer.find_connections()
        if not connections:
            return ""

        lines = ["## 🔗 Proje Bağlantıları\n\n"]
        for conn in connections:
            if conn["type"] == "shared_ai_service":
                lines.append(f"- 🧠 **{conn['service']}**: {', '.join(conn['projects'])}\n")
            elif conn["type"] == "shared_framework":
                lines.append(f"- 🔧 **{conn['framework']}**: {', '.join(conn['projects'])}\n")
            elif conn["type"] == "project_family":
                lines.append(f"- 👨‍👩‍👧‍👦 **{conn['family']} Ailesi**: {', '.join(conn['projects'])}\n")

        lines.append("\n---\n\n")
        return "".join(lines)

    def _top_projects_table(self, analyzer: ProjectAnalyzer) -> str:
        top = analyzer.get_largest_projects(10)
        lines = ["## 🏆 En Büyük Projeler (Kod Satırı)\n\n"]
        lines.append("| # | Proje | Dil | Satır | Dosya | Boyut |\n")
        lines.append("|---|-------|-----|-------|-------|-------|\n")
        for i, p in enumerate(top, 1):
            lines.append(
                f"| {i} | **{p.name}** | {p.primary_language} | "
                f"{p.stats.total_lines:,} | {p.stats.total_files} | {p.total_size_mb} MB |\n"
            )
        lines.append("\n---\n\n")
        return "".join(lines)

    def generate(self) -> str:
        """Tam Markdown raporu üretir ve dosyaya yazar."""
        report = self.analyzer.generate_report()

        md = ""
        md += self._header()
        md += self._summary_section(report)
        md += self._language_section(report)
        md += self._category_section(report)
        md += self._top_projects_table(self.analyzer)
        md += self._connections_section(self.analyzer)
        md += self._projects_section(report.projects)

        # Footer
        md += "\n---\n\n"
        md += "> 📋 Bu rapor **Emare Katip** tarafından otomatik olarak oluşturulmuştur.\n"
        md += f"> 🗓️ {datetime.now().strftime('%d %B %Y, %H:%M')}\n"

        # Dosyaya yaz
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_file = self.output_dir / f"rapor_{timestamp}.md"

        try:
            output_file.write_text(md, encoding="utf-8")

            # Son rapor bağlantısı
            latest_file = self.output_dir / "son_rapor.md"
            latest_file.write_text(md, encoding="utf-8")
        except (OSError, IOError) as e:
            raise ReportError(f"Dosya yazılamadı: {e}", "markdown") from e

        logger.info(f"Markdown rapor yazıldı: {output_file}")
        return str(output_file)
