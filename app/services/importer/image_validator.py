import hashlib

from PIL import Image


class ImageValidator:
    """
    Rejects tiny, corrupt, duplicate and invalid images.
    """

    MIN_WIDTH = 400
    MIN_HEIGHT = 400

    hashes = set()

    @classmethod
    def validate(cls, file):

        file.seek(0)

        try:

            image = Image.open(file)

            image.verify()

        except Exception:

            return False

        file.seek(0)

        image = Image.open(file)

        if image.width < cls.MIN_WIDTH:
            return False

        if image.height < cls.MIN_HEIGHT:
            return False

        return True

    @classmethod
    def duplicate(cls, file):

        file.seek(0)

        md5 = hashlib.md5(file.read()).hexdigest()

        file.seek(0)

        if md5 in cls.hashes:
            return True

        cls.hashes.add(md5)

        return False