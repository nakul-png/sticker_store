from pathlib import Path
from uuid import uuid4

from flask import current_app
from werkzeug.utils import secure_filename


def save_image(file_storage):
    if not file_storage or not file_storage.filename:
        return ""
    filename = secure_filename(file_storage.filename)
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if extension not in current_app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        raise ValueError("Only PNG, JPG, JPEG and WebP images are allowed.")
    # Browsers can lie about MIME type; check both the claimed MIME type and safe extension.
    if file_storage.mimetype and not file_storage.mimetype.startswith("image/"):
        raise ValueError("Uploaded file is not an image.")
    saved_name = f"{uuid4().hex}.{extension}"
    file_storage.save(Path(current_app.config["UPLOAD_FOLDER"]) / saved_name)
    return f"products/{saved_name}"
