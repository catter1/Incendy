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
from mediawiki import MediaWiki
from libraries import incendy

# Get keys
with open('resources/keys.json', 'r') as f:
	keys = json.load(f)

with open('resources/settings.json', 'r') as f:
	settings = json.load(f)

# DB Credentials and Connection object
postgres_pswd = keys["postgres-pswd"]
credentials = {"user": "incendy", "password": postgres_pswd, "database": "incendy", "host": "127.0.0.1"}

# Define Bot Client and Console
client = incendy.IncendyBot()
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
	def get_env() -> dict:
		environment = {}
		env_token = os.environ.get("INCENDY_BOT_TOKEN")
		environment["INCENDY_BOT_TOKEN"] = (env_token if env_token else "incendy-token")
		environment["INCENDY_WIKI_UPDATE_ENABLED"] = (bool(int(os.environ.get("INCENDY_WIKI_UPDATE_ENABLED"))) if os.environ.get("INCENDY_WIKI_UPDATE_ENABLED") else False)
		environment["INCENDY_STATS_UPDATE_ENABLED"] = (bool(int(os.environ.get("INCENDY_STATS_UPDATE_ENABLED"))) if os.environ.get("INCENDY_STATS_UPDATE_ENABLED") else False)

		return environment
	
	try:
		client.settings = settings
		client.keys = keys
		client.environment = get_env()

		try:
			client.db = await asyncpg.create_pool(**credentials)
			client.miraheze = MediaWiki(
				url="https://stardustlabs.miraheze.org/w/api.php",
				user_agent=keys["wiki-user-agent"]
			)
		except TimeoutError as e:
			logging.error("Could not log into the Miraheze Wiki via pymediawiki!")
			raise e

		logging.info(f"Booting with token {client.environment['INCENDY_BOT_TOKEN']}")
		await client.start(keys[client.environment["INCENDY_BOT_TOKEN"]])
	except KeyboardInterrupt:
		await client.db.close()
		await client.logout()

async def file_init():
	if not os.path.isdir("logs"):
		os.mkdir("logs")

	if not os.path.isdir("tmp"):
		os.mkdir("tmp")

	if not os.path.isfile("resources/keys.json"):
		keys_base = {"incendy-token": "","dummy-token": "","dbbot-token": "","twitch-id": "","twitch-secret": "","youtube-key": "","spotify-id": "","spotify-secret": "","pastebin-key": "","postgres-pswd": "","git-pat": "","cf-key": "","wiki-user-agent": "","wiki-username": "","wiki-password": ""}
		with open("resources/keys.json", 'w') as f:
			json.dump(keys_base, f, indent=4)
	
	if not os.path.isfile("resources/naughty.txt"):
		with open("resources/naughty.txt", 'w') as f:
			f.write()
	
	if not os.path.isfile("resources/pinglog.txt"):
		with open("resources/pinglog.txt", 'w') as f:
			f.write()

	if not os.path.isfile("resources/settings.json"):
		settings_base = {"locked": False,"contest-ongoing": False,"version": "","stardust-guild-id": None}
		with open("resources/settings.json", 'w') as f:
			json.dump(settings_base, f, indent=4)

	if not os.path.isfile("resources/timeout.json"):
		timeout_base = {"days": [],"members": {}}
		with open("resources/timeout.json", 'w') as f:
			json.dump(timeout_base, f, indent=4)

async def table_init():
	# Messages Table
	await client.db.execute('CREATE TABLE IF NOT EXISTS messages(id SERIAL PRIMARY KEY, user_id BIGINT, message_id BIGINT, sent_on TIMESTAMPTZ, message_content TEXT);')
	await client.db.execute('CREATE INDEX IF NOT EXISTS user_index ON messages (user_id);')

	# Command Table
	await client.db.execute('CREATE TABLE IF NOT EXISTS commands(id SERIAL PRIMARY KEY, user_id BIGINT, command_name TEXT, sent_on TIMESTAMPTZ);')
	await client.db.execute('CREATE INDEX IF NOT EXISTS cmd_index ON commands (command_name);')
	
	# FAQ Table
	await client.db.execute('CREATE TABLE IF NOT EXISTS faqs(id SERIAL PRIMARY KEY, user_id BIGINT, faq_name TEXT, sent_on TIMESTAMPTZ);')
	await client.db.execute('CREATE INDEX IF NOT EXISTS faq_index ON faqs (faq_name);')

	# Downloads Table
	await client.db.execute('CREATE TABLE IF NOT EXISTS downloads(id SERIAL PRIMARY KEY, day DATE, terralith INT, incendium INT, nullscape INT, structory INT, towers INT, continents INT, amplified INT);')
	await client.db.execute('CREATE INDEX IF NOT EXISTS day_index ON downloads (day);')

	# Wiki Table
	await client.db.execute('CREATE TABLE IF NOT EXISTS wiki(id SERIAL PRIMARY KEY, pageid INT, title TEXT, description TEXT, pageurl TEXT, imgurl TEXT, pagedata JSON);')
	await client.db.execute('CREATE INDEX IF NOT EXISTS title_index ON wiki (title);')

	# Stardusttv Table
	await client.db.execute('CREATE TABLE IF NOT EXISTS stardusttv(id SERIAL PRIMARY KEY, media TEXT, slug TEXT);')
	await client.db.execute('CREATE INDEX IF NOT EXISTS slug_index ON stardusttv (slug);')
		
@client.event
async def setup_hook():
	await file_init()
	await table_init()

	# Load cogs
	for filename in os.listdir('./cogs'):
		if filename.endswith('.py'):
			await client.load_extension(f'cogs.{filename[:-3]}')
		
	# All set!
	print('Incendy has woken up, ready for an amazing day! Say good morning!')

@client.command(name="sync")
@incendy.is_catter()
async def sync(ctx: commands.context.Context):
	synced = await client.tree.sync()
	await ctx.send(f"Synced {len(synced)} commands")

cog_group = app_commands.Group(name='cog', description='[ADMIN] Uses the cog management menu', default_permissions=discord.permissions.Permissions.all())

@cog_group.command(name="load", description="[ADMIN] Loads a cog")
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def load(interaction: discord.Interaction, cog: str):
	await interaction.response.defer(thinking=True, ephemeral=True)
	try:
		await client.load_extension(cog)
	except Exception as error:
		await interaction.followup.send("Issue loading cog!", ephemeral=True)
		raise error
	else:
		await interaction.followup.send("Cog loaded successfully", ephemeral=True)

@cog_group.command(name="unload", description="[ADMIN] Unloads a cog")
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def unload(interaction: discord.Interaction, cog: str):
	await interaction.response.defer(thinking=True, ephemeral=True)
	try:
		await client.unload_extension(cog)
	except Exception as error:
		await interaction.followup.send("Issue unloading cog!", ephemeral=True)
		raise error
	else:
		await interaction.followup.send("Cog unloaded successfully", ephemeral=True)

@cog_group.command(name="reload", description="[ADMIN] Reloads a cog")
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def _reload(interaction: discord.Interaction, cog: str):
	await interaction.response.defer(thinking=True, ephemeral=True)
	try:
		await client.unload_extension(cog)
		await client.load_extension(cog)
	except Exception as error:
		await interaction.followup.send("Issue reloading cog!", ephemeral=True)
		raise error
	else:
		await interaction.followup.send("Cog reloaded successfully", ephemeral=True)


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
	if interaction.guild.id == settings["stardust-guild-id"]:
		query = '''INSERT INTO commands(user_id, command_name, sent_on) VALUES(
			$1, $2, $3
		);'''
		
		await client.db.execute(query, interaction.user.id, command.name, interaction.created_at)

@client.listen('on_message')
async def on_message(message: discord.Message):
	try:
		if message.guild.id == settings["stardust-guild-id"]:
			query = '''INSERT INTO messages(user_id, message_id, sent_on, message_content) VALUES(
				$1, $2, $3, $4
			);'''

			await client.db.execute(query, message.author.id, message.id, message.created_at, message.content)
	except AttributeError as e:
		logger.log(3, e)
		logger.log(3, f"Message content: {message.content}")
		logger.log(3, f"Message author: {message.author}")

@client.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
	command = interaction.command.name
	if isinstance(error, app_commands.CommandOnCooldown):
		if command == "Translate to English":
			await interaction.response.send_message("Yikes! " + str(error) + ". We don't want to overwhelm the API servers...", ephemeral=True)
		elif command in ["feedback", "reportad", "remindme", "apply"]:
			await interaction.response.send_message("Yikes! " + str(error), ephemeral=True)
		else:
			await interaction.response.send_message("Yikes! " + str(error) + ". If you want to keep using without a cooldown, head to <#923571915879231509>!", ephemeral=True)
	elif isinstance(error, app_commands.CheckFailure):
		if command in ["stats", "incendy", "changelog"]:
			await interaction.response.send_message("This command can only be used in a bot command channel like <#923571915879231509>.", ephemeral=True)
		elif command in ["bug", "upload"]:
			await interaction.response.send_message("This command is only available for Contributors!", ephemeral=True)
		elif command == "close":
			await interaction.response.send_message("This command can only be executed in a support thread! You also must be the creator of the thread.", ephemeral=True)
		else:
			await interaction.response.send_message("You are not allowed to perform this command!", ephemeral=True)
	else:
		raise error

try:
	loop = asyncio.new_event_loop()
	loop.run_until_complete(run())
except KeyboardInterrupt:
	logging.info("Incendy shutting down...")