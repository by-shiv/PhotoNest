from .clip_model import get_text_embedding, compute_similarity
from collections import Counter

CATEGORY_MAP = {
    "dog": "animal",
    "puppy": "animal",
    "goat": "animal",
    "panda": "animal",
    "parrot": "animal",
    "bird": "animal",

    "person": "human",
    "people": "human",
    "man": "human",
    "woman": "human",
    "child": "human",
    "kid": "human",

    "car": "vehicle",
    "truck": "vehicle",
    "bus": "vehicle",
}

ACTION_WORDS = {
    "sitting", "standing", "running", "walking",
    "playing", "looking", "flying", "eating"
}

def get_category(tags):
    for tag in tags:
        if tag in CATEGORY_MAP:
            return CATEGORY_MAP[tag]
    return None

def build_tag_frequency(images):
    counter = Counter()

    for img in images:
        tags = (img.ai_tags or "").lower().split(", ")
        counter.update(tags)

    return counter

def get_tag_importance(tag, tag_freq):
    return 1 / (tag_freq.get(tag, 1)) 

def get_strong_tags(tags, tag_freq):
    tags = [t for t in tags if t and t not in ACTION_WORDS]

    if not tags:
        return set()

    sorted_tags = sorted(tags, key=lambda t: tag_freq.get(t, 0))

    return set(sorted_tags[:2])

def get_weighted_tag_score(target_tags, img_tags, tag_freq):
    score = 0

    for tag in target_tags:
        if tag in img_tags:
            score += get_tag_importance(tag, tag_freq)

    return score

def get_main_tag(tags, tag_freq):
    tags = [t for t in tags if t]

    return min(tags, key=lambda t: tag_freq.get(t, 0)) if tags else None

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

    tag_freq = build_tag_frequency(images)

    target_tags = (target_img.ai_tags or "").lower().split(", ")
    target_strong = get_strong_tags(target_tags, tag_freq)

    target_category = get_category(target_tags)

    results = []

    for img in images:
        if img.id == target_img.id or not img.embedding:
            continue

        img_tags = (img.ai_tags or "").lower().split(", ")
        img_strong = get_strong_tags(img_tags, tag_freq)

        img_category = get_category(img_tags)
        if target_category and img_category:
            if target_category != img_category:
                continue

        try:
            clip_score = compute_similarity(target_img.embedding, img.embedding)

            strong_match = target_strong.intersection(img_strong)

            if len(strong_match) == 0:
                if clip_score < 0.55:
                    continue

            tag_score = get_weighted_tag_score(target_tags, img_tags, tag_freq)
            tag_score = tag_score / (len(target_tags) + 1)

            final_score = (0.6 * clip_score) + (0.4 * tag_score)

            if final_score > 0.32:
                results.append((final_score, img))

        except Exception as e:
            print(f"[ERROR] {e}")

    results.sort(reverse=True, key=lambda x: x[0])

    return [img for score, img in results[:top_k]]