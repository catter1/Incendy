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
from libraries import incendy

class Autoresponse(commands.Cog):
	def __init__(self, client: incendy.IncendyBot):
		self.client = client

	async def cog_load(self):
		with open('resources/textlinks.json', 'r') as f:
			self.textlinks = json.load(f)
		with open('resources/reposts.json', 'r') as f:
			self.reposts = json.load(f)

		resp = requests.get("https://misode.github.io/sitemap.txt")
		self.misode_urls = {url.split('/')[-2]: url for url in resp.text.split("\n") if len(url.split("/")) > 4}
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
						links.append(discord.ui.Button(style=discord.ButtonStyle.link, label=f"Misode: {page.title()}", url=self.misode_urls[page], emoji="<:misode:1087040969574187010>"))
				
				elif "wiki" in match.split("|")[0].lower():
					page = match.split("|")[-1].lower()
					if page in self.wiki_urls.keys():
						links.append(discord.ui.Button(style=discord.ButtonStyle.link, label=f"Wiki: {page.title()}", url=self.wiki_urls[page], emoji="<:miraheze:890077957069111316>"))

				elif match.split("|")[0].lower() in ["mc", "mcpe", "realms"]:
					bug_id = match.split("|")[-1].lower()
					if bug_id.isdigit():
						links.append(discord.ui.Button(style=discord.ButtonStyle.link, label=f"{match.split('|')[0].upper()} {bug_id}", url=f"https://bugs.mojang.com/browse/{match.split('|')[0].upper()}-{bug_id}", emoji="<:mojira:1087079351452958761>"))

		view = discord.ui.View()
		if len(links) > 0:
			for item in links:
				view.add_item(item)
			await message.reply(view=view, mention_author=False)

	async def do_pastebin(self, message: discord.Message) -> None:
		for file in message.attachments:
			
			if any(ext in file.filename for ext in [".log", ".txt", ".log.gz"]):

				if file.filename.endswith(".log.gz"):
					bts = await file.read()

					with gzip.GzipFile(fileobj=io.BytesIO(bts), mode='rb') as gz:
						content = gz.read().decode('utf-8')
				else:
					bts = await file.read()
					content = bts.decode('utf-8')
				
				headers = {'Content-Type': 'application/x-www-form-urlencoded'}
				url = "https://api.mclo.gs/1/log"
				data = {"content": f"{content}"}
				x = requests.post(url, data=data, headers=headers)

				logurl = json.loads(x.text)["url"]

				await message.reply(f"{file.filename}: {logurl}", mention_author=False)

	async def stop_mod_reposts(self, message: discord.Message, url: str) -> None:
		for illegal in self.reposts:
			if illegal["domain"] in url:
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

async def setup(client):
	await client.add_cog(Autoresponse(client))