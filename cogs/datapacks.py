import discord
import os
import json
import requests
from mecha.api import Mecha
from mecha.contrib.statistics import Analyzer, Summary
from beet.library.data_pack import DataPack
from beet.contrib.json_log import JsonLogHandler
from discord import app_commands
from discord.ext import commands
from libraries import incendy

class Datapacks(commands.Cog):
	def __init__(self, client: incendy.IncendyBot):
		self.client = client
		self.all_versions = requests.get("https://launchermeta.mojang.com/mc/game/version_manifest.json").json()

	async def cog_load(self):
		print(f' - {self.__cog_name__} cog loaded.')

	async def cog_unload(self):
		print(f' - {self.__cog_name__} cog unloaded.')

	datapack_group = app_commands.Group(name="datapack", description="Various commands for datapack development")

	@datapack_group.command(name="analyze", description="Analyze and validate your datapackto see its stats and errors")
	@app_commands.describe(datapack="Attach your datapack ZIP here")
	async def analyze(self, interaction: discord.Interaction, version: str, datapack: discord.Attachment):
		if datapack.content_type != "application/zip":
			await interaction.response.send_message("Your attachment is not a valid datapack! It **must** be a zip file (not rar)!", ephemeral=True)
			return
		
		await interaction.response.defer(thinking=True)
		
		filename = f"{interaction.user.name}_datapack.zip"
		await datapack.save(f"tmp/{filename}")

		pack = DataPack(zipfile=f"tmp/{filename}")

		json_log_handler = JsonLogHandler()
		with json_log_handler.activate():
			mc = Mecha(version=version)
			analyzer = Analyzer(mc)
			mc.compile(pack, report=mc.diagnostics)
			mc.log_reported_diagnostics()

		errors = json_log_handler.entries
		error1 = errors[0].dict() if len(errors) > 0 else ''
		colour = (discord.Colour.green() if len(errors) == 0 else discord.Colour.red())
		stats = analyzer.stats.dict()
		nl = '\n'

		headers = {'Content-Type': 'application/x-www-form-urlencoded'}
		url = "https://api.mclo.gs/1/log"
		data = {"content": f"{Summary(mc.spec, analyzer.stats)}"}
		x = requests.post(url, data=data, headers=headers)
		logurl = json.loads(x.text)["url"]

		embed = discord.Embed(
			title=f"{datapack.filename[:-4]} Analysis",
			color=colour,
			description=f"""
			[Full Function Breakdown]({logurl})
			📁 **Total Functions**: {stats.get('function_count')}
			<:cmdblk:1073005612285308958> **Commands**: {sum([stats['command_count'][item][key] for item in stats['command_count'].keys() for key in stats['command_count'][item].keys()])}
			{nl.join([f'...🔹 __{cmd}__: {cnt}' for cmd, cnt in sorted(((item, sum(key for key in stats['command_count'][item].values())) for item in stats['command_count'].keys()), reverse=True, key=lambda item: item[1])[:5]])}
			
			<:i_blazing:1026201263509086228> **Execute Commands**: {stats.get('execute_count')}
			{'...execute **:** ' + ', '.join([f'__{cmd}__ ({cnt})' for cmd, cnt in sorted(stats['command_behind_execute_count'].items(), reverse=True, key=lambda item: item[1])[:3]]) if len(stats['command_behind_execute_count'].keys()) != 0 else ''}
			👉 **Selectors**: {', '.join([f'{cnt} **@{sel}**' for sel, cnt in ((item, stats['selector_count'][item]) for item in stats['selector_count'].keys())]) if len(stats['selector_count'].keys()) != 0 else 0}
			🥅 **Top Scoreboards**: {', '.join([f'__{sb}__ ({cnt})' for sb, cnt in sorted(stats['scoreboard_references'].items(), reverse=True, key=lambda item: item[1])[:3]]) if len(stats['scoreboard_references'].keys()) != 0 else 0}

			{'**No errors!** This datapack is valid.' if len(errors) == 0 else f'There {f"is **1** error." if len(errors) == 1 else f"are **{len(errors)}** errors. Here is the first one:"}{nl}```{error1["annotation"] + nl*2 + error1["message"] + nl*2 + nl.join(error1["details"])}```'}
			"""
		)
		embed.set_footer(text="Powered by Beet and Mecha.")

		await interaction.followup.send(embed=embed)
		os.remove(f"tmp/{filename}")

	@analyze.autocomplete('version')
	async def autocomplete_callback(self, interaction: discord.Interaction, current: str):
		return [
			app_commands.Choice(name=version, value=version)
			for version in ["1.19", "1.18", "1.17"]
			if current in version
		]


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