import re
from pathlib import Path


class ImageIndexer:
    """
    Scans the WordPress uploads folder and builds indexes for:

        1. Exact filename lookup
        2. Normalized filename lookup
        3. Partial filename lookup

    Optimized for WordPress imported product images.
    """

    VALID_EXTENSIONS = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".gif",
        ".bmp",
        ".avif",
    }

    THUMBNAIL_REGEX = re.compile(r"-\d+x\d+$")

    def __init__(self, uploads_folder):

        self.uploads_folder = Path(uploads_folder)

        # normalized name -> image path
        self.images = {}

        # exact filename -> image path
        self.filename_index = {}

        # original filename list for partial searches
        self.all_files = {}

        self.total_images = 0


    def normalize(self, text):

        text = text.lower()

        # remove extension
        text = re.sub(
            r"\.(jpg|jpeg|png|webp|gif|bmp|avif)$",
            "",
            text
        )

        # remove wordpress thumbnail sizes
        text = self.THUMBNAIL_REGEX.sub("", text)

        # remove wordpress scaled images
        text = re.sub(
            r"-scaled(-\d+)?$",
            "",
            text
        )

        # replace separators
        text = text.replace("-", " ")
        text = text.replace("_", " ")

        # remove special characters
        text = re.sub(
            r"[^a-z0-9 ]+",
            "",
            text
        )

        # remove extra spaces
        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()



    def build(self):

        self.images.clear()
        self.filename_index.clear()
        self.all_files.clear()

        self.total_images = 0


        for file in self.uploads_folder.rglob("*"):

            if not file.is_file():
                continue


            if file.suffix.lower() not in self.VALID_EXTENSIONS:
                continue


            self.total_images += 1


            filename = file.name.lower()


            # Exact filename index
            if filename not in self.filename_index:
                self.filename_index[filename] = file


            # Store all files for partial searching
            self.all_files[filename] = file



            # Normalized index
            key = self.normalize(file.stem)


            if key and key not in self.images:
                self.images[key] = file



        return self.images



    def find_by_filename(self, filename):

        if not filename:
            return None


        return self.filename_index.get(
            filename.lower()
        )



    def find(self, text):

        if not text:
            return None


        key = self.normalize(text)


        return self.images.get(key)



    def search_partial(self, stem):

        """
        Partial filename search.

        Example:

        Product:
        HP EliteBook 840 G3

        Image:
        hp-840-g3-1-100x100.jpg

        Returns:
        hp-840-g3-1-100x100.jpg
        """

        if not stem:
            return None


        search = self.normalize(stem)


        if not search:
            return None



        # First try direct partial match
        for filename, path in self.all_files.items():

            clean_name = self.normalize(filename)


            if search in clean_name:
                return path



        # Second attempt: compare words
        words = search.split()


        for filename, path in self.all_files.items():

            clean_name = self.normalize(filename)


            matches = 0


            for word in words:

                if word in clean_name:
                    matches += 1



            # if most words match, accept
            if matches >= max(1, len(words) - 1):
                return path



        return None



    def stats(self):

        return {
            "indexed": len(self.images),
            "total_files": self.total_images,
        }