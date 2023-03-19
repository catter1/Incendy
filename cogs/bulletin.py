import discord
import json
import logging
from discord.ext import commands
from discord import app_commands
from colorsys import hls_to_rgb
from libraries import incendy

class Bulletin(commands.Cog):
	def __init__(self, client: incendy.IncendyBot):
		self.client = client
	
	async def cog_load(self):
		logging.info(f'> {self.__cog_name__} cog loaded')
		
	async def cog_unload(self):
		logging.info(f'> {self.__cog_name__} cog unloaded')

	### COMMANDS ###

	@app_commands.command(name="featured", description="[ADMIN] Sends the \"featured\" list")
	@app_commands.default_permissions(administrator=True)
	@app_commands.checks.has_permissions(administrator=True)
	async def featured(self, interaction: discord.Interaction):
		""" /featured """
		
		with open('resources/featured.json', 'r') as f:
			data = json.load(f)
			
		count = 0
		for item in data:
			for pack in data[item]:
				count += 1

        # Thanks SO: https://stackoverflow.com/questions/58811499/generating-gradient-colors-in-python
		def rainbow_color_stops(n=10, end=3/3):
			return [ hls_to_rgb(end * i/(n-1), 0.5, 1) for i in range(n) ]
		
		def get_rgb_rainbow(n=10):
			rgb_float = rainbow_color_stops(n=n)
			rgb_int = []
			for rgb in rgb_float:
				rgb_int.append(
					(
                        int(rgb[0] * 255),
                        int(rgb[1] * 255),
                        int(rgb[2] * 255)
                    )
                )
			return rgb_int
		
		colours = get_rgb_rainbow(n=count)
		
		for item in data:
			for pack in data[item]:
				count -= 1
				
				embed = discord.Embed(
                    title= pack["title"],
                    url= pack["link"],
                    color= discord.Colour.from_rgb(
                        colours[count][0],
                        colours[count][1],
                        colours[count][2]
                    )
                )
				
				user = self.client.get_user(pack["user"])
				
				embed.add_field(name=f"{item.capitalize()}", value=pack["desc"])
				embed.set_footer(text=f"Created by {user.display_name}", icon_url=user.avatar)
				
				await interaction.channel.send(embed=embed)
	
	@app_commands.command(name="announce", description="[ADMIN] Pastes a message as Incendy. Message controlled by catter")
	@app_commands.default_permissions(administrator=True)
	@app_commands.checks.has_permissions(administrator=True)
	async def serverrules(self, interaction: discord.Interaction):
		#await interaction.channel.send("Hey y'all! It's getting close to a certain holiday that certain people may celebrate, and I wanted to give everyone the greatest gift of all: knowledge of cybersecurity :sunglasses:\n\nDuring the holidays especially, there are a lot of scam links. Discord especially... I already banned one person who's account got hacked and was sending phishing links (free nitro). Luckily, this person was able to get their account back. But you may not be so lucky.\n\nFirst of all, **one** click is all it takes. Just one. That can compromise your entire account, even if you don't explicitly say your private info. Outside of Discord, it can lead to more damage. It could instantly install malware, steal all accounts you are logged into (or passwords that your browser saves), and use all communication means (like email) that you have to phish more people. If your friend sends you a link from their actual email/Discord to this cool online Christmas card they made for you, wouldn't you click it? Always check the link first.\n\nAnd finally, scams aren't for stupid people. You don't have to be stupid to fall for scams. Although some scams are blatant, others are very well crafted. Here is a nice video (https://www.youtube.com/watch?v=ntrGrfvvkII) by Atomic Shrimp, who explains it quite nicely. Links are a lot more dangerous than you may think.\n\nAnyways, that's all. I wish that you will all be safe this holiday season, and for now on. It's a pleasure to be your friendly discord bot, and I love every minute of it here \<3")
		pass

	@app_commands.command(name="serverrules", description="[ADMIN] Prints the #servers message")
	@app_commands.default_permissions(administrator=True)
	@app_commands.checks.has_permissions(administrator=True)
	async def serverrules(self, interaction: discord.Interaction):
		embed = discord.Embed(
			title="Want to advertise your server?",
			description="If you're running Incendium, Terralith, Nullscape, or any other Stardust Labs project on a public server, feel free to advertise it here so people can play!\n_ _",
			colour=discord.Color.brand_red()
		)
		embed.add_field(name="Rules", value="**•** Only post servers that have at least one Stardust Labs project installed.\n**•** DO NOT repost your server.\n**•** Don't spam your list of plugins or features in your description.\n**•** Pirated/cracked servers are **not** allowed! Doing so will instantly get you banned.")
		embed.add_field(name="How to Advertise", value="`1)` Do **/server**. It will prompt you for the server's name and ip, and make you confirm you've read the rules.\n`2)` Optionally, you can include a link to a discord server, and/or a related image.\n`3)` After you submit the command, you will be prompted to create a description.\n`4)` Submit, and enjoy!")
		await interaction.channel.send(embed=embed)

	@app_commands.command(name="server", description="Advertise a server in the server channel")
	@app_commands.checks.dynamic_cooldown(incendy.super_long_cd)
	@app_commands.describe(
		valid="This server follows the server and channel's pinned rules.",
		image="(Optional) A related image for your server (png, jpeg, jpg)"
	)
	async def server(self, interaction: discord.Interaction, valid: bool, image: discord.Attachment = None):
		if not valid:
			await interaction.response.send_message("Read the rules and try again with `valid=True`.", ephemeral=True)
		if image:
			if image.content_type != "image/jpeg" and image.content_type != "image/png":
				await interaction.response.send_message("Your attachment is not a valid image! It must be a png, jpg, or jpeg. Try again.", ephemeral=True)

		modal = ServerDesc(self.client, image)
		await interaction.response.send_modal(modal)
	
	@app_commands.command(name="stardustmc", description="[ADMIN] Prints the StardustMC info channel")
	@app_commands.default_permissions(administrator=True)
	@app_commands.checks.has_permissions(administrator=True)
	async def stardustmc(self, interaction: discord.Interaction):
		""" /stardustmc """

		embed1 = discord.Embed(
			colour=discord.Colour.teal(),
			title="Rules",
			description="**[1]** Respect others. See <#757077131699159060> for more information.\n**[2]** Follow both Discord ToS and Minecraft EULA.\n**[3]** Obey staff.\n**[4]** No griefing, hacking, duping, or otherwise gaining an unfair advantage. This list is non-exclusive.\n**[5]** No spamming. No excessive or directed profanity.\n\nFailure to comply with these rules can result in mutes, kicks, or bans, as seen fit."
		)
		embed2 = discord.Embed(
			colour=discord.Colour.teal(),
			title="FAQ",
			description="Q: Can I do ________?\nA: As long as it follows the rules, and __all players involved and affected__ are okay with it, sure! You can do anything from starting a friendly war, creating a nether hub, starting a community game/contest.\n\nQ: Will the server reset?\nA: Not for quite a while.\n\nQ: Are minimaps allowed?\nA: Normal client-side minimaps are allowed, but there is no server-side Dynamap or similar.\n\nQ: Can I have a channel to chat with just my teammates?\nA: Yes! in <#1001293556612345856>, click \"create thread\", check the \"private thread\" box, name the thread whatever you want, then @ people to invite them.\n\nQ: What is the world border?\nA: Infinite (well, practically infinite), but the Random TP distance is 100k blocks.\n\nQ: Are Chat Reports enabled?\nA: No, it is blocked by the server. You do not need client-side mods to block them (sometimes, they can even cause issues)."
		)
		embed3 = discord.Embed(
			colour=discord.Colour.teal(),
			title="General Info",
			description="> • Java/Bedrock Address: **stardustmc.net**\n> • Bedrock Port: **19132**\n> • Java Version: **1.19.3**\n> • Bedrock Version: **Latest Release**\n\n- To leave spawn, do **/rt**.\n- You have up to 3 homes. Set them using **/sethome [home name]**. Do this after you leave spawn, so you don't lose your spot!\n- Teleport to your home with **/home [home_name]**, and to other players with **/tpa [player]**.\n- Claim your area by doing **/claim**, then clicking the two corners of the claim.\n- You start out with 400 claim blocks, and will earn 100 per hour of playtime.\n- Do **/warp shops** to visit the Flipside Shopping District, and even create your own shop!"
		)
		embed4 = discord.Embed(
			colour=discord.Colour.teal(),
			title="Ping Role",
			description="Want to be pinged with important StardustMC-related announcements in <#1002721350143721603>? If so, react to this message with <:stardust:1058423314672013382>!"
		)

		x = await interaction.channel.send(embeds=[embed1, embed2, embed3, embed4])
		await x.add_reaction('<:stardust:1058423314672013382>')

	@app_commands.command(name="library", description="[ADMIN] Prints the Downloads Library")
	@app_commands.default_permissions(administrator=True)
	@app_commands.checks.has_permissions(administrator=True)
	async def library(self, interaction: discord.Interaction):
		""" /library """

		forum: discord.ForumChannel
		forum = self.client.get_channel(1087096245228679330)

		for thread in forum.threads:
			await thread.delete()

		with open("resources/textlinks.json", 'r') as f:
			textlinks = json.load(f)

		await interaction.response.send_message(f"Posting the downloads library in <#{forum.id}>...", ephemeral=True)

		
		# Cave Tweaks
		post = await forum.create_thread(
			name="[Discontinued] Cave Tweaks",
			content="*A mod that allows for the extensive configuration of all caves.*",
			file=discord.File(f"assets/Cave Tweaks.png", filename="image.png"),
		)

		embed1 = discord.Embed(
			title="Downloads",
			color=discord.Colour.dark_grey(),
			description="""
**Note** - This project is __DISCONTINUED__. You may still use it for 1.18.1 and 1.18.1 only, but we offer no support for it.

**Mods** <:curseforge:1077301605717770260> - All available mod versions are downloaded here. These are in the format of `.jar`, and should be put in your mods folder.
		"""
		)

		embed2 = discord.Embed(
			title="Other Links",
			color=discord.Colour.dark_grey(),
			description="Various other related links can be found here. This includes everything from the wiki, Github, and more."
		)

		await post.thread.send(embed=embed1, view=CaveDownloads())
		await post.thread.send(embed=embed2, view=CaveLinks())
		textlinks["cave tweaks"]["link"] = post.thread.jump_url



		# Amplified Nether
		post = await forum.create_thread(
			name="Amplified Nether",
			content="*A pack that uses the new 1.18 features to increase the Nether height to 256 blocks tall, add new terrain types, and use 3D biomes... all without adding any biomes, structures, items, or mobs.*",
			file=discord.File(f"assets/Amplified Nether.png", filename="image.png"),
		)

		embed1 = discord.Embed(
			title="Downloads",
			color=discord.Colour.dark_red(),
			description="""
**Datapacks** <:pmc:1045336243216584744> <:github:1045336251605188679> <:stardust:1058423314672013382> - The latest datapack versions can be found here (exact number found on the button). These are in the format of `.zip`, and should be put in your datapacks folder.

**Mods** <:modrinth:1045336248950214706> <:curseforge:1077301605717770260> - All available mod versions are downloaded here. These are in the format of `.jar`, and should be put in your mods folder.
		"""
		)

		embed2 = discord.Embed(
			title="Other Links",
			color=discord.Colour.dark_red(),
			description="Various other related links can be found here. This includes everything from the wiki, Github, and more."
		)

		await post.thread.send(embed=embed1, view=AmplifiedDownloads())
		await post.thread.send(embed=embed2, view=AmplifiedLinks())
		textlinks["amplified nether"]["link"] = post.thread.jump_url

		

		# Continents
		post = await forum.create_thread(
			name="Continents",
			content="*A small add-on pack to reshape the world so that landmasses are further apart, varying in size and shape.*",
			file=discord.File(f"assets/Continents.png", filename="image.png"),
		)

		embed1 = discord.Embed(
			title="Downloads",
			color=discord.Colour.green(),
			description="""
**Datapacks** <:pmc:1045336243216584744> <:github:1045336251605188679> <:stardust:1058423314672013382> - The latest datapack versions can be found here (exact number found on the button). These are in the format of `.zip`, and should be put in your datapacks folder.

**Mods** <:modrinth:1045336248950214706> <:curseforge:1077301605717770260> - All available mod versions are downloaded here. These are in the format of `.jar`, and should be put in your mods folder.
		"""
		)

		embed2 = discord.Embed(
			title="Other Links",
			color=discord.Colour.green(),
			description="Various other related links can be found here. This includes everything from the wiki, Github, and more."
		)

		await post.thread.send(embed=embed1, view=ContinentsDownloads())
		await post.thread.send(embed=embed2, view=ContinentsLinks())
		textlinks["continents"]["link"] = post.thread.jump_url

		

		# Structory: Towers
		post = await forum.create_thread(
			name="Structory: Towers",
			content="*Related to Structory, and adds plenty of unique towers scattered throughout the world.*",
			file=discord.File(f"assets/Structory Towers.png", filename="image.png"),
		)

		embed1 = discord.Embed(
			title="Downloads",
			color=discord.Colour.teal(),
			description="""
**Datapacks** <:github:1045336251605188679> - The latest datapack versions can be found here (exact number found on the button). These are in the format of `.zip`, and should be put in your datapacks folder.

**Mods** <:curseforge:1077301605717770260> - All available mod versions are downloaded here. These are in the format of `.jar`, and should be put in your mods folder.
		"""
		)

		embed2 = discord.Embed(
			title="Other Links",
			color=discord.Colour.teal(),
			description="Various other related links can be found here. This includes everything from the wiki, Github, and more."
		)

		await post.thread.send(embed=embed1, view=TowersDownloads())
		await post.thread.send(embed=embed2, view=TowersLinks())
		textlinks["structory: towers"]["link"] = post.thread.jump_url
		textlinks["structory towers"]["link"] = post.thread.jump_url



		# Structory
		post = await forum.create_thread(
			name="Structory",
			content="*A seasonally updated, atmospheric structure pack with light lore, ruins, firetowers, cottages, stables, graveyards, settlements, boats, and more.*",
			file=discord.File(f"assets/Structory.png", filename="image.png"),
		)

		embed1 = discord.Embed(
			title="Downloads",
			color=discord.Colour.fuchsia(),
			description="""
**Datapacks** <:pmc:1045336243216584744> <:github:1045336251605188679> <:stardust:1058423314672013382> - The latest datapack versions can be found here (exact number found on the button). These are in the format of `.zip`, and should be put in your datapacks folder.

**Mods** <:curseforge:1077301605717770260> - All available mod versions are downloaded here. These are in the format of `.jar`, and should be put in your mods folder.
"""
		)

		embed2 = discord.Embed(
			title="Other Links",
			color=discord.Colour.fuchsia(),
			description="Various other related links can be found here. This includes everything from the wiki, Github, and more."
		)

		await post.thread.send(embed=embed1, view=StructoryDownloads())
		await post.thread.send(embed=embed2, view=StructoryLinks())
		textlinks["structory"]["link"] = post.thread.jump_url


		
		# Nullscape
		post = await forum.create_thread(
			name="Nullscape",
			content="*Overhauling the End's generation to maintain its bleak and depressing design, this pack adds a couple of biomes and tons of wacky terrain.*",
			file=discord.File(f"assets/Nullscape.png", filename="image.png"),
		)

		embed1 = discord.Embed(
			title="Downloads",
			color=discord.Colour.purple(),
			description="""
**Datapacks** <:pmc:1045336243216584744> <:github:1045336251605188679> <:stardust:1058423314672013382> - The latest datapack versions can be found here (exact number found on the button). These are in the format of `.zip`, and should be put in your datapacks folder.

**Mods** <:modrinth:1045336248950214706> <:curseforge:1077301605717770260> - All available mod versions are downloaded here. These are in the format of `.jar`, and should be put in your mods folder.

**Resourcepacks** <:modrinth:1045336248950214706> - Download links for all available and related resourcepacks.
		"""
		)

		embed2 = discord.Embed(
			title="Other Links",
			color=discord.Colour.purple(),
			description="Various other related links can be found here. This includes everything from the wiki, Github, and more."
		)

		await post.thread.send(embed=embed1, view=NullscapeDownloads())
		await post.thread.send(embed=embed2, view=NullscapeLinks())
		textlinks["nullscape"]["link"] = post.thread.jump_url



		# Incendium
		post = await forum.create_thread(
			name="Incendium",
			content="*Giving an almost modded feel, this pack adds tons of insane biomes, mobs, items, structures, and more, all while using Vanilla's features.*",
			file=discord.File(f"assets/Incendium.png", filename="image.png"),
		)

		embed1 = discord.Embed(
			title="Downloads",
			color=discord.Colour.brand_red(),
			description="""
**Datapacks** <:pmc:1045336243216584744> <:github:1045336251605188679> <:stardust:1058423314672013382> - The latest datapack versions can be found here (exact number found on the button). These are in the format of `.zip`, and should be put in your datapacks folder.

**Mods** <:modrinth:1045336248950214706> <:curseforge:1077301605717770260> - All available mod versions are downloaded here. These are in the format of `.jar`, and should be put in your mods folder.

**Resourcepacks** <:modrinth:1045336248950214706> - Download links for all available and related resourcepacks.
		"""
		)

		embed2 = discord.Embed(
			title="Other Links",
			color=discord.Colour.brand_red(),
			description="Various other related links can be found here. This includes everything from the wiki, Github, and more."
		)

		await post.thread.send(embed=embed1, view=IncendiumDownloads())
		await post.thread.send(embed=embed2, view=IncendiumLinks())
		textlinks["incendium"]["link"] = post.thread.jump_url



		# Terralith
		post = await forum.create_thread(
			name="Terralith",
			content="*Adding over 95 brand new biomes and updating almost every vanilla biome, this staple pack turns the overworld into a beautiful place with new terrain, biomes, structures, and more.*",
			file=discord.File(f"assets/Terralith.png", filename="image.png"),
		)

		embed1 = discord.Embed(
			title="Downloads",
			color=discord.Colour.dark_blue(),
			description="""
**Datapacks** <:pmc:1045336243216584744> <:stardust:1058423314672013382> <:github:1045336251605188679> <:seedfix:917599175259070474> - The latest datapack versions can be found here (exact number found on the button). These are in the format of `.zip`, and should be put in your datapacks folder.

**Mods** <:modrinth:1045336248950214706> <:curseforge:1077301605717770260> - All available mod versions are downloaded here. These are in the format of `.jar`, and should be put in your mods folder.

**Resourcepacks** <:modrinth:1045336248950214706> - Download links for all available and related resourcepacks.
		"""
		)

		embed2 = discord.Embed(
			title="Other Links",
			color=discord.Colour.dark_blue(),
			description="Various other related links can be found here. This includes everything from the wiki, Github, and more."
		)

		await post.thread.send(embed=embed1, view=TerralithDownloads())
		await post.thread.send(embed=embed2, view=TerralithLinks())
		textlinks["terralith"]["link"] = post.thread.jump_url



		with open("resources/settings.json", 'r') as f:
			if interaction.guild_id == json.load(f)["stardust-guild-id"]:
				with open("resources/textlinks.json", 'w') as f:
					json.dump(textlinks, f, indent=4)

	### LISTENERS ###

	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload):
		if not payload.member.bot and payload.emoji.name == "stardust":
			guild = self.client.get_guild(738046951236567162)
			role = guild.get_role(1045484675184984114)
			await payload.member.add_roles(role)

	@commands.Cog.listener()
	async def on_raw_reaction_remove(self, payload):
		guild = self.client.get_guild(738046951236567162)
		user = guild.get_member(payload.user_id)

		if not user.bot and payload.emoji.name == "stardust":
			role = guild.get_role(1045484675184984114)
			await user.remove_roles(role)

### BUTTONS ###

class TerralithDownloads(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Datapack (1.19-1.19.3)', emoji='<:pmc:1045336243216584744>', url='https://www.planetminecraft.com/data-pack/terralith-overworld-evolved-100-biomes-caves-and-more/', row=0))
		self.add_item(discord.ui.Button(label='Datapack (1.18.2 ONLY)', emoji='<:seedfix:917599175259070474>', url='https://seedfix.stardustlabs.net/', row=0))
		self.add_item(discord.ui.Button(label='All Versions (1.17-1.19.4)', emoji='<:github:1045336251605188679>', url='https://github.com/Stardust-Labs-MC/Terralith/releases', row=0))
		self.add_item(discord.ui.Button(label='All Versions (1.17-1.19.3)', emoji='<:stardust:1058423314672013382>', url='https://www.stardustlabs.net/version-library#Terralith', row=0))
		self.add_item(discord.ui.Button(label='Fabric/Forge (1.18-1.19.4)', emoji='<:modrinth:1045336248950214706>', url='https://modrinth.com/mod/terralith/versions', row=1))
		self.add_item(discord.ui.Button(label='Fabric/Forge (1.18-1.19.4)', emoji='<:curseforge:1077301605717770260>', url='https://www.curseforge.com/minecraft/mc-mods/terralith/files', row=1))
		self.add_item(discord.ui.Button(label='Biome Name Fix (1.18-1.19.4)', emoji='<:modrinth:1045336248950214706>', url='https://modrinth.com/resourcepack/stardust-biome-name-fix', row=2))
		self.add_item(discord.ui.Button(label='Remove Intro Message (1.17-1.19.4)', emoji='<:modrinth:1045336248950214706>', url='https://modrinth.com/datapack/remove-terralith-intro-message', row=2))

class TerralithLinks(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Stardust Labs License', emoji='<:github:1045336251605188679>', url='https://github.com/Stardust-Labs-MC/license/blob/main/license.txt', row=0))
		self.add_item(discord.ui.Button(label='Source Code', emoji='<:github:1045336251605188679>', url='https://github.com/Stardust-Labs-MC/Terralith', row=0))
		self.add_item(discord.ui.Button(label='Bug Reports', emoji='<:github:1045336251605188679>', url='https://github.com/Stardust-Labs-MC/Terralith/issues', row=0))
		self.add_item(discord.ui.Button(label='Datapack Map', emoji='<:datapackmap:1087035532934135809>', url='https://map.jacobsjo.eu/', row=1))
		self.add_item(discord.ui.Button(label='Wiki Page', emoji='<:miraheze:890077957069111316>', url='https://stardustlabs.miraheze.org/wiki/Terralith', row=1))
		self.add_item(discord.ui.Button(label='Compatibility Table', emoji='<:miraheze:890077957069111316>', url='https://stardustlabs.miraheze.org/wiki/Terralith#Compatibilities', row=1))
		self.add_item(discord.ui.Button(label='Translations', emoji='<:weblate:1087038433031110676>', url='https://weblate.catter.dev/projects/stardust-labs', row=1))


class IncendiumDownloads(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Datapack (1.19-1.19.3)', emoji='<:pmc:1045336243216584744>', url='https://www.planetminecraft.com/data-pack/incendium-nether-expansion/', row=0))
		self.add_item(discord.ui.Button(label='All Versions (1.16.5-1.19.4)', emoji='<:github:1045336251605188679>', url='https://github.com/Stardust-Labs-MC/Incendium/releases', row=0))
		self.add_item(discord.ui.Button(label='All Versions (1.16.5-1.19.3)', emoji='<:stardust:1058423314672013382>', url='https://www.stardustlabs.net/version-library#Incendium', row=0))
		self.add_item(discord.ui.Button(label='Fabric/Forge (1.18.2-1.19.4)', emoji='<:modrinth:1045336248950214706>', url='https://modrinth.com/mod/incendium/versions', row=1))
		self.add_item(discord.ui.Button(label='Fabric/Forge (1.18.2-1.19.4)', emoji='<:curseforge:1077301605717770260>', url='https://www.curseforge.com/minecraft/mc-mods/incendium/files', row=1))
		self.add_item(discord.ui.Button(label='Optional Resource Pack (1.18.2-1.19.4)', emoji='<:modrinth:1045336248950214706>', url='https://modrinth.com/resourcepack/incendium-optional-resourcepack', row=2))
		self.add_item(discord.ui.Button(label='Biome Name Fix (1.18-1.19.4)', emoji='<:modrinth:1045336248950214706>', url='https://modrinth.com/resourcepack/stardust-biome-name-fix', row=2))

class IncendiumLinks(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Stardust Labs License', emoji='<:github:1045336251605188679>', url='https://github.com/Stardust-Labs-MC/license/blob/main/license.txt', row=0))
		self.add_item(discord.ui.Button(label='Source Code', emoji='<:github:1045336251605188679>', url='https://github.com/Stardust-Labs-MC/Incendium', row=0))
		self.add_item(discord.ui.Button(label='Bug Reports', emoji='<:github:1045336251605188679>', url='https://github.com/Stardust-Labs-MC/Incendium/issues', row=0))
		self.add_item(discord.ui.Button(label='Datapack Map', emoji='<:datapackmap:1087035532934135809>', url='https://map.jacobsjo.eu/', row=1))
		self.add_item(discord.ui.Button(label='Wiki Page', emoji='<:miraheze:890077957069111316>', url='https://stardustlabs.miraheze.org/wiki/Incendium', row=1))
		self.add_item(discord.ui.Button(label='Compatibility Table', emoji='<:miraheze:890077957069111316>', url='https://stardustlabs.miraheze.org/wiki/Incendium#Compatibilities', row=1))
		self.add_item(discord.ui.Button(label='Translations', emoji='<:weblate:1087038433031110676>', url='https://weblate.catter.dev/projects/stardust-labs', row=1))


class NullscapeDownloads(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Datapack (1.19-1.19.3)', emoji='<:pmc:1045336243216584744>', url='https://www.planetminecraft.com/data-pack/nullscape/', row=0))
		self.add_item(discord.ui.Button(label='All Versions (1.18.2-1.19.4)', emoji='<:github:1045336251605188679>', url='https://github.com/Stardust-Labs-MC/Nullscape/releases', row=0))
		self.add_item(discord.ui.Button(label='All Versions (1.18.2-1.19.3)', emoji='<:stardust:1058423314672013382>', url='https://www.stardustlabs.net/version-library#Nullscape', row=0))
		self.add_item(discord.ui.Button(label='Fabric/Forge (1.18.2-1.19.4)', emoji='<:modrinth:1045336248950214706>', url='https://modrinth.com/mod/nullscape/versions', row=1))
		self.add_item(discord.ui.Button(label='Fabric/Forge (1.18.2-1.19.4)', emoji='<:curseforge:1077301605717770260>', url='https://www.curseforge.com/minecraft/mc-mods/nullscape/files', row=1))
		self.add_item(discord.ui.Button(label='Biome Name Fix (1.18-1.19.4)', emoji='<:modrinth:1045336248950214706>', url='https://modrinth.com/resourcepack/stardust-biome-name-fix', row=2))

class NullscapeLinks(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Stardust Labs License', emoji='<:github:1045336251605188679>', url='https://github.com/Stardust-Labs-MC/license/blob/main/license.txt', row=0))
		self.add_item(discord.ui.Button(label='Source Code', emoji='<:github:1045336251605188679>', url='https://github.com/Stardust-Labs-MC/Nullscape', row=0))
		self.add_item(discord.ui.Button(label='Bug Reports', emoji='<:github:1045336251605188679>', url='https://github.com/Stardust-Labs-MC/Nullscape/issues', row=0))
		self.add_item(discord.ui.Button(label='Datapack Map', emoji='<:datapackmap:1087035532934135809>', url='https://map.jacobsjo.eu/', row=1))
		self.add_item(discord.ui.Button(label='Wiki Page', emoji='<:miraheze:890077957069111316>', url='https://stardustlabs.miraheze.org/wiki/Nullscape', row=1))
		self.add_item(discord.ui.Button(label='Compatibility Table', emoji='<:miraheze:890077957069111316>', url='https://stardustlabs.miraheze.org/wiki/Nullscape#Compatibilities', row=1))
		self.add_item(discord.ui.Button(label='Translations', emoji='<:weblate:1087038433031110676>', url='https://weblate.catter.dev/projects/stardust-labs', row=1))


class StructoryDownloads(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Datapack (1.19-1.19.3)', emoji='<:pmc:1045336243216584744>', url='https://www.planetminecraft.com/data-pack/structory/', row=0))
		self.add_item(discord.ui.Button(label='All Versions (1.18.2-1.19.4)', emoji='<:github:1045336251605188679>', url='https://github.com/Stardust-Labs-MC/Structory/releases', row=0))
		self.add_item(discord.ui.Button(label='All Versions (1.18.2-1.19.3)', emoji='<:stardust:1058423314672013382>', url='https://www.stardustlabs.net/version-library#Structory', row=0))
		self.add_item(discord.ui.Button(label='Fabric/Forge (1.18.2-1.19.4)', emoji='<:curseforge:1077301605717770260>', url='https://www.curseforge.com/minecraft/mc-mods/structory/files', row=1))

class StructoryLinks(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Stardust Labs License', emoji='<:github:1045336251605188679>', url='https://github.com/Stardust-Labs-MC/license/blob/main/license.txt', row=0))
		self.add_item(discord.ui.Button(label='Source Code', emoji='<:github:1045336251605188679>', url='https://github.com/Stardust-Labs-MC/Structory', row=0))
		self.add_item(discord.ui.Button(label='Bug Reports', emoji='<:github:1045336251605188679>', url='https://github.com/Stardust-Labs-MC/Structory/issues', row=0))
		self.add_item(discord.ui.Button(label='Datapack Map', emoji='<:datapackmap:1087035532934135809>', url='https://map.jacobsjo.eu/', row=1))
		self.add_item(discord.ui.Button(label='Wiki Page', emoji='<:miraheze:890077957069111316>', url='https://stardustlabs.miraheze.org/wiki/Structory', row=1))


class TowersDownloads(discord.ui.View):
	def __init__(self):
		super().__init__()
		#self.add_item(discord.ui.Button(label='Datapack (1.19-1.19.3)', emoji='<:pmc:1045336243216584744>', url='https://www.planetminecraft.com/data-pack/structory-towers/', row=0))
		self.add_item(discord.ui.Button(label='All Versions (1.17-1.19.4)', emoji='<:github:1045336251605188679>', url='https://github.com/Stardust-Labs-MC/Structory-Towers/releases', row=0))
		self.add_item(discord.ui.Button(label='Fabric/Forge (1.18-1.19.4)', emoji='<:curseforge:1077301605717770260>', url='https://www.curseforge.com/minecraft/mc-mods/structory/files', row=1))

class TowersLinks(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Stardust Labs License', emoji='<:github:1045336251605188679>', url='https://github.com/Stardust-Labs-MC/license/blob/main/license.txt', row=0))
		self.add_item(discord.ui.Button(label='Source Code', emoji='<:github:1045336251605188679>', url='https://github.com/Stardust-Labs-MC/Structory-Towers', row=0))
		self.add_item(discord.ui.Button(label='Bug Reports', emoji='<:github:1045336251605188679>', url='https://github.com/Stardust-Labs-MC/Structory-Towers/issues', row=0))
		self.add_item(discord.ui.Button(label='Datapack Map', emoji='<:datapackmap:1087035532934135809>', url='https://map.jacobsjo.eu/', row=1))
		self.add_item(discord.ui.Button(label='Wiki Page', emoji='<:miraheze:890077957069111316>', url='https://stardustlabs.miraheze.org/wiki/Structory:_Towers', row=1))


class ContinentsDownloads(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Datapack (1.18.2-1.19.3)', emoji='<:pmc:1045336243216584744>', url='https://www.planetminecraft.com/data-pack/continents/', row=0))
		self.add_item(discord.ui.Button(label='All Versions (1.18.2-1.19.4)', emoji='<:github:1045336251605188679>', url='https://github.com/Stardust-Labs-MC/Continents/releases', row=0))
		self.add_item(discord.ui.Button(label='All Versions (1.18.2-1.19.3)', emoji='<:stardust:1058423314672013382>', url='https://www.stardustlabs.net/version-library#Continents', row=0))
		self.add_item(discord.ui.Button(label='Fabric/Forge (1.18.2-1.19.4)', emoji='<:modrinth:1045336248950214706>', url='https://modrinth.com/mod/continents/versions', row=1))
		self.add_item(discord.ui.Button(label='Fabric/Forge (1.18.2-1.19.4)', emoji='<:curseforge:1077301605717770260>', url='https://www.curseforge.com/minecraft/mc-mods/continents/files', row=1))

class ContinentsLinks(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Stardust Labs License', emoji='<:github:1045336251605188679>', url='https://github.com/Stardust-Labs-MC/license/blob/main/license.txt', row=0))
		self.add_item(discord.ui.Button(label='Source Code', emoji='<:github:1045336251605188679>', url='https://github.com/Stardust-Labs-MC/Continents', row=0))
		self.add_item(discord.ui.Button(label='Bug Reports', emoji='<:github:1045336251605188679>', url='https://github.com/Stardust-Labs-MC/Continents/issues', row=0))
		self.add_item(discord.ui.Button(label='Datapack Map', emoji='<:datapackmap:1087035532934135809>', url='https://map.jacobsjo.eu/', row=1))
		self.add_item(discord.ui.Button(label='Wiki Page', emoji='<:miraheze:890077957069111316>', url='https://stardustlabs.miraheze.org/wiki/Continents', row=1))
		self.add_item(discord.ui.Button(label='Compatibility Table', emoji='<:miraheze:890077957069111316>', url='https://stardustlabs.miraheze.org/wiki/Continents#Compatibilities', row=1))


class AmplifiedDownloads(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Datapack (1.19-1.19.3)', emoji='<:pmc:1045336243216584744>', url='https://www.planetminecraft.com/data-pack/amplified-nether-1-18/', row=0))
		self.add_item(discord.ui.Button(label='All Versions (1.16.5-1.19.4)', emoji='<:github:1045336251605188679>', url='https://github.com/Stardust-Labs-MC/Amplified-Nether/releases', row=0))
		self.add_item(discord.ui.Button(label='All Versions (1.16.5-1.19.3)', emoji='<:stardust:1058423314672013382>', url='https://www.stardustlabs.net/version-library#Amplified-Nether', row=0))
		self.add_item(discord.ui.Button(label='Fabric/Forge (1.18.2-1.19.4)', emoji='<:modrinth:1045336248950214706>', url='https://modrinth.com/mod/amplified-nether/versions', row=1))
		self.add_item(discord.ui.Button(label='Fabric/Forge (1.18.2-1.19.4)', emoji='<:curseforge:1077301605717770260>', url='https://www.curseforge.com/minecraft/mc-mods/amplified-nether/files', row=1))

class AmplifiedLinks(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Stardust Labs License', emoji='<:github:1045336251605188679>', url='https://github.com/Stardust-Labs-MC/license/blob/main/license.txt', row=0))
		self.add_item(discord.ui.Button(label='Source Code', emoji='<:github:1045336251605188679>', url='https://github.com/Stardust-Labs-MC/Amplified-Nether', row=0))
		self.add_item(discord.ui.Button(label='Bug Reports', emoji='<:github:1045336251605188679>', url='https://github.com/Stardust-Labs-MC/Amplified-Nether/issues', row=0))
		self.add_item(discord.ui.Button(label='Datapack Map', emoji='<:datapackmap:1087035532934135809>', url='https://map.jacobsjo.eu/', row=1))
		self.add_item(discord.ui.Button(label='Wiki Page', emoji='<:miraheze:890077957069111316>', url='https://stardustlabs.miraheze.org/wiki/Amplified_Nether', row=1))
		self.add_item(discord.ui.Button(label='Compatibility Table', emoji='<:miraheze:890077957069111316>', url='https://stardustlabs.miraheze.org/wiki/Amplified_Nether#Compatibilities', row=1))


class CaveDownloads(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Fabric/Forge (1.18.1 ONLY)', emoji='<:curseforge:1077301605717770260>', url='https://www.curseforge.com/minecraft/mc-mods/cave-tweaks/files', row=0))
		self.add_item(discord.ui.Button(label='All Versions (1.18.1 ONLY)', emoji='<:github:1045336251605188679>', url='https://github.com/Stardust-Labs-MC/Cave-Tweaks/releases', row=0))

class CaveLinks(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Stardust Labs License', emoji='<:github:1045336251605188679>', url='https://github.com/Stardust-Labs-MC/license/blob/main/license.txt', row=0))
		self.add_item(discord.ui.Button(label='Source Code', emoji='<:github:1045336251605188679>', url='https://github.com/Stardust-Labs-MC/Cave-Tweaks', row=0))
		self.add_item(discord.ui.Button(label='Wiki Page', emoji='<:miraheze:890077957069111316>', url='https://stardustlabs.miraheze.org/wiki/Cave_Tweaks', row=1))

class ServerDesc(discord.ui.Modal, title='Server Info'):
	def __init__(self, client: incendy.IncendyBot, image: discord.Attachment):
		super().__init__(timeout=600.0)
		self.image = image
		self.servchan = client.get_channel(756923587339878420)
	
	server_name = discord.ui.TextInput(
        label='Your server\'s name',
        style=discord.TextStyle.short,
        placeholder='Insert name here...',
        required=True,
        max_length=50
    )
	server_ip = discord.ui.TextInput(
        label='Your server\'s IP',
        style=discord.TextStyle.short,
        placeholder='Insert IP here...',
        required=True,
        max_length=30
    )
	server_desc = discord.ui.TextInput(
        label='A description for your server',
        style=discord.TextStyle.long,
        placeholder='Type description here...',
        required=True,
        max_length=700
    )
	server_discord = discord.ui.TextInput(
        label='An optional related Discord link',
        style=discord.TextStyle.short,
        placeholder='Insert Discord link here...',
        required=False,
        max_length=60
    )

	async def on_submit(self, interaction: discord.Interaction):
		embed = discord.Embed(
			title=f"{self.server_name} - {self.server_ip}",
			description=self.server_desc,
			colour=discord.Colour.brand_red()
		)
		if self.image: embed.set_thumbnail(url=self.image.url)
		if self.server_discord: embed.description += f"\n\n[Discord Server]({self.server_discord})"
		embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
		embed.set_footer(text="Want to advertise your server here? Do /server!")

		await self.servchan.send(embed=embed)
		#await interaction.response.send_message(embed=embed)

		await interaction.response.send_message("Thanks! Your server has been posted in <#756923587339878420>!", ephemeral=True)
		
	async def on_error(self, interaction: discord.Interaction, error: Exception):
		await interaction.response.send_message("Oops! Something went wrong. Please try again.", ephemeral=True)
		raise error

async def setup(client):
	await client.add_cog(Bulletin(client))