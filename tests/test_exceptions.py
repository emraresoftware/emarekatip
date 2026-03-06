"""
Emare Katip - Birim Testleri: Exceptions
==========================================
Özel hata sınıfları testleri.
"""

import pytest

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from exceptions import (
    EmareKatipError, ScanError, PermissionDeniedError,
    DiskNotFoundError, ReportError, DataError, ConfigError,
)


class TestExceptionHierarchy:
    """Exception hiyerarşi testleri."""

    def test_base_error(self):
        with pytest.raises(EmareKatipError):
            raise EmareKatipError("test")

    def test_scan_error_is_base(self):
        assert issubclass(ScanError, EmareKatipError)

    def test_permission_error_is_scan(self):
        assert issubclass(PermissionDeniedError, ScanError)

    def test_disk_not_found_is_scan(self):
        assert issubclass(DiskNotFoundError, ScanError)

    def test_report_error_is_base(self):
        assert issubclass(ReportError, EmareKatipError)

    def test_data_error_is_base(self):
        assert issubclass(DataError, EmareKatipError)

    def test_config_error_is_base(self):
        assert issubclass(ConfigError, EmareKatipError)


class TestExceptionMessages:
    """Exception mesaj testleri."""

    def test_scan_error_with_path(self):
        err = ScanError("dosya yok", "/some/path")
        assert "/some/path" in str(err)
        assert "Tarama hatası" in str(err)

    def test_scan_error_without_path(self):
        err = ScanError("genel hata")
        assert "Tarama hatası" in str(err)

    def test_permission_denied(self):
        err = PermissionDeniedError("/locked/dir")
        assert "izni reddedildi" in str(err).lower() or "Erişim" in str(err)
        assert err.path == "/locked/dir"

    def test_disk_not_found(self):
        err = DiskNotFoundError("/Volumes/KINGSTON")
        assert "bulunamadı" in str(err)

    def test_report_error_with_type(self):
        err = ReportError("yazılamadı", "markdown")
        assert "markdown" in str(err)
        assert err.report_type == "markdown"

    def test_data_error(self):
        err = DataError("bozuk JSON", "/data/file.json")
        assert "bozuk JSON" in str(err)
        assert err.file_path == "/data/file.json"

    def test_config_error(self):
        err = ConfigError("geçersiz ayar")
        assert "Konfigürasyon" in str(err)
