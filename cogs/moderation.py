import discord
import json
import datetime
import logging
import validators
from discord import app_commands
from discord.ext import commands, tasks
from libraries import incendy, url_search
import libraries.constants as Constants

class Moderation(commands.Cog):
	def __init__(self, client: incendy.IncendyBot):
		self.client = client
		with open('resources/naughty.txt', 'r') as f:
			self.naughty = f.readlines()

		self.shutup_app = app_commands.ContextMenu(
			name='Shutup',
			callback=self.shutup_button,
		)
		self.client.tree.add_command(self.shutup_app)

	async def cog_load(self):
		self.servchan = self.client.get_channel(Constants.Channel.SERVER)
		self.to_be_banned = []
		self.ping_check.start()
		self.timeout_check.start()
		logging.info(f'> {self.__cog_name__} cog loaded')
	
	async def cog_unload(self):
		self.client.tree.remove_command(self.shutup_app.name, type=self.shutup_app.type)
		self.ping_check.stop()
		self.timeout_check.stop()
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
		stardust_channel = self.client.get_channel(Constants.Channel.STARDUST)
		embed = discord.Embed(colour=discord.Colour.blue(), timestamp=datetime.datetime.utcnow())
		embed.set_author(name="Lmao, I caught someone being silly!")
		embed.add_field(name=fr"Here was {message.author.name}'s' silly message, censored for your convenience. \:)", value="||`" + message.content + "`||")
		embed2 = discord.Embed(colour=discord.Colour.blue(), timestamp=datetime.datetime.utcnow())
		embed2.set_author(name=message.author.name)
		embed2.add_field(name="Hey y'all!", value="I *probably* banned them correctly, but if I didn't... give the Stardust peeps a holler!")

		await message.author.send("Howdy! I have banned you from the Stardust Labs server for spamming, scamming, or being naughty. If you believe this was a mistake, please DM one of the Stardust peeps:\ncatter1 - `catter#0001`\nWhale - `Whale#4433`\nNetheferious - `Netheferious#1181`")
		await message.guild.ban(message.author, reason="I think this kid was being quite silly! -Incendy")

		await stardust_channel.send(embed=embed)
		await message.channel.send(embed=embed2)

	### COMMANDS ###

	### LISTENERS ###

	async def video_check(self, message: discord.Message) -> None:
		ids = Constants.Role.ALL_ADMINISTRATION + Constants.Role.ALL_DONATORS + Constants.Role.ALL_CONTRIBUTORS
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

			# Ping check
			if Constants.User.STARMUTE in message.raw_mentions:
				await self.check_ping(message=message)
	
	@commands.Cog.listener()
	async def on_message_edit(self, _: discord.Message, after: discord.Message):
		if not after.author.bot and not after.author.guild_permissions.administrator:

			# No videos in #general
			if after.channel.id in [Constants.Channel.GENERAL]:
				await self.video_check(message=after)

async def setup(client):
	await client.add_cog(Moderation(client))