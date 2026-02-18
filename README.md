# 📈 Financial Data Pipeline: CAC 40 & Macro-Economics Analytics

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?style=for-the-badge&logo=streamlit)
![Pandas](https://img.shields.io/badge/Pandas-ETL_Process-150458?style=for-the-badge&logo=pandas)
![Plotly](https://img.shields.io/badge/Plotly-Interactive_Viz-3F4F75?style=for-the-badge)
![Finance](https://img.shields.io/badge/Finance-Quantitative-008000?style=for-the-badge)

> **Projet Avancé de Data Management**


---

## 🚀 Vision du Projet & Complexité

Ce projet est une **solution complète d'ingénierie financière** conçue pour répondre à une problématique complexe : **Quantifier et visualiser l'exposition des fleurons du CAC 40 aux chocs macro-économiques mondiaux.**

Contrairement à un simple dashboard de visualisation, ce projet implémente un **Pipeline ETL (Extract, Transform, Load) automatisé** capable de traiter, nettoyer et normaliser plus de **20 ans d'historique boursier** pour synchroniser des données hétérogènes (Actions d'entreprises vs Indices Macro-économiques).

### 🔥 Les Défis Techniques Relevés
1.  **Ingestion Multi-Source & Multithreading :** Extraction simultanée de flux financiers massifs via l'API Yahoo Finance (35 entreprises + 12 indicateurs macro comme le Brent, l'Or, le VIX ou les Taux US).
2.  **Feature Engineering Financier :** Transformation des prix bruts en métriques comparables :
    * *Rentabilité Logarithmique* pour la stationnarité.
    * *Volatilité Glissante (Rolling Volatility)* pour l'analyse dynamique du risque.
    * *Rebasage (Base 100)* pour la comparaison visuelle d'actifs aux valorisations disparates.
3.  **Mapping Intelligent :** Développement d'une logique algorithmique (`graphes.py`) qui associe dynamiquement chaque entreprise à son facteur d'influence principal (ex: *TotalEnergies* ↔ *Pétrole*, *LVMH* ↔ *Taux de Change*).
4.  **Analyse de Données Non-Structurées (NLP) :** Intégration d'un module de **Web Scraping** et de **Text Mining** pour analyser le sentiment de marché via les articles de presse financière en temps réel.

---

## 🏗 Architecture & Explication des Modules

Le code est structuré de manière modulaire pour séparer la logique de traitement (Backend) de l'interface (Frontend). Voici le rôle précis de chaque fichier du dépôt :

### 📂 1. Le Moteur ETL : `data_management.ipynb` (ou `projet data`)
**C'est l'usine de données.** Ce script n'est exécuté qu'une seule fois pour construire la base de données locale.
* **Connexion API :** Utilise `yfinance` en mode multithread pour télécharger l'historique OHLCV.
* **Nettoyage (Cleaning) :** Gère les valeurs manquantes (fill NaN) et aligne les dates (les bourses n'ont pas les mêmes jours fériés).
* **Calculs :** Génère les colonnes dérivées (`Daily_Return`, `Volatilité_30j`).
* **Sortie :** Produit les fichiers CSV optimisés qui seront lus par le dashboard.

### 📂 2. La Logique Métier : `graphes.py`
**C'est le cerveau analytique.** Ce fichier agit comme une librairie interne pour garder le code principal propre.
* **Dictionnaire de Mapping :** Contient les règles métiers (ex: Lier `BNP Paribas` aux `Taux d'intérêts`).
* **Fonctions de Plotting :** Contient le code `Plotly` complexe pour générer :
    * La Frontière Efficiente de Markowitz.
    * Les graphiques de Corrélation Glissante (Rolling Correlation).
    * Les régressions linéaires (Beta).

### 📂 3. L'Interface Utilisateur : `app.py`
**C'est la tour de contrôle.** C'est le fichier exécuté par Streamlit.
* **Orchestration :** Charge les données, affiche la barre latérale et appelle les fonctions de `graphes.py` selon les choix de l'utilisateur.
* **Module NLP :** Contient la logique de scraping (`Requests` + `BeautifulSoup`) et de génération de Nuage de Mots (`WordCloud`) à partir d'une URL fournie par l'utilisateur.

### 📂 4. Gestion des Dépendances : `requirements.txt`
Liste toutes les bibliothèques nécessaires (`pandas`, `numpy`, `yfinance`, `plotly`, `streamlit`, etc.) pour assurer la reproductibilité de l'environnement sur n'importe quelle machine.

---

## 🛠️ Stack Technique & Algorithmes (SEO)

Pour assurer la performance et la précision financière, nous avons utilisé les bibliothèques et algorithmes suivants :

### 📚 Bibliothèques Principales
* **Data Engineering :** `pandas` (Manipulation de Séries Temporelles), `numpy` (Calculs vectoriels).
* **Finance API :** `yfinance` (Récupération de données de marché).
* **Visualisation :** `plotly.graph_objects` (Graphiques financiers interactifs), `matplotlib` (Rendu statique).
* **NLP & Scraping :** `beautifulsoup4` (Parsing HTML), `requests` (HTTP), `wordcloud` (Analyse de fréquence).
* **Frontend :** `streamlit` (Framework Web).

### 🧮 Algorithmes & Formules
1.  **Rentabilité Logarithmique (Log Returns) :** $R_t = \ln(\frac{P_t}{P_{t-1}})$
2.  **Volatilité Glissante (Rolling Volatility) :** $\sigma_{ann} = \sigma_{30d} \times \sqrt{252}$
3.  **Rebasage (Base 100) :** $P_{base} = (\frac{P_t}{P_{initial}}) \times 100$

---

## 💻 Installation & Démarrage

Clonez ce dépôt et lancez l'analyse en 3 commandes :

1.  **Installation des dépendances :**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Exécution du Pipeline ETL (Mise à jour des données) :**
    *Lancez ce script pour récupérer les dernières données de marché.*
    ```bash
    python "projet data"
    ```

3.  **Lancement du Dashboard :**
    ```bash
    streamlit run app.py
    ```

---
*Projet universitaire réalisé dans le cadre du Master Data Analytics.*
