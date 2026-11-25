import os

import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError
from groq import Groq
import PyPDF2

# --- 1. CONFIGURATION PAGE ---
st.set_page_config(
    page_title="Assistant AI Pro",
    page_icon="📄",
    layout="wide"
)

# --- 2. STYLE CSS (Clean & Minimaliste) ---
st.markdown("""
<style>
    /* Fond blanc et texte sombre */
    .stApp {
        background-color: #FFFFFF;
        color: #111827;
    }
    
    /* Sidebar discrète */
    section[data-testid="stSidebar"] {
        background-color: #F9FAFB;
        border-right: 1px solid #E5E7EB;
    }
    
    /* Inputs propres */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stChatInput textarea {
        background-color: #FFFFFF !important;
        border: 1px solid #D1D5DB !important;
        border-radius: 8px !important;
        color: #111827 !important;
    }
    
    /* Boutons bleus */
    .stButton button {
        background-color: #2563EB !important;
        color: white !important;
        border-radius: 6px !important;
        border: none !important;
    }
    
    /* Cacher menu hamburger */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 3. FONCTIONS ---

# Lecture PDF
def extract_text_from_pdf(pdf_file):
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        return ""

# Générateur pour nettoyer le flux (Fixe le problème d'affichage JSON)
def generate_chat_responses(chat_completion):
    """Extrait uniquement le texte du flux de réponse."""
    for chunk in chat_completion:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

# --- 4. INTERFACE ---
st.title("Assistant Documentaire")
st.caption("Interface simplifiée v2.1 • Lecture PDF active")
st.markdown("---")

# BARRE LATÉRALE
with st.sidebar:
    st.header("Réglages")
    
    # Clé API
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets.get("GROQ_API_KEY")
        except StreamlitSecretNotFoundError:
            api_key = None
    if not api_key:
        api_key = st.text_input("Clé API Groq", type="password", placeholder="gsk_...")
    else:
        st.success("✅ Système Connecté")

    st.markdown("### Modèle IA")
    
    # CORRECTION CRITIQUE 1 : Dictionnaire de mapping
    # À gauche : Ce qu'on voit. À droite : L'ID technique pour l'API.
    models_map = {
        "Mode Puissant ": "llama-3.3-70b-versatile",
        "Mode Rapide ": "llama3-8b-8192",
        "Mode Équilibré ": "mixtral-8x7b-32768"
    }
    
    # On laisse l'utilisateur choisir la "Clé" (le texte lisible)
    selected_label = st.selectbox("Moteur", list(models_map.keys()), label_visibility="collapsed")
    # On récupère la "Valeur" (l'ID technique) grâce à la clé
    selected_model_id = models_map[selected_label]

    st.markdown("### Document")
    uploaded_file = st.file_uploader("Charger un PDF", type="pdf")
    
    st.markdown("---")
    if st.button("Nouvelle conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- 5. LOGIQUE CHAT ---
if api_key:
    client = Groq(api_key=api_key)

    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({"role": "assistant", "content": "Bonjour. Je suis prêt à analyser vos documents."})

    # Gestion Contexte
    pdf_context = ""
    if uploaded_file:
        raw_text = extract_text_from_pdf(uploaded_file)
        if raw_text:
            pdf_context = f"CONTEXTE PDF : {raw_text[:30000]} \n\n"
            st.toast("Document analysé avec succès.", icon="📎")

    # Afficher historique
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input Utilisateur
    if prompt := st.chat_input("Votre question..."):
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Préparation Prompt
        messages_api = []
        system_instruction = "Tu es un assistant professionnel. Réponds en français de manière claire et structurée."
        
        if pdf_context:
            system_instruction += " Utilise les informations du PDF fourni pour répondre."
            messages_api.append({"role": "system", "content": pdf_context})
        
        messages_api.append({"role": "system", "content": system_instruction})
        
        for m in st.session_state.messages:
            if m["role"] != "system":
                messages_api.append(m)

        # Génération Réponse
        with st.chat_message("assistant"):
            try:
                stream = client.chat.completions.create(
                    messages=messages_api,
                    model=selected_model_id, # Utilisation de l'ID correct
                    stream=True,
                    temperature=0.5
                )
                # CORRECTION CRITIQUE 2 : On passe par le générateur de nettoyage
                response = st.write_stream(generate_chat_responses(stream))
                
                # Sauvegarde en session
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                st.error(f"Erreur API : {e}")

else:
    st.info("Veuillez entrer une clé API valide dans la barre latérale.")