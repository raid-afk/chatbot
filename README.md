# Assistant documentaire PDF

Application Streamlit pour poser des questions en français sur un PDF. PyPDF2 extrait le texte et l’application transmet jusqu’à 30 000 caractères à Groq avec la conversation. Utiliser un document que vous pouvez partager avec ce service. Les PDF composés uniquement d’images nécessitent une reconnaissance de caractères préalable.

## Démarrage

```sh
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Saisir une clé Groq dans la barre latérale ou définir la variable d’environnement `GROQ_API_KEY` avant le lancement. La configuration existante via les secrets Streamlit est aussi prise en charge. Garder la clé hors du dépôt.

## Essai

Exporter en PDF un court texte indiquant par exemple « La livraison est prévue vendredi ». Charger le document et demander « Quel jour la livraison est-elle prévue ? ». Vérifier la réponse dans le document d’origine.
