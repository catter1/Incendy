import discord
import os
import json
from discord import app_commands
from discord.ext import commands
from mediawiki import MediaWiki
from resources import custom_checks as cc

class Wiki(commands.Cog):
	def __init__(self, client):
		self.client = client

	async def cog_load(self):
		print(f' - {self.__cog_name__} cog loaded.')

	async def cog_unload(self):
		print(f' - {self.__cog_name__} cog unloaded.')

	@app_commands.command(name="wiki", description="Explore the Stardust Labs Wiki!")
	async def wiki(self, interaction: discord.Interaction):
		""" /wiki """

		embed = discord.Embed(
			title="Wiki Explorer",
			description="Thanks to <@234748321258799104>, Stardust Labs has an amazing Wiki for all its projects! This command allows you to search the entire Wiki for whatever article you're looking for.\n\nPress the button below to get started!",
			color=discord.Colour.brand_red()
		)

		await interaction.response.send_message(embed=embed, view=WikiView())

class WikiView(discord.ui.View):
	def __init__(self):
		super().__init__(timeout=None)
		self.add_item(SearchButton())
		self.add_item(discord.ui.Button(style=discord.ButtonStyle.url, label="View Wiki Webpage", url="https://stardustlabs.miraheze.org/wiki/Main_page"))

class SearchButton(discord.ui.Button['Wiki']):
	def __init__(self):
		super().__init__(style=discord.ButtonStyle.green, label='Search Wiki!', emoji='<:miraheze:890077957069111316>')
	
	async def callback(self, interaction: discord.Interaction):
		await interaction.response.send_modal(SearchText())

class SearchText(discord.ui.Modal, title='Search Box'):
	def __init__(self):
		super().__init__()
		self.miraheze = MediaWiki(
			url="https://stardustlabs.miraheze.org/w/api.php",
			user_agent="catter1/Incendy (catter@zenysis.net)"
		)

	search_term = discord.ui.TextInput(
		label='Search the Wiki',
		style=discord.TextStyle.short,
		placeholder='Enter your search here...',
		required=True,
		max_length=50
	)

	async def on_submit(self, interaction: discord.Interaction):
		await interaction.response.defer(thinking=True)
		search_term = str(self.search_term)

		results = self.miraheze.search(search_term, results=5)
		results += self.miraheze.allpages(query=search_term, results=5)

		pages = []
		for result in results:
			page = self.miraheze.page(result)
			if page.title not in [page.title for page in pages]:
				pages.append(self.miraheze.page(result))

		for page in pages:
			embed = discord.Embed(
				title=page.title,
				description=page.summary,
				colour=discord.Colour.brand_red(),
				url=page.url
			)
			await interaction.followup.send(embed=embed)
		
	async def on_error(self, interaction: discord.Interaction, error: Exception):
		await interaction.followup.send('Oops! Something went wrong. Let catter know if the error persists.', ephemeral=True)
		raise error

async def setup(client):
	await client.add_cog(Wiki(client))