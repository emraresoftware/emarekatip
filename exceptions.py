"""
Emare Katip - Özel İstisnalar (Exceptions)
=============================================
Uygulama genelinde kullanılan özel hata sınıfları.
"""


class EmareKatipError(Exception):
    """Emare Katip temel hata sınıfı."""
    pass


class ScanError(EmareKatipError):
    """Tarama sırasında oluşan hatalar."""

    def __init__(self, message: str, path: str = ""):
        self.path = path
        super().__init__(f"Tarama hatası{f' ({path})' if path else ''}: {message}")


class PermissionDeniedError(ScanError):
    """Dizin/dosya okuma izni olmadığında."""

    def __init__(self, path: str):
        super().__init__("Erişim izni reddedildi", path)


class DiskNotFoundError(ScanError):
    """KINGSTON diski bulunamadığında."""

    def __init__(self, path: str):
        super().__init__(f"Disk bulunamadı: {path}", path)


class ReportError(EmareKatipError):
    """Rapor oluşturma sırasında oluşan hatalar."""

    def __init__(self, message: str, report_type: str = ""):
        self.report_type = report_type
        super().__init__(f"Rapor hatası{f' [{report_type}]' if report_type else ''}: {message}")


class DataError(EmareKatipError):
    """Veri okuma/yazma sırasında oluşan hatalar."""

    def __init__(self, message: str, file_path: str = ""):
        self.file_path = file_path
        super().__init__(f"Veri hatası{f' ({file_path})' if file_path else ''}: {message}")


class ConfigError(EmareKatipError):
    """Konfigürasyon hatası."""

    def __init__(self, message: str):
        super().__init__(f"Konfigürasyon hatası: {message}")
