"""
Emare Katip - HTML Rapor Üretici
===================================
Analiz sonuçlarını interaktif HTML raporu olarak üretir.
Tarayıcıda açılabilen, filtrelenebilen, modern bir dashboard rapor.
"""

from pathlib import Path
from datetime import datetime
from typing import List, Dict

from config import get_logger
from models.project import ProjectInfo, KingstonReport
from analyzers.project_analyzer import ProjectAnalyzer
from exceptions import ReportError

logger = get_logger("reporters.html")


class HtmlReporter:
    """HTML formatında interaktif proje raporu üretir."""

    CATEGORY_COLORS = {
        "AI / Yapay Zeka": "#8b5cf6",
        "AI Asistan": "#6366f1",
        "AI Bot": "#a78bfa",
        "Web Uygulama": "#3b82f6",
        "Web Servis": "#06b6d4",
        "Sistem": "#f97316",
        "Bot": "#10b981",
        "Yönetim Paneli": "#f59e0b",
        "Genel": "#6b7280",
    }

    MATURITY_COLORS = {
        "Boş": "#1f2937",
        "Erken Aşama": "#ef4444",
        "Prototip": "#f97316",
        "Geliştiriliyor": "#eab308",
        "Aktif Geliştirme": "#22c55e",
        "Üretim Hazır": "#3b82f6",
    }

    def __init__(self, analyzer: ProjectAnalyzer, output_dir: Path):
        self.analyzer = analyzer
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _css(self) -> str:
        return """
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #0f172a; color: #e2e8f0;
                line-height: 1.6; padding: 20px;
            }
            .container { max-width: 1400px; margin: 0 auto; }
            h1 { font-size: 2rem; margin-bottom: 8px; color: #f1f5f9; }
            h2 { font-size: 1.4rem; margin: 30px 0 16px; color: #94a3b8; border-bottom: 1px solid #334155; padding-bottom: 8px; }
            .subtitle { color: #64748b; margin-bottom: 30px; }

            /* Stats Cards */
            .stats-grid {
                display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 16px; margin-bottom: 30px;
            }
            .stat-card {
                background: #1e293b; border-radius: 12px; padding: 20px;
                border: 1px solid #334155; text-align: center;
                transition: transform 0.2s;
            }
            .stat-card:hover { transform: translateY(-2px); border-color: #4f46e5; }
            .stat-card .icon { font-size: 2rem; margin-bottom: 8px; }
            .stat-card .value { font-size: 1.8rem; font-weight: 700; color: #f1f5f9; }
            .stat-card .label { color: #94a3b8; font-size: 0.85rem; margin-top: 4px; }

            /* Filter Bar */
            .filter-bar {
                display: flex; gap: 12px; flex-wrap: wrap;
                margin-bottom: 20px; align-items: center;
            }
            .filter-bar input, .filter-bar select {
                background: #1e293b; border: 1px solid #334155; color: #e2e8f0;
                padding: 8px 14px; border-radius: 8px; font-size: 0.9rem;
            }
            .filter-bar input { flex: 1; min-width: 200px; }
            .filter-bar input:focus, .filter-bar select:focus { outline: none; border-color: #4f46e5; }

            /* Charts */
            .charts-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; margin-bottom: 30px; }
            .chart-card { background: #1e293b; border-radius: 12px; padding: 20px; border: 1px solid #334155; }
            .chart-card h3 { color: #94a3b8; font-size: 0.95rem; margin-bottom: 16px; }
            .bar-item { display: flex; align-items: center; margin-bottom: 8px; }
            .bar-label { width: 120px; font-size: 0.85rem; color: #cbd5e1; text-align: right; padding-right: 12px; }
            .bar-track { flex: 1; height: 24px; background: #0f172a; border-radius: 4px; overflow: hidden; }
            .bar-fill { height: 100%; border-radius: 4px; display: flex; align-items: center; padding-left: 8px; font-size: 0.75rem; font-weight: 600; min-width: 30px; transition: width 0.5s; }
            .badge { display: inline-block; padding: 2px 10px; border-radius: 999px; font-size: 0.75rem; font-weight: 600; }

            /* Project Table */
            .table-container { overflow-x: auto; }
            table { width: 100%; border-collapse: collapse; background: #1e293b; border-radius: 12px; overflow: hidden; }
            th { background: #334155; color: #94a3b8; text-align: left; padding: 12px 16px; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.5px; cursor: pointer; user-select: none; }
            th:hover { color: #e2e8f0; }
            td { padding: 12px 16px; border-bottom: 1px solid #1e293b; font-size: 0.9rem; }
            tr { transition: background 0.15s; }
            tr:hover { background: #1e293b99; }
            tr.hidden { display: none; }
            .project-name { font-weight: 600; color: #f1f5f9; }
            .ai-badge { background: #4f46e510; color: #a78bfa; border: 1px solid #4f46e5; }
            .fw-badge { background: #06b6d410; color: #67e8f9; border: 1px solid #06b6d4; }
            .git-badge { background: #f9731610; color: #fb923c; border: 1px solid #f97316; }

            /* Connections */
            .connection-list { list-style: none; }
            .connection-list li { padding: 8px 0; border-bottom: 1px solid #1e293b; }
            .connection-type { color: #94a3b8; font-size: 0.8rem; }

            footer { text-align: center; color: #475569; margin-top: 40px; padding: 20px; font-size: 0.85rem; }
        </style>"""

    def _script(self, projects: List[ProjectInfo]) -> str:
        return """
        <script>
        function filterProjects() {
            const search = document.getElementById('searchInput').value.toLowerCase();
            const catFilter = document.getElementById('catFilter').value;
            const langFilter = document.getElementById('langFilter').value;
            const rows = document.querySelectorAll('#projectTable tbody tr');

            rows.forEach(row => {
                const name = row.dataset.name || '';
                const cat = row.dataset.category || '';
                const lang = row.dataset.language || '';

                const matchSearch = name.includes(search);
                const matchCat = !catFilter || cat === catFilter;
                const matchLang = !langFilter || lang === langFilter;

                row.classList.toggle('hidden', !(matchSearch && matchCat && matchLang));
            });
        }

        function sortTable(colIndex) {
            const table = document.getElementById('projectTable');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            const th = table.querySelectorAll('th')[colIndex];
            const isAsc = th.dataset.sort !== 'asc';

            // Reset all headers
            table.querySelectorAll('th').forEach(h => { h.dataset.sort = ''; h.textContent = h.textContent.replace(/ [▲▼]/, ''); });

            rows.sort((a, b) => {
                let aVal = a.children[colIndex].dataset.value || a.children[colIndex].textContent.trim();
                let bVal = b.children[colIndex].dataset.value || b.children[colIndex].textContent.trim();

                // Try numeric sort
                const aNum = parseFloat(aVal.replace(/,/g, ''));
                const bNum = parseFloat(bVal.replace(/,/g, ''));
                if (!isNaN(aNum) && !isNaN(bNum)) {
                    return isAsc ? aNum - bNum : bNum - aNum;
                }
                return isAsc ? aVal.localeCompare(bVal, 'tr') : bVal.localeCompare(aVal, 'tr');
            });

            th.dataset.sort = isAsc ? 'asc' : 'desc';
            th.textContent += isAsc ? ' ▲' : ' ▼';
            rows.forEach(row => tbody.appendChild(row));
        }
        </script>"""

    def _build_stats_cards(self, report: KingstonReport) -> str:
        return f"""
        <div class="stats-grid">
            <div class="stat-card">
                <div class="icon">📁</div>
                <div class="value">{report.total_projects}</div>
                <div class="label">Toplam Proje</div>
            </div>
            <div class="stat-card">
                <div class="icon">📄</div>
                <div class="value">{report.total_files:,}</div>
                <div class="label">Toplam Dosya</div>
            </div>
            <div class="stat-card">
                <div class="icon">📝</div>
                <div class="value">{report.total_lines:,}</div>
                <div class="label">Kod Satırı</div>
            </div>
            <div class="stat-card">
                <div class="icon">💾</div>
                <div class="value">{report.total_size_mb:.1f}</div>
                <div class="label">Toplam MB</div>
            </div>
            <div class="stat-card">
                <div class="icon">🗣️</div>
                <div class="value">{len(report.language_distribution)}</div>
                <div class="label">Programlama Dili</div>
            </div>
            <div class="stat-card">
                <div class="icon">🧠</div>
                <div class="value">{len(report.ai_services_used)}</div>
                <div class="label">AI Servisi</div>
            </div>
        </div>"""

    def _build_charts(self, report: KingstonReport) -> str:
        # Language chart
        max_lang = max(report.language_distribution.values()) if report.language_distribution else 1
        lang_bars = ""
        colors = ["#4f46e5", "#3b82f6", "#06b6d4", "#10b981", "#22c55e", "#eab308", "#f97316", "#ef4444", "#ec4899", "#8b5cf6"]
        for i, (lang, count) in enumerate(list(report.language_distribution.items())[:10]):
            pct = (count / max_lang) * 100
            color = colors[i % len(colors)]
            lang_bars += f'''
            <div class="bar-item">
                <div class="bar-label">{lang}</div>
                <div class="bar-track">
                    <div class="bar-fill" style="width:{pct}%; background:{color};">{count}</div>
                </div>
            </div>'''

        # Category chart
        cat_items = ""
        for cat, count in report.category_distribution.items():
            color = self.CATEGORY_COLORS.get(cat, "#6b7280")
            cat_items += f'<div class="bar-item"><div class="bar-label">{cat}</div><div class="bar-track"><div class="bar-fill" style="width:{count/report.total_projects*100}%; background:{color};">{count}</div></div></div>'

        return f"""
        <div class="charts-grid">
            <div class="chart-card">
                <h3>🗣️ Dil Dağılımı (Dosya Sayısı)</h3>
                {lang_bars}
            </div>
            <div class="chart-card">
                <h3>🏷️ Kategori Dağılımı</h3>
                {cat_items}
            </div>
        </div>"""

    def _build_filter_bar(self, report: KingstonReport, projects: List[ProjectInfo]) -> str:
        cat_options = '<option value="">Tüm Kategoriler</option>'
        for cat in sorted(report.category_distribution.keys()):
            cat_options += f'<option value="{cat}">{cat}</option>'

        langs = sorted(set(p.primary_language for p in projects))
        lang_options = '<option value="">Tüm Diller</option>'
        for lang in langs:
            lang_options += f'<option value="{lang}">{lang}</option>'

        return f"""
        <div class="filter-bar">
            <input type="text" id="searchInput" placeholder="🔍 Proje ara..." oninput="filterProjects()">
            <select id="catFilter" onchange="filterProjects()">{cat_options}</select>
            <select id="langFilter" onchange="filterProjects()">{lang_options}</select>
        </div>"""

    def _build_project_table(self, projects: List[ProjectInfo]) -> str:
        rows = ""
        for p in sorted(projects, key=lambda x: x.stats.total_lines, reverse=True):
            mat_color = self.MATURITY_COLORS.get(p.maturity, "#6b7280")
            cat_color = self.CATEGORY_COLORS.get(p.category, "#6b7280")

            badges = ""
            for fw in p.frameworks[:3]:
                badges += f'<span class="badge fw-badge">{fw}</span> '
            for ai in p.ai_services[:2]:
                badges += f'<span class="badge ai-badge">{ai}</span> '
            if p.has_git:
                badges += '<span class="badge git-badge">Git</span> '

            rows += f'''
            <tr data-name="{p.name.lower()}" data-category="{p.category}" data-language="{p.primary_language}">
                <td class="project-name">{p.name}</td>
                <td>{p.primary_language}</td>
                <td><span class="badge" style="background:{cat_color}20;color:{cat_color};border:1px solid {cat_color}">{p.category}</span></td>
                <td><span class="badge" style="background:{mat_color}20;color:{mat_color};border:1px solid {mat_color}">{p.maturity}</span></td>
                <td data-value="{p.stats.total_files}">{p.stats.total_files}</td>
                <td data-value="{p.stats.code_files}">{p.stats.code_files}</td>
                <td data-value="{p.stats.total_lines}">{p.stats.total_lines:,}</td>
                <td data-value="{p.total_size_mb}">{p.total_size_mb} MB</td>
                <td>{badges}</td>
            </tr>'''

        return f"""
        <div class="table-container">
            <table id="projectTable">
                <thead>
                    <tr>
                        <th onclick="sortTable(0)">Proje</th>
                        <th onclick="sortTable(1)">Dil</th>
                        <th onclick="sortTable(2)">Kategori</th>
                        <th onclick="sortTable(3)">Olgunluk</th>
                        <th onclick="sortTable(4)">Dosya</th>
                        <th onclick="sortTable(5)">Kod</th>
                        <th onclick="sortTable(6)">Satır</th>
                        <th onclick="sortTable(7)">Boyut</th>
                        <th>Etiketler</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>"""

    def _build_connections(self, analyzer: ProjectAnalyzer) -> str:
        connections = analyzer.find_connections()
        if not connections:
            return ""

        items = ""
        for conn in connections:
            icon = "🧠" if conn["type"] == "shared_ai_service" else ("🔧" if conn["type"] == "shared_framework" else "👨‍👩‍👧‍👦")
            items += f'<li>{icon} <strong>{conn.get("service", conn.get("framework", conn.get("family", "")))}</strong> — {", ".join(conn["projects"])}</li>'

        return f"""
        <h2>🔗 Proje Bağlantıları</h2>
        <div class="chart-card">
            <ul class="connection-list">{items}</ul>
        </div>"""

    def generate(self) -> str:
        """Tam HTML raporu üretir ve dosyaya yazar."""
        report = self.analyzer.generate_report()
        now = datetime.now().strftime("%d %B %Y, %H:%M")

        html = f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Emare Katip — KINGSTON Raporu</title>
    {self._css()}
</head>
<body>
    <div class="container">
        <h1>📋 Emare Katip — KINGSTON Veri Raporu</h1>
        <p class="subtitle">Tarama Tarihi: {now} | Emare Katip tarafından otomatik oluşturulmuştur</p>

        {self._build_stats_cards(report)}
        {self._build_charts(report)}

        <h2>📁 Projeler</h2>
        {self._build_filter_bar(report, report.projects)}
        {self._build_project_table(report.projects)}
        {self._build_connections(self.analyzer)}

        <footer>
            📋 Emare Katip v1.0 — KINGSTON Veri Toplayıcı & Analizcisi<br>
            🗓️ {now}
        </footer>
    </div>
    {self._script(report.projects)}
</body>
</html>"""

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_file = self.output_dir / f"rapor_{timestamp}.html"

        try:
            output_file.write_text(html, encoding="utf-8")
            latest_file = self.output_dir / "son_rapor.html"
            latest_file.write_text(html, encoding="utf-8")
        except (OSError, IOError) as e:
            raise ReportError(f"HTML dosyası yazılamadı: {e}", "html") from e

        logger.info(f"HTML rapor yazıldı: {output_file}")
        return str(output_file)
