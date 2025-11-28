import streamlit as st
import requests
from PIL import Image

st.set_page_config(page_title="ShelfScanner", page_icon="📚", layout="wide")

API_BASE_URL = st.secrets["API_BASE_URL"]

# ---------------------------------------------------
# GLOBAL CSS (Fix toggle, remove purple box)
# ---------------------------------------------------
st.markdown("""
<style>

:root {
    --yellow-line: #f1c40f;
    --light-bg: #ffffff;
    --dark-bg: #0d1117;
}

/* CLEAN STREAMLIT PADDING */
section.main > div {padding-top: 0 !important;}

/* DARK / LIGHT BACKGROUND */
body[data-theme="dark"] {
    background-color: var(--dark-bg) !important;
    color: #eee !important;
}
body[data-theme="light"] {
    background-color: var(--light-bg) !important;
    color: #000 !important;
}

/* YELLOW LINE */
.separator {
    width: 100%;
    height: 3px;
    background: var(--yellow-line);
    margin: 25px 0;
}

/* Animated header */
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
    0% { background-position: 0%; }
    100% { background-position: 300%; }
}

/* Book card */
.book-card {
    border-radius: 15px;
    padding: 18px;
    margin-bottom: 10px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
}

/* FIXED FLOATING TOGGLE BUTTON */
.theme-toggle {
    position: fixed;
    top: 80px;
    left: 20px;
    width: 78px;
    height: 36px;
    border-radius: 50px;
    background: #2b2d3a;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: flex-start;
    padding: 4px;
    z-index: 999999999;
    pointer-events: auto:
    box-shadow: 0 3px 6px rgba(0,0,0,0.4);
}
header, iframe, .stAppViewTabHeader {
    pointer-events: none !important;
}
.theme-ball {
    width: 32px;
    height: 32px;
    background: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    transition: transform .3s;
}
.theme-sun {position:absolute; left:10px; opacity:0.3;}
.theme-moon {position:absolute; right:10px; opacity:1;}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# TOGGLE BUTTON (JS works correctly in Streamlit)
# ---------------------------------------------------
st.markdown("""
<div class="theme-toggle" onclick="toggleTheme()">
    <div class="theme-sun">☀</div>
    <div class="theme-moon">🌙</div>
    <div id="ball" class="theme-ball" style="transform: translateX(32px);">🌙</div>
</div>

<script>
function toggleTheme() {
    let body = window.parent.document.body;
    let ball = window.parent.document.getElementById("ball");

    if (body.getAttribute("data-theme") === "dark") {
        body.setAttribute("data-theme", "light");
        ball.style.transform = "translateX(0px)";
        ball.innerHTML = "☀";
    } else {
        body.setAttribute("data-theme", "dark");
        ball.style.transform = "translateX(32px)";
        ball.innerHTML = "🌙";
    }
}

window.parent.document.body.setAttribute("data-theme","dark");
</script>
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
c1, c2, c3 = st.columns([1,2,1])
with c2:
    uploaded_img = st.file_uploader("Upload bookshelf image", type=["jpg","jpeg","png"])
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

            # Titles
            st.subheader("📌 Extracted Titles")
            st.write(data.get("extracted_titles", []))

            st.markdown("<div class='separator'></div>", unsafe_allow_html=True)

            # Books Found
            st.subheader("📚 Books Found")
            books = data.get("books_found", [])

            if books:
                for book in books:
                    st.markdown("<div class='book-card'>", unsafe_allow_html=True)
                    col1, col2 = st.columns([1,4])

                    with col1:
                        if book.get("thumbnail"):
                            st.image(book["thumbnail"], width=100)

                    with col2:
                        st.markdown(f"### {book.get('title')}")
                        st.write("*Authors:*", book.get("authors"))
                        st.write("*Categories:*", book.get("categories"))

                        if book.get("description"):
                            with st.expander("📘 Description"):
                                st.write(book["description"])

                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.warning("No matching books found.")

            # Recommendations
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