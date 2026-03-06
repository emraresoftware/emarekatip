# ═══════════════════════════════════════════════════════════
#  Emare Katip — Makefile
# ═══════════════════════════════════════════════════════════
#  Kullanım:  make help
# ═══════════════════════════════════════════════════════════

PYTHON  := python3
PIP     := pip3
PROJECT := Emare Katip

.DEFAULT_GOAL := help

# ── Tarama & Rapor ────────────────────────────────────────

.PHONY: scan
scan: ## 🔍 KINGSTON diskini tara
	$(PYTHON) main.py --scan

.PHONY: report
report: ## 📝 Son verilerden rapor üret (MD + JSON + HTML + CSV)
	$(PYTHON) main.py --report

.PHONY: summary
summary: ## 📊 Kısa özet göster
	$(PYTHON) main.py --summary

.PHONY: diff
diff: ## 🔄 Son iki taramayı karşılaştır
	$(PYTHON) main.py --diff

.PHONY: all
all: ## 🚀 Tam tarama + rapor + özet
	$(PYTHON) main.py

.PHONY: verbose
verbose: ## 🔍 Detaylı log ile tam çalıştırma
	$(PYTHON) main.py --verbose

# ── Test & Kalite ─────────────────────────────────────────

.PHONY: test
test: ## 🧪 Tüm testleri çalıştır
	$(PYTHON) -m pytest tests/ -v --tb=short

.PHONY: test-cov
test-cov: ## 🧪 Testleri coverage ile çalıştır
	$(PYTHON) -m pytest tests/ -v --cov=. --cov-report=html --cov-report=term

.PHONY: lint
lint: ## 🔎 Kod kalitesi kontrolü (ruff)
	$(PYTHON) -m ruff check .

.PHONY: lint-fix
lint-fix: ## 🔧 Lint hatalarını otomatik düzelt
	$(PYTHON) -m ruff check . --fix

.PHONY: typecheck
typecheck: ## 🏷️  Tip kontrolü (mypy)
	$(PYTHON) -m mypy . --ignore-missing-imports

# ── Dashboard ─────────────────────────────────────────────

.PHONY: dashboard
dashboard: ## 🌐 Streamlit dashboard'u başlat
	streamlit run dashboard.py

# ── Kurulum ───────────────────────────────────────────────

.PHONY: install
install: ## 📦 Temel bağımlılıkları kur
	$(PIP) install pyyaml

.PHONY: install-dev
install-dev: ## 📦 Geliştirme bağımlılıklarını kur
	$(PIP) install pytest pytest-cov ruff mypy pyyaml

.PHONY: install-dashboard
install-dashboard: ## 📦 Dashboard bağımlılıklarını kur
	$(PIP) install streamlit plotly pandas

.PHONY: install-all
install-all: install install-dev install-dashboard ## 📦 Tüm bağımlılıkları kur

# ── Temizlik ──────────────────────────────────────────────

.PHONY: clean
clean: ## 🧹 Geçici dosyaları temizle
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	rm -f .coverage

.PHONY: clean-data
clean-data: ## 🗑️  Tarama verilerini temizle (dikkat!)
	rm -f data/scan_*.json data/son_tarama.json

.PHONY: clean-reports
clean-reports: ## 🗑️  Rapor dosyalarını temizle
	rm -f reports/*.md reports/*.json reports/*.html reports/*.csv reports/*.txt

.PHONY: clean-all
clean-all: clean clean-data clean-reports ## 🗑️  Her şeyi temizle

# ── Proje Bilgisi ─────────────────────────────────────────

.PHONY: project
project: ## 📁 Belirli bir projeyi göster (PROJE=isim)
	$(PYTHON) main.py --project "$(PROJE)"

# ── Yardım ────────────────────────────────────────────────

.PHONY: help
help: ## ❓ Bu yardım mesajını göster
	@echo ""
	@echo "  ╔══════════════════════════════════════════╗"
	@echo "  ║     $(PROJECT) — Makefile Komutları      ║"
	@echo "  ╚══════════════════════════════════════════╝"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'
	@echo ""
