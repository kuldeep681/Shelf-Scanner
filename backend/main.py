import os
import uvicorn
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from PIL import Image
import easyocr
import numpy as np
import io
import requests

from db import get_books_collection
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
# GLOBAL EASYOCR READER (Loaded once → Fast!)
# ------------------------------------------------------
reader = easyocr.Reader(["en"], gpu=False)


# ------------------------------------------------------
# FAST OCR FUNCTION (No Tesseract, Resize Image)
# ------------------------------------------------------
def extract_text(image_bytes):

    # Load image
    img = Image.open(io.BytesIO(image_bytes))

    # Resize to speed up OCR
    max_size = 1024
    img.thumbnail((max_size, max_size), Image.LANCZOS)

    img_np = np.array(img)

    # OCR
    try:
        result = reader.readtext(img_np, detail=0)
        text = "\n".join(result)
        print("Extracted text:", text)
        return text
    except Exception as e:
        print("❌ EasyOCR failed:", e)
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
async def scan_shelf(image: UploadFile = File(...)):

    image_bytes = await image.read()

    # 1. Extract OCR text
    extracted = extract_text(image_bytes)
    if not extracted.strip():
        return {"error": "Could not extract text from image."}

    possible_titles = [
        line.strip() for line in extracted.split("\n")
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

    # 4. Recommendations
    recommendations = recommend_books(books)

    return {
        "extracted_titles": possible_titles,
        "books_found": books,
        "recommended": recommendations
    }


# ------------------------------------------------------
# Root Route
# ------------------------------------------------------
@app.get("/")
def root():
    return {"message": "ShelfScanner API running successfully!"}


# ------------------------------------------------------
# Run Server (local only)
# ------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)