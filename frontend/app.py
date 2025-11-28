import streamlit as st
import requests
from PIL import Image
import io
import base64

# --------------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------------
st.set_page_config(
    page_title="ShelfScanner",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE_URL = st.secrets["API_BASE_URL"]

# --------------------------------------------------------
# SIDEBAR — Light/Dark Toggle
# --------------------------------------------------------
st.sidebar.header("🌗 Theme")
dark_mode = st.sidebar.toggle("Dark Mode", value=True)

if dark_mode:
    st.markdown("""
        <style>
            body, .stApp { background-color: #0e1117 !important; color: white !important; }
            .book-card { background-color: #1a1c23 !important; }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
            body, .stApp { background-color: #ffffff !important; color: black !important; }
            .book-card { background-color: #f9f9f9 !important; }
        </style>
    """, unsafe_allow_html=True)

# --------------------------------------------------------
# Custom Header Animation
# --------------------------------------------------------
header_html = """
<div style="
    width: 100%;
    text-align: center;
    font-size: 40px;
    font-weight: 800;
    margin-bottom: 10px;
    animation: slideIn 1.2s ease-out;
">
📚 ShelfScanner — Scan Your Bookshelf Instantly
</div>

<style>
@keyframes slideIn {
    0% { opacity: 0; transform: translateY(-25px); }
    100% { opacity: 1; transform: translateY(0px); }
}
</style>
"""
st.markdown(header_html, unsafe_allow_html=True)

# Yellow line separator
st.markdown(
    "<hr style='border: 0; height: 3px; background: #FFD700; margin-top: 5px;'>",
    unsafe_allow_html=True
)

# --------------------------------------------------------
# SEARCH BAR
# --------------------------------------------------------
search_query = st.text_input("🔎 Search scanned books", placeholder="Type book title... (local search only)")

# --------------------------------------------------------
# FILE UPLOAD SECTION
# --------------------------------------------------------
st.subheader("📤 Upload Bookshelf Image")

uploaded_file = st.file_uploader(
    "Upload a bookshelf image", 
    type=["jpg", "jpeg", "png"]
)

# Center Scan Button
col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    scan_button = st.button("📸 Scan Shelf", use_container_width=True)


# --------------------------------------------------------
# PROCESS IMAGE
# --------------------------------------------------------
books = []
if uploaded_file and scan_button:
    with st.spinner("⏳ Extracting text and scanning books..."):
        try:
            files = {"image": uploaded_file.getvalue()}

            response = requests.post(
                f"{API_BASE_URL}/api/scan",
                files=files,
                timeout=400
            )

            if response.status_code != 200:
                st.error("Error from API: " + response.text)
            else:
                data = response.json()

                extracted_titles = data.get("extracted_titles", [])
                books = data.get("books_found", [])
                recs = data.get("recommended", [])

                # ------------------------------------------------
                # SHOW EXTRACTED TITLES
                # ------------------------------------------------
                st.subheader("📝 Extracted Titles")
                if extracted_titles:
                    st.success(extracted_titles)
                else:
                    st.warning("No readable titles detected.")

                # ------------------------------------------------
                # SHOW BOOKS FOUND (Modern UI Cards)
                # ------------------------------------------------
                st.subheader("📚 Books Found")

                if books:
                    for book in books:

                        st.markdown(
                            f"""
                            <div class="book-card" style="
                                padding: 20px; 
                                border-radius: 12px; 
                                margin-bottom: 15px;
                            ">
                            """,
                            unsafe_allow_html=True,
                        )

                        cols = st.columns([1, 3])
                        with cols[0]:
                            if book.get("thumbnail"):
                                st.image(book["thumbnail"], width=130)

                        with cols[1]:
                            st.markdown(f"### {book.get('title')}")
                            st.write(f"*Authors:* {book.get('authors')}")
                            st.write(f"*Categories:* {book.get('categories')}")

                            if book.get("description"):
                                with st.expander("📖 Description"):
                                    st.write(book["description"])

                        st.markdown("</div>", unsafe_allow_html=True)

                else:
                    st.warning("No books matched.")

                # ------------------------------------------------
                # RECOMMENDED BOOKS (Only show if exists)
                # ------------------------------------------------
                if recs:
                    st.subheader("⭐ Recommended Books")
                    for r in recs:
                        st.markdown(
                            f"""
                            <div style="
                                padding: 15px; 
                                border-left: 5px solid #FFD700; 
                                margin-bottom: 10px;
                            ">
                                <b>{r.get('title')}</b><br>
                                {r.get('authors')}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

        except Exception as e:
            st.error(f"❌ Error: {e}")

# --------------------------------------------------------
# LOCAL SEARCH (No API calls)
# --------------------------------------------------------
if search_query and books:
    st.subheader("🔍 Search Results")
    filtered = [b for b in books if search_query.lower() in b["title"].lower()]

    if filtered:
        st.write(filtered)
    else:
        st.warning("No match found in scanned books.")