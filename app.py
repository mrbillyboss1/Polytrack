import streamlit as st
import feedparser
from googletrans import Translator
from groq import Groq

# Configuration de la page
st.set_page_config(page_title="PolyTrack Intelligence", layout="wide")
translator = Translator()

# Récupération de la clé API depuis les Secrets de Streamlit
# Si la clé n'est pas configurée, l'app affichera un avertissement
try:
    groq_key = st.secrets["GROQ_API_KEY"]
except:
    groq_key = None
    st.warning("⚠️ Clé API Groq manquante dans les Secrets.")

st.title("📊 PolyTrack Intelligence")
st.caption("Veille Polyester, Polyamide & Recyclage T2T")

SOURCES = {
    "CCF Group (Chine)": "https://www.ccfgroup.com/rss/news.xml",
    "Ecotextile": "https://www.ecotextile.com/rss-feeds.html",
    "Textile Exchange": "https://textileexchange.org/feed/"
}

def get_ai_summary(text, api_key):
    if not api_key:
        return "Impossible de générer le résumé : clé API absente."
    try:
        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": f"Résume en 3 points clés pour un acheteur textile : {text}"}]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Erreur lors du résumé : {str(e)}"

tab1, tab2 = st.tabs(["Flux en direct", "Analyse IA"])

with tab1:
    for name, url in SOURCES.items():
        st.subheader(f"📍 {name}")
        feed = feedparser.parse(url)
        if not feed.entries:
            st.write("Aucune donnée disponible pour le moment.")
        for entry in feed.entries[:3]:
            title = entry.title
            if any('\u4e00' <= c <= '\u9fff' for c in title):
                try:
                    title = translator.translate(title, dest='fr').text
                except:
                    pass
            
            with st.expander(title):
                st.write(entry.get('summary', 'Pas de résumé.'))
                st.link_button("Lire l'article", entry.link)

with tab2:
    if st.button("Générer le résumé stratégique"):
        if groq_key:
            combined_text = ""
            for url in SOURCES.values():
                f = feedparser.parse(url)
                for e in f.entries[:2]:
                    combined_text += e.title + " "
            
            with st.spinner("Analyse par l'IA en cours..."):
                summary = get_ai_summary(combined_text, groq_key)
                st.info(summary)
        else:
            st.error("Veuillez configurer la clé GROQ_API_KEY dans les Secrets.")
            
