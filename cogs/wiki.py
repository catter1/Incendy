import discord
import os
import json
import nltk
import requests
import shutil
from discord import app_commands
from discord.ext import commands
from mediawiki import MediaWiki, MediaWikiPage
from nltk.tokenize import sent_tokenize
from resources import incendy

class Wiki(commands.Cog):
	def __init__(self, client: incendy.IncendyBot):
		self.client = client

	async def cog_load(self):
		#nltk.download('punkt', quiet=True)
		print(f' - {self.__cog_name__} cog loaded.')

	async def cog_unload(self):
		print(f' - {self.__cog_name__} cog unloaded.')

	@app_commands.command(name="wiki", description="Explore the Stardust Labs Wiki!")
	@incendy.in_bot_channel()
	@app_commands.checks.dynamic_cooldown(incendy.very_long_cd)
	async def wiki(self, interaction: discord.Interaction):
		""" /wiki """

		embed = discord.Embed(
			title="Wiki Surfer (Beta)",
			description="Thanks to <@234748321258799104> and our <@1035916805794955295>s, Stardust Labs has an amazing Wiki for all its projects! This command allows you to search the entire Wiki for whatever information your looking for, and then returning some of the information, as well as links!\n\nPress one of the button below to get started! (Warning: the \"Search Wiki!\" button can sometimes take a **long** time to load - be patient!)",
			color=discord.Colour.brand_red()
		)

		await interaction.response.send_message(embed=embed, view=SearchView(self.client.miraheze))

	async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
		if isinstance(error, app_commands.CommandOnCooldown):
			await interaction.response.send_message("Yikes! " + str(error) + ".", ephemeral=True)
		elif isinstance(error, app_commands.CheckFailure):
			await interaction.response.send_message("This command can only be used in a bot command channel like <#923571915879231509>.", ephemeral=True)
		else:
			raise error

class SearchView(discord.ui.View):
	def __init__(self, miraheze, external: str = "View Wiki Webpage", url: str = "https://stardustlabs.miraheze.org/wiki/Main_page"):
		super().__init__(timeout=None)
		self.add_item(SearchButton(miraheze))
		self.add_item(discord.ui.Button(style=discord.ButtonStyle.url, label=external, url=url))

class SearchButton(discord.ui.Button['Wiki']):
	def __init__(self, miraheze):
		super().__init__(style=discord.ButtonStyle.green, label='Search Wiki!', emoji='<:miraheze:890077957069111316>')
		self.miraheze = miraheze
	
	async def callback(self, interaction: discord.Interaction):
		await interaction.response.send_modal(SearchText(self.miraheze))

class SearchText(discord.ui.Modal, title='Search Box'):
	def __init__(self, miraheze: MediaWiki):
		super().__init__()
		self.miraheze = miraheze

	search_term = discord.ui.TextInput(
		label='Search the Wiki',
		style=discord.TextStyle.short,
		placeholder='Enter your search here...',
		required=True,
		max_length=50
	)

	async def on_submit(self, interaction: discord.Interaction):
		def get_image(info: dict) -> str | None:
			if info["pageprops"].get("image") == None:
				return None
			imgname = info["pageprops"]["image"]

			if imgname.startswith("File:"):
				imgname = imgname.split(":")[1]

			resp = requests.get(
				"https://stardustlabs.miraheze.org/w/api.php",
				params={
					"action": "query",
					"format": "json",
					"list": "allimages",
					"aifrom": imgname,
					"aiprop": "url",
					"ailimit": "1"
				}
			).json()
			
			#if resp["query"]["allimages"][0]["title"] == info["pageprops"].get("image"):
			return resp["query"]["allimages"][0]["url"]
			#else
			#return None
		
		# Get search result titles
		results = self.miraheze.search(self.search_term.value, results=10)
		titles = "|".join(results)
		
		# Do we have results?
		if len(results) == 0:
			embed = discord.Embed(
				color=discord.Colour.brand_red(),
				title=f"Page Results: {self.search_term.value}",
				description="Oops! I found **no results** relating to your search. Click the button below to try again."
			)
			await interaction.response.send_message(embed=embed, view=SearchView(self.miraheze), ephemeral=True)
			return

		# Continue, but wait...
		await interaction.response.defer(thinking=True, ephemeral=True)

		# Create Embed
		embed = discord.Embed(
			color=discord.Colour.brand_red(),
			title=f"Page Results: {self.search_term.value}",
			description="After searching the Stardust Labs Wiki, these are the pages I found matching your search! Select one of the buttons below to get an overview of that page."
		)
		file = discord.File("assets/Wiki_Banner.png", filename="image.png")
		embed.set_image(url="attachment://image.png")
		
		# Get info based on each title
		payload = self.miraheze.wiki_request({"action":"query", "prop":"pageprops", "titles":titles, "format":"json"})["query"]["pages"]
		table = {}
		for pageid, info in payload.items():
			page = self.miraheze.page(pageid=pageid)

			if page.pageid not in [key for key in table.keys()]:
				table[page.pageid] = {
					"page": page,
					"title": page.title.title(),
					"imagefile":get_image(info)
				}

		# Get all the content for each page
		data = {}
		payload = self.miraheze.wiki_request({"action":"parse", "pageid":page.pageid})
		for section in payload["parse"]["sections"]:
			title = section["line"]
			data[title] = {
				"content": page.section(title),
				"toclevel": section["toclevel"]
			}

		# Create all the buttons
		buttons = []
		for key in table.keys():
			buttons.append(
				PageSelectButton(
					miraheze=self.miraheze,
					page=table[key]["page"],
					data=data,
					pagetitle=table[key]["title"],
					imagelink=table[key]["imagefile"]
				)
			)

		view = WikiView(buttons=buttons)
		await interaction.followup.send(embed=embed, file=file, view=view, ephemeral=True)
		
	async def on_error(self, interaction: discord.Interaction, error: Exception):
		await interaction.followup.send('Oops! Something went wrong. Let catter know if the error persists.', ephemeral=True)
		raise error

class WikiView(discord.ui.View):
	def __init__(self, buttons: list[discord.ui.Button]):
		super().__init__(timeout=None)

		for button in buttons:
			self.add_item(button)

class PageSelectButton(discord.ui.Button):
	def __init__(self, miraheze: MediaWiki, page: MediaWikiPage, data: dict, pagetitle: str, imagelink: str):
		super().__init__(
			style=discord.ButtonStyle.green,
			label=pagetitle
		)
		self.miraheze = miraheze
		self.page = page
		self.data = data
		self.pagetitle = pagetitle
		self.imagelink = imagelink
	
	async def callback(self, interaction: discord.Interaction):
		def get_content(content: str) -> str:
			sentences = sent_tokenize(content)
			count = min(len(sentences), 3)
			diff = len(sentences) - count

			if diff > 0:
				for i in range(0, len(sentences) - count):
					sentences.pop()
				#So user can see text was cut off
				sentences.append("...")
			
			final_content = " ".join(sentences)
			return final_content

		# Create Embed
		embed = discord.Embed(
			title=self.pagetitle,
			description=get_content(self.page.summary),
			color=discord.Colour.brand_red()
		)

		# Get/set image
		file = None
		if self.imagelink:
			ext = self.imagelink.split('.')[-1]
			filepath = f"tmp/{self.pagetitle}.{ext}"
			resp = requests.get(self.imagelink, stream=True)
			if resp.status_code == 200:
				with open(filepath, 'wb') as f:
					resp.raw.decode_content = True
					shutil.copyfileobj(resp.raw, f)

				file = discord.File(filepath, filename=f"image.{ext}")
				embed.set_image(url=f"attachment://image.{ext}")

		# Add Section info
		for key in self.data.keys():
			if self.data[key]["toclevel"] < 4:
				content = self.data[key]["content"]
				if content == None:
					continue
				if content.strip() != "" and content.strip() != "WIP":
					embed.add_field(
						name=key,
						value=get_content(self.data[key]["content"]),
						inline=False
					)

		# Edit message
		if file:
			await interaction.response.edit_message(embed=embed, attachments=[file], view=SearchView(self.miraheze, f"View {self.pagetitle} Wikipage", self.page.url))
			os.remove(filepath)
		else:
			await interaction.response.edit_message(embed=embed, attachments=[], view=SearchView(self.miraheze, f"View {self.pagetitle} Wikipage", self.page.url))

async def setup(client):
	await client.add_cog(Wiki(client))