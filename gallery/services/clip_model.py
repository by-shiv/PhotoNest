import torch
import torch.nn.functional as F
from PIL import Image
from io import BytesIO
import pillow_avif

from transformers.models.clip.modeling_clip import CLIPModel
from transformers import CLIPProcessor


model = CLIPModel.from_pretrained(
    "openai/clip-vit-base-patch32"
)

processor = CLIPProcessor.from_pretrained(
    "openai/clip-vit-base-patch32"
)


def get_image_embedding(image_bytes):

    image = Image.open(
        BytesIO(image_bytes)
    ).convert("RGB")

    inputs = processor(
        images=image,
        return_tensors="pt"
    )

    with torch.no_grad():

        features = model.get_image_features(
            pixel_values=inputs["pixel_values"]
        )

    return (
        features[0]
        .cpu()
        .numpy()
        .tolist()
    )


def get_text_embedding(text):

    inputs = processor(
        text=[text],
        return_tensors="pt",
        padding=True
    )

    with torch.no_grad():

        features = model.get_text_features(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"]
        )

    return (
        features[0]
        .cpu()
        .numpy()
        .tolist()
    )


def compute_similarity(img_emb, text_emb):

    img = torch.tensor(img_emb)
    txt = torch.tensor(text_emb)

    img = F.normalize(img, dim=0)
    txt = F.normalize(txt, dim=0)

    return torch.dot(img, txt).item()