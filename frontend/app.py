import streamlit as st
import requests
from PIL import Image
import io

st.set_page_config(page_title="ShelfScanner", page_icon="📚", layout="centered")

# -------------------------------
# API Base URL
# -------------------------------
API_BASE_URL = st.secrets["API_BASE_URL"]

st.title("📚 ShelfScanner")
st.write("Upload a shelf image and extract book information automatically.")

# -------------------------------
# File Upload
# -------------------------------
uploaded_file = st.file_uploader("Upload an image of your bookshelf", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # Preview image
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

    if st.button("Scan Shelf"):
        with st.spinner("Scanning your shelf... ⏳"):

            try:
                files = {"image": uploaded_file.getvalue()}

                # -------------------------------
                # SEND TO BACKEND WITH TIMEOUT
                # -------------------------------
                response = requests.post(
                    f"{API_BASE_URL}/api/scan",
                    files=files,
                    timeout=400
                )

                if response.status_code != 200:
                    st.error("Error from API: " + response.text)
                else:
                    data = response.json()

                    # Extracted titles
                    st.subheader("📌 Extracted Text (Possible Book Titles)")
                    titles = data.get("extracted_titles", [])
                    if titles:
                        st.write(titles)
                    else:
                        st.warning("No readable text detected.")

                    # Books Found
                    st.subheader("📚 Books Found")
                    books = data.get("books_found", [])

                    if books:
                        for book in books:
                            st.markdown("---")
                            st.write(f"*Title:* {book.get('title','N/A')}")
                            st.write(f"*Authors:* {book.get('authors',['N/A'])}")
                            st.write(f"*Categories:* {book.get('categories',['N/A'])}")

                            if book.get("thumbnail"):
                                st.image(book["thumbnail"], width=120)
                    else:
                        st.warning("No matching books found.")

                    # Recommendations
                    st.subheader("⭐ Recommended Books")
                    recs = data.get("recommended", [])

                    if recs:
                        for r in recs:
                            st.markdown("---")
                            st.write(f"*Title:* {r.get('title')}")
                            st.write(f"*Authors:* {r.get('authors')}")
                    else:
                        st.info("No recommendations yet — try scanning more books!")

            except Exception as e:
                st.error(f"An error occurred: {e}")