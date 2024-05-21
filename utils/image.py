from PIL import Image
import requests
from io import BytesIO
import numpy as np
import asyncio

def is_colorful(color):
    r, g, b = color
    return np.std([r, g, b])

async def get_discord_color(image_url, crop_percentage=0.5):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        get_discord_color_blocking,
        image_url,
        crop_percentage,
    )

def get_discord_color_blocking(image_url, crop_percentage=0.5):
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    width, height = img.size
    crop_width = int(width * crop_percentage)
    crop_height = int(height * crop_percentage)
    left = (width - crop_width) // 2
    top = (height - crop_height) // 2
    right = left + crop_width
    bottom = top + crop_height
    img = img.crop((left, top, right, bottom))
    img = img.convert("RGB")
    img_array = np.array(img)
    img_flattened = img_array.reshape(-1, 3)
    colorfulness = np.apply_along_axis(is_colorful, 1, img_flattened)
    most_colorful_color = img_flattened[np.argmax(colorfulness)]
    return int('0x{:02x}{:02x}{:02x}'.format(*most_colorful_color), 16)