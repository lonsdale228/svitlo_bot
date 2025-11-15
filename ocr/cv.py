from io import BytesIO

from PIL import Image


def crop_by_percent(
    image: Image.Image, left=0.0, top=0.0, right=0.0, bottom=0.0
) -> Image.Image:
    width, height = image.size

    left_px = int(width * left)
    top_px = int(height * top)
    right_px = int(width * (1 - right))
    bottom_px = int(height * (1 - bottom))

    cropped = image.crop((left_px, top_px, right_px, bottom_px))

    return cropped


def crop_img(file):
    img = Image.open(file)

    # cropped = crop_by_percent(img, left=0.445, top=0.481, right=0.35, bottom=0.34)
    cropped = crop_by_percent(img, left=0.35, top=0.37, right=0.35, bottom=0.35)

    buf = BytesIO()
    cropped.save(buf, format="JPEG")
    buf.seek(0)

    return buf
