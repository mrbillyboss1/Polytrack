import streamlit as st
import feedparser
from googletrans import Translator
from groq import Groq

# Configuration
st.set_page_config(page_title="PolyTrack Mobile", layout="wide")
translator = Translator()

# Récupération de la clé API sécurisée
groq_key = st.sidebar.text_input("Clé API Groq", type="password")

st.title("📊 PolyTrack Intelligence")
st.caption("Veille Polyester, Polyamide & Recyclage T2T")

# Sources ciblées
SOURCES = {
    "CCF Group (Chine)": "https://www.ccfgroup.com/rss/news.xml",
    "Ecotextile": "https://www.ecotextile.com/rss-feeds.html",
    "Textile Exchange": "https://textileexchange.org/feed/"
}

def get_ai_summary(text, api_key):
    if not api_key:
        return "Veuillez entrer une clé Groq pour le résumé."
    client = Groq(api_key=api_key)
    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": f"Résume en 3 points clés pour un acheteur textile : {text}"}]
    )
    return completion.choices[0].message.content

# Interface
tab1, tab2 = st.tabs(["Flux en direct", "Analyse IA"])

with tab1:
    for name, url in SOURCES.items():
        st.subheader(f"📍 {name}")
        feed = feedparser.parse(url)
        for entry in feed.entries[:3]:
            title = entry.title
            # Traduction automatique si titre en Chinois
            if any('\u4e00' <= c <= '\u9fff' for c in title):
                title = translator.translate(title, dest='fr').text
            
            with st.expander(title):
                st.write(entry.get('summary', 'Pas de résumé.'))
                st.link_button("Source", entry.link)

with tab2:
    if st.button("Générer le résumé stratégique du jour"):
        combined_text = ""
        for url in SOURCES.values():
            f = feedparser.parse(url)
            for e in f.entries[:2]:
                combined_text += e.title + " "
        
        summary = get_ai_summary(combined_text, groq_key)
        st.info(summary)
      
