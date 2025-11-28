import streamlit as st
import requests
from PIL import Image

st.set_page_config(page_title="ShelfScanner", page_icon="📚", layout="wide")

API_BASE_URL = st.secrets["API_BASE_URL"]

# ---------------------------------------------------
# FIXED: Inject CSS first (no JS inside CSS block)
# ---------------------------------------------------
st.markdown("""
<style>

:root {
    --yellow-line: #f1c40f;
    --light-bg: #ffffff;
    --dark-bg: #0d1117;
}

/* BODY THEMES */
body[data-theme="dark"] {
    background-color: var(--dark-bg) !important;
    color: white !important;
}
body[data-theme="light"] {
    background-color: var(--light-bg) !important;
    color: black !important;
}

/* YELLOW SEPARATOR */
.separator {
    width: 100%;
    height: 3px;
    background: var(--yellow-line);
    margin: 20px 0 30px 0;
}

/* HERO ANIMATION */
.hero {
    font-size: 50px;
    font-weight: 900;
    text-align: center;
    margin-top: 20px;
    background: linear-gradient(90deg, #ffdd00, #ff9900, #ffdd00);
    background-size: 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: flow 2s linear infinite;
}
@keyframes flow {
    0% { background-position: 0%; }
    100% { background-position: 300%; }
}

/* BOOK CARD */
.book-card {
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 10px;
    border: 1px solid rgba(255,255,255,0.1);
    background: rgba(255,255,255,0.05);
}

/* Beautiful Toggle Button */
.toggle-container {
    position: fixed;
    top: 15px;
    left: 15px;
    width: 70px;
    height: 32px;
    border-radius: 50px;
    background: #2b2d3a;
    cursor: pointer;
    display: flex;
    align-items: center;
    padding: 4px;
    z-index: 99999;
}
.toggle-circle {
    width: 28px;
    height: 28px;
    background: white;
    border-radius: 50%;
    font-size: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: transform .3s;
}
.sun-icon {
    position: absolute;
    left: 10px;
    opacity: .2;
}
.moon-icon {
    position: absolute;
    right: 10px;
    opacity: 1;
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------
# FIXED: JS + HTML TOGGLE BUTTON ADDED SEPARATELY
# ---------------------------------------------------
st.markdown("""
<script>
function switchTheme() {
    var body = window.parent.document.body;
    var ball = window.parent.document.getElementById("toggleBall");

    var theme = body.getAttribute("data-theme");
    if (theme === "dark") {
        body.setAttribute("data-theme","light");
        ball.style.transform = "translateX(0px)";
        ball.innerHTML = "☀";
    } else {
        body.setAttribute("data-theme","dark");
        ball.style.transform = "translateX(32px)";
        ball.innerHTML = "🌙";
    }
}
</script>

<div class="toggle-container" onclick="switchTheme()">
    <div class="sun-icon">☀</div>
    <div class="moon-icon">🌙</div>
    <div id="toggleBall" class="toggle-circle" style="transform: translateX(32px);">🌙</div>
</div>

<script>
window.parent.document.body.setAttribute("data-theme","dark");
</script>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# HERO TITLE
# ---------------------------------------------------
st.markdown("<div class='hero'>📚 ShelfScanner</div>", unsafe_allow_html=True)
st.markdown("<div class='separator'></div>", unsafe_allow_html=True)

# ---------------------------------------------------
# SEARCH BAR
# ---------------------------------------------------
search = st.text_input("🔍 Search scanned books")


# ---------------------------------------------------
# UPLOAD + SCAN UI
# ---------------------------------------------------
c1, c2, c3 = st.columns([1,2,1])

with c2:
    img = st.file_uploader("Upload bookshelf image", type=["jpg","jpeg","png"])
    scan = st.button("🔎 Scan Shelf", use_container_width=True)

# ---------------------------------------------------
# SCAN PROCESS
# ---------------------------------------------------
if img and scan:
    st.image(img, caption="Uploaded", use_column_width=True)

    with st.spinner("Scanning... ⏳"):
        try:
            files = {"image": img.getvalue()}
            res = requests.post(f"{API_BASE_URL}/api/scan", files=files, timeout=300)

            if res.status_code != 200:
                st.error("API error: " + res.text)
            else:
                data = res.json()

                st.subheader("📌 Extracted Titles")
                st.write(data.get("extracted_titles", []))

                st.markdown("<div class='separator'></div>", unsafe_allow_html=True)

                st.subheader("📚 Books Found")
                books = data.get("books_found", [])

                if books:
                    for b in books:
                        st.markdown("<div class='book-card'>", unsafe_allow_html=True)
                        colA, colB = st.columns([1,4])

                        with colA:
                            if b.get("thumbnail"):
                                st.image(b["thumbnail"], width=100)

                        with colB:
                            st.markdown(f"### {b.get('title')}")
                            st.write("*Authors:*", b.get("authors"))
                            st.write("*Categories:*", b.get("categories"))

                            if b.get("description"):
                                with st.expander("📘 Description"):
                                    st.write(b["description"])

                        st.markdown("</div>", unsafe_allow_html=True)

                else:
                    st.warning("No matching books.")

                st.subheader("⭐ Recommended Books")
                recs = data.get("recommended", [])
                if recs:
                    for r in recs:
                        st.write(f"### {r.get('title')}")
                        st.write(r.get("authors"))
                else:
                    st.info("No recommendations yet.")

        except Exception as e:
            st.error(f"Error: {e}")