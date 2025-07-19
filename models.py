from pydantic import BaseModel
from typing import List, Optional

class FAQItem(BaseModel):
    question: str
    answer: str

class BrandContext(BaseModel):
    product_catalog: List[str]
    hero_products: List[str]
    privacy_policy: Optional[str]
    return_refund_policy: Optional[str]
    faqs: Optional[List[FAQItem]]
    social_handles: Optional[List[str]]
    contact_details: Optional[List[str]]
    about_brand: Optional[str]
    important_links: Optional[List[str]]
