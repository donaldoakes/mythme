import hashlib


def trim_article(title: str) -> str:
    if title.lower().startswith("a "):
        return title[2:]
    elif title.lower().startswith("an "):
        return title[3:]
    elif title.lower().startswith("the "):
        return title[4:]
    else:
        return title


def gen_hash(unique: str) -> str:
    """16 char hex hash code."""
    hexstr = hashlib.sha256(unique.encode("utf-8")).hexdigest()
    return hexstr[:8] + hexstr[-8:]
