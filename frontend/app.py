import streamlit as st
import requests
from PIL import Image

st.set_page_config(page_title="ShelfScanner", page_icon="📚", layout="centered")

# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------
st.markdown("""
<style>

/* Fast animated header */
.hero-title {
    font-size: 42px;
    text-align: center;
    font-weight: 800;
    animation: fadeSlide 0.8s ease-out;
}

@keyframes fadeSlide {
    0% {opacity: 0; transform: translateY(-15px);}
    100% {opacity: 1; transform: translateY(0);}
}

/* Centering Scan Button */
.center-btn button {
    width: 230px !important;
    height: 55px !important;
    font-size: 20px !important;
    border-radius: 12px !important;
}

/* Yellow line separator */
.yellow-line {
    width: 100%;
    height: 3px;
    background: #FFD700;
    margin: 20px 0;
    border-radius: 4px;
}

/* Book text formatting */
.book-title {
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 5px;
}

.book-authors {
    font-size: 16px;
    opacity: 0.8;
}

/* Top-left theme toggle button */
#theme-toggle {
    position: fixed;
    top: 12px;
    left: 12px;
    background: transparent;
    border: none;
    font-size: 30px;
    cursor: pointer;
    z-index: 999;
}

</style>

<script>
function toggleTheme() {
    const root = window.parent.document.documentElement;
    const current = root.getAttribute("theme");
    const newTheme = current === "dark" ? "light" : "dark";
    root.setAttribute("theme", newTheme);
}
</script>

<button id="theme-toggle" onclick="toggleTheme()">🌞</button>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HERO HEADER
# --------------------------------------------------
st.markdown("<h1 class='hero-title'>📚 ShelfScanner</h1>", unsafe_allow_html=True)
st.write("Upload an image of your bookshelf and extract book information automatically.")

# --------------------------------------------------
# API URL
# --------------------------------------------------
API_BASE_URL = st.secrets["API_BASE_URL"]

# --------------------------------------------------
# SEARCH BAR (top, local search only)
# --------------------------------------------------
st.text_input("🔍 Search scanned books (local only)", "")

# --------------------------------------------------
# UPLOAD
# --------------------------------------------------
uploaded_file = st.file_uploader("Upload bookshelf image", type=["jpg", "jpeg", "png"])

# BUTTON CENTERING
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    scan_clicked = st.button("🔎 Scan Shelf", use_container_width=True)

# --------------------------------------------------
# PROCESS SCAN
# --------------------------------------------------
if uploaded_file and scan_clicked:

    st.markdown("<div class='yellow-line'></div>", unsafe_allow_html=True)

    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

    with st.spinner("⏳ Scanning... Extracting text from books..."):

        try:
            response = requests.post(
                f"{API_BASE_URL}/api/scan",
                files={"image": uploaded_file.getvalue()},
                timeout=400
            )

            if response.status_code != 200:
                st.error("API Error: " + response.text)
            else:
                data = response.json()

                # -------------------------------
                # Extracted Titles
                # -------------------------------
                st.subheader("📌 Extracted Titles")
                titles = data.get("extracted_titles", [])
                if titles:
                    st.write(titles)
                else:
                    st.warning("No readable text detected.")

                st.markdown("<div class='yellow-line'></div>", unsafe_allow_html=True)

                # -------------------------------
                # Books Found
                # -------------------------------
                st.subheader("📚 Books Found")
                books = data.get("books_found", [])

                if books:
                    for book in books:
                        # Title
                        st.markdown(f"<div class='book-title'>{book.get('title','N/A')}</div>", unsafe_allow_html=True)

                        # Authors
                        st.markdown(f"<div class='book-authors'>👤 {book.get('authors',['N/A'])}</div>", unsafe_allow_html=True)

                        # Categories
                        if book.get("categories"):
                            st.write(f"🏷 Categories: {book.get('categories')}")

                        # Thumbnail
                        if book.get("thumbnail"):
                            st.image(book["thumbnail"], width=140)

                        st.markdown("<div class='yellow-line'></div>", unsafe_allow_html=True)

                else:
                    st.warning("No books found.")

                # -------------------------------
                # Recommendations
                # -------------------------------
                recs = data.get("recommended", [])
                if recs:
                    st.subheader("⭐ Recommended Books")
                    for r in recs:
                        st.write(f"{r.get('title')}")
                        st.write(f"👤 {r.get('authors')}")
                        st.markdown("<div class='yellow-line'></div>", unsafe_allow_html=True)
                else:
                    st.info("No recommendations yet — scan more books!")

        except Exception as e:
            st.error(f"Error: {e}")