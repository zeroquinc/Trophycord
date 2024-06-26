import discord

from utils.image import get_discord_color
from utils.datetime import format_date
from utils.trophy import format_title, replace_trophy_with_emoji

from config.config import DISCORD_IMAGE, STACK_EMBED

from utils.custom_logger import logger

async def create_trophy_embed(trophy, trophy_title_info, client, current, total_trophies):
    trophy_title = trophy_title_info['trophy_title']
    game_url = format_title(trophy_title.title_name)  # format the title name into a URL
    platform = trophy_title_info['platform']
    most_common_color = await get_discord_color(trophy_title.title_icon_url)
    completion = current
    percentage = (completion / total_trophies) * 100
    embed = discord.Embed(title=trophy.trophy_name, description=f"{trophy.trophy_detail}\n\n[{trophy_title.title_name}]({game_url}) ({platform})", color=most_common_color)
    embed.add_field(name="Unlock Ratio", value=f"{trophy.trophy_earn_rate}%", inline=True)
    embed.add_field(name="Rarity", value=replace_trophy_with_emoji(trophy.trophy_type.name.lower()))
    embed.add_field(name="Progress", value=f"{completion}/{total_trophies} ({percentage:.2f}%)", inline=True)
    embed.set_image(url=DISCORD_IMAGE)
    embed.set_thumbnail(url=trophy.trophy_icon_url)
    embed.set_footer(text=f"{client.online_id} • {format_date(trophy.earned_date_time)}", icon_url=client.profile_picture_url)
    embed.set_author(name="Trophy unlocked", icon_url=trophy_title.title_icon_url)
    return embed

async def create_simple_trophy_embed(trophy, trophy_title_info, client, current, total_trophies):
    trophy_title = trophy_title_info['trophy_title']
    game_url = format_title(trophy_title.title_name)  # format the title name into a URL
    most_common_color = await get_discord_color(trophy_title.title_icon_url)
    completion = current
    percentage = (completion / total_trophies) * 100
    embed = discord.Embed(description=f"**{trophy.trophy_name} {replace_trophy_with_emoji(trophy.trophy_type.name.lower())} {trophy.trophy_earn_rate}%**\n{trophy.trophy_detail}\n\n[{trophy_title.title_name}]({game_url})", color=most_common_color)
    embed.set_thumbnail(url=trophy.trophy_icon_url)
    embed.set_footer(text=f"{format_date(trophy.earned_date_time)} • {completion}/{total_trophies} ({percentage:.2f}%)", icon_url=client.profile_picture_url)
    return embed

async def create_platinum_embed(trophy, trophy_title_info, client, formatted_time_diff):
    trophy_title = trophy_title_info['trophy_title']
    game_url = format_title(trophy_title.title_name)  # format the title name into a URL
    platform = trophy_title_info['platform']
    most_common_color = await get_discord_color(trophy_title.title_icon_url)
    embed = discord.Embed(description=f"**[{trophy_title.title_name}]({game_url}) ({platform})**\n\nAchieved in {formatted_time_diff} by [{client.online_id}](https://psnprofiles.com/{client.online_id})\n\n{trophy_title.title_name} has {trophy_title.defined_trophies['bronze']} Bronze, {trophy_title.defined_trophies['silver']} Silver, {trophy_title.defined_trophies['gold']} Gold, and {trophy_title.defined_trophies['platinum']} Platinum trophy\n\nThe Platinum has been achieved by {trophy.trophy_earn_rate}% of players", color=most_common_color)
    embed.add_field(name="Trophy", value=f"[{trophy.trophy_name}]({trophy.trophy_icon_url})", inline=True)
    embed.set_image(url=DISCORD_IMAGE)
    embed.set_thumbnail(url=trophy_title.title_icon_url)
    embed.set_footer(text=f"{client.online_id} • Platinum achieved on {format_date(trophy.earned_date_time)}", icon_url=client.profile_picture_url)
    embed.set_author(name="Platinum Unlocked", icon_url=trophy_title.title_icon_url)
    return embed

async def send_trophy_embeds(trophies_channel, trophy_embeds):
    trophy_embeds.sort(key=lambda x: x[0])  # Sort embeds by trophy earned date
    if trophy_embeds:
        logger.info(f"Sending {len(trophy_embeds)} trophy embeds to {trophies_channel}")
        if STACK_EMBED:
            for i in range(0, len(trophy_embeds), 10):
                batch = trophy_embeds[i:i+10]
                for _, embed in batch:
                    await trophies_channel.send(embed=embed)
        else:
            for _, embed in trophy_embeds:
                await trophies_channel.send(embed=embed)

async def send_platinum_embeds(platinum_channel, platinum_embeds):
    if platinum_embeds:
        logger.info(f"Sending {len(platinum_embeds)} platinum embeds to {platinum_channel}")
        if STACK_EMBED:
            for i in range(0, len(platinum_embeds), 10):
                batch = platinum_embeds[i:i+10]
                for _, embed in batch:
                    await platinum_channel.send(embed=embed)
        else:
            for _, embed in platinum_embeds:
                await platinum_channel.send(embed=embed)