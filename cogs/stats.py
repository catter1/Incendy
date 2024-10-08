import discord
import os
import time
import logging
from discord import app_commands
from discord.ext import commands, tasks
from libraries import incendy
from libraries import image_tools
from libraries import stardust_downloads as sd
import libraries.constants as Constants

class Stats(commands.Cog):
	def __init__(self, client: incendy.IncendyBot):
		self.client = client

	async def cog_load(self):
		if self.client.environment["INCENDY_STATS_UPDATE_ENABLED"]:
			self.loop_get_stats.start()
		else:
			logging.warning("Stats loop is disabled! Check your environment variable INCENDY_STATS_UPDATE_ENABLED if this is unintentional.")
		logging.info(f'> {self.__cog_name__} cog loaded')

	async def cog_unload(self):
		if self.client.environment["INCENDY_STATS_UPDATE_ENABLED"]:
			self.loop_get_stats.stop()
		logging.info(f'> {self.__cog_name__} cog unloaded')

	### LOOPS ###

	@tasks.loop(hours=6.0)
	async def loop_get_stats(self):
		await self.log_daily_downloads()

	@loop_get_stats.before_loop
	async def before_change_presence(self):
		await self.client.wait_until_ready()

	### COMMANDS ###

	@app_commands.command(name="incendy", description="Shows information about Incendy!")
	@incendy.in_bot_channel()
	@app_commands.checks.dynamic_cooldown(incendy.long_cd)
	async def _incendy(self, interaction: discord.Interaction):
		colour = await image_tools.get_user_color(self.client.user)

		embed = discord.Embed(
			color=colour,
			title="About Me",
			description=f"Hi! I'm Incendy, the loyal Discord bot of Stardust Labs!\n\n<@{Constants.User.CATTER}> brought me into this world on November 24, 2020. I evolved from a joke bot that added funny reactions to messages, into the all-powerful bot I am today.\n\nIf you aren't familiar with my commands, do `/help`! As for my non-command functions:\n- Automatically detect and upload logs to [mclo.gs](https://mclo.gs/)\n- Check for and resolve \"textlinks\" such as `[[wiki]]`\n- Post Stardust project releases and social media posts in <#{Constants.Channel.STARDUST_NEWS}>\n- Additional specialized moderation\n- An \"App Command\" that translates messages to English upon right-click\n- ...and more!\n\nIf you have any suggestions or found any bugs, please submit them to the GitHub issue tracker, linked below. If Incendy has helped you in any way, consider donating to catter via the link below. Thank you!"
		)
		embed.set_author(name=self.client.user.display_name, icon_url=self.client.user.display_avatar.url)

		view = discord.ui.View()
		view.add_item(discord.ui.Button(style=discord.ButtonStyle.link, label="Source Code", url="https://github.com/catter1/incendy", emoji=Constants.Emoji.GITHUB))
		view.add_item(discord.ui.Button(style=discord.ButtonStyle.link, label="Donate", url="https://ko-fi.com/catter1", emoji=Constants.Emoji.KOFI))
		view.add_item(discord.ui.Button(style=discord.ButtonStyle.blurple, label="Website (soon™️!)", disabled=True))

		await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
	
	@app_commands.command(name="stats", description="Shows stats about Stardust Labs")
	@incendy.in_bot_channel()
	@app_commands.checks.dynamic_cooldown(incendy.short_cd)
	async def stats(self, interaction: discord.Interaction, member: discord.Member = None):
		""" /stats [member]"""

		# Individual member stats
		if member:
			await interaction.response.defer(thinking=True)
			# Get color
			colour = await image_tools.get_user_color(member)

			# Total messages
			msg_query = 'SELECT COUNT(message_id) FROM messages WHERE user_id = $1;'
			totalmsgs = await self.client.db.fetchval(msg_query, member.id)

			# Top Commands
			cmd_query = 'SELECT command_name, COUNT(command_name) FROM commands WHERE user_id = $1 GROUP BY command_name ORDER BY COUNT(command_name) DESC LIMIT 5'
			topcmds = await self.client.db.fetch(cmd_query, member.id)
			topcmdstr = "\n".join([f"`{record['command_name']}`   ({'{:,}'.format(record['count'])})" for record in topcmds])

			# Top FAQs
			faq_query = 'SELECT faq_name, COUNT(faq_name) FROM faqs WHERE user_id = $1 GROUP BY faq_name ORDER BY COUNT(faq_name) DESC LIMIT 5'
			topfaqs = await self.client.db.fetch(faq_query, member.id)
			topfaqstr = "\n".join([f"`{record['faq_name']}`   ({'{:,}'.format(record['count'])})" for record in topfaqs])

			# Other stats
			joined = int(time.mktime(member.joined_at.timetuple()))
			created = int(time.mktime(member.created_at.timetuple()))

			# Create embed
			embed = discord.Embed(
				title=f"{member.global_name}'s Stats",
				color=colour,
				description=f"{Constants.Emoji.STARDUST} joined <t:{joined}:R>\n{Constants.Emoji.DISCORD} joined <t:{created}:R>"
			)
			
			embed.add_field(name="Total Messages", value="{:,}".format(totalmsgs), inline=False)
			if len(topcmds) > 2:
				embed.add_field(name="Most Used Commands", value=topcmdstr, inline=False)
			else:
				embed.add_field(name="Most Used Commands", value="*Use more commands to get your ranking!*", inline=False)
			if len(topfaqs) > 2:
				embed.add_field(name="Most Used FAQs", value=topfaqstr, inline=False)
			else:
				embed.add_field(name="Most Used FAQs", value="*Use more FAQs to get your ranking!*", inline=False)
			embed.set_thumbnail(url=member.display_avatar.url)
			embed.set_footer(text=f"{member.name}")

			await interaction.followup.send(embed=embed)

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
			colour = image_tools.get_color(filename)
			os.remove(f"{os.curdir}/{filename}")

			# Top commands
			cmd_query = 'SELECT command_name, COUNT(command_name) FROM commands GROUP BY command_name ORDER BY COUNT(command_name) DESC LIMIT 5'
			topcmds = await self.client.db.fetch(cmd_query)

			data["commands"] = []
			for record in topcmds:
				data["commands"].append({record["command_name"]: '{:,}'.format(record["count"])})

			# Streams/Videos/Tweets
			streams = await self.client.db.fetchval('SELECT COUNT(slug) FROM stardusttv WHERE media = $1;', "stream")
			videos = await self.client.db.fetchval('SELECT COUNT(slug) FROM stardusttv WHERE media = $1;', "video")
			tweets = await self.client.db.fetchval('SELECT COUNT(slug) FROM stardusttv WHERE media = $1;', "tweet")

			data["tweets"] = '{:,}'.format(tweets)
			data["streams"] = '{:,}'.format(streams)
			data["videos"] = '{:,}'.format(videos)

			# Discord info
			data["members"] = '{:,}'.format(interaction.guild.member_count)
			data["version"] = self.client.settings["version"]
			
			# Create image
			filepath = image_tools.create_stats_image(data)
			file = discord.File(filepath, filename="stats.jpg")

			embed = discord.Embed(color=colour)
			embed.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon)
			embed.set_footer(text="Template by Tera", icon_url=self.client.get_user(Constants.User.TERA).avatar.url)
			embed.set_image(url="attachment://stats.jpg")
			await interaction.response.send_message(embed=embed, file=file)

			# rm the tmp/ image
			os.remove(filepath)

	### OTHER FUNCTIONS ###

	async def log_daily_downloads(self):
		# Check if we've already logged downloads today!
		potential = await self.client.db.fetchval('SELECT day FROM downloads WHERE day = current_date LIMIT 1')

		if potential is not None:
			return

		logging.info("Updating the STATS table...")

		stats = sd.get_downloads(self.client.keys["overwolf-key"], self.client.keys["git-pat"])

		query = '''INSERT INTO downloads (day, terralith, incendium, nullscape, structory, towers, continents, amplified) VALUES(
			current_date, $1, $2, $3, $4, $5, $6, $7
		) RETURNING id'''
		
		await self.client.db.execute(
			query, stats["terralith"], stats["incendium"], stats["nullscape"], stats["structory"], stats["structory-towers"], stats["continents"], stats["amplified-nether"]
		)

		logging.info("Successfully updated the STATS table.")

async def setup(client):
	await client.add_cog(Stats(client))
