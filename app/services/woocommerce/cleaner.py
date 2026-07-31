import re

from bs4 import BeautifulSoup


class HTMLCleaner:
    """
    Converts WooCommerce HTML into clean readable text.
    """

    @staticmethod
    def clean(html):

        if not html:
            return ""

        soup = BeautifulSoup(html, "html.parser")

        # remove scripts/styles
        for tag in soup(["script", "style", "iframe"]):
            tag.decompose()

        # convert <br> into newlines
        for br in soup.find_all("br"):
            br.replace_with("\n")

        text = soup.get_text("\n")

        text = re.sub(r"\n{3,}", "\n\n", text)

        text = re.sub(r"[ \t]+", " ", text)

        return text.strip()