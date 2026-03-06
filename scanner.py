"""
Emare Katip - Disk Tarayıcı
=============================
KINGSTON diskini tarar, proje klasörlerini tespit eder.
"""

import os
from pathlib import Path
from typing import List, Tuple

from config import (
    SCAN_ROOT, EXCLUDED_DIRS, CODE_EXTENSIONS,
    DOC_EXTENSIONS, CONFIG_FILES, DATA_EXTENSIONS,
    PROJECT_MARKERS, MAX_SCAN_DEPTH, APP_EXCLUDED_SUFFIXES, get_logger,
)
from models.project import FileInfo, ProjectInfo, ProjectStats
from exceptions import ScanError, PermissionDeniedError, DiskNotFoundError
from collectors.git_collector import GitCollector

logger = get_logger("scanner")


class Scanner:
    """KINGSTON diskindeki projeleri ve dosyaları tarar."""

    def __init__(
        self,
        root: Path = None,
        max_depth: int = None,
        language_filter: str = None,
        min_files: int = 0,
        include_empty: bool = False,
        skip_duplicates: bool = True,
        category_filter: str = None,
        filetype_filter: str = None,
    ):
        self.root = root or SCAN_ROOT
        self.max_depth = max_depth if max_depth is not None else MAX_SCAN_DEPTH
        self.language_filter = language_filter.lower() if language_filter else None
        self.min_files = min_files
        self.include_empty = include_empty
        self.skip_duplicates = skip_duplicates
        self.category_filter = category_filter.lower() if category_filter else None
        # Dosya türü filtresi: ".md", ".py" vb. — sadece bu uzantılı dosyaları içeren projeleri göster
        if filetype_filter:
            ft = filetype_filter.lower().strip()
            self.filetype_filter = ft if ft.startswith('.') else f'.{ft}'
        else:
            self.filetype_filter = None
        self.discovered_projects: List[ProjectInfo] = []
        self.git_collector = GitCollector()
        # Duplike tespit: aynı içerikli projenin farklı konumlardaki kopyasını atla
        self._seen_fingerprints: set = set()

    def is_excluded(self, name: str) -> bool:
        """Hariç tutulan dizin/dosya mı?"""
        if name.startswith("."):
            return True
        if name in EXCLUDED_DIRS:
            return True
        # macOS .app paketleri ve benzeri atla
        suffix = Path(name).suffix.lower()
        if suffix in APP_EXCLUDED_SUFFIXES:
            return True
        return False

    def detect_project_type(self, path: Path) -> str:
        """Klasördeki dosyalara bakarak proje türünü tespit eder."""
        contents = set()
        try:
            for item in path.iterdir():
                contents.add(item.name)
        except PermissionError:
            return "general"

        for ptype, markers in PROJECT_MARKERS.items():
            if ptype == "general":
                continue
            for marker in markers:
                if marker in contents:
                    return ptype

        return "general"

    def categorize_file(self, ext: str) -> str:
        """Dosya uzantısına göre kategori döndürür."""
        if ext in CODE_EXTENSIONS:
            return "code"
        elif ext in DOC_EXTENSIONS:
            return "doc"
        elif ext in CONFIG_FILES:
            return "config"
        elif ext in DATA_EXTENSIONS:
            return "data"
        return "other"

    def get_language(self, ext: str) -> str:
        """Dosya uzantısına göre dil döndürür."""
        all_types = {**CODE_EXTENSIONS, **DOC_EXTENSIONS, **CONFIG_FILES, **DATA_EXTENSIONS}
        return all_types.get(ext, "Diğer")

    def count_lines(self, file_path: Path) -> int:
        """Dosyadaki satır sayısını sayar (metin dosyaları için)."""
        try:
            if file_path.stat().st_size > 5 * 1024 * 1024:  # 5MB'den büyük atla
                return 0
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return sum(1 for _ in f)
        except (PermissionError, OSError):
            return 0

    def scan_directory(self, dir_path: Path, max_files: int = 5000) -> Tuple[List[FileInfo], int]:
        """Bir dizini tarar, dosya listesi ve alt dizin sayısı döndürür.
        
        os.walk kullanarak hariç tutulan dizinlere hiç girmez (performans).
        max_files limiti aşılırsa tarama durur.
        """
        files = []
        dir_count = 0

        try:
            for root, dirs, filenames in os.walk(dir_path):
                # Hariç tutulan dizinleri in-place çıkar → os.walk o dizine girmez
                dirs[:] = [d for d in dirs if not self.is_excluded(d)]
                dir_count += len(dirs)

                for fname in filenames:
                    if fname.startswith("."):
                        continue
                    if len(files) >= max_files:
                        logger.warning(f"Dosya limiti ({max_files}) aşıldı, tarama kısaltılıyor: {dir_path.name}")
                        return files, dir_count

                    item = Path(root) / fname
                    ext = item.suffix.lower()
                    category = self.categorize_file(ext)
                    language = self.get_language(ext)

                    try:
                        st = item.stat()
                        size = st.st_size
                        mtime = st.st_mtime
                    except OSError:
                        size = 0
                        mtime = 0

                    line_count = 0
                    if category in ("code", "doc", "config"):
                        line_count = self.count_lines(item)

                    from datetime import datetime
                    fi = FileInfo(
                        path=str(item),
                        name=item.name,
                        extension=ext,
                        size_bytes=size,
                        language=language,
                        line_count=line_count,
                        category=category,
                        last_modified=datetime.fromtimestamp(mtime).isoformat() if mtime else None,
                    )
                    files.append(fi)

        except PermissionError:
            logger.warning(f"İzin hatası, bazı dosyalar atlandı: {dir_path}")

        return files, dir_count

    def build_stats(self, files: List[FileInfo], dir_count: int) -> ProjectStats:
        """Dosya listesinden istatistik oluşturur."""
        stats = ProjectStats()
        stats.total_files = len(files)
        stats.total_dirs = dir_count
        stats.total_size_bytes = sum(f.size_bytes for f in files)
        stats.total_lines = sum(f.line_count for f in files)

        languages = {}
        largest_file = None
        largest_lines = 0

        for f in files:
            if f.category == "code":
                stats.code_files += 1
                lang = f.language
                languages[lang] = languages.get(lang, 0) + 1
                if f.line_count > largest_lines:
                    largest_lines = f.line_count
                    largest_file = f.name
            elif f.category == "doc":
                stats.doc_files += 1
            elif f.category == "config":
                stats.config_files += 1
            elif f.category == "data":
                stats.data_files += 1

        stats.languages = languages
        stats.largest_file = largest_file
        stats.largest_file_lines = largest_lines
        return stats

    def extract_readme_summary(self, dir_path: Path) -> str:
        """README dosyasından ilk birkaç satırı çeker."""
        for name in ["README.md", "readme.md", "README.txt", "README"]:
            readme = dir_path / name
            if readme.exists():
                try:
                    with open(readme, "r", encoding="utf-8", errors="ignore") as f:
                        lines = []
                        for i, line in enumerate(f):
                            if i >= 10:
                                break
                            stripped = line.strip()
                            if stripped:
                                lines.append(stripped)
                        return " ".join(lines)[:500]
                except (PermissionError, OSError):
                    pass
        return ""

    def detect_features(self, dir_path: Path, files: List[FileInfo]) -> dict:
        """Proje özelliklerini tespit eder.
        
        Returns:
            dict: has_git, has_tests, has_docs, has_ci, frameworks, ai_services, dependencies
        """
        features = {
            "has_git": (dir_path / ".git").exists(),
            "has_tests": False,
            "has_docs": False,
            "has_ci": False,
            "frameworks": [],
            "ai_services": [],
            "dependencies": [],
        }

        file_names = {f.name for f in files}
        file_paths_str = " ".join(f.path for f in files)

        # Test dosyaları
        if any("test" in f.name.lower() for f in files) or (dir_path / "tests").exists():
            features["has_tests"] = True

        # Dokümantasyon
        if any(f.category == "doc" for f in files):
            features["has_docs"] = True

        # CI/CD
        if (dir_path / ".github" / "workflows").exists() or ".gitlab-ci.yml" in file_names:
            features["has_ci"] = True

        # Framework tespiti
        if "artisan" in file_names:
            features["frameworks"].append("Laravel")
        if "manage.py" in file_names:
            features["frameworks"].append("Django")
        if "Cargo.toml" in file_names:
            features["frameworks"].append("Rust/Cargo")
        if "vite.config.js" in file_names or "vite.config.ts" in file_names:
            features["frameworks"].append("Vite")
        if "next.config.js" in file_names:
            features["frameworks"].append("Next.js")

        # Bağımlılıkları oku
        for dep_file in ["requirements.txt", "package.json", "composer.json", "Cargo.toml"]:
            dep_path = dir_path / dep_file
            if dep_path.exists():
                try:
                    with open(dep_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        features["dependencies"].append(dep_file)

                        # AI servisleri tespit et
                        content_lower = content.lower()
                        if "openai" in content_lower:
                            features["ai_services"].append("OpenAI")
                        if "gemini" in content_lower or "google-generativeai" in content_lower:
                            features["ai_services"].append("Google Gemini")
                        if "anthropic" in content_lower or "claude" in content_lower:
                            features["ai_services"].append("Anthropic Claude")
                        if "ollama" in content_lower:
                            features["ai_services"].append("Ollama")
                        if "tavily" in content_lower:
                            features["ai_services"].append("Tavily")
                        if "huggingface" in content_lower or "transformers" in content_lower:
                            features["ai_services"].append("Hugging Face")

                        # Framework tespiti (package.json'dan)
                        if dep_file == "package.json":
                            if "express" in content_lower:
                                features["frameworks"].append("Express.js")
                            if "react" in content_lower:
                                features["frameworks"].append("React")
                            if "whatsapp-web.js" in content_lower:
                                features["frameworks"].append("WhatsApp Web.js")
                            if "streamlit" in content_lower:
                                features["frameworks"].append("Streamlit")

                        if dep_file == "requirements.txt":
                            if "flask" in content_lower:
                                features["frameworks"].append("Flask")
                            if "fastapi" in content_lower:
                                features["frameworks"].append("FastAPI")
                            if "streamlit" in content_lower:
                                features["frameworks"].append("Streamlit")
                            if "selenium" in content_lower:
                                features["frameworks"].append("Selenium")

                except (PermissionError, OSError):
                    pass

        # Dedup
        features["frameworks"] = list(set(features["frameworks"]))
        features["ai_services"] = list(set(features["ai_services"]))

        return features

    def classify_category(self, project_type: str, features: dict, readme: str) -> str:
        """Projenin kategorisini belirler."""
        readme_lower = readme.lower()
        frameworks = [f.lower() for f in features.get("frameworks", [])]

        if features.get("ai_services"):
            if "bot" in readme_lower or "whatsapp" in readme_lower:
                return "AI Bot"
            if "asistan" in readme_lower or "assistant" in readme_lower:
                return "AI Asistan"
            return "AI / Yapay Zeka"
        if "laravel" in frameworks or project_type == "php_laravel":
            return "Web Uygulama"
        if project_type == "rust":
            return "Sistem"
        if "bot" in readme_lower or "whatsapp" in readme_lower:
            return "Bot"
        if "express" in " ".join(frameworks):
            return "Web Servis"
        if "panel" in readme_lower or "dashboard" in readme_lower:
            return "Yönetim Paneli"
        return "Genel"

    def estimate_maturity(self, stats: ProjectStats, features: dict) -> str:
        """Proje olgunluk seviyesini tahmin eder."""
        if stats.total_files == 0:
            return "Boş"
        if stats.code_files <= 2 and stats.total_lines < 100:
            return "Erken Aşama"
        if features.get("has_tests") and features.get("has_ci"):
            return "Üretim Hazır"
        if stats.code_files > 10 or stats.total_lines > 2000:
            return "Aktif Geliştirme"
        if stats.code_files > 5:
            return "Geliştiriliyor"
        return "Prototip"

    def is_project_dir(self, path: Path) -> bool:
        """Bir dizinin proje dizini olup olmadığını kontrol eder.
        
        Proje marker dosyaları (README.md, requirements.txt, package.json vb.)
        veya kod dosyası içeriyorsa True döner.
        """
        try:
            contents = set()
            has_code = False
            for item in path.iterdir():
                contents.add(item.name)
                if item.is_file() and item.suffix.lower() in CODE_EXTENSIONS:
                    has_code = True
            
            # Proje marker kontrolü
            all_markers = []
            for markers in PROJECT_MARKERS.values():
                all_markers.extend(markers)
            
            if any(m in contents for m in all_markers):
                return True
            
            # Kod dosyası varsa proje sayılır
            if has_code:
                return True
                
            return False
        except PermissionError:
            return False

    def _process_directory(self, entry: Path) -> ProjectInfo | None:
        """Bir dizini proje olarak işler ve ProjectInfo döndürür."""
        project_type = self.detect_project_type(entry)
        files, dir_count = self.scan_directory(entry)

        if len(files) == 0 and not self.include_empty:
            logger.debug(f"Boş klasör atlanıyor: {entry.name}")
            return None

        # Min dosya filtresi
        if len(files) < self.min_files:
            logger.debug(f"Yetersiz dosya ({len(files)}<{self.min_files}), atlanıyor: {entry.name}")
            return None

        stats = self.build_stats(files, dir_count)
        readme_summary = self.extract_readme_summary(entry)
        features = self.detect_features(entry, files)
        git_info = self.git_collector.collect(entry)
        category = self.classify_category(project_type, features, readme_summary)
        maturity = self.estimate_maturity(stats, features)

        primary_language = "Bilinmeyen"
        if stats.languages:
            primary_language = max(stats.languages, key=stats.languages.get)

        # Dil filtresi
        if self.language_filter:
            lang_match = primary_language.lower() == self.language_filter
            sub_match = any(self.language_filter in l.lower() for l in stats.languages)
            if not lang_match and not sub_match:
                logger.debug(f"Dil filtresi eşleşmedi ({primary_language}), atlanıyor: {entry.name}")
                return None

        # Kategori filtresi
        if self.category_filter and self.category_filter not in category.lower():
            logger.debug(f"Kategori filtresi eşleşmedi ({category}), atlanıyor: {entry.name}")
            return None

        # Dosya türü filtresi: proje bu uzantıda dosya içeriyor mu?
        if self.filetype_filter:
            has_ft = any(f.extension.lower() == self.filetype_filter for f in files)
            if not has_ft:
                logger.debug(f"Dosya türü filtresi eşleşmedi ({self.filetype_filter}), atlanıyor: {entry.name}")
                return None

        # İç içe projelerde yolu göster: "30,08,2025/cetus"
        rel_path = entry.relative_to(self.root)
        display_name = str(rel_path)

        return ProjectInfo(
            name=display_name,
            path=str(entry),
            project_type=project_type,
            primary_language=primary_language,
            description=readme_summary[:200] if readme_summary else "",
            maturity=maturity,
            category=category,
            readme_summary=readme_summary,
            stats=stats,
            files=files,
            has_git=features["has_git"],
            has_tests=features["has_tests"],
            has_docs=features["has_docs"],
            has_ci=features["has_ci"],
            frameworks=features["frameworks"],
            ai_services=features["ai_services"],
            dependencies=features["dependencies"],
            git_info=git_info.to_dict() if git_info.is_git_repo else {},
        )

    def _is_duplicate_name(self, name: str) -> bool:
        """Zaten taranmış bir projenin kopyası mı kontrol eder."""
        name_lower = name.lower()
        # "kopyası", "backup", "yedek" gibi pattern'ler
        skip_words = ["kopyası", "kopyas", "backup", "yedek", "old", "bak"]
        return any(w in name_lower for w in skip_words)

    def _project_fingerprint(self, project: ProjectInfo) -> str:
        """Projenin içerik parmak izini oluşturur.
        
        Aynı klasör adı = aynı proje kopyası. İlk bulunan (en üst seviye) alınır.
        Dosya sayısı farklı olsa bile aynı isimli proje kopyaları atlanır.
        """
        basename = Path(project.path).name.lower().strip()
        return basename

    def _discover_projects(self, directory: Path, depth: int = 0) -> None:
        """Rekürsif olarak proje dizinlerini keşfeder.
        
        Bir dizin proje marker'ı içeriyorsa → proje olarak işle.
        İçermiyorsa → alt dizinlerine dal (maks derinliğe kadar).
        """
        if self.max_depth > 0 and depth >= self.max_depth:
            return

        try:
            entries = sorted(directory.iterdir())
        except PermissionError:
            logger.warning(f"İzin hatası: {directory}")
            return

        for entry in entries:
            if not entry.is_dir():
                continue
            if self.is_excluded(entry.name):
                continue

            rel = entry.relative_to(self.root)

            # Derinlik >0'daki kopyaları atla (kök seviyedeki orijinaller taranır)
            if self.skip_duplicates and depth > 0 and self._is_duplicate_name(entry.name):
                logger.debug(f"  ⏭️  Kopya atlanıyor: {rel}")
                continue

            logger.info(f"Taranıyor: {rel}")

            if self.is_project_dir(entry):
                # Bu bir proje — işle
                project = self._process_directory(entry)
                if project:
                    # Duplike kontrolü: aynı içerikli proje daha önce tarandı mı?
                    if self.skip_duplicates:
                        fp = self._project_fingerprint(project)
                        if fp in self._seen_fingerprints:
                            logger.info(f"  🔄 Kopya atlanıyor (zaten tarandı): {project.name}")
                            continue
                        self._seen_fingerprints.add(fp)

                    self.discovered_projects.append(project)
                    logger.info(f"  ✅ {project.name}: {project.stats.total_files} dosya, "
                                f"{project.stats.code_files} kod, {project.primary_language}, "
                                f"[{project.category}]")
            else:
                # Proje değil — alt dizinlere dal
                logger.debug(f"  📂 Alt dizinlere dalınıyor: {rel}")
                self._discover_projects(entry, depth + 1)

    def scan_projects(self) -> List[ProjectInfo]:
        """Kök dizindeki tüm projeleri rekürsif tarar ve döndürür.
        
        Proje marker'ı (README.md, requirements.txt, package.json vb.) veya 
        kod dosyası bulunan dizinler proje olarak algılanır. Marker'sız 
        dizinler ise alt dizinlerine dalınarak iç içe projeler keşfedilir.
        """
        logger.info(f"KINGSTON taranıyor: {self.root}")
        logger.info(f"Maksimum derinlik: {self.max_depth}")
        if self.language_filter:
            logger.info(f"Dil filtresi: {self.language_filter}")
        if self.category_filter:
            logger.info(f"Kategori filtresi: {self.category_filter}")
        if self.min_files > 0:
            logger.info(f"Min dosya: {self.min_files}")
        if self.filetype_filter:
            logger.info(f"Dosya türü filtresi: {self.filetype_filter}")
        self.discovered_projects = []

        if not self.root.exists():
            raise DiskNotFoundError(str(self.root))

        self._discover_projects(self.root, depth=0)

        logger.info(f"Toplam {len(self.discovered_projects)} proje bulundu.")
        return self.discovered_projects
