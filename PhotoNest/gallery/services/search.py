def smart_search_filter(query, images):
    query_words = query.lower().split()

    results = []

    for img in images:
        text = " ".join([
            img.title or "",
            img.tags or "",
            img.ai_tags or "",
            img.description or ""
        ]).lower()

        score = 0

        for word in query_words:
            if word in text:
              score += 2  # strong match
            if img.ai_tags and word in img.ai_tags.lower():
              score += 1
            if not images:
              images = base_images.order_by('-upload_date')[:10]

        if score > 0:
            results.append((score, img))

    # sort by relevance + latest
    results.sort(key=lambda x: (-x[0], -x[1].upload_date.timestamp()))

    return [img for _, img in results]