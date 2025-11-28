import os
import uvicorn
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import io
import requests

from db import get_books_collection
from recommender import recommend_books

# Google Vision API
from google.cloud import vision
from google.oauth2 import service_account

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
# GOOGLE VISION API SETUP
# ------------------------------------------------------
GOOGLE_CREDS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

if not GOOGLE_CREDS_PATH:
    raise Exception("❌ GOOGLE_APPLICATION_CREDENTIALS not set in Render variables!")

credentials = service_account.Credentials.from_service_account_file(
    GOOGLE_CREDS_PATH
)
vision_client = vision.ImageAnnotatorClient(credentials=credentials)


# ------------------------------------------------------
# OCR USING GOOGLE VISION API
# ------------------------------------------------------
def extract_text(image_bytes):
    try:
        image = vision.Image(content=image_bytes)
        response = vision_client.text_detection(image=image)

        if response.error.message:
            print("❌ Vision API Error:", response.error.message)
            return ""

        annotations = response.text_annotations
        if not annotations:
            return ""

        # Full extracted text
        return annotations[0].description

    except Exception as e:
        print("❌ Vision OCR failed:", e)
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
        "description": volume.get("description")
    }


# ------------------------------------------------------
# API: SCAN SHELF IMAGE
# ------------------------------------------------------
@app.post("/api/scan")
async def scan_shelf(image: UploadFile = File(...)):

    image_bytes = await image.read()

    # 1. OCR text
    extracted = extract_text(image_bytes)
    if not extracted.strip():
        return {"error": "Could not extract text from image."}

    # filter possible titles
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
# ROOT ROUTE
# ------------------------------------------------------
@app.get("/")
def root():
    return {"message": "ShelfScanner API running successfully with Google Vision OCR!"}


# ------------------------------------------------------
# LOCAL RUN
# ------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)