from PIL import Image

def compress_image(image_path):
    img = Image.open(image_path)

    img.thumbnail((1024, 1024))
    img.save(image_path, quality=80, optimize=True)