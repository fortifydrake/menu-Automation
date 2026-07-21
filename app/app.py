import streamlit as st
import tempfile
import json
import os
import pandas as pd
from datetime import datetime

# Import modular pipeline
from pipeline import run_menu_pipeline
from imagesearch import image_search
from db.mongo import food_upload
from db.cloudinary import upload_to_cloudinary

st.set_page_config(page_title="Menu Automation", layout="wide")

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

st.title("Menu Automation Pipeline")

# ---------------------------
# PDF UPLOAD
# ---------------------------

uploaded_file = st.file_uploader(
    "Upload Menu PDF",
    type=["pdf"]
)

# ---------------------------
# OCR EXTRACTION & PIPELINE
# ---------------------------

if uploaded_file is not None:

    st.success(f"Uploaded: {uploaded_file.name}")

    if st.button("Extract Menu"):
        # Reset items state for fresh extraction
        if "items" in st.session_state:
            del st.session_state["items"]
        if "final_df" in st.session_state:
            del st.session_state["final_df"]
        if "master_df" in st.session_state:
            del st.session_state["master_df"]

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as tmp_file:
            tmp_file.write(uploaded_file.read())
            pdf_path = tmp_file.name

        progress_bar = st.progress(0.0)
        status_text = st.empty()

        def update_ui_progress(msg: str, ratio: float):
            progress_bar.progress(min(max(ratio, 0.0), 1.0))
            status_text.info(msg)

        try:
            with st.spinner("Processing pipeline..."):
                items = run_menu_pipeline(pdf_path, progress_callback=update_ui_progress)

            st.session_state["items"] = items
            st.success(f"Pipeline Completed! Extracted {len(items)} items.")
        except Exception as e:
            st.error(f"Pipeline Execution Failed: {e}")
            st.exception(e)
        finally:
            if os.path.exists(pdf_path):
                try:
                    os.remove(pdf_path)
                except Exception:
                    pass

# ---------------------------
# SHOW EDITABLE TABLE
# ---------------------------

if (
    "items" in st.session_state
    and "final_df" not in st.session_state
):
    st.write(f"Parsed Items Count: {len(st.session_state['items'])}")

    if len(st.session_state["items"]) == 0:
        st.warning("No menu items were extracted. Check log files under `logs/` directory.")
    else:
        df = pd.DataFrame(st.session_state["items"]).copy()
        
        # Ensure column ordering
        expected_cols = ["food_item", "category", "description", "variations", "prices"]
        for col in expected_cols:
            if col not in df.columns:
                df[col] = ""
        df = df[expected_cols]

        df["prices"] = df["prices"].apply(
            lambda x: ", ".join(x) if isinstance(x, list) else str(x)
        )

        df["variations"] = df["variations"].apply(
            lambda x: ", ".join(x) if isinstance(x, list) else str(x)
        )
            
        edited_df = st.data_editor(
            df,
            num_rows="dynamic",
            use_container_width=True
        )

        if st.button("Confirm Menu"):
            confirmed_df = edited_df.copy()
            confirmed_df["prices"] = confirmed_df["prices"].apply(
                lambda x: [p.strip() for p in str(x).split(",") if p.strip()]
            )
            confirmed_df["variations"] = confirmed_df["variations"].apply(
                lambda x: [v.strip() for v in str(x).split(",") if v.strip()]
            )

            st.session_state["final_df"] = confirmed_df
            st.success(f"Menu Confirmed with {len(confirmed_df)} items")
            st.rerun()

# ---------------------------
# FINAL CONFIRMED MENU
# ---------------------------

if "final_df" in st.session_state:

    st.subheader("Confirmed Menu")

    st.dataframe(
        st.session_state["final_df"],
        use_container_width=True
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
                row.get("candidate_images", [])
            )

            if row.get("image_url"):
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
            
            all_images = row.get("candidate_images", [])

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