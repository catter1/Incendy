import discord
import os
import json
import requests
from discord import app_commands
from discord.ext import commands
from resources import incendy

class Datapacks(commands.Cog):
	def __init__(self, client: incendy.IncendyBot):
		self.client = client
		self.all_versions = requests.get("https://launchermeta.mojang.com/mc/game/version_manifest.json").json()

	async def cog_load(self):
		print(f' - {self.__cog_name__} cog loaded.')

	async def cog_unload(self):
		print(f' - {self.__cog_name__} cog unloaded.')

	datapack_group = app_commands.Group(name="datapack", description="Various commands for datapack development")

	@datapack_group.command(name="mcmeta", description="Download the latest default Vanilla datapack")
	@app_commands.describe(version="Minecraft version to get datapack for")
	async def mcmeta(self, interaction: discord.Interaction, version: str):
		await interaction.response.defer(thinking=True)

		tag = f"{version}-data-json"
		headers = {'Authorization':f'Bearer {self.client.keys["git-pat"]}', 'Accept':'application/vnd.github+json'}
		resp = requests.get(f"https://api.github.com/repos/misode/mcmeta/zipball/refs/tags/{tag}", headers=headers, stream=True)
		filename = f"{version}_datapack.zip"

		if not resp.status_code == 200:
			await interaction.followup.send("There was an error downloading the datapack!", ephemeral=True)
			return
		with open(f"tmp/{filename}", 'wb') as f:
			for chunk in resp.iter_content(chunk_size=256):
				f.write(chunk)

		embed = discord.Embed(
			title=f"{version}",
			color=discord.Colour.brand_red(),
			description=f"This Vanilla datapack was downloaded from <@149241652391706625>'s **mcmeta** repository."
		)
		file = discord.File(f"tmp/{filename}", filename=filename)
		view = discord.ui.View()
		view.add_item(discord.ui.Button(style=discord.ButtonStyle.link, emoji='<:github:1045336251605188679>', url="https://github.com/misode/mcmeta", label="Mcmeta Repository"))

		await interaction.followup.send(embed=embed, view=view, file=file)
		os.remove(f"tmp/{filename}")

	@mcmeta.autocomplete('version')
	async def autocomplete_callback(self, interaction: discord.Interaction, current: str):
		choices = [
			app_commands.Choice(name="Latest Release", value=self.all_versions["latest"]["release"]),
			app_commands.Choice(name="Latest Snapshot", value=self.all_versions["latest"]["snapshot"])
		]

		choices.extend([
			app_commands.Choice(name=version["id"], value=version["id"])
			for version in self.all_versions["versions"]
			if current.lower() in version["id"].lower()
		][:23])

		return choices

async def setup(client):
	await client.add_cog(Datapacks(client))