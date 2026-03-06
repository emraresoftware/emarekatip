# 📚 Emare Katip — API Referansı

> Tüm sınıflar, metotlar, veri modelleri ve parametrelerin detaylı referansı.

---

## 📦 Modül: `models/project.py`

### `FileInfo` (dataclass)

Tek bir dosyanın bilgilerini tutar.

| Alan | Tür | Varsayılan | Açıklama |
|------|-----|-----------|----------|
| `path` | `str` | — | Dosyanın tam yolu |
| `name` | `str` | — | Dosya adı |
| `extension` | `str` | — | Dosya uzantısı (`.py`, `.js` vb.) |
| `size_bytes` | `int` | — | Dosya boyutu (bayt) |
| `language` | `str` | `"Bilinmeyen"` | Dosyanın programlama dili |
| `line_count` | `int` | `0` | Satır sayısı |
| `category` | `str` | `"other"` | Dosya kategorisi: `code`, `doc`, `config`, `data`, `other` |
| `last_modified` | `Optional[str]` | `None` | Son değiştirilme tarihi (ISO format) |

---

### `ProjectStats` (dataclass)

Bir projenin sayısal istatistiklerini içerir.

| Alan | Tür | Varsayılan | Açıklama |
|------|-----|-----------|----------|
| `total_files` | `int` | `0` | Toplam dosya sayısı |
| `total_dirs` | `int` | `0` | Toplam dizin sayısı |
| `total_size_bytes` | `int` | `0` | Toplam boyut (bayt) |
| `total_lines` | `int` | `0` | Toplam satır sayısı |
| `code_files` | `int` | `0` | Kod dosyası sayısı |
| `doc_files` | `int` | `0` | Döküman dosyası sayısı |
| `config_files` | `int` | `0` | Konfigürasyon dosyası sayısı |
| `data_files` | `int` | `0` | Veri dosyası sayısı |
| `languages` | `dict` | `{}` | Dil dağılımı: `{"Python": 15, "JavaScript": 3}` |
| `largest_file` | `Optional[str]` | `None` | En büyük kod dosyasının adı |
| `largest_file_lines` | `int` | `0` | En büyük kod dosyasının satır sayısı |

---

### `ProjectInfo` (dataclass)

Bir projenin tüm bilgilerini barındıran ana veri modeli.

| Alan | Tür | Varsayılan | Açıklama |
|------|-----|-----------|----------|
| `name` | `str` | — | Proje adı (klasör adı) |
| `path` | `str` | — | Projenin tam yolu |
| `project_type` | `str` | `"Bilinmeyen"` | Proje türü: `python`, `nodejs`, `php_laravel`, `rust`, `general` |
| `primary_language` | `str` | `"Bilinmeyen"` | Birincil programlama dili |
| `description` | `str` | `""` | README'den çıkarılan kısa açıklama |
| `version` | `str` | `""` | Proje versiyonu |
| `maturity` | `str` | `"Bilinmeyen"` | Olgunluk seviyesi |
| `category` | `str` | `"Diğer"` | Proje kategorisi |
| `readme_summary` | `str` | `""` | README özeti (maks. 500 karakter) |
| `stats` | `ProjectStats` | `ProjectStats()` | Proje istatistikleri |
| `files` | `list` | `[]` | `List[FileInfo]` — proje dosyaları |
| `dependencies` | `list` | `[]` | Bağımlılık dosyaları listesi |
| `has_git` | `bool` | `False` | `.git` dizini var mı? |
| `has_tests` | `bool` | `False` | Test dosyaları var mı? |
| `has_docs` | `bool` | `False` | Döküman dosyaları var mı? |
| `has_ci` | `bool` | `False` | CI/CD yapılandırması var mı? |
| `frameworks` | `list` | `[]` | Tespit edilen framework'ler |
| `ai_services` | `list` | `[]` | Tespit edilen AI servisleri |
| `scan_date` | `str` | `datetime.now().isoformat()` | Tarama tarihi |

**Property'ler:**

| Property | Dönüş Tipi | Açıklama |
|----------|-----------|----------|
| `total_size_mb` | `float` | Boyutu MB cinsinden döndürür (2 ondalık) |

**Metotlar:**

| Metot | Dönüş Tipi | Açıklama |
|-------|-----------|----------|
| `to_dict()` | `dict` | Tüm alanları sözlük formatına dönüştürür (JSON serileştirme için) |

---

### `KingstonReport` (dataclass)

KINGSTON disk genelinin toplam raporu.

| Alan | Tür | Varsayılan | Açıklama |
|------|-----|-----------|----------|
| `scan_date` | `str` | `datetime.now().isoformat()` | Tarama tarihi |
| `total_projects` | `int` | `0` | Toplam proje sayısı |
| `total_files` | `int` | `0` | Tüm projelerdeki toplam dosya sayısı |
| `total_size_mb` | `float` | `0.0` | Toplam boyut (MB) |
| `total_lines` | `int` | `0` | Toplam satır sayısı |
| `projects` | `list` | `[]` | `List[ProjectInfo]` |
| `language_distribution` | `dict` | `{}` | Genel dil dağılımı |
| `category_distribution` | `dict` | `{}` | Kategori dağılımı |
| `ai_services_used` | `list` | `[]` | Kullanılan tüm AI servisleri |

**Metotlar:**

| Metot | Dönüş Tipi | Açıklama |
|-------|-----------|----------|
| `to_dict()` | `dict` | Raporu sözlük formatına dönüştürür (iç içe projeler dahil) |

---

## 📦 Modül: `scanner.py`

### `Scanner` Sınıfı

KINGSTON diskindeki projeleri ve dosyaları tarayan ana tarayıcı.

**Kurucu:**

```python
Scanner(root: Path = None)
```

| Parametre | Tür | Varsayılan | Açıklama |
|-----------|-----|-----------|----------|
| `root` | `Path` | `SCAN_ROOT` | Taranan kök dizin |

**Öznitelikler:**

| Öznitelik | Tür | Açıklama |
|-----------|-----|----------|
| `root` | `Path` | Taranan kök dizin yolu |
| `discovered_projects` | `List[ProjectInfo]` | Keşfedilen projeler listesi |

**Metotlar:**

#### `is_excluded(name: str) → bool`
Dizin/dosya adının hariç tutulup tutulmayacağını kontrol eder.
- `.` ile başlayan tüm adlar hariç tutulur
- `EXCLUDED_DIRS` kümesindeki adlar hariç tutulur

#### `detect_project_type(path: Path) → str`
Klasördeki dosyalara bakarak proje türünü tespit eder.

| Dönüş Değeri | Koşul |
|--------------|-------|
| `"python"` | `requirements.txt`, `setup.py`, `pyproject.toml`, `Pipfile`, `setup.cfg`, `main.py`, `app.py` |
| `"nodejs"` | `package.json`, `yarn.lock`, `package-lock.json` |
| `"php_laravel"` | `artisan`, `composer.json` |
| `"rust"` | `Cargo.toml`, `Cargo.lock` |
| `"general"` | Yukarıdakilerin hiçbiri eşleşmezse |

#### `categorize_file(ext: str) → str`
Dosya uzantısına göre kategori döndürür: `"code"`, `"doc"`, `"config"`, `"data"`, `"other"`.

#### `get_language(ext: str) → str`
Dosya uzantısına göre programlama dili adı döndürür. Bilinmeyen uzantılar için `"Diğer"`.

#### `count_lines(file_path: Path) → int`
Metin dosyasındaki satır sayısını sayar.
- 5 MB'den büyük dosyalar atlanır (performans)
- UTF-8 encoding, hatalar görmezden gelinir
- Hata durumunda `0` döner

#### `scan_directory(dir_path: Path) → Tuple[List[FileInfo], int]`
Bir dizini recursive olarak tarar.
- **Dönüş**: `(dosya_listesi, alt_dizin_sayısı)`
- Hariç tutulan parçalar filtrelenir
- Her dosya için `FileInfo` nesnesi oluşturulur

#### `build_stats(files: List[FileInfo], dir_count: int) → ProjectStats`
Dosya listesinden istatistik nesnesi oluşturur.
- Dil dağılımını hesaplar
- En büyük kod dosyasını bulur

#### `extract_readme_summary(dir_path: Path) → str`
README dosyasından ilk 10 satırı çeker ve 500 karaktere kırpar.
- Aranan dosyalar: `README.md`, `readme.md`, `README.txt`, `README`

#### `detect_features(dir_path: Path, files: List[FileInfo]) → dict`
Projenin özelliklerini tespit eder.

**Dönüş sözlüğü:**
```python
{
    "has_git": bool,
    "has_tests": bool,
    "has_docs": bool,
    "has_ci": bool,
    "frameworks": List[str],
    "ai_services": List[str],
    "dependencies": List[str],
}
```

**Tespit edilen framework'ler:** Laravel, Django, Rust/Cargo, Vite, Next.js, Express.js, React, WhatsApp Web.js, Flask, FastAPI, Streamlit, Selenium

**Tespit edilen AI servisleri:** OpenAI, Google Gemini, Anthropic Claude, Ollama, Tavily, Hugging Face

#### `classify_category(project_type: str, features: dict, readme: str) → str`
Projenin kategorisini belirler. Öncelik sırası:
1. AI servisi + "bot"/"whatsapp" → `"AI Bot"`
2. AI servisi + "asistan"/"assistant" → `"AI Asistan"`
3. AI servisi → `"AI / Yapay Zeka"`
4. Laravel / PHP → `"Web Uygulama"`
5. Rust → `"Sistem"`
6. Bot/WhatsApp → `"Bot"`
7. Express → `"Web Servis"`
8. Panel/Dashboard → `"Yönetim Paneli"`
9. Hiçbiri → `"Genel"`

#### `estimate_maturity(stats: ProjectStats, features: dict) → str`
Proje olgunluk seviyesini tahmin eder.

| Seviye | Koşul |
|--------|-------|
| `"Boş"` | `total_files == 0` |
| `"Erken Aşama"` | `code_files ≤ 2` ve `total_lines < 100` |
| `"Üretim Hazır"` | Test + CI/CD var |
| `"Aktif Geliştirme"` | `code_files > 10` veya `total_lines > 2000` |
| `"Geliştiriliyor"` | `code_files > 5` |
| `"Prototip"` | Diğer durumlar |

#### `scan_projects() → List[ProjectInfo]`
**Ana metot.** Kök dizindeki tüm projeleri tarar ve `ProjectInfo` listesi döndürür. Konsola ilerleme bilgisi yazar.

---

## 📦 Modül: `analyzers/project_analyzer.py`

### `ProjectAnalyzer` Sınıfı

**Kurucu:**
```python
ProjectAnalyzer(projects: List[ProjectInfo])
```

**Metotlar:**

| Metot | Dönüş Tipi | Açıklama |
|-------|-----------|----------|
| `get_language_distribution()` | `Dict[str, int]` | Tüm projelerdeki dil dağılımı (sıralı) |
| `get_category_distribution()` | `Dict[str, int]` | Kategori dağılımı |
| `get_all_ai_services()` | `List[str]` | Tüm AI servisleri (sıralı, unique) |
| `get_all_frameworks()` | `List[str]` | Tüm framework'ler (sıralı, unique) |
| `get_projects_by_category()` | `Dict[str, List[ProjectInfo]]` | Kategoriye göre gruplar |
| `get_projects_by_language()` | `Dict[str, List[ProjectInfo]]` | Dile göre gruplar |
| `get_largest_projects(top_n)` | `List[ProjectInfo]` | En büyük `top_n` proje (satır sayısına göre) |
| `find_connections()` | `List[Dict]` | Projeler arası bağlantılar |
| `generate_report()` | `KingstonReport` | Genel disk raporu oluşturur |

**Bağlantı Türleri (`find_connections` dönüşü):**

```python
{
    "type": "shared_ai_service" | "shared_framework" | "project_family",
    "service" | "framework" | "family": str,
    "projects": List[str],
    "description": str,
}
```

---

## 📦 Modül: `reporters/markdown_reporter.py`

### `MarkdownReporter` Sınıfı

**Kurucu:**
```python
MarkdownReporter(analyzer: ProjectAnalyzer, output_dir: Path)
```

**Sınıf Sabitleri:**
- `MATURITY_EMOJI` — Olgunluk seviyesi → emoji haritası
- `CATEGORY_EMOJI` — Kategori → emoji haritası

**Metotlar:**

| Metot | Erişim | Açıklama |
|-------|--------|----------|
| `_header()` | private | Rapor başlığı |
| `_summary_section(report)` | private | Genel özet tablosu |
| `_language_section(report)` | private | Dil dağılımı tablosu |
| `_category_section(report)` | private | Kategori listesi |
| `_project_detail(p)` | private | Tek proje detay kartı |
| `_projects_section(projects)` | private | Tüm projeler (kategoriye göre gruplu) |
| `_connections_section(analyzer)` | private | Bağlantılar bölümü |
| `_top_projects_table(analyzer)` | private | En büyük projeler tablosu |
| `generate()` | **public** | Tam rapor üret ve dosyaya yaz |

**`generate()` çıktı dosyaları:**
- `reports/rapor_YYYY-MM-DD_HH-MM-SS.md` (zaman damgalı)
- `reports/son_rapor.md` (en güncel kopyası)

---

## 📦 Modül: `reporters/json_reporter.py`

### `JsonReporter` Sınıfı

**Kurucu:**
```python
JsonReporter(analyzer: ProjectAnalyzer, output_dir: Path)
```

**Metotlar:**

| Metot | Dönüş Tipi | Açıklama |
|-------|-----------|----------|
| `generate()` | `str` | JSON rapor üretir, dosya yolunu döndürür |

**JSON çıktısına eklenen ekstra alanlar:**
- `connections` — Projeler arası bağlantılar
- `all_frameworks` — Tüm framework listesi

---

## 📦 Modül: `main.py` — CLI Fonksiyonları

| Fonksiyon | Açıklama |
|-----------|----------|
| `save_scan_data(projects)` | Tarama verilerini JSON olarak `data/` dizinine kaydeder |
| `load_last_scan()` | Son tarama verilerini `data/son_tarama.json`'dan yükler |
| `do_scan()` | Disk taraması başlatır ve sonuçları kaydeder |
| `do_report(projects)` | Markdown + JSON raporlarını üretir |
| `do_summary(projects)` | Konsola özet tablo yazdırır |
| `do_project_detail(projects, name)` | Belirli bir projenin detayını konsola yazdırır |
| `main()` | CLI argümanlarını parse eder ve ilgili fonksiyonları çağırır |

---

> Bu referans Emare Katip v1.0 kaynak kodundan üretilmiştir.
