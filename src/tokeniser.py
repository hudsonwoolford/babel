import re

def tokenise(document: str) -> list:

    document = document.lower()
    pattern = "\w+"

    terms = re.findall(pattern, document)
    return terms