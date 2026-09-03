"""
CivicAI — Image Preprocessing

Provides a single `preprocess_image` function that normalises an uploaded
image into a format suitable for downstream model inference.

IMPORTANT
---------
The current implementation performs only *generic* preprocessing (resize,
RGB conversion, numpy conversion).  When the real garbage-classification
model (or any future civic-issue model) is integrated, update this module
to match the model's exact requirements:
  • input resolution (e.g. 224×224, 256×256)
  • colour channel order (RGB vs BGR)
  • pixel-value normalisation (0-1, -1 to 1, ImageNet mean/std, etc.)
  • tensor format (numpy, tf.Tensor, torch.Tensor)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from PIL import Image

if TYPE_CHECKING:
    from numpy.typing import NDArray


# Default target size — change to match the real model later
_DEFAULT_TARGET_SIZE: tuple[int, int] = (224, 224)


def preprocess_image(
    image: Image.Image,
    target_size: tuple[int, int] = _DEFAULT_TARGET_SIZE,
    normalise: bool = True,
) -> NDArray[np.float32]:
    """Convert a PIL Image into a preprocessed numpy array.

    Parameters
    ----------
    image:
        A PIL Image (any mode/size).
    target_size:
        (width, height) to resize to.
    normalise:
        If ``True``, scale pixel values to [0, 1].

    Returns
    -------
    numpy.ndarray
        Shape ``(1, height, width, 3)`` — a batch of one RGB image,
        dtype ``float32``.
    """
    # Ensure RGB
    if image.mode != "RGB":
        image = image.convert("RGB")

    # Resize
    image = image.resize(target_size, Image.LANCZOS)

    # Convert to numpy
    arr: NDArray[np.float32] = np.asarray(image, dtype=np.float32)

    # Normalise to [0, 1]
    if normalise:
        arr = arr / 255.0

    # Add batch dimension → (1, H, W, 3)
    arr = np.expand_dims(arr, axis=0)

    return arr
