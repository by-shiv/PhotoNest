def clean_caption(caption):
    words = caption.split()

    cleaned = []
    for w in words:
        if not cleaned or cleaned[-1] != w:
            cleaned.append(w)

    return " ".join(cleaned)

def generate_tags_from_caption(caption):
    words = caption.lower().split()

    STOPWORDS = {"a", "the", "in", "on", "at", "with", "and", "of", "is"}

    tags = [w for w in words if w not in STOPWORDS]

    return list(set(tags))[:6]
