from PIL import Image
from io import BytesIO


def compress_image(image_bytes):

    image = Image.open(
        BytesIO(image_bytes)
    )

    # Convert transparent images to RGB
    if image.mode in ("RGBA", "LA", "P"):
        image = image.convert("RGB")

    image.thumbnail(
        (1024, 1024)
    )

    output = BytesIO()

    image.save(
        output,
        format="JPEG",
        quality=80,
        optimize=True
    )

    return output.getvalue()