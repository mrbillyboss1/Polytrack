import streamlit as st
import feedparser
import urllib.parse
from groq import Groq

# Configuration de la page
st.set_page_config(page_title="PolyTrack Synthetic Intelligence", layout="wide")

# Récupération de la clé API
try:
    groq_key = st.secrets["GROQ_API_KEY"]
except:
    groq_key = None
    st.error("Clé GROQ_API_KEY manquante dans les Secrets.")

# Fonction de recherche Google News optimisée (Anglais / Monde)
def get_google_news_url(query):
    encoded_query = urllib.parse.quote(query)
    # Paramètres hl=en et gl=US pour capter les sources internationales (Asie/USA/Europe)
    return f"https://news.google.com/rss/search?q={encoded_query}&hl=en&gl=US&ceid=US:en"

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

# Sources ciblées sur le synthétique et l'approvisionnement asiatique
    SOURCES = {
    "Asia Sourcing & Prices": get_google_news_url("recycled polyester rPET price China Vietnam India"),
    "Synthetic Chemical Recycling": get_google_news_url("chemical recycling polyester polyamide textile startup"),
    "T2T Synthetic Innovation": get_google_news_url("textile-to-textile recycling synthetic fiber rNylon rPET"),
    "Standards (Synthetic Focus)": get_google_news_url("\"Textile Exchange\" GRS RCS synthetic recycled fiber")
}
