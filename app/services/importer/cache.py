from pathlib import Path
import shutil


class ImageCache:

    def __init__(self):

        self.root = Path("media/import_cache")

        self.root.mkdir(
            parents=True,
            exist_ok=True,
        )

    def product_folder(self, product):

        folder = self.root / str(product.id)

        folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        return folder

    def image_path(self, product, filename):

        return self.product_folder(product) / filename

    def exists(self, product, filename):

        return self.image_path(
            product,
            filename,
        ).exists()

    def clear(self):

        if self.root.exists():

            shutil.rmtree(self.root)

        self.root.mkdir(
            parents=True,
            exist_ok=True,
        )