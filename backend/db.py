import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

# ------------------------------------------------------
# CONNECT TO MONGO
# ------------------------------------------------------
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "shelfscanner")

client = MongoClient(MONGODB_URI)
db = client[MONGODB_DB_NAME]


# ------------------------------------------------------
# BOOKS COLLECTION (Your existing function)
# ------------------------------------------------------
def get_books_collection():
    return db["books"]


# ------------------------------------------------------
# BOOKMARKS COLLECTION (NEW)
# ------------------------------------------------------
def get_bookmarks_collection():
    """
    Returns the MongoDB collection used to store user bookmarks.
    
    Each bookmarked document will look like:
    {
        "user_id": "user_xx82k",
        "title": "...",
        "authors": [...],
        "thumbnail": "...",
        "categories": [...],
        "description": "..."
    }
    """
    return db["bookmarks"]