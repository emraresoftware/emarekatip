# Emare Katip v1.0

## 📋 KINGSTON Disk Veri Toplayıcı & Analizcisi

**Emare Katip**, KINGSTON diskindeki tüm projeleri otomatik olarak tarar, analiz eder ve anlamlı raporlar üretir.

---

## 🚀 Hızlı Başlangıç

```bash
cd "/Volumes/KINGSTON/Emare Katip"
python main.py
```

## 📖 Kullanım

| Komut | Açıklama |
|-------|----------|
| `python main.py` | Tam tarama + rapor + özet |
| `python main.py --scan` | Sadece disk taraması yap |
| `python main.py --report` | Son verilere göre rapor üret |
| `python main.py --summary` | Kısa özet göster |
| `python main.py --project ghosty` | Belirli projenin detayı |

## 🏗️ Mimari

```
Emare Katip/
├── main.py                    # Ana program (CLI arayüzü)
├── config.py                  # Konfigürasyon ve ayarlar
├── scanner.py                 # Disk tarayıcı ve proje keşfi
├── models/
│   └── project.py             # Veri modelleri (ProjectInfo, FileInfo)
├── collectors/                # Veri toplayıcılar (genişletilebilir)
├── analyzers/
│   └── project_analyzer.py    # Proje analizi ve bağlantı tespiti
├── reporters/
│   ├── markdown_reporter.py   # Markdown rapor üretici
│   └── json_reporter.py       # JSON rapor üretici
├── data/                      # Tarama verileri (JSON)
├── reports/                   # Üretilen raporlar (MD + JSON)
└── logs/                      # Log dosyaları
```

## 🔍 Ne Yapar?

1. **Tarama** — KINGSTON diskindeki tüm klasörleri tarar
2. **Tanıma** — Her klasörün proje türünü tespit eder (Python, Node.js, PHP, Rust vb.)
3. **Analiz** — Kod istatistikleri, dil dağılımı, framework ve AI servisleri
4. **Bağlantı** — Projeler arası ortak bağımlılıkları ve ilişkileri bulur
5. **Raporlama** — Markdown ve JSON formatında detaylı raporlar üretir

## 📊 Analiz Edilen Özellikler

- Dosya sayısı ve boyut
- Kod satırı analizi
- Programlama dili dağılımı
- Framework tespiti (Laravel, Flask, Express, Streamlit vb.)
- AI servisleri tespiti (OpenAI, Gemini, Claude vb.)
- Git, test, CI/CD varlığı
- Proje olgunluk seviyesi
- README özeti
- Projeler arası bağlantılar

## 📁 Çıktılar

- `reports/son_rapor.md` — Son Markdown rapor
- `reports/son_rapor.json` — Son JSON rapor
- `data/son_tarama.json` — Son tarama verileri

---

> Emare Katip v1.0 — Tüm verilerinizi anlamlı bir şekilde kataloglayan akıllı asistan.
