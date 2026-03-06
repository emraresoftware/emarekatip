# 📋 Emare Katip v1.0 — Genel Bakış

> **KINGSTON Disk Veri Toplayıcı & Analizcisi**

---

## 🎯 Proje Amacı

**Emare Katip**, KINGSTON harici diskinde bulunan tüm yazılım projelerini **otomatik olarak tarayan**, **analiz eden** ve **raporlayan** bir Python uygulamasıdır. Disk üzerindeki onlarca projeyi tek bir komutla kataloglar, istatistiklerini çıkarır ve aralarındaki bağlantıları tespit eder.

## 🧩 Ne Problem Çözer?

Bir geliştirici olarak harici diskte birçok farklı proje barındırmak, zamanla şu sorunları doğurur:

| Problem | Emare Katip'in Çözümü |
|---------|----------------------|
| Hangi projelerin nerede olduğu unutulur | Tüm projeleri otomatik keşfeder ve listeler |
| Projelerin durumu bilinmez | Olgunluk seviyesini otomatik tahmin eder |
| Hangi dillerin/framework'lerin kullanıldığı karışır | Dil ve framework dağılımını raporlar |
| Projeler arası bağlantılar görülmez | Ortak bağımlılıkları ve AI servislerini tespit eder |
| Kod büyüklüğü ve istatistikler takip edilmez | Satır sayısı, dosya sayısı, boyut analizi yapar |

## ✨ Temel Özellikler

### 🔍 Akıllı Tarama
- KINGSTON diskinin kök dizinindeki tüm klasörleri tarar
- Proje türünü otomatik tanır (Python, Node.js, PHP/Laravel, Rust, Genel)
- macOS sistem dosyalarını, `node_modules`, `.git` gibi gereksiz dizinleri hariç tutar
- Kendisini taramaz (döngüsel tarama koruması)

### 📊 Derinlemesine Analiz
- **Dosya istatistikleri**: Dosya/dizin sayısı, toplam boyut
- **Kod analizi**: Toplam satır sayısı, en büyük dosya
- **Dil dağılımı**: 16+ programlama dili desteği
- **Framework tespiti**: Laravel, Django, Flask, FastAPI, Express.js, React, Vite, Next.js, Streamlit, Selenium
- **AI servisleri tespiti**: OpenAI, Google Gemini, Anthropic Claude, Ollama, Tavily, Hugging Face
- **Proje özellikleri**: Git varlığı, test dosyaları, CI/CD yapılandırması, dokümantasyon

### 🏷️ Otomatik Sınıflandırma
- **Kategori**: AI / Yapay Zeka, AI Asistan, AI Bot, Web Uygulama, Web Servis, Sistem, Bot, Yönetim Paneli, Genel
- **Olgunluk**: Boş → Erken Aşama → Prototip → Geliştiriliyor → Aktif Geliştirme → Üretim Hazır

### 🔗 Bağlantı Tespiti
- Aynı AI servisini kullanan projeler
- Aynı framework'ü paylaşan projeler
- İsim benzerliğine göre proje aileleri (örn: "Emare" ailesi)

### 📝 Çoklu Rapor Formatı
- **Markdown rapor**: Emoji destekli, tablo ve gruplamalarla zenginleştirilmiş
- **JSON rapor**: Makine tarafından okunabilir, programatik erişim için
- **Konsol özet**: Terminal üzerinde hızlı görüntüleme

## 🛠️ Teknoloji Yığını

| Bileşen | Teknoloji |
|---------|-----------|
| **Dil** | Python 3.x |
| **Veri Modeli** | Python `dataclasses` |
| **CLI** | `argparse` |
| **Dosya İşlemleri** | `pathlib`, `os` |
| **Veri Formatı** | JSON (veri depolama & raporlama) |
| **Harici Bağımlılık** | Yok (saf Python standart kütüphanesi) |

## 📈 Proje Metrikleri

- **Toplam kaynak dosya**: 8 Python modülü + 4 `__init__.py`
- **Toplam satır sayısı**: ~1.200+ satır Python kodu
- **Harici bağımlılık**: 0 (sadece Python standart kütüphanesi)
- **Desteklenen dil sayısı**: 16 programlama dili
- **Desteklenen framework sayısı**: 10+
- **Desteklenen AI servisi sayısı**: 6

## 📁 Çıktı Dosyaları

| Dosya | Açıklama |
|-------|----------|
| `reports/son_rapor.md` | En son üretilen Markdown rapor |
| `reports/son_rapor.json` | En son üretilen JSON rapor |
| `reports/rapor_YYYY-MM-DD_HH-MM-SS.md` | Zaman damgalı Markdown rapor |
| `reports/rapor_YYYY-MM-DD_HH-MM-SS.json` | Zaman damgalı JSON rapor |
| `data/son_tarama.json` | En son tarama ham verileri |
| `data/scan_YYYY-MM-DD_HH-MM-SS.json` | Zaman damgalı tarama verileri |
| `logs/emare_katip.log` | Uygulama log dosyası |

## 🗺️ Gelecek Vizyonu

- Web tabanlı dashboard arayüzü
- Zamanla proje büyüme grafiği
- Git commit geçmişi analizi
- Otomatik zamanlayıcı ile periyodik tarama
- Collector modülleri ile genişletilebilir veri toplama

---

> **Emare Katip v1.0** — Tüm verilerinizi anlamlı bir şekilde kataloglayan akıllı asistan.
