"""
Emare Katip - Proje Veri Modeli
================================
Taranan her proje için veri yapıları.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict
from pathlib import Path
from datetime import datetime


@dataclass
class FileInfo:
    """Tek bir dosyanın bilgileri."""
    path: str
    name: str
    extension: str
    size_bytes: int
    language: str = "Bilinmeyen"
    line_count: int = 0
    category: str = "other"  # code, doc, config, data, other
    last_modified: Optional[str] = None


@dataclass
class ProjectStats:
    """Proje istatistikleri."""
    total_files: int = 0
    total_dirs: int = 0
    total_size_bytes: int = 0
    total_lines: int = 0
    code_files: int = 0
    doc_files: int = 0
    config_files: int = 0
    data_files: int = 0
    languages: Dict[str, int] = field(default_factory=dict)   # {"Python": 15, "JS": 3}
    largest_file: Optional[str] = None
    largest_file_lines: int = 0


@dataclass
class ProjectInfo:
    """Bir projenin tüm bilgileri."""
    name: str
    path: str
    project_type: str = "Bilinmeyen"          # python, nodejs, php_laravel, rust, general
    primary_language: str = "Bilinmeyen"
    description: str = ""
    version: str = ""
    maturity: str = "Bilinmeyen"              # Erken Aşama, Aktif, Tamamlanmış, Arşiv
    category: str = "Diğer"                   # AI, Web, Sistem, Araç, Bot, Platform
    readme_summary: str = ""
    stats: ProjectStats = field(default_factory=ProjectStats)
    files: List['FileInfo'] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    has_git: bool = False
    has_tests: bool = False
    has_docs: bool = False
    has_ci: bool = False
    frameworks: List[str] = field(default_factory=list)
    ai_services: List[str] = field(default_factory=list)  # ["Gemini", "OpenAI", ...]
    git_info: Dict[str, object] = field(default_factory=dict)       # GitInfo.to_dict() verileri
    scan_date: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def total_size_mb(self) -> float:
        return round(self.stats.total_size_bytes / (1024 * 1024), 2)

    def to_dict(self) -> Dict[str, object]:
        """Dict formatına dönüştürür."""
        return {
            "name": self.name,
            "path": self.path,
            "project_type": self.project_type,
            "primary_language": self.primary_language,
            "description": self.description,
            "version": self.version,
            "maturity": self.maturity,
            "category": self.category,
            "readme_summary": self.readme_summary,
            "stats": {
                "total_files": self.stats.total_files,
                "total_dirs": self.stats.total_dirs,
                "total_size_bytes": self.stats.total_size_bytes,
                "total_size_mb": self.total_size_mb,
                "total_lines": self.stats.total_lines,
                "code_files": self.stats.code_files,
                "doc_files": self.stats.doc_files,
                "config_files": self.stats.config_files,
                "data_files": self.stats.data_files,
                "languages": self.stats.languages,
                "largest_file": self.stats.largest_file,
                "largest_file_lines": self.stats.largest_file_lines,
            },
            "dependencies": self.dependencies,
            "has_git": self.has_git,
            "has_tests": self.has_tests,
            "has_docs": self.has_docs,
            "has_ci": self.has_ci,
            "frameworks": self.frameworks,
            "ai_services": self.ai_services,
            "git_info": self.git_info,
            "scan_date": self.scan_date,
            "file_count_by_category": {
                "code": self.stats.code_files,
                "doc": self.stats.doc_files,
                "config": self.stats.config_files,
                "data": self.stats.data_files,
            },
        }


@dataclass
class KingstonReport:
    """KINGSTON disk genel raporu."""
    scan_date: str = field(default_factory=lambda: datetime.now().isoformat())
    total_projects: int = 0
    total_files: int = 0
    total_size_mb: float = 0.0
    total_lines: int = 0
    projects: List['ProjectInfo'] = field(default_factory=list)
    language_distribution: Dict[str, int] = field(default_factory=dict)
    category_distribution: Dict[str, int] = field(default_factory=dict)
    ai_services_used: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        return {
            "scan_date": self.scan_date,
            "total_projects": self.total_projects,
            "total_files": self.total_files,
            "total_size_mb": self.total_size_mb,
            "total_lines": self.total_lines,
            "language_distribution": self.language_distribution,
            "category_distribution": self.category_distribution,
            "ai_services_used": self.ai_services_used,
            "projects": [p.to_dict() for p in self.projects],
        }
