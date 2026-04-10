from gallery.models import ImageUpload
from gallery.services.clip_model import get_image_embedding
from gallery.services.blip_model import generate_caption
from gallery.services.tag_pipeline import generate_tags_from_caption

updated = 0

for img in ImageUpload.objects.all():
    if not img.embedding:
        try:
            caption = generate_caption(img.image.path)
            tags = generate_tags_from_caption(caption)
            emb = get_image_embedding(img.image.path)

            img.caption = caption
            img.ai_tags = ", ".join(tags)
            img.embedding = emb.tolist()
            img.save()

            updated += 1
            print(f"Processed {img.id}")

        except Exception as e:
            print(f"Error on {img.id}: {e}")

print(f"\nReprocessed {updated} images")