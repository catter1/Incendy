import discord
import logging
import logging.handlers
import os
import json
import asyncio
import asyncpg
from discord import app_commands
from discord.ext import commands
from discord.ext.tasks import loop
from resources import custom_checks as cc

# Get keys
with open('resources/keys.json', 'r') as f:
	keys = json.load(f)

# DB Credentials and Connection object
postgres_pswd = keys["postgres-pswd"]
credentials = {"user": "incendy", "password": postgres_pswd, "database": "incendy", "host": "127.0.0.1"}

# Define Bot Client and Console
client = commands.Bot(command_prefix="!", case_insensitive=True, intents=discord.Intents.all(), db=None)
client.remove_command('help')

# Logging settings
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
logging.getLogger('discord.http').setLevel(logging.INFO)
handler = logging.handlers.RotatingFileHandler(
	filename='logs/incendy.log',
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

# Define COG LIST for later
cog_list = sorted([
	f"{file[:-3]}"
	for file in os.listdir('./cogs')
	if file.endswith('.py')
])

# Start everything up!
async def run():
	try:
		client.db = await asyncpg.connect(**credentials)
		await client.start(keys["dummy-token"])
	except KeyboardInterrupt:
		await client.db.close()
		await client.logout()
		
@client.event
async def setup_hook():
	print('Incendy has woken up! Say good morning!')
	
	for filename in os.listdir('./cogs'):
		if filename.endswith('.py'):
			await client.load_extension(f'cogs.{filename[:-3]}')

	# Command Table
	await client.db.execute('CREATE TABLE IF NOT EXISTS commands(id SERIAL PRIMARY KEY, user_id BIGINT, command_name TEXT, sent_on TIMESTAMPTZ);')
	await client.db.execute('CREATE INDEX IF NOT EXISTS cmd_index ON commands (command_name);')
	
	# FAQ DB
	await client.db.execute('CREATE TABLE IF NOT EXISTS faqs(id SERIAL PRIMARY KEY, user_id BIGINT, faq_name TEXT, sent_on TIMESTAMPTZ);')
	await client.db.execute('CREATE INDEX IF NOT EXISTS faq_index ON faqs (faq_name);')

@client.command()
@cc.is_catter()
async def sync(ctx) -> None:
	synced = await ctx.bot.tree.sync()
	await ctx.send(f"Synced {len(synced)} commands")
	return

cog_group = app_commands.Group(name='cog', description='[ADMIN] Uses the cog management menu')

@cog_group.command(name="load", description="[ADMIN] Loads a cog")
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def load(interaction: discord.Interaction, cog: str):
	try:
		await client.load_extension(cog)
	except Exception as error:
		await interaction.response.send_message("Issue loading cog!", ephemeral=True)
		raise error
	else:
		await interaction.response.send_message("Cog loaded successfully", ephemeral=True)

@cog_group.command(name="unload", description="[ADMIN] Unloads a cog")
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def unload(interaction: discord.Interaction, cog: str):
	try:
		await client.unload_extension(cog)
	except Exception as error:
		await interaction.response.send_message("Issue unloading cog!", ephemeral=True)
		raise error
	else:
		await interaction.response.send_message("Cog unloaded successfully", ephemeral=True)

@cog_group.command(name="reload", description="[ADMIN] Reloads a cog")
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def _reload(interaction: discord.Interaction, cog: str):
	try:
		await client.unload_extension(cog)
		await client.load_extension(cog)
	except Exception as error:
		await interaction.response.send_message("Issue reloading cog!", ephemeral=True)
		raise error
	else:
		await interaction.response.send_message("Cog reloaded successfully", ephemeral=True)


@load.autocomplete('cog')
@unload.autocomplete('cog')
@_reload.autocomplete('cog')
async def autocomplete_callback(interaction: discord.Interaction, current: str):
	coglist = [
		app_commands.Choice(name=cog, value=f"cogs.{cog}")
		for cog in cog_list
		if current.lower() in cog.lower()
	]

	return coglist

client.tree.add_command(cog_group)

@client.event
async def on_command_error(ctx, error):
	raise error

@client.event
async def on_app_command_completion(interaction: discord.Interaction, command: app_commands.Command):
	query = '''INSERT INTO commands(user_id, command_name, sent_on) VALUES(
		$1, $2, $3
	);'''
	
	await client.db.execute(
		query, interaction.user.id, command.name, interaction.created_at
	)

@client.event
async def on_message(message: discord.Message):
	query = '''INSERT INTO test_messages(user_id, message_id, sent_on, message_content) VALUES(
		$1, $2, $3, $4
	);'''

	await client.db.execute(
		query, message.author.id, message.id, message.created_at, message.content
	)

try:
	loop = asyncio.get_event_loop()
	loop.run_until_complete(run())
except KeyboardInterrupt:
	print("Incendy shutting down...")