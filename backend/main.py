import os
import uvicorn
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from PIL import Image
import pytesseract
import easyocr
import io
import requests

from db import get_books_collection
from recommender import recommend_books

load_dotenv()

app = FastAPI()

# ------------------------------------------------------
# CORS (Required for Streamlit Frontend)
# ------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------
# OCR Function with Tesseract → EasyOCR fallback
# ------------------------------------------------------
def extract_text(image_bytes):
    tesseract_cmd = os.getenv("TESSERACT_CMD")

    # Try Tesseract first
    try:
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

        img = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(img)

        if text.strip():
            return text

    except Exception as e:
        print("⚠ Tesseract failed, switching to EasyOCR:", e)

    # Fallback to EasyOCR
    try:
        reader = easyocr.Reader(['en'], gpu=False)
        result = reader.readtext(image_bytes, detail=0)
        return " ".join(result)

    except Exception as e:
        print("❌ EasyOCR also failed:", e)
        return ""


# ------------------------------------------------------
# Google Books API
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
        "description": volume.get("description")
    }


# ------------------------------------------------------
# API: Scan Shelf Image
# ------------------------------------------------------
@app.post("/api/scan")
async def scan_shelf(image: UploadFile = File(...), request: Request = None):

    image_bytes = await image.read()

    # 1. Extract text
    extracted_text = extract_text(image_bytes)
    if not extracted_text.strip():
        return {"error": "Could not extract text from image."}

    # 2. Process OCR lines into book titles
    possible_titles = [
        line.strip() for line in extracted_text.split("\n")
        if len(line.strip()) > 3
    ]

    # 3. Fetch book details
    books = []
    for title in possible_titles:
        data = fetch_book_data(title)
        if data:
            books.append(data)

    # 4. Save to MongoDB
    collection = get_books_collection()
    if books:
        result = collection.insert_many(books)
        ids = result.inserted_ids

        # Convert MongoDB ObjectId to string
        for idx, _id in enumerate(ids):
            books[idx]["_id"] = str(_id)

    # 5. Recommend books
    recommendations = recommend_books(books)

    # Final cleanup: ensure JSON-safe
    for book in books:
        if "_id" in book and not isinstance(book["_id"], str):
            book["_id"] = str(book["_id"])

    return {
        "extracted_titles": possible_titles,
        "books_found": books,
        "recommended": recommendations
    }

# ------------------------------------------------------
# Root Route (Test)
# ------------------------------------------------------
@app.get("/")
def root():
    return {"message": "ShelfScanner API running successfully!"}


# ------------------------------------------------------
# Run Backend
# ------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)