BOOK_KEYWORDS = ["книг", "посоветуй книг", "что почитать", "рекомендуй книг"]
GAME_KEYWORDS = ["игр", "посоветуй игр", "во что поиграть", "рекомендуй игр"]

STRESS_KEYWORDS = {
    "anxiety": ["тревог", "страх", "паник", "боюс", "волну", "беспоко"],
    "stress": ["стресс", "напряж", "перегруз", "устал", "выгорел"],
    "sadness": ["груст", "печал", "тоск", "депресс", "уныни", "плохое настроение"],
}

def contains_keywords(text: str, keywords_list):
    text_lower = text.lower()
    return any(kw in text_lower for kw in keywords_list)

def detect_stress_type(text: str) -> str:
    text_lower = text.lower()
    for stress_type, keywords in STRESS_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return stress_type
    return "general"