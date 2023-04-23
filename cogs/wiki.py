import discord
import os
import json
import nltk
import requests
import urllib.parse
import shutil
import logging
import asyncpg
import asyncio
import functools
import itertools
import typing
from discord import app_commands
from discord.ext import commands, tasks
from time import perf_counter
from mediawiki import MediaWiki, MediaWikiPage
from nltk.tokenize import sent_tokenize
from thefuzz import process
from libraries import incendy

class Wiki(commands.Cog):
	def __init__(self, client: incendy.IncendyBot):
		self.client = client

	async def cog_load(self):
		#nltk.download('punkt', quiet=True)
		if self.client.environment["INCENDY_WIKI_UPDATE_ENABLED"]:
			self.loop_get_wiki.start()
		else:
			logging.warn("Wiki loop is disabled! Check your environment variable INCENDY_WIKI_UPDATE_ENABLED if this is unintentional.")
		logging.info(f'> {self.__cog_name__} cog loaded')

	async def cog_unload(self):
		if self.client.environment["INCENDY_WIKI_UPDATE_ENABLED"]:
			self.loop_get_wiki.stop()
		logging.info(f'> {self.__cog_name__} cog unloaded')

	### LOOPS ###

	# Thank you SO: https://stackoverflow.com/questions/65881761/discord-gateway-warning-shard-id-none-heartbeat-blocked-for-more-than-10-second
	@tasks.loop(hours=8.0)
	async def loop_get_wiki(self):
		start = perf_counter()
		db_values = await self.get_wiki_content()
		await self.client.db.execute('TRUNCATE wiki;')
		await self.client.db.executemany('INSERT INTO wiki (pageid, title, description, pageurl, imgurl, pagedata) VALUES($1, $2, $3, $4, $5, $6);', db_values)
		stop = perf_counter()
		logging.info(f"Successfully updated the WIKI table. Took {stop - start} seconds ({(stop - start)/60.0} minutes)!")

	@loop_get_wiki.before_loop
	async def before_change_presence(self):
		await self.client.wait_until_ready()

	### OTHER FUNCTIONS ###

	def to_thread(func: typing.Callable) -> typing.Coroutine:
		@functools.wraps(func)
		async def wrapper(*args, **kwargs):
			return await asyncio.to_thread(func, *args, **kwargs)
		return wrapper

	@to_thread
	def get_wiki_content(self) -> list:
		# ### STRUCTURE OF PAGE LIST FOR DB ENTRY ###
		"""
		{
			title: {
				"pageid": pageid,
				"description": description,
				"pageurl": page_url,
				"imgurl": image_url,
				"pagedata": {
					...
				}
			}
		}
		"""

		# Never-nester functions
		def get_image_url(imgname: str) -> str:
			if imgname == None:
				return None
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

			if not resp.get("query"):
				return None
			
			url = resp["query"]["allimages"][0]["url"] 
			return url

		def get_section_content(page: MediaWikiPage, title: str) -> str:
			section = page.section(title)
			if section == None:
				return None
			if section.strip() == "" or section.strip() == "WIP":
				return None
			
			sentences = sent_tokenize(section)
			count = min(len(sentences), 3)
			diff = len(sentences) - count

			if diff > 0:
				for i in range(0, len(sentences) - count):
					sentences.pop()
				#So user can see text was cut off
				sentences.append("...")
			
			final_content = " ".join(sentences)
			return final_content
			

		# Get all page titles in wiki
		pages_raw = self.client.miraheze.wiki_request({"action":"query", "list":"allpages", "apfilterredir":"nonredirects", "aplimit":500, "format":"json"})
		pages = {
			page["title"]: {"pageid": page["pageid"]} #Sets title and pageid
			for page in pages_raw["query"]["allpages"]
			if not (page["title"].startswith("Widget:") or page["title"].endswith("/en"))
		}

		# First loop: get info!
		for item in pages.keys():
			# Get page properties per title
			pageprops = self.client.miraheze.wiki_request({"action":"query", "prop":"pageprops", "titles":item, "format":"json"})["query"]["pages"][str(pages[item]["pageid"])]["pageprops"]
			pages[item]["description"] = pageprops["description"] # Sets the description

			# Do a bunch of pain to find the image url, and set it
			imgname = pageprops.get("image")
			if imgname == None:
				imgname = pageprops.get("page_image_free")
			pages[item]["imgurl"] = get_image_url(imgname)

			# Get the page content
			pagedata = {}
			page = self.client.miraheze.page(pageid=pages[item]["pageid"])
			sections = self.client.miraheze.wiki_request({"action":"parse", "pageid":pages[item]["pageid"], "format":"json"})["parse"]["sections"]
			pages[item]["pageurl"] = page.url # Sets the pageurl

			# Now, get the section content
			for section in sections:
				# Only if the section is important, continue
				if section["toclevel"] < 4:
					title = section["line"]
					section = get_section_content(page, title)
					if section != None:
						pagedata[title.title()] = get_section_content(page, title)

			# Set the page data
			pages[item]["pagedata"] = json.dumps(pagedata)
		
		# Second loop: format info for the DB!
		# pageid INT, title TEXT, description TEXT, pageurl TEXT, imgurl TEXT, pagedata JSON
		db_values = []
		for item in pages.keys():
			value = (pages[item]["pageid"], item, pages[item]["description"], pages[item]["pageurl"], pages[item]["imgurl"], pages[item]["pagedata"])
			db_values.append(value)

		# ...and for the grand finale: return the values!
		return db_values


	### COMMANDS ###

	wiki_group = app_commands.Group(name='wiki', description='Various commands regarding the wiki')

	@wiki_group.command(name="titles", description="Prints a list of all titles in the wiki.")
	@incendy.can_edit_wiki()
	async def titles(self, interaction: discord.Interaction):
		""" /wiki titles """

		await interaction.response.defer(thinking=True, ephemeral=True)

		pages_raw = self.client.miraheze.wiki_request({"action":"query", "list":"allpages", "apfilterredir":"nonredirects", "aplimit":500, "format":"json"})
		pages = [page["title"] for page in pages_raw["query"]["allpages"]]

		with open("tmp/wikipages.txt", 'w') as f:
			f.write("\n".join(pages))
		
		file = discord.File("tmp/wikipages.txt", filename="wikipages.txt")
		await interaction.followup.send("Here is the list of all wiki pages.", file=file, ephemeral=True)

		os.remove("tmp/wikipages.txt")

	@wiki_group.command(name="upload", description="Allows Photographers and Wiki Contributors to upload media to the wiki.")
	@incendy.can_edit_wiki()
	@app_commands.describe(
		name="The name of the media",
		media="The media itself. Must be png, jpg, jpeg, or mp4."
	)
	async def _upload(self, interaction: discord.Interaction, name: str, media: discord.Attachment):
		""" /wiki upload """

		async def login() -> requests.Session:
			wiki_session = requests.Session()
			base_url = "https://stardustlabs.miraheze.org/w/api.php"
			token_params = {"action":"query", "meta":"tokens", "type":"login", "format":"json"}
			login_token = wiki_session.get(url=base_url, params=token_params).json()['query']['tokens']['logintoken']
			login_params = {'action': "clientlogin", 'username': self.client.keys['wiki-username'], 'password': self.client.keys['wiki-password'], 'logintoken': login_token, 'loginreturnurl': 'http://127.0.0.1', 'format': "json"}
			resp = wiki_session.post(url=base_url, data=login_params).json()

			if not resp.get('clientlogin'):
				logging.error(resp)
				return None
			elif resp['clientlogin']['status'] == 'PASS':
				logging.info("Successfully logged into Miraheze Wiki")
				return wiki_session
			else:
				logging.error("Could not log into Miraheze Wiki")
				return None			

		self.client.wiki_session = await login()
		if not self.client.wiki_session:
			await interaction.response.send_message("There was an error logging into the Miraheze Wiki! Try again later. If the issue continues, let catter know.", ephemeral=True)
			return
		
		if media.content_type not in ["image/png", "image/jpeg", "video/mp4"]:
			await interaction.response.send_message("Your attachment is not a valid media type! It must be a png, jpg, jpeg, or mp4. Try again.", ephemeral=True)

		await interaction.response.defer(thinking=True)

		headers = {"User-Agent": self.client.keys["user-agent"], "Content-Type":"application/x-www-form-urlencoded"}
		url = "https://stardustlabs.miraheze.org/w/api.php"

		csrf_params = {"action":"query", "meta":"tokens", "type":"csrf", "format":"json"}
		csrf_token = self.client.wiki_session.post(url=url, data=csrf_params, headers=headers).json()["query"]["tokens"]["csrftoken"]

		media_params = {"action":"upload", "filename":f"{interaction.user.name}_{name}.{media.filename.split('.')[-1]}", "url":media.url, "format":"json", "token":csrf_token}
		media_resp = self.client.wiki_session.post(url=url, data=media_params, headers=headers).json()

		if not media_resp.get("upload"):
			await interaction.followup.send("There was an error uploading your media!", ephemeral=True)
			logging.error("Could not upload media to media!")
			logging.error(media_resp)
			return
		if media_resp["upload"]["result"] != "Success":
			await interaction.followup.send("There was an error uploading your media!", ephemeral=True)
			logging.error("Could not upload media to Wiki!")
			logging.error(media_resp)
			return
		
		if media_resp['upload'].get('imageinfo'):
			await interaction.followup.send(f"Your image has successfully been uploaded to the wiki! You can view it here: {media_resp['upload']['imageinfo']['url']}", ephemeral=False)
		else:
			await interaction.followup.send(f"Your image has successfully been uploaded to the wiki! You can view it here: {media_resp['upload']['videoinfo']['url']}", ephemeral=False)

	@wiki_group.command(name="search", description="Explore the Stardust Labs Wiki!")
	async def search(self, interaction: discord.Interaction):
		""" /wiki search """

		# embed = discord.Embed(
		# 	title="Wiki Surfer",
		# 	description="Thanks to <@234748321258799104> and our other Wiki Contributors, Stardust Labs has an amazing Wiki for all its projects! Too lazy to click on the website link and search there? This command allows you to search the entire Wiki for whatever information your looking for and display it here in Discord instead.\n\nPress one of the button below to get started!",
		# 	color=discord.Colour.brand_red()
		# )

		# view = SearchView(self.client.db)
		# await interaction.response.send_message(embed=embed, view=view)
		await interaction.response.send_modal(SearchText(self.client.db, first=True))

class SearchView(discord.ui.View):
	def __init__(self, db: asyncpg.Pool, label: str = "View Wiki Webpage", url: str = "https://stardustlabs.miraheze.org/wiki/Main_page"):
		super().__init__(timeout=None)
		self.add_item(SearchButton(db))
		self.add_item(discord.ui.Button(style=discord.ButtonStyle.url, label=label, url=url))

class SearchButton(discord.ui.Button):
	def __init__(self, db: asyncpg.Pool):
		super().__init__(style=discord.ButtonStyle.green, label='Search Wiki!', emoji='<:miraheze:890077957069111316>')
		self.db = db
	
	async def callback(self, interaction: discord.Interaction):
		await interaction.response.send_modal(SearchText(self.db))

class SearchText(discord.ui.Modal, title='Search Box'):
	def __init__(self, db: asyncpg.Pool, first: bool = False):
		super().__init__()
		self.db = db
		self.first = first

	search_term = discord.ui.TextInput(
		label='Search the Wiki',
		style=discord.TextStyle.short,
		placeholder='Enter your search here...',
		required=True,
		max_length=50
	)

	async def on_submit(self, interaction: discord.Interaction):
		# Get all titles and perform a fuzzy search
		all_titles = [record['title'] for record in await self.db.fetch('SELECT title FROM wiki;')]
		titles = [
					result[0]
					for result in process.extract(
						self.search_term.value,
						all_titles,
						limit=10
					)
					if result[1] > 70
				]
		
		# If didn't find any, say so
		if len(titles) == 0:
			embed = discord.Embed(
				color=discord.Colour.brand_red(),
				title=f"Page Results: {self.search_term.value}",
				description="Oops! I found **no results** relating to your search. Click the button below to try again."
			)
			if self.first:
				await interaction.response.send_message(embed=embed, view=SearchView(self.db), files=[])
			else:
				await interaction.response.edit_message(embed=embed, view=SearchView(self.db), attachments=[])
			return

		# Create the list of buttons
		buttons = []
		for title in titles:
			buttons.append(PageButton(self.db, label=title))

		# Create embed to display buttons
		embed = discord.Embed(
			color=discord.Colour.brand_red(),
			title=f"Page Results: {self.search_term.value}",
			description="After searching the Stardust Labs Wiki, these are the pages that match closest to your search term! Select one of the buttons below to get an overview of that page."
		)
		file = discord.File("assets/Wiki_Banner.jpg", filename="image.jpg")
		embed.set_image(url="attachment://image.jpg")

		if self.first:
			await interaction.response.send_message(embed=embed, view=WikiView(buttons=buttons), files=[file])
		else:
			await interaction.response.edit_message(embed=embed, view=WikiView(buttons=buttons), attachments=[file])

class PageButton(discord.ui.Button):
	def __init__(self, db: asyncpg.Pool, label: str | None = None):
		super().__init__(style=discord.ButtonStyle.green, label=label)
		self.db = db
		self.title = label

	async def callback(self, interaction: discord.Interaction):
		data = await self.db.fetchrow('SELECT * FROM wiki WHERE title = $1;', self.title)
		pagedata = json.loads(data["pagedata"])
		
		# Main embed init
		embed = discord.Embed(
			title=self.title,
			color=discord.Colour.brand_red(),
			description=data["description"]
		)

		# Set information fields
		for section in itertools.islice(pagedata, 6):
			embed.add_field(name=section, value=pagedata[section], inline=False)
		if len(pagedata.keys()) > 6:
			embed.add_field(name="...", value="This wiki page has too much information to display in Discord! Click the button below to view the page in a web browser.")

		# Magic to set the image
		if data["imgurl"]:
			ext = data["imgurl"].split('.')[-1]
			filepath = f"tmp/{self.title}.{ext}"
			resp = requests.get(data["imgurl"], stream=True)
			if resp.status_code == 200:
				with open(filepath, 'wb') as f:
					resp.raw.decode_content = True
					shutil.copyfileobj(resp.raw, f)

				file = discord.File(filepath, filename=f"image.{ext}")
				embed.set_image(url=f"attachment://image.{ext}")
		else:
			file = None

		# Send the message!
		if file:
			await interaction.response.edit_message(embed=embed, attachments=[file], view=SearchView(self.db, label=f"View {self.title} Wiki page", url=data["pageurl"]))
			os.remove(filepath)
		else:
			await interaction.response.edit_message(embed=embed, attachments=[], view=SearchView(self.db, label=f"View {self.title} Wiki page", url=data["pageurl"]))

class WikiView(discord.ui.View):
	def __init__(self, buttons: list[discord.ui.Button]):
		super().__init__(timeout=None)

		for button in buttons:
			self.add_item(button)

async def setup(client):
	await client.add_cog(Wiki(client))