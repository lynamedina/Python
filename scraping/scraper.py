import requests
from bs4 import BeautifulSoup

URL = "https://www.tunisie-annonce.com/"
response = requests.get(URL)
soup = BeautifulSoup(response.text, "html.parser")

annonces = soup.find_all("div", class_="annonce")  # Adapter en fonction du site
for annonce in annonces:
    titre = annonce.find("h2").text
    print(titre)