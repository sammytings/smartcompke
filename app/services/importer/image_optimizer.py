from io import BytesIO

from PIL import Image, ImageOps


class ImageOptimizer:
    """
    Produces clean, sharp product images suitable for e-commerce.

    • Removes EXIF rotation
    • Converts RGBA/P images to RGB
    • Resizes only if extremely large
    • Saves high-quality JPEG
    """

    MAX_SIZE = (2200, 2200)

    JPEG_QUALITY = 96

    @classmethod
    def optimize(cls, temp_file):

        temp_file.seek(0)

        image = Image.open(temp_file)

        image = ImageOps.exif_transpose(image)

        if image.mode in ("RGBA", "LA", "P"):

            background = Image.new(
                "RGB",
                image.size,
                (255, 255, 255),
            )

            if image.mode == "P":
                image = image.convert("RGBA")

            background.paste(
                image,
                mask=image.split()[-1],
            )

            image = background

        elif image.mode != "RGB":

            image = image.convert("RGB")

        if (
            image.width > cls.MAX_SIZE[0]
            or image.height > cls.MAX_SIZE[1]
        ):

            image.thumbnail(
                cls.MAX_SIZE,
                Image.LANCZOS,
            )

        output = BytesIO()

        image.save(

            output,

            format="JPEG",

            optimize=True,

            quality=cls.JPEG_QUALITY,

            subsampling=0,
        )

        output.seek(0)

        return output

    @classmethod
    def valid(cls, temp_file):

        try:

            temp_file.seek(0)

            img = Image.open(temp_file)

            img.verify()

            temp_file.seek(0)

            return True

        except Exception:

            return False