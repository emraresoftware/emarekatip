#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║                      EMARE KATİP v1.0                          ║
║         KINGSTON Disk Veri Toplayıcı & Analizcisi              ║
║                                                                  ║
║  KINGSTON diskindeki tüm projeleri tarar, analiz eder           ║
║  ve anlamlı raporlar oluşturur.                                  ║
╚══════════════════════════════════════════════════════════════════╝

Kullanım:
    python main.py              → Tam tarama ve rapor üretimi
    python main.py --scan       → Sadece tarama
    python main.py --scan --depth 5          → 5 seviye derinlikte tara
    python main.py --scan --lang python      → Sadece Python projeleri
    python main.py --scan --category ai      → Sadece AI projelerini tara
    python main.py --scan --min-files 5      → En az 5 dosyalı projeler
    python main.py --scan --include-empty    → Boş projeleri de dahil et
    python main.py --scan --no-skip-dupes    → Kopyaları da tara
    python main.py --scan --scan-filetype md → Sadece .md içeren projeleri tara
    python main.py --skeleton   → Klasör iskeletini çıkar
    python main.py --skeleton --depth 5  → 5 seviye derinlikte iskelet
    python main.py --find-dupes → Aynı isimli klasörleri bul
    python main.py --report     → Son verilere göre rapor üret
    python main.py --summary    → Kısa özet göster
    python main.py --project X  → Belirli projeyi detaylı göster
    python main.py --search X   → Projelerde arama yap
    python main.py --search X --deep  → Dosya içeriklerinde de ara
    python main.py --search X --deep --filetype md  → Sadece .md dosyalarında ara
"""

import sys
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime

# Proje kökünü sys.path'e ekle
BASE_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(BASE_DIR))

from config import ensure_dirs, DATA_DIR, REPORTS_DIR, SCAN_ROOT, get_timestamp, setup_logging, get_logger
from scanner import Scanner
from analyzers.project_analyzer import ProjectAnalyzer
from reporters.markdown_reporter import MarkdownReporter
from reporters.json_reporter import JsonReporter
from reporters.html_reporter import HtmlReporter
from reporters.csv_reporter import CsvReporter
from analyzers.diff_analyzer import ScanComparator
from exceptions import EmareKatipError, ScanError, DiskNotFoundError, DataError, ReportError

logger = get_logger("main")

BANNER = """
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║           ███████╗███╗   ███╗ █████╗ ██████╗ ███████╗            ║
║           ██╔════╝████╗ ████║██╔══██╗██╔══██╗██╔════╝            ║
║           █████╗  ██╔████╔██║███████║██████╔╝█████╗              ║
║           ██╔══╝  ██║╚██╔╝██║██╔══██║██╔══██╗██╔══╝              ║
║           ███████╗██║ ╚═╝ ██║██║  ██║██║  ██║███████╗            ║
║           ╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝            ║
║                                                                  ║
║                  K A T İ P   v 1 . 0                             ║
║          KINGSTON Veri Toplayıcı & Analizcisi                    ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""


def save_scan_data(projects: list) -> dict:
    """Tarama verilerini JSON olarak kaydeder."""
    data_file = DATA_DIR / f"scan_{get_timestamp()}.json"
    latest_file = DATA_DIR / "son_tarama.json"

    scan_data = {
        "scan_date": datetime.now().isoformat(),
        "scan_root": str(SCAN_ROOT),
        "project_count": len(projects),
        "projects": [p.to_dict() for p in projects],
    }

    try:
        for fpath in [data_file, latest_file]:
            with open(fpath, "w", encoding="utf-8") as f:
                json.dump(scan_data, f, ensure_ascii=False, indent=2)
    except (OSError, IOError) as e:
        raise DataError(f"Tarama verileri kaydedilemedi: {e}", str(data_file)) from e

    logger.info(f"Tarama verileri kaydedildi: {data_file}")
    return scan_data


def load_last_scan() -> dict | None:
    """Son tarama verilerini yükler."""
    latest = DATA_DIR / "son_tarama.json"
    if not latest.exists():
        logger.warning("Önceki tarama verisi bulunamadı. Önce tarama yapın: python main.py --scan")
        return None

    with open(latest, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            raise DataError(f"Tarama verisi bozuk: {e}", str(latest)) from e


def do_scan(
    max_depth: int = None,
    language_filter: str = None,
    min_files: int = 0,
    include_empty: bool = False,
    skip_duplicates: bool = True,
    category_filter: str = None,
    filetype_filter: str = None,
) -> list:
    """Disk taraması yapar.
    
    Args:
        max_depth: Tarama derinliği (None=config varsayılanı)
        language_filter: Sadece bu dili içeren projeler (ör: 'python')
        min_files: Minimum dosya sayısı filtresi
        include_empty: Boş projeleri dahil et
        skip_duplicates: Kopya klasörleri atla
        category_filter: Sadece bu kategoriyi içeren projeler (ör: 'ai')
        filetype_filter: Sadece bu dosya türünü içeren projeler (ör: 'md', 'py')
    """
    logger.info("KINGSTON diski taranıyor...")
    scanner = Scanner(
        max_depth=max_depth,
        language_filter=language_filter,
        min_files=min_files,
        include_empty=include_empty,
        skip_duplicates=skip_duplicates,
        category_filter=category_filter,
        filetype_filter=filetype_filter,
    )
    projects = scanner.scan_projects()
    save_scan_data(projects)
    return projects


def do_report(projects: list) -> tuple:
    """Rapor üretir."""
    logger.info("Raporlar oluşturuluyor...")
    analyzer = ProjectAnalyzer(projects)

    # Markdown rapor
    md_reporter = MarkdownReporter(analyzer, REPORTS_DIR)
    md_file = md_reporter.generate()

    # JSON rapor
    json_reporter = JsonReporter(analyzer, REPORTS_DIR)
    json_file = json_reporter.generate()

    # HTML rapor
    html_reporter = HtmlReporter(analyzer, REPORTS_DIR)
    html_file = html_reporter.generate()

    # CSV rapor
    csv_reporter = CsvReporter(analyzer, REPORTS_DIR)
    csv_file = csv_reporter.generate()

    return md_file, json_file, html_file, csv_file


def do_summary(projects: list) -> None:
    """Kısa özet yazdırır."""
    analyzer = ProjectAnalyzer(projects)
    report = analyzer.generate_report()

    print("\n" + "=" * 60)
    print("📊  EMARE KATİP — KINGSTON ÖZET RAPORU")
    print("=" * 60)
    print(f"  📁 Toplam Proje    : {report.total_projects}")
    print(f"  📄 Toplam Dosya    : {report.total_files:,}")
    print(f"  💾 Toplam Boyut    : {report.total_size_mb:.1f} MB")
    print(f"  📝 Toplam Satır    : {report.total_lines:,}")
    print()

    # Dil dağılımı
    print("  🗣️  Dil Dağılımı:")
    for lang, count in list(report.language_distribution.items())[:8]:
        bar = "█" * min(count, 30)
        print(f"      {lang:15s} {count:4d} {bar}")
    print()

    # Kategori dağılımı
    print("  🏷️  Kategoriler:")
    for cat, count in report.category_distribution.items():
        print(f"      {cat:20s} : {count} proje")
    print()

    # AI servisleri
    if report.ai_services_used:
        print(f"  🧠 AI Servisleri   : {', '.join(report.ai_services_used)}")
    print()

    # En büyük 5 proje
    top = analyzer.get_largest_projects(5)
    print("  🏆 En Büyük 5 Proje:")
    for i, p in enumerate(top, 1):
        print(f"      {i}. {p.name:25s} {p.stats.total_lines:>8,} satır  [{p.primary_language}]")

    # Bağlantılar
    connections = analyzer.find_connections()
    if connections:
        print("\n  🔗 Proje Bağlantıları:")
        for conn in connections:
            print(f"      • {conn['description']}")

    print("\n" + "=" * 60)


def do_project_detail(projects: list, project_name: str) -> None:
    """Belirli bir projenin detayını gösterir."""
    matching = [p for p in projects if project_name.lower() in p.name.lower()]

    if not matching:
        print(f"❌ '{project_name}' adında bir proje bulunamadı.")
        print("📁 Mevcut projeler:")
        for p in sorted(projects, key=lambda x: x.name):
            print(f"   • {p.name}")
        return

    for p in matching:
        print(f"\n{'=' * 60}")
        print(f"📁 {p.name}")
        print(f"{'=' * 60}")
        print(f"  📂 Yol          : {p.path}")
        print(f"  🏷️  Kategori     : {p.category}")
        print(f"  🗣️  Birincil Dil  : {p.primary_language}")
        print(f"  📊 Olgunluk     : {p.maturity}")
        print(f"  📄 Dosya Sayısı : {p.stats.total_files}")
        print(f"  💻 Kod Dosyası  : {p.stats.code_files}")
        print(f"  📝 Toplam Satır : {p.stats.total_lines:,}")
        print(f"  💾 Boyut        : {p.total_size_mb} MB")

        if p.frameworks:
            print(f"  🔧 Frameworkler : {', '.join(p.frameworks)}")
        if p.ai_services:
            print(f"  🧠 AI Servisleri: {', '.join(p.ai_services)}")
        if p.dependencies:
            print(f"  📦 Bağımlılıklar: {', '.join(p.dependencies)}")
        if p.has_git:
            print(f"  🔀 Git          : ✅")
        if p.has_tests:
            print(f"  🧪 Testler      : ✅")
        if p.has_ci:
            print(f"  🚀 CI/CD        : ✅")

        if p.stats.languages:
            print(f"\n  📊 Dil Dağılımı:")
            for lang, count in sorted(p.stats.languages.items(),
                                       key=lambda x: x[1], reverse=True):
                print(f"      {lang:15s} : {count} dosya")

        if p.stats.largest_file:
            print(f"\n  📏 En Büyük Dosya: {p.stats.largest_file} "
                  f"({p.stats.largest_file_lines:,} satır)")

        if p.description:
            print(f"\n  📖 Açıklama:")
            print(f"      {p.description[:500]}")

        print()


def do_search(projects: list, query: str, deep: bool = False, filetype: str = None) -> None:
    """Projelerde arama yapar.
    
    Arama alanları:
        - Proje adı
        - Kategori / Dil / Framework / AI servisleri
        - README içeriği
        - Dosya adları
        - (--deep) Dosya içerikleri (kod dosyalarında grep)
    
    Args:
        filetype: Sadece belirli dosya türünde ara (ör: 'md', 'py', 'js')
    """
    import os
    q = query.lower()
    # Dosya türü filtresi normalize et
    ft = None
    if filetype:
        ft = filetype.lower().strip('.')
        ft = f".{ft}"  # ".md", ".py" formatına çevir
    
    print(f"\n{'=' * 60}")
    print(f"🔍 ARAMA: '{query}'")
    if ft:
        print(f"📎 Dosya türü filtresi: *{ft}")
    print(f"{'=' * 60}")

    total_hits = 0

    for p in projects:
        matches = []  # (alan, detay)

        # 1) Proje adı
        if q in p.name.lower():
            matches.append(("📁 Proje Adı", p.name))

        # 2) Kategori
        if q in p.category.lower():
            matches.append(("🏷️  Kategori", p.category))

        # 3) Dil
        if q in p.primary_language.lower():
            matches.append(("🗣️  Dil", p.primary_language))

        # 4) Framework
        fw_hits = [fw for fw in (p.frameworks or []) if q in fw.lower()]
        if fw_hits:
            matches.append(("🔧 Framework", ", ".join(fw_hits)))

        # 5) AI servisleri
        ai_hits = [ai for ai in (p.ai_services or []) if q in ai.lower()]
        if ai_hits:
            matches.append(("🧠 AI Servisi", ", ".join(ai_hits)))

        # 6) Bağımlılık dosyaları
        dep_hits = [d for d in (p.dependencies or []) if q in d.lower()]
        if dep_hits:
            matches.append(("📦 Bağımlılık", ", ".join(dep_hits)))

        # 7) README içeriği
        readme = getattr(p, 'readme_summary', '') or ''
        if q in readme.lower():
            # Eşleşen bölümü göster
            idx = readme.lower().index(q)
            start = max(0, idx - 40)
            end = min(len(readme), idx + len(query) + 40)
            snippet = readme[start:end].replace('\n', ' ')
            if start > 0:
                snippet = '...' + snippet
            if end < len(readme):
                snippet = snippet + '...'
            matches.append(("📖 README", snippet))

        # 8) Dosya adlarında arama
        file_list = getattr(p, 'files', []) or []
        if ft:
            # Dosya türü filtresi: sadece belirtilen uzantıdaki dosyalarda ara
            file_hits = [f.name for f in file_list 
                         if f.extension.lower() == ft and q in f.name.lower()]
        else:
            file_hits = [f.name for f in file_list if q in f.name.lower()]
        if file_hits:
            shown = file_hits[:5]
            extra = f" (+{len(file_hits)-5} daha)" if len(file_hits) > 5 else ""
            matches.append(("📄 Dosya Adı", ", ".join(shown) + extra))

        # 9) Dil dağılımında arama
        lang_hits = [l for l in (p.stats.languages or {}) if q in l.lower()]
        if lang_hits and not any(m[0] == "🗣️  Dil" for m in matches):
            matches.append(("🗣️  Alt Dil", ", ".join(lang_hits)))

        # 10) Derin arama: dosya içerikleri
        if deep and os.path.isdir(p.path):
            content_hits = _deep_search(p.path, query, filetype=ft)
            if content_hits:
                matches.append(("🔎 İçerik", ""))
                for fpath, line_no, line_text in content_hits[:5]:
                    rel = os.path.relpath(fpath, p.path)
                    matches.append((f"   └ {rel}:{line_no}", line_text.strip()[:80]))
                if len(content_hits) > 5:
                    matches.append(("   └ ...", f"+{len(content_hits)-5} sonuç daha"))

        if matches:
            total_hits += 1
            lang_str = p.primary_language
            cat_str = p.category
            stats_str = f"{p.stats.code_files} kod, {p.stats.total_lines:,} satır"
            print(f"\n  📁 {p.name}  [{cat_str} · {lang_str} · {stats_str}]")
            print(f"     📂 {p.path}")
            for label, detail in matches:
                if detail:
                    print(f"     {label}: {detail}")
                else:
                    print(f"     {label}")

    print(f"\n{'=' * 60}")
    if total_hits == 0:
        print(f"  ❌ '{query}' için sonuç bulunamadı.")
        if not deep:
            print(f"  💡 Dosya içeriklerinde de aramak için: --search '{query}' --deep")
        if not ft:
            print(f"  💡 Sadece .md dosyalarında aramak için: --search '{query}' --deep --filetype md")
    else:
        print(f"  ✅ {total_hits} projede eşleşme bulundu.")
        if not deep:
            print(f"  💡 Dosya içeriklerinde de aramak için: --search '{query}' --deep")
        if not ft:
            print(f"  💡 Belirli dosya türünde aramak için: --filetype md (veya py, js, php...)")
    print(f"{'=' * 60}")


def _deep_search(project_path: str, query: str, max_results: int = 20, filetype: str = None) -> list:
    """Proje dosyalarının içinde metin arar.
    
    Args:
        filetype: Sadece belirli uzantıda ara (ör: '.md', '.py'). None ise tümü.
    
    Returns:
        list of (dosya_yolu, satır_no, satır_metni)
    """
    import os
    from config import CODE_EXTENSIONS, DOC_EXTENSIONS, CONFIG_FILES, EXCLUDED_DIRS

    searchable = set(CODE_EXTENSIONS) | set(DOC_EXTENSIONS) | set(CONFIG_FILES)
    results = []
    q_lower = query.lower()

    for root, dirs, files in os.walk(project_path):
        # Hariç tutulan dizinleri atla
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS and not d.startswith('.')]

        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            # Dosya türü filtresi varsa sadece o uzantıya bak
            if filetype:
                if ext != filetype:
                    continue
            elif ext not in searchable:
                continue

            fpath = os.path.join(root, fname)
            try:
                size = os.path.getsize(fpath)
                if size > 2 * 1024 * 1024:  # 2MB üstü atla
                    continue
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_no, line in enumerate(f, 1):
                        if q_lower in line.lower():
                            results.append((fpath, line_no, line))
                            if len(results) >= max_results:
                                return results
            except (PermissionError, OSError):
                continue

    return results


def do_diff() -> None:
    """Son iki taramayı karşılaştırır ve farkları gösterir."""
    comparator = ScanComparator()
    scans = comparator.list_scans()

    if len(scans) < 2:
        print("\n⚠️  Karşılaştırma için en az 2 tarama kaydı gerekli.")
        print(f"   Mevcut tarama sayısı: {len(scans)}")
        print("   Önce birden fazla tarama yapın: python main.py --scan")
        return

    diff = comparator.compare_latest()
    if diff is None:
        print("\n❌ Karşılaştırma yapılamadı.")
        return

    report_text = comparator.format_diff_report(diff)
    print("\n" + report_text)

    # Diff raporunu dosyaya kaydet
    diff_file = REPORTS_DIR / f"diff_{get_timestamp()}.txt"
    with open(diff_file, "w", encoding="utf-8") as f:
        f.write(report_text)
    logger.info(f"Diff raporu kaydedildi: {diff_file}")
    print(f"\n📄 Diff raporu: {diff_file}")


# ── İskelet ve Duplike Tespiti ──────────────────────────────────────

def do_skeleton(max_depth: int = 3) -> dict:
    """KINGSTON diskinin klasör iskeletini Finder tarzında çıkarır.
    Klasörler ve dosyalar birlikte listelenir.
    
    Returns:
        dict: İskelet verisi — folders, files, tree yapısı
    """
    import os
    import stat
    from config import SCAN_ROOT, EXCLUDED_DIRS, APP_EXCLUDED_SUFFIXES, CODE_EXTENSIONS, DOC_EXTENSIONS, CONFIG_FILES

    root = str(SCAN_ROOT)
    tree = []            # klasör listesi
    all_files = []       # dosya listesi
    folder_names = []    # duplike tespiti için
    folder_id = 0        # her klasöre benzersiz id

    # Dosya türü → ikon map
    EXT_ICONS = {
        ".py": "🐍", ".js": "🟨", ".ts": "🔷", ".jsx": "⚛️", ".tsx": "⚛️",
        ".php": "🐘", ".rs": "🦀", ".go": "🔵", ".java": "☕", ".c": "⚙️",
        ".cpp": "⚙️", ".h": "⚙️", ".swift": "🍎", ".rb": "💎",
        ".sh": "🐚", ".bash": "🐚", ".zsh": "🐚",
        ".md": "📝", ".txt": "📄", ".rst": "📄", ".pdf": "📕", ".doc": "📘", ".docx": "📘",
        ".json": "📋", ".yaml": "📋", ".yml": "📋", ".toml": "📋", ".xml": "📋",
        ".ini": "⚙️", ".cfg": "⚙️", ".env": "🔒",
        ".html": "🌐", ".css": "🎨", ".scss": "🎨", ".less": "🎨",
        ".png": "🖼️", ".jpg": "🖼️", ".jpeg": "🖼️", ".gif": "🖼️", ".svg": "🖼️",
        ".ico": "🖼️", ".webp": "🖼️", ".bmp": "🖼️",
        ".mp3": "🎵", ".wav": "🎵", ".ogg": "🎵", ".flac": "🎵",
        ".mp4": "🎬", ".avi": "🎬", ".mov": "🎬", ".mkv": "🎬", ".webm": "🎬",
        ".zip": "📦", ".tar": "📦", ".gz": "📦", ".rar": "📦", ".7z": "📦",
        ".sql": "🗃️", ".db": "🗃️", ".sqlite": "🗃️",
        ".lock": "🔒", ".log": "📜", ".csv": "📊", ".xls": "📊", ".xlsx": "📊",
    }

    def _file_icon(name: str) -> str:
        ext = os.path.splitext(name)[1].lower()
        if ext in EXT_ICONS:
            return EXT_ICONS[ext]
        if name.lower() in {"makefile", "dockerfile", "license", "readme", ".gitignore"}:
            return "📋"
        return "📄"

    def _file_category(name: str) -> str:
        ext = os.path.splitext(name)[1].lower()
        if ext in CODE_EXTENSIONS:
            return "Kod"
        if ext in DOC_EXTENSIONS:
            return "Doküman"
        if ext in CONFIG_FILES:
            return "Ayar"
        if ext in {".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp", ".bmp"}:
            return "Görsel"
        if ext in {".mp3", ".wav", ".ogg", ".flac"}:
            return "Ses"
        if ext in {".mp4", ".avi", ".mov", ".mkv", ".webm"}:
            return "Video"
        if ext in {".zip", ".tar", ".gz", ".rar", ".7z"}:
            return "Arşiv"
        return "Diğer"

    def _human_size(size_bytes: int) -> str:
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

    print("\n" + "=" * 70)
    print("🗂️  KINGSTON KLASÖR İSKELETİ (Finder Modu)")
    print("=" * 70)

    for dirpath, dirnames, filenames in os.walk(root):
        # Hariç tutulan dizinleri çıkar
        dirnames[:] = sorted([
            d for d in dirnames
            if d not in EXCLUDED_DIRS
            and not d.startswith(".")
            and not any(d.endswith(s) for s in APP_EXCLUDED_SUFFIXES)
        ])

        rel = os.path.relpath(dirpath, root)
        depth = 0 if rel == "." else rel.count(os.sep) + 1

        if max_depth > 0 and depth > max_depth:
            dirnames.clear()
            continue

        # Dosyaları filtrele (gizli dosyaları atla)
        visible_files = sorted([f for f in filenames if not f.startswith(".")])

        # Kod dosyası var mı?
        has_code = any(
            os.path.splitext(f)[1].lower() in CODE_EXTENSIONS
            for f in visible_files
        )

        # Klasör türünü belirle
        folder_type = "📂"
        marker_files = {"package.json", "requirements.txt", "Cargo.toml", "composer.json",
                        "go.mod", "Makefile", "setup.py", "pyproject.toml", "artisan"}
        has_marker = bool(set(visible_files) & marker_files)
        has_readme = any(f.lower().startswith("readme") for f in visible_files)

        if has_marker:
            folder_type = "📦 Proje"
        elif has_code:
            folder_type = "💻 Kod"
        elif has_readme:
            folder_type = "📖 Dokümantasyon"
        elif len(visible_files) == 0 and len(dirnames) == 0:
            folder_type = "📭 Boş"

        name = os.path.basename(dirpath) if rel != "." else "KINGSTON"
        display_name = rel if rel != "." else "/"

        # Klasör boyutunu hesapla (sadece doğrudan dosyalar)
        folder_size = 0
        for fn in visible_files:
            try:
                fp = os.path.join(dirpath, fn)
                folder_size += os.path.getsize(fp)
            except OSError:
                pass

        folder_id += 1
        parent_rel = os.path.dirname(rel) if rel != "." else ""

        entry = {
            "id": folder_id,
            "name": name,
            "path": dirpath,
            "rel_path": display_name,
            "parent_path": parent_rel if parent_rel != "." else "/",
            "depth": depth,
            "subdirs": len(dirnames),
            "files": len(visible_files),
            "has_code": has_code,
            "type": folder_type,
            "size": folder_size,
            "size_human": _human_size(folder_size),
        }
        tree.append(entry)

        if rel != ".":
            folder_names.append({"name": name, "path": dirpath, "depth": depth})

        # Her dosyanın detayını kaydet
        for fn in visible_files:
            fp = os.path.join(dirpath, fn)
            try:
                st_info = os.stat(fp)
                fsize = st_info.st_size
                fmod = datetime.fromtimestamp(st_info.st_mtime).strftime("%Y-%m-%d %H:%M")
            except OSError:
                fsize = 0
                fmod = ""

            ext = os.path.splitext(fn)[1].lower()
            file_entry = {
                "name": fn,
                "path": fp,
                "folder_path": display_name,
                "folder_id": folder_id,
                "depth": depth,
                "ext": ext,
                "icon": _file_icon(fn),
                "category": _file_category(fn),
                "size": fsize,
                "size_human": _human_size(fsize),
                "modified": fmod,
            }
            all_files.append(file_entry)

        # Görsel ağaç çizimi
        indent = "│   " * depth
        file_info = f"{len(visible_files)} dosya" if visible_files else ""
        sub_info = f"{len(dirnames)} alt" if dirnames else ""
        parts = [p for p in [file_info, sub_info] if p]
        meta = f" ({', '.join(parts)})" if parts else ""
        print(f"  {indent}├── {folder_type} {name}{meta}")

    print(f"\n  📊 Toplam: {len(tree)} klasör, {len(all_files)} dosya")

    # Dosya istatistikleri
    total_size = sum(f["size"] for f in all_files)
    cat_counts = {}
    for f in all_files:
        cat = f["category"]
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
    cat_str = ", ".join(f"{k}: {v}" for k, v in sorted(cat_counts.items(), key=lambda x: -x[1]))
    print(f"  💾 Toplam boyut: {_human_size(total_size)}")
    print(f"  📎 Dosya türleri: {cat_str}")

    # İskelet verisini kaydet
    skeleton_data = {
        "scan_date": datetime.now().isoformat(),
        "scan_root": root,
        "max_depth": max_depth,
        "total_folders": len(tree),
        "total_files": len(all_files),
        "total_size": total_size,
        "total_size_human": _human_size(total_size),
        "file_categories": cat_counts,
        "folders": tree,
        "files": all_files,
        "folder_names": folder_names,
    }

    skeleton_file = DATA_DIR / "iskelet.json"
    with open(skeleton_file, "w", encoding="utf-8") as f:
        json.dump(skeleton_data, f, ensure_ascii=False, indent=2)
    print(f"  💾 Kaydedildi: {skeleton_file}")

    # ── Okunabilir Harita Dosyası (harita.md) ────────────────────────
    harita_file = DATA_DIR / "harita.md"
    print(f"\n  📝 Harita dosyası oluşturuluyor...")

    # Klasör → dosyaları grupla
    folder_files_map = {}
    for fi in all_files:
        fid = fi.get("folder_id", 0)
        folder_files_map.setdefault(fid, []).append(fi)

    lines = []
    lines.append("# 🗺️ KINGSTON — Tam Dosyalama Haritası\n")
    lines.append(f"📅 Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"📂 Toplam Klasör: {len(tree):,}")
    lines.append(f"📄 Toplam Dosya: {len(all_files):,}")
    lines.append(f"💾 Toplam Boyut: {_human_size(total_size)}")
    lines.append(f"📏 Tarama Derinliği: {'Sınırsız' if max_depth == 0 else max_depth}\n")
    lines.append("---\n")

    for folder in tree:
        depth = folder.get("depth", 0)
        indent = "  " * depth
        ftype = folder.get("type", "📂")
        fname = folder.get("name", "")
        fsize = folder.get("size_human", "")
        subdirs = folder.get("subdirs", 0)
        fcount = folder.get("files", 0)

        meta_parts = []
        if fcount:
            meta_parts.append(f"{fcount} dosya")
        if subdirs:
            meta_parts.append(f"{subdirs} alt klasör")
        if fsize and fsize != "0 B":
            meta_parts.append(fsize)
        meta = f"  *({', '.join(meta_parts)})*" if meta_parts else ""

        lines.append(f"{indent}- **{ftype} {fname}**{meta}")

        # Bu klasördeki dosyaları listele
        fid = folder.get("id", 0)
        folder_files = folder_files_map.get(fid, [])
        for fi in sorted(folder_files, key=lambda x: x["name"].lower()):
            icon = fi.get("icon", "📄")
            finame = fi.get("name", "")
            fisize = fi.get("size_human", "")
            fimod = fi.get("modified", "")
            ficat = fi.get("category", "")
            detail_parts = [fisize]
            if ficat and ficat != "Diğer":
                detail_parts.append(ficat)
            if fimod:
                detail_parts.append(fimod)
            detail = f"  `{' · '.join(p for p in detail_parts if p)}`"
            lines.append(f"{indent}  - {icon} {finame}{detail}")

    # Özet bölümü
    lines.append("\n---\n")
    lines.append("## 📊 Özet İstatistikler\n")
    lines.append(f"| Metrik | Değer |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Toplam Klasör | {len(tree):,} |")
    lines.append(f"| Toplam Dosya | {len(all_files):,} |")
    lines.append(f"| Toplam Boyut | {_human_size(total_size)} |")
    lines.append(f"| Tarama Derinliği | {'Sınırsız' if max_depth == 0 else max_depth} |")
    lines.append("")
    lines.append("### Dosya Kategorileri\n")
    lines.append("| Kategori | Sayı |")
    lines.append("|----------|------|")
    for cat, cnt in sorted(cat_counts.items(), key=lambda x: -x[1]):
        lines.append(f"| {cat} | {cnt:,} |")

    # Klasör türleri
    folder_type_counts = {}
    for f in tree:
        t = f.get("type", "📂")
        folder_type_counts[t] = folder_type_counts.get(t, 0) + 1
    lines.append("")
    lines.append("### Klasör Türleri\n")
    lines.append("| Tür | Sayı |")
    lines.append("|-----|------|")
    for ft, cnt in sorted(folder_type_counts.items(), key=lambda x: -x[1]):
        lines.append(f"| {ft} | {cnt:,} |")

    with open(harita_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"  🗺️  Harita dosyası: {harita_file}")
    print(f"  📊 {len(lines)} satır yazıldı")

    return skeleton_data


def do_find_dupes(skeleton_data: dict = None) -> list:
    """Aynı isimli klasörleri bulur ve raporlar.
    
    Returns:
        list: [{name, count, locations: [{path, depth, files, type}]}]
    """
    from collections import defaultdict

    # İskelet verisi yoksa dosyadan yükle
    if skeleton_data is None:
        skeleton_file = DATA_DIR / "iskelet.json"
        if skeleton_file.exists():
            with open(skeleton_file, "r", encoding="utf-8") as f:
                skeleton_data = json.load(f)
        else:
            print("\n⚠️  Önce iskelet çıkarın: python main.py --skeleton")
            return []

    folder_names = skeleton_data.get("folder_names", [])
    if not folder_names:
        print("\n⚠️  Klasör verisi bulunamadı.")
        return []

    # İsme göre grupla
    groups = defaultdict(list)
    for item in folder_names:
        groups[item["name"].lower().strip()].append(item)

    # Sadece birden fazla olanları al ve sayıya göre sırala
    dupes = []
    for name, locations in sorted(groups.items(), key=lambda x: -len(x[1])):
        if len(locations) > 1:
            dupes.append({
                "name": locations[0]["name"],  # Orijinal case
                "count": len(locations),
                "locations": locations,
            })

    # Raporla
    print("\n" + "=" * 70)
    print("🔍 AYNI İSİMLİ KLASÖRLER")
    print("=" * 70)

    if not dupes:
        print("  ✅ Aynı isimli klasör bulunamadı.")
        return []

    total_dupes = sum(d["count"] for d in dupes)
    print(f"  📊 {len(dupes)} farklı isimde toplam {total_dupes} tekrarlanan klasör\n")

    for d in dupes:
        print(f"  📁 {d['name']}  ×{d['count']}")
        for loc in d["locations"]:
            rel = loc.get("path", "").replace(str(SCAN_ROOT) + "/", "")
            print(f"      └─ {rel}")
        print()

    # Duplike verisini kaydet
    dupes_file = DATA_DIR / "duplikeler.json"
    with open(dupes_file, "w", encoding="utf-8") as f:
        json.dump({
            "scan_date": datetime.now().isoformat(),
            "total_duplicate_names": len(dupes),
            "total_duplicate_folders": total_dupes,
            "duplicates": dupes,
        }, f, ensure_ascii=False, indent=2)
    print(f"  💾 Kaydedildi: {dupes_file}")

    return dupes


def main() -> None:
    print(BANNER)

    parser = argparse.ArgumentParser(
        description="Emare Katip — KINGSTON Veri Toplayıcı & Analizcisi"
    )
    parser.add_argument("--scan", action="store_true",
                        help="KINGSTON diskini tara")
    parser.add_argument("--depth", type=int, default=None,
                        help="Tarama derinliği (varsayılan: 3, 0=sınırsız)")
    parser.add_argument("--lang", type=str, default=None,
                        help="Sadece bu dildeki projeleri tara (ör: python, javascript, rust)")
    parser.add_argument("--category", type=str, default=None,
                        help="Sadece bu kategorideki projeleri tara (ör: ai, web, bot)")
    parser.add_argument("--min-files", type=int, default=0,
                        help="Minimum dosya sayısı filtresi (varsayılan: 0)")
    parser.add_argument("--include-empty", action="store_true",
                        help="Boş projeleri de dahil et")
    parser.add_argument("--no-skip-dupes", action="store_true",
                        help="Kopya klasörleri (yedek/kopyası) atlama")
    parser.add_argument("--scan-filetype", type=str, default=None,
                        help="Sadece bu dosya türünü içeren projeleri tara (ör: md, py, js, rs)")
    parser.add_argument("--skeleton", action="store_true",
                        help="KINGSTON klasör iskeletini çıkar")
    parser.add_argument("--find-dupes", action="store_true",
                        help="Aynı isimli klasörleri bul")
    parser.add_argument("--report", action="store_true",
                        help="Son tarama verilerinden rapor üret")
    parser.add_argument("--summary", action="store_true",
                        help="Kısa özet göster")
    parser.add_argument("--project", type=str, default=None,
                        help="Belirli bir projenin detayını göster")
    parser.add_argument("--all", action="store_true",
                        help="Tam tarama + rapor + özet (varsayılan)")
    parser.add_argument("--diff", action="store_true",
                        help="Son iki taramayı karşılaştır")
    parser.add_argument("--search", type=str, default=None,
                        help="Projeler içinde arama yap (ad, dil, dosya, içerik)")
    parser.add_argument("--deep", action="store_true",
                        help="--search ile birlikte: dosya içeriklerinde de ara")
    parser.add_argument("--filetype", type=str, default=None,
                        help="--search ile birlikte: sadece belirli uzantıda ara (ör: md, py, js)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Detaylı log çıktısı (DEBUG seviyesi)")

    args = parser.parse_args()

    # Loglama ve dizinleri kur
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(level=log_level, console=True)

    # Hiçbir flag verilmemişse --all gibi davran
    if not (args.scan or args.report or args.summary or args.project or args.diff or args.search or args.skeleton or args.find_dupes):
        args.all = True

    projects = None

    # Tarama
    if args.scan or args.all:
        projects = do_scan(
            max_depth=args.depth,
            language_filter=args.lang,
            min_files=args.min_files,
            include_empty=args.include_empty,
            skip_duplicates=not args.no_skip_dupes,
            category_filter=args.category,
            filetype_filter=args.scan_filetype,
        )

    # Projeleri yükle (tarama yapılmadıysa son veriden)
    if projects is None:
        scan_data = load_last_scan()
        if scan_data is None:
            return
        # Basitleştirilmiş ProjectInfo yeniden oluştur
        from models.project import ProjectInfo, ProjectStats
        projects = []
        for pd_data in scan_data.get("projects", []):
            stats = ProjectStats(
                total_files=pd_data.get("stats", {}).get("total_files", 0),
                total_dirs=pd_data.get("stats", {}).get("total_dirs", 0),
                total_size_bytes=pd_data.get("stats", {}).get("total_size_bytes", 0),
                total_lines=pd_data.get("stats", {}).get("total_lines", 0),
                code_files=pd_data.get("stats", {}).get("code_files", 0),
                doc_files=pd_data.get("stats", {}).get("doc_files", 0),
                config_files=pd_data.get("stats", {}).get("config_files", 0),
                data_files=pd_data.get("stats", {}).get("data_files", 0),
                languages=pd_data.get("stats", {}).get("languages", {}),
                largest_file=pd_data.get("stats", {}).get("largest_file"),
                largest_file_lines=pd_data.get("stats", {}).get("largest_file_lines", 0),
            )
            pi = ProjectInfo(
                name=pd_data.get("name", ""),
                path=pd_data.get("path", ""),
                project_type=pd_data.get("project_type", ""),
                primary_language=pd_data.get("primary_language", ""),
                description=pd_data.get("description", ""),
                maturity=pd_data.get("maturity", ""),
                category=pd_data.get("category", ""),
                readme_summary=pd_data.get("readme_summary", ""),
                stats=stats,
                has_git=pd_data.get("has_git", False),
                has_tests=pd_data.get("has_tests", False),
                has_docs=pd_data.get("has_docs", False),
                has_ci=pd_data.get("has_ci", False),
                frameworks=pd_data.get("frameworks", []),
                ai_services=pd_data.get("ai_services", []),
                dependencies=pd_data.get("dependencies", []),
                git_info=pd_data.get("git_info", {}),
            )
            projects.append(pi)

    # Rapor
    if args.report or args.all:
        md_file, json_file, html_file, csv_file = do_report(projects)
        print(f"\n✅ Raporlar hazır:")
        print(f"   📝 Markdown: {md_file}")
        print(f"   📊 JSON    : {json_file}")
        print(f"   🌐 HTML    : {html_file}")
        print(f"   📄 CSV     : {csv_file}")

    # Özet
    if args.summary or args.all:
        do_summary(projects)

    # Karşılaştırma
    if args.diff:
        do_diff()

    # Proje detayı
    if args.project:
        do_project_detail(projects, args.project)

    # Arama
    if args.search:
        do_search(projects, args.search, deep=args.deep, filetype=args.filetype)

    # İskelet
    skeleton_data = None
    if args.skeleton or args.find_dupes:
        _sk_depth = args.depth if args.depth is not None else 4
        skeleton_data = do_skeleton(max_depth=_sk_depth)

    # Duplike tespiti
    if args.find_dupes:
        do_find_dupes(skeleton_data)

    print("\n✨ Emare Katip işlemi tamamlandı.\n")


if __name__ == "__main__":
    try:
        main()
    except DiskNotFoundError as e:
        print(f"\n❌ {e}")
        print("💡 KINGSTON diskinin bağlı olduğundan emin olun.")
        sys.exit(1)
    except EmareKatipError as e:
        logging.getLogger("emare_katip").error(str(e))
        print(f"\n❌ Hata: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  İşlem kullanıcı tarafından iptal edildi.")
        sys.exit(130)
    except Exception as e:
        logging.getLogger("emare_katip").exception("Beklenmeyen hata")
        print(f"\n❌ Beklenmeyen hata: {e}")
        sys.exit(1)
