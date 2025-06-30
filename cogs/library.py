import discord
import logging
from discord import app_commands
from discord.ext import commands
from libraries import incendy
import libraries.constants as Constants

class Library(commands.Cog):
	def __init__(self, client: incendy.IncendyBot):
		self.client = client

	async def cog_load(self):
		logging.info(f'> {self.__cog_name__} cog loaded')

	async def cog_unload(self):
		logging.info(f'> {self.__cog_name__} cog unloaded')

	### COMMANDS ###

	@app_commands.command(name="library", description="[ADMIN] Prints the Downloads Library")
	@app_commands.default_permissions(administrator=True)
	@app_commands.checks.has_permissions(administrator=True)
	async def library(self, interaction: discord.Interaction):
		""" /library """

		forum: discord.ForumChannel
		if interaction.guild_id == Constants.Guild.STARDUST_LABS:
			forum = self.client.get_channel(1087096245228679330)
		else:
			forum = self.client.get_channel(1087041214911615058)

		threads: dict[str, discord.Thread | None]
		threads = {
			"[Discontinued] Cave Tweaks": None,
			"Sparkles: Stardust Labs Resourcepack": None,
			"Amplified Nether": None,
			"Continents": None,
			"Structory: Towers": None,
			"Structory": None,
			"Nullscape": None,
			"Incendium": None,
			"Terralith": None
		}

		for thread in forum.threads:
			if thread.name in threads.keys():
				threads[thread.name] = thread

		async for thread in forum.archived_threads():
			if thread.name in threads.keys():
				await thread.edit(archived=False, locked=False)
				threads[thread.name] = thread

		await interaction.response.send_message(f"Posting the downloads library in <#{forum.id}>...", ephemeral=True)

		
		# Cave Tweaks
		if not threads["[Discontinued] Cave Tweaks"]:
			post = await forum.create_thread(
				name="[Discontinued] Cave Tweaks",
				content="*A mod that allows for the extensive configuration of all caves.*",
				file=discord.File("assets/Cave Tweaks.png", filename="image.png"),
			)
			await post.message.pin()
			post = post.thread
			async for message in post.history(limit=1):
				if message.type == discord.MessageType.pins_add:
					await message.delete()
			
		else:
			post = threads["[Discontinued] Cave Tweaks"]
			async for message in post.history(limit=10):
				if not message.pinned:
					await message.delete()

		embed1 = discord.Embed(
			title="Downloads",
			color=discord.Colour.dark_grey(),
			description=f"""
**Note** - This project is __DISCONTINUED__. You may still use it for 1.18.1 and 1.18.1 only, but we offer no support for it.

**Mods** {Constants.Emoji.CURSEFORGE} - All available mod versions are downloaded here. These are in the format of `.jar`, and should be put in your mods folder.
		"""
		)

		embed2 = discord.Embed(
			title="Other Links",
			color=discord.Colour.dark_grey(),
			description="Various other related links can be found here. This includes everything from the wiki, Github, and more."
		)

		await post.send(embed=embed1, view=CaveDownloads())
		await post.send(embed=embed2, view=CaveLinks())



		# Sparkles
		if not threads["Sparkles: Stardust Labs Resourcepack"]:
			post = await forum.create_thread(
				name="Sparkles: Stardust Labs Resourcepack",
				content="*An optional resourcepack for all of Stardust Labs' projects. Adds localizations and minimap biome name fixes, as well as textures for Incendium.*",
				file=discord.File("assets/Sparkles.png", filename="image.png"),
			)
			await post.message.pin()
			post = post.thread
			async for message in post.history(limit=1):
				if message.type == discord.MessageType.pins_add:
					await message.delete()
			
		else:
			post = threads["Sparkles: Stardust Labs Resourcepack"]
			async for message in post.history(limit=10):
				if not message.pinned:
					await message.delete()

		embed1 = discord.Embed(
			title="Downloads",
			color=discord.Colour.yellow(),
			description=f"""
**Resourcepack** {Constants.Emoji.MODRINTH} - The latest resourcepack version can be found here (exact number found on the button). These are in the format of `.zip`, and should be put in your resourcepacks folder.

**Add-ons** {Constants.Emoji.MODRINTH} - The latest add-on versions can be found here (exact number found on the button). These are in the format of `.zip`, and should be put in your resourcepacks folder.
		"""
		)

		embed2 = discord.Embed(
			title="Other Links",
			color=discord.Colour.yellow(),
			description="Various other related links can be found here. This includes everything from the wiki, Github, and more."
		)

		await post.send(embed=embed1, view=SparklesDownloads())
		await post.send(embed=embed2, view=SparklesLinks())



		# Amplified Nether
		if not threads["Amplified Nether"]:
			post = await forum.create_thread(
				name="Amplified Nether",
				content="*The nether explorer's simple dream: doubled height and amplified terrain. What more is needed?*",
				file=discord.File("assets/Amplified Nether.png", filename="image.png"),
			)
			await post.message.pin()
			post = post.thread
			async for message in post.history(limit=1):
				if message.type == discord.MessageType.pins_add:
					await message.delete()
			
		else:
			post = threads["Amplified Nether"]
			async for message in post.history(limit=10):
				if not message.pinned:
					await message.delete()

		embed1 = discord.Embed(
			title="Downloads",
			color=discord.Colour.dark_red(),
			description=f"""
**Datapacks** {Constants.Emoji.MODRINTH} {Constants.Emoji.STARDUST} - The latest datapack versions can be found here (exact number found on the button). These are in the format of `.zip`, and should be put in your datapacks folder.

**Mods** {Constants.Emoji.MODRINTH} {Constants.Emoji.CURSEFORGE} - All available mod versions are downloaded here. These are in the format of `.jar`, and should be put in your mods folder.
		"""
		)

		embed2 = discord.Embed(
			title="Other Links",
			color=discord.Colour.dark_red(),
			description="Various other related links can be found here. This includes everything from the wiki, Github, and more."
		)

		await post.send(embed=embed1, view=AmplifiedDownloads())
		await post.send(embed=embed2, view=AmplifiedLinks())

		

		# Continents
		if not threads["Continents"]:
			post = await forum.create_thread(
				name="Continents",
				content="*Reshapes the world to consist of continents, separated by large oceans and small islands.*",
				file=discord.File("assets/Continents.png", filename="image.png"),
			)
			await post.message.pin()
			post = post.thread
			async for message in post.history(limit=1):
				if message.type == discord.MessageType.pins_add:
					await message.delete()
			
		else:
			post = threads["Continents"]
			async for message in post.history(limit=10):
				if not message.pinned:
					await message.delete()

		embed1 = discord.Embed(
			title="Downloads",
			color=discord.Colour.green(),
			description=f"""
**Datapacks** {Constants.Emoji.MODRINTH} {Constants.Emoji.STARDUST} - The latest datapack versions can be found here (exact number found on the button). These are in the format of `.zip`, and should be put in your datapacks folder.

**Mods** {Constants.Emoji.MODRINTH} {Constants.Emoji.CURSEFORGE} - All available mod versions are downloaded here. These are in the format of `.jar`, and should be put in your mods folder.
		"""
		)

		embed2 = discord.Embed(
			title="Other Links",
			color=discord.Colour.green(),
			description="Various other related links can be found here. This includes everything from the wiki, Github, and more."
		)

		await post.send(embed=embed1, view=ContinentsDownloads())
		await post.send(embed=embed2, view=ContinentsLinks())

		

		# Structory: Towers
		if not threads["Structory: Towers"]:
			post = await forum.create_thread(
				name="Structory: Towers",
				content="*An add-on for Structory that adds immersive, biome-themed towers to the world.*",
				file=discord.File("assets/Structory Towers.png", filename="image.png"),
			)
			await post.message.pin()
			post = post.thread
			async for message in post.history(limit=1):
				if message.type == discord.MessageType.pins_add:
					await message.delete()
			
		else:
			post = threads["Structory: Towers"]
			async for message in post.history(limit=10):
				if not message.pinned:
					await message.delete()

		embed1 = discord.Embed(
			title="Downloads",
			color=discord.Colour.teal(),
			description=f"""
**Datapacks** {Constants.Emoji.MODRINTH} {Constants.Emoji.STARDUST} - The latest datapack versions can be found here (exact number found on the button). These are in the format of `.zip`, and should be put in your datapacks folder.

**Mods** {Constants.Emoji.MODRINTH} {Constants.Emoji.CURSEFORGE} - All available mod versions are downloaded here. These are in the format of `.jar`, and should be put in your mods folder.
		"""
		)

		embed2 = discord.Embed(
			title="Other Links",
			color=discord.Colour.teal(),
			description="Various other related links can be found here. This includes everything from the wiki, Github, and more."
		)

		await post.send(embed=embed1, view=TowersDownloads())
		await post.send(embed=embed2, view=TowersLinks())



		# Structory
		if not threads["Structory"]:
			post = await forum.create_thread(
				name="Structory",
				content="*An atmospheric structure mod with detailed themes, varied builds, and light lore. Occasionally recieves seasonal updates and add-ons.*",
				file=discord.File("assets/Structory.png", filename="image.png"),
			)
			await post.message.pin()
			post = post.thread
			async for message in post.history(limit=1):
				if message.type == discord.MessageType.pins_add:
					await message.delete()
			
		else:
			post = threads["Structory"]
			async for message in post.history(limit=10):
				if not message.pinned:
					await message.delete()

		embed1 = discord.Embed(
			title="Downloads",
			color=discord.Colour.fuchsia(),
			description=f"""
**Datapacks** {Constants.Emoji.MODRINTH} {Constants.Emoji.STARDUST} - The latest datapack versions can be found here (exact number found on the button). These are in the format of `.zip`, and should be put in your datapacks folder.

**Mods** {Constants.Emoji.MODRINTH} {Constants.Emoji.CURSEFORGE} - All available mod versions are downloaded here. These are in the format of `.jar`, and should be put in your mods folder.
"""
		)

		embed2 = discord.Embed(
			title="Other Links",
			color=discord.Colour.fuchsia(),
			description="Various other related links can be found here. This includes everything from the wiki, Github, and more."
		)

		await post.send(embed=embed1, view=StructoryDownloads())
		await post.send(embed=embed2, view=StructoryLinks())


		
		# Nullscape
		if not threads["Nullscape"]:
			post = await forum.create_thread(
				name="Nullscape",
				content="*Transforms the boring Vanilla end into an alien dimension with the most surreal terrain imaginable. Topped with a couple of new biomes to add to the experience, whilst keeping the end desolate.*",
				file=discord.File("assets/Nullscape.png", filename="image.png"),
			)
			await post.message.pin()
			post = post.thread
			async for message in post.history(limit=1):
				if message.type == discord.MessageType.pins_add:
					await message.delete()
			
		else:
			post = threads["Nullscape"]
			async for message in post.history(limit=10):
				if not message.pinned:
					await message.delete()

		embed1 = discord.Embed(
			title="Downloads",
			color=discord.Colour.purple(),
			description=f"""
**Datapacks** {Constants.Emoji.MODRINTH} {Constants.Emoji.STARDUST} - The latest datapack versions can be found here (exact number found on the button). These are in the format of `.zip`, and should be put in your datapacks folder.

**Mods** {Constants.Emoji.MODRINTH} {Constants.Emoji.CURSEFORGE} - All available mod versions are downloaded here. These are in the format of `.jar`, and should be put in your mods folder.

**Resourcepacks** {Constants.Emoji.MODRINTH} - Download links for all available and related resourcepacks.
		"""
		)

		embed2 = discord.Embed(
			title="Other Links",
			color=discord.Colour.purple(),
			description="Various other related links can be found here. This includes everything from the wiki, Github, and more."
		)

		await post.send(embed=embed1, view=NullscapeDownloads())
		await post.send(embed=embed2, view=NullscapeLinks())



		# Incendium
		if not threads["Incendium"]:
			post = await forum.create_thread(
				name="Incendium",
				content="*A nether biome overhaul combined with challenging structures to conquer, unique weapons to obtain, and tricky mobs to defeat.*",
				file=discord.File("assets/Incendium.png", filename="image.png"),
			)
			await post.message.pin()
			post = post.thread
			async for message in post.history(limit=1):
				if message.type == discord.MessageType.pins_add:
					await message.delete()
			
		else:
			post = threads["Incendium"]
			async for message in post.history(limit=10):
				if not message.pinned:
					await message.delete()

		embed1 = discord.Embed(
			title="Downloads",
			color=discord.Colour.brand_red(),
			description=f"""
**Datapacks** {Constants.Emoji.MODRINTH} {Constants.Emoji.STARDUST} - The latest datapack versions can be found here (exact number found on the button). These are in the format of `.zip`, and should be put in your datapacks folder.

**Mods** {Constants.Emoji.MODRINTH} {Constants.Emoji.CURSEFORGE} - All available mod versions are downloaded here. These are in the format of `.jar`, and should be put in your mods folder.

**Resourcepacks** {Constants.Emoji.MODRINTH} - Download links for all available and related resourcepacks.
		"""
		)

		embed2 = discord.Embed(
			title="Other Links",
			color=discord.Colour.brand_red(),
			description="Various other related links can be found here. This includes everything from the wiki, Github, and more."
		)

		await post.send(embed=embed1, view=IncendiumDownloads())
		await post.send(embed=embed2, view=IncendiumLinks())



		# Terralith
		if not threads["Terralith"]:
			post = await forum.create_thread(
				name="Terralith",
				content="*Explore almost 100 new biomes consisting of both realism and light fantasy, using just Vanilla blocks. Complete with several immersive structures to compliment the overhauled terrain.*",
				file=discord.File("assets/Terralith.png", filename="image.png"),
			)
			await post.message.pin()
			post = post.thread
			async for message in post.history(limit=1):
				if message.type == discord.MessageType.pins_add:
					await message.delete()
			
		else:
			post = threads["Terralith"]
			async for message in post.history(limit=10):
				if not message.pinned:
					await message.delete()

		embed1 = discord.Embed(
			title="Downloads",
			color=discord.Colour.dark_blue(),
			description=f"""
**Datapacks** {Constants.Emoji.MODRINTH} {Constants.Emoji.STARDUST} {Constants.Emoji.SEEDFIX} - The latest datapack versions can be found here (exact number found on the button). These are in the format of `.zip`, and should be put in your datapacks folder.

**Mods** {Constants.Emoji.MODRINTH} {Constants.Emoji.CURSEFORGE} - All available mod versions are downloaded here. These are in the format of `.jar`, and should be put in your mods folder.

**Resourcepacks** {Constants.Emoji.MODRINTH} - Download links for all available and related resourcepacks.
		"""
		)

		embed2 = discord.Embed(
			title="Other Links",
			color=discord.Colour.dark_blue(),
			description="Various other related links can be found here. This includes everything from the wiki, Github, and more."
		)

		await post.send(embed=embed1, view=TerralithDownloads())
		await post.send(embed=embed2, view=TerralithLinks())

	
	### BUTTONS ###

	
class TerralithDownloads(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Datapack (1.19-1.21.7)', emoji=Constants.Emoji.MODRINTH, url='https://modrinth.com/datapack/terralith/versions?l=datapack', row=0))
		self.add_item(discord.ui.Button(label='Datapack (1.21-1.21.7)', emoji=Constants.Emoji.SMITHED, url='https://smithed.net/packs/terralith', row=0))
		self.add_item(discord.ui.Button(label='Datapack (1.17-1.21.7)', emoji=Constants.Emoji.STARDUST, url='https://www.stardustlabs.net/version-library', row=0))
		#self.add_item(discord.ui.Button(label='Datapack (1.21.7)', emoji=Constants.Emoji.PMC, url='https://www.planetminecraft.com/data-pack/terralith-overworld-evolved-100-biomes-caves-and-more/', row=0))
		self.add_item(discord.ui.Button(label='Datapack (1.18.2 ONLY)', emoji=Constants.Emoji.SEEDFIX, url='https://sawdust.catter1.com/tools/seedfix', row=0))
		# self.add_item(discord.ui.Button(label='Datapack (1.17-1.21.7)', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/Terralith/releases', row=0))
		self.add_item(discord.ui.Button(label='Fabric/Forge (1.18-1.21.7)', emoji=Constants.Emoji.MODRINTH, url='https://modrinth.com/datapack/terralith/versions?l=fabric&l=forge&l=neoforge&l=quilt', row=1))
		self.add_item(discord.ui.Button(label='Fabric/Forge (1.18-1.21.7)', emoji=Constants.Emoji.CURSEFORGE, url='https://www.curseforge.com/minecraft/mc-mods/terralith/files', row=1))
		self.add_item(discord.ui.Button(label='Sparkles (1.18.2-1.21.7)', emoji=Constants.Emoji.MODRINTH, url='https://modrinth.com/resourcepack/sparkles', row=2))
		self.add_item(discord.ui.Button(label='Remove Intro Message (1.17-1.21.7)', emoji=Constants.Emoji.MODRINTH, url='https://modrinth.com/datapack/remove-terralith-intro-message', row=2))

class TerralithLinks(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Stardust Labs License', emoji=Constants.Emoji.SCALES, url='https://github.com/Stardust-Labs-MC/license/blob/main/license.txt', row=0))
		self.add_item(discord.ui.Button(label='Source Code', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/Terralith', row=0))
		self.add_item(discord.ui.Button(label='Bug Reports', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/Terralith/issues', row=0))
		self.add_item(discord.ui.Button(label='Datapack Map', emoji=Constants.Emoji.DATAPACKMAP, url='https://map.jacobsjo.eu/', row=1))
		self.add_item(discord.ui.Button(label='Wiki Page', emoji=Constants.Emoji.MIRAHEZE, url='https://stardustlabs.miraheze.org/wiki/Terralith', row=1))
		self.add_item(discord.ui.Button(label='Compatibility Table', emoji=Constants.Emoji.MIRAHEZE, url='https://stardustlabs.miraheze.org/wiki/Terralith#Compatibilities', row=1))
		self.add_item(discord.ui.Button(label='Translations', emoji=Constants.Emoji.WEBLATE, url='https://weblate.catter.dev/projects/stardust-labs', row=1))


class IncendiumDownloads(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Datapack (1.18.2-1.20.x)', emoji=Constants.Emoji.MODRINTH, url='https://modrinth.com/datapack/incendium/versions?l=datapack', row=0))
		self.add_item(discord.ui.Button(label='Datapack (1.16.5-1.21.7)', emoji=Constants.Emoji.STARDUST, url='https://www.stardustlabs.net/version-library', row=0))
		#self.add_item(discord.ui.Button(label='Datapack (1.20.x)', emoji=Constants.Emoji.PMC, url='https://www.planetminecraft.com/data-pack/incendium-nether-expansion/', row=0))
		#self.add_item(discord.ui.Button(label='Datapack (1.16.5-1.20.x)', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/Incendium/releases', row=0))
		self.add_item(discord.ui.Button(label='Fabric/Forge (1.18.2-1.20.x)', emoji=Constants.Emoji.MODRINTH, url='https://modrinth.com/datapack/incendium/versions?l=fabric&l=forge&l=neoforge&l=quilt', row=1))
		self.add_item(discord.ui.Button(label='Fabric/Forge (1.18.2-1.20.x)', emoji=Constants.Emoji.CURSEFORGE, url='https://www.curseforge.com/minecraft/mc-mods/incendium/files', row=1))
		self.add_item(discord.ui.Button(label='Sparkles (1.18.2-1.21.7)', emoji=Constants.Emoji.MODRINTH, url='https://modrinth.com/resourcepack/sparkles', row=2))

class IncendiumLinks(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Stardust Labs License', emoji=Constants.Emoji.SCALES, url='https://github.com/Stardust-Labs-MC/license/blob/main/license.txt', row=0))
		self.add_item(discord.ui.Button(label='Source Code', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/Incendium', row=0))
		self.add_item(discord.ui.Button(label='Bug Reports', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/Incendium/issues', row=0))
		self.add_item(discord.ui.Button(label='Datapack Map', emoji=Constants.Emoji.DATAPACKMAP, url='https://map.jacobsjo.eu/', row=1))
		self.add_item(discord.ui.Button(label='Wiki Page', emoji=Constants.Emoji.MIRAHEZE, url='https://stardustlabs.miraheze.org/wiki/Incendium', row=1))
		self.add_item(discord.ui.Button(label='Compatibility Table', emoji=Constants.Emoji.MIRAHEZE, url='https://stardustlabs.miraheze.org/wiki/Incendium#Compatibilities', row=1))
		self.add_item(discord.ui.Button(label='Translations', emoji=Constants.Emoji.WEBLATE, url='https://weblate.catter.dev/projects/stardust-labs', row=1))


class NullscapeDownloads(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Datapack (1.18.2-1.21.7)', emoji=Constants.Emoji.MODRINTH, url='https://modrinth.com/datapack/nullscape/versions?l=datapack', row=0))
		self.add_item(discord.ui.Button(label='Datapack (1.18.2-1.21.7)', emoji=Constants.Emoji.STARDUST, url='https://www.stardustlabs.net/version-library', row=0))
		#self.add_item(discord.ui.Button(label='Datapack (1.21.7)', emoji=Constants.Emoji.PMC, url='https://www.planetminecraft.com/data-pack/nullscape/', row=0))
		#self.add_item(discord.ui.Button(label='Datapack (1.18.2-1.21.7)', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/Nullscape/releases', row=0))
		self.add_item(discord.ui.Button(label='Fabric/Forge (1.18.2-1.21.7)', emoji=Constants.Emoji.MODRINTH, url='https://modrinth.com/datapack/nullscape/versions?l=fabric&l=forge&l=neoforge&l=quilt', row=1))
		self.add_item(discord.ui.Button(label='Fabric/Forge (1.18.2-1.21.7)', emoji=Constants.Emoji.CURSEFORGE, url='https://www.curseforge.com/minecraft/mc-mods/nullscape/files', row=1))
		self.add_item(discord.ui.Button(label='Sparkles (1.18.2-1.21.7)', emoji=Constants.Emoji.MODRINTH, url='https://modrinth.com/resourcepack/sparkles', row=2))

class NullscapeLinks(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Stardust Labs License', emoji=Constants.Emoji.SCALES, url='https://github.com/Stardust-Labs-MC/license/blob/main/license.txt', row=0))
		self.add_item(discord.ui.Button(label='Source Code', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/Nullscape', row=0))
		self.add_item(discord.ui.Button(label='Bug Reports', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/Nullscape/issues', row=0))
		self.add_item(discord.ui.Button(label='Datapack Map', emoji=Constants.Emoji.DATAPACKMAP, url='https://map.jacobsjo.eu/', row=1))
		self.add_item(discord.ui.Button(label='Wiki Page', emoji=Constants.Emoji.MIRAHEZE, url='https://stardustlabs.miraheze.org/wiki/Nullscape', row=1))
		self.add_item(discord.ui.Button(label='Compatibility Table', emoji=Constants.Emoji.MIRAHEZE, url='https://stardustlabs.miraheze.org/wiki/Nullscape#Compatibilities', row=1))
		self.add_item(discord.ui.Button(label='Translations', emoji=Constants.Emoji.WEBLATE, url='https://weblate.catter.dev/projects/stardust-labs', row=1))


class StructoryDownloads(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Datapack (1.19-1.21.7)', emoji=Constants.Emoji.MODRINTH, url='https://modrinth.com/datapack/structory/versions?l=datapack', row=0))
		self.add_item(discord.ui.Button(label='Datapack (1.18.2-1.21.7)', emoji=Constants.Emoji.STARDUST, url='https://www.stardustlabs.net/version-library', row=0))
		#self.add_item(discord.ui.Button(label='Datapack (1.21.7)', emoji=Constants.Emoji.PMC, url='https://www.planetminecraft.com/data-pack/structory/', row=0))
		#self.add_item(discord.ui.Button(label='Datapack (1.18.2-1.21.7)', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/Structory/releases', row=0))
		self.add_item(discord.ui.Button(label='Fabric/Forge (1.19-1.21.7)', emoji=Constants.Emoji.MODRINTH, url='https://modrinth.com/datapack/structory/versions?l=fabric&l=forge&l=neoforge&l=quilt', row=1))
		self.add_item(discord.ui.Button(label='Fabric/Forge (1.18.2-1.21.7)', emoji=Constants.Emoji.CURSEFORGE, url='https://www.curseforge.com/minecraft/mc-mods/structory/files', row=1))
		self.add_item(discord.ui.Button(label='Sparkles (1.18.2-1.21.7)', emoji=Constants.Emoji.MODRINTH, url='https://modrinth.com/resourcepack/sparkles', row=2))

class StructoryLinks(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Stardust Labs License', emoji=Constants.Emoji.SCALES, url='https://github.com/Stardust-Labs-MC/license/blob/main/license.txt', row=0))
		self.add_item(discord.ui.Button(label='Source Code', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/Structory', row=0))
		self.add_item(discord.ui.Button(label='Bug Reports', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/Structory/issues', row=0))
		self.add_item(discord.ui.Button(label='Datapack Map', emoji=Constants.Emoji.DATAPACKMAP, url='https://map.jacobsjo.eu/', row=1))
		self.add_item(discord.ui.Button(label='Wiki Page', emoji=Constants.Emoji.MIRAHEZE, url='https://stardustlabs.miraheze.org/wiki/Structory', row=1))


class TowersDownloads(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Datapack (1.19-1.21.7)', emoji=Constants.Emoji.MODRINTH, url='https://modrinth.com/datapack/structory-towers/versions?l=datapack', row=0))
		self.add_item(discord.ui.Button(label='Datapack (1.19-1.21.7)', emoji=Constants.Emoji.STARDUST, url='https://www.stardustlabs.net/version-library', row=0))
		#self.add_item(discord.ui.Button(label='Datapack (1.19-1.21.7)', emoji=Constants.Emoji.PMC, url='https://www.planetminecraft.com/data-pack/structory-towers/', row=0))
		#self.add_item(discord.ui.Button(label='Datapack (1.19-1.21.7)', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/Structory-Towers/releases', row=0))
		self.add_item(discord.ui.Button(label='Fabric/Forge (1.19-1.21.7)', emoji=Constants.Emoji.MODRINTH, url='https://modrinth.com/datapack/structory-towers/versions?l=fabric&l=forge&l=neoforge&l=quilt', row=1))
		self.add_item(discord.ui.Button(label='Fabric/Forge (1.19-1.21.7)', emoji=Constants.Emoji.CURSEFORGE, url='https://www.curseforge.com/minecraft/mc-mods/structory-towers/files', row=1))
		self.add_item(discord.ui.Button(label='Sparkles (1.18.2-1.21.7)', emoji=Constants.Emoji.MODRINTH, url='https://modrinth.com/resourcepack/sparkles', row=2))

class TowersLinks(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Stardust Labs License', emoji=Constants.Emoji.SCALES, url='https://github.com/Stardust-Labs-MC/license/blob/main/license.txt', row=0))
		self.add_item(discord.ui.Button(label='Source Code', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/Structory-Towers', row=0))
		self.add_item(discord.ui.Button(label='Bug Reports', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/Structory-Towers/issues', row=0))
		self.add_item(discord.ui.Button(label='Datapack Map', emoji=Constants.Emoji.DATAPACKMAP, url='https://map.jacobsjo.eu/', row=1))
		self.add_item(discord.ui.Button(label='Wiki Page', emoji=Constants.Emoji.MIRAHEZE, url='https://stardustlabs.miraheze.org/wiki/Structory:_Towers', row=1))


class ContinentsDownloads(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Datapack (1.18.2-1.21.7)', emoji=Constants.Emoji.MODRINTH, url='https://modrinth.com/datapack/continents/versions?l=datapack', row=0))
		self.add_item(discord.ui.Button(label='Datapack (1.18.2-1.21.7)', emoji=Constants.Emoji.STARDUST, url='https://www.stardustlabs.net/version-library', row=0))
		#self.add_item(discord.ui.Button(label='Datapack (1.21.7)', emoji=Constants.Emoji.PMC, url='https://www.planetminecraft.com/data-pack/continents/', row=0))
		#self.add_item(discord.ui.Button(label='Datapack (1.18.2-1.21.7)', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/Continents/releases', row=0))
		self.add_item(discord.ui.Button(label='Fabric/Forge (1.18.2-1.21.7)', emoji=Constants.Emoji.MODRINTH, url='https://modrinth.com/datapack/continents/versions?l=fabric&l=forge&l=neoforge&l=quilt', row=1))
		self.add_item(discord.ui.Button(label='Fabric/Forge (1.18.2-1.21.7)', emoji=Constants.Emoji.CURSEFORGE, url='https://www.curseforge.com/minecraft/mc-mods/continents/files', row=1))

class ContinentsLinks(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Stardust Labs License', emoji=Constants.Emoji.SCALES, url='https://github.com/Stardust-Labs-MC/license/blob/main/license.txt', row=0))
		self.add_item(discord.ui.Button(label='Source Code', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/Continents', row=0))
		self.add_item(discord.ui.Button(label='Bug Reports', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/Continents/issues', row=0))
		self.add_item(discord.ui.Button(label='Datapack Map', emoji=Constants.Emoji.DATAPACKMAP, url='https://map.jacobsjo.eu/', row=1))
		self.add_item(discord.ui.Button(label='Wiki Page', emoji=Constants.Emoji.MIRAHEZE, url='https://stardustlabs.miraheze.org/wiki/Continents', row=1))
		self.add_item(discord.ui.Button(label='Compatibility Table', emoji=Constants.Emoji.MIRAHEZE, url='https://stardustlabs.miraheze.org/wiki/Continents#Compatibilities', row=1))


class AmplifiedDownloads(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Datapack (1.18.2-1.21.7)', emoji=Constants.Emoji.MODRINTH, url='https://modrinth.com/datapack/amplified-nether/versions?l=datapack', row=0))
		self.add_item(discord.ui.Button(label='Datapack (1.16.5-1.21.7)', emoji=Constants.Emoji.STARDUST, url='https://www.stardustlabs.net/version-library', row=0))
		#self.add_item(discord.ui.Button(label='Datapack (1.21.7)', emoji=Constants.Emoji.PMC, url='https://www.planetminecraft.com/data-pack/amplified-nether-1-18/', row=0))
		#self.add_item(discord.ui.Button(label='Datapack (1.16.5-1.21.7)', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/Amplified-Nether/releases', row=0))
		self.add_item(discord.ui.Button(label='Fabric/Forge (1.18.2-1.21.7)', emoji=Constants.Emoji.MODRINTH, url='https://modrinth.com/datapack/amplified-nether/versions?l=fabric&l=forge&l=neoforge&l=quilt', row=1))
		self.add_item(discord.ui.Button(label='Fabric/Forge (1.18.2-1.21.7)', emoji=Constants.Emoji.CURSEFORGE, url='https://www.curseforge.com/minecraft/mc-mods/amplified-nether/files', row=1))

class AmplifiedLinks(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Stardust Labs License', emoji=Constants.Emoji.SCALES, url='https://github.com/Stardust-Labs-MC/license/blob/main/license.txt', row=0))
		self.add_item(discord.ui.Button(label='Source Code', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/Amplified-Nether', row=0))
		self.add_item(discord.ui.Button(label='Bug Reports', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/Amplified-Nether/issues', row=0))
		self.add_item(discord.ui.Button(label='Datapack Map', emoji=Constants.Emoji.DATAPACKMAP, url='https://map.jacobsjo.eu/', row=1))
		self.add_item(discord.ui.Button(label='Wiki Page', emoji=Constants.Emoji.MIRAHEZE, url='https://stardustlabs.miraheze.org/wiki/Amplified_Nether', row=1))
		self.add_item(discord.ui.Button(label='Compatibility Table', emoji=Constants.Emoji.MIRAHEZE, url='https://stardustlabs.miraheze.org/wiki/Amplified_Nether#Compatibilities', row=1))


class SparklesDownloads(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Resourcepack (1.19-1.21.7)', emoji=Constants.Emoji.MODRINTH, url='https://modrinth.com/resourcepack/sparkles', row=0))
		self.add_item(discord.ui.Button(label='Resourcepack (1.20-1.21.7)', emoji=Constants.Emoji.SMITHED, url='https://smithed.net/packs/sparkles', row=0))
		self.add_item(discord.ui.Button(label='ADDON: Alpha Islands (1.19-1.21.1)', emoji=Constants.Emoji.MODRINTH, url='https://modrinth.com/resourcepack/sparkles-addon-alpha-islands', row=1))

class SparklesLinks(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='3-Clause BSD License', emoji=Constants.Emoji.SCALES, url='https://opensource.org/license/bsd-3-clause', row=0))
		self.add_item(discord.ui.Button(label='Source Code', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/Sparkles-Resourcepack', row=0))
		self.add_item(discord.ui.Button(label='Bug Reports', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/Sparkles-Resourcepack/issues', row=0))


class CaveDownloads(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Fabric/Forge (1.18.1 ONLY)', emoji=Constants.Emoji.MODRINTH, url='https://modrinth.com/mod/cave-tweaks/versions', row=0))
		self.add_item(discord.ui.Button(label='Fabric/Forge (1.18.1 ONLY)', emoji=Constants.Emoji.CURSEFORGE, url='https://www.curseforge.com/minecraft/mc-mods/cave-tweaks/files', row=0))
		self.add_item(discord.ui.Button(label='All Versions (1.18.1 ONLY)', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/Cave-Tweaks/releases', row=0))

class CaveLinks(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Stardust Labs License', emoji=Constants.Emoji.SCALES, url='https://github.com/Stardust-Labs-MC/license/blob/main/license.txt', row=0))
		self.add_item(discord.ui.Button(label='Source Code', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/Cave-Tweaks', row=0))
		self.add_item(discord.ui.Button(label='Wiki Page', emoji=Constants.Emoji.MIRAHEZE, url='https://stardustlabs.miraheze.org/wiki/Cave_Tweaks', row=1))


async def setup(client):
	await client.add_cog(Library(client))