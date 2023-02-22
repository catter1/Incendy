import discord
import logging
from discord import app_commands
from discord.ext import commands
from libraries import incendy

class Admin(commands.Cog):
	def __init__(self, client: incendy.IncendyBot):
		self.client = client

	async def cog_load(self):
		logging.info(f'> {self.__cog_name__} cog loaded')

	async def cog_unload(self):
		print(f' - {self.__cog_name__} cog unloaded.')

	@app_commands.command(name="thread", description="[ADMIN] Transfer a channel thread to a forum thread")
	@app_commands.default_permissions(administrator=True)
	@app_commands.checks.has_permissions(administrator=True)
	@app_commands.describe(
		thread="The thread to transfer over and delete",
		forum="The forum channel to move the thread to"
	)
	async def thread(self, interaction: discord.Interaction, thread: discord.Thread, forum: discord.ForumChannel):
		""" /thread <thread> <forum> """

		await interaction.response.defer(ephemeral=True)

		new_thread: discord.Thread
		webhook: discord.Webhook

		new_thread = getattr(await forum.create_thread(
			content=f"This thread used to be <#{thread.id}> as part of <#{thread.parent_id}>, but was transferred to this forum.",
			name=thread.name,
			auto_archive_duration=thread.auto_archive_duration,
			slowmode_delay=thread.slowmode_delay
		), "thread")

		webhook = await forum.create_webhook(name="Thread Mover")

		async for message in thread.history(limit=None, oldest_first=True):
			if message.type in [discord.MessageType.default, discord.MessageType.reply, discord.MessageType.thread_starter_message, discord.MessageType.context_menu_command]:
				await webhook.send(
					content=message.content,
					username=message.author.display_name,
					avatar_url=message.author.avatar.url,
					tts=False,
					ephemeral=False,
					thread=new_thread
				)
		
		await thread.send(f"This thread has been transferred to <#{new_thread.id}>.")
		await thread.edit(archived=True, locked=True)
		await webhook.delete()
		
		await interaction.followup.send("Moving complete!", ephemeral=True)

async def setup(client):
	await client.add_cog(Admin(client))