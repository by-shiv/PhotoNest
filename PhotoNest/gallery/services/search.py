from .clip_model import get_text_embedding, compute_similarity

def expand_query(query):
    synonyms = {
        "dog": ["dog", "puppy"],
        "puppy": ["dog", "puppy"],
        "human": ["human", "person", "people", "man", "woman"],
        "people": ["people", "person", "human", "crowd"],
        "car": ["car", "vehicle", "automobile"],
        "bird": ["bird", "parrot", "sparrow"],
    }

    return synonyms.get(query.lower(), [query.lower()])


def smart_search_filter(query, images):
    from .clip_model import get_text_embedding, compute_similarity

    expanded_queries = expand_query(query)

    query_embeddings = [get_text_embedding(q) for q in expanded_queries]

    results = []

    for img in images:
        if not img.embedding:
            continue

        try:
            best_score = 0
            keyword_match = False

            caption = (img.caption or "").lower()
            tags = (img.ai_tags or "").lower()

            for i, q in enumerate(expanded_queries):
                score = compute_similarity(img.embedding, query_embeddings[i])
                best_score = max(best_score, score)

                if q in caption or q in tags:
                    keyword_match = True

            if best_score > 0.26 or keyword_match:
                boost = 0.12 if keyword_match else 0
                results.append((best_score + boost, img))

        except Exception as e:
            print(f"[ERROR] IMG {img.id}: {e}")

    results.sort(reverse=True, key=lambda x: x[0])

    return [img for score, img in results]

def get_similar_images(target_img, images, top_k=8):
    from .clip_model import compute_similarity

    if not target_img.embedding:
        return []

    target_tags = set((target_img.ai_tags or "").lower().split(", "))

    results = []

    for img in images:
        if img.id == target_img.id or not img.embedding:
            continue

        try:
            clip_score = compute_similarity(target_img.embedding, img.embedding)

            img_tags = set((img.ai_tags or "").lower().split(", "))

            common_tags = target_tags.intersection(img_tags)

            if len(common_tags) == 0:
                continue

            tag_score = len(common_tags) / len(target_tags)
            final_score = (0.6 * clip_score) + (0.4 * tag_score)

            print(f"[SIM] IMG {img.id} | clip={clip_score:.3f} tags={common_tags}")

            
            if final_score > 0.25:
                results.append((final_score, img))

        except Exception as e:
            print(f"[ERROR] Similar IMG {img.id}: {e}")

    results.sort(reverse=True, key=lambda x: x[0])

    return [img for score, img in results[:top_k]]