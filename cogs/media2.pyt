import discord
from discord import app_commands
from discord.ext import commands
from resources import custom_checks as cc

class Media(commands.Cog):
	def __init__(self, client: incendy.IncendyBot):
		self.client = client

	async def cog_load(self):
		print(f' - {self.__cog_name__} cog loaded.')

	async def cog_unload(self):
		print(f' - {self.__cog_name__} cog unloaded.')

	async def links():
		{
			"linked roles community post": "https://support.discord.com/hc/en-us/articles/10388356626711-Connections-Linked-Roles-Admins",
			"application role connection metadata" : "https://discord.com/developers/docs/resources/application-role-connection-metadata",
			"make your own tutorial": "https://discord.com/developers/docs/tutorials/configuring-app-metadata-for-linked-roles",
			"js example bot": "https://github.com/discord/linked-roles-sample/blob/main/src/discord.js",
			"general oauth2 discord info": "https://discord.com/developers/docs/topics/oauth2"
		}

async def setup(client):
	await client.add_cog(Media(client))