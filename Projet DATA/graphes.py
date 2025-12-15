########################################################################################
#   ETAPE 4 : CREATION DE GRAPHES
#   Fichier : graphes.py
#
#   Rôle de ce fichier :
#   - Charger les données propres (actions CAC40 + facteurs macro).
#   - Définir des MAPPINGS :
#       * pour relier chaque entreprise à un facteur macro (pétrole, gaz, taux, change…)
#       * pour afficher des noms lisibles (LVMH, TotalEnergies, etc.)
#   - Fournir 5 fonctions de graphiques réutilisables dans Streamlit :
#       1) Graphe 1 : Action vs Facteur macro (base 100)
#       2) Graphe 2 : Corrélation glissante Action / Macro
#       3) Graphe 3 : Volatilité glissante (30 jours)
#       4) Graphe 4 : Carte Risque / Rendement (type Markowitz)
#       5) Graphe 5 : Nuage de points Action / Macro + régression (beta, R²)
#
#   Ces fonctions sont appelées dans app.py (Streamlit) pour construire l'application.
########################################################################################

import pandas as pd
import numpy as np
import plotly.graph_objects as go

# =========================
# 1) Chargement des données
# =========================
# On charge ici les fichiers CSV déjà nettoyés et produits dans les étapes précédentes
# (ETAPE 1, 2, 3 : récupération, nettoyage, création de variables…).
# df_actions contient les données des actions du CAC40 (avec Rentabilite, Volatilite_30j, etc.)
# df_macros contient les facteurs macro (pétrole, gaz, change, Nasdaq, taux, etc.)

df_actions = pd.read_csv("data/cac40_final.csv", parse_dates=["Date"])
df_macros  = pd.read_csv("data/macros_final.csv", parse_dates=["Date"])

print("Aperçu actions :")
print(df_actions[["Date", "Ticker", "Close"]].head())
print("\nAperçu macros :")
print(df_macros[["Date", "Ticker", "Close"]].head())

# =========================
# 2) MAPPINGS
# =========================
# Ces dictionnaires permettent de relier :
#   - une entreprise à un facteur macro (MACRO_MAPPING)
#   - un ticker à un nom d’entreprise lisible (ENTERPRISE_LABELS)
#   - un ticker macro à un nom de facteur lisible (MACRO_LABELS)
#
# L'idée : plutôt que de manipuler des codes bruts (TTE.PA, BZ=F, EURUSD=X),
# on structure l'information et on l'explique économiquement.

# 2.1 Action CAC40 -> Facteur macro (ticker Yahoo Finance)
# Pour chaque entreprise, on choisit le facteur macro le plus pertinent :
#   - énergie : pétrole, gaz, métaux
#   - luxe / industrie / conso : taux de change EURUSD
#   - banques / immobilier : taux longs (TNX)
#   - tech : Nasdaq (NDX)
MACRO_MAPPING = {
    # Energie / matières premières
    "TTE.PA": "BZ=F",        # TotalEnergies -> Prix du pétrole Brent
    "ENGI.PA": "NG=F",       # Engie -> Gaz naturel
    "SGO.PA": "HG=F",        # Saint-Gobain -> Cuivre (construction / matériaux)
    "MT.AS": "HG=F",         # ArcelorMittal -> Métaux / cuivre (proxy)
    "AIR.PA": "BZ=F",        # Airbus -> pétrole (carburant aviation)
    "SAF.PA": "BZ=F",        # Safran -> pétrole (industrie aéronautique)

    # Entreprises très exposées au change EUR/USD
    "MC.PA": "EURUSD=X",     # LVMH
    "KER.PA": "EURUSD=X",    # Kering
    "RMS.PA": "EURUSD=X",    # Hermès
    "OR.PA": "EURUSD=X",     # L'Oréal
    "BN.PA": "EURUSD=X",     # Danone
    "CA.PA": "EURUSD=X",     # Carrefour
    "AI.PA": "EURUSD=X",     # Air Liquide
    "ML.PA": "EURUSD=X",     # Michelin
    "RNO.PA": "EURUSD=X",    # Renault
    "VIE.PA": "EURUSD=X",    # Veolia
    "LR.PA": "EURUSD=X",     # Legrand
    "SU.PA": "EURUSD=X",     # Schneider Electric
    "TEP.PA": "EURUSD=X",    # Teleperformance
    "EN.PA": "EURUSD=X",     # Bouygues
    "DG.PA": "EURUSD=X",     # Vinci
    "ORA.PA": "EURUSD=X",    # Orange
    "SAN.PA": "EURUSD=X",    # Sanofi
    "PUB.PA": "EURUSD=X",    # Publicis
    "VIV.PA": "EURUSD=X",    # Vivendi

    # Banques -> sensibilité aux taux longs
    "BNP.PA": "^TNX",        # BNP Paribas
    "GLE.PA": "^TNX",        # Société Générale
    "ACA.PA": "^TNX",        # Crédit Agricole
    "CS.PA": "^TNX",         # AXA
    "URW.PA": "^TNX",        # Unibail (immobilier commercial)

    # Tech / croissance -> Nasdaq
    "STMPA.PA": "^NDX",      # STMicroelectronics (ticker tel qu'il apparaît dans notre dataset)
    "CAP.PA": "^NDX",        # Capgemini
    "DSY.PA": "^NDX",        # Dassault Systèmes
    "WLN.PA": "^NDX",        # Worldline
    "HO.PA": "^NDX",         # Thales
}

# 2.2 Ticker -> Nom d’entreprise lisible
# Sert uniquement à afficher des noms compréhensibles dans les légendes et les titres de graphiques.
ENTERPRISE_LABELS = {
    "MC.PA": "LVMH",
    "TTE.PA": "TotalEnergies",
    "OR.PA": "L'Oréal",
    "RMS.PA": "Hermès",
    "SAN.PA": "Sanofi",
    "AIR.PA": "Airbus",
    "SU.PA": "Schneider Electric",
    "BNP.PA": "BNP Paribas",
    "GLE.PA": "Société Générale",
    "ACA.PA": "Crédit Agricole",
    "CS.PA": "AXA",
    "DG.PA": "Vinci",
    "VIE.PA": "Veolia",
    "ENGI.PA": "Engie",
    "ORA.PA": "Orange",
    "CAP.PA": "Capgemini",
    "STMPA.PA": "STMicroelectronics",
    "SAF.PA": "Safran",
    "HO.PA": "Thales",
    "MT.AS": "ArcelorMittal",
    "RNO.PA": "Renault",
    "ML.PA": "Michelin",
    "PUB.PA": "Publicis",
    "BN.PA": "Danone",
    "CA.PA": "Carrefour",
    "KER.PA": "Kering",
    "LR.PA": "Legrand",
    "SGO.PA": "Saint-Gobain",
    "AI.PA": "Air Liquide",
    "EN.PA": "Bouygues",
    "URW.PA": "Unibail-Rodamco-Westfield",
    "WLN.PA": "Worldline",
    "VIV.PA": "Vivendi",
    "TEP.PA": "Teleperformance",
    "DSY.PA": "Dassault Systèmes",
}

# 2.3 Ticker macro -> Nom de facteur lisible
# Idem : pour rendre les graphiques lisibles sans connaître les codes Yahoo Finance.
MACRO_LABELS = {
    "BZ=F": "Prix du pétrole Brent",
    "NG=F": "Prix du gaz naturel",
    "HG=F": "Prix du cuivre",
    "EURUSD=X": "Taux de change EUR/USD",
    "^TNX": "Taux obligataire US (10 ans)",
    "^NDX": "Indice Nasdaq 100",
    "^VIX": "Indice de volatilité (VIX)",
    "BTC-USD": "Bitcoin (BTC/USD)",
}

########################################################################################
#                           GRAPHE 1 : ACTION vs FACTEUR MACRO
########################################################################################

def plot_action_vs_macro(df_actions, df_macros, ticker):
    """
    Graphe 1 : compare l'évolution d'une action du CAC40 et de son facteur macro associé.
    
    - On récupère la série de prix de clôture de l'action et du facteur macro.
    - On les met en base 100 (pour comparer les évolutions relatives).
    - On trace les deux courbes sur le même graphique.
    
    Paramètres :
        df_actions : DataFrame des actions (avec Date, Ticker, Close, etc.)
        df_macros  : DataFrame des facteurs macro (Date, Ticker, Close)
        ticker     : ticker de l'entreprise (ex : "TTE.PA")
    
    Retour :
        fig : objet plotly.graph_objects.Figure
    """

    # Vérifie que l'entreprise a bien un facteur macro défini dans notre mapping
    if ticker not in MACRO_MAPPING:
        raise ValueError(f"Aucun facteur macro défini pour le ticker {ticker} dans MACRO_MAPPING.")

    macro_ticker = MACRO_MAPPING[ticker]

    # On récupère les noms lisibles pour le titre et la légende
    entreprise_label = ENTERPRISE_LABELS.get(ticker, ticker)
    macro_label      = MACRO_LABELS.get(macro_ticker, macro_ticker)

    # Action : on récupère la série Close pour le ticker sélectionné
    df_act = (
        df_actions[df_actions["Ticker"] == ticker]
        .sort_values("Date")[["Date", "Close"]]
        .rename(columns={"Close": "Close_action"})
    )

    # Macro : on récupère la série Close pour le facteur associé
    df_mac = (
        df_macros[df_macros["Ticker"] == macro_ticker]
        .sort_values("Date")[["Date", "Close"]]
        .rename(columns={"Close": "Close_macro"})
    )

    # Fusion sur les dates communes (inner = on garde seulement les dates présentes dans les deux séries)
    df_merge = pd.merge(df_act, df_mac, on="Date", how="inner")

    if df_merge.empty:
        raise ValueError(f"Aucune date commune entre {ticker} et {macro_ticker}.")

    # Mise en base 100 sur la première valeur disponible
    df_merge["Action_base100"] = df_merge["Close_action"] / df_merge["Close_action"].iloc[0] * 100
    df_merge["Macro_base100"]  = df_merge["Close_macro"]  / df_merge["Close_macro"].iloc[0]  * 100

    # Création de la figure Plotly
    fig = go.Figure()

    # Courbe de l'action
    fig.add_trace(go.Scatter(
        x=df_merge["Date"],
        y=df_merge["Action_base100"],
        mode="lines",
        name=f"{entreprise_label} (Action, base 100)"
    ))

    # Courbe du facteur macro
    fig.add_trace(go.Scatter(
        x=df_merge["Date"],
        y=df_merge["Macro_base100"],
        mode="lines",
        name=f"{macro_label} (Facteur macro, base 100)"
    ))

    fig.update_layout(
        title=f"Évolution de {entreprise_label} et de son facteur macro : {macro_label}",
        xaxis_title="Date",
        yaxis_title="Indice base 100",
        hovermode="x unified",
        legend=dict(x=0.01, y=0.99)
    )

    return fig

########################################################################################
#                           GRAPHE 2 : CORRÉLATION GLISSANTE
########################################################################################

def plot_rolling_corr(df_actions, df_macros, ticker, window=60):
    """
    Graphe 2 : corrélation glissante entre la rentabilité de l'action et celle du facteur macro.
    
    Idée :
    - On ne compare plus les PRIX, mais les RENTABILITÉS (%).
    - On calcule la corrélation entre :
        * Act_R : rentabilité de l'action
        * Macro_R : rentabilité du facteur macro
      sur une fenêtre glissante (par défaut 60 jours).
    - On visualise comment cette corrélation évolue dans le temps.
    
    Paramètres :
        df_actions : DataFrame des actions (avec colonne 'Rentabilite')
        df_macros  : DataFrame des facteurs macro (avec 'Close')
        ticker     : ticker de l'entreprise
        window     : taille de la fenêtre (en jours)
    
    Retour :
        fig : Figure Plotly
    """

    if ticker not in MACRO_MAPPING:
        raise ValueError(f"Aucun facteur macro défini pour le ticker {ticker} dans MACRO_MAPPING.")

    macro_ticker = MACRO_MAPPING[ticker]

    entreprise_label = ENTERPRISE_LABELS.get(ticker, ticker)
    macro_label      = MACRO_LABELS.get(macro_ticker, macro_ticker)

    # Action : on prend les rentabilités journalières déjà calculées dans df_actions
    df_act = (
        df_actions[df_actions["Ticker"] == ticker]
        .sort_values("Date")[["Date", "Rentabilite"]]
        .rename(columns={"Rentabilite": "Act_R"})
    )

    # Macro : on calcule la rentabilité à partir des prix de clôture
    df_mac = (
        df_macros[df_macros["Ticker"] == macro_ticker]
        .sort_values("Date")[["Date", "Close"]]
    )
    df_mac["Macro_R"] = df_mac["Close"].pct_change() * 100
    df_mac = df_mac[["Date", "Macro_R"]]

    # Fusion sur la date
    df_merge = pd.merge(df_act, df_mac, on="Date", how="inner")

    if df_merge.empty:
        raise ValueError(f"Aucune date commune entre {ticker} et {macro_ticker}.")

    # Corrélation glissante sur 'window' jours
    df_merge["RollingCorr"] = df_merge["Act_R"].rolling(window).corr(df_merge["Macro_R"])

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_merge["Date"],
        y=df_merge["RollingCorr"],
        mode="lines",
        name=f"Corrélation {entreprise_label} vs {macro_label} (fenêtre {window} jours)"
    ))

    fig.update_layout(
        title=f"Corrélation glissante ({window} jours) entre {entreprise_label} et {macro_label}",
        xaxis_title="Date",
        yaxis_title="Corrélation",
        hovermode="x unified",
        legend=dict(x=0.01, y=0.99),
        yaxis=dict(range=[-1, 1])  # la corrélation est toujours entre -1 et 1
    )

    return fig

########################################################################################
#                           GRAPHE 3 : VOLATILITÉ 30 JOURS
########################################################################################

def plot_volatilite_30j(df_actions, tickers, start_date=None, end_date=None):
    """
    Graphe 3 : évolution de la volatilité glissante (30 jours) pour une ou plusieurs entreprises.
    
    - On utilise la colonne 'Volatilite_30j' déjà créée dans le nettoyage.
    - On peut filtrer sur une période (start_date / end_date).
    - On peut afficher 1 ou plusieurs entreprises sur le même graphe.
    
    Paramètres :
        df_actions : DataFrame des actions (Date, Ticker, Volatilite_30j, ...)
        tickers    : string ou liste de tickers (ex : "TTE.PA" ou ["TTE.PA","MC.PA"])
        start_date : date de début (optionnelle, string "YYYY-MM-DD")
        end_date   : date de fin (optionnelle)
    
    Retour :
        fig : Figure Plotly
    """

    # Si on fournit un seul ticker en string, on le convertit en liste
    if isinstance(tickers, str):
        tickers = [tickers]

    df = df_actions.copy()

    # Filtrage temporel si des bornes sont fournies
    if start_date is not None:
        df = df[df["Date"] >= pd.to_datetime(start_date)]
    if end_date is not None:
        df = df[df["Date"] <= pd.to_datetime(end_date)]

    # On garde uniquement les colonnes utiles
    df = df[["Date", "Ticker", "Volatilite_30j"]]

    # On filtre sur les tickers demandés
    df = df[df["Ticker"].isin(tickers)]

    if df.empty:
        raise ValueError("Aucune donnée de volatilité trouvée pour les tickers sélectionnés.")

    fig = go.Figure()

    # On trace une courbe par ticker
    for t in tickers:
        df_t = df[df["Ticker"] == t].sort_values("Date")
        nom_entreprise = ENTERPRISE_LABELS.get(t, t)

        fig.add_trace(go.Scatter(
            x=df_t["Date"],
            y=df_t["Volatilite_30j"],
            mode="lines",
            name=f"{nom_entreprise} (Volatilité 30j)"
        ))

    fig.update_layout(
        title="Évolution de la volatilité glissante (30 jours)",
        xaxis_title="Date",
        yaxis_title="Volatilité (écart-type des rentabilités)",
        hovermode="x unified",
        legend=dict(x=0.01, y=0.99)
    )

    return fig

########################################################################################
#                           GRAPHE 4 : CARTE RISQUE / RENDEMENT
########################################################################################

def compute_risque_rendement(df_actions, start_date=None, end_date=None):
    """
    Fonction utilitaire :
    Calcule, pour chaque entreprise, le rendement moyen et le risque (volatilité) sur une période.
    
    - Rendement_moyen = moyenne de la rentabilité journalière (%)
    - Risque = écart-type de la rentabilité journalière (%)
    
    Paramètres :
        df_actions : DataFrame des actions
        start_date : date de début (optionnelle)
        end_date   : date de fin (optionnelle)
    
    Retour :
        df_stats : DataFrame avec colonnes :
                   Ticker, Rendement_moyen, Risque, Nom_entreprise
    """

    df = df_actions.copy()

    # Filtrage temporel
    if start_date is not None:
        df = df[df["Date"] >= pd.to_datetime(start_date)]
    if end_date is not None:
        df = df[df["Date"] <= pd.to_datetime(end_date)]

    # On retire les NA sur la rentabilité pour éviter de biaiser les stats
    df = df.dropna(subset=["Rentabilite"])

    # Agrégation par ticker : moyenne et écart-type
    df_stats = (
        df.groupby("Ticker")["Rentabilite"]
        .agg(Rendement_moyen="mean", Risque="std")
        .reset_index()
    )

    # Ajout du nom d'entreprise lisible
    df_stats["Nom_entreprise"] = df_stats["Ticker"].map(
        lambda t: ENTERPRISE_LABELS.get(t, t)
    )

    return df_stats


def plot_risque_rendement(df_actions, start_date=None, end_date=None):
    """
    Graphe 4 : carte risque–rendement pour les entreprises du CAC40.
    
    - Axe X : Risque (volatilité, écart-type de la rentabilité)
    - Axe Y : Rendement moyen (moyenne de la rentabilité)
    - Chaque point = une entreprise, avec son nom affiché à côté.
    
    Paramètres :
        df_actions : DataFrame des actions
        start_date : début de la période
        end_date   : fin de la période
    
    Retour :
        fig : Figure Plotly
    """

    df_stats = compute_risque_rendement(df_actions, start_date, end_date)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_stats["Risque"],
        y=df_stats["Rendement_moyen"],
        mode="markers+text",
        text=df_stats["Nom_entreprise"],
        textposition="top center",
        marker=dict(size=10),
        name="Entreprises CAC40"
    ))

    fig.update_layout(
        title="Carte risque–rendement des entreprises du CAC40",
        xaxis_title="Risque (Volatilité des rentabilités)",
        yaxis_title="Rendement moyen (%)",
        hovermode="closest"
    )

    return fig

########################################################################################
#                           GRAPHE 5 : SCATTER + RÉGRESSION
########################################################################################

def plot_scatter_action_vs_macro(df_actions, df_macros, ticker):
    """
    Graphe 5 : nuage de points entre la rentabilité de l'action et celle du facteur macro associé,
    avec droite de régression linéaire.
    
    On estime la relation :
        Act_R = alpha + beta * Macro_R
    
    - X = rentabilité du facteur macro (%)
    - Y = rentabilité de l'action (%)
    - beta = sensibilité (pente)
    - R² = qualité de l'ajustement
    
    Paramètres :
        df_actions : DataFrame des actions (avec Rentabilite)
        df_macros  : DataFrame des facteurs macro (avec Close)
        ticker     : ticker de l'entreprise
    
    Retour :
        fig : Figure Plotly
    """

    if ticker not in MACRO_MAPPING:
        raise ValueError(f"Aucun facteur macro défini pour le ticker {ticker} dans MACRO_MAPPING.")

    macro_ticker = MACRO_MAPPING[ticker]

    entreprise_label = ENTERPRISE_LABELS.get(ticker, ticker)
    macro_label      = MACRO_LABELS.get(macro_ticker, macro_ticker)

    # Action : rentabilités
    df_act = (
        df_actions[df_actions["Ticker"] == ticker]
        .sort_values("Date")[["Date", "Rentabilite"]]
        .rename(columns={"Rentabilite": "Act_R"})
    )

    # Macro : rentabilités
    df_mac = (
        df_macros[df_macros["Ticker"] == macro_ticker]
        .sort_values("Date")[["Date", "Close"]]
    )
    df_mac["Macro_R"] = df_mac["Close"].pct_change() * 100
    df_mac = df_mac[["Date", "Macro_R"]]

    # Fusion sur la date, puis suppression des NA
    df_merge = pd.merge(df_act, df_mac, on="Date", how="inner").dropna(subset=["Act_R", "Macro_R"])

    if df_merge.empty:
        raise ValueError(
            f"Aucune donnée commune de rentabilité entre {ticker} et {macro_ticker}."
        )

    x = df_merge["Macro_R"].values
    y = df_merge["Act_R"].values

    # Régression linéaire : on estime beta (pente) et alpha (intercept)
    beta, alpha = np.polyfit(x, y, 1)
    # Corrélation linéaire
    corr = np.corrcoef(x, y)[0, 1]
    # Coefficient de détermination R²
    r2 = corr ** 2

    # Droite de régression : on génère des points réguliers sur l'axe X
    x_min, x_max = x.min(), x.max()
    x_line = np.linspace(x_min, x_max, 100)
    y_line = alpha + beta * x_line

    fig = go.Figure()

    # Nuage de points (observations journalières)
    fig.add_trace(go.Scatter(
        x=df_merge["Macro_R"],
        y=df_merge["Act_R"],
        mode="markers",
        name="Observations journalières",
        opacity=0.6
    ))

    # Droite de régression
    fig.add_trace(go.Scatter(
        x=x_line,
        y=y_line,
        mode="lines",
        name=f"Régression linéaire (β ≈ {beta:.2f}, R² ≈ {r2:.2f})"
    ))

    fig.update_layout(
        title=(
            f"Sensibilité de {entreprise_label} à son facteur macro : {macro_label}<br>"
            f"(β ≈ {beta:.2f}, R² ≈ {r2:.2f})"
        ),
        xaxis_title=f"Rentabilité {macro_label} (%)",
        yaxis_title=f"Rentabilité {entreprise_label} (%)",
        hovermode="closest"
    )

    return fig

########################################################################################
#                           TESTS LOCAUX
########################################################################################
# Ce bloc s'exécute uniquement si on lance directement graphes.py
# (et NON quand le fichier est importé par Streamlit).
# Il sert uniquement pour tester les fonctions de graphes en local. donc tu peux supp stv, je l'avais utilisé pour regarder les graphes avant de faire le streamlit
########################################################################################

if __name__ == "__main__":
    # GRAPHE 1 : Action vs Macro pour TotalEnergies
    fig1 = plot_action_vs_macro(df_actions, df_macros, "TTE.PA")
    fig1.show()

    # GRAPHE 1 : Action vs Macro pour LVMH
    fig1b = plot_action_vs_macro(df_actions, df_macros, "MC.PA")
    fig1b.show()

    # GRAPHE 2 : Corrélation glissante pour TotalEnergies
    fig2 = plot_rolling_corr(df_actions, df_macros, "TTE.PA", window=60)
    fig2.show()

    # GRAPHE 3 : Volatilité 30 jours pour quelques entreprises
    fig3 = plot_volatilite_30j(
        df_actions,
        ["TTE.PA", "MC.PA", "BNP.PA"],
        start_date="2005-01-01"
    )
    fig3.show()

    # GRAPHE 4 : Carte risque / rendement sur la période 2005+
    fig4 = plot_risque_rendement(
        df_actions,
        start_date="2005-01-01"
    )
    fig4.show()

    # GRAPHE 5 : Sensibilité Action / Macro pour TotalEnergies
    fig5_total = plot_scatter_action_vs_macro(df_actions, df_macros, "TTE.PA")
    fig5_total.show()

    # GRAPHE 5 : Sensibilité Action / Macro pour LVMH
    fig5_lvmh = plot_scatter_action_vs_macro(df_actions, df_macros, "MC.PA")
    fig5_lvmh.show()
