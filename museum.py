import streamlit as st
import requests

# 🎨 App Title
st.set_page_config(page_title="Explore Artworks with MET Museum API", page_icon="🎨", layout="centered")
st.title("🎨 Explore Artworks with MET Museum API")

# 🔍 Textbox for user input
query = st.text_input("Search for Artworks:")

# 🪄 Only run if the user typed something
if query:
    with st.spinner("Searching artworks..."):
        # 1️⃣ Search endpoint
        search_url = f"https://collectionapi.metmuseum.org/public/collection/v1/search?q={query}"
        response = requests.get(search_url)
        data = response.json()

        # 2️⃣ Check if there are any results
        if data.get("total", 0) > 0:
            st.success(f"Found {data['total']} results! Showing the first few...")

            # Show first 3 artworks
            for object_id in data["objectIDs"][:3]:
                object_url = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{object_id}"
                artwork_data = requests.get(object_url).json()

                # 3️⃣ Display artwork info
                st.subheader(artwork_data.get("title", "Untitled"))

                image_url = artwork_data.get("primaryImageSmall", "")
                if image_url:
                    st.image(image_url, use_container_width=True)
                else:
                    st.info("No image available.")

                st.caption(f"**Artist:** {artwork_data.get('artistDisplayName', 'Unknown')}")
                st.write(f"**Department:** {artwork_data.get('department', 'N/A')}")
                st.write(f"**Medium:** {artwork_data.get('medium', 'N/A')}")
                st.divider()
        else:
            st.warning("No artworks found. Try another keyword.")
