# 🏗️ Emare Katip — Mimari Dokümantasyon

> Projenin modüler yapısı, bileşen ilişkileri ve veri akışı.

---

## 📂 Dizin Yapısı

```
Emare Katip/
├── main.py                        # Ana giriş noktası (CLI arayüzü)
├── config.py                      # Konfigürasyon ve sabitler
├── scanner.py                     # Disk tarayıcı ve proje keşfi
│
├── models/                        # Veri modelleri
│   ├── __init__.py
│   └── project.py                 # FileInfo, ProjectStats, ProjectInfo, KingstonReport
│
├── analyzers/                     # Analiz motoru
│   ├── __init__.py
│   └── project_analyzer.py        # Çapraz proje analizi ve bağlantı tespiti
│
├── collectors/                    # Veri toplayıcılar (genişletme noktası)
│   └── __init__.py
│
├── reporters/                     # Rapor üreticiler
│   ├── __init__.py
│   ├── markdown_reporter.py       # Markdown formatında rapor
│   └── json_reporter.py           # JSON formatında rapor
│
├── data/                          # Tarama verileri (çalışma zamanında oluşur)
├── reports/                       # Üretilen raporlar (çalışma zamanında oluşur)
├── logs/                          # Log dosyaları (çalışma zamanında oluşur)
└── docs/                          # Dokümantasyon
```

## 🧱 Katmanlı Mimari

Emare Katip, **4 katmanlı** temiz bir mimari üzerine inşa edilmiştir:

```
┌─────────────────────────────────────────────────┐
│              CLI Katmanı (main.py)               │
│   argparse, kullanıcı etkileşimi, orkestrasyon   │
├─────────────────────────────────────────────────┤
│          Raporlama Katmanı (reporters/)          │
│      MarkdownReporter, JsonReporter              │
├─────────────────────────────────────────────────┤
│          Analiz Katmanı (analyzers/)             │
│   ProjectAnalyzer: dağılım, bağlantı, rapor     │
├─────────────────────────────────────────────────┤
│          Tarama Katmanı (scanner.py)             │
│   Scanner: keşif, dosya tarama, sınıflandırma    │
├─────────────────────────────────────────────────┤
│          Veri Modeli (models/)                    │
│   FileInfo, ProjectStats, ProjectInfo            │
├─────────────────────────────────────────────────┤
│        Konfigürasyon (config.py)                 │
│   Yollar, sabitler, uzantı haritaları            │
└─────────────────────────────────────────────────┘
```

## 🔄 Veri Akış Diyagramı

```
KINGSTON Diski
     │
     ▼
┌──────────┐     ┌────────────┐     ┌──────────────┐
│ config   │────▶│  Scanner   │────▶│ ProjectInfo  │
│ ayarlar  │     │  tarama    │     │ modelleri    │
└──────────┘     └────────────┘     └──────┬───────┘
                                           │
                      ┌────────────────────┤
                      │                    │
                      ▼                    ▼
               ┌──────────────┐    ┌───────────────┐
               │  JSON Data   │    │ ProjectAnalyzer│
               │  (data/)     │    │  analiz        │
               └──────────────┘    └───────┬───────┘
                                           │
                           ┌───────────────┼───────────────┐
                           │               │               │
                           ▼               ▼               ▼
                    ┌────────────┐  ┌────────────┐  ┌────────────┐
                    │ Markdown   │  │   JSON     │  │  Konsol    │
                    │ Reporter   │  │ Reporter   │  │  Özet      │
                    └────────────┘  └────────────┘  └────────────┘
                           │               │
                           ▼               ▼
                    ┌────────────┐  ┌────────────┐
                    │ .md rapor  │  │ .json rapor│
                    │ (reports/) │  │ (reports/) │
                    └────────────┘  └────────────┘
```

## 🧩 Modül Detayları

### 1. `config.py` — Konfigürasyon Merkezi

Uygulamanın tüm ayarlarını merkezi olarak yönetir.

| Sabit/Değişken | Tür | Açıklama |
|---------------|-----|----------|
| `BASE_DIR` | `Path` | Emare Katip kök dizini |
| `KINGSTON_ROOT` | `Path` | KINGSTON disk kökü (`/Volumes/KINGSTON`) |
| `SCAN_ROOT` | `Path` | Taranan kök dizin (= `KINGSTON_ROOT`) |
| `DATA_DIR` | `Path` | Tarama verilerinin saklandığı dizin |
| `REPORTS_DIR` | `Path` | Raporların yazıldığı dizin |
| `LOG_DIR` | `Path` | Log dosyalarının dizini |
| `EXCLUDED_DIRS` | `set` | Hariç tutulan dizin/dosya isimleri |
| `CODE_EXTENSIONS` | `dict` | Kod dosyası uzantı → dil haritası (16 dil) |
| `DOC_EXTENSIONS` | `dict` | Döküman uzantı → tür haritası |
| `CONFIG_FILES` | `dict` | Konfigürasyon dosyası uzantı haritası |
| `DATA_EXTENSIONS` | `dict` | Veri dosyası uzantı haritası |
| `PROJECT_MARKERS` | `dict` | Proje türü belirleme kuralları |

**Yardımcı Fonksiyonlar:**
- `ensure_dirs()` — Gerekli çalışma dizinlerini oluşturur
- `get_timestamp()` — Formatlanmış zaman damgası döndürür

---

### 2. `scanner.py` — Disk Tarayıcı

Asıl iş mantığının büyük kısmını içerir. `Scanner` sınıfı ile KINGSTON diskini tarar.

**Tarama Süreci (adım adım):**

```
scan_projects()
  │
  ├─ 1. Kök dizindeki klasörleri listele
  │
  ├─ 2. Her klasör için:
  │     ├─ detect_project_type()     → Proje türünü belirle
  │     ├─ scan_directory()          → Dosyaları recursive tara
  │     ├─ build_stats()             → İstatistikleri hesapla
  │     ├─ extract_readme_summary()  → README özetini çıkar
  │     ├─ detect_features()         → Framework/AI/Git tespiti
  │     ├─ classify_category()       → Kategori sınıflandır
  │     └─ estimate_maturity()       → Olgunluk seviyesi tahmin et
  │
  └─ 3. ProjectInfo listesi döndür
```

**Önemli Tasarım Kararları:**
- 5 MB'den büyük dosyalarda satır sayma atlanır (performans)
- `rglob("*")` ile recursive tarama yapılır
- Hariç tutulan dizinler `rel.parts` kontrolüyle filtrelenir
- Bağımlılık dosyaları (requirements.txt, package.json vb.) okunarak AI servisleri ve framework'ler tespit edilir

---

### 3. `models/project.py` — Veri Modelleri

Tüm veri yapıları `@dataclass` dekoratörü ile tanımlanmıştır.

```
FileInfo          → Tekil dosya bilgisi
     │
ProjectStats      → Bir projenin istatistik özeti
     │
ProjectInfo       → Bir projenin tüm bilgisi (stats + meta + dosyalar)
     │
KingstonReport    → Disk geneli toplam rapor
```

**İlişki diyagramı:**

```
KingstonReport
├── total_projects, total_files, total_lines...
├── language_distribution: Dict[str, int]
├── category_distribution: Dict[str, int]
└── projects: List[ProjectInfo]
       ├── name, path, project_type, primary_language
       ├── category, maturity, frameworks, ai_services
       ├── stats: ProjectStats
       │     ├── total_files, code_files, total_lines
       │     ├── languages: Dict[str, int]
       │     └── largest_file, largest_file_lines
       └── files: List[FileInfo]
             ├── path, name, extension
             ├── size_bytes, line_count
             ├── language, category
             └── last_modified
```

---

### 4. `analyzers/project_analyzer.py` — Analiz Motoru

Taranan projeleri çapraz analiz eder.

**Analiz Yetenekleri:**
- Dil dağılımı hesaplama (`Counter` kullanarak)
- Kategori dağılımı
- AI servisleri ve framework birleştirme
- Projeleri kategoriye/dile göre gruplama
- En büyük projeleri sıralama
- Projeler arası bağlantı tespiti (ortak AI servisi, ortak framework, isim ailesi)
- Genel rapor (`KingstonReport`) oluşturma

---

### 5. `reporters/` — Rapor Üreticiler

#### `markdown_reporter.py`
- Emoji destekli zengin Markdown formatı
- Bölümler: Özet → Dil Dağılımı → Kategoriler → En Büyük Projeler → Bağlantılar → Proje Detayları
- Projeleri kategoriye göre gruplar
- Zaman damgalı + "son rapor" dosyaları üretir

#### `json_reporter.py`
- Makine tarafından okunabilir format
- `KingstonReport.to_dict()` çıktısı + bağlantılar + framework listesi
- Aynı dosya adlandırma kuralları

## 🔒 Hariç Tutulan Dizinler

```python
EXCLUDED_DIRS = {
    # macOS sistem dosyaları
    ".DS_Store", ".DocumentRevisions-V100", ".Spotlight-V100",
    ".TemporaryItems", ".Trashes", ".fseventsd",
    
    # Geliştirme araçları
    "__pycache__", "node_modules", ".git", ".venv", "venv",
    "vendor", ".idea", ".vscode",
    
    # Uygulamalar
    "Visual Studio Code.app", "WinBox.app",
    
    # Kendisi (döngüsel tarama koruması)
    "Emare Katip", "EmareKatip",
}
```

## 🔌 Genişletme Noktaları

| Bileşen | Genişletme Yöntemi |
|---------|--------------------|
| **Yeni dil desteği** | `config.py` → `CODE_EXTENSIONS`'a ekleme |
| **Yeni framework tespiti** | `scanner.py` → `detect_features()` metodunda koşul ekleme |
| **Yeni AI servisi** | `scanner.py` → `detect_features()` metodunda keyword ekleme |
| **Yeni rapor formatı** | `reporters/` altına yeni reporter sınıfı |
| **Veri toplayıcı** | `collectors/` altına yeni collector modülü (şu an boş) |
| **Yeni kategori** | `scanner.py` → `classify_category()` metoduna koşul ekleme |
| **Hariç tutma kuralı** | `config.py` → `EXCLUDED_DIRS`'e ekleme |

---

> Bu dokümantasyon Emare Katip v1.0 kaynak koduna dayanmaktadır.
