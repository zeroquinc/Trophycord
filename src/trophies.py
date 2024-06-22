from datetime import timedelta
from psnawp_api import PSNAWP

from src.discord import create_trophy_embed, create_simple_trophy_embed, create_platinum_embed, send_trophy_embeds, send_platinum_embeds

from utils.datetime import calculate_total_time, get_current_time
from config.config import PSNTOKEN, TROPHIES_INTERVAL, COMPACT_EMBED

from utils.custom_logger import logger

psnawp = PSNAWP(PSNTOKEN)
profile_picture = {}

def get_client():
    client = psnawp.me()
    online_id = client.online_id
    if online_id in profile_picture:
        client.profile_picture_url = profile_picture[online_id]
        logger.info(f"Loaded profile picture from cache for user {online_id}")
    else:
        logger.info(f"Calling Sony API for profile information for user {online_id}")
        profile_legacy = client.get_profile_legacy()
        profile_picture_url = profile_legacy['profile']['personalDetail']['profilePictureUrls'][0]['profilePictureUrl']
        client.profile_picture_url = profile_picture_url
        profile_picture[online_id] = profile_picture_url
    return client

def get_recent_titles(client, hours=1000): 
    logger.info("Calling Sony API to get recently played games")
    now = get_current_time()
    titles = list(client.title_stats())
    title_ids = [(title.title_id, 'PS5' if 'ps5' in title.category.value else 'PS4') for title in titles if title.last_played_date_time > now - timedelta(hours=hours)]
    for title in titles:
        for id_, platform in title_ids:
            if title.title_id == id_:
                logger.info(f"Found a recently played game: {title.name} ({platform})")
    return title_ids

def get_earned_trophies(client, title_ids):
    trophies = []
    for title_id, platform in title_ids:
        for trophy_title in client.trophy_titles_for_title(title_ids=[title_id]):
            try:
                earned_trophies = client.trophies(np_communication_id=trophy_title.np_communication_id, platform=platform, trophy_group_id='all', include_metadata=True)
                # Add each trophy and its title to the list
                trophies.extend((trophy, {'trophy_title': trophy_title, 'platform': platform}) for trophy in earned_trophies)
                logger.info(f"Calling Sony API to get earned trophies for {trophy_title.title_name} ({platform})")
            except Exception as e:
                logger.error(f"Failed to get trophies for {trophy_title.title_name} ({platform}): {e}")
    return trophies

async def get_earned_and_recent_trophies(client, title_id, platform, TROPHIES_INTERVAL):
    # Get all trophies for the current title_id
    all_trophies = get_earned_trophies(client, [(title_id, platform)])
    # Filter out trophies with None earned date
    earned_trophies = [t for t in all_trophies if t[0].earned_date_time is not None]
    # Sort earned trophies by earned date
    earned_trophies.sort(key=lambda x: x[0].earned_date_time)
    # Calculate total trophies of the game (before filtering for earned_date_time)
    total_trophies = len(all_trophies)
    # Get current time and calculate cutoff time
    now = get_current_time()
    cutoff = now - timedelta(minutes=TROPHIES_INTERVAL)
    recent_trophies = [t for t in earned_trophies if t[0].earned_date_time >= cutoff]
    game_name = all_trophies[0][1]['trophy_title'].title_name if all_trophies else "Unknown"
    logger.info(f"Found {len(recent_trophies)} earned trophies for {game_name} ({platform})")
    return earned_trophies, recent_trophies, total_trophies

async def create_trophy_and_platinum_embeds(client, earned_trophies, recent_trophies, total_trophies):
    trophy_embeds = []
    platinum_embeds = []
    total_trophies_earned = len(earned_trophies)
    starting_count = total_trophies_earned - len(recent_trophies)
    for i, (trophy, trophy_title) in enumerate(recent_trophies):
        if COMPACT_EMBED:
            embed = await create_simple_trophy_embed(trophy, trophy_title, client, starting_count + i + 1, total_trophies)
        else:
            embed = await create_trophy_embed(trophy, trophy_title, client, starting_count + i + 1, total_trophies)
        trophy_embeds.append((trophy.earned_date_time, embed))
        if trophy.trophy_type.name.lower() == 'platinum':
            oldest_trophy = earned_trophies[0]
            newest_trophy = earned_trophies[-1]
            time_diff = newest_trophy[0].earned_date_time - oldest_trophy[0].earned_date_time
            formatted_time_diff = calculate_total_time(time_diff)
            embed = await create_platinum_embed(trophy, trophy_title, client, formatted_time_diff)
            platinum_embeds.append((trophy.earned_date_time, embed))
    return trophy_embeds, platinum_embeds

async def process_trophies_embeds(client, title_ids, TROPHIES_INTERVAL):
    trophy_embeds = []
    platinum_embeds = []
    for title_id, platform in title_ids:
        earned_trophies, recent_trophies, total_trophies = await get_earned_and_recent_trophies(client, title_id, platform, TROPHIES_INTERVAL)
        trophy_embeds_, platinum_embeds_ = await create_trophy_and_platinum_embeds(client, earned_trophies, recent_trophies, total_trophies)
        trophy_embeds.extend(trophy_embeds_)
        platinum_embeds.extend(platinum_embeds_)
    return trophy_embeds, len(recent_trophies), platinum_embeds

async def process_trophies(trophies_channel, platinum_channel):
    client = get_client()
    if title_ids := get_recent_titles(client):
        trophy_embeds, _, platinum_embeds = await process_trophies_embeds(client, title_ids, TROPHIES_INTERVAL)
        # Filter out trophy embeds with None earned date before sorting
        trophy_embeds = [te for te in trophy_embeds if te[0] is not None]
        await send_trophy_embeds(trophies_channel, trophy_embeds)
        await send_platinum_embeds(platinum_channel, platinum_embeds)