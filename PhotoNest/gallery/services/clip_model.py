import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import torch.nn.functional as F

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")


def get_image_embedding(image_path):
    image = Image.open(image_path).convert("RGB")
    inputs = processor(images=image, return_tensors="pt")

    with torch.no_grad():
        image_features = model.get_image_features(**inputs)

    return image_features[0].numpy()


def get_text_embedding(text):
    inputs = processor(text=[text], return_tensors="pt", padding=True)

    with torch.no_grad():
        text_features = model.get_text_features(**inputs)

    return text_features[0].numpy()


def compute_similarity(img_emb, text_emb):
    try:
        img_tensor = torch.tensor(img_emb, dtype=torch.float32)
        text_tensor = torch.tensor(text_emb, dtype=torch.float32)

        img_tensor = img_tensor.flatten()
        text_tensor = text_tensor.flatten()

        img_tensor = F.normalize(img_tensor, dim=0)
        text_tensor = F.normalize(text_tensor, dim=0)

        similarity = torch.dot(img_tensor, text_tensor).item()

        return similarity

    except Exception as e:
        print(f"[SIM ERROR] {e}")
        return 0.0