import requests
import os

API_KEY = os.getenv("STABILITY_API_KEY")

def generate_image_from_prompt(prompt):
    if not API_KEY:
        raise Exception("STABILITY_API_KEY not set")

    url = "https://api.stability.ai/v2beta/stable-image/generate/sd3"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "image/*"
    }

    files = {
        "prompt": (None, prompt),
        "output_format": (None, "png"),
    }

    response = requests.post(url, headers=headers, files=files, timeout=60)

    if response.status_code != 200:
        raise Exception(f"Stability Error: {response.text}")

    return response.content


def build_advanced_prompt(query, images):
    tags = []

    for img in images:
        if img.ai_tags:
            tags.extend(img.ai_tags.split(", "))

    tags = list(set(tags))[:8]
    context = ", ".join(tags)

    prompt = f"{query}, {context}, ultra realistic, cinematic lighting, highly detailed, 4k resolution, professional photography, sharp focus"

    return prompt