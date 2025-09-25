import requests
from bs4 import BeautifulSoup
import re
import unicodedata

# URLs base
BASE_URL = "https://books.toscrape.com/"
CATALOGUE_URL = BASE_URL + "catalogue/"

# Map rating
RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def clean_text(text):
    text = text.strip() # remove espaços extras 
    text = unicodedata.normalize('NFKD', text) # normaliza caracteres Unicode
    return text     

def get_soup(url: str):
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def get_categories():
    soup = get_soup(BASE_URL)
    category_links = soup.select("div.side_categories ul li ul li a")
    categories = {}
    for link in category_links:
        name = link.text.strip()
        url = BASE_URL + link['href']
        categories[name] = url
    return categories


def extract_books_from_page(soup, category_name):
    books = []
    for book in soup.select("article.product_pod"):
        title = clean_text(book.h3.a["title"])

        price_text = book.select_one(".price_color").text.strip()
        price = float(re.sub(r'[^\d.]', '', price_text))

        rating_text = book.p["class"][1]
        rating = RATING_MAP.get(rating_text, 0)

        availability = clean_text(book.select_one(".instock.availability").text)

        image_url = BASE_URL + book.img["src"].replace("../", "")

        books.append({
            "title": title,
            "price": price,
            "rating": rating,
            "availability": availability,
            "category": clean_text(category_name) or "Unknown",
            "image_url": image_url
        })
    return books



def scrape_books():
    all_books = []
    book_id = 1
    categories = get_categories()
    if not categories:
        categories = {"Unknown": BASE_URL}

    for category_name, category_url in categories.items():
        page_url = category_url
        while page_url:
            print(f"📖 Extraindo {category_name} - {page_url}")
            soup = get_soup(page_url)
            books = extract_books_from_page(soup, category_name)

            for b in books:
                b['id'] = book_id
                book_id += 1
            all_books.extend(books)

            next_btn = soup.select_one("li.next a")
            if next_btn:
                next_page = next_btn['href']
                page_url = "/".join(page_url.split("/")[:-1]) + "/" + next_page
            else:
                page_url = None
    return all_books
