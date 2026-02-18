# 📈 Financial Data Pipeline: CAC 40 & Macro-Economics Analytics

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?style=for-the-badge&logo=streamlit)
![Pandas](https://img.shields.io/badge/Pandas-ETL_Process-150458?style=for-the-badge&logo=pandas)
![Plotly](https://img.shields.io/badge/Plotly-Interactive_Viz-3F4F75?style=for-the-badge)
![Finance](https://img.shields.io/badge/Finance-Quantitative-008000?style=for-the-badge)

> **Projet Avancé de Data Management**
> **Auteurs :** Rishikaran Karunakaran & Tom Le Corre

---

## 🚀 Vision du Projet & Complexité

Ce projet est une **solution complète d'ingénierie financière** conçue pour répondre à une problématique complexe : **Quantifier et visualiser l'exposition des fleurons du CAC 40 aux chocs macro-économiques mondiaux.**

Contrairement à un simple dashboard de visualisation, ce projet implémente un **Pipeline ETL (Extract, Transform, Load) automatisé** capable de traiter, nettoyer et normaliser plus de **20 ans d'historique boursier** pour synchroniser des données hétérogènes (Actions d'entreprises vs Indices Macro-économiques).

### 🔥 Les Défis Techniques Relevés
1.  **Ingestion Multi-Source & Multithreading :** Extraction simultanée de flux financiers massifs via l'API Yahoo Finance (35 entreprises + 12 indicateurs macro comme le Brent, l'Or, le VIX ou les Taux US).
2.  **Feature Engineering Financier :** Transformation des prix bruts en métriques comparables (Rentabilité Logarithmique, Volatilité Glissante, Rebasage Base 100).
3.  **Mapping Intelligent :** Développement d'une logique algorithmique (`graphes.py`) qui associe dynamiquement chaque entreprise à son facteur d'influence principal.
4.  **Analyse de Données Non-Structurées (NLP) :** Intégration d'un module de **Web Scraping** et de **Text Mining** pour analyser le sentiment de marché via les articles de presse financière en temps réel.

---

## 🛠️ Stack Technique & Algorithmes

Pour assurer la performance et la précision financière, nous avons utilisé les bibliothèques et algorithmes suivants :

### 📚 Bibliothèques Principales
* **Data Engineering :**
    * `pandas` : Manipulation de Séries Temporelles, interpolation (fillna), réindexation et fusion de Dataframes (merge/concat).
    * `numpy` : Calculs vectoriels optimisés (Logarithmes, Écart-types).
* **Finance & API :**
    * `yfinance` : Connecteur API pour récupérer les données OHLCV historiques en multithreading.
* **Visualisation Interactive :**
    * `plotly.graph_objects` : Création de graphiques financiers interactifs (Zoom, Survol, Séries multiples).
    * `matplotlib` / `seaborn` : Utilisés pour les matrices de corrélation statiques et la génération de WordClouds.
* **NLP & Web Scraping :**
    * `beautifulsoup4` : Parsing HTML pour extraire le texte des articles financiers.
    * `requests` : Requêtes HTTP pour récupérer le contenu web.
    * `wordcloud` : Algorithme de génération de nuages de mots basés sur la fréquence.
    * `re` (Regex) : Nettoyage textuel avancé.
* **Frontend :** `streamlit` : Framework pour le déploiement de l'application Web.

### 🧮 Algorithmes & Formules Financières
Le projet intègre plusieurs modèles mathématiques financiers :

1.  **Rentabilité Logarithmique (Log Returns) :**
    Utilisée pour la stationnarité des séries temporelles.
    $$R_t = \ln(\frac{P_t}{P_{t-1}})$$

2.  **Volatilité Glissante (Rolling Volatility) :**
    Mesure du risque dynamique sur une fenêtre de 30 jours (Annualisée).
    $$\sigma_{ann} = \sigma_{30d} \times \sqrt{252}$$

3.  **Rebasage (Base 100) :**
    Normalisation pour comparer visuellement des actifs aux prix hétérogènes.
    $$P_{base} = (\frac{P_t}{P_{initial}}) \times 100$$

---

## 🏗 Architecture & Modules du Code

Le projet est segmenté en 3 modules distincts respectant le principe de séparation des responsabilités.

```mermaid
graph LR
A[Flux API Yahoo Finance] -->|Extract| B(data_management.ipynb)
B -->|Transform| C{Pandas Engine}
C -->|Nettoyage & Calculs| D[Dataframes Enrichis]
D -->|Load| E[Application Streamlit]
F[Web Articles] -->|Scraping| G[Module NLP]
G -->|Processing| E
