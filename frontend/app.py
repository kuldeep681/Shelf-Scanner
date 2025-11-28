import streamlit as st
import requests
from PIL import Image

st.set_page_config(page_title="ShelfScanner", page_icon="📚", layout="wide")

API_BASE_URL = st.secrets["API_BASE_URL"]

# ---------------------------------------------------
# GLOBAL UI CSS (no theme toggle)
# ---------------------------------------------------
st.markdown("""
<style>

:root {
    --yellow-line: #f1c40f;
}

/* Remove top padding */
section.main > div {padding-top: 0 !important;}

/* Page background */
body {
    background-color: #0d1117 !important;
    color: #eee !important;
}

/* Yellow separator line */
.separator {
    width: 100%;
    height: 3px;
    background: var(--yellow-line);
    margin: 25px 0;
}

/* Animated Header */
.hero {
    font-size: 55px;
    font-weight: 900;
    text-align: center;
    margin-top: 5px;
    background: linear-gradient(90deg, #ffdd00, #ff9900, #ffdd00);
    background-size: 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: flow 1.2s linear infinite;
}
@keyframes flow {
    0% {background-position: 0%;}
    100% {background-position: 300%;}
}

/* Book card */
.book-card {
    border-radius: 15px;
    padding: 18px;
    margin-bottom: 12px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# HEADER
# ---------------------------------------------------
st.markdown("<div class='hero'>📚 ShelfScanner</div>", unsafe_allow_html=True)
st.markdown("<div class='separator'></div>", unsafe_allow_html=True)

# ---------------------------------------------------
# SEARCH BAR
# ---------------------------------------------------
search = st.text_input("🔍 Search scanned books", "")

# ---------------------------------------------------
# UPLOAD SECTION
# ---------------------------------------------------
col1, col2, col3 = st.columns([1,2,1])
with col2:
    uploaded_img = st.file_uploader("Upload bookshelf image", type=["jpg", "jpeg", "png"])
    scan_btn = st.button("🔎 Scan Shelf", use_container_width=True)

# ---------------------------------------------------
# SCAN LOGIC
# ---------------------------------------------------
if uploaded_img and scan_btn:
    st.image(uploaded_img, caption="Uploaded Image", use_column_width=True)

    with st.spinner("Scanning... ⏳✨"):
        try:
            files = {"image": uploaded_img.getvalue()}
            res = requests.post(f"{API_BASE_URL}/api/scan", files=files, timeout=300)

            if res.status_code != 200:
                st.error("API Error: " + res.text)

            data = res.json()

            # Extracted Titles
            st.subheader("📌 Extracted Titles")
            st.write(data.get("extracted_titles", []))

            st.markdown("<div class='separator'></div>", unsafe_allow_html=True)

            # Books Found
            st.subheader("📚 Books Found")
            books = data.get("books_found", [])

            if books:
                for book in books:
                    st.markdown("<div class='book-card'>", unsafe_allow_html=True)
                    b1, b2 = st.columns([1,4])

                    with b1:
                        if book.get("thumbnail"):
                            st.image(book["thumbnail"], width=100)

                    with b2:
                        st.markdown(f"### {book.get('title')}")
                        st.write("*Authors:*", book.get("authors"))
                        st.write("*Categories:*", book.get("categories"))

                        if book.get("description"):
                            with st.expander("📘 Description"):
                                st.write(book["description"])

                    st.markdown("</div>", unsafe_allow_html=True)

            else:
                st.warning("No matching books found.")

            # Recommended Books
            st.subheader("⭐ Recommended Books")
            recs = data.get("recommended", [])

            if recs:
                for r in recs:
                    st.write(f"### {r['title']}")
                    st.write(r.get("authors"))
            else:
                st.info("No recommendations yet.")

        except Exception as e:
            st.error(f"Error: {e}")