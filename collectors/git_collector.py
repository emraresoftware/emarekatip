"""
Emare Katip - Git Veri Toplayıcı
==================================
Git deposu bilgilerini toplar: commit sayısı, branch, son commit, remote URL.
"""

import subprocess
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Dict, List

from config import get_logger

logger = get_logger("collectors.git")


@dataclass
class GitInfo:
    """Git deposu bilgileri."""
    is_git_repo: bool = False
    total_commits: int = 0
    branch_count: int = 0
    current_branch: str = ""
    last_commit_date: str = ""
    last_commit_message: str = ""
    last_commit_author: str = ""
    remote_url: str = ""
    has_uncommitted_changes: bool = False
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "is_git_repo": self.is_git_repo,
            "total_commits": self.total_commits,
            "branch_count": self.branch_count,
            "current_branch": self.current_branch,
            "last_commit_date": self.last_commit_date,
            "last_commit_message": self.last_commit_message,
            "last_commit_author": self.last_commit_author,
            "remote_url": self.remote_url,
            "has_uncommitted_changes": self.has_uncommitted_changes,
            "tags": self.tags,
        }


class GitCollector:
    """Git deposu bilgilerini toplar."""

    TIMEOUT = 5  # saniye

    def _run_git(self, project_path: Path, *args: str) -> Optional[str]:
        """Git komutunu çalıştırır ve çıktısını döndürür."""
        try:
            result = subprocess.run(
                ["git", "-C", str(project_path)] + list(args),
                capture_output=True,
                text=True,
                timeout=self.TIMEOUT,
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
            logger.debug(f"Git komutu başarısız: {project_path} — {e}")
            return None

    def collect(self, project_path: Path) -> GitInfo:
        """Proje dizininden Git bilgilerini toplar.

        Args:
            project_path: Proje kök dizini

        Returns:
            GitInfo: Git deposu bilgileri
        """
        info = GitInfo()
        git_dir = project_path / ".git"

        if not git_dir.exists():
            return info

        info.is_git_repo = True
        logger.debug(f"Git bilgisi toplanıyor: {project_path.name}")

        # Toplam commit sayısı
        output = self._run_git(project_path, "rev-list", "--count", "HEAD")
        if output:
            try:
                info.total_commits = int(output)
            except ValueError:
                pass

        # Mevcut branch
        output = self._run_git(project_path, "branch", "--show-current")
        if output:
            info.current_branch = output

        # Branch sayısı
        output = self._run_git(project_path, "branch", "--list")
        if output:
            branches = [b.strip().lstrip("* ") for b in output.split("\n") if b.strip()]
            info.branch_count = len(branches)

        # Son commit bilgileri
        output = self._run_git(project_path, "log", "-1", "--format=%ci||%s||%an")
        if output and "||" in output:
            parts = output.split("||", 2)
            info.last_commit_date = parts[0] if len(parts) > 0 else ""
            info.last_commit_message = parts[1][:200] if len(parts) > 1 else ""
            info.last_commit_author = parts[2] if len(parts) > 2 else ""

        # Remote URL
        output = self._run_git(project_path, "remote", "get-url", "origin")
        if output:
            info.remote_url = output

        # Uncommitted changes
        output = self._run_git(project_path, "status", "--porcelain")
        if output is not None:
            info.has_uncommitted_changes = len(output) > 0

        # Tags
        output = self._run_git(project_path, "tag", "--list")
        if output:
            info.tags = [t.strip() for t in output.split("\n") if t.strip()][:10]

        logger.debug(f"Git: {project_path.name} — {info.total_commits} commit, "
                     f"branch: {info.current_branch}")
        return info

    def collect_all(self, project_paths: List[Path]) -> Dict[str, GitInfo]:
        """Birden fazla proje için Git bilgilerini toplar.

        Args:
            project_paths: Proje dizinlerinin listesi

        Returns:
            Dict[str, GitInfo]: Proje adı → GitInfo haritası
        """
        results = {}
        for path in project_paths:
            try:
                results[path.name] = self.collect(path)
            except Exception as e:
                logger.warning(f"Git bilgisi toplanamadı: {path.name} — {e}")
                results[path.name] = GitInfo()
        return results
