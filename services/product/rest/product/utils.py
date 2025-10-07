import uuid
import os

def product_image_upload_path(instance, filename):
    """
    Generate a random filename for uploaded product images.
    Example: products/images/2c7e6b22-3fda-4d73-8e6f-6cde6e01e9ef.jpg
    """
    ext = os.path.splitext(filename)[1]  # Get file extension (.jpg, .png, etc.)
    new_filename = f"{uuid.uuid4()}{ext}"  # Random UUID with same extension
    return os.path.join("products", "images", new_filename)
