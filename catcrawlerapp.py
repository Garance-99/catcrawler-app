import streamlit as st
import requests
import re
from bs4 import BeautifulSoup
import time

# 🔹 Fonction pour récupérer le HTML d'une page
def get_soup(url):
    """Télécharge la page avec requests et retourne le HTML complet."""
    print(f"🌍 Chargement de {url}...")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            return BeautifulSoup(response.text, 'html.parser')
        else:
            print(f"❌ Erreur {response.status_code} en accédant à {url}")
            return None
    except requests.exceptions.RequestException:
        print(f"⏳ Timeout ou erreur réseau pour {url}")
        return None

# 🔹 Extraction des articles avec gestion de la page principale
def fetch_articles(category_url, excluded_urls):
    """🔍 Récupère les articles d'une catégorie ou de la page principale en analysant toutes ses pages.
    """
    soup = get_soup(category_url)
    if not soup:
        return []

    articles = set()
    visited_pages = set()
    pages_to_visit = [category_url]

    print(f"📌 Début de l'extraction pour la catégorie : {category_url}")

    while pages_to_visit:
        current_page = pages_to_visit.pop(0)
        if current_page in visited_pages:
            continue

        visited_pages.add(current_page)
        soup = get_soup(current_page)
        if not soup:
            continue

        st.write(f"📖 Exploration de la page : [{current_page}]({current_page})")

        # ✅ Extraction des articles
        for a_tag in soup.find_all("a", class_="button-read-more"):
            href = a_tag.get("href")
            if href and href.startswith("https://www.myes.school/fr/magazine/") and href not in excluded_urls:
                articles.add(href)

        # ✅ Recherche et correction des nouvelles pages de pagination
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            if re.search(r'/page/\d+/', href):
                full_url = requests.compat.urljoin(category_url, href)
                if full_url not in visited_pages and full_url not in pages_to_visit:
                    pages_to_visit.append(full_url)

        time.sleep(0.5)  # Pause courte pour éviter les blocages

    print(f"🔍 Extraction terminée. {len(articles)} articles trouvés.")
    return list(articles)

# 🔹 Extraction des liens internes d'un article (au-dessus de unicoach-post-navigation)
def fetch_links_from_article(article_url, excluded_urls):
    """🔗 Récupère les liens internes d'un article situés au-dessus de 'unicoach-post-navigation'.
    """
    soup = get_soup(article_url)
    if not soup:
        return []

    print(f"🔍 Analyse des liens internes de l'article : {article_url}")

    # Trouver la section de navigation pour limiter l'analyse
    navigation_section = soup.find("section", class_="unicoach-post-navigation")
    links = set()

    if navigation_section:
        # Récupérer tous les éléments avant la section 'unicoach-post-navigation'
        for element in soup.body.contents:
            if element == navigation_section:
                break  # Arrêter l'analyse dès qu'on atteint la section
            if element.name == "a" and element.has_attr("href"):
                href = element["href"].strip()
                if href.startswith("https://www.myes.school/fr/magazine/") and href not in excluded_urls:
                    links.add(href)
    else:
        # Si la section n'existe pas, analyser toute la page
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"].strip()
            if href.startswith("https://www.myes.school/fr/magazine/") and href not in excluded_urls:
                links.add(href)

    print(f"✅ Liens extraits pour {article_url} : {links}")
    return list(links)

# 🔹 Interface Streamlit
st.set_page_config(page_title="Scraper MyES", page_icon="🌍", layout="wide")

st.title("📰 Scraper MyES - Extraction d'articles")
st.write("Entrez une URL de catégorie (ou de la page principale du magazine) et récupérez les liens internes de chaque article.")

category_url = st.text_input("📌 URL de la catégorie :", "https://www.myes.school/fr/magazine/")

# ✅ Liste complète des URLs à exclure
excluded_urls = [
    "https://www.myes.school/fr/magazine/tourisme-et-culture/",
    "https://www.myes.school/fr/magazine/exercices-et-grammaire/grammaire-anglais/",
    "https://www.myes.school/fr/magazine/tourisme-et-culture/films-series-anglais/",
    "https://www.myes.school/fr/magazine/exercices-et-grammaire/exercices-anglais/",
    "https://www.myes.school/fr/magazine/exercices-et-grammaire/vocabulaire-anglais/",
    "https://www.myes.school/fr/magazine/conseils/certifications-anglais/",
    "https://www.myes.school/fr/magazine/conseils/formation-anglais/",
    "https://www.myes.school/fr/magazine/tourisme-et-culture/livres-anglais/",
    "https://www.myes.school/fr/magazine/conseils/professionnel/",
    "https://www.myes.school/fr/magazine/category/exercices-et-grammaire/",
    "https://www.myes.school/fr/magazine/exercices-et-grammaire/",
    "https://www.myes.school/fr/magazine/conseils/",
    "https://www.myes.school/fr/magazine/cpf/",
    "https://www.myes.school/fr/magazine/author/julie/",
    "https://www.myes.school/fr/magazine/",
    "https://www.myes.school/fr/magazine/tourisme-et-culture/culture/",
    "https://www.myes.school/fr/magazine/author/marketing/",
    "https://www.myes.school/fr/magazine/tourisme-et-culture/voyages/"
]

if st.button("🔍 Lancer l'extraction"):
    with st.spinner("⏳ Extraction en cours..."):
        articles = fetch_articles(category_url, excluded_urls)

        if articles:
            st.success(f"✅ {len(articles)} articles trouvés !")  # 🔥 Nombre d'articles affiché en cadre vert

            for article in articles:
                article_title = article.rstrip("/").split("/")[-1].replace("-", " ").capitalize()
                st.markdown(f"### 🔗 Extraction des liens internes pour [**{article_title}**]({article})")

                links = fetch_links_from_article(article, excluded_urls)

                if not links:
                    st.warning(f"⚠️ Aucun lien interne trouvé pour cet article.")
                else:
                    st.write(f"🔗 **Liens internes trouvés ({len(links)}) :**")
                    for link in links:
                        st.markdown(f"- [{link}]({link})")
