from urllib.parse import quote_plus

CATALOG = {
    "home": [
        ("Amazon", "LED ceiling light", "lighting", 1299), ("IKEA", "LACK side table", "furniture", 2490),
        ("Amazon", "Ceiling fan", "fan", 3299), ("IKEA", "LISABO dining table", "dining", 14990),
        ("Amazon", "Decorative wall art set", "decor", 1599), ("IKEA", "KALLAX shelf unit", "storage", 7990),
        ("Amazon", "Memory foam mattress", "bedroom", 8999), ("IKEA", "HEKTAR floor lamp", "lighting", 4490),
        ("Amazon", "Curtain set", "decor", 1199), ("IKEA", "POÄNG armchair", "seating", 6990),
    ],
    "party": [
        ("Swiggy", "Catering package", "catering", 350), ("Zomato", "Party food combo", "catering", 280),
        ("OYO", "Guest accommodation", "accommodation", 1800), ("Amazon", "Balloon decoration kit", "decoration", 899),
        ("Amazon", "Party speaker", "entertainment", 2999), ("Amazon", "LED party lights", "decoration", 1299),
        ("Zomato", "Dessert platter", "dessert", 950), ("Swiggy", "Beverage package", "beverages", 700),
    ],
    "jewelry": [
        ("Amazon", "Gold-tone statement earrings", "earrings", 899), ("Flipkart", "Kundan necklace set", "necklace", 1899),
        ("Amazon", "Pearl drop earrings", "earrings", 1299), ("Flipkart", "Minimal pendant", "necklace", 999),
        ("Amazon", "Bangle set", "bangles", 749), ("Flipkart", "Oxidized silver jhumka", "earrings", 699),
        ("Amazon", "Crystal bracelet", "bracelet", 799), ("Flipkart", "Artificial bridal necklace", "necklace", 2499),
    ],
}

def candidate_items(planner: str, terms: list[str] | None = None) -> list[dict]:
    terms = [t.lower() for t in (terms or [])]
    rows = []
    for platform, name, category, price in CATALOG[planner]:
        hay = f"{name} {category} {platform}".lower()
        score = sum(1 for t in terms if t and t in hay)
        rows.append({"platform": platform, "name": name, "category": category, "price": float(price), "score": score})
    rows.sort(key=lambda x: (-x["score"], x["price"]))
    return rows

def search_url(platform: str, name: str) -> str:
    q = quote_plus(name)
    hosts = {"Amazon": f"https://www.amazon.in/s?k={q}", "Flipkart": f"https://www.flipkart.com/search?q={q}", "IKEA": f"https://www.ikea.com/in/en/search/?q={q}", "Swiggy": f"https://www.swiggy.com/search?query={q}", "Zomato": f"https://www.zomato.com/search?query={q}", "OYO": f"https://www.oyorooms.com/search?location={q}"}
    return hosts.get(platform, f"https://www.google.com/search?q={q}")
