import discord
import requests
import os
import logging
from discord import app_commands
from discord.ext import commands
from libraries import incendy
import libraries.constants as Constants

class Faq(commands.Cog):
	def __init__(self, client: incendy.IncendyBot):
		self.client = client
		
	async def cog_load(self):
		logging.info(f'> {self.__cog_name__} cog loaded')
	
	async def cog_unload(self):
		logging.info(f'> {self.__cog_name__} cog unloaded')

	### COMMANDS ###

	@app_commands.command(name="qp", description="Sends a \"Quick Post\"!")
	@app_commands.checks.dynamic_cooldown(incendy.short_cd)
	async def qp(self, interaction: discord.Interaction, qp: str):
		""" /qp [quickpost] """

		qp_dict = {
			"Standards": "https://xkcd.com/927/",
			"Try it and See": "https://tryitands.ee/",
			"Dont Ask to Ask": "https://dontasktoask.com/",
			"Notch Code": "`bl2 = !bls[(ab * 16 + ac) * 8 + ad] && (ab < 15 && bls[((ab + 1) * 16 + ac) * 8 + ad] || ab > 0 && bls[((ab - 1) * 16 + ac) * 8 + ad] || ac < 15 && bls[(ab * 16 + ac + 1) * 8 + ad] || ac > 0 && bls[(ab * 16 + (ac - 1)) * 8 + ad] || ad < 7 && bls[(ab * 16 + ac) * 8 + ad + 1] || ad > 0 && bls[(ab * 16 + ac) * 8 + (ad - 1)]);`",
			"Optifine Alternatives": "https://lambdaurora.dev/optifine_alternatives/",
			"Admin Menu": "To view Incendium's Admin Menu, do `/function incendium:_admin_menu`. This allows you to give yourself the custom items, spawn custom mobs, and more. Keep in mind you most have `op` permissions to do this.",
			"Send Logs": "In order to properly give assistance, you need to provide logs. When sharing them, do ***NOT*** send screenshots or copy/paste the lines directly into Discord. Instead, upload the actual log file itself, or upload them to a [Pastebin-like site](<https://mclo.gs/>) (Incendy will do this automatically for you if you upload the file to Discord). Not sure where to find your logs?\n\n**Singleplayer**: `.minecraft/logs` and/or `.minecraft/crash-reports`\n**Server**: `[main folder]/logs` and/or `[main folder]/crash-reports`",
			"Dimension Folders": "`DIM1` = `minecraft:the_end`\n`DIM-1` = `minecraft:the_nether`\n\nHow to remember: Think of the Overworld as \"Ground Zero\", or 0. -1 is less than 0, and the Nether is below (or \"less than\") the overworld. Therefore, the Nether is -1, or DIM**-1**. The same logic applies to the End: it's above the overworld, and 1 is greater than 0. Therefore, the End is 1, or DIM**1**.",
			"Mod vs Datapack": "For all Stardust Labs projects, the mod version is the same as the datapack in regards to performance and content. The only difference is the mods go in the `mods` folder, and datapacks in the `datapacks` folder.\n\nIn 1.18.2 and lower, the mod versions of the projects rely on [Unfixed Seeds](https://modrinth.com/mod/unfixed-seeds) in order to allow for, well, unfixed seeds, due to a 1.18.x-only [Minecraft Bug](https://bugs.mojang.com/browse/MC-195717). Otherwise, you can enjoy the same experience with both! \:)",
			"Keep Exploring": "In Terralith, it is completely normal to spawn in an area that isn't as \"stunning\" or \"breathtaking\" as all the screenshots you see posted around are. To find them, you've got to go explore your world! Keep walking, and you *will* find beautiful landscapes.",
			"Binary Search": "Sometimes, when you are trying to figure out your issue, you need to use the \"remove until it stops crashing\" method. Here is an efficient way to do so:\n - Divide your mods in half: Half A and Half B.\n - Add Half A to your game/server, and start.\n - If it crashes, remove half of Half A.\n - If it does not crash, add half of Half B.\n - Repeat the process until it's narrowed down to the culprit!",
			"Give Details": "Please, please provide details and be descriptive with your issue. We literally cannot help you without context. It also helps if you check the faq (`/faq`) and attach logs.",
			"Screenshot Tips": "Noelle went ahead and made a in-depth guide on taking amazing photos in Minecraft! View the wiki here: <https://github.com/Interstellar-Cow/Minecraft-Screenshotting/wiki>",
			"Aternos Lag Meme": "",
			"Fractureiser": "**All the information you need to know is found in this document:** <https://github.com/fractureiser-investigation/fractureiser/blob/main/docs/users.md>. Read it!\n\nIf you have further questions, ask in the designated Discord server. They will have the best and safest answers for you: https://discord.gg/zPdFK47682",
			"Connect Patreon": "Read [this article](https://support.patreon.com/hc/en-us/articles/212052266-Getting-Discord-access) for information on how to connect Patreon to your Discord account. Once connected, you will have access to special channels such as <#795485705949544468>.",
			"Locate Command": "### Biomes\n- **1.18.2-** : `/locatebiome`\n- **1.19+** : `/locate biome`\n- **1.18.2-** (some Paper-like servers) : `/minecraft:locatebiome`\n- **1.19+** (some Paper-like servers) : `/minecraft:locate biome`\n### Structures\n- **1.18.2-** : `/locate`\n- **1.19+** : `/locate structure`\n- **1.18.2-** (some Paper-like servers) : `/minecraft:locate`\n- **1.19+** (some Paper-like servers) : `/minecraft:locate structure`"
		}

		if qp == "Aternos Lag Meme":
			file = discord.File("assets/aternos_meme.png", filename="image.png")
			await interaction.response.send_message(qp_dict[qp], file=file)
			return

		await interaction.response.send_message(qp_dict[qp])

	@qp.autocomplete('qp')
	async def autocomplete_callback(self, interaction: discord.Interaction, current: str):
		qp_list = sorted(["Standards", "Discord Links", "Try it and See", "Dont Ask to Ask", "Notch Code", "Optifine Alternatives", "Admin Menu", "Send Logs", "Wiki Link", "Dimension Folders", "Mod vs Datapack", "Keep Exploring", "Binary Search", "Give Details", "Screenshot Tips", "Aternos Lag Meme", "Fractureiser", "Locate Command"])

		return [
			app_commands.Choice(name=qp, value=qp)
			for qp in qp_list
			if current.replace(" ", "").lower() in qp.replace(" ", "").lower()
		]

	@app_commands.command(name="faq", description="Frequently Asked Questions (for support)")
	@app_commands.describe(
		faq="The FAQ to view",
		public="Whether to make the FAQ visible to everyone. Keep it False unless you're trying to share!"
	)
	async def faq(self, interaction: discord.Interaction, faq: str, public: bool = False):
		""" /faq [q] """
		faq_colour = discord.Colour.brand_red()
		public = not public
		view = None
		file = None

		match faq:
			case "Biome IDs":
				await interaction.response.defer(ephemeral=public, thinking=True)
				versions = await self.get_versions()
				embed = discord.Embed(
					title='Biome ID List',
					description=f'Here are all the biomes IDs from Terralith {versions["Terralith"]}, Incendium {versions["Incendium"]}, and Nullscape {versions["Nullscape"]}.',
					color=faq_colour
				)
				file = discord.File("resources/funny_biomes.txt", filename="biome_id_list.txt")
			case "Compatibility":
				embed = discord.Embed(
					title='Stardust Labs Compatibility',
					description='''
If you are wondering about compatibility for specific mods/datapacks, check out the in-depth compatibility table on the wiki by clicking the button below! Otherwise, select one of the options below.
					''',
					color=faq_colour
				)
				view = Compat()
			case "Configuration":
				embed = discord.Embed(
					title='Configuration',
					description='There is **no configuration file** for datapacks (custom world settings like Large Biomes do not work either). That said, if you want to modify how the packs work, you\'ll have to modify the code inside the datapack. Do keep in mind the [Stardust Labs License](https://github.com/Stardust-Labs-MC/license/blob/main/license.txt) found inside all datapacks, which prohibits you from distributing modified versions of the projects. Select a configuration from the selection menu below.\n\nIf you are editing the mod version of our projects, the same instructions apply. First rename the `.jar` to `.zip`, perform the changes, and then when you\'re all set, rename the `.zip` back to `.jar`.',
					color=faq_colour
				)
				view = Config()
			case "Contributing":
				embed = discord.Embed(
					title='Contributing',
					description='Interested in contributing to Stardust Labs in some way? Here are some ways you can help!',
					color=faq_colour
				)
				embed.add_field(name="Wiki", value=f"The wiki could always use your help! You can do anything from adding mod/datapack compatabilities to the [compat table](https://stardustlabs.miraheze.org/wiki/Terralith_compatibilities), or help out greatly by helping with [Tera's to-do list](https://discord.com/channels/738046951236567162/794630105463783484/923270468956483584). Either way, ask in <#{Constants.Channel.WIKI}> and check out the [Wiki contribution guide](https://stardustlabs.miraheze.org/wiki/Contributing)! By helping out with some of the tougher stuff, you can earn the **Wiki Contributor** role.", inline=False)
				embed.add_field(name="Translations", value=f"In Incendium, there is a lot of stuff to be translated. If you know another language, go check out our [Localization Website](https://weblate.catter.dev) to start translating for all Stardust Labs projects! Is your language not there? Ask <@{Constants.User.CATTER}> to add it! By translating, you can earn the **Translator** role.", inline=False)
				embed.add_field(name="Code, Structures, and Community", value="For the most part, we don\'t accept code contributions for our projects unless you are skilled, well-known in the community, and we're intersted in working with you. It's a similar story for structures: we already have great builders that help us out, but occasionally we might see stuff we like from others and ask if they want to contribute. Finally, the best way you can contribute to Stardust Labs is to hang around and be part of the community! For those who have helped in some way with either code, structures, creating helpful third-party tools, or just being an integral part of our community, you can earn the **Contributor** role.", inline=False)
			case "Existing Worlds":
				embed = discord.Embed(
					title='Adding Worldgen Packs to Existing Worlds',
					description='Generally, it isn\'t recommended to add worldgen packs to existing worlds as blending isn\'t enabled. If you still wish to anyways, you have a few options:',
					color=faq_colour
				)
				embed.add_field(name="Option 1", value="""
Reset the dimension you are trying to add a worldgen pack for. 
- Deleting the Overworld is not recommended for obvious reasons, but if you want to anyways delete the `region` folder in regular worlds and `world/region` on Paper/Spigot-like servers.
- Deleting the Nether requires deleting the `DIM-1` folder in regular worlds and `world_the_nether/region` on Paper/Spigot-like servers.
- Deleting the End requires deleting the `DIM1` folder in regular worlds and `world_the_end/region` on Paper/Spigot-like servers.
					""", inline=False)
				embed.add_field(name="Option 2", value="Use a program like MCA Selector to forcefully enable blending on an existing world. **Use this option at your own risk, no one will provide support for it in this server!**", inline=False)
				embed.add_field(name="Option 3", value="Install the worldgen datapack, then deal with very nasty chunk borders. Basically Option 2, but without doing anything.", inline=False)
			case "Foliage Colors":
				embed = discord.Embed(
					title='Foliage Colors',
					description='''
Terralith uses a variety of grass and leaf colors, but does not use a resource pack. Instead, this is actually a Vanilla mechanic: for example, in Vanilla swamps, the water is browner and the leaves/grass is a dull/dark green. In Jungles and Mooshroom Islands, grass is a vibrant green. If Terralith or Vanilla do not define a custom color, the color is calculated based on the biome's temperature and humidity instead.
					
This mechanic is what Terralith uses, but instead of doing different shades of green, Terralith will use the mechanic for all colors. This is how you see red leaves in Forested Highlands, blue grass in Mirage Isles, pink leaves in Sakura Groves, and much more. Leaves will always take the color of the biome they are placed in, which means the color cannot be "moved" to a different biome.

Sometimes, you may notice all the leaves are the same color. This could be caused by a resourcepack overriding the leaves' colormap, which will break this mechanic. If you are on Bedrock playing on a Geyser server that uses Terralith, then there is unfortunately no way around this limitation currently.
					''',
					color=faq_colour
				)
			case "Is It Working":
				embed = discord.Embed(
					title='How Do I Tell If It\'s Working?',
					description='''**•** Do `/datapack list` in game. Does the datapack appear green in that list? If not, it is not installed correctly - follow `/faq Server Installation` in the Discord.
**•** If the first step was successful, type `/locate biome #terralith:all_terralith_biomes` (`/locatebiome #terralith:all_terralith_biomes` for 1.18.2 and lower) in game and see if you get a result. Replace `terralith` with whatever relevant datapack you're installing. If you did not get any results, follow the Server Installation mentioned before.
**•** If you're using Structory, do `/locate structure structory:` (`/locate structory:` in 1.18.2 and below) and follow the previous steps.
**•** For Continents, there isn't a sure way to tell. Just make sure you followed the Server installation FAQ, see if the land looks like continents, and use something like DynMap if you'd like to see if it's working.
					''',
					color=faq_colour
				)
			case "License":
				embed = discord.Embed(
					title='Stardust Labs License',
					description='You can find the license inside all Stardust Labs datapacks, or view it at [this link](https://sawdust.catter1.com/license). It applies to *all* projects created by Stardust Labs. Read it for important information, especially about modifying Stardust Labs\' projects.',
					color=faq_colour
				)
			case "Multiverse":
				embed = discord.Embed(
					title='Multiverse',
					description='''
Multiverse is not the friendliest with worldgen datapacks. Below you can find a method to try - it\'s not 100% guarenteed to work, but it\'s the best we have, and nothing else we can do to help other than recommend a BungeeCord server rather than using Multiverse. MyWorlds is untested.
					
**1.** Stop your server and take a backup.
**2.** Make sure your main world is the one with the worldgen datapacks, and delete the `region` folder *inside* of that `world` folder (or whatever it is equivalently named).
**3.** Delete Multiverse\'s `world.yml`, along with a `worlds.txt` if you have it.
**4.** The default world in your `server.properties` should be the one with the worldgen datapacks.
**5.** Boot up your server, join, and see if it worked.
**6.** If it works and you just have leftover broken chunks, you can either reset the world, edit with MCA Selector, or using WorldEdit\'s `//regen` command.
					''',
					color=faq_colour
				)
			case "Ore Distribution":
				embed = discord.Embed(
					title='Ore Distribution',
					description='Terralith uses the normal Vanilla ore distribution. However, there are some places that have extra ores than others: emeralds in Emerald Peaks, redstone in Scarlet Mountains, copper in Dripstone Caves, few exposed diamonds in Skylands, and a couple other *secret* places.',
					color=faq_colour
				)
				file = discord.File("assets/ore.jpeg", filename="image.jpeg")
				embed.set_image(url="attachment://image.jpeg")
			case "Other World Types":
				embed = discord.Embed(
					title='Other World Types',
					description=f'''
Terralith is not compatible with the Vanilla world types. This includes Super Flat, Large Biomes, Amplified, and Single Biome.

This may be changed in the future. Currently, there is a [bug report](https://bugs.mojang.com/browse/MC-260949) that is marked as confirmed and important, created by **Apollo**. If/when this gets fixed, Terralith may be compatible with the world types!
					''',
					color=faq_colour
				)
			case "Passive Animals":
				embed = discord.Embed(
					title='Passive Animal Spawns',
					description='''
Passive mobs only spawn on grass blocks (and similar), on less-spiky terrain, and closer to sea level. Because Terralith is more mountainous than Vanilla, and there are more biomes without grass blocks, you will tend to find less passive mobs.
					
Although is is not possible to change passive mob spawning conditions, Terralith increases the spawn rates on the places they *are* able to spawn on. The TL;DR is that Terralith can\'t do anything about the rarity of mob spawning locations. If you want to learn more about Vanilla mob spawning rules, check out [this Minecraft Wiki article](https://minecraft.wiki/w/Spawn#Spawn_conditions).
					''',
					color=faq_colour
				)
			case "Pregeneration":
				embed = discord.Embed(
					title='Pregeneration',
					description='''
Worldgen alone only causes lag when generating chunks for the first time. Because of this, pregenerating your world is highly encouraged. One of the best pregen mods/plugins is Chunky, which is what we recommend.
					
Click the buttons below for download links. Check out their respective websites for instructions on how to use it - __don\'t ask here__.

Using a Vanilla server, and can't use mods or plugins? You can try out the [World Pregen](https://github.com/GoldenDelicios/world-pregen) datapack. 
					''',
					color=faq_colour
				)
				view = Pregen()
			case "Realms":
				embed = discord.Embed(
					title='Using Realms',
					description='Since worldgen is still considered an experimental feature by Mojang, you **cannot** use any worldgen datapack on a Realm. Also, we do __not__ recommend Minehut or Aternos due to their poor quality. Use a better hosting service. Stardust Labs is partnered with Bisect Hosting - you should check them out instead!',
					color=faq_colour
				)
				view = Realms()
			case "Removing Worldgen Packs":
				embed = discord.Embed(
					title='Removing Worldgen Packs',
					description='''
There are two options for removing worldgen datapacks. One method involves resetting the dimension, while the other (Terralith only) method allows you to keep your world, but have ugly chunk borders.

Read more information and instructions on the [Sawdust website](https://sawdust.catter1.com/worldgen-removal)!
					''',
					color=faq_colour
				)
			case "Resource Pack":
				embed = discord.Embed(
					title='Resource Pack',
					description=f'''
Thanks to the work from <@{Constants.User.TERA}>, <@{Constants.User.KUMA}>, and our volunteer translators, we have the Stardust Optional Resourcepack! This all-in-one resourcepack has custom textures for Incendium content, localizations for biomes and text, and fixes long biome names when using minimaps or simiar mods. Download it from Modrinth by clicking the link below.

If you're confused, we used to have two separate resourcepacks: Incendium Optional Resourcepack and Stardust Biome Name Fix. They have been merged into this single resourcepack.
					''',
					color=faq_colour
				)
				view = Resource()
			case "Seedfix":
				embed = discord.Embed(
					title='SeedFix',
					description='''
In 1.18.x **only**, there is a [Minecraft bug](https://bugs.mojang.com/browse/MC-195717) that makes all worldgen datapacks use the same seed. This is **not** the case in 1.19+, as you can use seeds as normal! To use the datapack version of Terralith in 1.18.2, download a version from the SeedFix tool on the Sawdust website, which allows you to input your own seed. The resulting file is Terralith itself, so do not use it alongside another Terralith download. The mod versions rely on [Unfixed Seeds](https://modrinth.com/mod/unfixed-seeds), which fixes this issue without needing the website tool.
					''',
					color=faq_colour
				)
				view = Seedfix()
			case "Server Installation":
				embed = discord.Embed(
					title='Server Installation',
					description='''
Select an installation method from the Select Menu below!
					
You should **__ONLY__** select the "Install Method 1.19.3+ ONLY" selection if you are using 1.19.3+ - it will *not* work if you are using 1.19.2 or lower!
					''',
					color=faq_colour
				)
				view=Server()
			case "Stone Generation":
				embed = discord.Embed(
					title='Stone Generation',
					description='''
In Terralith, granite, diorite, and andesite do not generate in blobs like in Vanilla. Instead, they only generate in the respective cave biomes: Andesite Caves, Granite Caves, and Diorite Caves. These cave biomes are relatively common, and are made entirely out of their respective stone, which makes it perfect for mods like Create!
					
If you have trouble finding the caves, you can look at the surface of your world for granite pillars, andesite boulders, and diorite patches. These features mean the respective stone\'s cave biome can be found underneath! Check the graphic attached to see examples of how they look like, or view the [wiki entry](https://stardustlabs.miraheze.org/wiki/Terralith#Andesite_boulders).
					''',
					color=faq_colour
				)
				file = discord.File("assets/cavefeatures.png", filename="image.png")
				embed.set_image(url="attachment://image.png")
			case "Structory Addons":
				embed = discord.Embed(
					title='Structory Addons',
					description='Structory has two types of updates: seasons and addons. **Seasons** are updates to the regular Structory datapack, similar to any other datapack. **Addons**, such as __Structory: Towers__, are separate datapacks. They can be used by themselves, or alongside Structory. The point of these addons is to allow easy customizability of Structory!',
					color=faq_colour
				)
			case "Support Us":
				embed = discord.Embed(
					title='Supporting Stardust Labs',
					description='Want to support Stardust Labs and get some cool perks? If so, thank you!',
					color=faq_colour
				)
				embed.add_field(
					name='Support Methods',
					value='''
**•** Stardust Labs is partnered with **Bisect Hosting**! Use code `STARDUST` to get 25% off your first month, as well as access to the __Supporter Showcase__.
**•** By **Nitro Boosting** the Discord server, you also gain access to the __Supporter Showcase__!
**•** Subscribing to either our **Patreon** or **Server Subscription**, you have access to a range of __Patron Benefits__.
**•** If a subscription doesn\'t suit you, feel free to do a one-time donation to our **Ko-Fi** to gain access to the __Supporter Showcase__.
					''',
					inline=False
				)
				embed.add_field(
					name='Supporter Benefits',
					value='''
**•** The **Supporter Showcase** gives you access to small projects, such as Terralith: Fire Extinguisher. You also get access to a more exclusive <#774837076821540864>, being able to see images before anyone else.
**•** Our **Patron Benefits** have a lot to offer, including beta versions of our main projects, access to our build server, and the ability to add an easter egg somewhere. More details in the Patreon/Server Subscription buttons below!
					''',
					inline=False
				)
				view=Support()
			case "Terra Mods":
				embed = discord.Embed(
					title='Difference Between all "Terra" Mods',
					description='''
**Terralith**: A worldgen datapack/mod created by Stardust Labs
**Terra**: A 1.16.5 and 1.18.2 worldgen mod, incompatible with Terralith
**Terrablender**: A mod that allows compatibility between worldgen mods
**Terraforged**: A 1.16.5 worldgen mod, incompatible with Terralith
**Terratonic**: The compatibility between Terralith and Tectonic (see `/faq Tectonic`)
					''',
					color=faq_colour
				)
			case "Traveller Maps":
				embed = discord.Embed(
					title='Traveller\'s Maps',
					description='''
If your world/server is crashing upon opening a chest in a Terralith structure, it is probably due to the Traveller\'s Maps. Because the lag is just absurd, they have been removed in the recent versions of Terralith. If you\'re on 1.18.2, ensure you\'re using Terralith v2.2.3, and if on 1.19.x, ensure you\'re on Terralith v2.3.3 or higher. In Terralith 2.3.7, the maps have been 100% removed.
					
As a fun note, some changes in Minecraft 1.19.3 has greatly improved the lookup speed for structures, which is what the maps rely on. Although the changes are appreciated, it is still slow, so the Traveller\'s Maps have been removed completely from Terralith.

If you are still having this issue (even with Vanilla!), it is recommended to use the [Async Locator](https://modrinth.com/mod/async-locator) mod on your client/server to improve this lag
					''',
					color=faq_colour
				)
			case "Translation Strings":
				embed = discord.Embed(
					title='Translation Strings',
					description='''
When using Incendium, you may get some broken translation strings. Here is how to fix them based on what you see:
### `%1$s%4733088$s`
Update to the latest Incendium version based on your Minecraft version as shown:
- 1.19-1.19.3: Incendium 5.1.6+
- 1.19.4: Incendium 5.2.1+
- 1.20+: Incendium 5.3.0+
### `incendium.advancement.misc.root.title` (or similar formatting)
Ensure you are updated as shown above, as well as the following:
- If on a Paper/Spigot-like server, use the minimum versions as shown:
 - Paper: 505
 - Purpur: 1957
 - Pufferfish: 66
- If you are using a custom client such as Lunar, Badlion, Essential, or likely anything similar to it: __This is a bug with your client.__ They need to update to support the new format of translation strings, which was changed in 1.19.4. However, there is [an untested/unofficial plugin](https://www.spigotmc.org/resources/serversidetranslations.112283/) you can use on your server that may solve the issue.
					''',
					color=faq_colour
				)
			case "Updating Versions":
				embed = discord.Embed(
					title='Updating Versions',
					description='Make sure to always take a backup before updating! Select a datapack from the selection menu below to see information on updating those datapacks.',
					color=faq_colour
				)
				view = Update()
			case _:
				await interaction.response.send_message("An unexpected error ocurred! Try again, and let catter know what FAQ you were trying if the issue continues.", ephemeral=True)
				return

		#embed.set_author(name="\u200b", icon_url=faq_icon)
		if file:
			if view:
				await interaction.response.send_message(embed=embed, file=file, view=view, ephemeral=public)
			else:
				if faq == "Biome IDs":
					await interaction.followup.send(embed=embed, file=file, ephemeral=public)
					os.remove('resources/funny_biomes.txt')
				else:
					await interaction.response.send_message(embed=embed, file=file, ephemeral=public)
		else:
			if view:
				await interaction.response.send_message(embed=embed, view=view, ephemeral=public)
			else:
				await interaction.response.send_message(embed=embed, ephemeral=public)

		# Enter into DB
		if interaction.guild_id == Constants.Guild.STARDUST_LABS:
			query = '''INSERT INTO faqs(user_id, faq_name, sent_on) VALUES($1, $2, $3);'''
			await self.client.db.execute(query, interaction.user.id, faq, interaction.created_at)

	@faq.autocomplete('faq')
	async def autocomplete_callback(self, interaction: discord.Interaction, current: str):
		faq_list = sorted(["Ore Distribution", "Biome IDs", "Removing Worldgen Packs", "Traveller Maps", "Passive Animals", "Pregeneration", "Foliage Colors", "Contributing", "Resource Pack", "Configuration", "Server Installation", "Updating Versions", "Seedfix", "Compatibility", "Realms", "License", "Support Us", "Is It Working", "Multiverse", "Stone Generation", "Structory Addons", "Other World Types", "Terra Mods", "Translation Strings", "Existing Worlds"])

		choices = [
			app_commands.Choice(name=faq, value=faq)
			for faq in faq_list
			if current.replace(" ", "").lower() in faq.replace(" ", "").lower()
		]

		return choices[:25]

	async def get_versions(self) -> dict:
		versions = {"Incendium":"", "Terralith":"", "Nullscape":""}
		biomeids = []

		for project in versions.keys():
			# Handle versions
			url = f'https://api.github.com/repos/Stardust-Labs-MC/{project}/releases/latest'
			response = requests.get(url)

			if response.status_code == 200:
				data = response.json()
				versions[project] = data['tag_name']
			else:
				return None

			# Handle biome IDs
			biomeids = await self.get_biome_ids(project, biomeids)

		with open('resources/funny_biomes.txt', 'w') as f:
				for biomeid in biomeids:
					f.write(biomeid + '\n')

		return versions

	async def get_biome_ids(self, project: str, biomeids: list[str], curr: str = '') -> list[str]:
		url = f'https://api.github.com/repos/Stardust-Labs-MC/{project}/contents/data/{project.lower()}/worldgen/biome/{curr}'
		response = requests.get(url, params={"ref": "1.20"})

		if response.status_code == 200:
			data = response.json()
			for item in data:
				if item['type'] == 'file':
					if curr == '':
						biomeids.append(f"{project.lower()}:{item['name'].rsplit('.', 1)[0]}")
					else:
						biomeids.append(f"{project.lower()}:{curr}/{item['name'].rsplit('.', 1)[0]}")
				if item['type'] == 'dir':
					biomeids = await self.get_biome_ids(project, biomeids, item['name'])
		else:
			return None

		return biomeids

### BUTTONS ###

class Compat(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(CompatMenu())
		self.add_item(discord.ui.Button(label='Terralith Compat', emoji=Constants.Emoji.MIRAHEZE, url='https://stardustlabs.miraheze.org/wiki/Terralith#Compatibilities'))
		self.add_item(discord.ui.Button(label='Incendium Compat', emoji=Constants.Emoji.MIRAHEZE, url='https://stardustlabs.miraheze.org/wiki/Incendium#Compatibilities'))
		self.add_item(discord.ui.Button(label='Nullscape Compat', emoji=Constants.Emoji.MIRAHEZE, url='https://stardustlabs.miraheze.org/wiki/Nullscape#Compatibilities'))

class Pregen(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Chunky (Fabric)', emoji=Constants.Emoji.FABRIC, url='https://www.curseforge.com/minecraft/mc-mods/chunky-pregenerator'))
		self.add_item(discord.ui.Button(label='Chunky (Forge)', emoji=Constants.Emoji.CURSEFORGE, url='https://www.curseforge.com/minecraft/mc-mods/chunky-pregenerator-forge'))
		self.add_item(discord.ui.Button(label='Chunky (Paper/Spigot)', emoji=Constants.Emoji.SPIGOT, url='https://www.spigotmc.org/resources/chunky.81534/'))

class Realms(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Bisect Hosting', emoji=Constants.Emoji.BISECT, url='https://bisecthosting.com/stardust'))

class Resource(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Stardust Optional Resourcepack', emoji=Constants.Emoji.MODRINTH, url='https://modrinth.com/resourcepack/stardust-optional-resourcepack'))

class Seedfix(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Seedfix Tool', emoji=Constants.Emoji.SEEDFIX, url='https://sawdust.catter1.com/tools/seedfix'))
		self.add_item(discord.ui.Button(label='Mod Download', emoji=Constants.Emoji.MODRINTH, url='https://modrinth.com/mod/terralith'))

class Support(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Bisect Hosting', emoji=Constants.Emoji.BISECT, url='https://bisecthosting.com/stardust'))
		self.add_item(discord.ui.Button(label='Patreon', emoji=Constants.Emoji.PATREON, url='https://www.patreon.com/stardustlabs'))
		self.add_item(discord.ui.Button(label='Server Subscriptions', emoji=Constants.Emoji.DISCORD, url='https://discord.com/servers/stardust-labs-738046951236567162'))
		self.add_item(discord.ui.Button(label='Ko-Fi', emoji=Constants.Emoji.KOFI, url='https://ko-fi.com/stardustlabs'))

### SELECT MENUS ###

class CompatMenu(discord.ui.Select):
	def __init__(self):
		options = [
			discord.SelectOption(label='Stardust Labs', description='Compatibility within Stardust Labs\' own projects'),
			discord.SelectOption(label='WWOO', description='Terralith compatibility with William Wyther\'s Overhauled Overworld'),
			discord.SelectOption(label='Tectonic', description='Terralith compatibility with Tectonic/Terratonic'),
			discord.SelectOption(label='Folia', description='Compatibility with Folia, the server software'),
			discord.SelectOption(label='Other Biome Mods', description='Specifics on other biome mod compatibility')
		]
		super().__init__(placeholder='Select an option...', min_values=1, max_values=1, options=options)

	async def callback(self, interaction: discord.Interaction):
		embed = interaction.message.embeds[0]

		match self.values[0]:
			case 'Stardust Labs':
				embed.title = 'Compatibility (Stardust Labs)'
				embed.description = '''
All of Stardust Labs's datapacks are compatible with one another (Terralith, Incendium\*, Nullscape, Continents, Structory, Structory: Towers, Amplified Nether\*), with one exception: Incendium and Amplified Nether are mutually exclusive (not compatible) with one another. If you try to load them together, one of two things will happen:
- Amplified Nether won't load at all, it'll just be regular Incendium.
- Amplified Nether will load, but all surfaces in Incendium will be broken (one of multiple examples is no quartz in Quartz Flats)
If you do want both, just use Incendium! It has all the custom mobs, structures, mobs, items, etc; as well as Amplified Nether's terrain and part of its height.
				'''

			case 'WWOO':
				embed.title = 'Compatibility (WWOO)'
				embed.description = '''
Terralith is compatible with William Wyther\'s Overhauled Overworld __only__ when using the mod version 3.0 or higher of WWOO. Terrablender ([Fabric](https://www.curseforge.com/minecraft/mc-mods/terrablender-fabric) or [Forge](https://www.curseforge.com/minecraft/mc-mods/terrablender)) is required.

You will need to go inside WWOO\'s configs and enable Terralith compat, or in-game if using Fabric with [ModMenu](https://www.curseforge.com/minecraft/mc-mods/modmenu) and [Cloth Config](https://www.curseforge.com/minecraft/mc-mods/cloth-config/files). More information can be found on WWOO\'s [CurseForge page](https://www.curseforge.com/minecraft/mc-mods/william-wythers-overhauled-overworld).
				'''

			case 'Tectonic':
				embed.title = 'Compatibility (Tectonic)'
				embed.description = '''
By default, Terralith and Tectonic are not compatible with each other. If you'd like them to work together, you'll have to use the compat method that Apollo created called **Terratonic**. This exists for both datapack and mod versions of the packs.

**Datapacks**: Install [Terratonic](https://www.planetminecraft.com/data-pack/terratonic/) and [Terralith](https://www.planetminecraft.com/data-pack/terralith-overworld-evolved-100-biomes-caves-and-more/) into your datapacks folder. The base version of Tectonic is **not** required! Just make sure Terratonic loads *above* Terralith.
**Mods**: Install [Tectonic](https://modrinth.com/mod/tectonic) and [Terralith](https://modrinth.com/mod/terralith) into your mods folder. You do *not* need Terratonic for compatibility: it's built into the mod version of Tectonic!
				'''

			case 'Folia':
				embed.title = 'Compatibility (Folia)'
				embed.description = '''
Due to the way Folia works, functions cannot run on servers using it.
- All of Incendium's custom mobs, items, bosses, etc. are completely broken by this. If you still wish to have the terrain and biomes of Incendium, use the [Incendium Biomes Only](https://modrinth.com/datapack/incendium-biomes-only) datapack. Keep in mind that this datapack is **completely** unsupported by Stardust Labs.
- Terralith has a few functions for the intro message. Download [this datapack](https://discord.com/channels/738046951236567162/885616716091125810/1110047059366662234) to remove these.
- Nullscape works as long as you aren't on 1.18.2. If you are on 1.18.2 there are functions to make the dragon fight and exit port work at all, these cannot be removed.
- Amplfied Nether, Structory and Continents all work without any issues.
				'''

			case 'Other Biome Mods':
				embed.title = 'Compatibility (Other Biome Mods)'
				embed.description = '''
- If the mod relies on Terrablender, it will technically work. However, Terralith biomes will be very rare and you'll get a lot of "microbiomes" (biomes less than a few chunks big). The exception is if you use Terralith 2.2.4+ for 1.18.2, which has specific Terrablender compatibility coded in.
- If the mod relies on Biolith, the biomes that mods generate may be rarer but otherwise it will work without issues.
- If the mod relies on another dependency such as Blueprint, it may or may not work. Your best bet is to try it and see.
- If the mod relies on none of these, it very likely won't work with Terralith. Ask the mod offer for clarification if you wish.
				'''
		
		await interaction.response.edit_message(embed=embed)

class ConfigMenu(discord.ui.Select):
	def __init__(self):
		options = [
			discord.SelectOption(label='Resized Terralith Biomes', description='How to adjust biome size in Terralith'),
			discord.SelectOption(label='Remove Biomes', description='How to remove/replace biomes in Terralith'),
			discord.SelectOption(label='Taller Nether', description='How to add space above bedrock in the Nether'),
			discord.SelectOption(label='Adjusted Continent Size', description='How to change the size of landmasses in Continents'),
			discord.SelectOption(label='Resized Continents Spawn Island', description='How to change the size of the spawn island in Continents'),
			discord.SelectOption(label='Biome Layout', description='How to change Terralith\'s biome layout or terrain shaping')
		]
		super().__init__(placeholder='Select a configuration...', min_values=1, max_values=1, options=options)
		
	async def callback(self, interaction: discord.Interaction):
		embed = interaction.message.embeds[0]

		match self.values[0]:
			case 'Resized Terralith Biomes':
				embed.title = 'Configuration (Resized Terralith Biomes)'
				embed.description = '''
Open the mod/datapack files and navigate to `data/minecraft/worldgen/density_function/overworld`.
Open `base_erosion.json`, `temperature.json`, and `vegetation.json`. In each, you should see something like this: ```json
{
  "argument": {
	"xz_scale": 0.25,
	"y_scale": 0.0,
	"noise": "minecraft:erosion",
	"shift_x": "minecraft:shift_x",
	"shift_y": 0.0,
	"shift_z": "minecraft:shift_z",
	"type": "minecraft:shifted_noise"
  },
  "type": "minecraft:flat_cache"
}
```
Only change `xz_scale`, __do not touch anything else__. Smaller values = larger biomes. An `xz_scale` of 0.5 is 4x smaller biomes, and an `xz_scale` of 0.125 is 4x larger biomes. For context, the vanilla Large Biomes world type effectively uses an `xz_scale` of 0.0625.
				'''

			case 'Remove Biomes':
				embed.title = 'Configuration (Remove Biomes)'
				embed.description = '''
This method is not perfect, but can get the job done. This is not offocially supported.
- Unzip Terralith and open the `Terralith/data/minecraft/dimension/` folder.
- Open `overworld.json` and search (Ctrl+F) for the biomes you want to remove.
- Replace **only** the name of the biome and ignore the numbers. For example, replace `terralith:unwanted_biome` with `minecraft:wanted_biome` 
 - When removing Skylands, replace them with an ocean type (such as `minecraft:ocean`).
				'''

			case 'Biome Layout':
				embed.title = 'Configuration (Biome Layout/Terrain Shaping)'
				embed.description = '''
**Short answer:** *No.*
**Long answer:** Neither editing the biome layout or adjusting terrain shaping are possible without a lot of pain and suffering. You can try, but no one will offer support for this.
'''

			case 'Taller Nether':
				embed.title = 'Configuration (Taller Nether)'
				embed.description = f'''
Warning: It is recommended you reset the nether dimension when making this change. In currently loaded chunks, all space above y256 will be the Plains biome.
- Go to [this](https://github.com/Apollounknowndev/pack-library/tree/main/nether-build-height) link, which will bring you to two datapacks that raise the nether build height to 384: One for 1.18.1 and before, one for 1.18.2 and above. Download the one you need.
- Install it onto the world you want to have the taller nether as a datapack. __Load order with Amplified Nether/Incendium does not matter.__
(Special thanks to **Apollo** for this tutorial and datapack)
'''

			case 'Adjusted Continent Size':
				embed.title = 'Configuration (Adjusted Continent Size)'
				embed.description = f"""
This tutorial (graciously provided by **Apollo**) will show you how to adjust continent size with the Continents project.
- Unzip Continents and open the `Continents/data/minecraft/worldgen/density_function/overworld/` folder.
- Open `base_continents.json`. You should see this:
```json
{{
	"type": "add",
	"argument1":{{
		"argument": {{
			"xz_scale": 0.13,
			"y_scale": 0.0,
			"noise": "minecraft:continentalness",
			"shift_x": "minecraft:shift_x",
			"shift_y": 0.0,
			"shift_z": "minecraft:shift_z",
			"type": "minecraft:shifted_noise"
		}},
		"type": "minecraft:flat_cache"
	}},
	"argument2":"continents:continent_bias"
}}
```
- To increase the continent sizes, lower the `xz_scale` value. Halving = 4x larger continents.
- To decrease the continent sizes, raise the `xz_scale` value. Doubling = 4x smaller continents.
- Do not change anything else!
- Zip it up and enjoy! Keep in mind that this has __zero__ impact on the spawn island.
				"""

			case 'Resized Continents Spawn Island':
				embed.title = 'Configuration (Resized Continents Spawn Island)'
				embed.description = f"""
- Open the mod/datapack files and navigate to `data/continents/worldgen/density_function/centroid/`.
- Open `spawn_island.json`. The 5th line of the file should be this:
```json
"argument1": 0.25,
```
Only change this value, __do not touch anything else__. Smaller values = larger biomes. A value of 0.5 leads to a 4x smaller spawn island, and a value of 0.125 leads to a 4x larger spawn island.
				"""
			
		await interaction.response.edit_message(embed=embed)

class Config(discord.ui.View):
	def __init__(self):
		super().__init__(timeout=None)
		self.add_item(ConfigMenu())

class ServerMenu(discord.ui.Select):
	def __init__(self):
		options = [
			discord.SelectOption(label='Normal Install Method'),
			discord.SelectOption(label='Install Method 1.19.3+ ONLY')
		]
		super().__init__(placeholder='Select a method...', min_values=1, max_values=1, options=options)
	
	async def callback(self, interaction: discord.Interaction):
		embed = interaction.message.embeds[0]
		
		match self.values[0]:
			case 'Normal Install Method':
				embed.title = 'Normal Install Method'
				embed.description = '''
This **will** reset your dimension(s) - you should only do this on a new world, or if you're okay with resetting! Pick your favorite server software (Fabric, Paper, etc) since this method will work on all of them, whether you\'re using a hosting service or not.

**1.** If using datapacks (ends in `.zip`), put them all in the `world/datapacks` folder. If using mods (ends in `.jar`), put them all in the `mods` folder.

**2.** Start your server, wait for it to load, then stop it.
				
**3a.** [Terralith/Continents] Inside the `world` folder, delete the entire `region` folder, and *nothing* else.
**3b.** [Incendium/Amplified Nether] Inside the nether folder, delete **__only__** the `region` folder, and **__nothing__** else. On Spigot/Paper, the nether folder is `world_nether/DIM-1`, and it\'s `world/DIM-1` on Fabric/Vanilla.
**3c.** [Nullscape] Inside the end folder, delete **__only__** the `region` folder, and **__nothing__** else. On Spigot/Paper, the end folder is `world_the_end/DIM1`, and it\'s `world/DIM1` on Fabric/Vanilla.
				
**4.** Start your server again, and enjoy!
				
Note: *You can add Structory to an already generated world - the structures will only generate in new chunks, though.
				'''

			case 'Install Method 1.19.3+ ONLY':
				embed.title = 'Install Method 1.19.3+ ONLY'
				embed.description = '''
**__Warning__**: this method works on **1.19.3+ ONLY!** It will __not__ work on 1.19.2 or lower. If you are on 1.19.2 or lower, select the "Normal Install Method" in the select menu below instead. If you use this method, and it does not work, try the Normal method.
				
Pick your favorite server software (Fabric, Paper, etc), since this method will work on all of them.
				
**1.** __Do not__ start your server at all. If you are using a server host and they have already generated your `world` folder, this method will **not** work. Same goes for self hosting, and if you already started the server. Swap to "Normal Install Method" immediately.
				
**2a.** [Datapacks (.zip) only] Manually create a `world` folder. Inside that folder, manually create a `datapacks` folder. Insert all your datapacks in that folder.
**2b.** [Mods (.jar) only] Manually create a `mods` folder. Insert all your mods in that folder.
				
**3.** Start your server and enjoy!
				'''

		await interaction.response.edit_message(embed=embed)

class Server(discord.ui.View):
	def __init__(self):
		super().__init__(timeout=None)
		self.add_item(ServerMenu())

class UpdateMenu(discord.ui.Select):
	def __init__(self):
		options = [
			discord.SelectOption(label='Terralith', emoji='🌍'),
			discord.SelectOption(label='Terralith (1.19)', emoji='🌍'),
			discord.SelectOption(label='Incendium', emoji='🔥'),
			discord.SelectOption(label='Nullscape', emoji='🌌'),
			discord.SelectOption(label='Other Stardust Packs', emoji='⭐')
		]
		super().__init__(placeholder='Select a project...', min_values=1, max_values=1, options=options)
	
	async def callback(self, interaction: discord.Interaction):
		embed = interaction.message.embeds[0]
		
		match self.values[0]:
			case 'Terralith':
				embed.title = 'Updating (Terralith)'
				embed.description = '''
- Updating Terralith between minor versions (2.3.x) - for example, 2.3.3 to 2.3.5 - is perfectly fine! You can do so with little to no chunk borders.
- If using the datapack version in 1.18.2, __make sure you use the same seed both times__ from the [Seedfix](https://sawdust.catter1.com/tools/seedfix/) tool. This is the seed you entered into the site the first time (found in the name of the file you downloaded), *not* from `/seed`.
- If updating from Terralith 2.0.x to 2.1.x, check if you have any deserts generated in your world. If so, make sure you generate them all the way, since 2.1.x completely revamped the desert terrain. If you don\'t, you will have ugly chunk borders there.
- Updating from 2.2.x (1.18.2) to 2.3.x (1.19.x)? Click on the Terralith (1.19) option from the Selection Menu.
				'''

			case 'Terralith (1.19)':
				embed.title = 'Updating (Terralith 1.19)'
				embed.description = f'''
**1.** If you used Seedfix, continue. If you downloaded the datapack directly from Planet Minecraft without entering a seed into the Seedfix website, skip to Step **4**.
**2.** Open your `world/level.dat` using <@{Constants.User.MISODE}>\'s [NBT Viewer](https://marketplace.visualstudio.com/items?itemName=Misodee.vscode-nbt) extension for [Visual Studio Code](https://code.visualstudio.com/) or [NBT Explorer](https://minecraft.wiki/w/Tutorials/Programs_and_editors/NBTExplorer).
**3.** In the `level.dat`, change the overworld seed in `Data>WorldGenSettings>dimensions` to the seed displayed in `Data>WorldGenSettings>dimensions>minecraft:overworld>generator>biome_source`. If it is the same, you\'re all good! Do not forget the  "-" if there is any.
**4.** Once that is done, you can replace Terralith 2.x.x with Terralith 2.3.x and start up your world!
				'''

			case 'Incendium':
				embed.title = 'Updating (Incendium)'
				embed.description = '''
- You cannot update Incendium worlds used in 1.17.1 (Incendium 4.0.0) or lower to 1.18.2 (Incendium 5.0.x).
- Updating from 1.18.2 to 1.19 (5.0.x to 5.1.x) is mostly fine!
- Updating to minor versions (5.1.x) works fine - for example, 5.1.2 to 5.1.4.
				'''

			case 'Nullscape':
				embed.title = 'Updating (Nullscape)'
				embed.description = '''
- Updating to minor versions (v1.2.x) works fine.
- If you want to use 1.18.2, ensure you use 1.1.2 **only**. This version is stable, unlike 1.1.1.
- Nullscape 1.19 (v1.2) is different from all other versions, since it is combined into one dimension, like it should! Because of that, you cannot update a 1.18.x Nullscape world (v1.1.1) to 1.19 (v1.2) without completely resetting your end and heavily editing your `level.dat`.
				'''

			case 'Other Stardust Packs':
				embed.title = 'Updating (Other Stardust Packs)'
				embed.description = '''
- Updating between minor and major versions is mostly okay!
- You cannot update Amplified Nether from older versions to 1.18.x or higher.
				'''
		
		await interaction.response.edit_message(embed=embed)

class Update(discord.ui.View):
	def __init__(self):
		super().__init__(timeout=None)
		self.add_item(UpdateMenu())

async def setup(client):
	await client.add_cog(Faq(client))
