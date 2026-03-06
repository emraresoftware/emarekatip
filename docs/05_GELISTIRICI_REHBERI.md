# 🛠️ Emare Katip — Geliştirici Rehberi

> Projeyi genişletmek, yeni modüller eklemek ve katkıda bulunmak için rehber.

---

## 🏗️ Geliştirme Ortamı

### Gereksinimler

```bash
# Python 3.7+ gerekli
python3 --version

# Harici bağımlılık yok — saf standart kütüphane
```

### Proje Yapısını Anlama

```
Emare Katip/
├── main.py                    # Orkestrasyon + CLI
├── config.py                  # Sabitler ve ayarlar
├── scanner.py                 # Tarama motoru
├── models/project.py          # Veri modelleri
├── analyzers/project_analyzer.py  # Analiz motoru
├── reporters/
│   ├── markdown_reporter.py   # MD çıktı
│   └── json_reporter.py       # JSON çıktı
├── collectors/                # 🔮 Genişletme noktası (boş)
├── data/                      # Çalışma zamanı verileri
├── reports/                   # Üretilen raporlar
└── logs/                      # Log dosyaları
```

---

## 🔌 Genişletme Rehberi

### 1. Yeni Programlama Dili Desteği Eklemek

[config.py](../config.py) dosyasındaki `CODE_EXTENSIONS` sözlüğüne yeni uzantı ekleyin:

```python
CODE_EXTENSIONS = {
    # ... mevcut diller ...
    ".kt": "Kotlin",
    ".scala": "Scala",
    ".dart": "Dart",
    ".lua": "Lua",
}
```

> Başka hiçbir dosyada değişiklik gerekmez. Tarayıcı bu haritayı otomatik kullanır.

---

### 2. Yeni Framework Tespiti Eklemek

[scanner.py](../scanner.py) dosyasındaki `detect_features()` metoduna yeni koşullar ekleyin:

```python
def detect_features(self, dir_path, files):
    # ... mevcut kod ...
    
    # Yeni framework tespiti — dosya adına göre
    if "angular.json" in file_names:
        features["frameworks"].append("Angular")
    
    # Yeni framework tespiti — bağımlılık dosyasından
    if dep_file == "package.json":
        if "vue" in content_lower:
            features["frameworks"].append("Vue.js")
        if "svelte" in content_lower:
            features["frameworks"].append("Svelte")
```

---

### 3. Yeni AI Servisi Tespiti Eklemek

Aynı `detect_features()` metodundaki AI servis kontrollerine ekleyin:

```python
# Mevcut AI servisleri bloğuna ekle
if "cohere" in content_lower:
    features["ai_services"].append("Cohere")
if "mistral" in content_lower:
    features["ai_services"].append("Mistral AI")
if "replicate" in content_lower:
    features["ai_services"].append("Replicate")
```

---

### 4. Yeni Proje Kategorisi Eklemek

[scanner.py](../scanner.py) dosyasındaki `classify_category()` metoduna yeni koşul ekleyin:

```python
def classify_category(self, project_type, features, readme):
    # ... mevcut koşullar ...
    
    # Yeni kategori — Mobil uygulama
    if "flutter" in frameworks or "react-native" in " ".join(frameworks):
        return "Mobil Uygulama"
    
    # Yeni kategori — Oyun
    if "unity" in readme_lower or "godot" in readme_lower:
        return "Oyun"
    
    return "Genel"
```

Ayrıca [reporters/markdown_reporter.py](../reporters/markdown_reporter.py) dosyasındaki `CATEGORY_EMOJI` sözlüğüne emoji ekleyin:

```python
CATEGORY_EMOJI = {
    # ... mevcut emojiler ...
    "Mobil Uygulama": "📱",
    "Oyun": "🎮",
}
```

---

### 5. Yeni Rapor Formatı Oluşturmak

`reporters/` altına yeni bir reporter sınıfı ekleyebilirsiniz.

**Örnek: HTML Reporter**

```python
# reporters/html_reporter.py

"""Emare Katip - HTML Rapor Üretici"""

from pathlib import Path
from datetime import datetime
from analyzers.project_analyzer import ProjectAnalyzer


class HtmlReporter:
    """HTML formatında proje raporu üretir."""

    def __init__(self, analyzer: ProjectAnalyzer, output_dir: Path):
        self.analyzer = analyzer
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(self) -> str:
        report = self.analyzer.generate_report()
        
        html = f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Emare Katip Raporu</title>
</head>
<body>
    <h1>📋 KINGSTON Veri Raporu</h1>
    <p>Toplam Proje: {report.total_projects}</p>
    <p>Toplam Dosya: {report.total_files}</p>
    <!-- ... daha fazla içerik ... -->
</body>
</html>"""
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_file = self.output_dir / f"rapor_{timestamp}.html"
        output_file.write_text(html, encoding="utf-8")
        
        print(f"🌐 HTML rapor yazıldı: {output_file}")
        return str(output_file)
```

**`main.py`'ye entegrasyon:**

```python
from reporters.html_reporter import HtmlReporter

def do_report(projects):
    analyzer = ProjectAnalyzer(projects)
    
    # ... mevcut raporlar ...
    
    # HTML rapor
    html_reporter = HtmlReporter(analyzer, REPORTS_DIR)
    html_file = html_reporter.generate()
```

---

### 6. Collector (Veri Toplayıcı) Modülü Oluşturmak

`collectors/` dizini genişletme için hazırlanmış ancak şu an boştur. Örnek bir collector:

```python
# collectors/git_collector.py

"""Git commit geçmişini toplayan collector."""

import subprocess
from pathlib import Path
from typing import Dict, Optional


class GitCollector:
    """Git deposu bilgilerini toplar."""

    def collect(self, project_path: Path) -> Optional[Dict]:
        git_dir = project_path / ".git"
        if not git_dir.exists():
            return None

        info = {
            "total_commits": self._count_commits(project_path),
            "last_commit_date": self._last_commit_date(project_path),
            "branch_count": self._count_branches(project_path),
            "remote_url": self._get_remote(project_path),
        }
        return info

    def _count_commits(self, path: Path) -> int:
        try:
            result = subprocess.run(
                ["git", "-C", str(path), "rev-list", "--count", "HEAD"],
                capture_output=True, text=True, timeout=5
            )
            return int(result.stdout.strip()) if result.returncode == 0 else 0
        except Exception:
            return 0

    def _last_commit_date(self, path: Path) -> str:
        try:
            result = subprocess.run(
                ["git", "-C", str(path), "log", "-1", "--format=%ci"],
                capture_output=True, text=True, timeout=5
            )
            return result.stdout.strip() if result.returncode == 0 else ""
        except Exception:
            return ""

    def _count_branches(self, path: Path) -> int:
        try:
            result = subprocess.run(
                ["git", "-C", str(path), "branch", "--list"],
                capture_output=True, text=True, timeout=5
            )
            return len(result.stdout.strip().split("\n")) if result.returncode == 0 else 0
        except Exception:
            return 0

    def _get_remote(self, path: Path) -> str:
        try:
            result = subprocess.run(
                ["git", "-C", str(path), "remote", "get-url", "origin"],
                capture_output=True, text=True, timeout=5
            )
            return result.stdout.strip() if result.returncode == 0 else ""
        except Exception:
            return ""
```

---

### 7. Hariç Tutma Kuralı Eklemek

[config.py](../config.py) dosyasındaki `EXCLUDED_DIRS` kümesine ekleme yapın:

```python
EXCLUDED_DIRS = {
    # ... mevcut kurallar ...
    "yeni_klasor_adi",
    "BaskaBirApp.app",
}
```

---

## 🧪 Test Stratejisi

Proje şu an resmi test dosyaları içermiyor. Aşağıda test yapısı önerisi:

```
tests/
├── __init__.py
├── test_scanner.py           # Scanner sınıfı testleri
├── test_project_analyzer.py  # Analyzer testleri
├── test_models.py            # Veri modeli testleri
├── test_reporters.py         # Reporter testleri
└── fixtures/                 # Test verileri
    ├── mock_project/
    │   ├── main.py
    │   ├── requirements.txt
    │   └── README.md
    └── mock_scan_data.json
```

**Örnek test:**

```python
# tests/test_scanner.py

import unittest
from pathlib import Path
from scanner import Scanner


class TestScanner(unittest.TestCase):

    def test_detect_python_project(self):
        scanner = Scanner()
        # requirements.txt olan klasör Python olarak tanınmalı
        # (mock dizin oluşturarak test edilebilir)
        result = scanner.detect_project_type(Path("tests/fixtures/mock_project"))
        self.assertEqual(result, "python")

    def test_categorize_file_code(self):
        scanner = Scanner()
        self.assertEqual(scanner.categorize_file(".py"), "code")
        self.assertEqual(scanner.categorize_file(".js"), "code")

    def test_categorize_file_doc(self):
        scanner = Scanner()
        self.assertEqual(scanner.categorize_file(".md"), "doc")

    def test_categorize_file_unknown(self):
        scanner = Scanner()
        self.assertEqual(scanner.categorize_file(".xyz"), "other")

    def test_is_excluded(self):
        scanner = Scanner()
        self.assertTrue(scanner.is_excluded("node_modules"))
        self.assertTrue(scanner.is_excluded(".git"))
        self.assertTrue(scanner.is_excluded(".DS_Store"))
        self.assertFalse(scanner.is_excluded("my_project"))


if __name__ == "__main__":
    unittest.main()
```

**Test çalıştırma:**

```bash
cd "/Volumes/KINGSTON/Emare Katip"
python -m pytest tests/ -v
# veya
python -m unittest discover tests/
```

---

## 📐 Kod Standartları

### Genel Kurallar

| Kural | Açıklama |
|-------|----------|
| **Encoding** | Tüm dosyalar UTF-8 |
| **Docstring** | Her modül ve sınıf docstring içermeli |
| **Type Hints** | Metot parametreleri ve dönüş tipleri belirtilmeli |
| **Adlandırma** | snake_case (fonksiyon/değişken), PascalCase (sınıf) |
| **Satır uzunluğu** | Maks. 100 karakter |
| **İçe aktarımlar** | stdlib → proje modülleri sırasıyla |

### Dosya Şablonu

```python
"""
Emare Katip - [Modül Adı]
===========================
[Modülün kısa açıklaması]
"""

from typing import List, Dict, Optional
from pathlib import Path

# Proje içi importlar
from models.project import ProjectInfo


class YeniModul:
    """[Sınıf açıklaması]"""

    def __init__(self, param: str):
        self.param = param

    def metot_adi(self, veri: List[str]) -> Dict[str, int]:
        """[Metot açıklaması]"""
        pass
```

---

## 🔧 Yapılabilecek İyileştirmeler

### Kısa Vadeli
- [ ] `unittest` veya `pytest` ile birim testler eklenmesi
- [ ] `logging` modülü ile düzgün loglama (şu an sadece `print`)
- [ ] `collectors/` modülüne Git collector eklenmesi
- [ ] CSV rapor formatı desteği

### Orta Vadeli
- [ ] Asenkron tarama (`asyncio` + `aiofiles`) ile performans artışı
- [ ] Konfigürasyon dosyasını dışarıdan okuma (YAML/TOML)
- [ ] Eski taramamla karşılaştırma (diff) özelliği
- [ ] Proje arama ve filtreleme (dil, kategori, boyut)

### Uzun Vadeli
- [ ] Web dashboard (Flask/Streamlit ile)
- [ ] Proje büyüme zaman serileri ve grafikler
- [ ] Git commit geçmişi analizi
- [ ] Otomatik zamanlayıcı (cron job) ile periyodik tarama
- [ ] Birden fazla disk desteği
- [ ] Plugin sistemi ile 3. parti genişletmeler

---

## 📊 Veri Modeli ER Diyagramı

```
┌─────────────────────────────┐
│       KingstonReport        │
├─────────────────────────────┤
│ scan_date: str              │
│ total_projects: int         │
│ total_files: int            │
│ total_size_mb: float        │
│ total_lines: int            │
│ language_distribution: dict │
│ category_distribution: dict │
│ ai_services_used: list      │
├─────────────────────────────┤
│ projects: List[ProjectInfo] │◆────┐
└─────────────────────────────┘     │
                                    │ 1..*
┌─────────────────────────────┐     │
│        ProjectInfo          │◄────┘
├─────────────────────────────┤
│ name: str                   │
│ path: str                   │
│ project_type: str           │
│ primary_language: str       │
│ category: str               │
│ maturity: str               │
│ frameworks: list            │
│ ai_services: list           │
│ has_git/tests/docs/ci: bool │
├─────────────────────────────┤
│ stats: ProjectStats         │◆────┐
│ files: List[FileInfo]       │◆──┐ │
└─────────────────────────────┘   │ │
                                  │ │
┌─────────────────────┐           │ │  ┌─────────────────────┐
│      FileInfo       │◄──────────┘ └─▶│   ProjectStats      │
├─────────────────────┤                 ├─────────────────────┤
│ path: str           │                 │ total_files: int    │
│ name: str           │                 │ total_lines: int    │
│ extension: str      │                 │ code_files: int     │
│ size_bytes: int     │                 │ languages: dict     │
│ language: str       │                 │ largest_file: str   │
│ line_count: int     │                 │ ...                 │
│ category: str       │                 └─────────────────────┘
│ last_modified: str  │
└─────────────────────┘
```

---

## 🤝 Katkıda Bulunma

1. Projeyi fork edin veya yeni bir branch oluşturun
2. Değişikliklerinizi yapın
3. Test yazın (varsa)
4. Docstring ve type hint ekleyin
5. Pull request gönderin

---

> Emare Katip v1.0 — Geliştirici Rehberi
