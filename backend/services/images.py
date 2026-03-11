import io

from PIL import Image, ImageOps, UnidentifiedImageError


MAX_IMAGE_DIMENSION = 1600
JPEG_QUALITY = 85


def normalize_image_bytes(
    image_bytes: bytes,
    *,
    output_format: str = "JPEG",
    max_dimension: int = MAX_IMAGE_DIMENSION,
) -> tuple[bytes, str]:
    try:
        with Image.open(io.BytesIO(image_bytes)) as image:
            normalized = ImageOps.exif_transpose(image)
            normalized.thumbnail((max_dimension, max_dimension))

            buffer = io.BytesIO()
            if output_format.upper() == "PNG":
                normalized.convert("RGBA").save(buffer, format="PNG", optimize=True)
                return buffer.getvalue(), "image/png"

            normalized.convert("RGB").save(
                buffer,
                format="JPEG",
                quality=JPEG_QUALITY,
                optimize=True,
            )
            return buffer.getvalue(), "image/jpeg"
    except UnidentifiedImageError as exc:
        raise ValueError("unsupported or corrupted image") from exc
