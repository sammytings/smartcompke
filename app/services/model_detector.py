import re


MODEL_PATTERNS = [

    r"[A-Z]{2,5}-[A-Z0-9]{3,}",

    r"[A-Z0-9]{5,20}"

]


def detect_model(text):

    for pattern in MODEL_PATTERNS:

        match = re.search(pattern, text)

        if match:

            return match.group()

    return ""