import discord
import typing
import asyncpg
from mediawiki import MediaWiki
from discord import app_commands
from discord.ext import commands

class IncendyBot(commands.Bot):
	def __init__(self, command_prefix: str = "!", db: asyncpg.pool.Pool = None, miraheze: MediaWiki = None):
		super().__init__(command_prefix=command_prefix, case_insensitive=True, intents=discord.Intents.all())
		self.db = db
		self.miraheze = miraheze

def in_bot_channel():
	"""Interaction is in bot channel"""

	def bot_channel(interaction: discord.Interaction):
		if interaction.channel_id == 871376111857193000 or interaction.channel_id == 923571915879231509:
			return True
		if interaction.user.guild_permissions.administrator:
			return True
		else:
			return False
	return app_commands.check(bot_channel)

def is_catter():
	"""Is catter1"""
	
	def catter(interaction: discord.Interaction):
		if interaction.user.id == 260929689126699008:
			return True
		else:
			return False
	return app_commands.check(catter)

def can_report_bug():
	"""Is Contributor or Dev"""

	def bug_reporter(interaction: discord.Interaction):
		if any([role.id for role in interaction.user.roles if role.id == 749701703938605107 or role.id == 885719021176119298]):
			return True
		if interaction.user.guild_permissions.administrator:
			return True
		else:
			return False
	return app_commands.check(bug_reporter)

def can_close():
	"""Can close current forum thread"""

	def closer(interaction: discord.Interaction):
		if not isinstance(interaction.channel, discord.Thread):
			return False
		if interaction.user.id == interaction.channel.owner_id:
			return True
		elif interaction.user.guild_permissions.administrator:
			return True
		return False
	return app_commands.check(closer)

def default_cd(interaction: discord.Interaction) -> typing.Optional[app_commands.Cooldown]:
	"""2 commands per 25 seconds"""

	if interaction.user.guild_permissions.administrator:
		return None
	if interaction.channel_id == 871376111857193000:
		return None
	return app_commands.Cooldown(2, 25.0)

def short_cd(interaction: discord.Interaction) -> typing.Optional[app_commands.Cooldown]:
	"""1 command per 15 seconds"""

	if interaction.user.guild_permissions.administrator:
		return None
	if interaction.channel_id == 871376111857193000:
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