import streamlit as st
import feedparser
import urllib.parse
import requests
from datetime import datetime
from groq import Groq
from email.utils import parsedate_to_datetime

st.set_page_config(
    page_title="PolyTrack Synthetic Intelligence",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------
# 🎨 CSS Glassmorphism
# -----------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

/* Base */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: #e8eaf0;
}

.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #0d1528 40%, #0a1a2e 70%, #0e1020 100%);
    min-height: 100vh;
}

/* Supprime fond blanc Streamlit */
.block-container {
    padding-top: 2rem;
    max-width: 1200px;
}

/* Titre principal */
h1 {
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
    font-size: 2.4rem !important;
    background: linear-gradient(90deg, #60a5fa, #a78bfa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.5px;
}

/* Sous-titres catégories */
h2, h3 {
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    color: #93c5fd !important;
    font-size: 1.1rem !important;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    margin-top: 2rem !important;
}

/* Cards glass pour les articles */
.glass-card {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 0.8rem;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    transition: all 0.25s ease;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3);
}

.glass-card:hover {
    background: rgba(255, 255, 255, 0.07);
    border-color: rgba(96, 165, 250, 0.3);
    box-shadow: 0 8px 32px rgba(96, 165, 250, 0.1);
    transform: translateY(-1px);
}

/* Titre article */
.article-title {
    font-family: 'Syne', sans-serif;
    font-weight: 600;
    font-size: 0.95rem;
    color: #e2e8f0;
    margin-bottom: 0.4rem;
    line-height: 1.4;
}

/* Meta infos (source + heure) */
.article-meta {
    display: flex;
    gap: 1rem;
    align-items: center;
    margin-bottom: 0.6rem;
    flex-wrap: wrap;
}

.meta-source {
    background: rgba(96, 165, 250, 0.15);
    border: 1px solid rgba(96, 165, 250, 0.25);
    color: #60a5fa;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.3px;
}

.meta-time {
    color: #64748b;
    font-size: 0.72rem;
    display: flex;
    align-items: center;
    gap: 4px;
}

/* Lien article */
.article-link {
    color: #34d399 !important;
    font-size: 0.78rem;
    text-decoration: none;
    font-weight: 500;
    letter-spacing: 0.3px;
}

/* Résumé article */
.article-summary {
    color: #94a3b8;
    font-size: 0.82rem;
    line-height: 1.6;
    margin-top: 0.5rem;
    border-top: 1px solid rgba(255,255,255,0.05);
    padding-top: 0.5rem;
}

/* Analyse IA */
.ia-block {
    background: rgba(167, 139, 250, 0.06);
    border: 1px solid rgba(167, 139, 250, 0.2);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin-top: 0.8rem;
}

.ia-section-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
    margin-top: 0.8rem;
}

.ia-key { color: #60a5fa; }
.ia-action { color: #34d399; }
.ia-number { color: #f59e0b; }

/* Divider */
hr {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.07);
    margin: 2rem 0;
}

/* Boutons Streamlit */
.stButton > button {
    background: rgba(96, 165, 250, 0.1) !important;
    border: 1px solid rgba(96, 165, 250, 0.3) !important;
    color: #93c5fd !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    padding: 0.4rem 1rem !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    background: rgba(96, 165, 250, 0.2) !important;
    border-color: rgba(96, 165, 250, 0.6) !important;
    transform: translateY(-1px) !important;
}

/* Bouton primaire */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, rgba(96,165,250,0.25), rgba(167,139,250,0.25)) !important;
    border: 1px solid rgba(167, 139, 250, 0.4) !important;
    color: #e0e7ff !important;
    font-size: 0.9rem !important;
    padding: 0.6rem 1.8rem !important;
}

/* Spinner */
.stSpinner > div {
    border-color: #60a5fa !important;
}

/* Caption */
.stCaption, [data-testid="stCaptionContainer"] {
    color: #475569 !important;
    font-size: 0.8rem !important;
}

/* Cacher éléments Streamlit inutiles */
#MainMenu, footer, header { visibility: hidden; }

/* Analyse globale box */
.global-ia-box {
    background: rgba(52, 211, 153, 0.05);
    border: 1px solid rgba(52, 211, 153, 0.2);
    border-radius: 16px;
    padding: 1.5rem 2rem;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------
# Config
# -----------------------------------------------
try:
    groq_key = st.secrets["GROQ_API_KEY"]
except:
    groq_key = None
    st.error("Clé GROQ_API_KEY manquante dans les Secrets.")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://news.google.com/",
}

def get_google_news_url(query):
    encoded_query = urllib.parse.quote(query)
    return f"https://news.google.com/rss/search?q={encoded_query}&hl=en&gl=US&ceid=US:en"

def fetch_feed(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return feedparser.parse(response.content)
    except requests.exceptions.HTTPError as e:
        st.warning(f"Erreur HTTP {e.response.status_code}")
        return None
    except Exception as e:
        st.warning(f"Erreur : {str(e)}")
        return None

def extract_source(entry):
    """Extrait le nom de la source depuis le flux RSS."""
    if hasattr(entry, 'source') and hasattr(entry.source, 'title'):
        return entry.source.title
    if hasattr(entry, 'tags') and entry.tags:
        return entry.tags[0].get('term', '')
    # Extrait depuis l'URL
    link = entry.get('link', '')
    try:
        from urllib.parse import urlparse
        domain = urlparse(link).netloc
        return domain.replace('www.', '').split('.')[0].capitalize()
    except:
        return "Source inconnue"

def format_date(entry):
    """Formate la date de publication."""
    for field in ['published', 'updated', 'created']:
        raw = entry.get(field, '')
        if raw:
            try:
                dt = parsedate_to_datetime(raw)
                now = datetime.now(dt.tzinfo)
                delta = now - dt
                hours = int(delta.total_seconds() // 3600)
                if hours < 1:
                    mins = int(delta.total_seconds() // 60)
                    return f"il y a {mins}min"
                elif hours < 24:
                    return f"il y a {hours}h"
                else:
                    return dt.strftime("%d %b %Y")
            except:
                return raw[:16]
    return ""

def ask_groq(prompt, api_key):
    if not api_key:
        return None
    try:
        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Tu es un expert acheteur textile spécialisé dans les fibres synthétiques recyclées. "
                        "Réponds TOUJOURS en français. Sois concis, factuel et orienté décision."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Erreur IA : {str(e)}"

def parse_ia_response(text):
    """Affiche la réponse IA avec les sections colorées."""
    sections = {
        "messages_clés": ("💬 Messages clés", "ia-key"),
        "actions": ("⚡ Actions concrètes", "ia-action"),
        "chiffres": ("📊 Chiffres & données", "ia-number"),
    }
    # Affichage brut mais stylé si pas de parsing possible
    st.markdown(f'<div class="ia-block">{text}</div>', unsafe_allow_html=True)

# -----------------------------------------------
# Header
# -----------------------------------------------
st.markdown("<h1>📊 PolyTrack — Synthetic Intelligence</h1>", unsafe_allow_html=True)
st.caption("Focus : rPET · rNylon · Recyclage Chimique · Sourcing Asie/USA/Europe")

SOURCES = {
    "🌏 Asia Sourcing & Prices": get_google_news_url("recycled polyester rPET price China Vietnam India"),
    "⚗️ Chemical Recycling": get_google_news_url("chemical recycling polyester polyamide textile startup"),
    "🔄 T2T Synthetic Innovation": get_google_news_url("textile-to-textile recycling synthetic fiber rNylon rPET"),
    "📋 Standards & Certifications": get_google_news_url('"Textile Exchange" GRS RCS synthetic recycled fiber'),
}

all_articles_text = []

# -----------------------------------------------
# Flux RSS
# -----------------------------------------------
for category, url in SOURCES.items():
    st.markdown(f"### {category}")
    feed = fetch_feed(url)

    if feed is None or len(feed.entries) == 0:
        st.info("Aucun article trouvé.")
        continue

    category_texts = []

    for i, entry in enumerate(feed.entries[:5]):
        title = entry.get("title", "Sans titre")
        link = entry.get("link", "#")
        summary = entry.get("summary", "")
        source = extract_source(entry)
        pub_date = format_date(entry)

        # Nettoyage summary HTML basique
        import re
        clean_summary = re.sub(r'<[^>]+>', '', summary)[:300]

        card_html = f"""
        <div class="glass-card">
            <div class="article-title">{title}</div>
            <div class="article-meta">
                <span class="meta-source">🏢 {source}</span>
                <span class="meta-time">🕐 {pub_date}</span>
            </div>
            <a href="{link}" target="_blank" class="article-link">↗ Lire l'article complet</a>
            {"<div class='article-summary'>" + clean_summary + "…</div>" if clean_summary else ""}
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)

        # Bouton analyse IA par article
        btn_key = f"ia_{category}_{i}"
        if st.button("🤖 Analyser", key=btn_key):
            with st.spinner("Analyse en cours..."):
                prompt = f"""Analyse cet article sur le textile synthétique recyclé :

Titre : {title}
Résumé : {clean_summary}

Réponds UNIQUEMENT avec ce format exact :

💬 MESSAGES CLÉS
• [message 1]
• [message 2]
• [message 3]

⚡ ACTIONS CONCRÈTES
• [action 1 pour un acheteur textile]
• [action 2]

📊 CHIFFRES & DONNÉES
• [chiffre ou donnée clé mentionnée, ou "Aucun chiffre disponible"]
"""
                result = ask_groq(prompt, groq_key)
            if result:
                st.markdown(f'<div class="ia-block"><pre style="font-family:DM Sans,sans-serif;white-space:pre-wrap;font-size:0.85rem;color:#cbd5e1;">{result}</pre></div>', unsafe_allow_html=True)

        category_texts.append(f"- {title} : {clean_summary[:200]}")

    all_articles_text.append(f"\n### {category}\n" + "\n".join(category_texts))

# -----------------------------------------------
# Analyse Globale
# -----------------------------------------------
st.markdown("---")
st.markdown("### 🧠 Analyse IA Globale")
st.caption("Synthèse de toutes les actualités collectées")

if st.button("🚀 Lancer l'analyse globale", type="primary"):
    if not all_articles_text:
        st.warning("Aucune actualité à analyser.")
    else:
        with st.spinner("Analyse macro en cours..."):
            full_text = "\n".join(all_articles_text)
            prompt = f"""Voici un agrégat d'actualités sur le textile synthétique recyclé :

{full_text}

Réponds UNIQUEMENT avec ce format :

💬 MESSAGES CLÉS DU MARCHÉ
• [tendance 1]
• [tendance 2]
• [tendance 3]

⚡ ACTIONS CONCRÈTES POUR UN ACHETEUR rPET/rNylon
• [action 1]
• [action 2]
• [action 3]

📊 CHIFFRES & SIGNAUX À RETENIR
• [chiffre ou signal 1]
• [chiffre ou signal 2]

🌍 MARCHÉS LES PLUS ACTIFS
• [marché 1 : raison]
• [marché 2 : raison]
"""
            result = ask_groq(prompt, groq_key)
        if result:
            st.markdown(f'<div class="global-ia-box"><pre style="font-family:DM Sans,sans-serif;white-space:pre-wrap;font-size:0.88rem;color:#e2e8f0;line-height:1.7;">{result}</pre></div>', unsafe_allow_html=True)
