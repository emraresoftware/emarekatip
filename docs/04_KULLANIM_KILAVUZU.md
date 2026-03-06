# 📖 Emare Katip — Kullanım Kılavuzu

> Kurulum, çalıştırma, CLI komutları ve pratik kullanım örnekleri.

---

## 🔧 Gereksinimler

| Gereksinim | Minimum Versiyon | Açıklama |
|-----------|-----------------|----------|
| **Python** | 3.7+ | `dataclasses` desteği için |
| **İşletim Sistemi** | macOS | `/Volumes/KINGSTON` bağlama noktası |
| **Harici Kütüphane** | Yok | Saf Python standart kütüphanesi |
| **Disk** | KINGSTON USB | `/Volumes/KINGSTON` olarak bağlı olmalı |

## ⚡ Hızlı Başlangıç

### 1. Terminali Açın

```bash
cd "/Volumes/KINGSTON/Emare Katip"
```

### 2. Tam Tarama + Rapor + Özet

```bash
python main.py
```

Bu komut sırasıyla:
1. ✅ KINGSTON diskini tarar
2. ✅ Tarama verilerini JSON olarak kaydeder
3. ✅ Markdown ve JSON raporlarını üretir
4. ✅ Konsola özet tablo yazdırır

---

## 🖥️ CLI Komutları

### Temel Kullanım

```bash
python main.py [SEÇENEKLER]
```

### Komut Seçenekleri

| Komut | Kısaltma | Açıklama |
|-------|----------|----------|
| `python main.py` | — | Tam çalıştırma (tarama + rapor + özet) |
| `python main.py --scan` | — | Sadece disk taraması yap |
| `python main.py --report` | — | Son tarama verileriyle rapor üret |
| `python main.py --summary` | — | Kısa özet göster |
| `python main.py --project <isim>` | — | Belirli projenin detayını göster |
| `python main.py --all` | — | Tam çalıştırma (varsayılan) |

> **Not:** Hiçbir flag verilmezse `--all` davranışı uygulanır.

---

## 📋 Kullanım Senaryoları

### Senaryo 1: İlk Kullanım — Tam Tarama

```bash
python main.py
```

**Çıktı:**
```
╔══════════════════════════════════════════════════════════════════╗
║           ███████╗███╗   ███╗ █████╗ ██████╗ ███████╗            ║
║           ...                                                    ║
║                  K A T İ P   v 1 . 0                             ║
╚══════════════════════════════════════════════════════════════════╝

🔍 KINGSTON diski taranıyor...

  📁 Taraniyor: ghosty
    ✅ 156 dosya, 89 kod, Python, [AI / Yapay Zeka]
  📁 Taraniyor: Emare Finance
    ✅ 243 dosya, 178 kod, PHP, [Web Uygulama]
  ...

📊 Toplam 25 proje bulundu.
💾 Tarama verileri kaydedildi: data/scan_2026-03-01_14-30-00.json

📝 Raporlar oluşturuluyor...
📝 Markdown rapor yazıldı: reports/rapor_2026-03-01_14-30-00.md
📊 JSON rapor yazıldı: reports/rapor_2026-03-01_14-30-00.json

============================================================
📊  EMARE KATİP — KINGSTON ÖZET RAPORU
============================================================
  📁 Toplam Proje    : 25
  📄 Toplam Dosya    : 3,456
  💾 Toplam Boyut    : 245.7 MB
  📝 Toplam Satır    : 89,123
  ...
============================================================

✨ Emare Katip işlemi tamamlandı.
```

---

### Senaryo 2: Sadece Rapor Güncelleme

Tarama verisi zaten varsa, sadece raporu yeniden üretmek için:

```bash
python main.py --report
```

Bu komut `data/son_tarama.json` dosyasını okuyarak yeni raporlar üretir. Disk taraması yapmaz, bu yüzden çok daha hızlıdır.

---

### Senaryo 3: Hızlı Özet Görüntüleme

```bash
python main.py --summary
```

Konsola tablo formatında kısa özet yazdırır:
- Toplam proje, dosya, boyut, satır sayısı
- Dil dağılımı (bar grafikli)
- Kategori dağılımı
- AI servisleri
- En büyük 5 proje
- Proje bağlantıları

---

### Senaryo 4: Belirli Bir Projenin Detayı

```bash
python main.py --project ghosty
```

**Çıktı:**
```
============================================================
📁 ghosty
============================================================
  📂 Yol          : /Volumes/KINGSTON/ghosty
  🏷️  Kategori     : AI / Yapay Zeka
  🗣️  Birincil Dil  : Python
  📊 Olgunluk     : Aktif Geliştirme
  📄 Dosya Sayısı : 156
  💻 Kod Dosyası  : 89
  📝 Toplam Satır : 12,345
  💾 Boyut        : 8.5 MB
  🔧 Frameworkler : Flask, Streamlit
  🧠 AI Servisleri: OpenAI, Google Gemini
  📦 Bağımlılıklar: requirements.txt
  🔀 Git          : ✅
  🧪 Testler      : ✅

  📊 Dil Dağılımı:
      Python          : 75 dosya
      JavaScript      : 10 dosya
      Shell           : 4 dosya
```

> **İpucu:** Proje adı kısmi eşleşme destekler. `--project emare` yazdığınızda ismi "emare" içeren tüm projeler gösterilir.

---

### Senaryo 5: Sadece Tarama (Rapor Üretmeden)

```bash
python main.py --scan
```

Disk taraması yapar ve verileri `data/` dizinine kaydeder. Rapor üretmez.

---

## 📁 Çıktı Dosyalarını Kullanma

### Markdown Rapor

```bash
# En güncel raporu görüntüle
open "reports/son_rapor.md"

# veya VS Code ile
code "reports/son_rapor.md"
```

### JSON Verisi ile Programatik Erişim

```python
import json

with open("data/son_tarama.json", "r") as f:
    data = json.load(f)

# Tüm projelerin isimlerini listele
for p in data["projects"]:
    print(f"{p['name']} — {p['primary_language']} — {p['stats']['total_lines']} satır")

# Python projelerini filtrele
python_projs = [p for p in data["projects"] if p["primary_language"] == "Python"]
print(f"\n{len(python_projs)} Python projesi bulundu.")
```

### JSON Rapor

```bash
# jq ile güzel görüntüleme
cat reports/son_rapor.json | python -m json.tool

# Belirli alanı çekmek
python -c "import json; d=json.load(open('reports/son_rapor.json')); print(d['total_projects'])"
```

---

## ⚠️ Bilinen Sınırlamalar

| Sınırlama | Açıklama |
|-----------|----------|
| **macOS bağımlılığı** | `/Volumes/KINGSTON` bağlama noktası macOS'a özgü |
| **5 MB dosya limiti** | 5 MB'den büyük dosyalarda satır sayısı 0 olarak sayılır |
| **Tek seviye tarama** | Sadece KINGSTON kökündeki ilk seviye klasörler proje olarak tanınır |
| **İkili dosyalar** | Binary dosyalar satır sayısına dahil edilmez |
| **Encoding** | UTF-8 dışı dosyalarda hatalar görmezden gelinir |
| **Git geçmişi** | Git commit/branch bilgileri analiz edilmez |

## 🔍 Sorun Giderme

### "Önceki tarama verisi bulunamadı" hatası
```bash
# Önce tarama yapın
python main.py --scan
# Sonra rapor üretin
python main.py --report
```

### KINGSTON disk bağlı değilse
```
Disk bağlı olmalı: /Volumes/KINGSTON
# Diski takın ve tekrar deneyin
```

### İzin (Permission) hataları
```bash
# Disk izinlerini kontrol edin
ls -la /Volumes/KINGSTON
```

---

## 💡 İpuçları

1. **Düzenli tarama**: Proje ekleyip çıkardıktan sonra `python main.py` çalıştırarak güncel rapor alın
2. **Karşılaştırma**: Farklı tarihlerdeki `data/scan_*.json` dosyalarını karşılaştırarak proje büyümesini takip edin
3. **Kısmi arama**: `--project` parametresinde tam isim yazmak zorunda değilsiniz, kısmi eşleşme yeterli
4. **Hızlı güncelleme**: Tarama verisi zaten güncel ise `--report` ile sadece rapor üretin
5. **JSON ile otomasyon**: `data/son_tarama.json` dosyasını kendi scriptlerinizde kullanabilirsiniz

---

> Emare Katip v1.0 — Kullanım Kılavuzu
