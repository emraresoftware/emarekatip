# 🧠 Emare Katip — Proje Hafıza Dosyası

> 🔗 **Ortak Hafıza:** [`EMARE_ORTAK_HAFIZA.md`](/Users/emre/Desktop/Emare/EMARE_ORTAK_HAFIZA.md) — Tüm Emare ekosistemi, sunucu bilgileri, standartlar ve proje envanteri için bak.

> **Son Güncelleme:** 4 Mart 2026  
> **Durum:** Aktif kullanımda  
> **Proje:** KINGSTON disk veri toplayıcı ve analizcisi

---

## 📋 Proje Nedir?

**Emare Katip**, KINGSTON diskindeki tüm projeleri otomatik olarak tarar, analiz eder ve anlamlı raporlar üretir.

### Temel Özellikler
- Disk taraması (tüm proje klasörlerini bulur)
- Teknoloji tespiti (package.json, requirements.txt, composer.json vb.)
- Satır, dosya, karakter sayımı
- Git commit sayısı ve son commit bilgisi
- Proje durum analizi (aktif/terk edilmiş/yeni)
- Markdown rapor oluşturma
- Dashboard görüntüleme

---

## 🏗️ Mimari

```
Emare Katip/
├── main.py                    # Ana program (CLI arayüzü)
├── scanner.py                 # Disk tarayıcı
├── dashboard.py               # Flask dashboard
├── collectors/                # Veri toplayıcılar
│   ├── git_collector.py
│   ├── file_collector.py
│   └── tech_collector.py
├── analyzers/                 # Analizciler
│   ├── project_analyzer.py
│   └── trend_analyzer.py
├── reporters/                 # Rapor üreticiler
│   └── markdown_reporter.py
├── models/                    # Veri modelleri
├── data/                      # Tarama verileri (JSON)
├── reports/                   # Üretilen raporlar
└── logs/                      # Log dosyaları
```

---

## 🚀 Kullanım

### Ana Komutlar

```bash
# Tam tarama + rapor + özet
python main.py

# Sadece disk taraması
python main.py --scan

# Sadece rapor üret (son verilerle)
python main.py --report

# Kısa özet
python main.py --summary

# Belirli projenin detayı
python main.py --project ghosty
```

### Dashboard

```bash
python dashboard.py
# http://127.0.0.1:5000
```

---

## 🛠️ Teknoloji

- **Python 3.11+**
- **Flask** (dashboard)
- **pytest** (testler)
- JSON veri depolama
- Git analizi (GitPython potansiyel)

---

## 📂 Veri Yapısı

Tarama sonuçları `data/` klasöründe JSON olarak saklanır:

```json
{
  "project_name": "ghosty",
  "path": "/Volumes/KINGSTON/ghosty",
  "technologies": ["Python", "Flask"],
  "total_lines": 15432,
  "total_files": 187,
  "git_commits": 52,
  "last_commit": "2026-02-15",
  "status": "active"
}
```

---

## 📊 Raporlar

`reports/` klasöründe Markdown formatında üretilir:
- `full_report.md` — Tam detaylı rapor
- `summary_report.md` — Özet rapor
- `tech_stack_report.md` — Teknoloji analizi

---

## 🔄 Durum

**Tamamlandı:**
- ✅ Disk tarayıcı
- ✅ Teknoloji tespiti
- ✅ Temel analizler
- ✅ Markdown rapor
- ✅ CLI arayüzü

**Devam Eden:**
- 🔄 Dashboard (Flask)
- 🔄 Trend analizi

**Planlanan:**
- 📅 Grafik görselleri (Chart.js)
- 📅 CSV export
- 📅 Otomatik tarama zamanlaması

---

## 📝 Notlar

- KINGSTON diski takılı olmadan çalışmaz
- İlk tarama uzun sürebilir (büyük proje sayısına göre)
- Git analizi için `.git` klasörü gerekli

---

*Son güncelleyen: Copilot (4 Mart 2026)*
