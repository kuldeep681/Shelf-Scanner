import os
import uvicorn
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import requests

from db import get_books_collection
from recommender import recommend_books

load_dotenv()

app = FastAPI()

# ------------------------------------------------------
# CORS (Allow Streamlit Frontend)
# ------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------
# OCR.SPACE API SETUP
# ------------------------------------------------------
OCR_API_KEY = os.getenv("OCR_API_KEY")

if not OCR_API_KEY:
    raise Exception("❌ OCR_API_KEY not found! Add it to Render environment variables.")


def extract_text(image_bytes):
    """
    Extract text from image using OCR.Space Free Cloud API.
    """
    url = "https://api.ocr.space/parse/image"

    try:
        response = requests.post(
            url,
            files={"file": ("image.jpg", image_bytes)},
            data={"apikey": OCR_API_KEY, "language": "eng"},
        )

        result = response.json()

        if result.get("IsErroredOnProcessing"):
            print("OCR error:", result.get("ErrorMessage"))
            return ""

        parsed = result["ParsedResults"][0]["ParsedText"]
        return parsed

    except Exception as e:
        print("❌ OCR.Space API failed:", e)
        return ""


# ------------------------------------------------------
# GOOGLE BOOKS API
# ------------------------------------------------------
GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY", "")

def fetch_book_data(title):
    params = {"q": title, "maxResults": 1}
    if GOOGLE_BOOKS_API_KEY:
        params["key"] = GOOGLE_BOOKS_API_KEY

    url = "https://www.googleapis.com/books/v1/volumes"
    res = requests.get(url, params=params)

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
        "description": volume.get("description"),
    }


# ------------------------------------------------------
# API: SCAN IMAGE
# ------------------------------------------------------
@app.post("/api/scan")
async def scan_shelf(image: UploadFile = File(...)):

    image_bytes = await image.read()

    # 1. OCR text
    extracted = extract_text(image_bytes)

    if not extracted.strip():
        return {"error": "Could not extract text from image."}

    # clean titles
    possible_titles = [
        line.strip()
        for line in extracted.split("\n")
        if len(line.strip()) > 3
    ]

    # 2. Fetch book details
    books = []
    for title in possible_titles:
        data = fetch_book_data(title)
        if data:
            books.append(data)

    # 3. Save to MongoDB
    collection = get_books_collection()
    if books:
        result = collection.insert_many(books)
        ids = result.inserted_ids
        for idx, _id in enumerate(ids):
            books[idx]["_id"] = str(_id)

    # 4. Recommend books
    recommendations = recommend_books(books)

    return {
        "extracted_titles": possible_titles,
        "books_found": books,
        "recommended": recommendations,
    }


# ------------------------------------------------------
# Root Test Route
# ------------------------------------------------------
@app.get("/")
def root():
    return {"message": "ShelfScanner API running with OCR.Space Cloud OCR!"}


# ------------------------------------------------------
# Local Dev
# ------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)