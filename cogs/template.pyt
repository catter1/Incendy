import logging

import discord
from discord import app_commands
from discord.ext import commands

import libraries.constants as Constants
from libraries import incendy

logger = logging.getLogger(__name__)

class Template(commands.Cog):
	def __init__(self, client: incendy.IncendyBot):
		self.client = client

	async def cog_load(self):
		logger.info(f'> {self.__cog_name__} cog loaded')

	async def cog_unload(self):
		logger.info(f'> {self.__cog_name__} cog unloaded')

async def setup(client):
	await client.add_cog(Template(client))