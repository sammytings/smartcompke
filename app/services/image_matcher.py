import re
from difflib import SequenceMatcher


class ImageMatcher:
    """
    Intelligent fallback matcher.

    Order of matching:

    1. Exact normalized filename
    2. Product slug
    3. Product name
    4. Fuzzy similarity
    """

    MIN_SCORE = 0.75

    def __init__(self, indexer):
        self.indexer = indexer

    def normalize(self, text):

        text = text.lower()

        text = re.sub(
            r"\.(jpg|jpeg|png|webp|gif|bmp|avif)$",
            "",
            text,
        )

        text = re.sub(r"-scaled(-\d+)?$", "", text)

        text = re.sub(r"-copy(-\d+)?$", "", text)

        text = re.sub(r"-\d+x\d+$", "", text)

        text = text.replace("-", " ")
        text = text.replace("_", " ")

        text = re.sub(r"[^a-z0-9 ]+", "", text)
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    def similarity(self, a, b):

        return SequenceMatcher(
            None,
            self.normalize(a),
            self.normalize(b),
        ).ratio()

    def match(self, product):

        # -------------------------------------------------
        # Exact match using slug
        # -------------------------------------------------

        image = self.indexer.find(product.slug)

        if image:
            return image

        # -------------------------------------------------
        # Exact match using name
        # -------------------------------------------------

        image = self.indexer.find(product.name)

        if image:
            return image

        # -------------------------------------------------
        # Fuzzy search
        # -------------------------------------------------

        best_path = None
        best_score = 0

        for key, path in self.indexer.images.items():

            score = max(
                self.similarity(product.slug, key),
                self.similarity(product.name, key),
            )

            if score > best_score:
                best_score = score
                best_path = path

        if best_score >= self.MIN_SCORE:
            return best_path

        return None