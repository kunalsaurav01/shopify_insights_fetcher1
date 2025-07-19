import requests
from bs4 import BeautifulSoup
import re

# --- Fetch Website HTML ---
def fetch_html(url: str) -> str:
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    elif response.status_code == 404:
        raise Exception("404 - Website not found.")
    else:
        raise Exception("500 - Internal Error.")

# --- Extract Product Catalog ---
def extract_product_catalog(base_url: str) -> list:
    try:
        json_url = base_url.rstrip('/') + "/products.json"
        response = requests.get(json_url)
        data = response.json()
        return [product["title"] for product in data.get("products", [])]
    except:
        return []

# --- Extract Hero Products ---
def extract_hero_products(soup: BeautifulSoup) -> list:
    products = []
    for link in soup.find_all('a', href=True):
        if '/products/' in link['href']:
            title = link.get_text(strip=True)
            if title:
                products.append(title)
    return list(set(products))

# --- Extract Clean Policy Text ---
def extract_policy_text(base_url: str, policy_slug: str) -> str:
    try:
        html = fetch_html(base_url.rstrip('/') + f"/policies/{policy_slug}")
        soup = BeautifulSoup(html, 'lxml')
        # Focus on main content area
        content = soup.find('main') or soup.find('div', {'class': 'main-content'}) or soup.find('div', {'id': 'content'})
        if content:
            return content.get_text(separator="\n", strip=True)
        return soup.get_text(separator="\n", strip=True)
    except:
        return None

# --- Extract Social Handles ---
def extract_social_links(soup: BeautifulSoup) -> list:
    links = []
    for a in soup.find_all('a', href=True):
        if any(social in a['href'] for social in ['instagram.com', 'facebook.com', 'tiktok.com']):
            links.append(a['href'])
    return list(set(links))

# --- Extract Contact Details (Improved) ---
def extract_contact_details(soup: BeautifulSoup) -> list:
    text = soup.get_text(separator=" ")

    # Extract emails
    emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)

    # Extract phone numbers (improved regex)
    phones = re.findall(r"(\+?\d[\d\s\-()]{8,15})", text)
    phones = [p for p in phones if len(re.sub(r"\D", "", p)) >= 10]  # Keep only valid phone numbers

    return list(set(emails + phones))

# --- Extract FAQs ---
def extract_faqs(soup: BeautifulSoup) -> list:
    faqs = []

    # Look for common FAQ sections
    faq_sections = soup.find_all('div', class_=re.compile("faq", re.I))

    for section in faq_sections:
        questions = section.find_all(['h2', 'h3', 'strong'])
        answers = section.find_all('p')

        for q, a in zip(questions, answers):
            q_text = q.get_text(strip=True)
            if '?' in q_text:
                a_text = a.get_text(strip=True)
                faqs.append({
                    "question": q_text,
                    "answer": a_text
                })

    return faqs

# --- Extract About Brand Text and Important Links ---
def extract_about_and_links(soup: BeautifulSoup, base_url: str) -> tuple:
    about_text = None
    important_links = []

    for a in soup.find_all('a', href=True):
        href = a['href']
        text = a.get_text(strip=True)

        # Identify important links
        if any(keyword in href.lower() for keyword in ['contact', 'track', 'blog', 'about']):
            if href.startswith('/'):
                full_link = base_url.rstrip('/') + href
            elif href.startswith('http'):
                full_link = href
            else:
                full_link = base_url.rstrip('/') + '/' + href
            important_links.append(full_link)

        # Try to fetch About Page content
        if 'about' in href.lower() and not about_text:
            try:
                about_html = fetch_html(base_url.rstrip('/') + href)
                about_soup = BeautifulSoup(about_html, 'lxml')
                about_content = about_soup.find('main') or about_soup.find('div', {'class': 'main-content'})
                if about_content:
                    about_text = about_content.get_text(separator="\n", strip=True)
            except:
                continue

    return about_text, list(set(important_links))
