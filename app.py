import streamlit as st
import feedparser
import urllib.parse
import requests
from groq import Groq

# Configuration de la page
st.set_page_config(page_title="PolyTrack Synthetic Intelligence", layout="wide")

# Récupération de la clé API
try:
    groq_key = st.secrets["GROQ_API_KEY"]
except:
    groq_key = None
    st.error("Clé GROQ_API_KEY manquante dans les Secrets.")

# ✅ CORRECTIF 403 : headers qui imitent un navigateur réel
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

# ✅ CORRECTIF : fetch manuel avec requests avant de passer à feedparser
def fetch_feed(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        feed = feedparser.parse(response.content)
        return feed
    except requests.exceptions.HTTPError as e:
        st.warning(f"Erreur HTTP {e.response.status_code} pour : {url}")
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
                {"role": "system", "content": "Tu es un expert acheteur textile spécialisé dans les fibres synthétiques recyclées."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Erreur IA : {str(e)}"

st.title("📊 PolyTrack : Synthetic & Asian Sourcing")
st.caption("Focus : Recyclage Chimique, rPET, rNylon et Start-up (Asie/USA/Europe)")

SOURCES = {
    "Asia Sourcing & Prices": get_google_news_url("recycled polyester rPET price China Vietnam India"),
    "Synthetic Chemical Recycling": get_google_news_url("chemical recycling polyester polyamide textile startup"),
    "T2T Synthetic Innovation": get_google_news_url("textile-to-textile recycling synthetic fiber rNylon rPET"),
    "Standards (Synthetic Focus)": get_google_news_url("\"Textile Exchange\" GRS RCS synthetic recycled fiber"),
}

# Affichage des flux
for category, url in SOURCES.items():
    st.subheader(f"📰 {category}")
    feed = fetch_feed(url)

    if feed is None or len(feed.entries) == 0:
        st.info("Aucun article trouvé pour cette catégorie.")
        continue

    for entry in feed.entries[:5]:  # 5 articles max par catégorie
        with st.expander(entry.get("title", "Sans titre")):
            st.markdown(f"🔗 [Lire l'article]({entry.get('link', '#')})")
            summary = entry.get("summary", "")
            if summary:
                st.markdown(summary, unsafe_allow_html=True)
