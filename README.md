# 📚 **ShelfScanner**

### _Scan Bookshelves → Discover Books → Save Your Favourites_

A modern, fast, AI-powered bookshelf scanner built using **FastAPI + Streamlit + MongoDB** with OCR-based text extraction and a beautiful user interface.

**👉 LIVE DEMO:** https://shelf-scanner1122.streamlit.app/
**👉 GitHub Repo:** https://github.com/kuldeep681/Shelf-Scanner.git

---

## 🎯 **Why ShelfScanner?**

Standing in front of a huge bookshelf, but don’t know any book?
ShelfScanner reads the entire bookshelf image, detects titles, fetches data, recommends books, and lets you bookmark your favourites — all in one smooth workflow.

**_Just upload → scan → explore._**

---

## ✨ **Key Features**

### 📸 **AI Shelf Scanner**

- Upload a photo of a bookshelf

- OCR extracts book titles from the image

- Automatically fetches details using Google Books API

### 🔍 **Smart Search**

- Search instantly through scanned books

- Instant filtering without reloading the page

### ⭐ **Bookmarks (No Login Required!)**

- Add books to "Your Bookmarks"

- Remove individual bookmarks

- Clear all bookmarks

- Uses session-based user ID

- Bookmarks stored in MongoDB per user session

### 🧠 **Simple Recommendations**

Basic content-based recommendation using categories + authors.
Lightweight and fast — no heavy ML required.

### 💛 **Beautiful UI**

- Animated golden header

- Yellow separators

- Clean card layout

- Sidebar showing real-time bookmarks

- Fully responsive layout

---

## 🧰 **Tech Stack**

**- Frontend**

- Streamlit

- Python

- Custom CSS (animated gradients, styled cards)

**- Backend**

- FastAPI

- Python

- OCR.Space API (for OCR extraction)

- Google Books API

**- Database**

- MongoDB Atlas

**- Collections:**

- books

- bookmarks

**- Other Tools**

- UUID for user-based session IDs

- Requests library for API communication

---

## 📁 **Project Folder Structure**

```bash
shelfscanner/
│
├── backend/
│ ├── main.py # FastAPI backend + OCR + Routes
│ ├── db.py # MongoDB connection + collections
│ ├── recommender.py # Book recommendation logic
│ ├── requirements.txt # Python packages for backend
│
├── frontend/
│ ├── app.py # Streamlit UI
│ ├── requirements.txt # Python packages for frontend
│
├── .gitignore
├── README.md # This file
└── images/ # (Optional) Screenshots for README
```

---

🛠 Local Development Setup

Follow this to run the app locally.

---

🔧 1. Clone the Repository

git clone <repo-url>
cd shelfscanner

---

🐍 2. Backend Setup (FastAPI)

Navigate:

cd backend

Install dependencies:

pip install -r requirements.txt

Run FastAPI:

uvicorn main:app --reload --port 8000

FastAPI will run at:

👉 http://127.0.0.1:8000

---

🖥 3. Frontend Setup (Streamlit)

Navigate:

cd ../frontend

Install dependencies:

pip install -r requirements.txt

Run Streamlit:

streamlit run app.py

Streamlit will run at:

👉 http://localhost:8501

---

🌐 Global Deployment

You deployed using Render (Backend) + Streamlit Cloud (Frontend).

---

🚀 A. Deploy Backend on Render

1. Push code to GitHub

Render pulls from GitHub.

2. Create a Render Web Service

Select your repo

Start command:

uvicorn main:app --host 0.0.0.0 --port $PORT

3. Add Environment Variables

OCR_API_KEY=your_api_key
GOOGLE_BOOKS_API_KEY=your_api_key
MONGODB_URI=your_mongodb_uri

4. Deploy

Render gives your backend URL like:

👉 https://your-backend.onrender.com

Use this in Streamlit secrets.

---

🚀 B. Deploy Frontend on Streamlit Cloud

1. Go to share.streamlit.io

2. Select your GitHub repo

3. Add secrets:

API_BASE_URL="https://your-backend.onrender.com"

4. Deploy

Streamlit gives a link like:

👉 https://your-shelfscanner.streamlit.app

Paste this link at the top of README.

---

🔐 Environment Variables Summary

Backend .env / Render Variables

OCR_API_KEY=xxxx
GOOGLE_BOOKS_API_KEY=xxxx
MONGODB_URI=xxxx

Frontend Streamlit Secrets

API_BASE_URL="https://your-backend.onrender.com"

---

🧠 How It Works (Simplified)

1️⃣ OCR detects titles

Using OCR.Space API → returns extracted text.

2️⃣ Text filtered into possible book names

Simple line-based filtering.

3️⃣ Google Books API fetches metadata

Title → authors → categories → thumbnail → description.

4️⃣ Recommendations generated

Uses category + author similarity.

5️⃣ User bookmarks stored

Each user = a unique session ID saved in Streamlit memory.

6️⃣ Bookmarks saved in MongoDB

No login required.
Session persists until browser close.

---

🌟 Screenshots & Demo

(Add your screenshots here later — via GitHub issues or local images)

Example placeholder:

![App Screenshot](https://raw.githubusercontent.com/<your-username>/<repo>/main/images/screenshot1.png)

---

📩 Support

If you face issues, feel free to reach out:

📧 Your Email Here
🐛 Open a GitHub Issue

---

❤ Built With Love

This project was created to help make discovering books easier, faster, and more enjoyable.

---

✅ Your README is now:

✔ Beautiful
✔ Creative
✔ Detailed
✔ Easy to understand
✔ Includes folder structure
✔ Includes deployment instructions
✔ Includes code snippets

---

If you want, I can also create:
✔ A badge-section (Python / FastAPI / Streamlit / MongoDB)
✔ GIF demo
✔ A professional logo
✔ Auto-generated docs

Just tell me!
