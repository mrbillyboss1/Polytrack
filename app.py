import streamlit as st
import feedparser
import urllib.parse
import requests
from groq import Groq

st.set_page_config(page_title="PolyTrack Synthetic Intelligence", layout="wide")

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
        st.warning(f"Erreur de connexion : {str(e)}")
        return None

def ask_groq(prompt, api_key):
    if not api_key:
        return "Erreur : Clé API manquante."
    try:
        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Tu es un expert acheteur textile spécialisé dans les fibres synthétiques recyclées. "
                        "Tu analyses des actualités et fournis des résumés synthétiques, des tendances marché "
                        "et des recommandations concrètes pour un acheteur professionnel."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Erreur IA : {str(e)}"

# -----------------------------------------------
st.title("📊 PolyTrack : Synthetic & Asian Sourcing")
st.caption("Focus : Recyclage Chimique, rPET, rNylon et Start-up (Asie/USA/Europe)")

SOURCES = {
    "Asia Sourcing & Prices": get_google_news_url("recycled polyester rPET price China Vietnam India"),
    "Synthetic Chemical Recycling": get_google_news_url("chemical recycling polyester polyamide textile startup"),
    "T2T Synthetic Innovation": get_google_news_url("textile-to-textile recycling synthetic fiber rNylon rPET"),
    "Standards (Synthetic Focus)": get_google_news_url('"Textile Exchange" GRS RCS synthetic recycled fiber'),
}

# -----------------------------------------------
# Collecte de tous les articles pour l'analyse globale
all_articles_text = []

for category, url in SOURCES.items():
    st.subheader(f"📰 {category}")
    feed = fetch_feed(url)

    if feed is None or len(feed.entries) == 0:
        st.info("Aucun article trouvé pour cette catégorie.")
        continue

    category_texts = []

    for entry in feed.entries[:5]:
        title = entry.get("title", "Sans titre")
        link = entry.get("link", "#")
        summary = entry.get("summary", "")

        with st.expander(title):
            st.markdown(f"🔗 [Lire l'article]({link})")
            if summary:
                st.markdown(summary, unsafe_allow_html=True)

            # ✅ Bouton analyse IA par article
            btn_key = f"ia_{category}_{title[:30]}"
            if st.button("🤖 Analyser cet article", key=btn_key):
                with st.spinner("Analyse en cours..."):
                    prompt = (
                        f"Voici un article de presse sur le textile synthétique recyclé :\n\n"
                        f"Titre : {title}\n"
                        f"Résumé : {summary}\n\n"
                        f"1. Fais un résumé en 3 points clés.\n"
                        f"2. Quelle est l'implication pour un acheteur textile ?\n"
                        f"3. Y a-t-il une opportunité ou un risque marché ?"
                    )
                    result = ask_groq(prompt, groq_key)
                st.markdown("**🧠 Analyse IA :**")
                st.markdown(result)

        # Accumule pour analyse globale
        category_texts.append(f"- {title} : {summary[:200]}")

    all_articles_text.append(f"\n### {category}\n" + "\n".join(category_texts))

# -----------------------------------------------
# ✅ Bouton analyse globale de toutes les news
st.divider()
st.subheader("🧠 Analyse IA Globale")
st.caption("Synthèse de toutes les actualités du jour par catégorie")

if st.button("🚀 Lancer l'analyse globale", type="primary"):
    if not all_articles_text:
        st.warning("Aucune actualité à analyser.")
    else:
        with st.spinner("Analyse globale en cours..."):
            full_text = "\n".join(all_articles_text)
            prompt = (
                f"Voici un agrégat d'actualités sur le textile synthétique recyclé :\n\n"
                f"{full_text}\n\n"
                f"En tant qu'expert acheteur textile :\n"
                f"1. Quelles sont les 3 tendances majeures du moment ?\n"
                f"2. Quels marchés (Asie, Europe, USA) sont les plus actifs ?\n"
                f"3. Quelles recommandations concrètes pour un acheteur rPET/rNylon ?\n"
                f"4. Y a-t-il des signaux d'alerte ou opportunités à surveiller ?"
            )
            result = ask_groq(prompt, groq_key)
        st.markdown(result)
