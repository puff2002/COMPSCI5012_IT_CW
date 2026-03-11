import io

from PIL import Image, ImageOps, UnidentifiedImageError


LLM_INPUT_MAX_DIMENSION = 1024
LLM_OUTPUT_SIZE = (512, 512)
JPEG_QUALITY = 85


def _crop_to_visible_content(image: Image.Image) -> Image.Image:
    if image.mode != "RGBA":
        return image
    alpha = image.getchannel("A")
    bbox = alpha.getbbox()
    if bbox is None:
        return image
    return image.crop(bbox)


def _resize_to_square_canvas(image: Image.Image, target_size: tuple[int, int], *, background: str) -> Image.Image:
    contained = ImageOps.contain(image, target_size)
    canvas_mode = "RGBA" if background == "transparent" else "RGB"
    canvas_color = (0, 0, 0, 0) if background == "transparent" else (255, 255, 255)
    canvas = Image.new(canvas_mode, target_size, canvas_color)
    offset = (
        (target_size[0] - contained.width) // 2,
        (target_size[1] - contained.height) // 2,
    )
    canvas.paste(contained, offset, contained if contained.mode == "RGBA" else None)
    return canvas


def normalize_image_bytes(
    image_bytes: bytes,
    *,
    output_format: str = "JPEG",
    max_dimension: int = LLM_INPUT_MAX_DIMENSION,
    target_size: tuple[int, int] | None = None,
    crop_to_content: bool = False,
) -> tuple[bytes, str]:
    try:
        with Image.open(io.BytesIO(image_bytes)) as image:
            normalized = ImageOps.exif_transpose(image)
            normalized.thumbnail((max_dimension, max_dimension))
            if crop_to_content:
                normalized = _crop_to_visible_content(normalized.convert("RGBA"))
            if target_size is not None:
                background = "transparent" if output_format.upper() == "PNG" else "white"
                base = normalized.convert("RGBA" if background == "transparent" else "RGB")
                normalized = _resize_to_square_canvas(base, target_size, background=background)

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
