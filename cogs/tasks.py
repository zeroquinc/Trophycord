import asyncio
from discord.ext import tasks, commands
from src.trophies import process_trophies
from utils.datetime import delay_until_next_interval
from config.config import TROPHIES_INTERVAL, TROPHIES_CHANNEL_ID, PLATINUM_CHANNEL_ID, TASK_START_DELAY
from utils.custom_logger import logger

class TasksCog(commands.Cog):
    def __init__(self, bot: commands.Bot, start_delay: dict = None) -> None:
        self.bot = bot
        self.start_delay = start_delay or {}
        self.process_trophies.start()  # Always start the task when the cog is loaded

    @tasks.loop(minutes=TROPHIES_INTERVAL)
    async def process_trophies(self):
        trophies_channel = self.bot.get_channel(TROPHIES_CHANNEL_ID)
        platinum_channel = self.bot.get_channel(PLATINUM_CHANNEL_ID)
        try:
            await process_trophies(trophies_channel, platinum_channel)
        except Exception as e:
            logger.error(f'Error processing trophies: {e}')

    @process_trophies.before_loop
    async def before_process_trophies(self):
        await self.bot.wait_until_ready()  # Wait until the bot has connected to the discord API
        if self.start_delay.get('process_trophies', False):  # Only delay the start of the task if its value in the start_delay dictionary is True
            delay = delay_until_next_interval('trophies')  # Calculate the delay
            logger.info(f'Waiting {delay} seconds for Trophies task to start')
            await asyncio.sleep(delay)  # Wait for the specified delay

async def setup(bot):
    await bot.add_cog(TasksCog(bot, start_delay=TASK_START_DELAY))