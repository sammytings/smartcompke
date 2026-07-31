def __init__(self, media_folder):

    self.indexer = ImageIndexer(media_folder)
    self.indexer.build()

    self.matcher = ImageMatcher(self.indexer)

    self.csv = CSVImageMapper(
        r"C:\Users\user\Downloads\wc-product-export-29-7-2026-1785330184424.csv"
    )
    self.csv.build()

    self.imported = 0
    self.skipped = 0
    self.missing = 0