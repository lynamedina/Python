import requests
import sqlite3
import pandas as pd
from fastapi import FastAPI
from bs4 import BeautifulSoup
from datetime import datetime

app = FastAPI()

# Nom de la base de données
DB_NAME = "annonces_new.db"

# Fonction pour initialiser la base de données SQLite
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS annonces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            region TEXT,
            nature TEXT,
            type TEXT,
            texte TEXT,
            prix TEXT,
            modifie TEXT,
            superficie TEXT,
            description TEXT,
            numero_tel TEXT,
            localisation TEXT,
            details_link TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()


# Route pour récupérer les annonces stockées
@app.get("/annonces")
def get_annonces():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM annonces", conn)
    conn.close()
    return df.to_dict(orient="records")

# Route pour lancer le scraping
@app.post("/scrape")
def scrape_annonces():
    base_url = "http://www.tunisie-annonce.com/AnnoncesImmobilier.asp?rech_order_by=11&rech_page_num={}"
    annonces = []
   # page = 1

    date_min = datetime(2025, 1, 1)
    date_max = datetime(2025, 2, 28)

    for page in range(315, 321):
        url = base_url.format(page)
        print(f"Scraping page {page}...")

        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, "html.parser")

        rows = soup.select("tr[bgcolor='#294a73'] ~ tr")
        if not rows:
            break

        for row in rows:
            try:
                cols = row.find_all("td")
                if len(cols) > 10 and cols[1].text.strip() != "":
                    modifie = cols[11].text.strip()
                    try:
                        date_modifie = datetime.strptime(modifie, "%d/%m/%Y")

                        if date_min <= date_modifie <= date_max:
                            region = cols[1].text.strip()
                            nature = cols[3].text.strip()
                            type_ = cols[5].text.strip()
                            texte = cols[7].text.strip()
                            prix = cols[9].text.strip()
                            details_link = "http://www.tunisie-annonce.com/" + cols[7].find("a")["href"]

                            # Ouvrir la page des détails pour récupérer plus d'infos
                            detail_resp = requests.get(details_link)
                            detail_soup = BeautifulSoup(detail_resp.text, "html.parser")

                            def get_detail(xpath):
                                el = detail_soup.find("tr", text=lambda t: t and xpath in t)
                                if el and el.find_next("td"):
                                    return el.find_next("td").text.strip()
                                return "non disponible"

                            superficie = get_detail("Surface")
                            description = get_detail("Texte")
                            localisation = get_detail("Localisation")

                            try:
                                numero_tel = detail_soup.find("li", {"class": "cellphone"}).find("span").text.strip()
                            except:
                                numero_tel = "non disponible"

                            # Ajouter aux résultats
                            annonces.append((region, nature, type_, texte, prix, modifie, superficie, description, numero_tel, localisation, details_link))

                    except Exception as e:
                        print(f"Erreur parsing date: {e}")

            except Exception as e:
                print(f"Erreur ligne: {e}")

        print(f"Page {page} récupérée avec succès!")
        #page += 1

    # Enregistrer dans la base de données SQLite
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.executemany("""
        INSERT INTO annonces (region, nature, type, texte, prix, modifie, superficie, description, numero_tel, localisation, details_link)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, annonces)
    conn.commit()
    conn.close()

    return {"message": f"{len(annonces)} annonces enregistrées avec succès!"}

