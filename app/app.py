import streamlit as st
import tempfile
import json
import pandas as pd
from Pdf_text_extraction import extract_text_from_pdf_menu
from imagesearch import image_search
from datetime import datetime
from db.mongo import food_upload
from db.cloudinary import upload_to_cloudinary

st.markdown("""
<style>
.food-image {
    width: 180px;
    height: 180px;
    object-fit: cover;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

if "selected_images" not in st.session_state:
    st.session_state["selected_images"] = {}
    
# ---------------------------
# PAGE TITLE
# ---------------------------

st.title("Menu Automation From Tshitto")

# ---------------------------
# PDF UPLOAD
# ---------------------------

uploaded_file = st.file_uploader(
    "Upload Menu PDF",
    type=["pdf"]
)

# ---------------------------
# OCR EXTRACTION
# ---------------------------

if uploaded_file is not None:

    st.success(f"Uploaded: {uploaded_file.name}")

    if st.button("Extract Menu"):

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as tmp_file:

            tmp_file.write(uploaded_file.read())

            pdf_path = tmp_file.name

        with st.spinner("Running OCR..."):

            text = extract_text_from_pdf_menu(pdf_path)

        st.session_state["ocr_text"] = text
        print(type(text))
        st.success("OCR Complete")

# ---------------------------
# PARSE JSON ONLY ONCE
# ---------------------------

if (
    "ocr_text" in st.session_state
    and "items" not in st.session_state
):

    text = st.session_state["ocr_text"]

    text = (
        text.replace("```json", "")
        .replace("```", "")
        .strip()
    )

    items = []

    decoder = json.JSONDecoder()

    idx = 0

    while idx < len(text):

        try:

            obj, end = decoder.raw_decode(
                text[idx:]
            )

            if isinstance(obj, list):
                items.extend(obj)

            elif isinstance(obj, dict):
                items.append(obj)

            idx += end

        except Exception:
            idx += 1

    st.write("Parsed Items:", len(items))

    if len(items) == 0:
        st.error("No items parsed")
        st.code(text[:3000])

    st.session_state["items"] = items
        
# ---------------------------
# SHOW EDITABLE TABLE
# ---------------------------

if (
    "items" in st.session_state
    and "final_df" not in st.session_state
):

    df = pd.DataFrame(st.session_state["items"]).copy()
    
    df["prices"] = df["prices"].apply(
        lambda x: ", ".join(x)
        if isinstance(x, list)
        else str(x)
    )

    df["variations"] = df["variations"].apply(
        lambda x: ", ".join(x)
        if isinstance(x, list)
        else str(x)
    )
        
    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        width="stretch"
    )

    edited_df["prices"] = edited_df["prices"].apply(
        lambda x: [p.strip() for p in str(x).split(",") if p.strip()]
    )

    edited_df["variations"] = edited_df["variations"].apply(
        lambda x: [v.strip() for v in str(x).split(",") if v.strip()]
    )
    
    if st.button("Confirm Menu"):

        st.session_state["final_df"] = (
            edited_df.copy()
        )

        st.success(
            f"Menu Confirmed with {len(edited_df)} items"
        )

        st.rerun()

# ---------------------------
# FINAL CONFIRMED MENU
# ---------------------------

if "final_df" in st.session_state:

    st.subheader("Confirmed Menu")

    st.dataframe(
        st.session_state["final_df"],
        width="stretch"
    )

    st.success(
        f"Ready to process {len(st.session_state['final_df'])} items"
    )
    
    # -------------------------------
    # START FOOD PROCESSING
    # -------------------------------

    if st.button("Start Food Processing"):

        final_df = st.session_state["final_df"]

        with st.spinner(f"Processing {len(final_df)} food items..."):

            results = image_search(final_df)

        st.session_state["master_df"] = pd.DataFrame(results)

        if "selected_images" not in st.session_state:
            st.session_state["selected_images"] = {}

# -------------------------------
# SHOW IMAGE REVIEW UI
# -------------------------------

if "master_df" in st.session_state:

    master_df = st.session_state["master_df"]

    
    for row_idx, row in master_df.iterrows():

        food_key = row["food_item"].strip().upper()

        selected = (
            food_key in
            st.session_state["selected_images"]
        )

        with st.expander(
            f"{row['food_item']}",
            expanded=False
        ):

            total_images = len(
                row["candidate_images"]
            )

            if row["image_url"]:
                total_images += 1

            total_images = max(
                total_images,
                1
            )

            idx = 0
            
            # --------------------------------
            # CANDIDATE IMAGES
            # --------------------------------

            food_key = row["food_item"].strip().upper()
            
            all_images = row["candidate_images"]

            for start in range(0, len(all_images), 3):

                cols = st.columns(3)

                batch = all_images[start:start+3]

                for img_idx, (col, img) in enumerate(
                    zip(cols, batch)
                ):

                    with col:

                        st.image(
                            img["thumbnail"],
                            use_container_width=True
                        )

                        if st.button(
                            "Select",
                            key=f"use_{row_idx}_{food_key}_{start}_{img_idx}"
                        ):

                            st.session_state["selected_images"][
                                food_key
                            ] = {
                                "provider": img["provider"],
                                "image_url": img["image_url"],
                                "thumbnail": img["thumbnail"]
                            }

                            st.rerun()

            # --------------------------------
            # UPLOAD IMAGE
            # --------------------------------

            st.markdown("### Upload Your Own Image")

            uploaded = st.file_uploader(
                f"Upload image for {row['food_item']}",
                type=["jpg", "jpeg", "png"],
                key=f"upload_{row_idx}_{food_key}"
            )

            if uploaded:

                st.session_state["selected_images"][
                    food_key
                ] = {
                    "provider": "upload",
                    "file_bytes": uploaded.getvalue(),
                    "filename": uploaded.name
                }

            # --------------------------------
            # CURRENT SELECTION
            # --------------------------------

            selected = (
                st.session_state["selected_images"]
                .get(food_key)
            )

            if selected:

                st.success("Selected Image")

                # Upload image
                if selected["provider"] == "upload":

                    st.image(
                        selected["file_bytes"],
                        width=300
                    )

                    st.caption(
                        selected["filename"]
                    )

                # Pixabay / Pexels / MongoDB
                else:

                    st.image(
                        selected["image_url"],
                        width=300
                    )

                st.write(
                    f"Source: {selected['provider']}"
                )
                if st.button(
                    "❌ Clear Selection",
                    key=f"clear_{row_idx}_{food_key}"
                ):

                    if food_key in st.session_state["selected_images"]:
                        del st.session_state["selected_images"][food_key]

                    st.rerun()
# -------------------------------
# FINAL APPROVAL
# -------------------------------

if (
    "selected_images" in st.session_state
    and len(st.session_state["selected_images"]) > 0
):

    if st.button("Approve All Images"):

        approved_images = (
            st.session_state["selected_images"]
        )

        st.write(approved_images)

        st.success(
            "All images approved!"
        )
        
        final_records = []

        for _, row in st.session_state["final_df"].iterrows():

            food_key = row["food_item"].strip().upper()

            image_data = (
                st.session_state["selected_images"]
                .get(food_key)
            )

            final_records.append({
                "food_name": row.get("food_item", ""),
                "category": row.get("category", ""),
                "description": row.get("description", ""),
                "prices": row.get("prices", []),
                "image_data": image_data,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })

        st.write("uploading to db")
        progress = st.progress(0)

        for idx, record in enumerate(final_records):

            if not record["image_data"]:
                continue

            cloudinary_data = upload_to_cloudinary(
                record["image_data"],
                record["food_name"]
            )

            record["image"] = {
                "provider": "cloudinary",
                "url": cloudinary_data["url"],
                "public_id": cloudinary_data["public_id"]
            }

            del record["image_data"]

            progress.progress(
                (idx + 1) / len(final_records)
            )

        food_upload(final_records)

        st.success(
            f"{len(final_records)} items uploaded successfully"
        )