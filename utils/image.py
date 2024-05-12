from PIL import Image
import requests
from io import BytesIO
import numpy as np
from sklearn.cluster import KMeans
import asyncio

def is_colorful(color, tolerance=20, saturation_threshold=50):
    r, g, b = color
    saturation = np.std([r, g, b])
    return (
        saturation > saturation_threshold and
        (abs(r - g) >= tolerance or abs(r - b) >= tolerance or abs(g - b) >= tolerance)
    )

async def get_discord_color(image_url, num_colors=10, crop_percentage=0.5):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        get_discord_color_blocking,
        image_url,
        num_colors,
        crop_percentage,
    )

def get_discord_color_blocking(image_url, num_colors=10, crop_percentage=0.5):
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

    img = img.resize((img.width // 2, img.height // 2))

    img = img.convert("RGB")

    img_array = np.array(img)
    img_flattened = img_array.reshape(-1, 3)

    kmeans = KMeans(n_clusters=num_colors)
    kmeans.fit(img_flattened)

    counts = np.bincount(kmeans.labels_)
    sorted_colors = sorted([(count, color) for count, color in zip(counts, kmeans.cluster_centers_) if is_colorful(color)], reverse=True)

    dominant_color = sorted_colors[0][1] if len(sorted_colors) != 0 else kmeans.cluster_centers_[np.argmax(counts)]

    return int('0x{:02x}{:02x}{:02x}'.format(*dominant_color.astype(int)), 16)