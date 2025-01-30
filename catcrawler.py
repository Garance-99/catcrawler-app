import time
import re
from collections import defaultdict
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup

def get_soup_with_selenium(url):
    """📥 Charge la page avec Selenium, clique sur les éléments cachés et retourne le HTML complet."""
    print(f"🌍 Chargement de {url} avec Selenium...")

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)

    # ✅ Attente du chargement initial
    time.sleep(3)

    # ✅ Scroll lent pour charger les articles
    last_height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(5):
        driver.execute_script("window.scrollBy(0, 500);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # ✅ Cliquer sur les boutons "Read More"
    try:
        read_more_buttons = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "read-more-wrap"))
        )
        for button in read_more_buttons:
            try:
                driver.execute_script("arguments[0].click();", button)
                time.sleep(1)
            except:
                pass
    except:
        pass

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()
    return soup

def fetch_articles(category_url, excluded_urls):
    """🔍 Récupère les articles depuis la catégorie et les pages de pagination."""
    soup = get_soup_with_selenium(category_url)
    if not soup:
        return []

    articles = set()
    pagination_links = set()

    print(f"📌 Analyse de la catégorie : {category_url}")

    for a_tag in soup.find_all("a", class_="button-read-more"):
        href = a_tag['href']
        if href.startswith("https://www.myes.school/fr/magazine/") and href not in excluded_urls:
            print(f"✅ Article détecté : {href}")
            articles.add(href)

    for a_tag in soup.find_all("a", href=True):
        href = a_tag['href']
        if re.search(r'/page/\d+/', href) and href not in pagination_links:
            print(f"📖 Page de pagination trouvée : {href}")
            pagination_links.add(href)

    # ✅ Ajout des pages de pagination manquantes
    for i in range(2, 7):  # De page 2 à 6
        pagination_links.add(f"https://www.myes.school/fr/magazine/vocabulaire-anglais/page/{i}/")

    for page in pagination_links:
        pagination_articles = fetch_articles_from_pagination(page, excluded_urls)
        articles.update(pagination_articles)

    return list(articles)

def fetch_articles_from_pagination(pagination_url, excluded_urls):
    """📖 Récupère les articles depuis une page de pagination et affiche ses liens internes."""
    soup = get_soup_with_selenium(pagination_url)
    if not soup:
        return []

    articles = set()
    print(f"🔄 Exploration de la pagination : {pagination_url}")

    for a_tag in soup.find_all("a", class_="button-read-more"):
        href = a_tag['href']
        if href.startswith("https://www.myes.school/fr/magazine/") and href not in excluded_urls:
            print(f"✅ Article extrait depuis pagination : {href}")
            articles.add(href)

    # ✅ Extraction et affichage des liens internes présents dans la page de pagination
    links_in_page = fetch_links_in_page(soup, excluded_urls)
    print(f"📌 Liens internes trouvés dans {pagination_url} :")
    for link in links_in_page:
        print(f"  - {link}")

    return list(articles)

def fetch_links_in_page(soup, excluded_urls):
    """🔗 Récupère les liens internes trouvés dans une page (sans les articles)."""
    links = set()
    for a_tag in soup.find_all("a", href=True):
        href = a_tag['href']
        if href.startswith("https://www.myes.school/fr/magazine/") and href not in excluded_urls:
            links.add(href)
    return list(links)

def fetch_links_from_article(article_url, excluded_urls):
    """🔗 Récupère les liens internes d'un article en s'arrêtant avant 'unicoach-post-navigation'."""
    soup = get_soup_with_selenium(article_url)
    if not soup:
        return []

    links = set()
    print(f"🔍 Analyse des liens internes de l'article : {article_url}")

    # ✅ Arrêter l'analyse avant la section <section class="unicoach-post-navigation">
    main_content = soup.find("section", class_="unicoach-post-navigation")
    if main_content:
        content_to_analyze = main_content.find_previous_sibling()
    else:
        content_to_analyze = soup

    # ✅ Récupérer uniquement les liens valides
    for a_tag in content_to_analyze.find_all("a", href=True):
        href = a_tag['href']
        if href.startswith("https://www.myes.school/fr/magazine/") and href not in excluded_urls:
            links.add(href)

    return list(links)

def main():
    category_url = "https://www.myes.school/fr/magazine/vocabulaire-anglais/"
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

    articles = fetch_articles(category_url, excluded_urls)

    print("\n✅ Liste finale des articles extraits :")
    for i, article in enumerate(articles, start=1):
        print(f"{i}. {article}")

    all_links = {}
    for article in articles:
        links = fetch_links_from_article(article, excluded_urls)
        all_links[article] = links
        print(f"\n📌 Liens internes trouvés dans l'article {article} :")
        for link in links:
            print(f"  - {link}")

if __name__ == "__main__":
    main()
