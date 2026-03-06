"""
Emare Katip - Proje Analizcisi
================================
Taranan proje verilerini analiz eder, bağlantıları ve örüntüleri tespit eder.
"""

from typing import List, Dict
from collections import Counter

from models.project import ProjectInfo, KingstonReport


class ProjectAnalyzer:
    """Taranan projeleri analiz eder ve genel rapor oluşturur."""

    def __init__(self, projects: List[ProjectInfo]):
        self.projects = projects

    def get_language_distribution(self) -> Dict[str, int]:
        """Tüm projelerdeki dil dağılımını hesaplar."""
        lang_counter = Counter()
        for p in self.projects:
            for lang, count in p.stats.languages.items():
                lang_counter[lang] += count
        return dict(lang_counter.most_common())

    def get_category_distribution(self) -> Dict[str, int]:
        """Proje kategori dağılımı."""
        cat_counter = Counter(p.category for p in self.projects)
        return dict(cat_counter.most_common())

    def get_all_ai_services(self) -> List[str]:
        """Kullanılan tüm AI servislerini listeler."""
        services = set()
        for p in self.projects:
            services.update(p.ai_services)
        return sorted(services)

    def get_all_frameworks(self) -> List[str]:
        """Kullanılan tüm frameworkleri listeler."""
        frameworks = set()
        for p in self.projects:
            frameworks.update(p.frameworks)
        return sorted(frameworks)

    def get_projects_by_category(self) -> Dict[str, List[ProjectInfo]]:
        """Projeleri kategoriye göre gruplar."""
        groups = {}
        for p in self.projects:
            groups.setdefault(p.category, []).append(p)
        return groups

    def get_projects_by_language(self) -> Dict[str, List[ProjectInfo]]:
        """Projeleri birincil dile göre gruplar."""
        groups = {}
        for p in self.projects:
            groups.setdefault(p.primary_language, []).append(p)
        return groups

    def get_largest_projects(self, top_n: int = 10) -> List[ProjectInfo]:
        """En büyük projeleri döndürür (kod satırı sayısına göre)."""
        return sorted(self.projects, key=lambda p: p.stats.total_lines, reverse=True)[:top_n]

    def find_connections(self) -> List[Dict]:
        """Projeler arası bağlantıları tespit eder."""
        connections = []

        # Aynı AI servisini kullanan projeler
        ai_map = {}
        for p in self.projects:
            for svc in p.ai_services:
                ai_map.setdefault(svc, []).append(p.name)
        for svc, projs in ai_map.items():
            if len(projs) > 1:
                connections.append({
                    "type": "shared_ai_service",
                    "service": svc,
                    "projects": projs,
                    "description": f"{svc} kullanan projeler: {', '.join(projs)}",
                })

        # Aynı framework kullanan projeler
        fw_map = {}
        for p in self.projects:
            for fw in p.frameworks:
                fw_map.setdefault(fw, []).append(p.name)
        for fw, projs in fw_map.items():
            if len(projs) > 1:
                connections.append({
                    "type": "shared_framework",
                    "framework": fw,
                    "projects": projs,
                    "description": f"{fw} kullanan projeler: {', '.join(projs)}",
                })

        # İsim benzerliği olan projeler (Emare ailesi)
        emare_projects = [p.name for p in self.projects if "emare" in p.name.lower()]
        if len(emare_projects) > 1:
            connections.append({
                "type": "project_family",
                "family": "Emare",
                "projects": emare_projects,
                "description": f"Emare ailesi projeleri: {', '.join(emare_projects)}",
            })

        return connections

    def generate_report(self) -> KingstonReport:
        """Tüm verileri birleştirip genel rapor oluşturur."""
        report = KingstonReport()
        report.total_projects = len(self.projects)
        report.total_files = sum(p.stats.total_files for p in self.projects)
        report.total_size_mb = round(
            sum(p.stats.total_size_bytes for p in self.projects) / (1024 * 1024), 2
        )
        report.total_lines = sum(p.stats.total_lines for p in self.projects)
        report.projects = self.projects
        report.language_distribution = self.get_language_distribution()
        report.category_distribution = self.get_category_distribution()
        report.ai_services_used = self.get_all_ai_services()
        return report
