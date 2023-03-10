import discord
import requests
import typing
import json
import re
import random
#import googletrans
import logging
from discord import app_commands
from discord.ext import commands, tasks
from libraries import incendy

class Basic(commands.Cog):
	def __init__(self, client: incendy.IncendyBot):
		self.client = client
		#self.translator = googletrans.Translator()

		#self.translate_app = app_commands.ContextMenu(
		#	name='Translate to English',
		#	callback=self._translate,
		#)
		#self.client.tree.add_command(self.translate_app)
	
	async def cog_load(self):
		self.change_presence.start()

		self.webchan = self.client.get_channel(917905247056306246)
		with open('resources/textlinks.json', 'r') as f:
			self.textlinks = json.load(f)

		resp = requests.get("https://misode.github.io/sitemap.txt")
		self.misode_urls = {url.split('/')[-2]: url for url in resp.text.split("\n") if len(url.split("/")) > 4}
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

	@app_commands.command(name="apply", description="Send your interest in becoming a StardustMC Security member for Season 2")
	@app_commands.checks.dynamic_cooldown(incendy.super_long_cd)
	@app_commands.describe(
		ign="Your Minecraft username",
		timezone="What is your timezone?"
	)
	async def apply(self, interaction: discord.Interaction, ign: str, timezone: str):
		"""/apply <ign> <timezone>"""

		embed = discord.Embed(
			title="Security Application",
			color=discord.Colour.dark_blue(),
			description=f"""
			Minecraft Username: {ign}
			Timezone: {timezone}
			"""
		)
		embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)

		channel = self.client.get_channel(1002216414335221841)
		await channel.send(embed=embed)
		await interaction.response.send_message("Thanks for your Security member application! Don't ask about your application - we will get back to you when we're ready.", ephemeral=True)

	@app_commands.command(name="discord", description="Gets links for other Discord servers")
	@app_commands.checks.dynamic_cooldown(incendy.default_cd)
	@app_commands.describe(
		server="Discord server"
	)
	async def _discord(self, interaction: discord.Interaction, server: str):
		""" /discord [server] """

		if not server.startswith("https://discord.gg/"):
			await interaction.response.send_message("Unknown error! Please try again.", ephemeral=True)
			return
			
		await interaction.response.send_message(server)

	@_discord.autocomplete('server')
	async def autocomplete_callback(self, interaction: discord.Interaction, current: str):
		server_dict = {
			"New In Town": "https://discord.gg/KvdmxHM",
			"Minecraft Configs": "https://discord.gg/EjrKNBU",
			"Still Loading": "https://discord.gg/vkUtRKCdtg",
			"REDUX": "https://discord.gg/BBNavaXH8v",
			"Hashs": "https://discord.gg/eKQSEmH9dY",
			"Botany": "https://discord.gg/BMzTfru5tp",
			"Distant Horizons": "https://discord.gg/Hdh2MSvwyc",
			"Complementary": "https://discord.gg/A6faFYt",
			"Apollo": "https://discord.gg/vFz67Pvceu",
			"Smithed": "https://discord.gg/gkp6UqEUph",
			"Beet": "https://discord.gg/98MdSGMm8j",
			"Minecraft Commands": "https://discord.gg/QAFXFtZ",
			"LimeSplatus": "https://discord.gg/5DqYxxZdeb",
			"WWOO": "https://discord.gg/jT34CWwzth",
			"BYG": "https://discord.gg/F28fGPCJH8",
			"Foka's Studios": "https://discord.gg/J6guYAySN8",
			"YUNG": "https://discord.gg/rns3beq",
			"BetterX": "https://discord.gg/kYuATbYbKW",
			#"LPS": "https://discord.gg/8ZmhaPPbjE",
			"ChoiceTheorem": "https://discord.gg/JzYEw7PxQv",
			"rx": "https://discord.gg/CzjCF8QNX6",
			"Bisect Hosting": "https://discord.gg/zb8vZap",
			"Modrinth": "https://discord.gg/modrinth-734077874708938864",
			"Fabric": "https://discord.gg/v6v4pMv",
			"Stardust Labs": "https://discord.gg/stardustlabs"
		}
		server_list = sorted([server for server in server_dict.keys()])

		return [
			app_commands.Choice(name=server, value=server_dict[server])
			for server in server_list
			if current.replace(" ", "").lower() in server.replace(" ", "").lower()
		]

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
			"Some say Scarlet Mountains is the best, but only I know which is truly the greatest...",
			"You think the End is desolate? Ha! Consider yourself lucky. You know nothing.",
			"Can confirm: cats are indeed better than dogs. They're quite intelligent, and the one I met i- [REDACTED]",
			"Fried, boiled, jacket, baked, red, russet, scalloped, cheesy, loaded, mashed, dilled, roasted, sweet..."
		]
		await interaction.response.send_message(f"{interaction.user.mention} {random.choice(responses)}")

	# @app_commands.checks.dynamic_cooldown(incendy.default_cd)
	# async def _translate(self, interaction: discord.Interaction, message: discord.Message):
	# 	translation = self.translator.translate(message.content, dest='en')

	# 	embed = discord.Embed(title="Translation", description=translation.text, colour=discord.Colour.brand_red())
	# 	embed.set_footer(text=f"Translated from {googletrans.LANGUAGES[translation.src]}")
		
	# 	await interaction.response.send_message(embed=embed, ephemeral=True)

	@app_commands.command(name="issue", description="Creates an issue on a GitHub repo")
	@incendy.can_report_bug()
	async def issue(self, interaction: discord.Interaction, project: str):
		modal = BugInfo(project=project)
		await interaction.response.send_modal(modal)

	@issue.autocomplete('project')
	async def autocomplete_callback(self, interaction: discord.Interaction, current: str):
		projects = sorted(["Terralith", "Incendium", "Nullscape", "Structory", "Amplified-Nether", "Continents", "Structory-Towers", "Incendium-Optional-Resourcepack", "Incendy"])

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
		view.add_item(MisodeLinks(self.misode_urls))
		view.add_item(WikiLinks(self.wiki_urls))
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

		await self.webchan.send(embed=embed)
		await interaction.response.send_message("Ad successfully reported! Thank you!", ephemeral=True)

	### EVENTS ###

	@commands.Cog.listener()
	async def on_message(self, message: discord.Message):
		if not message.author.bot:
			#SOON TM
			if message.content == '\U0001F1FB\U0001F1E8':
				await message.delete()
				await message.channel.send("<:soontm:780592610666348585>")
				return

			#TERRALITH 1.16?!?!?
			if '1.16' in message.content.lower() and 'terralith' in message.content.lower():
				await message.add_reaction('<:NEVER:909247811256713236>')

			#Angry Ping
			if str('332701537535262720') in str(message.mentions):
				ids = [744788173128859670, 760569251618226257, 744788229579866162, 821429484674220036, 885719021176119298, 862343886864384010, 749701703938605107, 908104350218469438, 918174846318428200, 877672384872738867, 795469887790252084, 795469805678755850, 795463111561445438]
				if [role.id for role in message.author.roles if role.id in ids]:
					await message.add_reaction('<:Kappa:852579238259327006>')
				elif 804009152288260106 in message.author.roles:
					await message.add_reaction('<:birb:982866294187638815>')
				else:
					await message.add_reaction('<:angryPING:875547905614839818>')
			
			#Pings Incendy
			if str('780588749825638410') in str(message.mentions):
				if random.randint(0, 20) == 1:
					await message.add_reaction('<:cringe:828845270732374021>')
				else:
					await message.add_reaction('????')

			#Pineapple Pin
			if " pin " in message.content.lower() or message.content.startswith("pin ") or message.content.endswith(" pin"):
				if message.author.id == 234748321258799104:
					await message.add_reaction('????')
					await message.add_reaction('????')

			#Textlinks
			matches = re.findall(r"[\[]{2}(\w[\w |':]+\w)?[\]]{2}", message.content)
			if len(matches) > 0:
				links = []
				for match in matches:
					if match.lower() in [textlink for textlink in self.textlinks]:
						links.append(discord.ui.Button(style=discord.ButtonStyle.link, label=match.lower().title(), url=self.textlinks[match.lower()]))
						#await message.reply(f"{match.lower().title()} link: <{self.textlinks[match.lower()]}>", mention_author=False)
					elif "|" in match:
						if "misode" in match.split("|")[0].lower():
							page = match.split("|")[-1].lower().replace(" ", "-")
							if page in self.misode_urls.keys():
								links.append(discord.ui.Button(style=discord.ButtonStyle.link, label=f"Misode: {page.title()}", url=self.misode_urls[page]))
								#await message.reply(f"{page.replace('-', ' ').title()} Misode link: <{self.misode_urls[page]}>", mention_author=False)
						elif "wiki" in match.split("|")[0].lower():
							page = match.split("|")[-1].lower()
							if page in self.wiki_urls.keys():
								links.append(discord.ui.Button(style=discord.ButtonStyle.link, label=f"Wiki: {page.title()}", url=self.wiki_urls[page]))
								#await message.reply(f"{page.title()} Wiki link: <{self.wiki_urls[page]}>", mention_author=False)
				
				view = discord.ui.View()
				if len(links) > 0:
					for item in links:
						view.add_item(item)
					await message.reply(view=view, mention_author=False)

			#Pastebin feature
			if len(message.attachments) > 0:
				for file in message.attachments:
					if ".log" in file.filename or ".txt" in file.filename:

						bts = await file.read()
						content = bts.decode('utf-8')
						
						headers = {'Content-Type': 'application/x-www-form-urlencoded'}
						url = "https://api.mclo.gs/1/log"
						data = {"content": f"{content}"}
						x = requests.post(url, data=data, headers=headers)

						logurl = json.loads(x.text)["url"]

						await message.reply(f"{file.filename}: {logurl}", mention_author=False)

class Feedback(discord.ui.Modal, title='Incendy Feedback'):
	def __init__(self, feedback_chan: typing.Optional[typing.Union[discord.abc.GuildChannel, discord.Thread, discord.abc.PrivateChannel]]):
		super().__init__(timeout=300.0)
		self.feedback_chan = feedback_chan

	feedback = discord.ui.TextInput(
		label='Let Incendy know your feedback for her!',
		style=discord.TextStyle.long,
		placeholder='Insert feedback here...',
		required=True,
		max_length=1000
	)

	async def on_submit(self, interaction: discord.Interaction):
		embed = discord.Embed(
			title="Incendy Feedback",
			description=self.feedback,
			color=discord.Colour.brand_red()
		)
		embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
		await self.feedback_chan.send(embed=embed)
		await interaction.response.send_message("Thanks for your feedback!")

class BugInfo(discord.ui.Modal, title='Bug Information'):
	def __init__(self, project: str):
		super().__init__(timeout=300.0)
		self.project = project
		with open('resources/keys.json', 'r') as f:
			self.pat = json.load(f)["git-pat"]
		
	bug_title = discord.ui.TextInput(
		label='The title for the bug report',
		style=discord.TextStyle.short,
		placeholder='Type title here...',
		required=True,
		max_length=100
	)
	bug_description = discord.ui.TextInput(
		label='The description for the bug report',
		style=discord.TextStyle.long,
		placeholder='Type description here...',
		required=True,
		max_length=1000
	)
	
	async def on_submit(self, interaction: discord.Interaction):
		if self.project == "Incendy":
			url = f'https://api.github.com/repos/catter1/{self.project}/issues'
		else:
			url = f'https://api.github.com/repos/Stardust-Labs-MC/{self.project}/issues'
		headers = {'User-Agent': 'application/vnd.github+json'}
		auth = ('catter1', self.pat)
		data = {
			'title': self.bug_title.value,
			'body': f'{self.bug_description.value}\n\n*Bug created by {interaction.user.name} via Incendy in the Stardust Labs discord server*'
		}

		response = requests.post(url, auth=auth, json=data, headers=headers)
		if response.status_code == 201:
			await interaction.response.send_message(f"Issue created successfully! You can view and add to it here: {response.json()['html_url']}")
		else:
			await interaction.response.send_message('There was an error creating the issue! Please try again, or contact catter if the issue continues.', ephemeral=True)
	
	async def on_error(self, interaction: discord.Interaction, error: Exception):
		await interaction.response.send_message("Oops! Something went wrong. Please try again.", ephemeral=True)
		raise error
	
class TextLinks(discord.ui.Button):
	def __init__(self):
		super().__init__(style=discord.ButtonStyle.blurple, label='Instructions')
	
	async def callback(self, interaction: discord.Interaction):
		embed = interaction.message.embeds[0]
		embed.title = "Textlink Instructions"
		embed.description = "Textlinks are an easy way to send related links in the middle of a message without having to go find them. For example, you could type: \"Check out the [[wiki]] for more information\", and Incendy will followup with the link to the wiki.\n\nTextlinks are always surrounded by double square brackets (`[[...]]`), and are case-insensitive. Click the buttons below to view the available textlinks. Use `/feedback` to send ideas of textlinks you'd like to see!"

		await interaction.response.edit_message(embed=embed)
	
class GeneralLinks(discord.ui.Button):
	def __init__(self, textlinks: dict):
		super().__init__(style=discord.ButtonStyle.green, label='General')
		self.textlinks = textlinks
	
	async def callback(self, interaction: discord.Interaction):
		embed = interaction.message.embeds[0]
		embed.title = "General Textlinks"
		embed.description = "  -  ".join([f"[{textlink.replace('-', ' ').title()}]({self.textlinks[textlink]})" for textlink in self.textlinks])

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

async def setup(client):
	await client.add_cog(Basic(client))