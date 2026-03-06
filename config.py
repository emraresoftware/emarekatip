"""
Emare Katip - Konfigürasyon Modülü
===================================
KINGSTON diskindeki projeleri tarayan ve kataloglayan sistemin ayarları.
config.yaml varsa ondan okur, yoksa varsayılanları kullanır.
"""

import os
import logging
from pathlib import Path
from datetime import datetime
from typing import Any, Dict

# ── YAML desteği (opsiyonel) ─────────────────────────────────────────
try:
    import yaml
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False

# ── Temel Yollar ──────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.resolve()
KINGSTON_ROOT = BASE_DIR.parent  # /Volumes/KINGSTON
CONFIG_YAML = BASE_DIR / "config.yaml"
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"


def _load_yaml_config() -> Dict[str, Any]:
    """config.yaml varsa yükler, yoksa boş dict döner."""
    if not _HAS_YAML or not CONFIG_YAML.exists():
        return {}
    try:
        with open(CONFIG_YAML, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return data
    except Exception:
        return {}


_YAML = _load_yaml_config()


def yaml_get(*keys, default=None):
    """YAML config'den iç içe anahtar okur.

    Örnek: yaml_get("scan", "max_depth", default=0)
    """
    node = _YAML
    for k in keys:
        if isinstance(node, dict):
            node = node.get(k)
        else:
            return default
        if node is None:
            return default
    return node


# ── Taranan Kök Dizin ────────────────────────────────────────────────
_scan_root_override = yaml_get("scan", "root", default="")
SCAN_ROOT = Path(_scan_root_override) if _scan_root_override else KINGSTON_ROOT

# ── Hariç Tutulan Klasörler ──────────────────────────────────────────
_DEFAULT_EXCLUDED = {
    ".DS_Store",
    ".DocumentRevisions-V100",
    ".Spotlight-V100",
    ".TemporaryItems",
    ".Trashes",
    ".fseventsd",
    ".com.apple.timemachine.supported",
    "__pycache__",
    "node_modules",
    ".git",
    ".venv",
    "venv",
    "vendor",
    ".idea",
    ".vscode",
    "Visual Studio Code.app",
    "WinBox.app",
    "VSCode-darwin-universal.zip",
    "Emare Katip",           # Kendimizi taramayalım
    "EmareKatip",            # Eski boş klasör
    "Obsidian Vault",        # Dev yedek klasör
    "SoftMaker",             # Dev uygulama klasörü
    "SOMBRERO_OS_V314_PORTABLE",  # Portatif OS
    "Wav2Lip",               # Büyük ML model dizini
}

# .app uzantılı macOS uygulamalarını atlamak için ek kontrol
APP_EXCLUDED_SUFFIXES = {".app"}

# Rekürsif taramada maksimum derinlik (0 = sınırsız)
MAX_SCAN_DEPTH = yaml_get("scan", "max_depth", default=3)
_yaml_excluded = yaml_get("scan", "excluded_dirs", default=None)
EXCLUDED_DIRS = set(_yaml_excluded) if _yaml_excluded else _DEFAULT_EXCLUDED

# ── Desteklenen Dosya Uzantıları ─────────────────────────────────────
CODE_EXTENSIONS = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".jsx": "React JSX",
    ".tsx": "React TSX",
    ".php": "PHP",
    ".rs": "Rust",
    ".go": "Go",
    ".java": "Java",
    ".c": "C",
    ".cpp": "C++",
    ".h": "C/C++ Header",
    ".swift": "Swift",
    ".rb": "Ruby",
    ".sh": "Shell",
    ".bash": "Bash",
    ".zsh": "Zsh",
}

DOC_EXTENSIONS = {
    ".md": "Markdown",
    ".txt": "Text",
    ".rst": "reStructuredText",
    ".pdf": "PDF",
    ".doc": "Word",
    ".docx": "Word",
}

CONFIG_FILES = {
    ".json": "JSON",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".toml": "TOML",
    ".ini": "INI",
    ".cfg": "Config",
    ".env": "Environment",
    ".xml": "XML",
}

DATA_EXTENSIONS = {
    ".csv": "CSV",
    ".sqlite": "SQLite",
    ".db": "Database",
    ".sql": "SQL",
}

# ── Proje Tanıma Kuralları ───────────────────────────────────────────
PROJECT_MARKERS = {
    "python": [
        "requirements.txt", "setup.py", "pyproject.toml",
        "Pipfile", "setup.cfg", "main.py", "app.py",
    ],
    "nodejs": [
        "package.json", "yarn.lock", "package-lock.json",
    ],
    "php_laravel": [
        "artisan", "composer.json",
    ],
    "rust": [
        "Cargo.toml", "Cargo.lock",
    ],
    "general": [
        "README.md", "README.txt", "readme.md",
    ],
}

# ── Rapor Ayarları ───────────────────────────────────────────────────
REPORT_TIMESTAMP_FORMAT = "%Y-%m-%d_%H-%M-%S"
REPORT_DATE_FORMAT = "%d %B %Y, %H:%M"

# ── Loglama ──────────────────────────────────────────────────────────
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "emare_katip.log"
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def ensure_dirs():
    """Gerekli dizinleri oluşturur."""
    for d in [DATA_DIR, REPORTS_DIR, LOG_DIR]:
        d.mkdir(parents=True, exist_ok=True)

def setup_logging(level: int = logging.INFO, console: bool = True) -> None:
    """Loglama sistemini yapılandırır.
    
    Args:
        level: Log seviyesi (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        console: Konsola da log yazılsın mı?
    """
    ensure_dirs()
    root_logger = logging.getLogger("emare_katip")
    root_logger.setLevel(level)
    root_logger.handlers.clear()

    # Dosya handler
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT))
    root_logger.addHandler(file_handler)

    # Konsol handler
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT))
        root_logger.addHandler(console_handler)

def get_logger(name: str) -> logging.Logger:
    """Modül için logger döndürür."""
    return logging.getLogger(f"emare_katip.{name}")

def get_timestamp():
    """Anlık zaman damgası döndürür."""
    return datetime.now().strftime(REPORT_TIMESTAMP_FORMAT)
