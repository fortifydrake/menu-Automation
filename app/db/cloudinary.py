import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv
from uuid import uuid4
import re
load_dotenv()
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)


def upload_to_cloudinary(
    image_data,
    food_name
):

    public_id = re.sub(
        r"[^a-z0-9_-]",
        "_",
        food_name
    )

    public_id = re.sub(
        r"_+",
        "_",
        public_id
    )
    
    public_id = public_id.strip("_")+ "_" + str(uuid4())[:8]

    if image_data["provider"] == "upload":

        result = cloudinary.uploader.upload(
            image_data["file_bytes"],
            folder="menu_images",
            public_id=public_id,
            overwrite=True
        )

    else:

        result = cloudinary.uploader.upload(
            image_data["image_url"],
            folder="menu_images",
            public_id=public_id,
            overwrite=True
        )

    return {
        "url": result["secure_url"],
        "public_id": result["public_id"]
    }