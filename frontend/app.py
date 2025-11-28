import streamlit as st
import requests
from PIL import Image
import io

# ---------------------------------------------------
# Streamlit Page Setup
# ---------------------------------------------------
st.set_page_config(page_title="ShelfScanner", page_icon="📚", layout="wide")

API_BASE_URL = st.secrets["API_BASE_URL"]

# ---------------------------------------------------
# Add CSS + JS for Shutterstock-style Toggle (Sun/Moon)
# ---------------------------------------------------
TOGGLE_CSS = """
<style>
:root {
    --light-bg: #f5f5f5;
    --dark-bg: #0d1117;
    --yellow-line: #f1c40f;
    --toggle-light: #e8e8e8;
    --toggle-dark: #2b2d3a;
}

/* Body themes */
body[data-theme="light"] {
    background-color: var(--light-bg) !important;
    color: black !important;
}
body[data-theme="dark"] {
    background-color: var(--dark-bg) !important;
    color: white !important;
}

/* Yellow separator line */
.separator {
    width: 100%;
    height: 3px;
    background: var(--yellow-line);
    margin: 20px 0;
}

/* Hero animated text */
.hero {
    font-size: 48px;
    font-weight: 900;
    text-align: center;
    margin-top: 40px;
    background: linear-gradient(90deg, #ffdd00, #ff9900, #ffdd00);
    background-size: 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: flow 3s infinite linear;
}
@keyframes flow {
    0% { background-position: 0%; }
    100% { background-position: 300%; }
}

/* Pretty Book Card */
.book-card {
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 10px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
}
</style>
"""

TOGGLE_JS = """
<script>
function switchTheme() {
    var body = window.parent.document.body;
    var circle = window.parent.document.getElementById("toggleCircle");

    var current = body.getAttribute("data-theme");

    if (current === "light") {
        body.setAttribute("data-theme", "dark");
        circle.style.transform = "translateX(32px)";
        circle.innerHTML = "🌙";
    } else {
        body.setAttribute("data-theme", "light");
        circle.style.transform = "translateX(0px)";
        circle.innerHTML = "☀";
    }
}
</script>
"""

TOGGLE_HTML = """
<div onclick="switchTheme()" style="
    position: fixed;
    top: 20px;
    left: 20px;
    width: 70px;
    height: 32px;
    border-radius: 50px;
    background: var(--toggle-dark);
    display: flex;
    align-items: center;
    padding: 3px;
    cursor: pointer;
    z-index: 9999;
">
    <!-- Sun faint -->
    <div style="
        position: absolute;
        left: 10px;
        font-size: 16px;
        opacity: 0.2;
    ">☀</div>

    <!-- Moon faint -->
    <div style="
        position: absolute;
        right: 10px;
        font-size: 16px;
        opacity: 1;
    ">🌙</div>

    <!-- Sliding circle -->
    <div id="toggleCircle" style="
        width: 28px;
        height: 28px;
        background: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: transform 0.3s;
        font-size: 16px;
        transform: translateX(32px);
    ">🌙</div>
</div>
"""

# Inject CSS + HTML + JS
st.markdown(TOGGLE_CSS, unsafe_allow_html=True)
st.markdown(TOGGLE_JS + TOGGLE_HTML, unsafe_allow_html=True)

# Default theme is dark
st.markdown("""
<script>
window.parent.document.body.setAttribute("data-theme","dark");
</script>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# HERO HEADER
# ---------------------------------------------------
st.markdown("<div class='hero'>📚 ShelfScanner</div>", unsafe_allow_html=True)

# Yellow line
st.markdown("<div class='separator'></div>", unsafe_allow_html=True)

# ---------------------------------------------------
# SEARCH BAR (no backend needed)
# ---------------------------------------------------
search_query = st.text_input("🔍 Search scanned books", "")

# ---------------------------------------------------
# Layout for Upload + Scan
# ---------------------------------------------------
col1, col2, col3 = st.columns([1.5, 2, 1])

with col2:
    uploaded_file = st.file_uploader(
        "Upload Bookshelf Image",
        type=["jpg", "jpeg", "png"],
        help="Upload one image of your bookshelf"
    )

    scan_btn = st.button("🔎 Scan Shelf", use_container_width=True)

# ---------------------------------------------------
# When Scan Button Clicked
# ---------------------------------------------------
if uploaded_file and scan_btn:
    st.markdown("<div class='separator'></div>", unsafe_allow_html=True)

    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

    with st.spinner("📡 Scanning shelf... Please wait..."):
        try:
            files = {"image": uploaded_file.getvalue()}
            response = requests.post(
                f"{API_BASE_URL}/api/scan",
                files=files,
                timeout=300
            )

            if response.status_code != 200:
                st.error("❌ API Error: " + response.text)
            else:
                data = response.json()

                # ---------------------
                # Extracted Titles
                # ---------------------
                st.subheader("📌 Extracted Titles")
                titles = data.get("extracted_titles", [])
                st.write(titles if titles else "No readable titles.")

                st.markdown("<div class='separator'></div>", unsafe_allow_html=True)

                # ---------------------
                # Books Found (Cards UI)
                # ---------------------
                books = data.get("books_found", [])

                st.subheader("📚 Books Found")
                if books:
                    for book in books:
                        with st.container():
                            st.markdown("<div class='book-card'>", unsafe_allow_html=True)

                            cols = st.columns([1, 4])
                            with cols[0]:
                                if book.get("thumbnail"):
                                    st.image(book["thumbnail"], width=100)

                            with cols[1]:
                                st.markdown(f"### {book.get('title','N/A')}")
                                st.write(f"*Authors:* {book.get('authors',['N/A'])}")
                                st.write(f"*Categories:* {book.get('categories',['N/A'])}")

                                if book.get("description"):
                                    with st.expander("📘 Description"):
                                        st.write(book["description"])

                            st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.warning("No matching books found.")

                st.markdown("<div class='separator'></div>", unsafe_allow_html=True)

                # ---------------------
                # Recommendations
                # ---------------------
                recs = data.get("recommended", [])
                st.subheader("⭐ Recommended Books")

                if recs:
                    for r in recs:
                        st.write(f"### {r.get('title')}")
                        st.write(f"*Authors:* {r.get('authors')}")
                        st.markdown("---")
                else:
                    st.info("No recommendations yet.")

        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")