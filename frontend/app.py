import streamlit as st
import requests
from PIL import Image

st.set_page_config(page_title="ShelfScanner", page_icon="📚", layout="centered")

# --------------------------------
# API URL
# --------------------------------
API_BASE_URL = st.secrets["API_BASE_URL"]

# --------------------------------
# HERO HEADER
# --------------------------------
st.markdown("""
<div style="text-align:center; padding: 20px 0;">
    <h1 style="color:#ffce00; font-size:48px; margin-bottom:-10px;">📚 ShelfScanner</h1>
    <p style="font-size:18px; color:#dcdcdc;">Scan your bookshelf and get instant book insights.</p>
</div>
""", unsafe_allow_html=True)

# --------------------------------
# File Upload
# --------------------------------
uploaded = st.file_uploader("Upload a bookshelf image", type=["jpg", "jpeg", "png"])

if uploaded:
    st.image(uploaded, use_column_width=True)
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🔍 Scan Shelf", use_container_width=True):
        with st.spinner("Scanning... Please wait ⏳"):

            try:
                files = {"image": uploaded.getvalue()}
                response = requests.post(
                    f"{API_BASE_URL}/api/scan",
                    files=files,
                    timeout=400
                )

                if response.status_code != 200:
                    st.error("Error: " + response.text)
                else:
                    data = response.json()

                    # --------------------------------
                    # Extracted Titles Section
                    # --------------------------------
                    titles = data.get("extracted_titles", [])
                    if titles:
                        st.markdown("<hr style='border:1px solid #ffce00;'>", unsafe_allow_html=True)
                        st.subheader("📌 Extracted Text (Possible Titles)")
                        st.write(titles)
                    else:
                        st.warning("No readable text detected.")

                    # --------------------------------
                    # Books Found Section
                    # --------------------------------
                    books = data.get("books_found", [])

                    if books:
                        st.markdown("<hr style='border:1px solid #ffce00;'>", unsafe_allow_html=True)
                        st.subheader("📚 Books Found")

                        for book in books:
                            st.markdown("""
                                <div style="padding:15px; border-radius:10px; background-color:#1f1f1f; margin-bottom:15px;">
                            """, unsafe_allow_html=True)

                            cols = st.columns([1, 3])
                            with cols[0]:
                                if book.get("thumbnail"):
                                    st.image(book["thumbnail"], width=120)

                            with cols[1]:
                                st.markdown(f"### *{book.get('title','N/A')}*")
                                st.write(f"*Authors:* {book.get('authors','N/A')}")
                                st.write(f"*Categories:* {book.get('categories','N/A')}")

                                # Description toggle
                                if book.get("description"):
                                    with st.expander("📖 Description"):
                                        st.write(book["description"])

                            st.markdown("</div>", unsafe_allow_html=True)

                    else:
                        st.warning("No matching books found.")

                    # --------------------------------
                    # Recommended Books Section
                    # --------------------------------
                    recommendations = data.get("recommended", [])

                    if recommendations:
                        st.markdown("<hr style='border:1px solid #ffce00;'>", unsafe_allow_html=True)
                        st.subheader("⭐ Recommended Books")

                        for rec in recommendations:
                            st.markdown("""
                                <div style="padding:15px; border-radius:10px; background-color:#232323; margin-bottom:10px;">
                            """, unsafe_allow_html=True)

                            st.write(f"*Title:* {rec.get('title')}")
                            st.write(f"*Authors:* {rec.get('authors')}")

                            st.markdown("</div>", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Error: {e}")