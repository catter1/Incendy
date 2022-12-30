import discord
import requests
import json
import os
import socket
import urllib3
import time
import cv2 as cv
import numpy as np
from discord import app_commands
from discord.ext import commands, tasks
from bs4 import BeautifulSoup
from collections import OrderedDict
from resources import custom_checks as cc

class Stats(commands.Cog):
	def __init__(self, client):
		self.client = client

	async def cog_load(self):
		#self.loop_get_stats.start()
		print(f' - {self.__cog_name__} cog loaded.')

	async def cog_unload(self):
		#self.loop_get_stats.stop()
		print(f' - {self.__cog_name__} cog unloaded.')

	### LOOPS ###

	@tasks.loop(hours=6.0)
	async def loop_get_stats(self):
		self.stats = await self.get_stats()

	@loop_get_stats.before_loop
	async def before_change_presence(self):
		await self.client.wait_until_ready()

	### COMMANDS ###

	@app_commands.command(name="news", description="The latest unofficial news from Stardust Labs")
	@cc.in_bot_channel()
	@app_commands.checks.dynamic_cooldown(cc.very_long_cd)
	async def news(self, interaction: discord.Interaction):
		""" /news """

		with open("resources/news.json", 'r') as f:
			news = json.load(f)

		catter = interaction.guild.get_member(260929689126699008)
		embed = discord.Embed(color=discord.Colour.brand_red())
		embed.set_author(name="Unofficial Stardust News", icon_url=catter.avatar.url)
		
		for item in news:
			embed.title = item["title"]
			embed.description = f"{item['desc']}\n<t:{item['timestamp']}:D>"

		await interaction.response.send_message(embed=embed)
	
	@app_commands.command(name="stats", description="Shows stats about Stardust Labs")
	@cc.in_bot_channel()
	@app_commands.checks.dynamic_cooldown(cc.very_long_cd)
	async def stats(self, interaction: discord.Interaction, member: discord.Member = None):
		""" /stats [member]"""

		# Individual member stats
		if member:
			filename = f"seeds/{member.id}.webp"
			await member.avatar.save(filename)
			colour = await self.get_color(filename)
			os.remove(f"{os.curdir}/{filename}")

			joined = int(time.mktime(member.joined_at.timetuple()))
			created = int(time.mktime(member.created_at.timetuple()))

			embed = discord.Embed(
				title=f"{member.display_name}'s Stats",
				color=colour,
				description=f"<:stardust:1058423314672013382> joined <t:{joined}:R>\n<:discord:1048627498734342206> joined <t:{created}:R>"
			)
			
			embed.add_field(name="Total Messages", value="Coming Soon", inline=False)
			embed.add_field(name="Most Used Commands", value="Coming Soon")
			embed.set_thumbnail(url=member.display_avatar.url)
			embed.set_footer(text=f"{member.name}#{member.discriminator}")

			await interaction.response.send_message(embed=embed)

		# Stardust Labs stats
		else:
			stats = self.stats

			filename = f"seeds/{interaction.guild.id}.webp"
			await member.avatar.save(filename)
			colour = await self.get_color(filename)
			os.remove(f"{os.curdir}/{filename}")
			
			embed = discord.Embed(color=colour)
			embed.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon)
			embed.add_field(name='Incendy Version', value=self.version)
			embed.add_field(name='Member Count', value=interaction.guild.member_count)
			embed.add_field(name='StardustTV', value="Videos: {:,}".format(stats["videos"] + "\nStreams: {:,}".format(stats["streams"])))
			#embed.add_field(name='\u200b', value='\u200b')
			embed.add_field(name='Terralith Downloads', value="{:,}".format(stats["terralith"]))
			embed.add_field(name='Incendium Downloads', value="{:,}".format(stats["incendium"]))
			embed.add_field(name='Nullscape Downloads', value="{:,}".format(stats["nullscape"]))
			embed.add_field(name='Structory Downloads', value="{:,}".format(stats["structory"]))
			embed.add_field(name='Amplified Nether Downloads', value="{:,}".format(stats["amplified-nether"]))
			embed.add_field(name='Continents Downloads', value="{:,}".format(stats["continents"]))
			embed.set_footer(text='<:pmc:1045336243216584744> <:modrinth:1045336248950214706> <:curseforge:1045336245900939274> <:seedfix:917599175259070474>')
			await interaction.response.send_message(embed=embed)

	# thanks! https://towardsdatascience.com/finding-most-common-colors-in-python-47ea0767a06a
	async def get_color(self, filename: str) -> discord.Color:
		img = cv.imread(filename) #Image here
		img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
		img = cv.resize(img, (80, 80), interpolation = cv.INTER_AREA)

		unique, counts = np.unique(img.reshape(-1, 3), axis=0, return_counts=True)
		final = unique[np.argmax(counts)]
		colour = discord.Colour.from_rgb(int(final[0]), int(final[1]), int(final[2]))

		return colour

	async def get_stats(self) -> dict:
		stats = {}

		with open('resources/stats.json', 'r') as f:
			stats["streams"] = len(json.load(f)["streams"])
			stats["videos"] = len(json.load(f)["videos"])

		projects = ["terralith", "incendium", "nullscape", "amplified-nether", "continents", "structory"]
		for project in projects:
			stats[project] = 0

		# Curseforge
		for project in projects:
			## Thanks! https://python.tutorialink.com/pythons-requests-triggers-cloudflares-security-while-urllib-does-not/
			answers = socket.getaddrinfo('www.curseforge.com', 443)
			(family, type, proto, canonname, (address, port)) = answers[0]
			headers = OrderedDict({
				'Host': "www.curseforge.com",
				'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
			})
			s = requests.Session()
			s.headers = headers
			urllib3.disable_warnings()
			response = s.get(f"https://{address}/minecraft/mc-mods/{project}", verify=False)

			soup = BeautifulSoup(response.content, "html.parser")
			stats[project] += int(soup.find_all(text="Total Downloads")[0].parent.parent.contents[3].text.replace(",", ""))
		
		# Modrinth
		headers = {'User-Agent': 'catter1/Incendy (catter@zenysis.net)'}
		projects.remove('structory')
		for project in projects:
			url = f"https://api.modrinth.com/v2/project/{project}"
			x = requests.get(url=url, headers=headers)
			stats[project] += json.loads(x.text)["downloads"]

		# PMC
		pmc_projects = {
			"terralith": "terralith-overworld-evolved-100-biomes-caves-and-more/",
			"incendium": "incendium-nether-expansion",
			"nullscape": "nullscape",
			"structory": "structory",
			"amplified-nether": "amplified-nether-1-18/",
			"continents": "continents"
		}
		for project in pmc_projects.keys():
			url = f"https://www.planetminecraft.com/data-pack/{pmc_projects[project]}"
			x = requests.get(url=url, headers=headers)
			soup = BeautifulSoup(x.text, "html.parser")
			stats[project] += int(soup.find_all(text=" downloads, ")[0].parent.contents[1].text.replace(",", ""))

		# Seedfix
		url = "https://seedfix.stardustlabs.net/api/get_downloads/"
		x = requests.get(url=url, headers=headers)
		stats["terralith"] += int(x.text)

		return stats

	async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
		if isinstance(error, app_commands.CommandOnCooldown):
			if interaction.command.name == "stats":
				await interaction.response.send_message("Yikes! " + str(error), ephemeral=True)
		elif isinstance(error, app_commands.CheckFailure):
			if interaction.command.name == "stats":
				await interaction.response.send_message("This command can only be used in a bot command channel like <#871376111857193000>.", ephemeral=True)

async def setup(client):
	await client.add_cog(Stats(client))