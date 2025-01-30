import streamlit as st
import requests
import re
from bs4 import BeautifulSoup

# 🔹 Fonction pour récupérer le HTML d'une page sans Selenium
def get_soup(url):
    """Télécharge la page avec requests et retourne le HTML complet."""
    print(f"🌍 Chargement de {url} avec Requests...")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    else:
        print(f"❌ Erreur {response.status_code} en accédant à {url}")
        return None

# 🔹 Extraction des articles
def fetch_articles(category_url, excluded_urls):
    """🔍 Récupère les articles depuis la catégorie et les pages de pagination."""
    soup = get_soup(category_url)
    if not soup:
        return []

    articles = set()
    pagination_links = set()

    print(f"📌 Analyse de la catégorie : {category_url}")

    for a_tag in soup.find_all("a", class_="button-read-more"):
        href = a_tag.get("href")
        if href and href.startswith("https://www.myes.school/fr/magazine/") and href not in excluded_urls:
            print(f"✅ Article détecté : {href}")
            articles.add(href)

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if re.search(r'/page/\d+/', href) and href not in pagination_links:
            print(f"📖 Page de pagination trouvée : {href}")
            pagination_links.add(href)

    # ✅ Ajout des pages de pagination manquantes (de page 2 à 6)
    for i in range(2, 7):
        pagination_links.add(f"https://www.myes.school/fr/magazine/vocabulaire-anglais/page/{i}/")

    for page in pagination_links:
        pagination_articles = fetch_articles_from_pagination(page, excluded_urls)
        articles.update(pagination_articles)

    return list(articles)

# 🔹 Extraction des articles depuis une page de pagination
def fetch_articles_from_pagination(pagination_url, excluded_urls):
    """📖 Récupère les articles depuis une page de pagination et affiche ses liens internes."""
    soup = get_soup(pagination_url)
    if not soup:
        return []

    articles = set()
    print(f"🔄 Exploration de la pagination : {pagination_url}")

    for a_tag in soup.find_all("a", class_="button-read-more"):
        href = a_tag.get("href")
        if href and href.startswith("https://www.myes.school/fr/magazine/") and href not in excluded_urls:
            print(f"✅ Article extrait depuis pagination : {href}")
            articles.add(href)

    return list(articles)

# 🔹 Extraction des liens internes d'un article
def fetch_links_from_article(article_url, excluded_urls):
    """🔗 Récupère les liens internes d'un article en s'arrêtant avant 'unicoach-post-navigation'."""
    soup = get_soup(article_url)
    if not soup:
        return []

    print(f"🔍 Analyse des liens internes de l'article : {article_url}")

    # ✅ Vérifier si on trouve la section "unicoach-post-navigation"
    main_content = soup.find("section", class_="unicoach-post-navigation")

    # ✅ Si on trouve cette section, on prend tout ce qui est avant
    if main_content:
        content_to_analyze = main_content.find_previous_sibling()
        if not content_to_analyze:
            content_to_analyze = soup  # Sécurité : si rien n'est trouvé, analyser tout
    else:
        content_to_analyze = soup  # Si la section n'existe pas, on analyse tout

    # 🛠 Debug : Afficher le contenu analysé
    print(f"📌 Contenu analysé pour {article_url}")

    # ✅ Récupérer TOUS les liens trouvés
    links = set()
    for a_tag in content_to_analyze.find_all("a", href=True):
        href = a_tag["href"].strip()  # Supprimer les espaces inutiles
        links.add(href)

    # ✅ Debug : Afficher tous les liens trouvés AVANT filtrage
    print(f"📌 Liens trouvés (AVANT filtrage) pour {article_url} : {links}")

    # ✅ Filtrage des liens valides
    filtered_links = {link for link in links if link.startswith("https://www.myes.school/fr/magazine/") and link not in excluded_urls}

    # ✅ Debug : Afficher tous les liens trouvés APRÈS filtrage
    print(f"✅ Liens après filtrage pour {article_url} : {filtered_links}")

    return list(filtered_links)

# 🔹 Interface Streamlit
st.set_page_config(page_title="Scraper MyES", page_icon="🌍", layout="wide")

st.title("📰 Scraper MyES - Extraction d'articles")
st.write("Entrez une URL de catégorie et récupérez automatiquement les articles et leurs liens internes.")

category_url = st.text_input("📌 URL de la catégorie :", "https://www.myes.school/fr/magazine/vocabulaire-anglais/")

# ✅ Liste complète des URLs à exclure
excluded_urls = [
    "https://www.myes.school/fr/magazine/exercices-et-grammaire/exercices-anglais/",
    "https://www.myes.school/fr/magazine/exercices-et-grammaire/vocabulaire-anglais/",
    "https://www.myes.school/fr/magazine/tourisme-et-culture/",
    "https://www.myes.school/fr/magazine/category/exercices-et-grammaire/",
    "https://www.myes.school/fr/magazine/conseils/certifications-anglais/",
    "https://www.myes.school/fr/magazine/non-classifiee/",
    "https://www.myes.school/fr/magazine/",
    "https://www.myes.school/fr/magazine/conseils/professionnel/",
    "https://www.myes.school/fr/magazine/tourisme-et-culture/voyages/",
    "https://www.myes.school/fr/magazine/author/marketing/",
    "https://www.myes.school/fr/magazine/cpf/",
    "https://www.myes.school/fr/magazine/tourisme-et-culture/films-series-anglais/",
    "https://www.myes.school/fr/magazine/exercices-et-grammaire/grammaire-anglais/",
    "https://www.myes.school/fr/magazine/tourisme-et-culture/livres-anglais/",
    "https://www.myes.school/fr/magazine/conseils/certifications-anglais/",
    "https://www.myes.school/fr/magazine/conseils/formation-anglais/"
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
