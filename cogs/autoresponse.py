import discord
import logging
import re
import json
import requests
from discord import app_commands
from discord.ext import commands
from libraries import incendy

class Autoresponse(commands.Cog):
	def __init__(self, client: incendy.IncendyBot):
		self.client = client

	async def cog_load(self):
		with open('resources/textlinks.json', 'r') as f:
			self.textlinks = json.load(f)

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

	@commands.Cog.listener()
	async def on_message(self, message: discord.Message):
		if not message.author.bot:
			matches = re.findall(r"[\[]{2}(\w[\w |':]+\w)?[\]]{2}", message.content)
			if len(matches) > 0:
				await self.do_textlinks(message=message, matches=matches)

async def setup(client):
	await client.add_cog(Autoresponse(client))