import discord
import os
import json
import typing
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import has_permissions

class Events(commands.Cog):
	def __init__(self, client):
		self.client = client

	async def cog_load(self):
		print(f' - {self.__cog_name__} cog loaded.')

	async def cog_unload(self):
		print(f' - {self.__cog_name__} cog unloaded.')

	### COOLDOWNS & CHECKS ###
	
	def in_bot_channel():
		def bot_channel(interaction: discord.Interaction):
			if interaction.channel_id == 871376111857193000 or interaction.channel_id == 923571915879231509:
				return True
			if interaction.user.guild_permissions.administrator:
				return True
			else:
				return False
		return app_commands.check(bot_channel)
	
	def long_cd(interaction: discord.Interaction) -> typing.Optional[app_commands.Cooldown]:
		if interaction.user.guild_permissions.administrator:
			return None
		return app_commands.Cooldown(1, 35.0)

	@app_commands.command(name="contest", description="Information about the ongoing contest")
	@app_commands.checks.dynamic_cooldown(long_cd)
	async def contest(self, interaction: discord.Interaction, action: str, submission: discord.Attachment = None):

		with open("resources/settings.json") as f:
			settings = json.load(f)
			if not settings["contest-ongoing"]:
				await interaction.response.send_message("Sorry, but there isn't currently any contest! Check back later for when there is one.")
				return

		if action == "submit":

			# Check if they already made a submission
			for item in os.listdir(f"{os.curdir()}/submissions/"):
				if item.split(".")[0] == str(interaction.user.id):
					await interaction.response.send_message("You have already uploaded a submission! If you would like to change your submission, do `/contest unsubmit`, then try again.", ephemeral=True)
					return
			
			# Did they attach an image?
			if not submission:
				await interaction.response.send_message("You must upload an image with your submission!", ephemeral=True)
				return

			# Is it *actually* an image?
			if not submission.content_type.split("/")[0] == "image":
				await interaction.response.send_message("Your submission must be an actual image!", ephemeral=True)

			# Add their submission
			await submission.save(f"submissions/{interaction.user.id}.{submission.filename.split('.')[-1]}")
			await interaction.response.send_message("Congrats! Your entry is now successfully submitted. Good luck!")
			
		else:
			
			# Find their submission and remove
			for item in os.listdir(f"{os.curdir()}/submissions/"):
				if item.split(".")[0] == str(interaction.user.id):
					os.remove(f"{os.curdir()}/submissions/{item}")
					await interaction.response.send_message("Your entry has been removed. If you would like to enter again, feel free by doing `/contest submit`!", ephemeral=True)
					return

			# Hey, you haven't submitted anything!
			await interaction.response.send_message("You don't have a submission yet! Submit one by doing `/contest submit`.", ephemeral=True)

	@contest.autocomplete('action')
	async def autocomplete_callback(self, interaction: discord.Interaction, current: str):
		actions = sorted(["submit", "unsubmit"])
		
		return [
            app_commands.Choice(name=action, value=action)
            for action in actions
            if current.lower() in action.lower()
        ]

	@app_commands.command(name="biome", description="Displays a biome vote")
	@app_commands.default_permissions(administrator=True)
	@app_commands.checks.has_permissions(administrator=True)
	async def biome(self, interaction: discord.Interaction, roundnum: int, day: int, matchnum: int, biome1: str, biome2: str, foto: discord.Member):
		""" /biome round_number day match_number biome1 biome2 photo_credit """
		
		embed = discord.Embed(color=discord.Colour.dark_teal(), title=f"Round {roundnum}, Day {day}, Match {matchnum}")
		embed.add_field(name=f"🔴 **{biome1}** (Top)   vs.   🟦 **{biome2}** (Bottom)", value="Vote for which one you think is the best biome!")
		embed.set_footer(text=f"{foto} (Photo Credit)", icon_url=foto.avatar)
		file = discord.File(f"images/{str(roundnum)}.{str(matchnum)}.png", filename="image.png")
		embed.set_image(url="attachment://image.png")
		msg = await interaction.channel.send(file=file, embed=embed)
		await msg.add_reaction("🔴")
		await msg.add_reaction("🟦")

async def setup(client):
	await client.add_cog(Events(client))