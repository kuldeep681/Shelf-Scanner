import streamlit as st
import requests
from PIL import Image

# ------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------
st.set_page_config(
    page_title="ShelfScanner",
    page_icon="📚",
    layout="wide"
)

# ------------------------------------------------------------
# THEME STATE
# ------------------------------------------------------------
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

theme = st.session_state.theme

# ------------------------------------------------------------
# SUN-MOON TOGGLE (TOP LEFT)
# ------------------------------------------------------------
toggle_html = f"""
<div class="toggle-container" onclick="toggleTheme()">
    <div class="toggle-circle"></div>
    <div class="sun">☀</div>
    <div class="moon">🌙</div>
</div>

<script>
function toggleTheme() {{
    window.parent.postMessage({{"themeToggle": true}}, "*");
}}
</script>
"""

st.markdown(toggle_html, unsafe_allow_html=True)

# Handle toggle event
if "_theme_triggered" not in st.session_state:
    st.session_state._theme_triggered = False

# JS → Streamlit hack
theme_toggle = st.session_state._theme_triggered
if "themeToggle" in st.session_state:
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
    st.session_state._theme_triggered = False
    st.experimental_rerun()


# ------------------------------------------------------------
# CUSTOM CSS FOR THEMES + TOGGLE
# ------------------------------------------------------------
st.markdown(f"""
<style>

/* Background */
body {{
    background-color: {"#0d0d0d" if theme=='dark' else "#ffffff"};
}}

/* Hero Header Animation */
@keyframes float {{
  0% {{transform: translateY(0px);}}
  50% {{transform: translateY(-5px);}}
  100% {{transform: translateY(0px);}}
}}

.hero {{
    animation: float 3s ease-in-out infinite;
    text-align: center;
}}

.hero h1 {{
    font-size: 55px;
    font-weight: 800;
    margin-top: -10px;
    color: {"#ffdd33" if theme=='dark' else "#333"};
}}

/* Toggle Switch */
.toggle-container {{
    position: fixed;
    top: 15px;
    left: 15px;
    width: 60px;
    height: 28px;
    background: {"#444" if theme=='dark' else "#ddd"};
    border-radius: 20px;
    cursor: pointer;
    display: flex;
    align-items: center;
    padding: 3px;
    transition: background 0.3s;
    z-index: 99999;
}}

.toggle-circle {{
    width: 22px;
    height: 22px;
    border-radius: 50%;
    background: {"#ffdd33" if theme=='light' else "#ffffff"};
    transform: translateX({0 if theme=='dark' else 32}px);
    transition: transform 0.3s ease, background 0.3s;
}}

.sun {{
    position: absolute;
    left: 6px;
    font-size: 15px;
    opacity: {0 if theme=='dark' else 1};
    transition: opacity 0.3s;
}}

.moon {{
    position: absolute;
    right: 6px;
    font-size: 15px;
    opacity: {1 if theme=='dark' else 0};
    transition: opacity 0.3s;
}}

/* Book Cards */
.book-card {{
    padding: 18px;
    background-color: {"#1c1c1c" if theme=='dark' else "#f5f5f5"};
    border-radius: 12px;
    border: 1px solid {"#333" if theme=='dark' else "#ddd"};
    margin-bottom: 18px;
}}

.separator {{
    border-top: 2px solid #ffdd33;
    margin-top: 25px;
    margin-bottom: 25px;
}}

/* Center the scan button */
.scan-btn {{
    display: flex;
    justify-content: center;
    margin-top: 10px;
}}

</style>
""", unsafe_allow_html=True)


# -------------------------------------------------------------------
# SECRET BASE URL
# -------------------------------------------------------------------
API_BASE_URL = st.secrets["API_BASE_URL"]

# -------------------------------------------------------------------
# HERO HEADER
# -------------------------------------------------------------------
st.markdown("""
<div class="hero">
    <h1>📚 ShelfScanner</h1>
    <p style="font-size:18px; opacity:0.9;">Scan your bookshelf. Discover books. Get recommendations.</p>
</div>
""", unsafe_allow_html=True)


# -------------------------------------------------------------------
# SEARCH BAR (TOP)
# -------------------------------------------------------------------
search_query = st.text_input("🔍 Search inside scanned results (local search)", "")


# -------------------------------------------------------------------
# FILE UPLOAD
# -------------------------------------------------------------------
uploaded_file = st.file_uploader(
    "Upload a bookshelf image",
    type=["jpg", "jpeg", "png"]
)

# Centered scan button
if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

    if st.button("🔍 Scan Shelf", key="scan", help="Extract book titles", type="primary"):
        with st.spinner("🌀 Scanning your shelf... Please wait..."):

            try:
                files = {"image": uploaded_file.getvalue()}
                response = requests.post(
                    f"{API_BASE_URL}/api/scan",
                    files=files,
                    timeout=200
                )

                if response.status_code != 200:
                    st.error("Error from API: " + response.text)

                else:
                    data = response.json()

                    # ---------------------------------------------
                    # Extracted Titles
                    # ---------------------------------------------
                    st.markdown("<div class='separator'></div>", unsafe_allow_html=True)
                    st.subheader("📌 Extracted Titles")
                    titles = data.get("extracted_titles", [])

                    if titles:
                        st.write(titles)
                    else:
                        st.warning("No readable titles found.")

                    # ---------------------------------------------
                    # BOOKS FOUND
                    # ---------------------------------------------
                    st.markdown("<div class='separator'></div>", unsafe_allow_html=True)
                    st.subheader("📚 Books Found")

                    books = data.get("books_found", [])

                    # Apply search filter
                    if search_query:
                        books = [
                            b for b in books
                            if search_query.lower() in (b.get("title","").lower())
                        ]

                    if books:
                        for book in books:
                            st.markdown('<div class="book-card">', unsafe_allow_html=True)
                            st.write(f"*Title:* {book.get('title','N/A')}")
                            st.write(f"*Authors:* {book.get('authors',['N/A'])}")
                            st.write(f"*Categories:* {book.get('categories',['N/A'])}")
                            if book.get("thumbnail"):
                                st.image(book["thumbnail"], width=120)
                            st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.info("No books match your search.")

                    # ---------------------------------------------
                    # RECOMMENDATIONS
                    # ---------------------------------------------
                    recs = data.get("recommended", [])

                    if recs:
                        st.markdown("<div class='separator'></div>", unsafe_allow_html=True)
                        st.subheader("⭐ Recommended Books")

                        for r in recs:
                            st.markdown('<div class="book-card">', unsafe_allow_html=True)
                            st.write(f"*Title:* {r.get('title')}")
                            st.write(f"*Authors:* {r.get('authors')}")
                            st.markdown('</div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"An error occurred: {e}")