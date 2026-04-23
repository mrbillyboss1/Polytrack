import streamlit as st
import feedparser
from groq import Groq

# Configuration de la page
st.set_page_config(page_title="PolyTrack Intelligence", layout="wide")

# Récupération de la clé API
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

# Fonction unique pour traduire ou résumer avec Groq
def ask_groq(prompt, api_key):
    if not api_key:
        return None
    try:
        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content
    except:
        return None

tab1, tab2 = st.tabs(["Flux en direct", "Analyse IA"])

with tab1:
    for name, url in SOURCES.items():
        st.subheader(f"📍 {name}")
        feed = feedparser.parse(url)
        if not feed.entries:
            st.write("Aucune donnée disponible.")
        
        for entry in feed.entries[:3]:
            title = entry.title
            
            # Si le titre contient du chinois, on demande à Groq de traduire
            if any('\u4e00' <= c <= '\u9fff' for c in title) and groq_key:
                translation_prompt = f"Traduis ce titre technique chinois en français : {title}"
                translated = ask_groq(translation_prompt, groq_key)
                title = translated if translated else title
            
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
            
            with st.spinner("Analyse en cours..."):
                summary_prompt = f"Résume ces actualités en 3 points clés pour un acheteur textile : {combined_text}"
                summary = ask_groq(summary_prompt, groq_key)
                if summary:
                    st.info(summary)
                else:
                    st.error("Erreur de génération.")
        else:
            st.error("Configurez votre clé API dans les Secrets.")
