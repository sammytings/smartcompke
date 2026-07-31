import html
import re

from bs4 import BeautifulSoup


class HTMLCleaner:

    @classmethod
    def clean(cls, text):

        if not text:
            return ""

        text = html.unescape(text)

        text = text.replace("\\n", "\n")
        text = text.replace("\\r", "")
        text = text.replace("\\t", " ")

        soup = BeautifulSoup(text, "html.parser")

        for br in soup.find_all("br"):
            br.replace_with("\n")

        for tag in soup.find_all(["p", "div"]):
            tag.append("\n\n")

        for li in soup.find_all("li"):
            li.insert_before("• ")
            li.append("\n")

        for h in soup.find_all(
            ["h1", "h2", "h3", "h4", "h5", "h6"]
        ):
            h.insert_before("\n")
            h.append("\n")

        text = soup.get_text()

        text = text.replace("\xa0", " ")

        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r" *\n *", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()

    @classmethod
    def short_description(cls, text, length=250):

        text = cls.clean(text)

        if len(text) <= length:
            return text

        text = text[:length]

        if " " in text:
            text = text.rsplit(" ", 1)[0]

        return text + "..."