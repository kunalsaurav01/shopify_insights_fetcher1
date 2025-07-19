from fastapi import FastAPI, HTTPException
from scraper import *
from models import BrandContext, FAQItem
from bs4 import BeautifulSoup

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Shopify Insights Fetcher API running."}

@app.get("/fetch_insights/", response_model=BrandContext)
def fetch_insights(website_url: str):
    try:
        html = fetch_html(website_url)
        soup = BeautifulSoup(html, 'lxml')

        product_catalog = extract_product_catalog(website_url)
        hero_products = extract_hero_products(soup)
        privacy_policy = extract_text_from_policy_page(website_url, "privacy-policy")
        return_refund_policy = extract_text_from_policy_page(website_url, "refund-policy")
        faqs_raw = extract_faqs(soup)
        faqs = [FAQItem(**faq) for faq in faqs_raw]
        social_handles = extract_social_links(soup)
        contact_details = extract_contact_details(soup)
        about_brand, important_links = extract_about_and_links(soup)

        return BrandContext(
            product_catalog=product_catalog,
            hero_products=hero_products,
            privacy_policy=privacy_policy,
            return_refund_policy=return_refund_policy,
            faqs=faqs if faqs else None,
            social_handles=social_handles,
            contact_details=contact_details,
            about_brand=about_brand,
            important_links=important_links
        )

    except Exception as e:
        error_message = str(e)
        if "404" in error_message:
            raise HTTPException(status_code=401, detail="Website not found.")
        else:
            raise HTTPException(status_code=500, detail="Internal server error.")
