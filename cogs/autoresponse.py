import discord
import logging
import re
import io
import gzip
import json
import requests
import validators
from discord import app_commands
from discord.ext import commands
from lxml import etree
from libraries import incendy
import libraries.constants as Constants

class Autoresponse(commands.Cog):
	def __init__(self, client: incendy.IncendyBot):
		self.client = client

	async def cog_load(self):
		with open('resources/textlinks.json', 'r') as f:
			self.textlinks = json.load(f)
		with open('resources/reposts.json', 'r') as f:
			self.reposts = json.load(f)

		apollo_resp = requests.get("https://www.worldgen.dev/sitemap.xml")
		root = etree.fromstring(apollo_resp.content, parser=etree.XMLParser(recover=True, encoding='utf-8'))

		loc_elements = root.xpath("//ns:loc", namespaces={"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"})
		apollo_links = [element.text for element in loc_elements]
		self.apollo_urls = {url.split('/')[-2]: url for url in apollo_links if len(url.split("/")) > 4 and not url.split('/')[-2].startswith("_")}

		misode_resp = requests.get("https://misode.github.io/sitemap.txt")
		self.misode_urls = {url.split('/')[-2]: url for url in misode_resp.text.split("\n") if len(url.split("/")) > 4}

		self.wiki_urls = {record['title'].lower(): record['pageurl'] for record in await self.client.db.fetch('SELECT title, pageurl FROM wiki ORDER BY title;')}

		logging.info(f'> {self.__cog_name__} cog loaded')

	async def cog_unload(self):
		logging.info(f'> {self.__cog_name__} cog unloaded')

	
	### EVENTS ###

	async def do_textlinks(self, message: discord.Message, matches: list) -> None:
		links = []
		for match in matches:

			# General matches
			if match.lower() in [textlink for textlink in self.textlinks]:
				links.append(discord.ui.Button(style=discord.ButtonStyle.link, label=match.lower().title(), url=self.textlinks[match.lower()]["link"], emoji=self.textlinks[match.lower()]["icon"]))

			elif "|" in match:

				if "misode" in match.split("|")[0].lower():
					page = match.split("|")[-1].lower().replace(" ", "-")
					if page in self.misode_urls.keys():
						links.append(discord.ui.Button(style=discord.ButtonStyle.link, label=f"Misode: {page.replace('-', ' ').title()}", url=self.misode_urls[page], emoji=Constants.Emoji.MISODE))

				elif "worldgen" in match.split("|")[0].lower():
					page = match.split("|")[-1].lower().replace(" ", "-")
					if page in self.apollo_urls.keys():
						links.append(discord.ui.Button(style=discord.ButtonStyle.link, label=f"Worldgen: {page.replace('-', ' ').title()}", url=self.apollo_urls[page]))
				
				elif "wiki" in match.split("|")[0].lower():
					page = match.split("|")[-1].lower()
					if page in self.wiki_urls.keys():
						links.append(discord.ui.Button(style=discord.ButtonStyle.link, label=f"Wiki: {page.title()}", url=self.wiki_urls[page], emoji=Constants.Emoji.MIRAHEZE))

				elif match.split("|")[0].lower() in ["mc", "mcpe", "realms"]:
					bug_id = match.split("|")[-1].lower()
					if bug_id.isdigit():
						links.append(discord.ui.Button(style=discord.ButtonStyle.link, label=f"{match.split('|')[0].upper()} {bug_id}", url=f"https://bugs.mojang.com/browse/{match.split('|')[0].upper()}-{bug_id}", emoji=Constants.Emoji.MOJIRA))

		view = discord.ui.View()
		if len(links) > 0:
			for item in links:
				view.add_item(item)
			await message.reply(view=view, mention_author=False)

	async def do_pastebin(self, message: discord.Message) -> None:
		for file in message.attachments:
			
			if any(ext in file.filename for ext in [".log", ".txt", ".log.gz"]):
				
				# Read log or gzip content
				if file.filename.endswith(".log.gz"):
					bts = await file.read()

					with gzip.GzipFile(fileobj=io.BytesIO(bts), mode='rb') as gz:
						content = gz.read().decode('utf-8')
				else:
					bts = await file.read()
					content = bts.decode('utf-8')
				
				# Send content to mclo.gs
				headers = {'Content-Type': 'application/x-www-form-urlencoded'}
				url = "https://api.mclo.gs/1/log"
				data = {"content": f"{content}"}
				x = requests.post(url, data=data, headers=headers)

				# Init button
				logurl = json.loads(x.text)["url"]
				view = discord.ui.View()
				view.add_item(discord.ui.Button(style=discord.ButtonStyle.link, label=file.filename, url=logurl, emoji=Constants.Emoji.MCLOGS))

				# Check for issues
				scanner = LogScanner(content)
				embed = scanner.scan("embed")

				# Send message
				await message.reply(view=view, embed=embed, mention_author=False)

	async def stop_mod_reposts(self, message: discord.Message, url: str) -> None:
		for illegal in self.reposts:
			if illegal["domain"] in url:
				if illegal["path"] != "/" and illegal["path"] not in url:
					continue
				embed = discord.Embed(
					title="WARNING: Illegal Mod Distribution Site!",
					description=f"The site `{illegal['domain']}` has been marked by [StopModReposts](https://stopmodreposts.org/) as a website that illegally redistributes mods. You should **not** download anything from here!",
					color=discord.Colour.red()
				)
				if illegal["notes"] != "/":
					embed.add_field(
						name="Additional Notes:",
						value=illegal["notes"]
					)

				await message.reply(embed=embed, mention_author=False)
				return


	@commands.Cog.listener()
	async def on_message(self, message: discord.Message):
		if not message.author.bot:

			# Textlinks
			matches = re.findall(r"[\[]{2}(\w[\w |':]+\w)?[\]]{2}", message.content)
			if len(matches) > 0:
				await self.do_textlinks(message=message, matches=matches)

			# Pastebin feature
			if len(message.attachments) > 0:
				await self.do_pastebin(message=message)

			# Stop Mod Reposts
			for word in message.content.split():
				if validators.url(word):
					await self.stop_mod_reposts(message=message, url=word)

class LogScanner:
	"""
	A class representing the contents of a log file, able to do scans on itself.

	Attributes
	-----
	`contents`
		A string of utf-8 encoded text
	`responses`
		List of all issues found
	"""
	def __init__(self, contents: str) -> None:
		self.contents = contents
		self.responses = []
		self._precip = False

	def scan(self, resp: str) -> list | discord.Embed | None:
		"""
		Scan the contents of the log for hanging fruit errors.

		Parameters:
			`resp` - Either "list" or "embed". For return type.

		Returns:
			A list of `responses`. `None` if no issues found.
		or
			An embed encoded with all the `responses`. `None` if no issues found.
		"""

		if resp.lower().strip() not in ["list", "embed"]:
			raise ValueError("Must be either 'list' or 'embed'")
		
		resp = resp.lower().strip()

		self.check_precipitation()
		self.check_messy_uninstall()
		self.check_nullscape_seedfix()
		self.check_plugin_installation()
		self.check_auditory_incendium()

		if resp == "list":
			if len(self.responses) == 0:
				return None
			
			return self.responses
		else:
			if len(self.responses) == 0:
				return None
			
			nl = '\n'
			embed = discord.Embed(
				title="[Auto Scanner]",
				color=discord.Colour.dark_magenta(),
				description=f"I've taken a glance at your log. Here are some potential issues I found!\n\n{nl.join(['**•** ' + resp for resp in self.responses])}"
			)
			embed.set_footer(text="How was my response? Let me know!")

			return embed
	
	def check_precipitation(self) -> None:
		precipitation_3 = re.search(r"No key precipitation in MapLike", self.contents)
		precipitation_4 = re.search(r"No key has_precipitation in MapLike", self.contents)

		if precipitation_3:
			error = "Your game/server is running 1.19.3, but one or more of your worldgen datapacks is made for 1.19.4. Update your server, or download the correct versions of your datapack(s)."
			self.responses.append(error)
			self._precip = True
			return
		
		if precipitation_4:
			error = "Your game/server is running 1.19.4, but one or more of your worldgen datapacks is made for 1.19.3. Downgrade your server, or download the correct versions of your datapack(s)."
			self.responses.append(error)
			self._precip = True
			return
		
		return
	
	def check_messy_uninstall(self) -> None:
		failed = re.search(r"Failed to get element ResourceKey\[minecraft:worldgen/biome / (?P<Namespace>[a-z]+):(?P<Biome>[a-z_\-\/]+)\]", self.contents)
		unbound = re.search(r"Unbound values in registry ResourceKey\[minecraft:root / minecraft:worldgen/biome]: \[(?P<Namespace>[a-z]+):(?P<Biome>[a-z_\-\/]+)", self.contents)

		if failed or unbound and not self._precip:
			if failed:
				pack = failed.group(1).title()
			else:
				pack = unbound.group(1).title()

			error = f"It appears {pack} was uninstalled incorrectly. Biomes must be removed from the `level.dat` - see `/faq Removing Worldgen Packs`."
			self.responses.append(error)
			return
		
		return
	
	def check_nullscape_seedfix(self) -> None:
		seedfix = re.search(r"Exception in thread \"main\" java\.lang\.module\.ResolutionException: Modules ([a-z_-]+) and ([a-z_-]+) export package net\.hypercubemc\.seedfix to module ([a-z_-]+)", self.contents)
		nullscape = re.search(r"Nullscape_1\.18\.2_v1\.1\.3\.jar", self.contents)

		if seedfix and nullscape:
			error = f"You are using Nullscape 1.1.3, which currently has issues with its Seedfix implementation. Downgrade to Nullscape 1.1.2 until we provide a more permanent solution."
			self.responses.append(error)
			return
		
		return
	
	def check_plugin_installation(self) -> None:
		plugin = re.search(r"Error loading plugin: File 'plugins\\(?P<Datapack>Terralith|Incendium|Nullscape|Amplified_Nether|Structory|Continents|Structory_Towers)", self.contents)

		if plugin:
			pack = plugin.group(1).replace('_', ' ').title()
			error = f"You have installed {pack} as a plugin! The `jar` versions of our projects are mods, not plugins. To use {pack} on a Spigot/Paper server, use the datapack version and put it in the `world/datapacks` folder."
			self.responses.append(error)
			return
		
		return
	
	def check_auditory_incendium(self) -> None:
		auditory = re.search(r"auditory\$onHit", self.contents)
		enderpearl = re.search(r"(ThrownEnderpearlMixin|EnderPearlSoundMixin|EnderPearlEntityMixin)", self.contents)

		if auditory:
			error = f"This is an [issue with Auditory](https://github.com/Sydokiddo/auditory/issues/32). In the meantime, this can be fixed by disabling {'enderpearl' if enderpearl else 'the problem'} sounds in the Auditory config."
			self.responses.append(error)
			return
		
		return


async def setup(client):
	await client.add_cog(Autoresponse(client))