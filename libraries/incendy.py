import discord
import typing
import asyncpg
import requests
from mediawiki import MediaWiki
from discord import app_commands
from discord.ext import commands
import libraries.constants as Constants

class IncendyBot(commands.Bot):
	def __init__(self, command_prefix: str = "!", db: asyncpg.pool.Pool = None, miraheze: MediaWiki = None, wiki_session: requests.Session = None, keys: dict = None, settings: dict = None, environment: dict = None):
		super().__init__(command_prefix=command_prefix, case_insensitive=True, intents=discord.Intents.all())
		self.db = db
		self.miraheze = miraheze
		self.wiki_session = wiki_session
		self.keys = keys
		self.settings = settings
		self.environment = environment

class NotInBotChannel(app_commands.CheckFailure):
	pass

class CantCloseThread(app_commands.CheckFailure):
	pass

def in_bot_channel():
	"""Interaction is in bot channel"""

	def bot_channel(interaction: discord.Interaction):
		if interaction.channel_id == Constants.Channel.BOT:
			return True
		if interaction.user.guild_permissions.administrator:
			return True
		else:
			raise NotInBotChannel(f"You must be in <#{Constants.Channel.BOT}> to use this command!")
	return app_commands.check(bot_channel)

def is_catter():
	"""Is catter1"""
	
	def catter(interaction: discord.Interaction):
		if interaction.user.id == Constants.User.CATTER:
			return True
		else:
			return app_commands.MissingPermissions("Only catter is allowed to use this command!")
	return app_commands.check(catter)

def can_upload_projects():
	"""Is a project uploader"""
	
	def project_uploader(interaction: discord.Interaction):
		if interaction.user.id in [Constants.User.STARMUTE, Constants.User.CATTER, Constants.User.TERA, Constants.User.KUMA]:
			return True
		else:
			return app_commands.MissingPermissions("You must have VERY special permissions for this command!")
	return app_commands.check(project_uploader)

def can_report_bug():
	"""Is Contributor or Dev"""

	def bug_reporter(interaction: discord.Interaction):
		if any([role.id for role in interaction.user.roles if role.id in [Constants.Role.CONTRIBUTOR, Constants.Role.DEV_TEAM]]):
			return True
		if interaction.user.guild_permissions.administrator:
			return True
		else:
			return app_commands.MissingPermissions("You must be a Contributor or Dev Team member to use this command!")
	return app_commands.check(bug_reporter)

def can_edit_wiki():
	"""Is Wiki Contributor, Photographer, or higher"""

	def wiki_editor(interaction: discord.Interaction):
		ids = [Constants.Role.WIKI_CONTRIBUTOR] + [Constants.Role.CONTRIBUTOR] + [Constants.Role.WIKI_CEO] + Constants.Role.ALL_ADMINISTRATION + [Constants.Role.DEV_TEAM] + [Constants.Role.PHOTOGRAPHER]
		if any([role.id for role in interaction.user.roles if role.id in ids]):
			return True
		else:
			return app_commands.MissingPermissions("You must be a Photographer, Wiki Contributor, or another higher role to use this command!")
	return app_commands.check(wiki_editor)

def can_close():
	"""Can close current forum thread"""

	def closer(interaction: discord.Interaction):
		if not isinstance(interaction.channel, discord.Thread):
			return CantCloseThread("This command can only be used in Threads!")
		if interaction.user.id == interaction.channel.owner_id:
			return True
		elif interaction.user.guild_permissions.administrator:
			return True
		return CantCloseThread("You must either be the owner of the thread, or a Contributor/staff member to close this thread.")
	return app_commands.check(closer)

def default_cd(interaction: discord.Interaction) -> typing.Optional[app_commands.Cooldown]:
	"""2 commands per 25 seconds"""

	if interaction.user.guild_permissions.administrator:
		return None
	if interaction.channel_id == Constants.Channel.BOT:
		return None
	return app_commands.Cooldown(2, 25.0)

def short_cd(interaction: discord.Interaction) -> typing.Optional[app_commands.Cooldown]:
	"""1 command per 15 seconds"""

	if interaction.user.guild_permissions.administrator:
		return None
	if interaction.channel_id == Constants.Channel.BOT:
		return None
	return app_commands.Cooldown(1, 15.0)

def long_cd(interaction: discord.Interaction) -> typing.Optional[app_commands.Cooldown]:
	"""1 command per 35 seconds"""

	if interaction.user.guild_permissions.administrator:
		return None
	return app_commands.Cooldown(1, 35.0)

def very_long_cd(interaction: discord.Interaction) -> typing.Optional[app_commands.Cooldown]:
	"""1 command per 2 minutes"""

	if interaction.user.guild_permissions.administrator:
		return None
	return app_commands.Cooldown(1, 120.0)

def super_long_cd(interaction: discord.Interaction) -> typing.Optional[app_commands.Cooldown]:
	"""1 command per 100 minutes"""
	if interaction.user.guild_permissions.administrator:
		return None
	return app_commands.Cooldown(1, 6000.0)