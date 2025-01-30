import streamlit as st
import requests
import re
from bs4 import BeautifulSoup

# 🔹 Fonction pour récupérer le HTML d'une page
def get_soup(url):
    """Télécharge la page avec requests et retourne le HTML complet."""
    print(f"🌍 Chargement de {url} avec Requests...")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return BeautifulSoup(response.text, 'html.parser')
    else:
        print(f"❌ Erreur {response.status_code} en accédant à {url}")
        return None

# 🔹 Extraction des articles et de la pagination automatiquement
def fetch_articles(category_url, excluded_urls):
    """🔍 Récupère les articles depuis une catégorie en analysant toutes ses pages."""
    soup = get_soup(category_url)
    if not soup:
        return []

    articles = set()
    pagination_links = set([category_url])  # On commence avec la page principale

    print(f"📌 Analyse de la catégorie : {category_url}")

    # 🔄 Tant qu'on trouve des nouvelles pages de pagination, on les explore
    while pagination_links:
        current_page = pagination_links.pop()
        soup = get_soup(current_page)
        if not soup:
            continue

        # ✅ Extraction des articles
        for a_tag in soup.find_all("a", class_="button-read-more"):
            href = a_tag.get("href")
            if href and href.startswith("https://www.myes.school/fr/magazine/") and href not in excluded_urls:
                print(f"✅ Article détecté : {href}")
                articles.add(href)

        # ✅ Recherche de nouvelles pages de pagination
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            if re.search(r'/page/\d+/', href) and href not in pagination_links:
                print(f"📖 Page de pagination trouvée : {href}")
                pagination_links.add(href)

    return list(articles)

# 🔹 Extraction des liens internes d'un article
def fetch_links_from_article(article_url, excluded_urls):
    """🔗 Récupère les liens internes d'un article."""
    soup = get_soup(article_url)
    if not soup:
        return []

    print(f"🔍 Analyse des liens internes de l'article : {article_url}")

    # ✅ Vérifier si on trouve la section "unicoach-post-navigation"
    main_content = soup.find("section", class_="unicoach-post-navigation")

    # ✅ Si cette section existe, on analyse tout ce qui est avant
    if main_content:
        content_to_analyze = main_content.find_previous_sibling()
        if not content_to_analyze:
            content_to_analyze = soup
    else:
        content_to_analyze = soup

    # ✅ Récupérer tous les liens internes valides
    links = set()
    for a_tag in content_to_analyze.find_all("a", href=True):
        href = a_tag["href"].strip()
        if href.startswith("https://www.myes.school/fr/magazine/") and href not in excluded_urls:
            links.add(href)

    print(f"✅ Liens extraits pour {article_url} : {links}")

    return list(links)

# 🔹 Interface Streamlit
st.set_page_config(page_title="Scraper MyES", page_icon="🌍", layout="wide")

st.title("📰 Scraper MyES - Extraction d'articles")
st.write("Entrez une URL de catégorie et récupérez automatiquement les articles et leurs liens internes.")

category_url = st.text_input("📌 URL de la catégorie :", "https://www.myes.school/fr/magazine/vocabulaire-anglais/")

# ✅ Liste complète des URLs à exclure
excluded_urls = [
    "https://www.myes.school/fr/magazine/",
    "https://www.myes.school/fr/magazine/category/",
    "https://www.myes.school/fr/magazine/non-classifiee/",
]

if st.button("🔍 Lancer l'extraction"):
    with st.spinner("⏳ Extraction en cours..."):
        articles = fetch_articles(category_url, excluded_urls)

        if articles:
            st.success(f"✅ {len(articles)} articles trouvés !")
            st.write("### 📋 Liste des articles extraits")
            for article in articles:
                st.markdown(f"- [{article}]({article})")

            for article in articles:
                # Extraire le titre depuis l'URL
                article_title = article.rstrip("/").split("/")[-1].replace("-", " ").capitalize()

                # Afficher une phrase avec un lien cliquable
                st.markdown(f"### 🔗 Extraction des liens internes pour [**{article_title}**]({article})")

                links = fetch_links_from_article(article, excluded_urls)

                if not links:
                    st.warning(f"⚠️ Aucun lien interne trouvé pour cet article.")
                else:
                    st.write(f"🔗 **Liens internes trouvés ({len(links)}) :**")
                    for link in links:
                        st.markdown(f"- [{link}]({link})")
