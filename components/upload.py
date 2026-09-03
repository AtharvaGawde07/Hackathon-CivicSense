"""
CivicAI — Image Upload Component

Renders the Streamlit file-uploader widget, validates the uploaded file,
and shows a preview.  Returns the PIL Image and metadata to the caller
(``app.py``) — no AI logic lives here.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import streamlit as st
from PIL import Image

from config.constants import ALLOWED_IMAGE_EXTENSIONS, MAX_IMAGE_SIZE_MB

if TYPE_CHECKING:
    from streamlit.runtime.uploaded_file_manager import UploadedFile


def render_upload_section() -> tuple[Image.Image | None, "UploadedFile | None"]:
    """Display the image upload UI and return the result.

    Returns
    -------
    (image, uploaded_file)
        ``image`` is a PIL Image if a valid file was uploaded, else ``None``.
        ``uploaded_file`` is the raw Streamlit ``UploadedFile`` (useful for
        filename / size metadata).
    """
    st.subheader("📷 Upload a Photo of the Civic Issue")

    st.markdown(
        f"""
        Upload a clear photograph of the civic problem you want to report.

        - **Accepted formats:** {', '.join(ext.upper() for ext in ALLOWED_IMAGE_EXTENSIONS)}
        - **Maximum size:** {MAX_IMAGE_SIZE_MB} MB
        - **Tip:** Use good lighting and capture the full extent of the issue.
        """
    )

    uploaded_file: UploadedFile | None = st.file_uploader(
        "Choose an image",
        type=ALLOWED_IMAGE_EXTENSIONS,
        help="Take or select a photo showing the civic issue.",
        key="civic_image_uploader",
    )

    if uploaded_file is None:
        return None, None

    # ── Size check ───────────────────────────────────────────
    size_mb = uploaded_file.size / (1024 * 1024)
    if size_mb > MAX_IMAGE_SIZE_MB:
        st.error(
            f"File is too large ({size_mb:.1f} MB). "
            f"Please upload an image under {MAX_IMAGE_SIZE_MB} MB."
        )
        return None, None

    # ── Open & preview ───────────────────────────────────────
    try:
        image = Image.open(uploaded_file)
    except Exception:
        st.error("Unable to read the uploaded file. Please upload a valid image.")
        return None, None

    st.image(image, caption="Uploaded Image Preview", use_container_width=True)

    st.caption(
        f"**File:** {uploaded_file.name}  •  "
        f"**Size:** {size_mb:.2f} MB  •  "
        f"**Dimensions:** {image.width} × {image.height} px"
    )

    return image, uploaded_file
