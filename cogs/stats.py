import discord
import json
import os
import time
import datetime
from discord import app_commands
from discord.ext import commands, tasks
from resources import custom_checks as cc
from resources import incendy_image as ii
from resources import stardust_downloads as sd

class Stats(commands.Cog):
	def __init__(self, client):
		self.client = client

	async def cog_load(self):
		self.loop_get_stats.start()
		print(f' - {self.__cog_name__} cog loaded.')

	async def cog_unload(self):
		self.loop_get_stats.stop()
		print(f' - {self.__cog_name__} cog unloaded.')

	### LOOPS ###

	@tasks.loop(hours=6.0)
	async def loop_get_stats(self):
		await self.log_daily_downloads()

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
			# Get color
			filename = f"tmp/{member.id}.webp"
			await member.avatar.save(filename)
			colour = ii.get_color(filename)
			os.remove(f"{os.curdir}/{filename}")

			# Total messages
			msg_query = 'SELECT COUNT(message_id) FROM test_messages WHERE user_id = $1;'
			totalmsgs = await self.client.db.fetchval(msg_query, member.id)

			# Top Commands
			cmd_query = 'SELECT command_name, COUNT(command_name) FROM commands WHERE user_id = $1 GROUP BY command_name ORDER BY COUNT(command_name) DESC LIMIT 5'
			topcmds = await self.client.db.fetch(cmd_query, member.id)
			topcmdstr = "\n".join([f"**{record['command_name']}**   ({'{:,}'.format(record['count'])})" for record in topcmds])

			# Other stats
			joined = int(time.mktime(member.joined_at.timetuple()))
			created = int(time.mktime(member.created_at.timetuple()))

			# Create embed
			embed = discord.Embed(
				title=f"{member.display_name}'s Stats",
				color=colour,
				description=f"<:stardust:1058423314672013382> joined <t:{joined}:R>\n<:discord:1048627498734342206> joined <t:{created}:R>"
			)
			
			embed.add_field(name="Total Messages", value="{:,}".format(totalmsgs), inline=False)
			if len(topcmds) > 2:
				embed.add_field(name="Most Used Commands", value=topcmdstr)
			else:
				embed.add_field(name="Most Used Commands", value="*Use more commands to get your ranking!*")
			embed.set_thumbnail(url=member.display_avatar.url)
			embed.set_footer(text=f"{member.name}#{member.discriminator}")

			await interaction.response.send_message(embed=embed)

		# Stardust Labs stats
		else:
			# Init data
			data = {}

			# Get most recent Download Stats object
			downloads_query = await self.client.db.fetch('SELECT terralith, incendium, nullscape, structory, towers, continents, amplified FROM downloads ORDER BY day DESC LIMIT 1')
			downloads = downloads_query[0]

			# Set that Download Stats object
			data["downloads"] = {}
			for project in downloads.keys():
				data["downloads"][project] = '{:,}'.format(downloads[project])
			data["downloads"]["total"] = '{:,}'.format(sum(count for count in list(downloads)))
			
			# Get color
			filename = f"tmp/{interaction.guild.id}.webp"
			await interaction.guild.icon.save(filename)
			colour = ii.get_color(filename)
			os.remove(f"{os.curdir}/{filename}")

			# Top commands
			cmd_query = 'SELECT command_name, COUNT(command_name) FROM commands GROUP BY command_name ORDER BY COUNT(command_name) DESC LIMIT 5'
			topcmds = await self.client.db.fetch(cmd_query)

			data["commands"] = []
			for record in topcmds:
				data["commands"].append({record["command_name"]: '{:,}'.format(record["count"])})

			# Streams/Videos/Tweets
			with open("resources/stats.json", 'r') as f:
				media = json.load(f)
			data["tweets"] = '{:,}'.format(0)
			data["streams"] = '{:,}'.format(len(media["streams"]))
			data["videos"] = '{:,}'.format(len(media["videos"]))

			# Discord info
			with open("resources/settings.json", 'r') as f:
				settings = json.load(f)
			data["members"] = '{:,}'.format(interaction.guild.member_count)
			data["version"] = settings["version"]
			
			# Create image
			filepath = ii.create_stats_image(data)
			file = discord.File(filepath, filename="stats.jpg")

			embed = discord.Embed(color=colour)
			embed.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon)
			embed.set_footer(text="Does not include Curseforge downloads yet. Soon!")
			embed.set_image(url="attachment://stats.jpg")
			await interaction.response.send_message(embed=embed, file=file)

			# rm the tmp/ image
			os.remove(filepath)

	### OTHER FUNCTIONS ###

	async def log_daily_downloads(self):
		# Make the table if it doesn't already exist!
		await self.client.db.execute(
			'CREATE TABLE IF NOT EXISTS downloads(id SERIAL PRIMARY KEY, day DATE, terralith INT, incendium INT, nullscape INT, structory INT, towers INT, continents INT, amplified INT);'
		)

		# Check if we've already logged downloads today!
		potential = await self.client.db.fetchval('SELECT day FROM downloads WHERE day = current_date LIMIT 1')

		if potential != None:
			return

		stats = sd.get_downloads()

		query = '''INSERT INTO downloads (day, terralith, incendium, nullscape, structory, towers, continents, amplified) VALUES(
			current_date, $1, $2, $3, $4, $5, $6, $7
		) RETURNING id'''
		
		await self.client.db.execute(
			query, stats["terralith"], stats["incendium"], stats["nullscape"], stats["structory"], stats["structory-towers"], stats["continents"], stats["amplified-nether"]
		)

	async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
		if isinstance(error, app_commands.CommandOnCooldown):
			if interaction.command.name == "stats":
				await interaction.response.send_message("Yikes! " + str(error), ephemeral=True)
		elif isinstance(error, app_commands.CheckFailure):
			if interaction.command.name == "stats":
				await interaction.response.send_message("This command can only be used in a bot command channel like <#871376111857193000>.", ephemeral=True)

async def setup(client):
	await client.add_cog(Stats(client))