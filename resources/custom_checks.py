import discord
from discord import app_commands
import typing

def in_bot_channel():
	def bot_channel(interaction: discord.Interaction):
		if interaction.channel_id == 871376111857193000 or interaction.channel_id == 923571915879231509:
			return True
		if interaction.user.guild_permissions.administrator:
			return True
		else:
			return False
	return app_commands.check(bot_channel)

def is_catter():
	def catter(interaction: discord.Interaction):
		if interaction.user.id == 260929689126699008:
			return True
		else:
			return False
	return app_commands.check(catter)

def can_report_bug():
	def bug_reporter(interaction: discord.Interaction):
		if any([role.id for role in interaction.user.roles if role.id == 749701703938605107 or role.id == 885719021176119298]):
			return True
		if interaction.user.guild_permissions.administrator:
			return True
		else:
			return False
	return app_commands.check(bug_reporter)

def can_close():
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
	if interaction.user.guild_permissions.administrator:
		return None
	if interaction.channel_id == 871376111857193000:
		return None
	return app_commands.Cooldown(2, 25.0)

def short_cd(interaction: discord.Interaction) -> typing.Optional[app_commands.Cooldown]:
	if interaction.user.guild_permissions.administrator:
		return None
	if interaction.channel_id == 871376111857193000:
		return None
	return app_commands.Cooldown(1, 15.0)

def long_cd(interaction: discord.Interaction) -> typing.Optional[app_commands.Cooldown]:
	if interaction.user.guild_permissions.administrator:
		return None
	return app_commands.Cooldown(1, 35.0)

def super_long_cd(interaction: discord.Interaction) -> typing.Optional[app_commands.Cooldown]:
	if interaction.user.guild_permissions.administrator:
		return None
	return app_commands.Cooldown(1, 6000.0)