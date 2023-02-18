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

class Clock:
	def __init__(self, client: incendy.IncendyBot):
		self.client = client
		self.endtime: typing.Optional[datetime.datetime] = None # Our current closest endtime
		self.id: typing.Optional[int] = None # The id of our reminder in the database
		self._task: typing.Optional[asyncio.Task] = None # The task that is currently running
		self.client.loop.create_task(self.update()) # Telling our code to update
		
	async def get_closest_reminder(self) -> asyncpg.Record:
		return await self.client.db.fetchrow(
            '''SELECT * FROM reminders ORDER BY endtime DESC LIMIT 3'''
        )
		
	async def create(self, 
	            reminder: str, 
		     	channel_id: int,
	            user_id: int, 
	            endtime: datetime.datetime
		) -> int:
		
		query = '''INSERT INTO reminders (channel_id, user_id, reminder, endtime) VALUES(
            $1, $2, $3, $4
        ) RETURNING id'''
		
		id = await self.client.db.fetchval(
            query, channel_id, user_id, reminder, endtime
        ) # Our query, inserting into the database and getting the id
		if (not self._task or self._task.done()) or endtime < self.endtime: # if the timer ends sooner then the current scheduled one
			if self._task and not self._task.done(): # if the task exists
				self._task.cancel() # cancel it
			reminder = await self.get_closest_reminder()
			self._task = self.client.loop.create_task(
				self.end_timer(reminder)
			)
			self.endtime = endtime
			self.id = id
		return id # just return the id we want

	async def update(self):
		await self.client.db.execute(
			'''CREATE TABLE IF NOT EXISTS reminders(id SERIAL PRIMARY KEY, channel_id BIGINT, user_id BIGINT, reminder TEXT, endtime TIMESTAMP);'''
		)

		reminder = await self.get_closest_reminder()
		if not reminder:
			return
		if not self._task or self._task.done(): # if the task is done or no task exists we just create the task
			self._task = self.client.loop.create_task(
				self.end_timer(reminder)
            )
			self.endtime = reminder["endtime"] # store the endtime
			self.id = reminder["id"] # store the id
			return
		
		if reminder["endtime"] < self.endtime: # Otherwise, if the reminder ends sooner then the current closest endtime
			self._task.cancel() # cancel the task
			self._task = self.client.loop.create_task(
				self.end_timer(reminder)
			)
			self.endtime = reminder["endtime"] # store the endtime
			self.id = reminder["id"] # store the id

	async def end_timer(self, reminder: asyncpg.Record):
		await discord.utils.sleep_until(reminder["endtime"]) # sleeping until the endtime

		remind_channel = self.client.get_channel(reminder["channel_id"])
		embed = discord.Embed(title="Reminder", colour=discord.Colour.brand_red(), description=reminder["reminder"])
		await remind_channel.send(f"Hey <@{reminder['user_id']}>!", embed=embed)
		
		await self.client.db.execute("DELETE FROM reminders WHERE id = $1", reminder["id"]) # remove from database
		
		self.client.loop.create_task(self.update()) # re update
	
	def stop(self):
		self._task.cancel()

class Remind(commands.Cog):
	def __init__(self, client: incendy.IncendyBot):
		self.client = client
		self.clock = Clock(client)

	async def cog_load(self):
		logging.info(f'> {self.__cog_name__} cog loaded')

	async def cog_unload(self):
		self.clock.db.close()
		print(f' - {self.__cog_name__} cog unloaded.')

	### COMMANDS ###
	@app_commands.command(name="remindme", description="Set a reminder up for later")
	@app_commands.checks.dynamic_cooldown(incendy.long_cd)
	@app_commands.describe(
    	time="Time ending in s, m, h, or d - for seconds, minutes, hours, or days, respectively. Example: 10h",
    	reminder="What do you need reminded?"
	)
	async def remindme(self, interaction: discord.Interaction, time: str, reminder: str): # i'll leave it to you to make the time converters
		""" /remindme [time] [reason] """
		
		def check_end(x):
			return time.endswith(x)
		
		if not any(map(check_end, ['s', 'm', 'h', 'd'])):
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
		endtime = now + time_dict[unit]
		
		id = await self.clock.create(
            reminder= reminder,
			channel_id= interaction.channel_id,
			user_id= interaction.user.id,
			endtime= endtime
        )

		await interaction.response.send_message(f"Reminder successfully created! I will ping you in {time} with your reminder.")

async def setup(client):
	await client.add_cog(Remind(client))