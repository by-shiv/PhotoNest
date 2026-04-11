from gallery.models import ImageUpload
from gallery.services.clip_model import get_image_embedding

def run():
    count = 0

    for img in ImageUpload.objects.all():
        try:
            emb = get_image_embedding(img.image.path)
            img.embedding = emb
            img.save()
            count += 1
            print(f"Processed {img.id}")

        except Exception as e:
            print(f"Error on {img.id}: {e}")

    print(f"\nDone. {count} images processed.")