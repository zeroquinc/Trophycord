from PIL import Image
import requests
from io import BytesIO
import numpy as np
import asyncio
import json
from pathlib import Path

from utils.custom_logger import logger

# Cache file path
cache_file_path = Path("src/image_cache.json")

# Function to load cache
def load_cache():
    if not cache_file_path.exists():
        return {}
    with open(cache_file_path, "r") as file:
        return json.load(file)

# Function to save cache
def save_cache(cache):
    with open(cache_file_path, "w") as file:
        json.dump(cache, file)

# Check if the color is colorful
def is_colorful(color):
    r, g, b = color
    return np.std([r, g, b])

# Asynchronous function to get discord color
async def get_discord_color(image_url, crop_percentage=0.5):
    # Load the cache
    cache = load_cache()
    # Check if the URL is already in the cache
    if image_url in cache:
        logger.debug(f"Cache hit for {image_url}")
        return cache[image_url]
    # If not in cache, process the image
    loop = asyncio.get_event_loop()
    color = await loop.run_in_executor(
        None,
        get_discord_color_blocking,
        image_url,
        crop_percentage,
    )
    # Update the cache with the new color
    cache[image_url] = color
    save_cache(cache)
    return color

# Blocking function to get discord color
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