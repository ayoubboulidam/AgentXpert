import os
import pandas as pd

# Directory to store uploaded files (ensure this directory exists)
UPLOAD_DIR = "uploaded_files"

# Create the directory if it does not exist
os.makedirs(UPLOAD_DIR, exist_ok=True)


def handle_file_upload(uploaded_file) -> str:
    """
    Handle file upload and store it in a persistent directory.
    Returns the path to the saved file.
    """
    # Save the uploaded file to the persistent directory
    file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Return the path to the uploaded file
    return file_path
