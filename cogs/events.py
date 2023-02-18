import discord
import os
import json
from discord import app_commands
from discord.ext import commands
from libraries import incendy

class Events(commands.Cog):
	def __init__(self, client: incendy.IncendyBot):
		self.client = client

	async def cog_load(self):
		print(f' - {self.__cog_name__} cog loaded.')

	async def cog_unload(self):
		print(f' - {self.__cog_name__} cog unloaded.')

	### COMMANDS ###

	@app_commands.command(name="contest", description="Information about the ongoing contest")
	@app_commands.checks.dynamic_cooldown(incendy.long_cd)
	async def contest(self, interaction: discord.Interaction, action: str, submission: discord.Attachment = None):
		""" /contest <action> """

		if not self.client.settings["contest-ongoing"]:
			await interaction.response.send_message("Sorry, but there isn't currently any contest! Check back later for when there is one.")
			return

		if action == "info":
			embed = discord.Embed(
				title="Screenshot Contest",
				color=discord.Colour.brand_red(),
				description="Have a knack for taking screenshots? Submit a Minecraft screenshot of any Stardust Labs project for a chance to win cash prizes! All shaders and texture packs are fair game. Submit the image through Incendy via `/contest submit` - one submission per person. Submissions will be judged by the Stardust Labs team after the submission time has closed.\n\n**Prizes**: 1st - $20, 2nd - $10, 3rd - $5\n**Starts**: <t:1672570800:D>\n**Ends**: <t:1673175600:D>"
			)

			await interaction.response.send_message(embed=embed)

		elif action == "submit":

			# Check if they already made a submission
			for item in os.listdir(f"{os.curdir}/submissions/"):
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
				return

			# Is it too big?
			if submission.size > 10000000:
				await interaction.response.send_message("Your image is too big! Try a smaller one.", ephemeral=True)
				return

			# Add their submission
			await submission.save(f"submissions/{interaction.user.id}.{submission.filename.split('.')[-1]}")
			await interaction.response.send_message("Congrats! Your entry is now successfully submitted. Good luck!")
			
		else:
			
			# Find their submission and remove
			for item in os.listdir(f"{os.curdir}/submissions/"):
				if item.split(".")[0] == str(interaction.user.id):
					os.remove(f"{os.curdir}/submissions/{item}")
					await interaction.response.send_message("Your entry has been removed. If you would like to enter again, feel free by doing `/contest submit`!", ephemeral=True)
					return

			# Hey, you haven't submitted anything!
			await interaction.response.send_message("You don't have a submission yet! Submit one by doing `/contest submit`.", ephemeral=True)

	@contest.autocomplete('action')
	async def autocomplete_callback(self, interaction: discord.Interaction, current: str):
		actions = sorted(["submit", "unsubmit", "info"])
		
		return [
            app_commands.Choice(name=action, value=action)
            for action in actions
            if current.lower() in action.lower()
        ]

	@app_commands.command(name="biome", description="[ADMIN] Displays a biome vote")
	@app_commands.default_permissions(administrator=True)
	@app_commands.checks.has_permissions(administrator=True)
	async def biome(self, interaction: discord.Interaction, roundnum: int, day: int, matchnum: int, biome1: str, biome2: str, foto: discord.Member):
		""" /biome round_number day match_number biome1 biome2 photo_credit """
		
		embed = discord.Embed(color=discord.Colour.dark_teal(), title=f"Round {roundnum}, Day {day}, Match {matchnum}")
		embed.add_field(name=f"🔴 **{biome1}** (Top)   vs.   🟦 **{biome2}** (Bottom)", value="Vote for which one you think is the best biome!")
		embed.set_footer(text=f"{foto} (Photo Credit)", icon_url=foto.avatar)
		file = discord.File(f"assets/{str(roundnum)}.{str(matchnum)}.png", filename="image.png")
		embed.set_image(url="attachment://image.png")
		msg = await interaction.channel.send(file=file, embed=embed)
		await msg.add_reaction("🔴")
		await msg.add_reaction("🟦")

async def setup(client):
	await client.add_cog(Events(client))