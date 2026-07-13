from transformers import (
    BlipProcessor,
    BlipForConditionalGeneration
)

from PIL import Image
from io import BytesIO
import torch


processor = BlipProcessor.from_pretrained(
    "Salesforce/blip-image-captioning-base"
)

model = BlipForConditionalGeneration.from_pretrained(
    "Salesforce/blip-image-captioning-base"
)


def generate_caption(image_bytes):

    image = Image.open(
        BytesIO(image_bytes)
    ).convert("RGB")

    inputs = processor(
        images=image,
        return_tensors="pt"
    )

    with torch.no_grad():

        out = model.generate(
            **inputs,
            max_new_tokens=50,
            repetition_penalty=1.2
        )

    return processor.decode(
        out[0],
        skip_special_tokens=True
    )