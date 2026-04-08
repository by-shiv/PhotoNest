STOPWORDS = {"image", "photo", "fun", "event", "object"}

def process_tags(labels):
    # confidence filter
    tags = [name for name, score in labels if score > 0.75]

    # remove stopwords
    tags = [t for t in tags if t.lower() not in STOPWORDS]

    # normalize
    tags = list(set([t.lower().strip() for t in tags]))

    return tags[:5]