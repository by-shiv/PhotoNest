from google.cloud import vision

client = vision.ImageAnnotatorClient()

def get_labels(filepath):
    with open(filepath, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = client.label_detection(image=image)

    return [(label.description, label.score) for label in response.label_annotations]