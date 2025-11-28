import streamlit as st
import requests
import uuid

st.set_page_config(page_title="ShelfScanner", page_icon="📚", layout="wide")

API_BASE_URL = st.secrets["API_BASE_URL"]

# ---------------------------------------------------
# USER ID (stored once)
# ---------------------------------------------------
if "user_id" not in st.session_state:
    st.session_state["user_id"] = "user_" + uuid.uuid4().hex[:8]

USER_ID = st.session_state["user_id"]

# ---------------------------------------------------
# SESSION STATE FIX (to stop losing scan results)
# ---------------------------------------------------
if "scanned_books" not in st.session_state:
    st.session_state["scanned_books"] = []

if "extracted_titles" not in st.session_state:
    st.session_state["extracted_titles"] = []

if "recommendations" not in st.session_state:
    st.session_state["recommendations"] = []


# ---------------------------------------------------
# CSS SECTION (unchanged)
# ---------------------------------------------------
st.markdown("""
<style>

.separator {height:3px; width:100%; background:#f1c40f; margin:20px 0;}

.hero {
    font-size:50px; font-weight:900; text-align:center;
    background:linear-gradient(90deg,#ffdd00,#ff9900,#ffdd00);
    background-size:300%;
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
    animation:flow 1.2s linear infinite;
}
@keyframes flow {0%{background-position:0%}100%{background-position:300%}}

.book-card {
    padding:15px;
    border-radius:12px;
    margin-bottom:10px;
    border:1px solid rgba(255,255,255,0.1);
    background:rgba(255,255,255,0.04);
}

.bookmark-btn {
    background:#ffdd00;
    padding:6px 10px;
    border-radius:6px;
    color:black;
    font-weight:700;
    cursor:pointer;
}

</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------
# HEADER
# ---------------------------------------------------
st.markdown("<div class='hero'>📚 ShelfScanner</div>", unsafe_allow_html=True)
st.markdown("<div class='separator'></div>", unsafe_allow_html=True)


# ---------------------------------------------------
# RIGHT SIDEBAR — BOOKMARKS
# ---------------------------------------------------
with st.sidebar:
    st.header("⭐ Your Bookmarks")

    try:
        resp = requests.get(f"{API_BASE_URL}/api/bookmarks/{USER_ID}", timeout=20)
        bookmarks = resp.json().get("bookmarks", [])
        
    except:
        bookmarks = []

    if bookmarks:
        for b in bookmarks:
            st.write(f"{b.get('title')}")
            st.caption(", ".join(b.get("authors", [])))
    else:
        st.info("No bookmarks yet.")


# ---------------------------------------------------
# SEARCH BAR (This should NOT reset scan)
# ---------------------------------------------------
search = st.text_input(
    "🔍 Search scanned books",
    st.session_state.get("search_text", ""),
)

# Save search in session_state
st.session_state["search_text"] = search


# ---------------------------------------------------
# UPLOAD BUTTON
# ---------------------------------------------------
colL, colM, colR = st.columns([1,2,1])

with colM:
    uploaded_img = st.file_uploader("Upload bookshelf image", type=["jpg","jpeg","png"])
    scan_btn = st.button("🔎 Scan Shelf", use_container_width=True)


# ---------------------------------------------------
# SCAN ACTION
# ---------------------------------------------------
if uploaded_img and scan_btn:

    st.image(uploaded_img, caption="Uploaded Image", use_column_width=True)

    with st.spinner("Scanning your books... ⏳✨"):

        files = {"image": uploaded_img.getvalue()}
        res = requests.post(f"{API_BASE_URL}/api/scan", files=files, timeout=300)

        if res.status_code != 200:
            st.error("API Error: " + res.text)
        else:
            data = res.json()

            # STORE RESULTS IN SESSION STATE
            st.session_state["extracted_titles"] = data.get("extracted_titles", [])
            st.session_state["scanned_books"] = data.get("books_found", [])
            st.session_state["recommendations"] = data.get("recommended", [])


# ---------------------------------------------------
# SHOW SCAN RESULTS (persistent)
# ---------------------------------------------------
if st.session_state["extracted_titles"]:
    st.subheader("📌 Extracted Titles")
    st.write(st.session_state["extracted_titles"])

    st.markdown("<div class='separator'></div>", unsafe_allow_html=True)


# ---------------------------------------------------
# DISPLAY BOOKS
# ---------------------------------------------------
books = st.session_state["scanned_books"]

# Apply search filter
if search:
    books = [b for b in books if search.lower() in b.get("title", "").lower()]

st.subheader("📚 Books Found")

if books:
    for book in books:
        st.markdown("<div class='book-card'>", unsafe_allow_html=True)

        c1, c2 = st.columns([1,4])

        with c1:
            if book.get("thumbnail"):
                st.image(book["thumbnail"], width=100)

        with c2:
            st.markdown(f"### {book.get('title')}")
            st.write("*Authors:*", book.get("authors"))
            st.write("*Categories:*", book.get("categories"))

            if book.get("description"):
                with st.expander("📘 Description"):
                    st.write(book["description"])

            # ⭐ BOOKMARK BUTTON (NO RESET NOW)
            if st.button(f"⭐ Bookmark '{book.get('title')}'", key=book.get("title")):
                payload = {
                    "user_id": USER_ID,
                    "title": book.get("title"),
                    "authors": book.get("authors"),
                    "thumbnail": book.get("thumbnail"),
                    "categories": book.get("categories"),
                    "description": book.get("description"),
                }

                requests.post(f"{API_BASE_URL}/api/bookmark", json=payload)

                st.success("Book added to bookmarks!")

        st.markdown("</div>", unsafe_allow_html=True)

else:
    st.info("No books found or match your search.")


# ---------------------------------------------------
# RECOMMENDATIONS
# ---------------------------------------------------
if st.session_state["recommendations"]:
    st.subheader("⭐ Recommended Books")
    for r in st.session_state["recommendations"]:
        st.write(f"### {r['title']}")
        st.write(r.get("authors"))