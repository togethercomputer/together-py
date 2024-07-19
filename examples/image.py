import base64

from together import Together

client = Together(api_key="04cf1e314be9c686cd14b3881f5c4ad76505af4c93a8d3fe6ef62337114d1d51")

image = client.images.create(
    model="runwayml/stable-diffusion-v1-5",
    prompt="space robots",
    n=1,
)

# Write the image to a file
if image.data and image.data[0] and image.data[0].b64_json:
    image_data = image.data[0].b64_json

    binary_data = base64.b64decode(image_data)

    with open("image.jpg", "wb") as f:
        f.write(binary_data)
