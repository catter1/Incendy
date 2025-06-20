from typing import Any
import discord
import logging
import re
import io
import gzip
import json
import requests
import validators
import datetime
from discord.ext import commands
from lxml import etree
from lzstring import LZString
from libraries import incendy
import libraries.constants as Constants

class Autoresponse(commands.Cog):
	def __init__(self, client: incendy.IncendyBot):
		self.client = client

	async def cog_load(self):
		self.lz = LZString()
		with open('resources/textlinks.json', 'r') as f:
			self.textlinks: dict = json.load(f)
		with open('resources/reposts.json', 'r') as f:
			self.reposts = json.load(f)

		try:
			sawdust_resp = requests.get("https://sawdust.catter1.com/sitemap.xml")
			sawdust_root = etree.fromstring(sawdust_resp.content, parser=etree.XMLParser(recover=True, encoding='utf-8'))
			sawdust_loc_elements = sawdust_root.xpath("//ns:loc", namespaces={"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"})
			sawdust_links = [element.text for element in sawdust_loc_elements]
			self.sawdust_urls = {url.split('/')[-2]: url for url in sawdust_links if len(url.split("/")) > 4 and not url.split('/')[-2].startswith("_")}
		except requests.exceptions.ConnectionError:
			self.sawdust_urls = {}

		try:
			misode_resp = requests.get("https://misode.github.io/sitemap.txt")
			self.misode_urls = {url.split('/')[-2]: url for url in misode_resp.text.split("\n") if len(url.split("/")) > 4}
		except requests.exceptions.ConnectionError:
			self.misode_urls = {}
			
		self.map_packs = ["terralith", "incendium", "nullscape", "structory", "structory-towers", "continents", "amplified-nether", "strayed-fates-forsaken", "tectonic", "terratonic", "dungeons-and-taverns", "geophilic", "explorify", "towns-and-towers", "ct-overhaul-village"]

		self.wiki_urls = {record['title'].lower(): record['pageurl'] for record in await self.client.db.fetch('SELECT title, pageurl FROM wiki ORDER BY title;')}

		logging.info(f'> {self.__cog_name__} cog loaded')

	async def cog_unload(self):
		logging.info(f'> {self.__cog_name__} cog unloaded')

	
	### EVENTS ###

	async def do_textlinks(self, matches: list) -> discord.ui.View | None:
		links = []
		for match in matches:

			# General matches
			if match.lower() in [textlink for textlink in self.textlinks]:
				emoji = self.textlinks[match.lower()]["icon"] if self.textlinks[match.lower()]["icon"] != "" else None
				links.append(discord.ui.Button(style=discord.ButtonStyle.link, label=match.lower().title(), url=self.textlinks[match.lower()]["link"], emoji=emoji))

			elif "|" in match:

				if "misode" in match.split("|")[0].lower():
					page = match.split("|")[-1].lower().replace(" ", "-")
					if page in self.misode_urls.keys():
						links.append(discord.ui.Button(style=discord.ButtonStyle.link, label=f"Misode: {page.replace('-', ' ').title()}", url=self.misode_urls[page], emoji=Constants.Emoji.MISODE))
	
				elif "sawdust" in match.split("|")[0].lower():
					page = match.split("|")[-1].lower().replace(" ", "-")
					if page in self.sawdust_urls.keys():
						links.append(discord.ui.Button(style=discord.ButtonStyle.link, label=f"Sawdust: {page.replace('-', ' ').title()}", url=self.sawdust_urls[page], emoji=Constants.Emoji.SEEDFIX))
				
				elif "wiki" in match.split("|")[0].lower():
					full = match.split("|")[-1]
					page = full.split("#")[0].lower()
					if page in self.wiki_urls.keys():
						header = "" if len(full.split("#")) <= 1 else f"#{full.split('#')[-1].title().replace(' ', '_')}"
						links.append(discord.ui.Button(style=discord.ButtonStyle.link, label=f"Wiki: {page.title()}", url=f"{self.wiki_urls[page]}{header}", emoji=Constants.Emoji.MIRAHEZE))

				elif "map" in match.split("|")[0].lower():
					full = match.split("|")[-1]					
					packs = full.replace(", ", ",").lower().replace(" ", "-").split(",")
					overlap = [pack for pack in packs if pack in self.map_packs]

					if overlap:
						if "terralith" in overlap and "tectonic" in overlap:
							overlap[overlap.index("tectonic")] = "terratonic"

						if "terralith" in overlap and "terratonic" in overlap:
							in_ter = overlap.index("terralith")
							in_tec = overlap.index("terratonic")
							if in_ter > in_tec:
								overlap[in_ter], overlap[in_tec] = overlap[in_tec], overlap[in_ter]
					
						url_substring = ",".join([f"modrinth:{pack}" for pack in overlap])
						links.append(discord.ui.Button(style=discord.ButtonStyle.link, label="Map (With Datapacks)", url=f"{self.textlinks['map']['link']}?datapacks={url_substring}", emoji=Constants.Emoji.DATAPACKMAP))

				elif match.split("|")[0].lower() in ["mc", "mcpe", "realms"]:
					bug_id = match.split("|")[-1].lower()
					if bug_id.isdigit():
						links.append(discord.ui.Button(style=discord.ButtonStyle.link, label=f"{match.split('|')[0].upper()} {bug_id}", url=f"https://mojira.dev/{match.split('|')[0].upper()}-{bug_id}", emoji=Constants.Emoji.MOJIRA))

		view = discord.ui.View()
		if len(links) > 0:
			for item in links:
				view.add_item(item)
			return view
		
		return None
			
	async def find_textlink_buttons(self, orig_message: discord.Message) -> discord.Message | None:
		async for message in orig_message.channel.history(after=orig_message.created_at, limit=100, oldest_first=True):
			if not message.author.bot:
				continue
			if not message.reference:
				continue
			if message.reference.message_id == orig_message.id:
				return message
			
		return None
			
	async def edit_textlinks(self, message: discord.Message, matches: list) -> None:
		textlink_message = await self.find_textlink_buttons(message)
		view = await self.do_textlinks(matches=matches)
		if not view:
			view = discord.ui.View()
			view.add_item(discord.ui.Button(style=discord.ButtonStyle.blurple, label="Textlink Removed", disabled=True))

		if textlink_message:
			await textlink_message.edit(view=view)
		else:
			await message.reply(view=view, mention_author=False)
			

	async def do_jsons(self, message: discord.Message, jsons: list[discord.Attachment]) -> None:
		view = discord.ui.View()
		
		for file in jsons:
			bts = await file.read()
			content = bts.decode('utf-8')
			data = self.lz.compressToBase64(content)

			# Which json is it?
			if '"rolls"' in content:
				generator_type = "loot-table"
			elif '"config"' in content:
				generator_type = "worldgen/feature"
			elif '"placement"' in content:
				generator_type = "worldgen/placed-feature"
			elif '"parent"' in content:
				generator_type = "advancement"
			elif '"ingredient"' in content:
				generator_type = "recipe"
			else:
				continue
			
			# Send content to misode.github.io
			headers = {"Content-Type": "application/json", "User-Agent": "catter1/Incendy (catter@stardustlabs.net)"}
			url = "https://snippets.misode.workers.dev"
			body = json.dumps({"data":data,"type":generator_type,"version":"1.21.5","show_preview":True})
			resp = requests.post(url, data=body, headers=headers)

			# Init button
			shareid = json.loads(resp.text)["id"]
			misode_url = f"https://misode.github.io/{generator_type}/?share={shareid}"

			view.add_item(discord.ui.Button(
				style=discord.ButtonStyle.link,
				label=file.filename,
				url=misode_url,
				emoji=Constants.Emoji.MISODE
			))

		# Send message
		await message.reply(view=view, mention_author=False)


	async def do_pastebin(self, message: discord.Message, logs: list[discord.Attachment]) -> None:
		view = discord.ui.View()
		scanner = LogScanner()
		
		for file in logs:
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
			resp = requests.post(url, data=data, headers=headers)

			# Init button
			logurl = json.loads(resp.text)["url"]
			view.add_item(discord.ui.Button(
				style=discord.ButtonStyle.link,
				label=file.filename,
				url=logurl,
				emoji=Constants.Emoji.MCLOGS
			))

			# Add log to Scanner
			scanner.add_log(logdata=content, logname=file.filename, loglink=logurl)

		# Send message
		view.add_item(RawButton())
		embed = scanner.scan(resp='embed', append_name=bool(len(logs) > 1))
		await message.reply(view=view, embed=embed, mention_author=False)

	async def do_other_logs(self, message: discord.Message, mclogs: list, pastebin: list) -> None:
		scanner = LogScanner()

		for log_id in mclogs:
			raw_url = f"https://api.mclo.gs/1/raw/{log_id}"
			insights_url = f"https://api.mclo.gs/1/insights/{log_id}"
			raw = requests.get(raw_url)
			insights = requests.get(insights_url)

			# Check for insights failure
			try:
				title = insights.json()['title']
			except requests.exceptions.JSONDecodeError:
				continue
			
			# Check for data failure
			try:
				_ = raw.json()
			except requests.exceptions.JSONDecodeError:
				content = raw.text
			else:
				continue

			scanner.add_log(logdata=content, logname=title, loglink=f"https://mclo.gs/{log_id}")

		for i, log_id in enumerate(pastebin):
			raw_url = f"https://pastebin.com/raw/{log_id}"
			raw = requests.get(raw_url)

			# Check for log failure
			if raw.status_code == 404:
				continue

			content = raw.text

			scanner.add_log(logdata=content, logname=f"Pastebin #{str(i+1)}", loglink=f"https://pastebin.com/{log_id}")

		embed = scanner.scan(resp='embed', append_name=bool(len(mclogs) + len(pastebin) > 1))
		if embed:
			await message.reply(embed=embed, mention_author=False)

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
			
	async def parse_textlinks(self, content: str) -> list:
		return re.findall(r"[\[]{2}(\w[\w |',-:#]+\w)?[\]]{2}", content)

	@commands.Cog.listener()
	async def on_message(self, message: discord.Message):
		if not message.author.bot:

			# Textlinks
			matches = await self.parse_textlinks(message.content)
			if len(matches) > 0:
				view = await self.do_textlinks(matches=matches)
				if view:
					await message.reply(view=view, mention_author=False)
					
			# Upload JSONs to Misode
			jsons = [file for file in message.attachments if file.filename.endswith(".json")]
			if len(jsons) > 0:
				await self.do_jsons(message=message, jsons=jsons)

			# Pastebin feature
			logs = [file for file in message.attachments if any(ext in file.filename for ext in [".log", ".txt", ".log.gz"])]
			if len(logs) > 0:
				await self.do_pastebin(message=message, logs=logs)

			# Scan 3rd-party logs
			mclogs = re.findall(r"https:\/\/mclo.gs\/(\w{5,})", message.content)
			pastebin = re.findall(r"https:\/\/(?:w{3}.)?pastebin.com/(\w{5,})", message.content)
			if len(mclogs) > 0 or len(pastebin) > 0:
				await self.do_other_logs(message=message, mclogs=mclogs, pastebin=pastebin)

			# Stop Mod Reposts
			for word in message.content.split():
				if validators.url(word):
					await self.stop_mod_reposts(message=message, url=word)
					
	@commands.Cog.listener()
	async def on_message_edit(self, before: discord.Message, after: discord.Message):
		if not after.author.bot and datetime.datetime.now(datetime.timezone.utc) - before.created_at < datetime.timedelta(minutes=5):
			# Textlinks
			after_matches = await self.parse_textlinks(after.content)
			before_matches = await self.parse_textlinks(before.content)
			if len(after_matches) > 0 or len(before_matches) > 0:
				await self.edit_textlinks(message=after, matches=after_matches)

class LogContents:
	"""
	A class representing the contents and properties of a log file.

	Attributes
	-----
	`logdata`
		utf-8 encoded string of the contents of the log
	`logname`
		Name of the log
	`loglink`
		(Optional) Link to mclo.gs
	`responses`
		List of full responses of any errors in the logdata
	`precip`
		Whether the log was already marked with a precipitation error
	"""

	def __init__(self, logdata: str, logname: str, loglink: str = None) -> None:
		if not logdata:
			raise ValueError("Missing logdata to init LogContents!")
		if not logname:
			raise ValueError("Missing logname to init LogContents!")
		
		self.logdata: str = logdata
		self.logname: str = logname
		self.loglink: str = loglink
		self.responses: list = []
		self.precip: bool = False

class LogScanner:
	"""
	A class representing a collection of a log files, able to do scans on itself.

	Attributes
	-----
	`contents`
		A list of all log files with their errors
	"""

	def __init__(self, logdata: str = None, logname: str = '') -> None:
		"""
		Initialize the contents of this scanner instance

		Parameters
		-----
		`logdata`
			(Optional) To init first LogContents
		`logname`
			(Optional) To init first LogContents
		"""

		self.contents: list[LogContents] = []
		if logdata:
			self.contents.append(LogContents(logdata=logdata, logname=logname))

	def add_log(self, logdata: str, logname: str, loglink: str = None) -> None:
		self.contents.append(LogContents(logdata=logdata, logname=logname, loglink=loglink))

	def scan(self, resp: str, append_name: bool = False) -> list | discord.Embed | None:
		"""
		Scan the contents of all logs for hanging fruit errors.

		Parameters:
			`resp` - Either "list" or "embed". For return type.
			`append_name` = Whether to append lognames to errors. Defaults to False.

		Returns:
			A list of `responses`. If `append_name`, will be a list of tuples (response, name, link). `None` if no issues found.
		or
			An embed encoded with all the `responses`. `None` if no issues found.
		"""

		if len(self.contents) < 1:
			raise ValueError("No logs have been added yet!")

		if resp.lower().strip() not in ["list", "embed"]:
			raise ValueError("Must be either 'list' or 'embed'")
		
		resp = resp.lower().strip()
		
		self._check_all()

		total_responses: list[tuple] = []
		for log in self.contents:
			total_responses.extend(map(lambda x: tuple([x, log.logname, log.loglink]), log.responses))

		if len(total_responses) == 0:
			return None

		if resp == "list":
			if append_name:
				return total_responses
			return [resp[0] for resp in total_responses]
		
		else:
			if append_name:	
				formatted_responses = '\n'.join([f'- {resp[0]} ({f"[{resp[1]}]({resp[2]})" if resp[2] else resp[1]})' for resp in total_responses])
			else:
				formatted_responses = '\n'.join([f'- {resp[0]}' for resp in total_responses])
			embed = discord.Embed(
				title="[Auto Scanner]",
				color=discord.Colour.dark_magenta(),
				description=f"I've taken a glance at your log{'s' if len(self.contents) > 1 else ''}. Here are some potential issues I found!\n\n{formatted_responses}"
			)
			embed.set_footer(text="How was my response? Let me know!")

			return embed
		
	def _check_all(self) -> None:
		"""Loops through all checks and all log files."""

		for i in range(len(self.contents)):
			self.check_precipitation(i)
			self.check_messy_uninstall(i)
			self.check_nullscape_seedfix(i)
			self.check_plugin_installation(i)
			self.check_auditory_incendium(i)
			self.check_cyclic_crash(i)
	
	def check_precipitation(self, index: int) -> None:
		precipitation_3 = re.search(r"No key precipitation in MapLike", self.contents[index].logdata)
		precipitation_4 = re.search(r"No key has_precipitation in MapLike", self.contents[index].logdata)

		if precipitation_3:
			error = "Your game/server is running 1.19.3, but one or more of your worldgen datapacks is made for 1.19.4 or 1.20.x. Update your server, or download the correct versions of your datapack(s)."
			self.contents[index].responses.append(error)
			self.contents[index].precip = True
			return
		
		if precipitation_4:
			error = "Your game/server is running 1.19.4 or 1.20.x, but one or more of your worldgen datapacks is made for 1.19.3. Downgrade your server, or download the correct versions of your datapack(s)."
			self.contents[index].responses.append(error)
			self.contents[index].precip = True
			return
		
		return
	
	def check_messy_uninstall(self, index: int) -> None:
		failed = re.search(r"Failed to get element ResourceKey\[minecraft:worldgen/biome / (?P<Namespace>[a-z]+):(?P<Biome>[a-z_\-\/]+)\]", self.contents[index].logdata)
		unbound = re.search(r"Unbound values in registry ResourceKey\[minecraft:root / minecraft:worldgen/biome]: \[(?P<Namespace>[a-z]+):(?P<Biome>[a-z_\-\/]+)", self.contents[index].logdata)

		if self.contents[index].precip:
			return
		if not (failed or unbound):
			return
		
		if failed:
			pack = failed.group(1).title()
		else:
			pack = unbound.group(1).title()

		error = f"It appears {pack} was uninstalled incorrectly. Biomes must be removed from the `level.dat` - see `/faq Removing Worldgen Packs`."
		self.contents[index].responses.append(error)

		return
	
	def check_nullscape_seedfix(self, index: int) -> None:
		seedfix = re.search(r"Exception in thread \"main\" java\.lang\.module\.ResolutionException: Modules ([a-z_-]+) and ([a-z_-]+) export package net\.hypercubemc\.seedfix to module ([a-z_-]+)", self.contents[index].logdata)
		nullscape = re.search(r"Nullscape_1\.18\.2_v1\.1\.3\.jar", self.contents[index].logdata)

		if seedfix and nullscape:
			error = "You are using Nullscape 1.1.3, which currently has issues with its Seedfix implementation. Upgrade to [Nullscape 1.1.4](https://modrinth.com/mod/nullscape/versions?g=1.18.2) or higher and download its [Unfixed Seeds](https://modrinth.com/mod/unfixed-seeds) dependency!"
			self.contents[index].responses.append(error)
			return
		
		return
	
	def check_plugin_installation(self, index: int) -> None:
		plugin = re.search(r"Error loading plugin: File 'plugins\\(?P<Datapack>Terralith|Incendium|Nullscape|Amplified_Nether|Structory|Continents|Structory_Towers)", self.contents[index].logdata)

		if plugin:
			pack = plugin.group(1).replace('_', ' ').title()
			error = f"You have installed {pack} as a plugin! The `jar` versions of our projects are mods, not plugins. To use {pack} on a Spigot/Paper server, use the datapack version and put it in the `world/datapacks` folder."
			self.contents[index].responses.append(error)
			return
		
		return
	
	def check_auditory_incendium(self, index: int) -> None:
		auditory = re.search(r"auditory\$onHit", self.contents[index].logdata)
		enderpearl = re.search(r"(ThrownEnderpearlMixin|EnderPearlSoundMixin|EnderPearlEntityMixin)", self.contents[index].logdata)

		if auditory:
			error = f"This is an [issue with Auditory](https://github.com/Sydokiddo/auditory/issues/32). In the meantime, this can be fixed by disabling {'enderpearl' if enderpearl else 'the problem'} sounds in the Auditory config."
			self.contents[index].responses.append(error)
			return
		
		return
	
	def check_cyclic_crash(self, index: int) -> None:
		cyclic = re.search(r"mod:cyclic", self.contents[index].logdata)
		foc = re.search(r"Feature order cycle found, involved sources", self.contents[index].logdata)
		snowy_cherry_grove = re.search(r"terralith:snowy_cherry_grove", self.contents[index].logdata)

		if all([cyclic, foc, snowy_cherry_grove]):
			error = "This is an issue with Cyclic that can be resolved by updating Cyclic to 1.12.11+."
			self.contents[index].responses.append(error)
			return
		
		return
	
class RawButton(discord.ui.Button):
	def __init__(self, label: str = 'Raw', custom_id: str = 'raw'):
		super().__init__(style=discord.ButtonStyle.blurple, label=label, disabled=False, custom_id=custom_id, emoji='🗒️')

	async def callback(self, interaction: discord.Interaction) -> Any:
		view = discord.ui.View()

		for item in self.view.children:
			if item.emoji.name == 'mclogs':
				log_id = item.url.split('/')[-1]
				if interaction.data['custom_id'] == 'raw':
					item.url = f"https://api.mclo.gs/1/raw/{log_id}"
					item.label = f"{item.label} (raw)"
				else:
					item.url = f"https://mclo.gs/{log_id}"
					item.label = item.label[:-6]
				view.add_item(item)

		if interaction.data['custom_id'] == 'raw':
			view.add_item(RawButton(label='Pretty', custom_id='pretty'))
		else:
			view.add_item(RawButton())

		await interaction.response.edit_message(view=view)


async def setup(client):
	await client.add_cog(Autoresponse(client))