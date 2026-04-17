import discord
import re
import datetime
import logging
import validators
from time import sleep
from discord.ext import commands, tasks
from libraries import incendy, url_search
import libraries.constants as Constants

class Moderation(commands.Cog):
	def __init__(self, client: incendy.IncendyBot):
		self.client = client
		with open('resources/naughty.txt', 'r') as f:
			self.naughty = f.readlines()

	async def cog_load(self):
		self.servchan = self.client.get_channel(Constants.Channel.SERVER)
		self.to_be_banned = []
		logging.info(f'> {self.__cog_name__} cog loaded')
	
	async def cog_unload(self):
		logging.info(f'> {self.__cog_name__} cog unloaded')

	### LOOPS ###

	@tasks.loop(seconds=5.0)
	async def detect(self):
		ids = Constants.Role.ALL_ADMINISTRATION + Constants.Role.ALL_PATRONS + [Constants.Role.BOOSTER] + [Constants.Role.CONTRIBUTOR] + [Constants.Role.DEV_TEAM]
		strikes = []
		
		for cache in reversed(self.client.cached_messages):
			if (discord.utils.utcnow() - cache.created_at).seconds > 15:
				break
			if not cache.guild:
				continue
			if cache.guild.id != Constants.Guild.STARDUST_LABS:
				continue
			if [role.id for role in cache.author.roles if role.id in ids]:
				continue

			if any([word for word in cache.content.split() if validators.url(word) and not word.endswith('.gif') and "https://tenor.com" not in word]):
				strikes.append(cache)
		
		if len(strikes) >= 3:
			sus_users = [cache.author.id for cache in strikes]
			dead_users = []
			dead_caches = []
			for cache in strikes:
				if sus_users.count(cache.author.id) >= 3:
					if cache.author.id not in dead_users:
						dead_caches.append(cache)
						dead_users.append(cache.author.id)

			if len(dead_caches) > 0:
				for cache in dead_caches:
					await self.ban_hammer(cache)

	@detect.before_loop
	async def before_loop_wait(self):
		await self.client.wait_until_ready()

	### OTHER FUNCTIONS ###

	async def ban_hammer(self, message):
		prison_channel = self.client.get_channel(Constants.Channel.PRISON)
		embed = discord.Embed(colour=discord.Colour.blue(), timestamp=datetime.datetime.now(datetime.timezone.utc))
		embed.set_author(name="Lmao, I caught someone being silly!")
		embed.add_field(name=fr"Here was {message.author.name}'s' silly message, censored for your convenience. \:)", value="||`" + message.content + "`||")
		embed2 = discord.Embed(colour=discord.Colour.blue(), timestamp=datetime.datetime.now(datetime.timezone.utc))
		embed2.set_author(name=message.author.name)
		embed2.add_field(name="Hey y'all!", value="I *probably* banned them correctly, but if I didn't... give the Stardust peeps a holler!")

		await message.author.send(f"Hello. I have banned you from the Stardust Labs server. If you believe this was a mistake, please DM catter1 (<@{Constants.User.CATTER}>).")
		await message.guild.ban(message.author, reason="I think this kid was being quite silly! -Incendy")

		await prison_channel.send(embed=embed)
		await message.channel.send(embed=embed2)

	### COMMANDS ###

	### LISTENERS ###

	async def video_check(self, message: discord.Message) -> None:
		ids = Constants.Role.ALL_TRUSTED
		if not [role.id for role in message.author.roles if role.id in ids]:

			for item in message.attachments:
				if item.content_type.split("/")[0] == "video":
					await message.delete()
					await message.channel.send(r"Sorry, no videos allowed \:)")
					return

			exts = ['.mp4', '.mov', '.avi', '.mk4', '.flv', '.wmv', '.m4v', '.webm', '.vob', '.mts', '.ogv', '.3gp']
			if url_search.url(message.content) and any([ext for ext in exts if ext in message.content]):
				await message.delete()
				await message.channel.send(r"Sorry, no videos allowed \:)")

	async def subjugate_suspicion(self, member: discord.Member, points: int, reasons: list[str]):
		# Set color based on priority
		priority_color = discord.colour.Colour.brand_green()
		if 2 <= points <= 4:
			priority_color = discord.colour.Colour.yellow()
		elif 5 <= points <= 7:
			priority_color = discord.colour.Colour.orange()
		elif 8 <= points:
			priority_color = discord.colour.Colour.brand_red()

		# Setup embed
		embed = discord.Embed(
			colour=priority_color,
			title="Suspicious user",
			timestamp=datetime.datetime.now()
		)

		embed.add_field(
			name="User",
			value=f"> **Username:** {member.name} (<@{member.id}>)\n> **ID:** {member.id}\n> **Created:** <t:{int(member.created_at.timestamp())}:R>\n> **Joined:** <t:{int(member.joined_at.timestamp())}:R>\n> **Sus Score:** {points}/10",
			inline=False
		)
		embed.add_field(
			name="Reasons",
			value="\n".join([f"- {reason}" for reason in reasons]),
			inline=False
		)
		embed.add_field(
			name="Notes",
			value=f"This user was given the <@&{Constants.Role.SUSPICIOUS}> role. They can only chat in <#{Constants.Channel.HONEYPOT}>. If they send a message asking for rescue, remove the role from them."
				if points >= 2 else
				f"This user is not suspicious enough to be given the <@&{Constants.Role.SUSPICIOUS}> role, but maybe keep an eye on them.",
			inline=False
		)
		embed.set_thumbnail(url=member.display_avatar.url)

		# Get guild/channel/role
		guild = self.client.get_guild(Constants.Guild.STARDUST_LABS)
		sus_role = guild.get_role(Constants.Role.SUSPICIOUS)
		prison_channel = self.client.get_channel(Constants.Channel.PRISON)

		# Apply role and send embed
		await prison_channel.send(embed=embed)
		if points >= 2:
			await member.add_roles(sus_role, reason="Sus")


	@commands.Cog.listener()
	async def on_thread_create(self, thread: discord.Thread):
		await thread.join()
	
	@commands.Cog.listener()
	async def on_message(self, message: discord.Message):
		if not message.author.bot and not message.author.guild_permissions.administrator:

			# Naughty spammers :3
			if any([word.strip("\n") in message.content.lower() for word in self.naughty]):
				await self.ban_hammer(message)

			# No videos in #general
			if message.channel.id in [Constants.Channel.GENERAL]:
				await self.video_check(message=message)
	
	@commands.Cog.listener()
	async def on_message_edit(self, _: discord.Message, after: discord.Message):
		if not after.author.bot and not after.author.guild_permissions.administrator:

			# No videos in #general
			if after.channel.id in [Constants.Channel.GENERAL]:
				await self.video_check(message=after)
				
	@commands.Cog.listener()
	async def on_member_join(self, member: discord.Member):
		# Check for suspicious members
		sleep(30)
		points = 0
		reasons = []

		# Default avatar (2 points)
		if member.display_avatar == member.default_avatar:
			reasons.append("Default avatar")
			points += 2

		# Generated username (1-3 points)
		underscore_re = r"[a-zA-Z0-9][_][a-zA-Z0-9]"
		underscore_results = re.findall(underscore_re, member.name)
		if len(underscore_results) == 1:
			reasons.append("Randomly generated username")
			points += 1
			second_half = member.name.split('_', 1)[1]
			if second_half.isnumeric():
				points += 2

		# New account (1-3 points)
		now = datetime.datetime.now(datetime.timezone.utc)
		if datetime.timedelta(0) <= now - member.created_at <= datetime.timedelta(days=1):
			reasons.append("Extremely new account")
			points += 3
		elif datetime.timedelta(0) <= now - member.created_at <= datetime.timedelta(days=5):
			reasons.append("Very new account")
			points += 2
		elif datetime.timedelta(0) <= now - member.created_at <= datetime.timedelta(days=30):
			reasons.append("Somewhat new account")
			points += 1

		# Deleted welcome message (2 points)
		welcome_channel = self.client.get_channel(Constants.Channel.WELCOME)
		if not [message async for message in welcome_channel.history(limit=20) if message.author == member]:
			reasons.append("Welcome message deleted")
			points += 2

		# Status (-1 points)
		if member.activity:
			points -= 1

		if points > 0:
			await self.subjugate_suspicion(member, points, reasons)

async def setup(client):
	await client.add_cog(Moderation(client))