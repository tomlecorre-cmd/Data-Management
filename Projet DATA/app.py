import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import re
import requests
from bs4 import BeautifulSoup

from graphes import (
    df_actions,
    df_macros,
    MACRO_MAPPING,
    ENTERPRISE_LABELS,
    plot_action_vs_macro,
    plot_rolling_corr,
    plot_volatilite_30j,
    plot_risque_rendement,
    plot_scatter_action_vs_macro,
)

# -----------------------------
# CONFIG DE LA PAGE
# -----------------------------
st.set_page_config(
    page_title="Projet Data Management - CAC 40 & Macro",
    layout="wide"
)

st.title("Projet Data Management – CAC 40 et facteurs macroéconomiques")

st.markdown(
    """
    Cette application Streamlit illustre notre analyse des actions du CAC 40 
    et de leurs principaux facteurs macroéconomiques (matières premières, taux, change, etc.).

    Utilise le menu à gauche pour naviguer entre :
    - la **présentation du jeu de données**,
    - les **graphiques interactifs**,
    - la partie **text mining** (article & nuage de mots).
    """
)

# -----------------------------
# SIDEBAR : navigation
# -----------------------------
st.sidebar.header("Navigation")

page = st.sidebar.selectbox(
    "Choisis une page :",
    ["Présentation des données", "Graphiques", "Text Mining"]
)

# Préparation des listes pour les graphes (page “Graphiques”)
TICKERS_DISPONIBLES = sorted(MACRO_MAPPING.keys())

ENTREPRISES_OPTIONS = [
    f"{ENTERPRISE_LABELS.get(t, t)} ({t})" for t in TICKERS_DISPONIBLES
]

OPTION_TO_TICKER = {
    label: ticker for label, ticker in zip(ENTREPRISES_OPTIONS, TICKERS_DISPONIBLES)
}


# =========================
# PAGE 1 : Présentation des données
# =========================
if page == "Présentation des données":
    st.subheader("1. Présentation du jeu de données")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Données Actions (CAC 40)")
        st.write(f"- Nombre de lignes : **{len(df_actions):,}**")
        st.write(f"- Nombre de colonnes : **{df_actions.shape[1]}**")
        st.write("Aperçu des premières lignes :")
        st.dataframe(df_actions.head())

        st.markdown("**Variables principales (actions) :**")
        st.markdown(
            """
            - `Date` : date de cotation  
            - `Ticker` : code de l’entreprise (ex : TTE.PA, MC.PA, BNP.PA…)  
            - `Open`, `High`, `Low`, `Close` : prix d’ouverture, plus haut, plus bas, clôture  
            - `Adj Close` : prix de clôture ajusté  
            - `Volume` : volume échangé  
            - `Rentabilite` : variation quotidienne du prix de clôture (en %)  
            - `Volatilite_30j` : écart-type des rentabilités sur une fenêtre glissante de 30 jours  
            """
        )

    with col2:
        st.markdown("#### Données Facteurs Macro")
        st.write(f"- Nombre de lignes : **{len(df_macros):,}**")
        st.write(f"- Nombre de colonnes : **{df_macros.shape[1]}**")
        st.write("Aperçu des premières lignes :")
        st.dataframe(df_macros.head())

        st.markdown("**Exemples de facteurs macro :**")
        st.markdown(
            """
            - `BZ=F` : prix du pétrole Brent  
            - `NG=F` : prix du gaz naturel  
            - `HG=F` : prix du cuivre  
            - `EURUSD=X` : taux de change euro / dollar  
            - `^TNX` : taux obligataire US à 10 ans  
            - `^NDX` : indice Nasdaq 100  
            """
        )

    st.markdown("---")
    st.markdown("#### Statistiques descriptives (rentabilité)")

    # Statistiques descriptives sur la rentabilité par entreprise
    df_stats = (
        df_actions[["Ticker", "Rentabilite"]]
        .groupby("Ticker")["Rentabilite"]
        .agg(Rendement_moyen="mean", Risque="std")
        .reset_index()
    )

    # Ajout du nom lisible de l'entreprise
    df_stats["Nom_entreprise"] = df_stats["Ticker"].apply(
        lambda t: ENTERPRISE_LABELS.get(t, t)
    )

    # Réorganisation des colonnes
    df_stats = df_stats[["Ticker", "Nom_entreprise", "Rendement_moyen", "Risque"]]

    st.write(
        "Pour chaque entreprise pour laquelle nous avons des rentabilités calculées, "
        "on calcule le **rendement moyen quotidien** et la **volatilité** "
        "(écart-type des rentabilités)."
    )

    st.dataframe(df_stats)


# =========================
# PAGE 2 : Graphiques
# =========================
elif page == "Graphiques":
    st.subheader("2. Graphiques interactifs")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Paramètres des graphiques")

    type_graphe = st.sidebar.selectbox(
        "Choisir le type de graphique :",
        [
            "Graphe 1 – Action vs facteur macro (base 100)",
            "Graphe 2 – Corrélation glissante Action / Macro",
            "Graphe 3 – Volatilité glissante (30 jours)",
            "Graphe 4 – Carte Risque / Rendement (CAC40)",
            "Graphe 5 – Sensibilité Action / Macro (régression)",
        ]
    )

    entreprise_option = st.sidebar.selectbox(
        "Choisir une entreprise :",
        ENTREPRISES_OPTIONS,
    )
    ticker_choisi = OPTION_TO_TICKER[entreprise_option]

    window_corr = st.sidebar.slider(
        "Fenêtre de corrélation (jours) pour le Graphe 2 :",
        min_value=20,
        max_value=180,
        value=60,
        step=10,
    )

    start_date = st.sidebar.date_input(
        "Date de début (pour la volatilité et le risque/rendement) :",
        value=df_actions["Date"].min().date()
    )
    end_date = st.sidebar.date_input(
        "Date de fin :",
        value=df_actions["Date"].max().date()
    )

    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    st.markdown(f"**Entreprise sélectionnée :** {entreprise_option}")

    st.markdown("---")
    st.markdown("### Visualisation")

    if type_graphe.startswith("Graphe 1"):
        st.markdown(
            "#### Graphe 1 – Évolution comparée de l’action et de son facteur macro\n"
            "Les deux séries sont normalisées en base 100 pour comparer leurs dynamiques sur la période."
        )
        fig = plot_action_vs_macro(df_actions, df_macros, ticker_choisi)
        st.plotly_chart(fig, use_container_width=True)

    elif type_graphe.startswith("Graphe 2"):
        st.markdown(
            f"#### Graphe 2 – Corrélation glissante ({window_corr} jours)\n"
            "On mesure comment la corrélation entre la rentabilité de l’action et celle du facteur macro "
            "évolue dans le temps."
        )
        fig = plot_rolling_corr(df_actions, df_macros, ticker_choisi, window=window_corr)
        st.plotly_chart(fig, use_container_width=True)

    elif type_graphe.startswith("Graphe 3"):
        st.markdown(
            "#### Graphe 3 – Volatilité glissante (30 jours)\n"
            "On suit l’évolution du risque (instabilité des rendements) de l’action dans le temps."
        )
        fig = plot_volatilite_30j(
            df_actions,
            [ticker_choisi],
            start_date=start_date_str,
            end_date=end_date_str
        )
        st.plotly_chart(fig, use_container_width=True)

    elif type_graphe.startswith("Graphe 4"):
        st.markdown(
            "#### Graphe 4 – Carte Risque / Rendement\n"
            "Chaque point représente une entreprise du CAC 40 avec :\n"
            "- en abscisse : la volatilité de la rentabilité (le risque)\n"
            "- en ordonnée : la rentabilité moyenne sur la période"
        )
        fig = plot_risque_rendement(
            df_actions,
            start_date=start_date_str,
            end_date=end_date_str
        )
        st.plotly_chart(fig, use_container_width=True)

    elif type_graphe.startswith("Graphe 5"):
        st.markdown(
            "#### Graphe 5 – Sensibilité de l’action à son facteur macro\n"
            "On trace la rentabilité de l’action en fonction de la rentabilité du facteur macro, "
            "et on ajuste une droite de régression pour obtenir un **beta macro** et un **R²**."
        )
        fig = plot_scatter_action_vs_macro(df_actions, df_macros, ticker_choisi)
        st.plotly_chart(fig, use_container_width=True)



# =========================
# PAGE 3 : Text Mining (Version Scraping)
# =========================
elif page == "Text Mining":
    st.subheader("3. Text Mining : Analyse d'un article via URL")

    st.markdown("""
    **Objectif :** Récupérer automatiquement le texte d'un article web et générer un nuage de mots.
    """)

    url_par_defaut = "https://www.capital.fr/entreprises-marches/bourse-ou-va-le-cac-40-lavenir-de-la-france-peut-etre-pas-aussi-noir-que-redoute-1507766"

    st.info("💡 Par défaut, l'application analyse une page pédagogique sur le fonctionnement du CAC 40.")
    url_article = st.text_input("Colle l'URL de l'article ici :", value=url_par_defaut)

    if st.button("Scraper & Générer le Nuage de Mots"):
        if url_article:
            with st.spinner('Récupération de l\'article en cours'):
                try:
                    
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                    }
                    response = requests.get(url_article, headers=headers)
                    
                    if response.status_code == 200:
                        
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        paragraphes = soup.find_all('p')
                        texte_complet = " ".join([p.get_text() for p in paragraphes])
                        
                        st.success("Article récupéré avec succès")
                        
                        with st.expander("Voir le texte brut extrait"):
                            st.write(texte_complet[:500] + " [...]")

                        text_clean = texte_complet.lower()
                        text_clean = re.sub(r'[^a-zàâçéèêëîïôûùüÿñæoe\s]', '', text_clean)
                        
                        stopwords_fr = set([
                            "le", "la", "les", "de", "du", "des", "un", "une", "et", "est", "sont", "en", "au", "aux",
                            "pour", "par", "sur", "dans", "avec", "il", "elle", "ils", "elles", "ce", "cet", "cette",
                            "ces", "qui", "que", "quoi", "dont", "ou", "où", "mais", "donc", "or", "ni", "car", "pas",
                            "ne", "se", "sa", "ses", "son", "leur", "leurs", "plus", "moins", "très", "aussi", "être",
                            "avoir", "tout", "tous", "toute", "toutes", "fait", "faire", "comme", "c'est", "a", "y",
                            "été", "ont", "sous", "vers", "ici", "nous", "vous", "notre", "votre"
                        ])

                        wc = WordCloud(
                            background_color="white",
                            max_words=50,
                            stopwords=stopwords_fr,
                            width=800,
                            height=400,
                            colormap="viridis"
                        ).generate(text_clean)

                        st.markdown("### Thèmes principaux de la page web")
                        fig, ax = plt.subplots(figsize=(10, 5))
                        ax.imshow(wc, interpolation='bilinear')
                        ax.axis("off")
                        st.pyplot(fig)

                    else:
                        st.error(f"Impossible d'accéder au site (Erreur {response.status_code}). Essaie un autre lien.")
                
                except Exception as e:
                    st.error(f"Une erreur s'est produite : {e}")
        else:
            st.warning("L'URL est vide")