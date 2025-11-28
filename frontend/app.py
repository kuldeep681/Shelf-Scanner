import streamlit as st
import requests
from PIL import Image
import io

st.set_page_config(page_title="ShelfScanner", page_icon="📚", layout="wide")

API_BASE_URL = st.secrets["API_BASE_URL"]

# ---------------------------------------------------------
# 🔥 HERO HEADER (Modern + Animated)
# ---------------------------------------------------------
st.markdown(
    """
    <div style="padding:40px 0; text-align:center;">
        <h1 style="font-size:60px; margin-bottom:0;">📚 ShelfScanner</h1>
        <p style="font-size:22px; opacity:0.8;">Scan your bookshelf, discover books, and explore recommendations.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# Upload
# ---------------------------------------------------------
uploaded_file = st.file_uploader(
    "Upload an image of your bookshelf",
    type=["jpg", "jpeg", "png"],
)

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

    if st.button("Scan Shelf"):
        with st.spinner("🔍 Extracting text... This may take a moment."):

            files = {"image": uploaded_file.getvalue()}

            # API Call
            response = requests.post(
                f"{API_BASE_URL}/api/scan",
                files=files,
                timeout=400
            )

            if response.status_code != 200:
                st.error("Error from API: " + response.text)
            else:
                data = response.json()

                # ---------------------------------------------------------
                # 🎯 Extracted Titles
                # ---------------------------------------------------------
                st.subheader("📌 Extracted Titles")
                titles = data.get("extracted_titles", [])
                if titles:
                    st.success("Text extracted successfully! 🎉")
                    st.write(titles)
                else:
                    st.warning("No readable text detected.")

                # ---------------------------------------------------------
                # 🔍 SEARCH BAR FOR BOOK RESULTS
                # ---------------------------------------------------------
                st.subheader("🔎 Search Books")
                search_query = st.text_input("Search by title or author")

                # ---------------------------------------------------------
                # 📚 Books Found (Modern Card UI)
                # ---------------------------------------------------------
                st.subheader("📚 Books Found")

                books = data.get("books_found", [])

                if books:
                    for book in books:

                        # Apply search filter
                        if search_query:
                            if search_query.lower() not in str(book).lower():
                                continue

                        st.markdown(
                            """
                            <div style="
                                border-radius: 12px;
                                padding: 20px;
                                margin: 15px 0;
                                background: #ffffff;
                                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                            ">
                            """,
                            unsafe_allow_html=True
                        )

                        cols = st.columns([1, 3])
                        with cols[0]:
                            if book.get("thumbnail"):
                                st.image(book["thumbnail"], width=120)
                            else:
                                st.write("No image")

                        with cols[1]:
                            st.markdown(f"### {book.get('title','N/A')}")
                            st.markdown(f"*Authors:* {book.get('authors',['N/A'])}")
                            st.markdown(f"*Categories:* {book.get('categories',['N/A'])}")

                            desc = book.get("description", "")
                            if desc:
                                with st.expander("📄 Description"):
                                    st.write(desc)

                        st.markdown("</div>", unsafe_allow_html=True)

                else:
                    st.warning("No books found.")

                # ---------------------------------------------------------
                # ⭐ Recommendations
                # ---------------------------------------------------------
                st.subheader("⭐ Recommended Books")

                recs = data.get("recommended", [])

                if recs:
                    for r in recs:
                        st.markdown(
                            f"""
                            <div style="
                                border-radius: 12px;
                                padding: 15px;
                                background: #f7f7f7;
                                margin-bottom: 10px;
                            ">
                                <strong>{r.get('title')}</strong><br>
                                <span style="opacity:0.7;">{r.get('authors')}</span>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                else:
                    st.info("No recommendations yet — scan more books!")