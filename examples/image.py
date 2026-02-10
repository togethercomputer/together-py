import base64

from together import Together
from together.types.image_data_b64 import ImageDataB64

client = Together()

image = client.images.generate(
    model="runwayml/stable-diffusion-v1-5",
    prompt="space robots",
    n=1,
)

# Write the image to a file
if image.data and image.data[0] and isinstance(image.data[0], ImageDataB64):
    image_data = image.data[0].b64_json

    binary_data = base64.b64decode(image_data)

    with open("image.jpg", "wb") as f:
        f.write(binary_data)
