import discord
import logging
import os
from discord import app_commands
from discord.ext import commands
from libraries import incendy
from libraries.project import Project
import libraries.constants as Constants

class Updater(commands.Cog):
	def __init__(self, client: incendy.IncendyBot):
		self.client = client

	async def cog_load(self):
		logging.info(f'> {self.__cog_name__} cog loaded')

	async def cog_unload(self):
		logging.info(f'> {self.__cog_name__} cog unloaded')

	### FUNCTIONS ###

	async def get_patrons(self, interaction: discord.Interaction) -> dict:
		"""Get a dictionary of all patrons based on their level"""

		guild = self.client.get_guild(Constants.Guild.STARDUST_LABS)

		patrons = {"blaze":[],"sentry":[],"inferno":[],"overlord":[],"undying":[],"flamekeeper":[]}
		patrons["flamekeeper"].extend([member.name for member in guild.get_role(Constants.Role.FLAMEKEEPER_PATRON).members])
		patrons["undying"].extend([member.name for member in guild.get_role(Constants.Role.UNDYING_PATRON).members])
		patrons["overlord"].extend([member.name for member in guild.get_role(Constants.Role.OVERLORD_PATRON).members])
		patrons["inferno"].extend([member.name for member in guild.get_role(Constants.Role.INFERNO_PATRON).members])
		patrons["inferno"].extend([member.name for member in guild.get_role(Constants.Role.INFERNO_SUB).members])
		patrons["sentry"].extend([member.name for member in guild.get_role(Constants.Role.SENTRY_PATRON).members])
		patrons["sentry"].extend([member.name for member in guild.get_role(Constants.Role.SENTRY_SUB).members])
		patrons["blaze"].extend([member.name for member in guild.get_role(Constants.Role.BLAZE_PATRON).members])
		patrons["blaze"].extend([member.name for member in guild.get_role(Constants.Role.BLAZE_SUB).members])

		return patrons

	### COMMANDS ###

	@app_commands.default_permissions(administrator=True)
	@app_commands.checks.has_permissions(administrator=True)
	@app_commands.command(name="makemod", description="[ADMIN] Create a mod version of a given datapack")
	@app_commands.describe(
		project="The name of the project to upload for",
		archive="A physical Zip file to upload"
	)
	async def makemod(self, interaction: discord.Interaction, project: str, archive: discord.Attachment = None):
		if archive.content_type != "application/zip":
			await interaction.response.send_message("The attachment is not a valid datapack! It **must** be a zip (not rar)!", ephemeral=True)
			return
		
		embed = discord.Embed(
			title=project,
			color=discord.Colour.blue(),
			description=f"Select which Minecraft versions that this {project} version is compatible with.\n\n**OBS**: Make sure you select *all* compatible versions! For example, if uploading a 1.19.3 pack, select 1.19, 1.19.1, 1.19.2, and 1.19.3."
		)
		view = discord.ui.View()
		patrons = await self.get_patrons(interaction)
		project_upload = Project(client=self.client, archive=archive, project_name=project, patrons=patrons)
		view.add_item(ModVersionSelect(project_upload))
		
		await interaction.response.send_message(embed=embed, view=view)

	@app_commands.default_permissions(administrator=True)
	@app_commands.checks.has_permissions(administrator=True)
	@app_commands.command(name="upload", description="[ADMIN] Upload datapacks or mods to any of our distribution platforms")
	@app_commands.describe(
		project="The name of the project to upload for",
		archive="A physical Jar or Zip file to upload"
	)
	async def update(self, interaction: discord.Interaction, project: str, archive: discord.Attachment = None):
		if archive.content_type not in ["application/zip", "application/java-archive"]:
			await interaction.response.send_message("The attachment is not a valid datapack or mod! It **must** be a zip (not rar) or jar file!", ephemeral=True)
			return
		
		embed = discord.Embed(
			title=project,
			color=discord.Colour.blue(),
			description=f"Select which platforms you'd like to upload {project} to.\n\n**OBS**: If you've uploaded a datapack, and select a modded platform, Incendy will automatically turn it into a mod!"
		)
		view = discord.ui.View()
		patrons = await self.get_patrons(interaction)
		project_upload = Project(client=self.client, archive=archive, project_name=project, patrons=patrons)
		view.add_item(PlatformSelect(project_upload))
		
		await interaction.response.send_message(embed=embed, view=view)

	@makemod.autocomplete('project')
	@update.autocomplete('project')
	async def autocomplete_callback(self, interaction: discord.Interaction, current: str):
		if interaction.user.id in [Constants.User.TERA, Constants.User.KUMA]:
			projects = ["Sparkles"]
		else:
			projects = sorted(["Terralith", "Incendium", "Nullscape", "Structory", "Amplified Nether", "Continents", "Structory: Towers", "Sparkles"])
		
		return [
            app_commands.Choice(name=project, value=project)
            for project in projects
            if current.replace(" ", "").lower() in project.replace(" ", "").lower()
        ]

### COMPONENTS ###
	
class PlatformSelect(discord.ui.Select):
	def __init__(self, project_upload: Project):
		self.project_upload = project_upload

		options = [
			discord.SelectOption(label=platform, description=self.project_upload.platforms[platform]["description"], emoji=self.project_upload.platforms[platform]["emoji"])
			for platform in project_upload.platforms
			if project_upload.project_name in project_upload.platforms[platform]["projects"].keys()
		]

		super().__init__(placeholder='Select your platforms...', min_values=1, max_values=max(1, len(options)), options=options)

	async def callback(self, interaction: discord.Interaction):
		self.project_upload.set_platforms(self.values)

		embed = interaction.message.embeds[0]
		embed.description = f"Select which Minecraft versions that this {self.project_upload.project_name} version is compatible with.\n\n**OBS**: Make sure you select *all* compatible versions! For example, if uploading a 1.19.3 pack, select 1.19, 1.19.1, 1.19.2, and 1.19.3."
		self.view.clear_items()
		self.view.add_item(VersionSelect(self.project_upload))
		await interaction.response.edit_message(embed=embed, view=self.view)

class VersionSelect(discord.ui.Select):
	def __init__(self, project_upload: Project):
		self.project_upload = project_upload

		options = [discord.SelectOption(label=version) for version in ["1.21.7", "1.21.6", "1.21.5", "1.21.4", "1.21.3", "1.21.2", "1.21.1", "1.21", "1.20.6", "1.20.5", "1.20.4", "1.20.3", "1.20.2", "1.20.1", "1.20", "1.19.4", "1.19.3", "1.19.2", "1.19.1", "1.19", "1.18.2", "1.18.1", "1.18", "1.17.1", "1.17"]]

		super().__init__(placeholder='Select compatible Minecraft versions...', min_values=1, max_values=len(options), options=options)

	async def callback(self, interaction: discord.Interaction):
		self.project_upload.set_mc_versions(sorted(self.values))
		await interaction.response.send_modal(UploadModal(self.project_upload))

class ModVersionSelect(discord.ui.Select):
	def __init__(self, project_upload: Project):
		self.project_upload = project_upload

		options = [discord.SelectOption(label=version) for version in ["1.21.7", "1.21.6", "1.21.5", "1.21.4", "1.21.3", "1.21.2", "1.21.1", "1.21", "1.20.6", "1.20.5", "1.20.4", "1.20.3", "1.20.2", "1.20.1", "1.20", "1.19.4", "1.19.3", "1.19.2", "1.19.1", "1.19", "1.18.2", "1.18.1", "1.18", "1.17.1", "1.17"]]

		super().__init__(placeholder='Select compatible Minecraft versions...', min_values=1, max_values=len(options), options=options)

	async def callback(self, interaction: discord.Interaction):
		self.project_upload.set_mc_versions(sorted(self.values))
		await interaction.response.send_modal(ModModal(self.project_upload))

class UploadModal(discord.ui.Modal, title='Update Information'):
	def __init__(self, project_upload: Project):
		super().__init__(timeout=1200.0)
		self.project_upload = project_upload

	version_number = discord.ui.TextInput(
        label='Version Number',
        style=discord.TextStyle.short,
        placeholder='ex: 5.1.5 (not v5.1.5)',
        required=True,
        max_length=10
    )

	changelog = discord.ui.TextInput(
		label='Changelog',
        style=discord.TextStyle.long,
        placeholder='Write in Markdown form...',
        required=True,
        max_length=2000
	)

	async def on_submit(self, interaction: discord.Interaction):
		self.project_upload.set_version_number(self.version_number.value)
		self.project_upload.set_changelog(self.changelog.value)

		self.clear_items()
		await interaction.response.defer(thinking=True, ephemeral=False)

		# Upload
		responses = await self.project_upload.upload()

		# Uploader's response
		embed = discord.Embed(title=f"{self.project_upload.project_name} {self.project_upload.version_name} Upload Status", color=discord.Color.blue())
		for site, resp in responses.items():
			if resp:
				embed.add_field(name=site.title(), value=f"[SUCCESS!]({resp})", inline=False)
			else:
				embed.add_field(name=site.title(), value="FAILED - Check logs!", inline=False)

		await interaction.followup.send(embed=embed)

		# Stardust News Posting
		embed = discord.Embed(
			title=f"New {self.project_upload.project_name} Release!",
			color=discord.Color.green(),
			description=f"{self.project_upload.version_name} Changelog:\n\n{self.project_upload.changelog}"
		)
		view = discord.ui.View()

		for site, resp in responses.items():
			if resp:
				view.add_item(discord.ui.Button(
					style=discord.ButtonStyle.link,
					label=site.title(),
					url=resp,
					emoji=Constants.Emoji.DOWNLOADS[site]
				))

		stardust_news = interaction.client.get_channel(Constants.Channel.STARDUST_NEWS)
		release = await stardust_news.send(embed=embed, view=view)
		await release.publish()

class ModModal(discord.ui.Modal, title='Mod Information'):
	def __init__(self, project_upload: Project):
		super().__init__(timeout=1200.0)
		self.project_upload = project_upload

	version_number = discord.ui.TextInput(
        label='Version Number',
        style=discord.TextStyle.short,
        placeholder='ex: 5.1.5 (not v5.1.5)',
        required=True,
        max_length=10
    )

	async def on_submit(self, interaction: discord.Interaction):
		self.project_upload.set_version_number(self.version_number.value)

		self.clear_items()
		await interaction.response.defer(thinking=True, ephemeral=False)

		filepath = await self.project_upload.create_mod()
		with open(filepath, 'rb') as f:
			modfile = discord.File(f, filename=filepath.split('/')[-1])

		await interaction.followup.send(file=modfile)

		os.remove(filepath)

async def setup(client):
	await client.add_cog(Updater(client))
