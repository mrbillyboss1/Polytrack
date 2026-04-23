import streamlit as st
import feedparser
import urllib.parse
from groq import Groq

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="PolyTrack Intelligence", layout="wide", initial_sidebar_state="collapsed")

# --- GESTION DES SECRETS ---
try:
    groq_key = st.secrets["GROQ_API_KEY"]
except:
    groq_key = None
    st.error("Clé GROQ_API_KEY manquante dans les Secrets Streamlit.")

# --- FONCTIONS TECHNIQUES ---
def get_google_news_url(query):
    """Génère une URL de flux RSS Google News basée sur une requête."""
    encoded_query = urllib.parse.quote(query)
    return f"https://news.google.com/rss/search?q={encoded_query}&hl=fr&gl=FR&ceid=FR:fr"

def ask_groq(prompt, api_key):
    """Interroge le modèle Llama 3.3 de Groq."""
    if not api_key:
        return "Erreur : Clé API manquante."
    try:
        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Tu es un expert analyste en achat textile et matières premières plastiques."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Erreur lors de l'analyse : {str(e)}"

# --- INTERFACE UTILISATEUR ---
st.title("📊 PolyTrack Intelligence")
st.markdown("Veille stratégique : **rPET, Polyamide & Recyclage T2T**")

# Définition des sources (Google News + Sources spécialisées)
SOURCES = {
    "Marché rPET & T2T": get_google_news_url("recycled polyester price textile-to-textile industry"),
    "Marché Polyamide": get_google_news_url("polyamide recycling nylon price market"),
    "Textile Exchange": "https://textileexchange.org/feed/",
    "Fibre2Fashion": "https://feeds.feedburner.com/fibre2fashion"
}

# Création des onglets
tab1, tab2 = st.tabs(["📢 Flux d'Actualités", "🧠 Synthèse Stratégique IA"])

with tab1:
    st.info("Les news sont extraites en temps réel de Google News et des revues spécialisées.")
    
    # Création de colonnes pour un affichage plus dense
    cols = st.columns(2)
    
    for i, (name, url) in enumerate(SOURCES.items()):
        target_col = cols[i % 2]
        with target_col:
            st.subheader(f"📍 {name}")
            feed = feedparser.parse(url)
            
            if not feed.entries:
                st.warning(f"Aucune donnée pour {name}.")
                continue
                
            for entry in feed.entries[:4]:
                with st.expander(entry.title):
                    st.caption(f"Source : {entry.get('source', {}).get('title', 'N/A')} | {entry.get('published', '')}")
                    st.write(entry.get('summary', 'Pas de résumé disponible.'))
                    st.link_button("Lire l'article", entry.link)

with tab2:
    st.subheader("Rapport d'aide à la décision")
    if st.button("Lancer l'Analyse IA (Llama 3.3)"):
        if groq_key:
            # On compile les 3 derniers titres de chaque source pour donner du contexte à l'IA
            context_text = ""
            for name, url in SOURCES.items():
                f = feedparser.parse(url)
                for e in f.entries[:3]:
                    context_text += f"- [{name}] {e.title}\n"
            
            with st.spinner("L'IA analyse les tendances du marché..."):
                analysis_prompt = f"""
                Analyse les informations suivantes pour un acheteur textile professionnel :
                
                {context_text}
                
                Fournis un rapport structuré :
                1. **Tendances de prix et tensions** (Polyester, Polyamide).
                2. **Avancées législatives et durabilité** (Focus Recyclage).
                3. **Opportunités de sourcing** identifiées.
                4. **Risques potentiels** pour la supply chain.
                
                Réponds en Anglais de manière concise et professionnelle.
                """
                report = ask_groq(analysis_prompt, groq_key)
                st.markdown("---")
                st.markdown(report)
        else:
            st.error("Veuillez configurer la clé GROQ_API_KEY dans les Secrets de l'application.")

# --- FOOTER ---
st.divider()
st.caption("PolyTrack v2.1 | Données basées sur Google News RSS et Textile Exchange.")
