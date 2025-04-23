from dash import Dash, html, dcc
import pandas as pd
import plotly.express as px
import sqlite3

# Charger les données
def load_data():
    conn = sqlite3.connect("../annonces_new.db")  # adapte le chemin si besoin
    df = pd.read_sql_query("SELECT * FROM annonces", conn)
    conn.close()

    df["prix_clean"] = df["prix"].str.replace(r"[^\d]", "", regex=True)
    df["prix_clean"] = pd.to_numeric(df["prix_clean"], errors='coerce')

    return df

# Initialiser les données
df = load_data()

# Créer les figures
fig_types = px.pie(df, names="type", title="Répartition des types de biens")
fig_prix = px.histogram(df, x="prix_clean", nbins=20, title="Distribution des prix")

# App Dash
app = Dash(__name__)
app.layout = html.Div([
    html.H1("Mini Dashboard Immobilier", style={"textAlign": "center"}),

    dcc.Graph(figure=fig_types),
    dcc.Graph(figure=fig_prix)
])

if __name__ == "__main__":
    app.run(debug=True)
