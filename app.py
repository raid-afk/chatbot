import streamlit as st
import os
from groq import Groq
import PyPDF2

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Raid RAG - DocuChat", page_icon="📄", layout="wide")

# --- TITRE & STYLE ---
st.title("📄 Docu-Chat : Discutez avec vos PDF")
st.markdown("""
**Technologie RAG (Retrieval-Augmented Generation)**
*Importez un document et posez des questions précises dessus. 
Propulsé par Llama 3 & Groq.*
""")

# --- SIDEBAR : CONFIGURATION ---
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # 1. Gestion Clé API
    # 1. Gestion Clé API (Version corrigée pour le local)
    try:
        # On essaie de récupérer la clé dans les secrets (pour le Cloud)
        api_key = st.secrets["GROQ_API_KEY"]
    except:
        # Si ça plante (parce qu'on est en local), on ne met rien
        api_key = None

    # Si la clé n'est pas trouvée, on affiche le champ de saisie
    if not api_key:
        api_key = st.text_input("Clé API Groq", type="password")
    if not api_key:
        api_key = st.text_input("Clé API Groq", type="password")
    
    # 2. Upload du fichier
    st.header("📂 Votre Document")
    uploaded_file = st.file_uploader("Chargez un PDF", type=("pdf"))

    # Bouton Reset
    if st.button("Effacer la conversation"):
        st.session_state.messages = []
        st.rerun()

# --- FONCTION D'EXTRACTION PDF ---
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# --- LOGIQUE PRINCIPALE ---
if api_key:
    client = Groq(api_key=api_key)

    # Initialisation de l'historique
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # GESTION DU PDF
    pdf_context = ""
    if uploaded_file:
        with st.spinner("Analyse du document en cours..."):
            raw_text = extract_text_from_pdf(uploaded_file)
            # On prépare le contexte pour l'IA
            pdf_context = f"INFORMATION DU DOCUMENT : {raw_text[:25000]} \n\n" 
            st.success(f"Document analysé ! ({len(raw_text)} caractères)")
            
            # Message système invisible pour guider l'IA
            system_prompt = {
                "role": "system", 
                "content": "Tu es un assistant expert. Tu dois répondre aux questions de l'utilisateur EN TE BASANT UNIQUEMENT sur le texte fourni ci-dessus appelé 'INFORMATION DU DOCUMENT'. Si la réponse n'est pas dans le texte, dis-le clairement."
            }

    # AFFICHAGE DES MESSAGES
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # INPUT UTILISATEUR
    if prompt := st.chat_input("Posez votre question sur le document..."):
        # 1. Afficher la question
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # 2. Préparer l'envoi à l'IA
        messages_for_api = []
        
        # Si un PDF est chargé, on injecte le contexte au début
        if pdf_context:
            messages_for_api.append({"role": "system", "content": pdf_context + "Réponds à la question suivante en utilisant le contexte ci-dessus."})
        
        # On ajoute l'historique de conversation
        messages_for_api.extend([
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ])

        # 3. Génération de la réponse
       # 3. Génération de la réponse
        with st.chat_message("assistant"):
            stream = client.chat.completions.create(
                messages=messages_for_api,
                model="llama-3.3-70b-versatile",
                stream=True,
            )
            
            # --- LE FILTRE QUI MANQUAIT ---
            def gen_text():
                for chunk in stream:
                    content = chunk.choices[0].delta.content
                    if content:
                        yield content
            # -----------------------------
        response = st.write_stream(gen_text())
        st.session_state.messages.append({"role": "assistant", "content": response})