import os
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import requests
from bson import ObjectId

from db import get_books_collection, get_bookmarks_collection
from recommender import recommend_books


load_dotenv()
app = FastAPI()

# ------------------------------------------------------
# CORS
# ------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------
# OCR.SPACE API
# ------------------------------------------------------
OCR_API_KEY = os.getenv("OCR_API_KEY")


def extract_text(image_bytes):
    url = "https://api.ocr.space/parse/image"
    files = {"file": ("image.jpg", image_bytes, "image/jpeg")}
    data = {
        "apikey": OCR_API_KEY,
        "language": "eng",
        "OCREngine": 2,
        "scale": True,
        "isTable": False,
        "detectOrientation": True
    }

    try:
        response = requests.post(url, files=files, data=data)
        result = response.json()

        if result.get("IsErroredOnProcessing"):
            return ""

        parsed = result["ParsedResults"][0]["ParsedText"]
        return parsed.strip()

    except Exception as e:
        print("OCR ERROR:", e)
        return ""


# ------------------------------------------------------
# GOOGLE BOOKS API
# ------------------------------------------------------
GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY", "")


def fetch_book_data(title):
    params = {"q": title, "maxResults": 1}
    if GOOGLE_BOOKS_API_KEY:
        params["key"] = GOOGLE_BOOKS_API_KEY

    res = requests.get("https://www.googleapis.com/books/v1/volumes", params=params)

    if res.status_code != 200:
        return None

    items = res.json().get("items")
    if not items:
        return None

    volume = items[0]["volumeInfo"]

    return {
        "title": volume.get("title"),
        "authors": volume.get("authors"),
        "thumbnail": volume.get("imageLinks", {}).get("thumbnail"),
        "categories": volume.get("categories"),
        "description": volume.get("description")
    }


# ------------------------------------------------------
# SCAN SHELF
# ------------------------------------------------------
@app.post("/api/scan")
async def scan_shelf(image: UploadFile = File(...)):
    image_bytes = await image.read()
    extracted = extract_text(image_bytes)

    if not extracted.strip():
        return {"error": "Could not extract text from image."}

    possible_titles = [
        line.strip()
        for line in extracted.split("\n")
        if len(line.strip()) > 3
    ]

    books = []
    for title in possible_titles:
        data = fetch_book_data(title)
        if data:
            books.append(data)

    collection = get_books_collection()
    if books:
        result = collection.insert_many(books)
        for idx, obj_id in enumerate(result.inserted_ids):
            books[idx]["_id"] = str(obj_id)

    recommendations = recommend_books(books)

    return {
        "extracted_titles": possible_titles,
        "books_found": books,
        "recommended": recommendations
    }


# ------------------------------------------------------
# ⭐ BOOKMARK: ADD
# ------------------------------------------------------
@app.post("/api/bookmark")
async def add_bookmark(book: dict):
    """
    {
        "user_id": "...",
        "title": "...",
        "authors": [...],
        "thumbnail": "...",
        "categories": [...],
        "description": "..."
    }
    """

    if "user_id" not in book:
        raise HTTPException(status_code=400, detail="user_id required")

    bookmarks = get_bookmarks_collection()
    inserted = bookmarks.insert_one(book)

    book["_id"] = str(inserted.inserted_id)
    return {"message": "Book bookmarked!", "bookmark": book}


# ------------------------------------------------------
# ⭐ BOOKMARK: GET ALL
# ------------------------------------------------------
@app.get("/api/bookmarks/{user_id}")
async def get_bookmarks(user_id: str):
    bookmarks = get_bookmarks_collection()

    docs = list(bookmarks.find({"user_id": user_id}))
    results = []

    for d in docs:
        d["_id"] = str(d["_id"])
        results.append(d)

    return {"bookmarks": results}


# ------------------------------------------------------
# ⭐ BOOKMARK: REMOVE ONE
# ------------------------------------------------------
@app.delete("/api/bookmark/{user_id}/{bookmark_id}")
async def remove_bookmark(user_id: str, bookmark_id: str):
    bookmarks = get_bookmarks_collection()

    try:
        result = bookmarks.delete_one({
            "_id": ObjectId(bookmark_id),
            "user_id": user_id
        })

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Bookmark not found")

        return {"message": "Bookmark removed"}

    except Exception:
        raise HTTPException(status_code=400, detail="Invalid bookmark ID")


# ------------------------------------------------------
# ⭐ BOOKMARK: CLEAR ALL
# ------------------------------------------------------
@app.delete("/api/bookmarks/clear/{user_id}")
async def clear_bookmarks(user_id: str):
    bookmarks = get_bookmarks_collection()
    deleted = bookmarks.delete_many({"user_id": user_id})

    return {"message": "All bookmarks cleared", "deleted": deleted.deleted_count}


# ------------------------------------------------------
# ROOT
# ------------------------------------------------------
@app.get("/")
def root():
    return {"message": "ShelfScanner API running with OCR + Bookmarks + Delete + Clear!"}


# ------------------------------------------------------
# LOCAL RUN
# ------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)