from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import csv

# Chemin vers ton WebDriver (télécharge-le si nécessaire : https://chromedriver.chromium.org/downloads)
CHROMEDRIVER_PATH = "chromedriver.exe"

# Options pour éviter les fenêtres qui s'ouvrent
options = Options()
options.add_argument("--headless")  # Mode sans interface graphique

# Lancer le navigateur
service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

# Ouvrir la page
url = "https://www.tunisie-annonce.com/AnnoncesImmobilier.asp"
driver.get(url)

# Attendre le chargement des annonces
driver.implicitly_wait(5)

# Récupérer les annonces
annonces = driver.find_elements(By.CLASS_NAME, "small")

# Liste pour stocker les annonces extraites
annonces_data = []

for annonce in annonces:
    try:
        titre = annonce.find_element(By.CLASS_NAME, "annonceur").text.strip()
        prix = annonce.find_element(By.CLASS_NAME, "prix").text.strip()
        # Extraire le lien si disponible
        lien = annonce.find_element(By.TAG_NAME, "a").get_attribute("href") if annonce.find_element(By.TAG_NAME, "a") else "N/A"
        
        # Ajouter les données extraites dans la liste
        annonces_data.append([titre, prix, lien])
        
        print(f"Titre: {titre} | Prix: {prix} | Lien: {lien}")
    except Exception as e:
        print(f"Erreur lors de l'extraction de l'annonce: {e}")

# Fermer Selenium
driver.quit()

# Sauvegarder les annonces dans un fichier CSV
with open("annonces.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Titre", "Prix", "Lien"])  # Écrire les en-têtes
    writer.writerows(annonces_data)  # Écrire les données des annonces