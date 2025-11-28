import streamlit as st
import requests
from PIL import Image
import io

st.set_page_config(page_title="ShelfScanner", page_icon="📚", layout="centered")

# -------------------------------
# API Base URL (local or cloud)
# -------------------------------
API_BASE_URL = st.secrets.get("API_BASE_URL") if "API_BASE_URL" in st.secrets else "http://127.0.0.1:8000"

st.title("📚 ShelfScanner")
st.write("Upload a shelf image and extract book information automatically.")

# -------------------------------
# File Upload
# -------------------------------
uploaded_file = st.file_uploader("Upload an image of your bookshelf", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # Show the image preview
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # Submit button
    if st.button("Scan Shelf"):
        with st.spinner("Scanning your shelf... ⏳"):

            # Send file to FastAPI
            files = {"image": uploaded_file.getvalue()}
            try:
                response = requests.post(f"{API_BASE_URL}/api/scan", files=files)

                if response.status_code != 200:
                    st.error("Error from API: " + response.text)
                else:
                    data = response.json()

                    # -------------------------------
                    # Extracted Titles
                    # -------------------------------
                    st.subheader("📌 Extracted Text (Possible Book Titles)")
                    if data["extracted_titles"]:
                        st.write(data["extracted_titles"])
                    else:
                        st.warning("No readable text detected.")

                    # -------------------------------
                    # Books Found
                    # -------------------------------
                    st.subheader("📚 Books Found")
                    books = data["books_found"]

                    if books:
                        for book in books:
                            st.markdown("---")
                            st.write(f"*Title:* {book.get('title', 'N/A')}")
                            st.write(f"*Authors:* {book.get('authors', ['N/A'])}")
                            st.write(f"*Categories:* {book.get('categories', ['N/A'])}")

                            if book.get("thumbnail"):
                                st.image(book["thumbnail"], width=120)
                    else:
                        st.warning("No matching books found in Google Books API.")

                    # -------------------------------
                    # Recommendations
                    # -------------------------------
                    st.subheader("⭐ Recommended Books")
                    recs = data["recommended"]

                    if recs:
                        for r in recs:
                            st.markdown("---")
                            st.write(f"*Title:* {r.get('title')}")
                            st.write(f"*Authors:* {r.get('authors')}")
                    else:
                        st.info("No recommendations yet — try scanning more books!")

            except Exception as e:
                st.error(f"An error occurred: {e}")