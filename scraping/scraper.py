from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time

# Configuration du navigateur
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")  # Pour éviter la détection
# options.add_argument("--headless")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Accéder à la page
url = "http://www.tunisie-annonce.com/AnnoncesImmobilier.asp"
driver.get(url)

# Attendre que la page se charge complètement
time.sleep(5)  # Augmentez ce délai si nécessaire

# Récupérer le HTML
soup = BeautifulSoup(driver.page_source, 'html.parser')

# Fermer le navigateur
driver.quit()

# Trouver le tableau principal
table = soup.find('table', {'width': '100%', 'cellspacing': '0', 'cellpadding': '0'})

annonces = []

if table:
    # Trouver toutes les lignes d'annonces (ignore la première ligne d'en-tête)
    for row in table.find_all('tr')[1:]:
        cols = row.find_all('td')
        
        # Vérifier que nous avons assez de colonnes
        if len(cols) >= 12:
            annonce = {
                'Région': cols[1].get_text(strip=True),
                'Nature': cols[3].get_text(strip=True),
                'Type': cols[5].get_text(strip=True),
                'Texte annonce': cols[7].get_text(strip=True),
                'Prix': cols[9].get_text(strip=True).replace(' ', ''),
                'Modifiée': cols[11].get_text(strip=True)
            }
            annonces.append(annonce)

# Sauvegarder en CSV
if annonces:
    df = pd.DataFrame(annonces)
    
    # Nettoyage supplémentaire
    df['Prix'] = df['Prix'].str.extract(r'(\d+)')[0]  # Extraire uniquement les chiffres
    
    # Sauvegarde
    df.to_csv('annonces_immobilieres.csv', index=False, encoding='utf-8-sig')
    print(f"✅ {len(annonces)} annonces sauvegardées dans annonces_immobilieres.csv")
else:
    print("⚠️ Aucune annonce trouvée. Raisons possibles :")
    print("- Le site a changé sa structure HTML")
    print("- Le chargement prend plus de temps (augmentez le time.sleep)")
    print("- Le site bloque les robots (essayez avec --headless désactivé)")
    
    # Sauvegarde du HTML pour analyse
    with open("debug_page.html", "w", encoding="utf-8") as f:
        f.write(soup.prettify())
    print("HTML sauvegardé dans debug_page.html pour inspection")