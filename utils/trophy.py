import re
import json

from utils.custom_logger import logger

def format_title(title):
    title = title.lower()  # convert to lowercase
    title = re.sub(r"[^\w\s]", '', title)  # remove special characters except whitespace and underscores
    title = title.replace(' ', '-')  # replace spaces with hyphens
    return f"https://www.playstation.com/games/{title}/"  # prepend base URL

def replace_trophy_with_emoji(trophy_type):
    try:
        with open('config/emoji.json') as f:
            emoji = json.load(f)
        emoji_dict = emoji['emojis']
        return emoji_dict.get(trophy_type.lower(), trophy_type)
    except FileNotFoundError:
        logger.error("Error: emoji.json not found!")
    except json.JSONDecodeError:
        logger.error("Error: emoji.json is not correctly formatted!")