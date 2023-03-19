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
		logging.info(f'> {self.__cog_name__} cog unloaded')

	@app_commands.command(name="move", description="[ADMIN] Move a channel or thread to a forum thread")
	@app_commands.default_permissions(administrator=True)
	@app_commands.checks.has_permissions(administrator=True)
	@app_commands.describe(
		channel="The channel or thread to transfer over",
		forum="The forum channel to move the channel to"
	)
	async def move(self, interaction: discord.Interaction, channel: discord.TextChannel | discord.Thread, forum: discord.ForumChannel):
		""" /move <channel> <forum> """

		await interaction.response.defer(ephemeral=True)

		new_thread: discord.Thread | discord.TextChannel
		webhook: discord.Webhook

		if isinstance(channel, discord.Thread):
			content = f"This thread used to be <#{channel.id}> as part of <#{channel.parent_id}>, but was transferred to this forum."
		else:
			content = f"This thread used to be <#{channel.id}>, but was transferred to this forum."

		new_thread = getattr(await forum.create_thread(
			content=content,
			name=channel.name
		), "thread")

		webhook = await forum.create_webhook(name="Channel Mover")

		async for message in channel.history(limit=None, oldest_first=True):
			if message.type in [discord.MessageType.default, discord.MessageType.reply, discord.MessageType.thread_starter_message, discord.MessageType.context_menu_command]:
				
				files = [await attachment.to_file(filename=attachment.filename) for attachment in message.attachments if attachment.size < 8000000]

				if (message.content == "" or message.content == None) and len(files) == 0:
					continue
				
				if "Deleted User" in message.author.display_name:
					avatar_url = self.client.user.avatar.url
					username = "Deleted User"
				else:
					avatar_url = message.author.avatar.url if message.author.avatar.url else self.client.user.avatar.url
					username = message.author.display_name
				
				content = "" if message.content in ["", " ", None] else message.content
				if len(content) > 2000:
					content1 = content[:2000]
					content2 = content[2000:]

					await webhook.send(
						content=content1,
						username=username,
						avatar_url=avatar_url,
						tts=False,
						ephemeral=False,
						thread=new_thread
					)
					await webhook.send(
						content=content2,
						files=files,
						username=username,
						avatar_url=avatar_url,
						tts=False,
						ephemeral=False,
						thread=new_thread
					)
				else:
					await webhook.send(
						content=content,
						files=files,
						username=username,
						avatar_url=avatar_url,
						tts=False,
						ephemeral=False,
						thread=new_thread
					)
		
		final_msg = f"This thread has been transferred to <#{new_thread.id}>." if isinstance(channel, discord.Thread) else f"This channel has been transferred to <#{new_thread.id}>."

		await channel.send(final_msg)
		if isinstance(channel, discord.Thread):
			await channel.edit(archived=True, locked=True)
		await webhook.delete()
		
		await interaction.followup.send("Moving complete!", ephemeral=True)

async def setup(client):
	await client.add_cog(Admin(client))