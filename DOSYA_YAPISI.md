# 📁 Emare Katip — Dosya Yapısı

> **Oluşturulma:** Otomatik  
> **Amaç:** Yapay zekalar kod yazmadan önce mevcut dosya yapısını incelemeli

---

## Proje Dosya Ağacı

```
/Users/emre/Desktop/Emare/emarekatip
├── DOSYA_YAPISI.md
├── EMARE_AI_COLLECTIVE.md
├── EMARE_ANAYASA.md
├── EMARE_ORTAK_CALISMA -> /Users/emre/Desktop/Emare/EMARE_ORTAK_CALISMA
├── EMARE_ORTAK_HAFIZA.md
├── Makefile
├── README.md
├── analyzers
│   ├── __init__.py
│   ├── diff_analyzer.py
│   └── project_analyzer.py
├── collectors
│   ├── __init__.py
│   └── git_collector.py
├── config.py
├── config.yaml
├── dashboard.py
├── data
│   ├── .gitkeep
│   ├── duplikeler.json
│   ├── harita.md
│   ├── iskelet.json
│   ├── scan_2026-03-01_07-42-34.json
│   ├── scan_2026-03-01_07-55-09.json
│   ├── scan_2026-03-01_08-19-40.json
│   ├── scan_2026-03-01_08-21-31.json
│   ├── scan_2026-03-01_08-22-54.json
│   ├── scan_2026-03-01_08-23-56.json
│   ├── scan_2026-03-01_08-25-06.json
│   ├── scan_2026-03-01_08-28-19.json
│   ├── scan_2026-03-01_08-30-51.json
│   ├── scan_2026-03-01_08-31-41.json
│   ├── scan_2026-03-01_08-32-15.json
│   ├── scan_2026-03-01_08-32-39.json
│   ├── scan_2026-03-01_08-33-11.json
│   ├── scan_2026-03-01_08-33-35.json
│   ├── scan_2026-03-01_08-34-04.json
│   ├── scan_2026-03-01_08-34-34.json
│   ├── scan_2026-03-01_08-34-38.json
│   ├── scan_2026-03-01_08-35-23.json
│   ├── scan_2026-03-01_08-36-04.json
│   ├── scan_2026-03-01_08-41-58.json
│   ├── scan_2026-03-01_08-43-53.json
│   └── son_tarama.json
├── docs
│   ├── 01_GENEL_BAKIS.md
│   ├── 02_MIMARI.md
│   ├── 03_API_REFERANS.md
│   ├── 04_KULLANIM_KILAVUZU.md
│   └── 05_GELISTIRICI_REHBERI.md
├── emarekatip_hafiza.md
├── exceptions.py
├── logs
│   ├── .gitkeep
│   └── emare_katip.log
├── main.py
├── models
│   ├── __init__.py
│   └── project.py
├── pyproject.toml
├── pytest.ini
├── reporters
│   ├── __init__.py
│   ├── csv_reporter.py
│   ├── html_reporter.py
│   ├── json_reporter.py
│   └── markdown_reporter.py
├── reports
│   └── .gitkeep
├── scanner.py
└── tests
    ├── __init__.py
    ├── test_analyzer.py
    ├── test_diff.py
    ├── test_exceptions.py
    ├── test_models.py
    ├── test_reporters.py
    └── test_scanner.py

11 directories, 68 files

```

---

## 📌 Kullanım Talimatları (AI İçin)

Bu dosya, kod üretmeden önce projenin mevcut yapısını kontrol etmek içindir:

1. **Yeni dosya oluşturmadan önce:** Bu ağaçta benzer bir dosya var mı kontrol et
2. **Yeni klasör oluşturmadan önce:** Mevcut klasör yapısına uygun mu kontrol et
3. **Import/require yapmadan önce:** Dosya yolu doğru mu kontrol et
4. **Kod kopyalamadan önce:** Aynı fonksiyon başka dosyada var mı kontrol et

**Örnek:**
- ❌ "Yeni bir auth.py oluşturalım" → ✅ Kontrol et, zaten `app/auth.py` var mı?
- ❌ "config/ klasörü oluşturalım" → ✅ Kontrol et, zaten `config/` var mı?
- ❌ `from utils import helper` → ✅ Kontrol et, `utils/helper.py` gerçekten var mı?

---

**Not:** Bu dosya otomatik oluşturulmuştur. Proje yapısı değiştikçe güncellenmelidir.

```bash
# Güncelleme komutu
python3 /Users/emre/Desktop/Emare/create_dosya_yapisi.py
```
