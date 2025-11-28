import requests

GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"

def recommend_books(scanned_books, max_results=5):
    """
    Recommend books based on categories from scanned books.
    """

    # -------------------------------------------
    # 1️⃣ Collect all categories from scanned books
    # -------------------------------------------
    categories = set()
    for book in scanned_books:
        cats = book.get("categories")
        if cats:
            for c in cats:
                if isinstance(c, str):
                    categories.add(c)
    
    # If no categories found → return empty recommendations
    if not categories:
        return []

    category_list = list(categories)

    # -------------------------------------------
    # 2️⃣ Pick BEST category (first most common)
    # -------------------------------------------
    main_category = category_list[0]

    # -------------------------------------------
    # 3️⃣ Query Google Books API for recommendations
    # -------------------------------------------
    params = {
        "q": f"subject:{main_category}",
        "maxResults": max_results
    }

    try:
        res = requests.get(GOOGLE_BOOKS_API_URL, params=params)
        if res.status_code != 200:
            return []

        items = res.json().get("items", [])
        recommendations = []

        # -------------------------------------------
        # 4️⃣ Format final recommended books
        # -------------------------------------------
        for item in items:
            info = item.get("volumeInfo", {})
            recommendations.append({
                "title": info.get("title"),
                "authors": info.get("authors"),
                "thumbnail": info.get("imageLinks", {}).get("thumbnail"),
                "categories": info.get("categories"),
                "description": info.get("description"),
            })

        return recommendations

    except Exception as e:
        print("Recommendation error:", e)
        return []