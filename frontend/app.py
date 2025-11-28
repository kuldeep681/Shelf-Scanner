import streamlit as st
import requests
import uuid

st.set_page_config(page_title="ShelfScanner", page_icon="📚", layout="wide")

API_BASE_URL = st.secrets["API_BASE_URL"]

# ---------------------------------------------------
# GENERATE USER ID (stored in session_state)
# ---------------------------------------------------
if "user_id" not in st.session_state:
    st.session_state["user_id"] = "user_" + uuid.uuid4().hex[:8]

USER_ID = st.session_state["user_id"]


# ---------------------------------------------------
# CSS STYLING
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
# BOOKMARK SIDEBAR (RIGHT SIDE)
# ---------------------------------------------------
with st.sidebar:
    st.header("⭐ Your Bookmarks")

    try:
        resp = requests.get(f"{API_BASE_URL}/api/bookmarks/{USER_ID}", timeout=20)
        saved_books = resp.json().get("bookmarks", [])
    except:
        saved_books = []

    if saved_books:
        for b in saved_books:
            st.write(f"{b.get('title')}")
            st.caption(", ".join(b.get("authors", [])))
    else:
        st.info("No bookmarks yet.")


# ---------------------------------------------------
# SEARCH + UPLOAD
# ---------------------------------------------------
search = st.text_input("🔍 Search scanned books")

colL, colM, colR = st.columns([1,2,1])

with colM:
    uploaded_img = st.file_uploader("Upload bookshelf image", type=["jpg","jpeg","png"])
    scan_btn = st.button("🔎 Scan Shelf", use_container_width=True)


# ---------------------------------------------------
# SCAN LOGIC
# ---------------------------------------------------
if uploaded_img and scan_btn:

    st.image(uploaded_img, caption="Uploaded Image", use_column_width=True)

    with st.spinner("Scanning your books... ⏳✨"):
        try:
            files = {"image": uploaded_img.getvalue()}
            res = requests.post(f"{API_BASE_URL}/api/scan", files=files, timeout=300)

            if res.status_code != 200:
                st.error("API Error: " + res.text)

            data = res.json()

            # ---------------- Titles ----------------
            st.subheader("📌 Extracted Titles")
            titles = data.get("extracted_titles", [])
            st.write(titles)

            st.markdown("<div class='separator'></div>", unsafe_allow_html=True)

            # ---------------- Books ----------------
            st.subheader("📚 Books Found")
            books = data.get("books_found", [])

            if not books:
                st.warning("No books found.")
            else:
                for book in books:
                    st.markdown("<div class='book-card'>", unsafe_allow_html=True)

                    cA, cB = st.columns([1,4])

                    with cA:
                        if book.get("thumbnail"):
                            st.image(book["thumbnail"], width=100)

                    with cB:
                        st.markdown(f"### {book.get('title')}")
                        st.write("*Authors:*", book.get("authors"))
                        st.write("*Categories:*", book.get("categories"))

                        # Description
                        if book.get("description"):
                            with st.expander("📘 Description"):
                                st.write(book["description"])

                        # ⭐ BOOKMARK BUTTON
                        if st.button(f"⭐ Bookmark '{book.get('title')}'", key=book.get("title")):

                            payload = {
                                "user_id": USER_ID,
                                "title": book.get("title"),
                                "authors": book.get("authors"),
                                "thumbnail": book.get("thumbnail"),
                                "categories": book.get("categories"),
                                "description": book.get("description")
                            }

                            try:
                                requests.post(f"{API_BASE_URL}/api/bookmark", json=payload)
                                st.success("Book added to bookmarks!")
                            except:
                                st.error("Failed to save bookmark.")

                    st.markdown("</div>", unsafe_allow_html=True)


            # ---------------- Recommendations ----------------
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