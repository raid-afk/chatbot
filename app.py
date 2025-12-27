import streamlit as st
import os
from groq import Groq

# 1. Configuration de la page (Titre et Icône)
st.set_page_config(page_title="Raid AI Assistant", page_icon="🤖")

# 2. Titre et description pour le portfolio
st.title("🤖 Assistant IA - Raid Brahmi Portfolio")
st.markdown("""
*Ce projet démontre l'intégration d'un LLM (Llama 3 via Groq) 
dans une interface web Python, conteneurisée avec Docker.*
""")

# 3. Gestion de la clé API (Sécurité)
# On récupère la clé depuis les variables d'environnement ou la barre latérale
api_key = os.environ.get("GROQ_API_KEY")

if not api_key:
    st.sidebar.warning("⚠️ Aucune clé API détectée.")
    api_key = st.sidebar.text_input("Entrez votre clé API Groq (gratuite):", type="password")

# 4. Initialisation du client Groq
if api_key:
    client = Groq(api_key=api_key)

    # 5. Gestion de l'historique de chat (Session State)
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Afficher les anciens messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 6. Zone de saisie utilisateur
    if prompt := st.chat_input("Posez une question à l'IA..."):
        # Afficher le message utilisateur
        with st.chat_message("user"):
            st.markdown(prompt)
        # Sauvegarder dans l'historique
        st.session_state.messages.append({"role": "user", "content": prompt})

        # 7. Génération de la réponse
# 7. Génération de la réponse
        with st.chat_message("assistant"):
            stream = client.chat.completions.create(
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                model="llama-3.3-70b-versatile",
                stream=True,
            )

            # --- CORRECTION ---
            # Fonction pour extraire uniquement le texte du flux de données
            def gen_text():
                for chunk in stream:
                    content = chunk.choices[0].delta.content
                    if content:
                        yield content
            
            # On affiche le flux de texte propre
            response = st.write_stream(gen_text())
            # ------------------
        
        # Sauvegarder la réponse
        st.session_state.messages.append({"role": "assistant", "content": response})