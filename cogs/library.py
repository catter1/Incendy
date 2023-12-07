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
				file=discord.File(f"assets/Cave Tweaks.png", filename="image.png"),
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



		# Amplified Nether
		if not threads["Amplified Nether"]:
			post = await forum.create_thread(
				name="Amplified Nether",
				content="*A pack that uses the new 1.18 features to increase the Nether height to 256 blocks tall, add new terrain types, and use 3D biomes... all without adding any biomes, structures, items, or mobs.*",
				file=discord.File(f"assets/Amplified Nether.png", filename="image.png"),
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
**Datapacks** {Constants.Emoji.PMC} {Constants.Emoji.GITHUB} {Constants.Emoji.STARDUST} - The latest datapack versions can be found here (exact number found on the button). These are in the format of `.zip`, and should be put in your datapacks folder.

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
				content="*A small add-on pack to reshape the world so that landmasses are further apart, varying in size and shape.*",
				file=discord.File(f"assets/Continents.png", filename="image.png"),
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
**Datapacks** {Constants.Emoji.PMC} {Constants.Emoji.GITHUB} {Constants.Emoji.STARDUST} - The latest datapack versions can be found here (exact number found on the button). These are in the format of `.zip`, and should be put in your datapacks folder.

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
				content="*Related to Structory, and adds plenty of unique towers scattered throughout the world.*",
				file=discord.File(f"assets/Structory Towers.png", filename="image.png"),
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
**Datapacks** {Constants.Emoji.GITHUB} - The latest datapack versions can be found here (exact number found on the button). These are in the format of `.zip`, and should be put in your datapacks folder.

**Mods** {Constants.Emoji.CURSEFORGE} - All available mod versions are downloaded here. These are in the format of `.jar`, and should be put in your mods folder.
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
				content="*A seasonally updated, atmospheric structure pack with light lore, ruins, firetowers, cottages, stables, graveyards, settlements, boats, and more.*",
				file=discord.File(f"assets/Structory.png", filename="image.png"),
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
**Datapacks** {Constants.Emoji.PMC} {Constants.Emoji.GITHUB} {Constants.Emoji.STARDUST} - The latest datapack versions can be found here (exact number found on the button). These are in the format of `.zip`, and should be put in your datapacks folder.

**Mods** {Constants.Emoji.CURSEFORGE} - All available mod versions are downloaded here. These are in the format of `.jar`, and should be put in your mods folder.
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
				content="*Overhauling the End's generation to maintain its bleak and depressing design, this pack adds a couple of biomes and tons of wacky terrain.*",
				file=discord.File(f"assets/Nullscape.png", filename="image.png"),
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
**Datapacks** {Constants.Emoji.PMC} {Constants.Emoji.GITHUB} {Constants.Emoji.STARDUST} - The latest datapack versions can be found here (exact number found on the button). These are in the format of `.zip`, and should be put in your datapacks folder.

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
				content="*Giving an almost modded feel, this pack adds tons of insane biomes, mobs, items, structures, and more, all while using Vanilla's features.*",
				file=discord.File(f"assets/Incendium.png", filename="image.png"),
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
**Datapacks** {Constants.Emoji.PMC} {Constants.Emoji.GITHUB} {Constants.Emoji.STARDUST} - The latest datapack versions can be found here (exact number found on the button). These are in the format of `.zip`, and should be put in your datapacks folder.

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
				content="*Adding over 95 brand new biomes and updating almost every vanilla biome, this staple pack turns the overworld into a beautiful place with new terrain, biomes, structures, and more.*",
				file=discord.File(f"assets/Terralith.png", filename="image.png"),
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
**Datapacks** {Constants.Emoji.PMC} {Constants.Emoji.STARDUST} {Constants.Emoji.GITHUB} {Constants.Emoji.SEEDFIX} - The latest datapack versions can be found here (exact number found on the button). These are in the format of `.zip`, and should be put in your datapacks folder.

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
		#self.add_item(discord.ui.Button(label='Datapack (1.20.x)', emoji=Constants.Emoji.PMC, url='https://www.planetminecraft.com/data-pack/terralith-overworld-evolved-100-biomes-caves-and-more/', row=0))
		self.add_item(discord.ui.Button(label='Datapack (1.17-1.20.x)', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/Terralith/releases', row=0))
		self.add_item(discord.ui.Button(label='Datapack (1.18.2 ONLY)', emoji=Constants.Emoji.SEEDFIX, url='https://sawdust.catter1.com/tools/seedfix', row=0))
		#self.add_item(discord.ui.Button(label='All Versions (1.17-1.20.x)', emoji=Constants.Emoji.STARDUST, url='https://www.stardustlabs.net/version-library#Terralith', row=0))
		self.add_item(discord.ui.Button(label='Fabric/Forge (1.18-1.20.x)', emoji=Constants.Emoji.MODRINTH, url='https://modrinth.com/mod/terralith/versions', row=1))
		self.add_item(discord.ui.Button(label='Fabric/Forge (1.18-1.20.x)', emoji=Constants.Emoji.CURSEFORGE, url='https://www.curseforge.com/minecraft/mc-mods/terralith/files', row=1))
		self.add_item(discord.ui.Button(label='Sparkles: Stardust Labs Resourcepack (1.18.2-1.20.x)', emoji=Constants.Emoji.MODRINTH, url='https://modrinth.com/resourcepack/sparkles', row=2))
		self.add_item(discord.ui.Button(label='Remove Intro Message (1.17-1.20.x)', emoji=Constants.Emoji.MODRINTH, url='https://modrinth.com/datapack/remove-terralith-intro-message', row=2))

class TerralithLinks(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Stardust Labs License', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/license/blob/main/license.txt', row=0))
		self.add_item(discord.ui.Button(label='Source Code', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/Terralith', row=0))
		self.add_item(discord.ui.Button(label='Bug Reports', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/Terralith/issues', row=0))
		self.add_item(discord.ui.Button(label='Datapack Map', emoji=Constants.Emoji.DATAPACKMAP, url='https://map.jacobsjo.eu/', row=1))
		self.add_item(discord.ui.Button(label='Wiki Page', emoji=Constants.Emoji.MIRAHEZE, url='https://stardustlabs.miraheze.org/wiki/Terralith', row=1))
		self.add_item(discord.ui.Button(label='Compatibility Table', emoji=Constants.Emoji.MIRAHEZE, url='https://stardustlabs.miraheze.org/wiki/Terralith#Compatibilities', row=1))
		self.add_item(discord.ui.Button(label='Translations', emoji=Constants.Emoji.WEBLATE, url='https://weblate.catter.dev/projects/stardust-labs', row=1))


class IncendiumDownloads(discord.ui.View):
	def __init__(self):
		super().__init__()
		#self.add_item(discord.ui.Button(label='Datapack (1.20.x)', emoji=Constants.Emoji.PMC, url='https://www.planetminecraft.com/data-pack/incendium-nether-expansion/', row=0))
		self.add_item(discord.ui.Button(label='Datapack (1.16.5-1.20.x)', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/Incendium/releases', row=0))
		#self.add_item(discord.ui.Button(label='All Versions (1.16.5-1.20.x)', emoji=Constants.Emoji.STARDUST, url='https://www.stardustlabs.net/version-library#Incendium', row=0))
		self.add_item(discord.ui.Button(label='Fabric/Forge (1.18.2-1.20.x)', emoji=Constants.Emoji.MODRINTH, url='https://modrinth.com/mod/incendium/versions', row=1))
		self.add_item(discord.ui.Button(label='Fabric/Forge (1.18.2-1.20.x)', emoji=Constants.Emoji.CURSEFORGE, url='https://www.curseforge.com/minecraft/mc-mods/incendium/files', row=1))
		self.add_item(discord.ui.Button(label='Sparkles: Stardust Labs Resourcepack (1.18.2-1.20.x)', emoji=Constants.Emoji.MODRINTH, url='https://modrinth.com/resourcepack/sparkles', row=2))

class IncendiumLinks(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Stardust Labs License', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/license/blob/main/license.txt', row=0))
		self.add_item(discord.ui.Button(label='Source Code', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/Incendium', row=0))
		self.add_item(discord.ui.Button(label='Bug Reports', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/Incendium/issues', row=0))
		self.add_item(discord.ui.Button(label='Datapack Map', emoji=Constants.Emoji.DATAPACKMAP, url='https://map.jacobsjo.eu/', row=1))
		self.add_item(discord.ui.Button(label='Wiki Page', emoji=Constants.Emoji.MIRAHEZE, url='https://stardustlabs.miraheze.org/wiki/Incendium', row=1))
		self.add_item(discord.ui.Button(label='Compatibility Table', emoji=Constants.Emoji.MIRAHEZE, url='https://stardustlabs.miraheze.org/wiki/Incendium#Compatibilities', row=1))
		self.add_item(discord.ui.Button(label='Translations', emoji=Constants.Emoji.WEBLATE, url='https://weblate.catter.dev/projects/stardust-labs', row=1))


class NullscapeDownloads(discord.ui.View):
	def __init__(self):
		super().__init__()
		#self.add_item(discord.ui.Button(label='Datapack (1.20.x)', emoji=Constants.Emoji.PMC, url='https://www.planetminecraft.com/data-pack/nullscape/', row=0))
		self.add_item(discord.ui.Button(label='Datapack (1.18.2-1.20.x)', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/Nullscape/releases', row=0))
		#self.add_item(discord.ui.Button(label='All Versions (1.18.2-1.20.x)', emoji=Constants.Emoji.STARDUST, url='https://www.stardustlabs.net/version-library#Nullscape', row=0))
		self.add_item(discord.ui.Button(label='Fabric/Forge (1.18.2-1.20.x)', emoji=Constants.Emoji.MODRINTH, url='https://modrinth.com/mod/nullscape/versions', row=1))
		self.add_item(discord.ui.Button(label='Fabric/Forge (1.18.2-1.20.x)', emoji=Constants.Emoji.CURSEFORGE, url='https://www.curseforge.com/minecraft/mc-mods/nullscape/files', row=1))
		self.add_item(discord.ui.Button(label='Sparkles: Stardust Labs Resourcepack (1.18.2-1.20.x)', emoji=Constants.Emoji.MODRINTH, url='https://modrinth.com/resourcepack/sparkles', row=2))

class NullscapeLinks(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Stardust Labs License', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/license/blob/main/license.txt', row=0))
		self.add_item(discord.ui.Button(label='Source Code', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/Nullscape', row=0))
		self.add_item(discord.ui.Button(label='Bug Reports', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/Nullscape/issues', row=0))
		self.add_item(discord.ui.Button(label='Datapack Map', emoji=Constants.Emoji.DATAPACKMAP, url='https://map.jacobsjo.eu/', row=1))
		self.add_item(discord.ui.Button(label='Wiki Page', emoji=Constants.Emoji.MIRAHEZE, url='https://stardustlabs.miraheze.org/wiki/Nullscape', row=1))
		self.add_item(discord.ui.Button(label='Compatibility Table', emoji=Constants.Emoji.MIRAHEZE, url='https://stardustlabs.miraheze.org/wiki/Nullscape#Compatibilities', row=1))
		self.add_item(discord.ui.Button(label='Translations', emoji=Constants.Emoji.WEBLATE, url='https://weblate.catter.dev/projects/stardust-labs', row=1))


class StructoryDownloads(discord.ui.View):
	def __init__(self):
		super().__init__()
		#self.add_item(discord.ui.Button(label='Datapack (1.20.x)', emoji=Constants.Emoji.PMC, url='https://www.planetminecraft.com/data-pack/structory/', row=0))
		self.add_item(discord.ui.Button(label='Datapack (1.18.2-1.20.x)', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/Structory/releases', row=0))
		#self.add_item(discord.ui.Button(label='All Versions (1.18.2-1.20.x)', emoji=Constants.Emoji.STARDUST, url='https://www.stardustlabs.net/version-library#Structory', row=0))
		self.add_item(discord.ui.Button(label='Fabric/Forge (1.18.2-1.20.x)', emoji=Constants.Emoji.CURSEFORGE, url='https://www.curseforge.com/minecraft/mc-mods/structory/files', row=1))
		self.add_item(discord.ui.Button(label='Sparkles: Stardust Labs Resourcepack (1.18.2-1.20.x)', emoji=Constants.Emoji.MODRINTH, url='https://modrinth.com/resourcepack/sparkles', row=2))

class StructoryLinks(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Stardust Labs License', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/license/blob/main/license.txt', row=0))
		self.add_item(discord.ui.Button(label='Source Code', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/Structory', row=0))
		self.add_item(discord.ui.Button(label='Bug Reports', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/Structory/issues', row=0))
		self.add_item(discord.ui.Button(label='Datapack Map', emoji=Constants.Emoji.DATAPACKMAP, url='https://map.jacobsjo.eu/', row=1))
		self.add_item(discord.ui.Button(label='Wiki Page', emoji=Constants.Emoji.MIRAHEZE, url='https://stardustlabs.miraheze.org/wiki/Structory', row=1))


class TowersDownloads(discord.ui.View):
	def __init__(self):
		super().__init__()
		#self.add_item(discord.ui.Button(label='Datapack (1.19-1.19.3)', emoji=Constants.Emoji.PMC, url='https://www.planetminecraft.com/data-pack/structory-towers/', row=0))
		self.add_item(discord.ui.Button(label='Datapack (1.19-1.20.x)', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/Structory-Towers/releases', row=0))
		self.add_item(discord.ui.Button(label='Fabric/Forge (1.19-1.20.x)', emoji=Constants.Emoji.CURSEFORGE, url='https://www.curseforge.com/minecraft/mc-mods/structory-towers/files', row=1))
		self.add_item(discord.ui.Button(label='Sparkles: Stardust Labs Resourcepack (1.18.2-1.20.x)', emoji=Constants.Emoji.MODRINTH, url='https://modrinth.com/resourcepack/sparkles', row=2))

class TowersLinks(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Stardust Labs License', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/license/blob/main/license.txt', row=0))
		self.add_item(discord.ui.Button(label='Source Code', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/Structory-Towers', row=0))
		self.add_item(discord.ui.Button(label='Bug Reports', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/Structory-Towers/issues', row=0))
		self.add_item(discord.ui.Button(label='Datapack Map', emoji=Constants.Emoji.DATAPACKMAP, url='https://map.jacobsjo.eu/', row=1))
		self.add_item(discord.ui.Button(label='Wiki Page', emoji=Constants.Emoji.MIRAHEZE, url='https://stardustlabs.miraheze.org/wiki/Structory:_Towers', row=1))


class ContinentsDownloads(discord.ui.View):
	def __init__(self):
		super().__init__()
		#self.add_item(discord.ui.Button(label='Datapack (1.20.x)', emoji=Constants.Emoji.PMC, url='https://www.planetminecraft.com/data-pack/continents/', row=0))
		self.add_item(discord.ui.Button(label='Datapack (1.18.2-1.20.x)', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/Continents/releases', row=0))
		#self.add_item(discord.ui.Button(label='All Versions (1.18.2-1.20.x)', emoji=Constants.Emoji.STARDUST, url='https://www.stardustlabs.net/version-library#Continents', row=0))
		self.add_item(discord.ui.Button(label='Fabric/Forge (1.18.2-1.20.x)', emoji=Constants.Emoji.MODRINTH, url='https://modrinth.com/mod/continents/versions', row=1))
		self.add_item(discord.ui.Button(label='Fabric/Forge (1.18.2-1.20.x)', emoji=Constants.Emoji.CURSEFORGE, url='https://www.curseforge.com/minecraft/mc-mods/continents/files', row=1))

class ContinentsLinks(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Stardust Labs License', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/license/blob/main/license.txt', row=0))
		self.add_item(discord.ui.Button(label='Source Code', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/Continents', row=0))
		self.add_item(discord.ui.Button(label='Bug Reports', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/Continents/issues', row=0))
		self.add_item(discord.ui.Button(label='Datapack Map', emoji=Constants.Emoji.DATAPACKMAP, url='https://map.jacobsjo.eu/', row=1))
		self.add_item(discord.ui.Button(label='Wiki Page', emoji=Constants.Emoji.MIRAHEZE, url='https://stardustlabs.miraheze.org/wiki/Continents', row=1))
		self.add_item(discord.ui.Button(label='Compatibility Table', emoji=Constants.Emoji.MIRAHEZE, url='https://stardustlabs.miraheze.org/wiki/Continents#Compatibilities', row=1))


class AmplifiedDownloads(discord.ui.View):
	def __init__(self):
		super().__init__()
		#self.add_item(discord.ui.Button(label='Datapack (1.20.x)', emoji=Constants.Emoji.PMC, url='https://www.planetminecraft.com/data-pack/amplified-nether-1-18/', row=0))
		self.add_item(discord.ui.Button(label='Datapack (1.16.5-1.20.x)', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/Amplified-Nether/releases', row=0))
		#self.add_item(discord.ui.Button(label='All Versions (1.16.5-1.20.x)', emoji=Constants.Emoji.STARDUST, url='https://www.stardustlabs.net/version-library#Amplified-Nether', row=0))
		self.add_item(discord.ui.Button(label='Fabric/Forge (1.18.2-1.20.x)', emoji=Constants.Emoji.MODRINTH, url='https://modrinth.com/mod/amplified-nether/versions', row=1))
		self.add_item(discord.ui.Button(label='Fabric/Forge (1.18.2-1.20.x)', emoji=Constants.Emoji.CURSEFORGE, url='https://www.curseforge.com/minecraft/mc-mods/amplified-nether/files', row=1))

class AmplifiedLinks(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Stardust Labs License', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/license/blob/main/license.txt', row=0))
		self.add_item(discord.ui.Button(label='Source Code', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/Amplified-Nether', row=0))
		self.add_item(discord.ui.Button(label='Bug Reports', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/Amplified-Nether/issues', row=0))
		self.add_item(discord.ui.Button(label='Datapack Map', emoji=Constants.Emoji.DATAPACKMAP, url='https://map.jacobsjo.eu/', row=1))
		self.add_item(discord.ui.Button(label='Wiki Page', emoji=Constants.Emoji.MIRAHEZE, url='https://stardustlabs.miraheze.org/wiki/Amplified_Nether', row=1))
		self.add_item(discord.ui.Button(label='Compatibility Table', emoji=Constants.Emoji.MIRAHEZE, url='https://stardustlabs.miraheze.org/wiki/Amplified_Nether#Compatibilities', row=1))


class CaveDownloads(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Fabric/Forge (1.18.1 ONLY)', emoji=Constants.Emoji.CURSEFORGE, url='https://www.curseforge.com/minecraft/mc-mods/cave-tweaks/files', row=0))
		self.add_item(discord.ui.Button(label='All Versions (1.18.1 ONLY)', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/Cave-Tweaks/releases', row=0))

class CaveLinks(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Stardust Labs License', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/license/blob/main/license.txt', row=0))
		self.add_item(discord.ui.Button(label='Source Code', emoji=Constants.Emoji.GITHUB, url='https://github.com/Stardust-Labs-MC/Cave-Tweaks', row=0))
		self.add_item(discord.ui.Button(label='Wiki Page', emoji=Constants.Emoji.MIRAHEZE, url='https://stardustlabs.miraheze.org/wiki/Cave_Tweaks', row=1))


async def setup(client):
	await client.add_cog(Library(client))