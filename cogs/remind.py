import discord
import datetime 
import asyncpg
import asyncio
import typing
import logging
from discord import app_commands
from discord.ext import commands
from libraries import incendy

# Tons of thanks to pikaninja! https://gist.github.com/pikaninja/d9ab2a91cb3344c62b3d13a435255154

class Remind(commands.Cog):
	def __init__(self, client: incendy.IncendyBot):
		self.client = client
		self.endtime: typing.Optional[datetime.datetime] = None # Soonest endtime
		self._task: typing.Optional[asyncio.Task] = None # Current task
		self.client.loop.create_task(self.update()) # Get latest task

	async def cog_load(self):
		logging.info(f'> {self.__cog_name__} cog loaded')

	async def cog_unload(self):
		logging.info(f'> {self.__cog_name__} cog unloaded')


	### HELPER FUNCTIONS ###

	async def get_closest_reminder(self) -> asyncpg.Record:
		return await self.client.db.fetchrow(
            '''SELECT * FROM reminders ORDER BY endtime ASC LIMIT 1'''
        )
	
	async def create(self, reminder: str, channel_id: int, user_id: int, endtime: datetime.datetime ) -> int:
		
		query = '''INSERT INTO reminders (channel_id, user_id, reminder, endtime) VALUES(
            $1, $2, $3, $4
        ) RETURNING id'''
		
		# Submit reminder into DB
		_id = await self.client.db.fetchval(query, channel_id, user_id, reminder, endtime)
		
		# Update the most recent reminder
		self.client.loop.create_task(self.update())

		return _id
	
	async def update(self):
		# Get latest reminder; return if non-existant
		reminder = await self.get_closest_reminder()
		if not reminder:
			return
		
		# If no task exists or is running, create a new task and make it the soonest
		if not self._task or self._task.done():
			self._task = self.client.loop.create_task(
				self.end_timer(reminder)
            )
			self.endtime = reminder["endtime"]
			return
		
		# If a task exists, only create the task if this reminder ends sooner than the first one
		if reminder["endtime"] < self.endtime:
			# Cancel task and replace
			self._task.cancel()
			self._task = self.client.loop.create_task(
				self.end_timer(reminder)
			)
			self.endtime = reminder["endtime"]
	
	async def end_timer(self, reminder: asyncpg.Record):
		# Sleep until reminder is ready
		await discord.utils.sleep_until(reminder["endtime"])

		# Init reminder message
		remind_channel = self.client.get_channel(reminder["channel_id"])
		embed = discord.Embed(title="Reminder", colour=discord.Colour.brand_red(), description=reminder["reminder"])
		await remind_channel.send(f"Hey <@{reminder['user_id']}>!", embed=embed)
		
		# Clean up
		await self.client.db.execute("DELETE FROM reminders WHERE id = $1", reminder["id"]) # remove from database
		
		self.client.loop.create_task(self.update())
	

	### COMMANDS ###

	@app_commands.command(name="remindme", description="Set a reminder up for later")
	@app_commands.checks.dynamic_cooldown(incendy.long_cd)
	@app_commands.describe(
    	time="Time ending in s, m, h, or d - for seconds, minutes, hours, or days, respectively. Example: 10h",
    	reminder="What do you need reminded?"
	)
	async def remindme(self, interaction: discord.Interaction, time: str, reminder: str):
		""" /remindme [time] [reminder] """
		
		if not any(map(lambda x: time.endswith(x), ['s', 'm', 'h', 'd'])):
			await interaction.response.send_message("Your time needs to end in `s`, `m`, `h`, or `d` - for seconds, minutes, hours, or days, respectively. For example, if you wanted to be reminded in 45 minutes, do `45m`.", ephemeral=True)
			return
		if not time[:-1].isnumeric():
			await interaction.response.send_message("You need a valid number for your time! The only letter allowed is the last character, to determine seconds, minutes, hours, or days.", ephemeral=True)
			return

		time = time.replace(" ", "")
		amount = float(time[:-1])
		now = datetime.datetime.now()
		unit = time[-1:]
		time_dict = {
			's': datetime.timedelta(seconds=amount),
			'm': datetime.timedelta(minutes=amount),
			'h': datetime.timedelta(hours=amount),
			'd': datetime.timedelta(days=amount)
		}
		limit_dict = {
			's': amount,
			'm': amount * 60,
			'h': amount * 60 * 60,
			'd': amount * 60 * 60 * 24
		}
		endtime = now + time_dict[unit]

		if limit_dict[unit] > 31536000:
			await interaction.response.send_message(f"Hey, {time} is too far away! Try keeping it under a year.", ephemeral=True)
			return
		
		reminder_id = await self.create(
            reminder= reminder,
			channel_id= interaction.channel_id,
			user_id= interaction.user.id,
			endtime= endtime
        )

		if not reminder_id:
			await interaction.response.send_message("There was an issue creating your reminder!", ephemeral=True)
			return

		await interaction.response.send_message(f"Reminder successfully created! I will ping you in {time} with your reminder.")
	

async def setup(client):
	await client.add_cog(Remind(client))