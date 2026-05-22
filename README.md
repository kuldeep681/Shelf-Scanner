# 📚 **ShelfScanner**

### _Scan Bookshelves → Discover Books → Save Your Favourites_

A modern, fast, AI-powered bookshelf scanner built using **FastAPI + Streamlit + MongoDB** with OCR-based text extraction and a beautiful user interface.

**👉 LIVE DEMO:** [https://shelf-scanner1122.streamlit.app/ ](https://shelf-scanner1122.streamlit.app/ ) 
**👉 GitHub Repo:** [https://github.com/kuldeep681/Shelf-Scanner](https://github.com/kuldeep681/Shelf-Scanner)

---

## 🎯 **Why ShelfScanner?**

Standing in front of a huge bookshelf, but don’t know any book?
ShelfScanner reads the entire bookshelf image, detects titles, fetches data, recommends books, and lets you bookmark your favourites — all in one smooth workflow.

**_Just upload → scan → explore._**

---

## ✨ **Key Features**

## 📸 **AI Shelf Scanner**

- Upload a photo of a bookshelf

- OCR extracts book titles from the image

- Automatically fetches details using Google Books API

## 🔍 **Smart Search**

- Search instantly through scanned books

- Instant filtering without reloading the page

## ⭐ **Bookmarks (No Login Required!)**

- Add books to "Your Bookmarks"

- Remove individual bookmarks

- Clear all bookmarks

- Uses session-based user ID

- Bookmarks stored in MongoDB per user session

## 🧠 **Simple Recommendations**

Basic content-based recommendation using categories + authors.
Lightweight and fast — no heavy ML required.

## 💛 **Beautiful UI**

- Animated golden header

- Yellow separators

- Clean card layout

- Sidebar showing real-time bookmarks

- Fully responsive layout

---

## 🧰 **Tech Stack**

## **- Frontend**

- Streamlit

- Python

- Custom CSS (animated gradients, styled cards)

## **- Backend**

- FastAPI

- Python

- OCR.Space API (for OCR extraction)

- Google Books API

## **- Database**

- MongoDB Atlas

## **- Collections:**

- books

- bookmarks

## **- Other Tools**

- UUID for user-based session IDs

- Requests library for API communication

---

## 📁 **Project Folder Structure**

```bash
shelfscanner/
│
├── backend/
│     ├── main.py            # FastAPI backend + OCR + API routes
│     ├── db.py              # MongoDB connection + collections
│     ├── recommender.py     # Recommendation logic
│     ├── requirements.txt   # Backend dependencies
│
├── frontend/
│     ├── .streamlit/        # Streamlit config (secrets.toml)
│     ├── app.py             # Streamlit UI
│     ├── requirements.txt   # Frontend dependencies
│
├── .gitignore
└── README.md                # Project documentation
```

---

## 🛠 **Local Development Setup**

Follow this to run the app locally.

---

## 🔧 1. Clone the Repository

```bash
git clone (https://github.com/kuldeep681/Shelf-Scanner.git)
cd shelfscanner
```

---

## 🐍 2. Backend Setup (FastAPI)\*\*

**Navigate:**

```bash
cd backend
```

**Install dependencies:**

```bash
pip install -r requirements.txt
```

**Run FastAPI:**

```bash
uvicorn main:app --reload --port 8000
```

FastAPI will run at:

👉 http://127.0.0.1:8000

---

## 🖥 **3. Frontend Setup (Streamlit)**

**Navigate:**

```bash
cd frontend
```

**Install dependencies:**

```bash
pip install -r requirements.txt
```

**Run Streamlit:**

```bash
streamlit run app.py
```

Streamlit will run at:

👉 http://localhost:8501

---

## 🌐 **Global Deployment**

I deployed using Render (Backend) + Streamlit Cloud (Frontend).

---

**🚀 A. Deploy Backend on Render**

1. Push code to GitHub

Render pulls from GitHub.

2. Create a Render Web Service

Select your repo

Start command:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

3. Add Environment Variables

```bash
OCR_API_KEY=your_api_key
GOOGLE_BOOKS_API_KEY=your_api_key
MONGODB_URI=your_mongodb_uri
```

4. Deploy

Render gives your backend URL like:

👉 [https://your-backend.onrender.com](https://your-backend.onrender.com)

Use this in Streamlit secrets.

---

**🚀 B. Deploy Frontend on Streamlit Cloud**

1. Go to share.streamlit.io

2. Select your GitHub repo

3. Add secrets:

```bash
API_BASE_URL="https://your-backend.onrender.com"
```

4. Deploy

Streamlit gives a link like:

👉 [https://your-shelfscanner.streamlit.app](https://your-shelfscanner.streamlit.app)

---

## 🔐 \*_Environment Variables Summary_

Backend .env / Render Variables

```bash
OCR_API_KEY=xxxx
GOOGLE_BOOKS_API_KEY=xxxx
MONGODB_URI=xxxx
```

Frontend Streamlit Secrets

```bash
API_BASE_URL="https://your-backend.onrender.com"
```

---

## 🧠 **How It Works (Simplified)**

1️⃣ **OCR detects titles**

Using OCR.Space API → returns extracted text.

2️⃣ **Text filtered into possible book names**

Simple line-based filtering.

3️⃣ **Google Books API fetches metadata**

Title → authors → categories → thumbnail → description.

4️⃣ **Recommendations generated**

Uses category + author similarity.

5️⃣ **User bookmarks stored**

Each user = a unique session ID saved in Streamlit memory.

6️⃣ **Bookmarks saved in MongoDB**

No login required.
Session persists until browser close.

---

## 📩 **Support**

If you face issues, feel free to reach out:

### 📧 **Email :** [kuldeepmandal175514@gmail.com](mailto:kuldeepmandal175514@gmail.com)

### 🐛 **Open a GitHub Issue**

---
