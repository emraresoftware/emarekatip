#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║          EMARE KATİP — Streamlit Dashboard                       ║
║                                                                  ║
║  Tarama verilerini görsel arayüzde keşfedin.                     ║
║                                                                  ║
║  Kullanım:                                                       ║
║      pip install streamlit plotly pandas                          ║
║      streamlit run dashboard.py                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""

import sys
import os
import json
from pathlib import Path

# Proje kökünü path'e ekle
BASE_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(BASE_DIR))

try:
    import streamlit as st
    import plotly.express as px
    import plotly.graph_objects as go
    import pandas as pd
except ImportError:
    print("❌ Gerekli paketler yüklü değil. Lütfen kurun:")
    print("   pip install streamlit plotly pandas")
    sys.exit(1)

import subprocess

from config import DATA_DIR


# ── Yardımcı fonksiyonlar ────────────────────────────────────

def run_scan(depth, lang, category, min_files, include_empty, skip_dupes, filetype=None):
    """Arka planda tarama çalıştırır."""
    cmd = [sys.executable, str(BASE_DIR / "main.py"), "--scan"]
    if depth is not None:
        cmd += ["--depth", str(depth)]
    if lang:
        cmd += ["--lang", lang]
    if category:
        cmd += ["--category", category]
    if min_files > 0:
        cmd += ["--min-files", str(min_files)]
    if include_empty:
        cmd += ["--include-empty"]
    if not skip_dupes:
        cmd += ["--no-skip-dupes"]
    if filetype:
        cmd += ["--scan-filetype", filetype]

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(BASE_DIR), timeout=300)
    return result

@st.cache_data
def load_scan_data(path: str) -> dict:
    """Tarama verisini yükler ve cache'ler."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_available_scans() -> list:
    """Mevcut tarama dosyalarını listeler."""
    if not DATA_DIR.exists():
        return []
    scans = sorted(DATA_DIR.glob("scan_*.json"), reverse=True)
    # son_tarama.json'u hariç tut
    return [s for s in scans if s.name != "son_tarama.json"]


def scan_to_df(data: dict) -> pd.DataFrame:
    """Tarama verisini DataFrame'e çevirir."""
    rows = []
    for p in data.get("projects", []):
        stats = p.get("stats", {})
        rows.append({
            "Proje": p.get("name", ""),
            "Kategori": p.get("category", ""),
            "Dil": p.get("primary_language", ""),
            "Tür": p.get("project_type", ""),
            "Olgunluk": p.get("maturity", ""),
            "Dosya": stats.get("total_files", 0),
            "Kod Dosyası": stats.get("code_files", 0),
            "Satır": stats.get("total_lines", 0),
            "Boyut (MB)": stats.get("total_size_mb", 0),
            "Git": "✅" if p.get("has_git") else "❌",
            "Test": "✅" if p.get("has_tests") else "❌",
            "CI/CD": "✅" if p.get("has_ci") else "❌",
            "Frameworkler": ", ".join(p.get("frameworks", [])),
            "AI Servisleri": ", ".join(p.get("ai_services", [])),
        })
    return pd.DataFrame(rows)


# ── Sayfa yapılandırması ──────────────────────────────────────

st.set_page_config(
    page_title="Emare Katip Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar ────────────────────────────────────────────────────

st.sidebar.title("📀 Emare Katip")
st.sidebar.caption("KINGSTON Disk Analiz Paneli")

# ── Yeniden Tarama Bölümü ────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.subheader("🔄 Yeni Tarama")

with st.sidebar.form("scan_form"):
    scan_depth = st.number_input("📏 Tarama Derinliği", min_value=0, max_value=10, value=3,
                                  help="0 = sınırsız, 3 = varsayılan")
    scan_lang = st.selectbox("🗣️ Dil Filtresi",
                              ["Tümü", "Python", "JavaScript", "TypeScript", "PHP", "Rust", "Go", "Java", "Shell", "C", "C++"],
                              index=0)
    scan_category = st.selectbox("🏷️ Kategori Filtresi",
                                  ["Tümü", "AI / Yapay Zeka", "AI Asistan", "AI Bot", "Web Uygulama", "Web Servis", "Bot", "Sistem", "Yönetim Paneli", "Genel"],
                                  index=0)
    scan_filetype = st.selectbox("📎 Dosya Türü Filtresi",
                                  ["Tümü", ".md", ".py", ".js", ".ts", ".tsx", ".jsx", ".php", ".rs", ".go", ".java", ".sh", ".json", ".yaml", ".toml"],
                                  index=0, help="Sadece bu dosya türünü içeren projeler listelenir")
    scan_min_files = st.number_input("📁 Min Dosya Sayısı", min_value=0, max_value=100, value=0,
                                      help="Bu sayıdan az dosyalı projeler atlanır")
    scan_include_empty = st.checkbox("📭 Boş projeleri dahil et", value=False)
    scan_skip_dupes = st.checkbox("🚫 Kopyaları atla", value=True)

    scan_submitted = st.form_submit_button("🚀 TARA", type="primary", width="stretch")

if scan_submitted:
    with st.sidebar:
        with st.spinner("⏳ KINGSTON taranıyor... Bu birkaç dakika sürebilir."):
            try:
                _lang = None if scan_lang == "Tümü" else scan_lang
                _cat = None if scan_category == "Tümü" else scan_category
                _ft = None if scan_filetype == "Tümü" else scan_filetype
                result = run_scan(
                    depth=scan_depth,
                    lang=_lang,
                    category=_cat,
                    min_files=scan_min_files,
                    include_empty=scan_include_empty,
                    skip_dupes=scan_skip_dupes,
                    filetype=_ft,
                )
                if result.returncode == 0:
                    st.success("✅ Tarama tamamlandı! Sayfa yenileniyor...")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error(f"❌ Tarama hatası:\n{result.stderr[-500:]}")
            except subprocess.TimeoutExpired:
                st.error("⏰ Tarama zaman aşımına uğradı (5dk). Daha dar filtre deneyin.")
            except Exception as e:
                st.error(f"❌ Hata: {e}")

st.sidebar.markdown("---")

# Tarama seçici
scans = get_available_scans()
if not scans:
    st.error("❌ Tarama verisi bulunamadı. Önce tarama yapın: `python main.py --scan`")
    st.stop()

latest = DATA_DIR / "son_tarama.json"
scan_options = ["📌 Son Tarama"] + [s.stem for s in scans]
selected = st.sidebar.selectbox("Tarama Seçin", scan_options)

if selected == "📌 Son Tarama":
    scan_path = latest
else:
    scan_path = DATA_DIR / f"{selected}.json"

data = load_scan_data(str(scan_path))
df = scan_to_df(data)

# ── Filtreler ──────────────────────────────────────────────────

st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Filtreler")

categories = ["Tümü"] + sorted(df["Kategori"].unique().tolist())
sel_category = st.sidebar.selectbox("Kategori", categories)

languages = ["Tümü"] + sorted(df["Dil"].unique().tolist())
sel_language = st.sidebar.selectbox("Dil", languages)

maturities = ["Tümü"] + sorted(df["Olgunluk"].unique().tolist())
sel_maturity = st.sidebar.selectbox("Olgunluk", maturities)

# Filtre uygula
filtered = df.copy()
if sel_category != "Tümü":
    filtered = filtered[filtered["Kategori"] == sel_category]
if sel_language != "Tümü":
    filtered = filtered[filtered["Dil"] == sel_language]
if sel_maturity != "Tümü":
    filtered = filtered[filtered["Olgunluk"] == sel_maturity]


# ── Başlık ─────────────────────────────────────────────────────

st.title("📊 Emare Katip — KINGSTON Analiz Dashboard")
st.caption(f"Tarama: {data.get('scan_date', 'Bilinmiyor')[:19]}  •  Kök: {data.get('scan_root', '')}")

# ── KPI kartları ───────────────────────────────────────────────

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("📁 Projeler", len(filtered))
col2.metric("📄 Dosyalar", f"{filtered['Dosya'].sum():,}")
col3.metric("💻 Kod Dosyası", f"{filtered['Kod Dosyası'].sum():,}")
col4.metric("📝 Satırlar", f"{filtered['Satır'].sum():,}")
col5.metric("💾 Boyut", f"{filtered['Boyut (MB)'].sum():.1f} MB")

st.markdown("---")

# ── Grafikler ──────────────────────────────────────────────────

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📊 Genel Bakış", "📁 Proje Tablosu", "🔍 Arama", "🔎 Proje Detayı", "📈 Karşılaştırma", "🗂️ İskelet & Duplikeler"])

with tab1:
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        # Dil dağılımı — Pasta
        lang_counts = filtered["Dil"].value_counts().reset_index()
        lang_counts.columns = ["Dil", "Proje Sayısı"]
        fig_lang = px.pie(
            lang_counts, names="Dil", values="Proje Sayısı",
            title="🗣️ Dil Dağılımı", hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3,
        )
        st.plotly_chart(fig_lang, width="stretch")

    with chart_col2:
        # Kategori dağılımı — Bar
        cat_counts = filtered["Kategori"].value_counts().reset_index()
        cat_counts.columns = ["Kategori", "Proje Sayısı"]
        fig_cat = px.bar(
            cat_counts, x="Kategori", y="Proje Sayısı",
            title="🏷️ Kategori Dağılımı",
            color="Kategori",
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        fig_cat.update_layout(showlegend=False)
        st.plotly_chart(fig_cat, width="stretch")

    chart_col3, chart_col4 = st.columns(2)

    with chart_col3:
        # Olgunluk dağılımı
        mat_counts = filtered["Olgunluk"].value_counts().reset_index()
        mat_counts.columns = ["Olgunluk", "Proje Sayısı"]
        fig_mat = px.pie(
            mat_counts, names="Olgunluk", values="Proje Sayısı",
            title="📊 Olgunluk Dağılımı", hole=0.4,
        )
        st.plotly_chart(fig_mat, width="stretch")

    with chart_col4:
        # En büyük 15 proje — Yatay bar
        top = filtered.nlargest(15, "Satır")
        fig_top = px.bar(
            top, x="Satır", y="Proje", orientation="h",
            title="🏆 En Büyük 15 Proje (Satır)",
            color="Dil",
        )
        fig_top.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_top, width="stretch")

    # Boyut vs Satır scatter
    st.subheader("💾 Boyut vs Satır")
    fig_scatter = px.scatter(
        filtered, x="Boyut (MB)", y="Satır", size="Dosya",
        color="Kategori", hover_name="Proje",
        title="Proje Boyut ve Satır İlişkisi",
        size_max=40,
    )
    st.plotly_chart(fig_scatter, width="stretch")


with tab2:
    st.subheader("📁 Proje Listesi")

    # Arama
    search = st.text_input("🔍 Proje ara", placeholder="Proje adı yazın...")
    display_df = filtered.copy()
    if search:
        display_df = display_df[display_df["Proje"].str.contains(search, case=False, na=False)]

    # Sıralama
    sort_col = st.selectbox("Sıralama", ["Satır", "Dosya", "Boyut (MB)", "Proje"], index=0)
    sort_asc = st.checkbox("Artan sıra", value=False)
    display_df = display_df.sort_values(sort_col, ascending=sort_asc)

    st.dataframe(
        display_df,
        width="stretch",
        height=600,
        hide_index=True,
    )

    st.download_button(
        "📥 CSV İndir",
        display_df.to_csv(index=False).encode("utf-8"),
        "emare_katip_projeler.csv",
        "text/csv",
    )


with tab3:
    st.subheader("🔍 Akıllı Arama")
    st.caption("Proje adı, dil, framework, README ve dosya içeriklerinde arama yapın")

    with st.form("search_form"):
        search_query = st.text_input("🔍 Ne arıyorsunuz?", placeholder="openai, flask, asistan, whatsapp...")

        s_col1, s_col2, s_col3 = st.columns([2, 1, 1])
        with s_col1:
            search_fields = st.multiselect(
                "Arama Alanları",
                ["Proje Adı", "Dil", "Kategori", "Framework", "AI Servisi", "README", "Dosya Adı", "Dosya İçeriği"],
                default=["Proje Adı", "Dil", "Kategori", "Framework", "AI Servisi", "README", "Dosya Adı"],
            )
        with s_col2:
            filetype_options = ["Tümü", ".md", ".py", ".js", ".ts", ".tsx", ".jsx", ".php", ".rs", ".go", ".java", ".sh", ".json", ".yaml", ".toml", ".txt"]
            sel_filetype = st.selectbox("📎 Dosya Türü", filetype_options, index=0)
        with s_col3:
            max_content_results = st.slider("Maks sonuç", 5, 50, 10)

        search_clicked = st.form_submit_button("🔍 ARA", type="primary", width="stretch")

    # Session state başlat
    if "search_results" not in st.session_state:
        st.session_state.search_results = None
        st.session_state.search_term = ""

    if search_clicked and search_query:
        st.session_state.search_term = search_query
        q = search_query.lower()
        _results = []

        for proj in data.get("projects", []):
            hits = []
            p_name = proj.get("name", "")
            p_cat = proj.get("category", "")
            p_lang = proj.get("primary_language", "")
            p_frameworks = proj.get("frameworks", [])
            p_ai = proj.get("ai_services", [])
            p_readme = proj.get("readme_summary", "") or ""
            p_path = proj.get("path", "")
            p_stats = proj.get("stats", {})

            if "Proje Adı" in search_fields and q in p_name.lower():
                hits.append(("📁 Ad", p_name))
            if "Dil" in search_fields and q in p_lang.lower():
                hits.append(("🗣️ Dil", p_lang))
            if "Kategori" in search_fields and q in p_cat.lower():
                hits.append(("🏷️ Kategori", p_cat))
            if "Framework" in search_fields:
                fw = [f for f in p_frameworks if q in f.lower()]
                if fw:
                    hits.append(("🔧 Framework", ", ".join(fw)))
            if "AI Servisi" in search_fields:
                ai = [a for a in p_ai if q in a.lower()]
                if ai:
                    hits.append(("🧠 AI", ", ".join(ai)))
            if "README" in search_fields and q in p_readme.lower():
                idx = p_readme.lower().index(q)
                start = max(0, idx - 50)
                end = min(len(p_readme), idx + len(search_query) + 50)
                snippet = p_readme[start:end].replace('\n', ' ')
                hits.append(("📖 README", f"...{snippet}..."))

            # Dosya adı arama (tam yol bilgisiyle)
            if "Dosya Adı" in search_fields:
                files = proj.get("files", [])
                if sel_filetype != "Tümü":
                    f_hits = [(f.get("name", ""), f.get("path", "")) for f in files 
                              if f.get("extension", "").lower() == sel_filetype and q in f.get("name", "").lower()]
                else:
                    f_hits = [(f.get("name", ""), f.get("path", "")) for f in files if q in f.get("name", "").lower()]
                if f_hits:
                    for fname, fpath in f_hits[:10]:
                        hits.append(("📄 file", {"name": fname, "path": fpath}))
                    if len(f_hits) > 10:
                        hits.append(("📄 info", f"+{len(f_hits)-10} dosya daha"))

            # Dosya içeriği arama (derin arama)
            if "Dosya İçeriği" in search_fields and os.path.isdir(p_path):
                import os as _os
                from config import CODE_EXTENSIONS, DOC_EXTENSIONS, CONFIG_FILES, EXCLUDED_DIRS
                searchable_exts = set(CODE_EXTENSIONS) | set(DOC_EXTENSIONS) | set(CONFIG_FILES)
                content_hits = []
                try:
                    for root, dirs, fnames in _os.walk(p_path):
                        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS and not d.startswith('.')]
                        for fn in fnames:
                            ext = _os.path.splitext(fn)[1].lower()
                            # Dosya türü filtresi
                            if sel_filetype != "Tümü":
                                if ext != sel_filetype:
                                    continue
                            elif ext not in searchable_exts:
                                continue
                            fp = _os.path.join(root, fn)
                            try:
                                if _os.path.getsize(fp) > 2 * 1024 * 1024:
                                    continue
                                with open(fp, 'r', encoding='utf-8', errors='ignore') as fobj:
                                    for line_no, line in enumerate(fobj, 1):
                                        if q in line.lower():
                                            rel = _os.path.relpath(fp, p_path)
                                            content_hits.append((rel, line_no, line.strip()[:100]))
                                            if len(content_hits) >= max_content_results:
                                                break
                            except (PermissionError, OSError):
                                continue
                            if len(content_hits) >= max_content_results:
                                break
                        if len(content_hits) >= max_content_results:
                            break
                except Exception:
                    pass
                if content_hits:
                    hits.append(("🔎 İçerik", f"{len(content_hits)} eşleşme"))
                    for rel, ln, txt in content_hits[:10]:
                        full = _os.path.join(p_path, rel)
                        hits.append(("🔎 content", {"rel": rel, "line": ln, "text": txt, "path": full}))

            if hits:
                _results.append({
                    "name": p_name,
                    "path": p_path,
                    "category": p_cat,
                    "language": p_lang,
                    "code_files": p_stats.get("code_files", 0),
                    "lines": p_stats.get("total_lines", 0),
                    "hits": hits,
                })

        # Sonuçları session_state'e kaydet
        st.session_state.search_results = _results

    # Sonuçları göster (session_state'ten)
    search_results = st.session_state.search_results
    if search_results is not None and len(search_results) > 0:
        st.success(f"✅ {len(search_results)} projede eşleşme bulundu!")

        for res in search_results:
            with st.expander(f"📁 {res['name']}  —  [{res['category']} · {res['language']} · {res['code_files']} kod, {res['lines']:,} satır]", expanded=False):
                from urllib.parse import quote
                folder_url = "file://" + quote(res['path'])
                st.markdown(f"📂 `{res['path']}`  &nbsp; [📁 Klasörü Aç]({folder_url})")

                for label, detail in res["hits"]:
                    if label == "📄 file" and isinstance(detail, dict):
                        fpath = detail['path']
                        fname = detail['name']
                        file_url = "file://" + quote(fpath)
                        parent_url = "file://" + quote(os.path.dirname(fpath))
                        st.markdown(
                            f"&nbsp;&nbsp;&nbsp;&nbsp;📄 **[{fname}]({file_url})**"
                            f" &nbsp; [📁 Konum]({parent_url})"
                        )
                    elif label == "📄 info":
                        st.caption(f"&nbsp;&nbsp;&nbsp;&nbsp;{detail}")
                    elif label == "🔎 content" and isinstance(detail, dict):
                        fpath = detail['path']
                        rel = detail['rel']
                        ln = detail['line']
                        txt = detail['text']
                        file_url = "file://" + quote(fpath)
                        parent_url = "file://" + quote(os.path.dirname(fpath))
                        st.markdown(
                            f"&nbsp;&nbsp;&nbsp;&nbsp;`{rel}:{ln}` "
                            f" [📄 Aç]({file_url}) [📁 Konum]({parent_url})"
                        )
                        st.caption(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`{txt}`")
                    elif isinstance(detail, str):
                        st.markdown(f"**{label}:** {detail}")
    elif search_results is not None and len(search_results) == 0:
        st.warning(f"❌ '{st.session_state.search_term}' için sonuç bulunamadı.")
        if "Dosya İçeriği" not in search_fields:
            st.info("💡 Dosya içeriklerinde de aramak için 'Dosya İçeriği' alanını ekleyin.")


with tab4:
    st.subheader("🔍 Proje Detayı")

    project_names = sorted(filtered["Proje"].tolist())
    if project_names:
        sel_project = st.selectbox("Proje Seçin", project_names)

        # Ham veriden detayları al
        project_data = next((p for p in data["projects"] if p["name"] == sel_project), None)
        if project_data:
            dc1, dc2, dc3 = st.columns(3)
            dc1.metric("Kategori", project_data.get("category", ""))
            dc2.metric("Dil", project_data.get("primary_language", ""))
            dc3.metric("Olgunluk", project_data.get("maturity", ""))

            stats = project_data.get("stats", {})
            dc4, dc5, dc6 = st.columns(3)
            dc4.metric("Dosyalar", stats.get("total_files", 0))
            dc5.metric("Satırlar", f"{stats.get('total_lines', 0):,}")
            dc6.metric("Boyut", f"{stats.get('total_size_mb', 0):.1f} MB")

            # Özellikler
            feature_col1, feature_col2 = st.columns(2)
            with feature_col1:
                st.markdown("**🔧 Özellikler:**")
                features = {
                    "Git": project_data.get("has_git", False),
                    "Testler": project_data.get("has_tests", False),
                    "Dokümantasyon": project_data.get("has_docs", False),
                    "CI/CD": project_data.get("has_ci", False),
                }
                for feat, val in features.items():
                    st.write(f"{'✅' if val else '❌'} {feat}")

            with feature_col2:
                if project_data.get("frameworks"):
                    st.markdown("**🔧 Frameworkler:**")
                    st.write(", ".join(project_data["frameworks"]))
                if project_data.get("ai_services"):
                    st.markdown("**🧠 AI Servisleri:**")
                    st.write(", ".join(project_data["ai_services"]))
                if project_data.get("dependencies"):
                    st.markdown("**📦 Bağımlılıklar:**")
                    st.write(", ".join(project_data["dependencies"][:20]))

            # Dil dağılımı
            langs = stats.get("languages", {})
            if langs:
                st.markdown("**📊 Dil Dağılımı:**")
                lang_df = pd.DataFrame(list(langs.items()), columns=["Dil", "Dosya"])
                fig = px.bar(lang_df, x="Dil", y="Dosya", color="Dil")
                fig.update_layout(showlegend=False, height=300)
                st.plotly_chart(fig, width="stretch")

            # Açıklama
            desc = project_data.get("description") or project_data.get("readme_summary")
            if desc:
                st.markdown("**📖 Açıklama:**")
                st.info(desc[:1000])


with tab5:
    st.subheader("📈 Tarama Karşılaştırma")

    scan_files = get_available_scans()
    if len(scan_files) < 2:
        st.warning("⚠️ Karşılaştırma için en az 2 tarama kaydı gerekli.")
    else:
        cmp_col1, cmp_col2 = st.columns(2)
        with cmp_col1:
            old_scan = st.selectbox("Eski Tarama", [s.stem for s in scan_files], index=min(1, len(scan_files) - 1))
        with cmp_col2:
            new_scan = st.selectbox("Yeni Tarama", [s.stem for s in scan_files], index=0)

        if st.button("🔄 Karşılaştır"):
            old_data = load_scan_data(str(DATA_DIR / f"{old_scan}.json"))
            new_data = load_scan_data(str(DATA_DIR / f"{new_scan}.json"))

            old_df = scan_to_df(old_data)
            new_df = scan_to_df(new_data)

            # Genel karşılaştırma
            kcol1, kcol2, kcol3 = st.columns(3)
            kcol1.metric("Projeler", len(new_df), delta=len(new_df) - len(old_df))
            kcol2.metric("Satırlar", f"{new_df['Satır'].sum():,}",
                         delta=int(new_df["Satır"].sum() - old_df["Satır"].sum()))
            kcol3.metric("Dosyalar", f"{new_df['Dosya'].sum():,}",
                         delta=int(new_df["Dosya"].sum() - old_df["Dosya"].sum()))

            # Yeni ve silinen projeler
            old_names = set(old_df["Proje"])
            new_names = set(new_df["Proje"])

            added = new_names - old_names
            removed = old_names - new_names

            if added:
                st.success(f"🆕 Yeni Projeler ({len(added)}): {', '.join(sorted(added))}")
            if removed:
                st.error(f"🗑️ Silinen Projeler ({len(removed)}): {', '.join(sorted(removed))}")

            # Değişen projelerin detayları
            common = old_names & new_names
            changes = []
            for name in sorted(common):
                old_row = old_df[old_df["Proje"] == name].iloc[0]
                new_row = new_df[new_df["Proje"] == name].iloc[0]
                line_diff = int(new_row["Satır"] - old_row["Satır"])
                if line_diff != 0:
                    changes.append({"Proje": name, "Eski Satır": int(old_row["Satır"]),
                                    "Yeni Satır": int(new_row["Satır"]), "Fark": line_diff})

            if changes:
                st.markdown("**🔄 Değişen Projeler:**")
                change_df = pd.DataFrame(changes).sort_values("Fark", ascending=False)
                st.dataframe(change_df, width="stretch", hide_index=True)


with tab6:
    st.subheader("🗂️ Dosya Gezgini")
    st.info("✅ Tab6 yüklendi — test modu")

if False:  # ── GEÇİCİ DEVRE DIŞI ──
    harita_path = DATA_DIR / "harita.md"
    iskelet_path = DATA_DIR / "iskelet.json"
    dupe_path = DATA_DIR / "duplikeler.json"

    tc1, tc2 = st.columns([1, 3])
    with tc1:
        if st.button("🗺️ Haritayı Yeniden Oluştur", key="finder_map"):
            with st.spinner("⏳ Taranıyor..."):
                try:
                    cmd = [sys.executable, str(BASE_DIR / "main.py"),
                           "--skeleton", "--find-dupes", "--depth", "0"]
                    result = subprocess.run(cmd, capture_output=True, text=True,
                                            cwd=str(BASE_DIR), timeout=600)
                    st.success("✅ Bitti!") if result.returncode == 0 else st.error("❌ Hata")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ {e}")
    with tc2:
        if harita_path.exists():
            h_mb = harita_path.stat().st_size / (1024 * 1024)
            st.caption(f"📄 harita.md: {h_mb:.0f} MB — Konumu: `{harita_path}`")

    # ── Meta istatistikler (ilk 3000 char, hafif) ────────────────
    iskelet_meta = None
    if iskelet_path.exists():
        try:
            with open(iskelet_path, "r", encoding="utf-8") as f:
                head = f.read(3000)
            import re
            def _extract(key):
                m = re.search(rf'"{key}":\s*(".*?"|[\d.]+|null)', head)
                return m.group(1).strip('"') if m else None
            def _extract_int(key):
                m = re.search(rf'"{key}":\s*(\d+)', head)
                return int(m.group(1)) if m else 0
            def _extract_obj(key):
                m = re.search(rf'"{key}":\s*\{{([^}}]+)\}}', head)
                if m:
                    pairs = re.findall(r'"(\w+)":\s*(\d+)', m.group(1))
                    return {k: int(v) for k, v in pairs}
                return {}
            iskelet_meta = {
                "scan_date": _extract("scan_date") or "",
                "total_folders": _extract_int("total_folders"),
                "total_files": _extract_int("total_files"),
                "total_size_human": _extract("total_size_human") or "?",
                "max_depth": _extract_int("max_depth"),
                "file_categories": _extract_obj("file_categories"),
            }
        except Exception:
            pass

    if iskelet_meta:
        mc = st.columns(5)
        mc[0].metric("📂 Klasör", f"{iskelet_meta['total_folders']:,}")
        mc[1].metric("📄 Dosya", f"{iskelet_meta['total_files']:,}")
        mc[2].metric("💾 Boyut", iskelet_meta["total_size_human"])
        mc[3].metric("📏 Derinlik", iskelet_meta["max_depth"] or "∞")
        mc[4].metric("📅 Tarih", iskelet_meta["scan_date"][:10])

    finder_tab1, finder_tab2, finder_tab3 = st.tabs(
        ["📂 Dosya Gezgini", "📊 İstatistikler", "📁 Aynı İsimli Klasörler"])

    # ═══════════════════════════════════════════════════════════════
    # TAB 1: FINDER — Ultra hafif
    # ═══════════════════════════════════════════════════════════════
    with finder_tab1:
        from config import SCAN_ROOT, EXCLUDED_DIRS, APP_EXCLUDED_SUFFIXES, CODE_EXTENSIONS
        import subprocess as _sp
        from html import escape as _esc
        from datetime import datetime as _dt

        if "finder_cwd" not in st.session_state:
            st.session_state.finder_cwd = str(SCAN_ROOT)

        current_abs = st.session_state.finder_cwd
        scan_root_str = str(SCAN_ROOT)

        def _short(p):
            r = os.path.relpath(p, scan_root_str)
            return "KINGSTON/" + r if r != "." else "KINGSTON"

        EXT_ICONS = {
            ".py":"🐍",".js":"🟨",".ts":"🔷",".jsx":"⚛️",".tsx":"⚛️",
            ".php":"🐘",".rs":"🦀",".go":"🔵",".java":"☕",
            ".c":"⚙️",".cpp":"⚙️",".h":"⚙️",".swift":"🍎",".rb":"💎",
            ".sh":"🐚",".md":"📝",".txt":"📄",".pdf":"📕",
            ".json":"📋",".yaml":"📋",".yml":"📋",".toml":"📋",".xml":"📋",
            ".html":"🌐",".css":"🎨",".png":"🖼️",".jpg":"🖼️",".gif":"🖼️",".svg":"🖼️",
            ".mp3":"🎵",".wav":"🎵",".mp4":"🎬",".mov":"🎬",
            ".zip":"📦",".tar":"📦",".gz":"📦",".sql":"🗃️",".db":"🗃️",
            ".log":"📜",".csv":"📊",".xls":"📊",".lock":"🔒",".env":"🔒",
        }

        def _hsz(b):
            if b < 1024: return f"{b} B"
            if b < 1048576: return f"{b/1024:.1f} KB"
            if b < 1073741824: return f"{b/1048576:.1f} MB"
            return f"{b/1073741824:.2f} GB"

        # ── Konum + Breadcrumb ─────────────────────
        st.code(current_abs, language=None)

        rel = os.path.relpath(current_abs, scan_root_str)
        parts = [] if rel == "." else rel.split(os.sep)
        crumbs = [("💿 KINGSTON", scan_root_str)]
        for i, p in enumerate(parts):
            crumbs.append((f"📂 {p}", os.path.join(scan_root_str, *parts[:i+1])))
        if len(crumbs) > 6:
            crumbs = crumbs[:1] + crumbs[-4:]

        bc = st.columns(len(crumbs))
        for i, (lbl, cp) in enumerate(crumbs):
            if bc[i].button(lbl, key=f"bc_{i}"):
                st.session_state.finder_cwd = cp
                st.rerun()

        # ── Üst klasör + Finder ────────────────────
        t1, t2 = st.columns(2)
        if current_abs != scan_root_str:
            if t1.button("⬆️ Üst Klasör", key="go_up"):
                st.session_state.finder_cwd = os.path.dirname(current_abs)
                st.rerun()
        if t2.button("🔍 Finder'da Aç", key="open_finder"):
            _sp.Popen(["open", current_abs])

        # ── Filtre ─────────────────────────────────
        search_filter = st.text_input("🔎 Filtrele:", key="ff", placeholder="ad ara...",
                                      label_visibility="collapsed")

        # ── Disk oku ───────────────────────────────
        try:
            raw = os.listdir(current_abs)
        except (PermissionError, FileNotFoundError):
            st.warning("⚠️ Erişim yok veya bulunamadı.")
            raw = []
            if not os.path.isdir(current_abs):
                st.session_state.finder_cwd = scan_root_str

        raw = [e for e in raw
               if not e.startswith(".")
               and e not in EXCLUDED_DIRS
               and not any(e.endswith(s) for s in APP_EXCLUDED_SUFFIXES)]
        if search_filter:
            raw = [e for e in raw if search_filter.lower() in e.lower()]

        # ── Veri topla ─────────────────────────────
        dirs = []
        files = []
        marker_set = {"package.json","requirements.txt","Cargo.toml","composer.json",
                      "go.mod","Makefile","setup.py","pyproject.toml","artisan"}

        for name in sorted(raw, key=str.lower):
            full = os.path.join(current_abs, name)
            try:
                si = os.stat(full, follow_symlinks=False)
                mod = _dt.fromtimestamp(si.st_mtime).strftime("%Y-%m-%d %H:%M")
                if os.path.isdir(full):
                    try:
                        sub = [s for s in os.listdir(full)
                               if not s.startswith(".") and s not in EXCLUDED_DIRS]
                    except (PermissionError, OSError):
                        sub = []
                    ss = set(sub)
                    if ss & marker_set: t = "📦 Proje"
                    elif any(os.path.splitext(s)[1].lower() in CODE_EXTENSIONS for s in ss): t = "💻 Kod"
                    elif not sub: t = "📭 Boş"
                    else: t = "📂 Klasör"
                    dirs.append({"Ad": f"📂 {name}", "Yol": _short(full),
                                 "Tür": t, "Öğe": len(sub), "Tarih": mod,
                                 "_path": full, "_name": name})
                else:
                    ext = os.path.splitext(name)[1].lower()
                    icon = EXT_ICONS.get(ext, "📄")
                    files.append({"Ad": f"{icon} {name}", "Yol": _short(full),
                                  "Boyut": _hsz(si.st_size), "Uzantı": ext,
                                  "Tarih": mod, "_path": full})
            except (OSError, PermissionError):
                continue

        st.caption(f"📂 {len(dirs)} klasör  •  📄 {len(files)} dosya")

        # ── Klasörler: st.dataframe + tek navigasyon butonu ──
        if dirs:
            st.markdown("##### 📂 Klasörler")
            dir_df = pd.DataFrame(dirs)[["Ad", "Yol", "Tür", "Öğe", "Tarih"]]
            st.dataframe(dir_df, hide_index=True, width="stretch",
                         column_config={
                             "Ad": st.column_config.TextColumn("Ad", width="medium"),
                             "Yol": st.column_config.TextColumn("Yol", width="large"),
                             "Tür": st.column_config.TextColumn("Tür", width="small"),
                             "Öğe": st.column_config.NumberColumn("Öğe", width="small"),
                             "Tarih": st.column_config.TextColumn("Tarih", width="small"),
                         })

            # Navigasyon: klasör seç → git
            dir_names = [d["_name"] for d in dirs]
            sel_dir = st.selectbox("📂 Klasör seç ve gir:", dir_names,
                                   key="dir_nav_sel", label_visibility="collapsed")
            if st.button("➡️ Seçili klasöre gir", key="dir_go"):
                target = next((d["_path"] for d in dirs if d["_name"] == sel_dir), None)
                if target:
                    st.session_state.finder_cwd = target
                    st.rerun()

        # ── Dosyalar: st.dataframe (tek widget) ───
        if files:
            st.markdown("##### 📄 Dosyalar")
            file_df = pd.DataFrame(files)[["Ad", "Yol", "Boyut", "Uzantı", "Tarih"]]
            st.dataframe(file_df, hide_index=True, width="stretch",
                         column_config={
                             "Ad": st.column_config.TextColumn("Ad", width="medium"),
                             "Yol": st.column_config.TextColumn("Yol", width="large"),
                             "Boyut": st.column_config.TextColumn("Boyut", width="small"),
                             "Uzantı": st.column_config.TextColumn("Uzantı", width="small"),
                             "Tarih": st.column_config.TextColumn("Tarih", width="small"),
                         })

        if not dirs and not files:
            st.info("📭 Boş" if not search_filter else f"🔎 '{search_filter}' bulunamadı.")

    # ═══════════════════════════════════════════════════════════════
    # TAB 2: İSTATİSTİKLER
    # ═══════════════════════════════════════════════════════════════
    with finder_tab2:
        if iskelet_meta and iskelet_meta.get("file_categories"):
            cats = iskelet_meta["file_categories"]
            cat_df = pd.DataFrame([{"Kategori": k, "Sayı": v} for k, v in cats.items()])
            fig = px.pie(cat_df, names="Kategori", values="Sayı",
                         title="📎 Dosya Türü Dağılımı", hole=0.4)
            st.plotly_chart(fig, width="stretch")

            st.markdown(f"""
            | Metrik | Değer |
            |--------|-------|
            | 📂 Klasör | **{iskelet_meta['total_folders']:,}** |
            | 📄 Dosya | **{iskelet_meta['total_files']:,}** |
            | 💾 Boyut | **{iskelet_meta['total_size_human']}** |
            """)

            if harita_path.exists():
                with st.expander("🗺️ Harita Önizleme (ilk 100 satır)"):
                    with open(harita_path, "r", encoding="utf-8") as f:
                        lines = []
                        for i, line in enumerate(f):
                            if i >= 100: break
                            lines.append(line)
                    st.code("".join(lines), language="markdown")
        else:
            st.warning("⚠️ Veri yok. '🗺️ Haritayı Yeniden Oluştur' butonuna tıklayın.")

    # ═══════════════════════════════════════════════════════════════
    # TAB 3: AYNI İSİMLİ KLASÖRLER
    # ═══════════════════════════════════════════════════════════════
    with finder_tab3:
        if dupe_path.exists():
            try:
                with open(dupe_path, "r", encoding="utf-8") as f:
                    dupes = json.load(f)
            except Exception:
                dupes = {"duplicates": []}

            dupe_list = dupes.get("duplicates", [])
            st.info(f"📁 **{len(dupe_list)}** grup  •  "
                    f"Toplam: **{sum(d.get('count', 0) for d in dupe_list)}**")

            if dupe_list:
                top = sorted(dupe_list, key=lambda x: -x.get("count", 0))[:20]
                rows = []
                for d in top:
                    locs = d.get("locations", [])
                    paths = []
                    for loc in locs[:3]:
                        p = loc.get("path", str(loc)) if isinstance(loc, dict) else str(loc)
                        paths.append(p.replace("/Volumes/KINGSTON/", ""))
                    rows.append({
                        "Klasör": d.get("name", ""),
                        "Tekrar": d.get("count", 0),
                        "Konumlar": " | ".join(paths)
                    })
                st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

                chart = pd.DataFrame([{"Klasör": d["name"], "Tekrar": d["count"]} for d in top])
                fig = px.bar(chart, x="Klasör", y="Tekrar", title="🔁 Top 20",
                             color="Tekrar", color_continuous_scale="Reds")
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, width="stretch")

                with st.expander("📋 Detay (ilk 30)"):
                    for d_idx, d in enumerate(sorted(dupe_list, key=lambda x: -x.get("count", 0))[:30]):
                        locs = d.get("locations", [])
                        loc_txt = "\n".join(
                            f"  └─ `{(loc.get('path', str(loc)) if isinstance(loc, dict) else str(loc)).replace('/Volumes/KINGSTON/', 'KINGSTON/')}`"
                            for loc in locs
                        )
                        st.markdown(f"**📁 {d['name']}** ×{d['count']}\n{loc_txt}")
                        st.markdown("---")
        else:
            st.warning("⚠️ Veri yok. '🗺️ Haritayı Yeniden Oluştur' butonuna tıklayın.")


# ── Footer ────────────────────────────────────────────────────

st.markdown("---")
st.caption("Emare Katip v1.0 — KINGSTON Disk Veri Toplayıcı & Analizcisi")
