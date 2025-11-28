def recommend_books(books):
    if not books:
        return []

    # Simple recommender based on categories
    category_count = {}
    for book in books:
        if book.get("categories"):
            for c in book["categories"]:
                category_count[c] = category_count.get(c, 0) + 1

    if not category_count:
        return []

    favorite_category = max(category_count, key=category_count.get)

    # Recommend books from same category
    recommendations = [b for b in books if b.get("categories") and favorite_category in b["categories"]]

    return recommendations[:5]