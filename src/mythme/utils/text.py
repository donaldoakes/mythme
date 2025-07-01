def trim_article(title: str) -> str:
    if title.lower().startswith("a "):
        return title[2:]
    elif title.lower().startswith("an "):
        return title[3:]
    elif title.lower().startswith("the "):
        return title[4:]
    else:
        return title
