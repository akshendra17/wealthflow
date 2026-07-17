"""Categorizer service — assigns categories to transactions based on keyword matching."""

from __future__ import annotations

from typing import Optional, Dict, List
import structlog

logger = structlog.get_logger()

# Default category keywords — used to seed the database and for in-memory fallback.
# Key: category name, Value: list of keywords (matched case-insensitively against description)
DEFAULT_CATEGORIES: dict[str, dict] = {
    "Food": {
        "icon": "🍔",
        "color": "#ff6b6b",
        "keywords": [
            "swiggy", "zomato", "uber eats", "dominos", "pizza hut", "mcdonalds",
            "burger king", "kfc", "subway", "starbucks", "cafe", "restaurant",
            "dining", "food", "eat", "biryani", "meals", "doordash", "grubhub",
            "dunkin", "wendy", "taco bell", "chipotle", "panera",
        ],
    },
    "Grocery": {
        "icon": "🛒",
        "color": "#51cf66",
        "keywords": [
            "bigbasket", "blinkit", "zepto", "dmart", "reliance fresh", "grocery",
            "supermarket", "walmart", "costco", "trader joe", "whole foods",
            "kroger", "aldi", "target", "safeway", "publix", "more supermarket",
            "nature basket", "grofers", "jiomart", "instamart", "swiggy instamart",
        ],
    },
    "Loans": {
        "icon": "🏦",
        "color": "#ff922b",
        "keywords": [
            "loan", "home loan", "personal loan", "car loan", "vehicle loan",
            "education loan", "mortgage", "lending", "bajaj finserv", "hdfc loan",
            "sbi loan", "icici loan", "axis loan",
        ],
    },
    "EMI": {
        "icon": "💳",
        "color": "#f06595",
        "keywords": [
            "emi", "installment", "equated monthly", "no cost emi", "emi payment",
            "loan emi", "auto debit emi",
        ],
    },
    "Clothing": {
        "icon": "👕",
        "color": "#cc5de8",
        "keywords": [
            "myntra", "ajio", "zara", "h&m", "uniqlo", "pantaloons", "lifestyle",
            "max fashion", "westside", "fabindia", "clothing", "apparel", "fashion",
            "nike", "adidas", "puma", "levi", "gap", "old navy", "shein", "asos",
        ],
    },
    "Leisure": {
        "icon": "🎮",
        "color": "#339af0",
        "keywords": [
            "netflix", "spotify", "amazon prime", "hotstar", "disney", "youtube premium",
            "gaming", "steam", "playstation", "xbox", "movie", "pvr", "inox",
            "bookmyshow", "concert", "event", "entertainment", "hulu", "hbo",
            "apple music", "apple tv", "paramount",
        ],
    },
    "Shopping": {
        "icon": "🛍️",
        "color": "#20c997",
        "keywords": [
            "amazon", "flipkart", "meesho", "snapdeal", "ebay", "online shopping",
            "shopping", "electronics", "gadget", "croma", "reliance digital",
            "best buy", "apple store",
        ],
    },
    "Transport": {
        "icon": "🚗",
        "color": "#fcc419",
        "keywords": [
            "uber", "ola", "rapido", "metro", "bus", "train", "irctc", "petrol",
            "diesel", "fuel", "gas station", "parking", "toll", "lyft", "taxi",
            "cab", "auto rickshaw", "highway",
        ],
    },
    "Utilities": {
        "icon": "💡",
        "color": "#748ffc",
        "keywords": [
            "electricity", "water bill", "gas bill", "internet", "wifi", "broadband",
            "jio", "airtel", "vodafone", "bsnl", "mobile recharge", "phone bill",
            "dth", "tata sky", "cable", "utility",
        ],
    },
    "Health": {
        "icon": "🏥",
        "color": "#f783ac",
        "keywords": [
            "hospital", "doctor", "pharmacy", "medical", "medicine", "health",
            "clinic", "diagnostic", "lab test", "apollo", "fortis", "max hospital",
            "practo", "1mg", "pharmeasy", "netmeds", "dental", "eye care",
            "insurance premium", "health insurance",
        ],
    },
    "Rent": {
        "icon": "🏠",
        "color": "#e599f7",
        "keywords": [
            "rent", "house rent", "flat rent", "pg rent", "maintenance",
            "society maintenance", "apartment",
        ],
    },
    "Investments": {
        "icon": "📈",
        "color": "#38d9a9",
        "keywords": [
            "mutual fund", "sip", "zerodha", "groww", "upstox", "angel one",
            "investment", "stock", "shares", "nps", "ppf", "fixed deposit",
            "fd", "rd", "recurring deposit",
        ],
    },
    "Misc": {
        "icon": "📦",
        "color": "#859399",
        "keywords": [],
    },
}


def categorize_transaction(description: str, custom_keywords: Optional[Dict[str, List[str]]] = None) -> str:
    """Categorize a transaction based on its description.

    Uses keyword matching against the description. Returns the category name.
    Falls back to 'Misc' if no match is found.

    Args:
        description: The transaction description text.
        custom_keywords: Optional dict of {category_name: [keywords]} to override defaults.

    Returns:
        The matched category name (e.g., "Food", "Transport", "Misc").
    """
    desc_lower = description.lower()

    # Build keyword lookup: merge defaults with custom keywords
    categories = DEFAULT_CATEGORIES.copy()
    if custom_keywords:
        for cat_name, keywords in custom_keywords.items():
            if cat_name in categories:
                categories[cat_name]["keywords"] = list(
                    set(categories[cat_name]["keywords"]) | set(keywords)
                )
            else:
                categories[cat_name] = {"icon": "📦", "color": "#859399", "keywords": keywords}

    # Score each category by matching keywords
    best_match = "Misc"
    best_score = 0

    for cat_name, cat_data in categories.items():
        if cat_name == "Misc":
            continue
        for keyword in cat_data.get("keywords", []):
            if keyword.lower() in desc_lower:
                # Longer keyword matches are more specific, so score by length
                score = len(keyword)
                if score > best_score:
                    best_score = score
                    best_match = cat_name

    return best_match


def get_default_categories() -> dict[str, dict]:
    """Return the default category definitions for seeding."""
    return DEFAULT_CATEGORIES
