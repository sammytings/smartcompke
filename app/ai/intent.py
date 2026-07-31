import re


class Intent:
    GREETING = "greeting"
    PRODUCT = "product"
    ORDER = "order"
    REPAIR = "repair"
    UNKNOWN = "unknown"


def detect(message):
    text = message.lower().strip()

    if re.search(r"\b(hello|hi|hey)\b", text):
        return Intent.GREETING

    if "laptop" in text:
        return Intent.PRODUCT

    if "order" in text:
        return Intent.ORDER

    if "repair" in text:
        return Intent.REPAIR

    return Intent.UNKNOWN