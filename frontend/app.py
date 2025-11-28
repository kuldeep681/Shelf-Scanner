import streamlit as st
import requests

st.set_page_config(page_title="ShelfScanner", page_icon="📚", layout="wide")

API_BASE_URL = st.secrets["API_BASE_URL"]

# ---------------------------------------------------
# GLOBAL CSS (UI + Colors + Toggle Button)
# ---------------------------------------------------
st.markdown("""
<style>

:root {
    --yellow-line: #f1c40f;
    --light-bg: #ffffff;
    --dark-bg: #0d1117;
}

/* remove Streamlit extra padding */
section.main > div {padding-top: 0 !important;}

/* DARK / LIGHT THEMING */
body[data-theme="dark"] {
    background-color: var(--dark-bg) !important;
    color: #eee !important;
}
body[data-theme="light"] {
    background-color: var(--light-bg) !important;
    color: #000 !important;
}

/* Yellow separator line */
.separator {
    width: 100%;
    height: 3px;
    background: var(--yellow-line);
    margin: 25px 0;
}

/* HERO ANIMATED TEXT */
.hero {
    font-size: 55px;
    font-weight: 900;
    text-align: center;
    margin-top: 10px;
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

/* Book card UI */
.book-card {
    border-radius: 15px;
    padding: 18px;
    margin-bottom: 12px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.12);
}

/* ------------------------------
   CUSTOM TOGGLE BUTTON (SUN/MOON)
--------------------------------*/
.theme-toggle {
    position: fixed;
    top: 70px;    /* moved down so it's visible */
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

    z-index: 999999999 !important;
    pointer-events: auto !important;

    box-shadow: 0 3px 8px rgba(0,0,0,0.45);
}

/* prevent Streamlit header from blocking button */
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

.theme-sun  { position: absolute; left: 10px; opacity: 0.3; }
.theme-moon { position: absolute; right: 10px; opacity: 1; }

</style>
""", unsafe_allow_html=True)



# ---------------------------------------------------
# TOGGLE BUTTON (JS WORKS INSIDE STREAMLIT NOW)
# ---------------------------------------------------
st.markdown("""
<div class="theme-toggle" id="themeToggle">
    <div class="theme-sun">☀</div>
    <div class="theme-moon">🌙</div>
    <div id="ball" class="theme-ball" style="transform: translateX(32px);">🌙</div>
</div>

<script>

// Streamlit shadow-root safe selector
function getAppRoot() {
    const frames = window.parent.document.getElementsByTagName("iframe");
    for (let f of frames) {
        try {
            if (f.contentDocument.querySelector(".stApp")) {
                return f.contentDocument.querySelector(".stApp");
            }
        } catch {}
    }
    return window.parent.document.querySelector(".stApp");
}

function toggleTheme() {
    let root = getAppRoot();
    let ball = document.getElementById("ball");

    let current = root.getAttribute("data-theme") || "dark";

    if (current === "dark") {
        root.setAttribute("data-theme", "light");
        ball.style.transform = "translateX(0px)";
        ball.innerHTML = "☀";
    } else {
        root.setAttribute("data-theme", "dark");
        ball.style.transform = "translateX(32px)";
        ball.innerHTML = "🌙";
    }
}

// Attach click listener safely
setTimeout(() => {
    document.getElementById("themeToggle").onclick = toggleTheme;

    // default theme
    let root = getAppRoot();
    root.setAttribute("data-theme","dark");
}, 400);

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
# IMAGE UPLOAD + SCAN UI
# ---------------------------------------------------
center = st.columns([1,2,1])[1]

with center:
    uploaded_img = st.file_uploader("Upload bookshelf image", type=["jpg", "jpeg", "png"])
    scan_btn = st.button("🔎 Scan Shelf", use_container_width=True)



# ---------------------------------------------------
# SCANNING PROCESS
# ---------------------------------------------------
if uploaded_img and scan_btn:

    st.image(uploaded_img, caption="Uploaded Image", use_column_width=True)

    with st.spinner("Scanning your bookshelf... ⏳✨"):

        try:
            files = {"image": uploaded_img.getvalue()}
            res = requests.post(f"{API_BASE_URL}/api/scan", files=files, timeout=300)

            if res.status_code != 200:
                st.error("API Error: " + res.text)

            data = res.json()

            # ------------------- Extracted Titles -------------------
            st.subheader("📌 Extracted Titles")
            st.write(data.get("extracted_titles", []))

            st.markdown("<div class='separator'></div>", unsafe_allow_html=True)

            # ------------------- Books Found -------------------
            st.subheader("📚 Books Found")
            books = data.get("books_found", [])

            if books:
                for book in books:
                    st.markdown("<div class='book-card'>", unsafe_allow_html=True)

                    colA, colB = st.columns([1,4])

                    with colA:
                        if book.get("thumbnail"):
                            st.image(book["thumbnail"], width=110)

                    with colB:
                        st.markdown(f"### {book.get('title')}")
                        st.write("*Authors:*", book.get("authors"))
                        st.write("*Categories:*", book.get("categories"))

                        if book.get("description"):
                            with st.expander("📘 Description"):
                                st.write(book["description"])

                    st.markdown("</div>", unsafe_allow_html=True)

            else:
                st.warning("No matching books found.")

            # ------------------- Recommended Books -------------------
            st.subheader("⭐ Recommended Books")
            recs = data.get("recommended", [])

            if recs:
                for r in recs:
                    st.write(f"### {r.get('title')}")
                    st.write(r.get("authors"))
            else:
                st.info("No recommendations yet — scan more books!")

        except Exception as e:
            st.error(f"Error: {e}")