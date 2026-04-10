from .clip_model import get_text_embedding, compute_similarity

def smart_search_filter(query, images):
    query_emb = get_text_embedding(query)

    if hasattr(query_emb, "tolist"):
        query_emb = query_emb.tolist()

    results = []

    for img in images:
        if not img.embedding:
            continue

        try:
            img_emb = img.embedding

            if isinstance(img_emb[0], list):
                img_emb = img_emb[0]

            score = compute_similarity(img_emb, query_emb)

        except Exception as e:
            print(f"[ERROR] IMG {img.id}: {e}")
            continue

        text = (img.caption or "").lower()

        print(f"[DEBUG] IMG {img.id} | score={score:.4f} | caption={text}")

        if score > 0.05 or query.lower() in text:
            results.append((score, img))

    results.sort(key=lambda x: -x[0])

    print(f"[DEBUG] TOTAL MATCHES: {len(results)}")

    return [img for _, img in results]