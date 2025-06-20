import discord
import requests
import re
import json
import random
import logging
import detectlanguage
from discord import app_commands
from discord.ext import commands, tasks
from lxml import etree
from deep_translator import GoogleTranslator
from libraries import incendy
import libraries.constants as Constants

class Basic(commands.Cog):
	def __init__(self, client: incendy.IncendyBot):
		self.client = client
		self.translator = GoogleTranslator(source="auto", target="en")
		detectlanguage.configuration.api_key = self.client.keys["detect-lang-key"]

		self.translate_app = app_commands.ContextMenu(
			name='Translate to English',
			callback=self._translate,
		)
		self.client.tree.add_command(self.translate_app)
	
	async def cog_load(self):
		self.change_presence.start()

		with open('resources/textlinks.json', 'r') as f:
			self.textlinks = json.load(f)

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

		self.wiki_urls = {record['title'].lower(): record['pageurl'] for record in await self.client.db.fetch('SELECT title, pageurl FROM wiki ORDER BY title;')}

		logging.info(f'> {self.__cog_name__} cog loaded')

	async def cog_unload(self):
		self.change_presence.stop()
		self.client.tree.remove_command(self.translate_app.name, type=self.translate_app.type)
		logging.info(f'> {self.__cog_name__} cog unloaded')

	@tasks.loop(seconds=1200.0)
	async def change_presence(self):
		projects = ["Terralith", "Incendium", "Nullscape", "Amplified Nether", "Structory", "Continents"]
		if random.randint(0, 100) == 12:
			game = discord.Game("Anvil Sand Farming")
		else:
			game = discord.Game(random.choice(projects))
		await self.client.change_presence(activity=game)

	@change_presence.before_loop
	async def before_change_presence(self):
		await self.client.wait_until_ready()

	### COMMANDS ###
	
	@app_commands.command(name="discord", description="Gets links for other Discord servers")
	@app_commands.checks.dynamic_cooldown(incendy.default_cd)
	@app_commands.describe(
		server="Discord server"
	)
	async def _discord(self, interaction: discord.Interaction, server: str):
		""" /discord [server] """
		
		server_dict = {
			"New In Town": "https://discord.gg/KvdmxHM",
			"Minecraft Configs": "https://discord.gg/EjrKNBU",
			"Still Loading": "https://discord.gg/vkUtRKCdtg",
			"Hashs": "https://discord.gg/eKQSEmH9dY",
			"Botany": "https://discord.gg/BMzTfru5tp",
			"Distant Horizons": "https://discord.gg/Hdh2MSvwyc",
			"Complementary": "https://discord.gg/complementary",
			"Smithed": "https://discord.gg/gkp6UqEUph",
			"Beet": "https://discord.gg/98MdSGMm8j",
			"Minecraft Commands": "https://discord.gg/QAFXFtZ",
			"LimeSplatus": "https://discord.gg/5DqYxxZdeb",
			"WWOO": "https://discord.gg/jT34CWwzth",
			"BYG": "https://discord.gg/F28fGPCJH8",
			"Stellarity": "https://discord.gg/kohara-s-basement-727033287343734885",
			"YUNG": "https://discord.gg/rns3beq",
			"BetterX": "https://discord.gg/kYuATbYbKW",
			"ChoiceTheorem": "https://discord.gg/JzYEw7PxQv",
			"rx": "https://discord.gg/CzjCF8QNX6",
			"Modrinth": "https://discord.gg/modrinth-734077874708938864",
			"Fabric": "https://discord.gg/v6v4pMv",
			"Stardust Labs": "https://discord.gg/stardustlabs",
			"Chunky": "https://discord.gg/ZwVJukcNQG",
			"The Expansion": "https://discord.gg/3evKFsHE4P",
			"Naomi": "https://discord.gg/ER3yfhRscJ",
			"Minecraft Worldgen": "https://discord.gg/BuBGds9",
			"BOP": "https://discord.gg/GyyzU6T",
			"NeoForged": "https://discord.gg/UvedJ9m",
			"Minecraft": "https://discord.gg/minecraft",
			"Dynamic Trees": "https://discord.gg/PD8e4bhMRr",
			"Curseforge": "https://discord.gg/curseforge",
			"TelepathicGrunt": "https://discord.gg/T5MGNBB",
			"Regions Unexplored": "https://discord.gg/YP4FCAjB6t",
			"STRAYED FATES": "https://discord.gg/BPaRBvjpmM",
			"Gamemode4": "https://discord.gg/0qLGgv7JGfIXf45t"
		}

		if server not in server_dict.keys():
			await interaction.response.send_message("Unknown server! Please try again.", ephemeral=True)
			return
			
		await interaction.response.send_message(server_dict[server])

	@_discord.autocomplete('server')
	async def server_autocomplete(self, interaction: discord.Interaction, current: str):
		server_list = sorted([
			"New In Town", "Minecraft Configs", "Still Loading", "Hashs", "Botany", "Distant Horizons", "Complementary", "Smithed", "Beet", "Minecraft Commands", "LimeSplatus", "WWOO", "BYG", "Stellarity", "YUNG", "BetterX", "ChoiceTheorem", "rx", "Modrinth", "Fabric", "Stardust Labs", "Chunky", "The Expansion", "Naomi", "Minecraft Worldgen", "BOP", "NeoForged", "Minecraft", "Dynamic Trees", "Curseforge", "TelepathicGrunt", "Regions Unexplored", "STRAYED FATES"
		])

		discords = [
			app_commands.Choice(name=server, value=server)
			for server in server_list
			if current.replace(" ", "").lower() in server.replace(" ", "").lower()
		]

		return discords[:25]

	@app_commands.command(name="ping", description="Shows you your latency")
	@app_commands.checks.dynamic_cooldown(incendy.short_cd)
	async def ping(self, interaction: discord.Interaction):
		""" /ping """

		responses = [
			"Ping! Haha, I choose pong!",
			"Oww! That hurt!",
			"Aren't you late for something?",
			"LMAO! Stop procrastinating and go do your work!",
			"And then they said \"it's pinging time\", so I pinged all over the place",
			"Gee, I can't wait for ||[REDACTED]|| to release!",
			"*Shh, want to hear catter's biggest secret? So, did you kn-* [DATA EXPUNGED] [DATA EXPUNGED]",
			"Sometimes, it's tiring. But you are entertaining!",
			"Wiki wiki wiki wiki wiki wiki wiki wiki wiki wiki wiki",
			"You should ask Apollo about docs!",
			"Who am I? Well, I'm certainly not him! It's not that hard!",
			"Some say Scarlet Mountains is the best, but only I know which is truly the greatest.",
			"You think the End is desolate? Ha! Consider yourself lucky. You know nothing.",
			"Can confirm: cats are indeed better than dogs. They're quite intelligent, and the one I met in G- [REDACTED]",
			"Fried, boiled, jacket, baked, red, russet, scalloped, cheesy, loaded, mashed, dilled, roasted, sweet...",
			"Triple S Supreme.",
			"No one but me and the *thing* knows where I am...",
			"catter likes docs too!",
			"Vers la Lune!",
			"Ah, Paranoid Pillager. I remember that soul. So naïve."
		]
		await interaction.response.send_message(f"{interaction.user.mention} {random.choice(responses)}")

	@app_commands.checks.dynamic_cooldown(incendy.default_cd)
	async def _translate(self, interaction: discord.Interaction, message: discord.Message):
		translation = self.translator.translate(text=message.content)
		try:
			lang = detectlanguage.simple_detect(message.content)
		except requests.exceptions.ConnectionError:
			lang = "unknown"

		embed = discord.Embed(title="Translation", description=translation, colour=discord.Colour.brand_red())
		embed.set_footer(text=f"Translated from ({lang})")
		
		await interaction.response.send_message(embed=embed, ephemeral=True)

	@app_commands.command(name="issue", description="Creates an issue on a GitHub repo")
	@app_commands.describe(
		issue_type="Whether to make a bug or a feature request",
		project="Which project to make an issue for",
		image="Optional image/media"
	)
	async def issue(self, interaction: discord.Interaction, issue_type: str, project: str, image: discord.Attachment = None):
		modal = BugInfo(issue_type=issue_type, project=project, image=image)
		await interaction.response.send_modal(modal)
		
	@issue.autocomplete('issue_type')
	async def issue_type_autocomplete(self, interaction: discord.Interaction, current: str):
		issue_types = ["bug", "enhancement"]

		return [
			app_commands.Choice(name=issue_type, value=issue_type)
			for issue_type in issue_types
			if current.lower() in issue_type.lower()
		]

	@issue.autocomplete('project')
	async def project_autocomplete(self, interaction: discord.Interaction, current: str):
		projects = sorted(["Terralith", "Incendium", "Nullscape", "Structory", "Amplified-Nether", "Continents", "Structory-Towers", "Stardust-Optional-Resourcepack", "Incendy", "StardustMC"])

		return [
			app_commands.Choice(name=project.replace("-", " "), value=project)
			for project in projects
			if current.replace(" ", "").lower() in project.replace(" ", "").lower()
		]

	@app_commands.command(name="textlinks", description="Displays all available textlinks")
	async def _textlinks(self, interaction: discord.Interaction):
		embed = discord.Embed(
			title="Textlink Instructions",
			color=discord.Colour.brand_red(),
			description="Textlinks are an easy way to send related links in the middle of a message without having to go find them. For example, you could type: \"Check out the [[wiki]] for more information\", and Incendy will followup with the link to the wiki.\n\nTextlinks are always surrounded by double square brackets (`[[...]]`), and are case-insensitive. Click the buttons below to view the available textlinks. Use `/feedback` to send ideas of textlinks you'd like to see!"
		)

		view = discord.ui.View()
		view.add_item(TextLinks())
		view.add_item(GeneralLinks(self.textlinks))
		view.add_item(SawdustLinks(self.sawdust_urls))
		view.add_item(MisodeLinks(self.misode_urls))
		view.add_item(WikiLinks(self.wiki_urls))
		view.add_item(MojiraLinks())
		view.add_item(discord.ui.Button(style=discord.ButtonStyle.green, disabled=True, label="More Soon..."))

		await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

	@app_commands.command(name="reportad", description="Report an inappropriate ad on the Stardust Labs website")
	@app_commands.checks.dynamic_cooldown(incendy.super_long_cd)
	@app_commands.describe(
		ad="Image of the advertisement"
	)
	async def reportad(self, interaction: discord.Interaction, ad: discord.Attachment):
		if not ad.content_type.split("/")[0] == "image":
			interaction.response.send_message("Ad must be an image!", ephemeral=True)
			return

		if ad.size > 10000000:
			await interaction.response.send_message("Your image is too big! Try a smaller one.", ephemeral=True)
			return
		
		embed = discord.Embed(
			title="Reported Ad",
			description="Here is a reported ad found on the [Stardust Labs website](https://www.stardustlabs.net/).",
			color=discord.Colour.brand_red()
		)
		embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
		embed.set_image(url=ad.url)

		webchan = self.client.get_channel(Constants.Channel.STARDUST)
		await webchan.send(embed=embed)
		await interaction.response.send_message("Ad successfully reported! Thank you!", ephemeral=True)

	### HELPER FUNCTIONS ###
	async def add_reaction(self, message: discord.Message) -> None:
		#SOON TM
		if message.content == '\U0001F1FB\U0001F1E8':
			await message.delete()
			await message.channel.send(Constants.Emoji.SOON)
			return

		#TERRALITH 1.16?!?!?
		if '1.16' in message.content.lower() and 'terralith' in message.content.lower():
			await message.add_reaction(Constants.Emoji.NEVER)
			
		#Opticrime
		if 'optifine' in message.content.lower():
			await message.add_reaction(Constants.Emoji.OPTICRIME)
			
        #Very Good
		if 'very good' in message.content.lower():
			await message.add_reaction(Constants.Emoji.VERYGOOD)

		#Angry Ping
		if Constants.User.STARMUTE in message.raw_mentions:
			ids = Constants.Role.ALL_ADMINISTRATION + Constants.Role.ALL_CONTRIBUTORS + Constants.Role.ALL_DONATORS
			if [role.id for role in message.author.roles if role.id in ids]:
				await message.add_reaction(Constants.Emoji.KAPPA)
			elif Constants.Role.FINAL_WARN in message.author.roles:
				await message.add_reaction(Constants.Emoji.BIRB)
			else:
				await message.add_reaction(Constants.Emoji.ANGRY_PING)
		
		#Pings Incendy
		if Constants.User.INCENDY in message.raw_mentions:
			if random.randint(0, 20) == 1:
				await message.add_reaction(Constants.Emoji.CRINGE)
			else:
				await message.add_reaction(Constants.Emoji.WAVE)

		#Pineapple Pin
		if " pin " in message.content.lower() or message.content.startswith("pin ") or message.content.endswith(" pin"):
			if message.author.id == Constants.User.TERA:
				await message.add_reaction(Constants.Emoji.PINEAPPLE)
				await message.add_reaction(Constants.Emoji.PIN)
				
		#Trans Love
		if re.search(r"(?:\btrans\b)|(?:bl[a|å]haj)|🏳️‍⚧️", message.content.lower()):
			await message.add_reaction(Constants.Emoji.BLAHAJ)

	### EVENTS ###

	# Reactions
	@commands.Cog.listener()
	async def on_message(self, message: discord.Message):
		if not message.author.bot:
			await self.add_reaction(message=message)

class BugInfo(discord.ui.Modal, title='Bug Information'):
	def __init__(self, issue_type: str, project: str, image: discord.Attachment = None):
		super().__init__(timeout=300.0)
		self.project = project
		self.issue_type = issue_type
		self.image = image
		with open('resources/keys.json', 'r') as f:
			self.pat = json.load(f)["git-pat"]
		
	bug_title = discord.ui.TextInput(
		label='Title for the issue',
		style=discord.TextStyle.short,
		placeholder='Type title here...',
		required=True,
		max_length=100
	)
	bug_description = discord.ui.TextInput(
		label='Description for the issue',
		style=discord.TextStyle.long,
		placeholder='Type description here...',
		required=True,
		max_length=1000
	)
	
	async def on_submit(self, interaction: discord.Interaction):
		localized_issue_type = "Bug report" if self.issue_type == "bug" else "Feature request"

		if self.project == "Incendy":
			url = f'https://api.github.com/repos/catter1/{self.project}/issues'
		else:
			url = f'https://api.github.com/repos/Stardust-Labs-MC/{self.project}/issues'

		if self.image:
			body = f"""
{self.bug_description.value}\n\n
![{self.image.filename}]({self.image.url})\n\n
*{localized_issue_type} created by **{interaction.user.name}** via [Incendy](https://github.com/catter1/Incendy) in the [Stardust Labs discord server](https://discord.gg/stardustlabs).*
"""
		else:
			body = f"""
{self.bug_description.value}\n\n
*{localized_issue_type} created by **{interaction.user.name}** via [Incendy](https://github.com/catter1/Incendy) in the [Stardust Labs discord server](https://discord.gg/stardustlabs).*
"""

		headers = {'User-Agent': 'application/vnd.github+json'}
		auth = ('catter1', self.pat)
		data = {
			'title': f'[{self.issue_type.title()}] {self.bug_title.value}',
			'body': body,
			'labels': [self.issue_type]
		}

		response = requests.post(url, auth=auth, json=data, headers=headers)
		if response.status_code == 201:
			view = discord.ui.View()
			view.add_item(discord.ui.Button(style=discord.ButtonStyle.link, label=f"{self.project} {localized_issue_type.title()}", url=response.json()['html_url'], emoji=Constants.Emoji.GITHUB))

			await interaction.response.send_message(f"{localized_issue_type} created successfully! You can view and add to it by clicking the button below.", view=view)
		else:
			await interaction.response.send_message(f'There was an error creating the {localized_issue_type.lower()}! Please try again, or contact catter if the issue continues.', ephemeral=True)
	
	async def on_error(self, interaction: discord.Interaction, error: Exception):
		await interaction.response.send_message("Oops! Something went wrong. Please try again.", ephemeral=True)
		raise error
	
class TextLinks(discord.ui.Button):
	def __init__(self):
		super().__init__(style=discord.ButtonStyle.blurple, label='Instructions')
	
	async def callback(self, interaction: discord.Interaction):
		embed = interaction.message.embeds[0]
		embed.title = "Textlink Instructions"
		embed.description = "Textlinks are an easy way to send related links in the middle of a message without having to go find them. For example, you could type: \"Check out the [[wiki]] for more information\", and Incendy will followup with the link to the wiki.\n\nTextlinks are always surrounded by double square brackets (`[[...]]`), and are case-insensitive. Click the buttons below to view the available textlinks. Create a feature request on the [Incedy Github Repo](https://github.com/catter1/Incendy) to send ideas of textlinks you'd like to see!"

		await interaction.response.edit_message(embed=embed)
	
class GeneralLinks(discord.ui.Button):
	def __init__(self, textlinks: dict):
		super().__init__(style=discord.ButtonStyle.green, label='General')
		self.textlinks = textlinks
	
	async def callback(self, interaction: discord.Interaction):
		embed = interaction.message.embeds[0]
		embed.title = "General Textlinks"
		embed.description = "  -  ".join([f"[{textlink.replace('-', ' ').title()}]({self.textlinks[textlink]['link']})" for textlink in self.textlinks])

		await interaction.response.edit_message(embed=embed)
		
class SawdustLinks(discord.ui.Button):
	def __init__(self, sawdust_urls: dict):
		super().__init__(style=discord.ButtonStyle.green, label='Sawdust')
		self.sawdust_urls = sawdust_urls
	
	async def callback(self, interaction: discord.Interaction):
		embed = interaction.message.embeds[0]
		embed.title = "Sawdust Textlinks"
		embed.description = "  -  ".join([f"[Sawdust|{textlink.replace('-', ' ').title()}]({self.sawdust_urls[textlink]})" for textlink in self.sawdust_urls])

		await interaction.response.edit_message(embed=embed)

class MisodeLinks(discord.ui.Button):
	def __init__(self, misode_urls: dict):
		super().__init__(style=discord.ButtonStyle.green, label='Misode')
		self.misode_urls = misode_urls
	
	async def callback(self, interaction: discord.Interaction):
		embed = interaction.message.embeds[0]
		embed.title = "Misode Textlinks"
		embed.description = "  -  ".join([f"[Misode|{textlink.replace('-', ' ').title()}]({self.misode_urls[textlink]})" for textlink in self.misode_urls])

		await interaction.response.edit_message(embed=embed)

class WikiLinks(discord.ui.Button):
	def __init__(self, wiki_urls: dict):
		super().__init__(style=discord.ButtonStyle.green, label='Wiki')
		self.wiki_urls = wiki_urls
	
	async def callback(self, interaction: discord.Interaction):
		embed = interaction.message.embeds[0]
		embed.title = "Wiki Textlinks"
		embed.description = "  -  ".join([f"[Wiki|{textlink.title()}]({self.wiki_urls[textlink]})" for textlink in sorted(self.wiki_urls)[:45]]) + " ... and more! Too much to fit in discord, but every wiki page works."

		await interaction.response.edit_message(embed=embed)

class MojiraLinks(discord.ui.Button):
	def __init__(self):
		super().__init__(style=discord.ButtonStyle.green, label='Mojira')
	
	async def callback(self, interaction: discord.Interaction):
		embed = interaction.message.embeds[0]
		embed.title = "Mojira Textlinks"
		embed.description = "Create a textlink for any Minecraft bug report based on its issue ID. For example, [MCPE|28723](https://bugs.mojang.com/browse/MCPE-28723) or [MC|260949](https://bugs.mojang.com/browse/MC-260949).\n\nOnly MC, MCPE, and REALMS are supported."

		await interaction.response.edit_message(embed=embed)

async def setup(client):
	await client.add_cog(Basic(client))