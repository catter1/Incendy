import discord
from discord import app_commands
from discord.ext import commands
from resources import incendy

class Template(commands.Cog):
	def __init__(self, client: incendy.IncendyBot):
		self.client = client

	async def cog_load(self):
		print(f' - {self.__cog_name__} cog loaded.')

	async def cog_unload(self):
		print(f' - {self.__cog_name__} cog unloaded.')

async def setup(client):
	await client.add_cog(Template(client))