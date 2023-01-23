import discord
import asyncpg
import asyncio
import logging
import logging.handlers
import json
from discord.ext import commands
from resources import incendy

# Get keys
with open('resources/keys.json', 'r') as f:
	keys = json.load(f)

# DB Credentials and Connection object
postgres_pswd = keys["postgres-pswd"]
credentials = {"user": "incendy", "password": postgres_pswd, "database": "incendy", "host": "127.0.0.1"}

# Define Bot Client and Console
client = incendy.IncendyBot(command_prefix="?")
client.remove_command('help')

# Logging settings
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
logging.getLogger('discord.http').setLevel(logging.INFO)
handler = logging.handlers.RotatingFileHandler(
	filename='logs/db_bot.log',
	encoding='utf-8',
	maxBytes=32 * 1024 * 1024,  # 32 MiB
	backupCount=5,
)
dt_fmt = '%d-%m-%Y %H:%M:%S'
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Discord big doo doo butt >:(
discord.utils.setup_logging(handler=handler, formatter=formatter, level=logging.INFO, root=True)

async def run():
	try:
		client.db = await asyncpg.connect(**credentials)
		await client.start(keys["dbbot-token"])
	except KeyboardInterrupt:
		await client.db.close()
		await client.logout()

@client.event
async def setup_hook():
	print('DB Bot has woken up! Say good morning!')
	client.status = discord.Status.offline
	
@client.command(name="database")
@incendy.is_catter()
async def database(ctx: commands.context.Context) -> None:
	await ctx.send("Starting...")
	await client.db.execute('CREATE TABLE IF NOT EXISTS messages(id SERIAL PRIMARY KEY, user_id BIGINT, message_id BIGINT, sent_on TIMESTAMPTZ, message_content TEXT);')

	# Get all channels
	channels = []
	channels.extend([channel for channel in ctx.guild.text_channels])
	channels.extend([thread for thread in ctx.guild.threads])
	for channel in ctx.guild.text_channels:
		async for a_t in channel.archived_threads(limit=None):
			channels.append(a_t)
	for forum in ctx.guild.forums:
		async for a_t in forum.archived_threads(limit=None):
			channels.append(a_t)

	# Sort through messages
	for channel in channels:
		print(f'Starting {channel.name}...')
		async for message in channel.history(limit=None, oldest_first=True):
			if message.type == discord.MessageType.default or message.type == discord.MessageType.reply:
				query = '''INSERT INTO messages(user_id, message_id, sent_on, message_content) VALUES(
					$1, $2, $3, $4
				)'''
				
				await client.db.execute(
					query, message.author.id, message.id, message.created_at, message.content
				)
		print(f'Finished {channel.name}!')

	# Create Index
	print("Finished all channels! Creating index...")
	await client.db.execute('CREATE INDEX IF NOT EXISTS user_index ON messages (user_id);')

	print("Finished operation! Somehow...")
	
try:
	loop = asyncio.get_event_loop()
	loop.run_until_complete(run())
except KeyboardInterrupt:
	print("DB Bot shutting down...")
