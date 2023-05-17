import discord
import json
import datetime
import logging
import validators
from discord import app_commands
from discord.ext import commands, tasks
from libraries import incendy, url_search

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
		self.servchan = self.client.get_channel(756923587339878420)
		self.to_be_banned = []
		self.ping_check.start()
		self.detect.start()
		self.timeout_check.start()
		logging.info(f'> {self.__cog_name__} cog loaded')
	
	async def cog_unload(self):
		self.client.tree.remove_command(self.shutup_app.name, type=self.shutup_app.type)
		self.ping_check.stop()
		self.detect.stop()
		self.timeout_check.stop()
		logging.info(f'> {self.__cog_name__} cog unloaded')

	### LOOPS ###

	@tasks.loop(seconds=5.0)
	async def detect(self):
		# ids: Starmute, Stardust, Dev Team, Assistant, Contributor, Overlord, Inferno, Sentry, Blaze, Supporter, Premium Member
		ids = [744788173128859670, 744788229579866162, 885719021176119298, 862343886864384010, 749701703938605107, 877672384872738867, 795469887790252084, 795469805678755850, 1031650636544090166, 941157235390820382, 1031650634048487426]
		strikes = []
		#pattern = re.compile(r'(http|ftp|https|www):\/\/([\w\-_]+(?:(?:\.[\w\-_]+)+))([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?')
		
		for cache in reversed(self.client.cached_messages):
			try:
				if cache.guild.id == 738046951236567162:
					if (discord.utils.utcnow() - cache.created_at).seconds < 15:
						if not [role.id for role in cache.author.roles if role.id in ids]:
							#if len(re.findall(pattern, cache.content)) > 0 or "discord.gg" in cache.content:
							if any([word for word in cache.content.split() if validators.url(word) and not word.endswith('.gif') and not "https://tenor.com" in word]):
								#if not re.findall(r'\.gif', cache.content):
								strikes.append(cache)
					else:
						break
			except:
				pass
		
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

	@tasks.loop(minutes=10.0)
	async def ping_check(self):
		with open('resources/pinglog.txt', 'w') as plog:
			plog.write('')

	@tasks.loop(hours=8.0)
	async def timeout_check(self):
		with open('resources/timeout.json') as f:
			log = json.load(f)
		
		today = datetime.datetime.today().strftime("%d/%m/%Y")
		if today not in log["days"]:
			guild = self.client.get_guild(725920503893590056)
			
			# Ensure days dict doesn't get bloated
			log["days"].append(today)
			while len(log["days"]) > 5:
				log["days"].pop(0)

			# Sort through members' timeouts
			for entry_id in log["members"]:
				days = log["members"][entry_id]
				member = guild.get_member(int(entry_id))

				# Decrement days
				if days <= 1:
					log["members"].pop(entry_id)
				else:
					log["members"][entry_id] -= 1

				# Just in case the perpetrator leaves the server, we won't get annoying errors... but will still catch them if they rejoin
				if member == None:
					continue
				
				# Safe way to respect API
				if days < 28:
					future = datetime.timedelta(days=days)
				else:
					future = datetime.timedelta(days=27)
				
				# Remove/reapply timeout - this is cause API shenanigans
				await member.timeout(None)
				await member.timeout(future, reason="Shutup loser")
			
			# Save changes
			with open('resources/timeout.json', 'w') as f:
				json.dump(log, f, indent=4)

	@detect.before_loop
	@ping_check.before_loop
	@timeout_check.before_loop
	async def before_loop_wait(self):
		await self.client.wait_until_ready()

	### OTHER FUNCTIONS ###

	async def ban_hammer(self, message):
		stardust_channel = self.client.get_channel(825941927215890502)
		embed = discord.Embed(colour=discord.Colour.blue(), timestamp=datetime.datetime.utcnow())
		embed.set_author(name="Lmao, I caught someone being silly!")
		embed.add_field(name=f"Here was {message.author.name}'s' silly message, censored for your convenience. \:)", value="||`" + message.content + "`||")
		embed2 = discord.Embed(colour=discord.Colour.blue(), timestamp=datetime.datetime.utcnow())
		embed2.set_author(name=message.author.name)
		embed2.add_field(name="Hey y'all!", value="I *probably* banned them correctly, but if I didn't... give the Stardust peeps a holler!")

		await message.author.send("Howdy! I have banned you from the Stardust Labs server for spamming, scamming, or being naughty. If you believe this was a mistake, please DM one of the Stardust peeps:\ncatter1 - `catter#0001`\nWhale - `Whale#4433`\nNetheferious - `Netheferious#1181`")
		await message.guild.ban(message.author, reason="I think this kid was being quite silly! -Incendy")

		await stardust_channel.send(embed=embed)
		await message.channel.send(embed=embed2)

	### COMMANDS ###

	async def shutup(self, interaction: discord.Interaction, member: discord.Member, days: int = 9999):
		if days < 27:
			future = datetime.timedelta(days=days)
		else:
			with open("resources/timeout.json", 'r') as f:
				log = json.load(f)

			log["members"][member.id] = days - 1
			future = datetime.timedelta(days=27)

			with open("resources/timeout.json", 'w') as f:
				json.dump(log, f, indent=4)

		await interaction.response.send_message(f"{member.mention} shut up, nerd")
		await member.timeout(None)
		await member.timeout(future, reason="Shutup loser")
	
	@app_commands.default_permissions(administrator=True)
	@app_commands.checks.has_permissions(administrator=True)
	async def shutup_button(self, interaction: discord.Interaction, member: discord.Member):
		await self.shutup(interaction, member)

	@app_commands.command(name="shutup", description="[ADMIN] Time out a user forever (or custom amount of days)")
	@app_commands.default_permissions(administrator=True)
	@app_commands.checks.has_permissions(administrator=True)
	@app_commands.describe(
    	member="Member to shutup",
    	days="(Optional) Amount of days to timeout for. If ignored, will shutup forever"
	)
	async def shutup_cmd(self, interaction: discord.Interaction, member: discord.Member, days: int = 9999):
		await self.shutup(interaction, member, days)

	@app_commands.command(name="jschlatt", description="[ADMIN] You know what this does...")
	@app_commands.default_permissions(administrator=True)
	@app_commands.checks.has_permissions(administrator=True)
	@app_commands.describe(
    	strings="Purge all members that have any (space-separated) string in their name. Optional compat with minutes, but required if minutes not provided.",
    	minutes="Purge all members that joined in past x minutes. Optional compat with strings, but required if strings not provided."
	)
	async def jschlatt(self, interaction: discord.Interaction, strings: str = None, minutes: int = 0):
		# Double check in case if dumb
		if strings == None and minutes <= 0:
			await interaction.response.send_message("You need to provide either a list of names, amount of time, or both!", ephemeral=True)
			return
		
		# Safe init (in case)
		victims = []
		if strings:
			names = strings.split(" ")

		# List of all users with any {names} strings in their name, **AND** joined in the last {minutes} minutes
		if names and minutes > 0:
			checkpoint = discord.utils.utcnow() - datetime.timedelta(minutes=minutes)

			innocents = [member for member in interaction.guild.members if any([name for name in names if name.startswith("!") and name[1:].lower() in member.name.lower()]) and member.joined_at > checkpoint]
			victims = [member for member in interaction.guild.members if any([name for name in names if not name.startswith("!") and name.lower() in member.name.lower()]) and member.joined_at > checkpoint]
		
		# List of all users that joined in the last {minutes} minutes
		elif minutes > 0:
			checkpoint = discord.utils.utcnow() - datetime.timedelta(minutes=minutes)
			victims = [member for member in interaction.guild.members if member.joined_at > checkpoint]

		# List of all users with any {names} strings in their name
		elif names:
			innocents = [member for member in interaction.guild.members if any([name for name in names if name.startswith("!") and name[1:].lower() in member.name.lower()])]
			victims = [member for member in interaction.guild.members if any([name for name in names if not name.startswith("!") and name.lower() in member.name.lower()])]
			
		# No victims were found!
		if len(victims) == 0:
			lazy_response = "No users were found with your provided strings and/or minutes!"
			if minutes > 0:
				lazy_response += f"\n\nMinutes: {minutes}"
			if names:
				lazy_response += f"\n\nStrings: {names}"
			await interaction.response.send(lazy_response, ephemeral=True)
			return

		# Create the strings
		if len(victims) > 0:
			victimstr = ", ".join(victim.mention for victim in victims)
		else:
			victimstr = "NONE"
		if len(victimstr) > 1024:
			victimstr = "Too many victims to display! You will need to YOLO it..."
		if names: #There are no innocents if names were not provided
			if len(innocents) > 0:
				innocentstr = ", ".join(innocent.mention for innocent in innocents)
			else:
				innocentstr = "NONE"
			if len(innocentstr) > 1024:
				innocentstr = "Too many innocents to display! You've excluded plenty of users."	

		# We all gucci - send the funnee message and commence banning
		embed = discord.Embed(color= discord.Colour.brand_red(), title= "*Only for the most extreme of emergencies!*")
		embed.set_author(name="Jschlatt Button", icon_url="https://cdn.discordapp.com/emojis/944687134537842779.webp?size=96&quality=lossless")
		embed.add_field(name="Victims (Banned):", value=victimstr, inline=False)
		if names: embed.add_field(name="Innocents (Not Banned):", value=innocentstr, inline=False)
		embed.set_footer(text="React with ✅ to confirm the purge.")
		if minutes > 0:
			if len(victims) == 1:
				embed.description = f"Purging {len(victims)} user who joined in past {minutes} minutes."
			else:
				embed.description = f"Purging {len(victims)} users who joined in past {minutes} minutes."
		else:
			if len(victims) == 1:
				embed.description = f"Purging {len(victims)} user from this server."
			else:
				embed.description = f"Purging {len(victims)} users from this server."

		self.to_be_banned = victims
		await interaction.response.send_message(embed=embed)

	### LISTENERS ###

	async def video_check(self, message: discord.Message) -> None:
		ids = [744788173128859670, 760569251618226257, 744788229579866162, 821429484674220036, 885719021176119298, 862343886864384010, 749701703938605107, 908104350218469438, 918174846318428200, 877672384872738867, 795469887790252084, 795469805678755850, 795463111561445438]
		if not [role.id for role in message.author.roles if role.id in ids]:
			#pattern = re.compile(r'(http|ftp|https|www):\/\/([\w\-_]+(?:(?:\.[\w\-_]+)+))([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?')

			for item in message.attachments:
				if item.content_type.split("/")[0] == "video":
					await message.delete()
					await message.channel.send("Sorry, no videos allowed \:)")
					return

			#matches = pattern.finditer(message.content)
			exts = ['.mp4', '.mov', '.avi', '.mk4', '.flv', '.wmv', '.m4v', '.webm', '.vob', '.mts', '.ogv', '.3gp']
			if url_search.url(message.content) and any([ext for ext in exts if ext in message.content]):
				await message.delete()
				await message.channel.send("Sorry, no videos allowed \:)")

	async def check_ping(self, message: discord.Message) -> None:
		with open('resources/pinglog.txt', 'a') as log:
			log.write(str(message.author.id)+"\n")
		with open('resources/pinglog.txt', 'r') as log:
			def strip_line(x):
				return x.strip("\n")

			users = list(map(strip_line, log.readlines()))
			if users.count(str(message.author.id)) > 2:
				await message.reply("Please disable the ping on replies! https://tenor.com/view/discord-reply-discord-reply-off-discord-reply-gif-22150762")


	@commands.Cog.listener()
	async def on_thread_create(self, thread: discord.Thread):
		await thread.join()
	
	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload):
		msg = await self.client.get_channel(payload.channel_id).fetch_message(payload.message_id)

		# Check if it's a reaction being added by a human to an embed that a bot sent
		if payload.event_type == "REACTION_ADD" and not payload.member.bot and msg.author.bot and len(msg.embeds) == 1:
			# Stage 1
			if msg.embeds[0].title == "*Only for the most extreme of emergencies!*":
				if payload.member.guild_permissions.administrator:
					if payload.emoji.name == "✅":
						embed = msg.embeds[0]
						embed.title = "Are you *really* sure?"
						embed.set_footer(text="Now, react with 👍 to actually purge.")
						await msg.remove_reaction("✅", payload.member)
						await msg.edit(embed=embed)
				# If a non-Stardust peep tries to purge, ignore
				else:
					await msg.remove_reaction(payload.emoji, payload.member)

			# Stage 2
			elif msg.embeds[0].title == "Are you *really* sure?":
				if payload.member.guild_permissions.administrator:
					if payload.emoji.name == "👍":
						embed = msg.embeds[0]
						
						# Does the main list contain no users?
						if len(self.to_be_banned) == 0:
							embed.title = "An unexpected error has ocurred!"
							embed.set_footer(text="*Action aborted!*")
							return
						
						embed.title = "These members have now been purged!"
						embed.set_footer(text="*Gentlemen, if you are one of the lucky few to remain after this purge... then I applaud you.*")

						guild = self.client.get_guild(payload.guild_id)
						for user in self.to_be_banned:
							await guild.ban(user, reason=f"This user was banned in a Jschlatt purge, prompted by {payload.member.name}!")
						
						await msg.remove_reaction("👍", payload.member)
						await msg.edit(embed=embed)
				# If a non-Stardust peep tries to purge, ignore
				else:
					await msg.remove_reaction(payload.emoji, payload.member)
	
	@commands.Cog.listener()
	async def on_message(self, message: discord.Message):
		if not message.author.bot and not message.author.guild_permissions.administrator:

			# Naughty spammers :3
			if any([word.strip("\n") in message.content.lower() for word in self.naughty]):
				await self.ban_hammer(message)

			# No videos in #general
			if message.channel.id == 771617249910849556:
				await self.video_check(message=message)

			# Ping check
			if 332701537535262720 in message.raw_mentions:
				await self.check_ping(message=message)
	
	@commands.Cog.listener()
	async def on_message_edit(self, _: discord.Message, after: discord.Message):
		if not after.author.bot and not after.author.guild_permissions.administrator:

			# No videos in #general
			if after.channel.id == 771617249910849556:
				await self.video_check(message=after)

async def setup(client):
	await client.add_cog(Moderation(client))