import discord
from discord.ext import commands
from discord.ext.commands import has_permissions

class Faq(commands.Cog):
	def __init__(self, client):
		self.client = client

	async def cog_load(self):
		print(f' - {self.__name__} cog loaded.')

	def is_not_pirate():
		def pirate(ctx):
			if ctx.author.get_role(913342465359089684):
				return False
			else:
				return True
		return commands.check(pirate)

	@commands.group(aliases=['q'], invoke_without_command=True, pass_context=True)
	@is_not_pirate()
	async def faq(self, ctx):
		embed = discord.Embed(
			title='FAQ Menu',
			description='Select a category below! There are over 20 FAQs from you to choose from. If you cannot find what you are looking for, or have question regarding an FAQ, feel free to ask in <#869678422014697562>!',
			color=discord.Colour.teal()
		)
		await ctx.send(embed=embed, view=FaqButtons(self.client))

	@faq.command(name='server')
	@is_not_pirate()
	async def server(self, ctx):
		blurb = "Need to install a datapack/mod onto your server?"
		await Questions(self.client).server(ctx, blurb)

	@faq.command(name='ore', aliases=['ores'])
	@is_not_pirate()
	async def ore(self, ctx):
		blurb = "It's basically the Vanilla distribution."
		await Questions(self.client).ore(ctx, blurb)
	
	@faq.command(name='downloads', aliases=['download', 'links'])
	@is_not_pirate()
	async def downloads(self, ctx):
		await Questions(self.client).downloads(ctx)

	@faq.command(name='mods', aliases=['fabric', 'mod'])
	@is_not_pirate()
	async def mods(self, ctx):
		blurb = "Want some Fabric mod and shader recommendations?"
		await Questions(self.client).mods(ctx, blurb)

	@faq.command(name='wiki')
	@is_not_pirate()
	async def wiki(self, ctx):
		blurb = "Stardust Labs has an official wiki on Miraheze!"
		await Questions(self.client).wiki(ctx, blurb)

	@faq.command(name='resource', aliases=['packs'])
	@is_not_pirate()
	async def resource(self, ctx):
		blurb = "Need links for minimap mod biome name fixes, or cool Incendium resource packs?"
		await Questions(self.client).resource(ctx, blurb)

	@faq.command(name='license')
	@is_not_pirate()
	async def lisence(self, ctx):
		blurb = "Curious on what Stardust Labs' license is?"
		await Questions(self.client).lisence(ctx, blurb)

	@faq.command(name='update')
	@is_not_pirate()
	async def update(self, ctx):
		blurb = "Need to update your world?"
		await Questions(self.client).update(ctx, blurb)

	@faq.command(name='seedfix', aliases=['sameseed'])
	@is_not_pirate()
	async def seedfix(self, ctx):
		blurb = "Having trouble getting a different seed with Terralith?"
		await Questions(self.client).seedfix(ctx, blurb)

	@faq.command(name='config', aliases=['configuration'])
	@is_not_pirate()
	async def config(self, ctx):
		blurb = "There is no configuration file, but you can do *some* stuff with the datapacks."
		await Questions(self.client).config(ctx, blurb)

	@faq.command(name='seedtype', aliases=['seed', 'slime'])
	@is_not_pirate()
	async def seedtype(self, ctx):
		blurb = "Until 1.19 releases, there are two types of seeds in your custom worlds."
		await Questions(self.client).seedtype(ctx, blurb)

	@faq.command(name='tlauncher', aliases=['pirate', 'illegal'])
	async def tlauncher(self, ctx):
		await Questions(self.client).tlauncher(ctx)

	@faq.command(name='compat', aliases=['compatibility'])
	@is_not_pirate()
	async def compat(self, ctx):
		blurb = "What packs/mods are compatable with what?"
		await Questions(self.client).compat(ctx, blurb)

	@faq.command(name='ids', aliases=['id', 'list'])
	@is_not_pirate()
	async def ids(self, ctx):
		blurb = "Need a list of all of Terralith's Biome IDs?"
		await Questions(self.client).ids(ctx, blurb)

	@faq.command(name='support', aliases=['patreon', 'boost', 'patron', 'kofi', 'donate'])
	@is_not_pirate()
	async def support(self, ctx):
		await Questions(self.client).support(ctx)

	@faq.command(name='remove')
	@is_not_pirate()
	async def remove(self, ctx):
		await Questions(self.client).remove(ctx)

	@faq.command(name='realms')
	@is_not_pirate()
	async def realms(self, ctx):
		blurb = "Realms doesn't work with custom worldgen."
		await Questions(self.client).realms(ctx)

	@faq.command(name='maps', aliases=['map'])
	@is_not_pirate()
	async def maps(self, ctx):
		blurb = "If opening chests crashes your server, you might want to disable the Traveller\'s Maps."
		await Questions(self.client).maps(ctx, blurb)

	@faq.command(name='animals', aliases=['passive'])
	@is_not_pirate()
	async def animals(self, ctx):
		blurb = "Passive animal spawns are Vanilla."
		await Questions(self.client).animals(ctx, blurb)

	@faq.command(name='wwoo', aliases=['WWOO'])
	@is_not_pirate()
	async def wwoo(self, ctx):
		await Questions(self.client).wwoo(ctx)

	@faq.command(name='pregen', aliases=['chunky'])
	@is_not_pirate()
	async def pregen(self, ctx):
		blurb = "Terralith only causes lag if you do not pregen your world."
		await Questions(self.client).pregen(ctx, blurb)

	@faq.command(name='color', aliases=['colors', 'grass', 'leaf', 'leaves'])
	@is_not_pirate()
	async def color(self, ctx):
		blurb = "Terralith foliage colors are a vanilla mechanic."
		await Questions(self.client).color(ctx, blurb)

	@faq.command(name='packdiff', aliases=['vs', 'nether'])
	@is_not_pirate()
	async def packdiff(self, ctx):
		await Questions(self.client).packdiff(ctx)

class FaqButtonsMenu(discord.ui.Select):
	def __init__(self, client):
		self.client = client
		self.channel = self.client.get_channel(923571915879231509)
		options = [
        	discord.SelectOption(label='Terralith', description='FAQs relating to Terralith specifically', emoji='🟩'),
        	discord.SelectOption(label='Resources', description='Helpful websites and information', emoji='⬛'),
			discord.SelectOption(label='Troubleshooting', description='Guides and more to fix issues', emoji='🟥'),
			discord.SelectOption(label='Stardust Labs', description='Official Stardust Labs content', emoji='🟦')
		]
		super().__init__(placeholder='Select an FAQ category...', min_values=1, max_values=1, options=options)

	async def callback(self, interaction: discord.Interaction):
		msg = interaction.message
		embed = interaction.message.embeds[0]
		self.view.clear_items()
		self.view.add_item(FaqButtonsMenu(self.client))
		if self.values[0] == 'Terralith':
			embed.title = 'FAQ Menu (Terralith)'
			embed.description = '**!q Prompts:**\nOre Distribution - [`ore`, `ores`]\nSeed Types - [`seedtype`, `seed`, `slime`]\nBiome IDs - [`ids`, `id`, `list`]\nRemoving Terralith - [`remove`]\nTraveller\'s Maps - [`maps`, `map`]\nPassive Animals - [`animals`, `passive`]\nPregen - [`pregen`, `chunky`]\nFoliage Colors - [`color`, `colors`, `leaf`, `leaves`, `grass`]'

			self.view.add_item(QOre(self.client))
			self.view.add_item(QSeedtype(self.client))
			self.view.add_item(QIds(self.client))
			self.view.add_item(QRemove(self.client))
			self.view.add_item(QMaps(self.client))
			self.view.add_item(QAnimals(self.client))
			self.view.add_item(QPregen(self.client))
			self.view.add_item(QColor(self.client))
		elif self.values[0] == 'Resources':
			embed.title = 'FAQ Menu (Resources)'
			embed.description = '**!q Prompts:**\nDownloads - [`downloads`, `download`, `links`]\nMods - [`mods`, `mod`, `fabric`]\nWiki - [`wiki`]\nResource Packs - [`resource`, `packs`]\nConfiguration - [`config`, `configuration`],\nIncendium vs Amplified Nether - [`packdiff`, `vs`, `nether`]'
			
			self.view.add_item(QDownloads(self.client))
			self.view.add_item(QMods(self.client))
			self.view.add_item(QWiki(self.client))
			self.view.add_item(QResource(self.client))
			self.view.add_item(QConfig(self.client))
			self.view.add_item(QPackdiff(self.client))
		elif self.values[0] == 'Troubleshooting':
			embed.title = 'FAQ Menu (Troubleshooting)'
			embed.description = '**!q Prompts:**\nServer - [`server`]\nUpdating - [`update`]\nSeedFix - [`seedfix`, `sameseed`]\nTLauncher - [`tlauncher`, `pirate`, `illegal`]\nCompatibility - [`compat`, `compatibility`]\nRealms - [`realms`]\nWWOO - [`wwoo`, `WWOO`]'
			
			self.view.add_item(QServer(self.client))
			self.view.add_item(QUpdate(self.client))
			self.view.add_item(QSeedfix(self.client))
			self.view.add_item(QTlauncher(self.client))
			self.view.add_item(QCompat(self.client))
			self.view.add_item(QRealms(self.client))
			self.view.add_item(QWwoo(self.client))
		elif self.values[0] == 'Stardust Labs':
			embed.title = 'FAQ Menu (Stardust Labs)'
			embed.description = '**!q Prompts:**\nLicense - [`license`]\nSupport Us! - [`support`, `donate`, `patreon`, `patron`, `kofi`, `boost`]'
			
			self.view.add_item(QLisence(self.client))
			self.view.add_item(QSupport(self.client))

		await msg.edit(embed=embed, view=self.view)

### TERRALITH ###
class QOre(discord.ui.Button):
	def __init__(self, client):
		self.client = client
		super().__init__(label='Ore Distributon', style=discord.ButtonStyle.success)

	async def callback(self, interaction: discord.Interaction):
		blurb = "It's essentially the Vanilla ore distribution."
		await Questions(self.client).ore(interaction, blurb)

class QSeedtype(discord.ui.Button):
	def __init__(self, client):
		self.client = client
		super().__init__(label='Seed Types', style=discord.ButtonStyle.success)

	async def callback(self, interaction: discord.Interaction):
		blurb = "In 1.18.2 and lower, there are two types of seeds in your custom worlds (not applicable in 1.19)."
		await Questions(self.client).seedtype(interaction, blurb)

class QIds(discord.ui.Button):
	def __init__(self, client):
		self.client = client
		super().__init__(label='Biome IDs', style=discord.ButtonStyle.success)

	async def callback(self, interaction: discord.Interaction):
		blurb = "Need a list of all of Terralith's Biome IDs?"
		await Questions(self.client).ids(interaction, blurb)

class QRemove(discord.ui.Button):
	def __init__(self, client):
		self.client = client
		super().__init__(label='Removing Terralith', style=discord.ButtonStyle.success)

	async def callback(self, interaction: discord.Interaction):
		await Questions(self.client).remove(interaction)

class QMaps(discord.ui.Button):
	def __init__(self, client):
		self.client = client
		super().__init__(label='Traveller\'s Maps', style=discord.ButtonStyle.success)

	async def callback(self, interaction: discord.Interaction):
		blurb = "If opening chests crashes your server, you might want to disable the Traveller\'s Maps."
		await Questions(self.client).maps(interaction, blurb)

class QAnimals(discord.ui.Button):
	def __init__(self, client):
		self.client = client
		super().__init__(label='Passive Animals', style=discord.ButtonStyle.success)

	async def callback(self, interaction: discord.Interaction):
		blurb = "Passive animal spawns are Vanilla."
		await Questions(self.client).animals(interaction, blurb)

class QPregen(discord.ui.Button):
	def __init__(self, client):
		self.client = client
		super().__init__(label='Pregen', style=discord.ButtonStyle.success)

	async def callback(self, interaction: discord.Interaction):
		blurb = "Terralith only causes lag if you do not pregen your world."
		await Questions(self.client).pregen(interaction, blurb)

class QColor(discord.ui.Button):
	def __init__(self, client):
		self.client = client
		super().__init__(label='Foliage Colors', style=discord.ButtonStyle.success)

	async def callback(self, interaction: discord.Interaction):
		blurb = "Terralith foliage colors are a vanilla mechanic."
		await Questions(self.client).color(interaction, blurb)

### RESOURCES ###
class QDownloads(discord.ui.Button):
	def __init__(self, client):
		self.client = client
		super().__init__(label='Downloads', style=discord.ButtonStyle.secondary)

	async def callback(self, interaction: discord.Interaction):
		await Questions(self.client).downloads(interaction)

class QMods(discord.ui.Button):
	def __init__(self, client):
		self.client = client
		super().__init__(label='Mods', style=discord.ButtonStyle.secondary)

	async def callback(self, interaction: discord.Interaction):
		blurb = "Want some Fabric mod and shader recommendations?"
		await Questions(self.client).mods(interaction, blurb)

class QWiki(discord.ui.Button):
	def __init__(self, client):
		self.client = client
		super().__init__(label='Wiki', style=discord.ButtonStyle.secondary)

	async def callback(self, interaction: discord.Interaction):
		blurb = "Stardust Labs has an official wiki on Miraheze!"
		await Questions(self.client).wiki(interaction, blurb)

class QResource(discord.ui.Button):
	def __init__(self, client):
		self.client = client
		super().__init__(label='Resource Packs', style=discord.ButtonStyle.secondary)

	async def callback(self, interaction: discord.Interaction):
		blurb = "Need links for minimap mod biome name fixes, or cool Incendium resource packs?"
		await Questions(self.client).resource(interaction, blurb)

class QPackdiff(discord.ui.Button):
	def __init__(self, client):
		self.client = client
		super().__init__(label='Incendium vs Amp Nether', style=discord.ButtonStyle.secondary)

	async def callback(self, interaction: discord.Interaction):
		await Questions(self.client).packdiff(interaction)

class QConfig(discord.ui.Button):
	def __init__(self, client):
		self.client = client
		super().__init__(label='Configuration', style=discord.ButtonStyle.secondary)

	async def callback(self, interaction: discord.Interaction):
		blurb = "There is no configuration file, but you can do *some* stuff with the datapacks."
		await Questions(self.client).config(interaction, blurb)

### TROUBLESHOOTING ###
class QServer(discord.ui.Button):
	def __init__(self, client):
		self.client = client
		super().__init__(label='Server', style=discord.ButtonStyle.danger)

	async def callback(self, interaction: discord.Interaction):
		blurb = "Need to install a datapack/mod onto your server?"
		await Questions(self.client).server(interaction, blurb)

class QUpdate(discord.ui.Button):
	def __init__(self, client):
		self.client = client
		super().__init__(label='Updating', style=discord.ButtonStyle.danger)

	async def callback(self, interaction: discord.Interaction):
		blurb = "Need to update your world?"
		await Questions(self.client).update(interaction, blurb)

class QSeedfix(discord.ui.Button):
	def __init__(self, client):
		self.client = client
		super().__init__(label='SeedFix', style=discord.ButtonStyle.danger)

	async def callback(self, interaction: discord.Interaction):
		blurb = "Having trouble getting a different seed with Terralith?"
		await Questions(self.client).seedfix(interaction, blurb)

class QTlauncher(discord.ui.Button):
	def __init__(self, client):
		self.client = client
		super().__init__(label='TLauncher', style=discord.ButtonStyle.danger)

	async def callback(self, interaction: discord.Interaction):
		await Questions(self.client).tlauncher(interaction)

class QCompat(discord.ui.Button):
	def __init__(self, client):
		self.client = client
		super().__init__(label='Compatibility', style=discord.ButtonStyle.danger)

	async def callback(self, interaction: discord.Interaction):
		blurb = "What packs/mods are compatable with what?"
		await Questions(self.client).compat(interaction, blurb)

class QRealms(discord.ui.Button):
	def __init__(self, client):
		self.client = client
		super().__init__(label='Realms', style=discord.ButtonStyle.danger)

	async def callback(self, interaction: discord.Interaction):
		await Questions(self.client).realms(interaction)

class QWwoo(discord.ui.Button):
	def __init__(self, client):
		self.client = client
		super().__init__(label='WWOO', style=discord.ButtonStyle.danger)

	async def callback(self, interaction: discord.Interaction):
		await Questions(self.client).wwoo(interaction)

### STARDUST LABS ###
class QLisence(discord.ui.Button):
	def __init__(self, client):
		self.client = client
		super().__init__(label='License', style=discord.ButtonStyle.primary)

	async def callback(self, interaction: discord.Interaction):
		blurb = "Curious on what Stardust Labs' license is?"
		await Questions(self.client).lisence(interaction, blurb)

class QSupport(discord.ui.Button):
	def __init__(self, client):
		self.client = client
		super().__init__(label='Support Us!', style=discord.ButtonStyle.primary)

	async def callback(self, interaction: discord.Interaction):
		await Questions(self.client).support(interaction)

### MAIN CONTENT CLASS ###
class Questions():
	def __init__(self, client):
		self.client = client
		self.channel = self.client.get_channel(923571915879231509)

	async def point(self, ctx, x, blurb):
		if ctx.channel != self.channel:
			jumpmsg = f"{blurb} Click the button below to see more details!"
			await ctx.send(jumpmsg, view=Pointer(x))

	async def server(self, ctx, blurb):
		embed = discord.Embed(
			title='FAQ - Server Installation (Recommended)',
			description='Pick your favorite server software (Fabric, Paper, etc), as this method will work on all of them; even if you\'re using a hosting service, or not!\n\n**1a.** If using datapacks (end in `.zip`), put them all in the `world/datapacks` folder.\n**1b.** If using mods (end in `.jar`), put them all in the `mods` folder.\n\n**2.** Start your server, wait for it to load, then stop it.\n\n**3a.** [Terralith only] Inside the `world` folder, delete the entire `region` folder, and *nothing* else.\n**3b.** [Incendium/Amplified Nether only] Inside the nether folder, delete the entire `region` folder, and *nothing* else. On Spigot/Paper, the nether folder is `world_the_nether`, and it\'s `world/DIM-1` on Fabric/Vanilla.\n\n**4.** Start your server again, and enjoy!',
			color=discord.Colour.teal()
		)
		x = await self.channel.send(embed=embed, view=Server())
		await self.point(ctx, x, blurb)

	async def ore(self, ctx, blurb):
		embed = discord.Embed(
			title='FAQ - Ore Distribution',
			description='Terralith uses the normal Vanilla 1.19 ore distribution. However, there are some places that have extra ores than others: emeralds in Emerald Peaks, redstone in Scarlet Mountains, copper in Dripstone Caves, few exposed diamonds in Skylands, and a couple other *secret* places.',
			color=discord.Colour.teal()
		)
		file = discord.File("assets/ore.jpeg", filename="image.jpeg")
		embed.set_image(url="attachment://image.jpeg")
		x = await self.channel.send(file=file, embed=embed)
		await self.point(ctx, x, blurb)

	async def downloads(self, ctx):
		await ctx.send('Find downloads of all versions and projects here: <#900598465430716426>')
	
	async def mods(self, ctx, blurb):
		embed = discord.Embed(
			title='FAQ - Fabric Performance Mods',
			description='Almost *all* of these mods require Fabric API. Select a category below for links and descriptions of Fabric mods to use.',
			color=discord.Colour.teal()
		)
		embed.set_footer(text='List compiled by NordicGamerFE and catter1', icon_url=self.client.get_user(260929689126699008).avatar)
		x = await self.channel.send(embed=embed, view=Mods())
		await self.point(ctx, x, blurb)

	async def wiki(self, ctx, blurb):
		embed = discord.Embed(
			title='FAQ - Important Wiki Links',
			description=' - Visit the [main page](https://stardustlabs.miraheze.org/wiki/Main_page)\n - Learn how to [contribute](https://stardustlabs.miraheze.org/wiki/Contributing) to the wiki\n - Get a [list of all Terralith biomes](https://stardustlabs.miraheze.org/wiki/Terralith_biomes)\n - Find information about [Incendium\'s custom items](https://stardustlabs.miraheze.org/wiki/Incendium_custom_items)\n - Check out project [compatabilities](https://stardustlabs.miraheze.org/wiki/Terralith_compatibilities)\n - Find a few [troubleshooting](https://stardustlabs.miraheze.org/wiki/Troubleshooting) links',
			color=discord.Colour.teal()
		)
		x = await self.channel.send(embed=embed)
		await self.point(ctx, x, blurb)

	async def resource(self, ctx, blurb):
		embed = discord.Embed(
			title='FAQ - Resource Packs',
			description='When using a minimap or any other mod that displays biomes, Starduts datapack biomes may appear very long. <@212447019296489473> made this cool resource pack that fixes it! Find more information here: <#915435433360490507>.\n\nIf you want some resource packs for Incendium, check out <@234748321258799104>\'s resource packs: Biome Lava, and Incendium\'s Optional Resourcepack Remix (IORR)! They are very cool, and you can find more information at their download pages linked below.',
			color=discord.Colour.teal()
		)
		file = discord.File("resources/Stardust_Omni-Biome_Name_Fix_v1.1.zip", filename="Stardust_Omni-Biome_Name_Fix_v1.1.zip")
		x = await self.channel.send(embed=embed, file=file, view=Resource())
		await self.point(ctx, x, blurb)

	async def lisence(self, ctx, blurb):
		embed = discord.Embed(
			title='FAQ - License',
			description='You can find the license inside Stardust Labs datapacks; it is also attached to this FAQ. It applies to *all* projects created by Stardust Labs. Read it for important information, especially about modifying Stardust Labs\' projects.',
			color=discord.Colour.teal()
		)
		file = discord.File("resources/license.txt", filename="license.txt")
		x = await self.channel.send(embed=embed, file=file)
		await self.point(ctx, x, blurb)

	async def update(self, ctx, blurb):
		embed = discord.Embed(
			title='FAQ - Updating',
			description='Make sure to always take a backup before updating! Select a datapack from the selection menu below to see information on updating those datapacks.',
			color=discord.Colour.teal()
		)
		x = await self.channel.send(embed=embed, view=Update())
		await self.point(ctx, x, blurb)

	async def seedfix(self, ctx, blurb):
		embed = discord.Embed(
			title='FAQ - SeedFix',
			description='There is a [Minecraft bug](https://bugs.mojang.com/browse/MC-195717) that makes all worldgen datapacks use the same seed, but it applies **only** in 1.18.2 and lower. To use the datapack version of Terralith in 1.18.x, download a version from the SeedFix website, which allows you to input your own seed. The mod versions have SeedFix built in, so you can use seeds as normal.',
			color=discord.Colour.teal()
		)
		x = await self.channel.send(embed=embed, view=Seedfix())
		await self.point(ctx, x, blurb)
	
	async def config(self, ctx, blurb):
		embed = discord.Embed(
			title='FAQ - Configuration',
			description='There is **no configuration file** for datapacks (custom world settings do not work either). That said, if you want to modify how the packs work, you\'ll have to modify the code inside the datapack. Do keep in mind the license (`!faq license`), which prohibits you from distributing modified versions of the projects. Select a configuration from the selection menu below.',
			color=discord.Colour.teal()
		)
		x = await self.channel.send(embed=embed, view=Config())
		await self.point(ctx, x, blurb)

	async def seedtype(self, ctx, blurb):
		embed = discord.Embed(
			title='FAQ - Seed Types',
			description='Due to a [Minecraft bug](https://bugs.mojang.com/browse/MC-195717) in 1.18.2 and lower, worldgen datapacks are forced to use a set seed, hence SeedFix. Because of this, prior to 1.19, there are two "types" of seeds when dealing with worldgen *datapacks*. To prepare for when it gets fixed, you should - when using the datapack - set the world seed the same as the terrain seed.\n\n - The **world seed** is the seed you get from looking at `/seed`, `level.dat`, or `server.properties`. This seed effects how __structures__ generate and where __slime chunks__ are.\n\n - The **terrain seed** is the seed found in Terralith\'s `overworld.json` file (it\'s what SeedFix changes!). This seed affects how terrain generates and where biomes are.',
			color=discord.Colour.teal()
		)
		x = await self.channel.send(embed=embed)
		await self.point(ctx, x, blurb)

	async def tlauncher(self, ctx):
		embed = discord.Embed(
			title='FAQ - TLauncher Support',
			description='Are you illegally pirating Minecraft? We do not support this behavior at Stardust Labs. Stop immediately. But if you will not heed our advice, follow this tutorial.',
			color=discord.Colour.dark_teal()
		)
		await ctx.send(embed=embed, view=Tlauncher())

	async def compat(self, ctx, blurb):
		embed = discord.Embed(
			title='FAQ - Project compatibility',
			description='A couple key compatabilities with Stardust Labs\' projects. You can find an in depth compatibility table on the wiki!\n\n- Terralith 2.3.x can work with all Stardust packs released for 1.19 \n- Terralith 2.2.x can work with Incendium 5.0 and Nullscape 1.1.1\n - Terralith 2.0 can work with Cave Tweaks, Amplified Nether, and Nullscape\n - Terralith Legacy (1.17) can work with Incendium 4.0 and Nullscape Legacy\n - Incendium and Amplified Nether do **not** work together in all versions\n - Terralith 2.0+ works with Biomes O\' Plenty and BYG if Terablender is present\n - Better Nether works with Amplified Nether, but not Incendium (1.18.2)\n - Nullscape (1.19 only) works with Better End, as well as all Stardust packs\n - Structory works with Terralith, and all other Stardust packs',
			color=discord.Colour.teal()
		)
		x = await self.channel.send(embed=embed, view=Compat())
		await self.point(ctx, x, blurb)

	async def ids(self, ctx, blurb):
		embed = discord.Embed(
			title='FAQ - Terralith ID List',
			description='Last updated for Terralith v2.3.2',
			color=discord.Colour.teal()
		)
		file = discord.File("resources/funny_biomes.txt", filename="terralith_id_list.txt")
		x = await self.channel.send(embed=embed, file=file)
		await self.point(ctx, x, blurb)

	async def support(self, ctx):
		embed = discord.Embed(
			title='FAQ - Supporting Stardust Labs',
			description='Want to support Stardust Labs and get some cool perks? If so, thank you!\n\n**Bisect Hosting** - Stardust Labs is partnered with Bisect Hosting! Use code `STARDUST` to get 25% off your first month, as well as to earn the Supporter role, which gives you access to the Supporter Showcase - access to small projects and sneak peeks.\n**Server Boosting** - By boosting the Discord server, you also gain access to the Suporter Showcase!\n**Patreon** - Subscribe to one of four tiers to support us directly! Perks range from access to a patron-only chat to early access to main pack updates.\n**Ko-Fi** - Don\'t want to do a subscription? Feel free to drop a 1-time donation instead!',
			color=discord.Colour.teal()
		)
		await ctx.send(embed=embed, view=Support())

	async def remove(self, ctx):
		await ctx.send("**DO NOT REMOVE TERRALITH: YOUR WORLD WILL NOT LOAD!**")

	async def realms(self, ctx):
		embed = discord.Embed(
			title='FAQ - Using Realms',
			description='Unfortuantely, since worldgen is considered an experimental feature by Mojang, you cannot use any worldgen datapack on a Realm. Use a better hosting service. Stardust Labs is partnered with Bisect Hosting - check them out instead!',
			color=discord.Colour.teal()
		)
		await ctx.send(embed=embed, view=Realms())

	async def maps(self, ctx, blurb):
		embed = discord.Embed(
			title='FAQ - Disabling Traveller\'s Maps',
			description='If your world/server is crashing upon opening a chest in a Terralith structure, it is probably due to the Traveller\'s Maps. You can disable them be using these two commands:\n`/scoreboard objectives add tr.disable_maps dummy`\n`/scoreboard players set %DISABLE_MAP tr.disable_maps 1`\n\nIf you want to check if it worked, you should get no item after doing this command:\n`/loot give @p loot terralith:random_traveler_map`',
			color=discord.Colour.teal()
		)
		x = await self.channel.send(embed=embed)
		await self.point(ctx, x, blurb)

	async def animals(self, ctx, blurb):
		embed = discord.Embed(
			title='FAQ - Passive Animal Spawns',
			description='It is a Vanilla mechanic that passive mobs only spawn on grass blocks (and similar), on less-spiky terrain, and closer to sea level. Because Terralith is more mountainous than Vanilla, and a lot of biomes don\'t primarily use grass, you will tend to find less passive mobs.\n\nAlthough is is not possible to change passive mob spawning conditions, more recent versions of Terralith have increased the spawn rates on the places they *are* able to spawn on.',
			color=discord.Colour.teal()
		)
		x = await self.channel.send(embed=embed)
		await self.point(ctx, x, blurb)

	async def wwoo(self, ctx):
		embed = discord.Embed(
			title='FAQ - William Wyther\'s Overhauled Overworld',
			description='WWOO has recently released for 1.18.1. Unfortunately, it is not compatible with Terralith due to surface rules being mutually exclusive, and multiple other data format issues preventing compatibility.',
			color=discord.Colour.teal()
		)
		await ctx.send(embed=embed)

	async def pregen(self, ctx, blurb):
		embed = discord.Embed(
			title='FAQ - Pregenerating',
			description='Terralith will only cause lag to your world when chunks are generated for the very first time. Because of this, pregenning your world is highly encouraged. One of the only and best pregen mods/plugins is Chunky.\n\nClick the buttons below for download links. Check out their respective websites for instructions on how to use it.',
			color=discord.Colour.teal()
		)
		x = await self.channel.send(embed=embed, view=Pregen())
		await self.point(ctx, x, blurb)

	async def color(self, ctx, blurb):
		embed = discord.Embed(
			title='FAQ - Foliage Colors',
			description='Terralith uses a variety of grass and leaf colors, but does not use a resource pack. Instead, this is actually a Vanilla mechanic. In Vanilla swamps, the water is browner, and the leaves and grass is a dull/dark green. In Jungles and Mooshroom Islands, grass is a vibrant green. This mechanic is what Terralith uses, but instead of doing different shades of green, Terralith will use the mechanic for all colors - red leaves in Forested Highlands, blue grass in Mirage Isles, pink leaves in Sakura Groves, and much more.',
			color=discord.Colour.teal()
		)
		x = await self.channel.send(embed=embed)
		await self.point(ctx, x, blurb)

	async def packdiff(self, ctx):
		embed = discord.Embed(
			title='FAQ - Incendium vs. Amplified Nether',
			description='Incendium and Amplified Nether are very different packs, and are **not** compatible with each other.\n**-** __Amplified Nether__ is a Vanilla nether, with 3D biomes, cool terrain shapes, and an extended height.\n**-** __Incendium__ has what Amplified Nether has, but with custom mobs, items, biomes, structures, and a cool boss. (Although, the Incendium height extension is not quite as Amplified Nether\'s.)',
			color=discord.Colour.teal()
		)
		await ctx.send(embed=embed)

class Pointer(discord.ui.View):
	def __init__(self, x):
		super().__init__()
		self.add_item(discord.ui.Button(label='View FAQ', emoji='❓', url=x.jump_url))

### BUTTONS ###
class Seedfix(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='SeedFix Website', emoji='<:seedfix:917599175259070474>', url='https://seedfix.stardustlabs.net/'))
		self.add_item(discord.ui.Button(label='Mod Download', emoji='<:curseforge:962397090732970004>', url='https://www.curseforge.com/minecraft/mc-mods/terralith'))

class Tlauncher(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Tutorial', emoji='🏴‍☠️', url='https://static.miraheze.org/stardustlabswiki/8/80/How_to_install_Terralith_1.16.4_to_TLauncher_1.mp4'))

class Compat(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Compatibility Table', emoji='<:miraheze:890077957069111316>', url='https://stardustlabs.miraheze.org/wiki/Terralith_compatibilities'))

class Resource(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Biome Lava', url='https://www.planetminecraft.com/texture-pack/biome-lava-1-18/'))
		self.add_item(discord.ui.Button(label='IORR', url='https://github.com/Stardust-Labs-MC/downloads-library/tree/main/Incendium/Resource%20Pack'))

class Support(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Bisect Hosting', emoji='<:bisect:962410759462203462>', url='https://bisecthosting.com/stardust'))
		self.add_item(discord.ui.Button(label='Patreon', emoji='<:patreon:962411326628581376>', url='https://www.patreon.com/stardustlabs'))
		self.add_item(discord.ui.Button(label='Ko-Fi', emoji='<:kofi:962411326666334259>', url='https://ko-fi.com/stardustlabs'))

class Realms(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Bisect Hosting', emoji='<:bisect:962410759462203462>', url='https://bisecthosting.com/stardust'))

class Pregen(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(discord.ui.Button(label='Chunky (Fabric)', emoji='<:fabric:962456210773262346>', url='https://www.curseforge.com/minecraft/mc-mods/chunky-pregenerator'))
		self.add_item(discord.ui.Button(label='Chunky (Forge)', emoji='<:curseforge:962397090732970004>', url='https://www.curseforge.com/minecraft/mc-mods/chunky-pregenerator-forge'))
		self.add_item(discord.ui.Button(label='Chunky (Paper/Spigot)', emoji='<:spigot:964945252890861649>', url='https://www.spigotmc.org/resources/chunky.81534/'))

### SELECT MENUS ###
class ServerMenu(discord.ui.Select):
	def __init__(self):
		options = [
        	discord.SelectOption(label='Recommended', description='Easiest method for datapack installation'),
        	discord.SelectOption(label='Singleplayer', description='Alternate, more complicated method')
		]
		super().__init__(placeholder='Select another method...', min_values=1, max_values=1, options=options)
		
	async def callback(self, interaction: discord.Interaction):
		msg = interaction.message
		embed = interaction.message.embeds[0]
		if self.values[0] == 'Recommended':
			embed.title = 'FAQ - Server Installation (Recommended)'
			embed.description = 'Pick your favorite server software (Fabric, Paper, etc), as this method will work on all of them; even if you\'re using a hosting service, or not!\n\n**1a.** If using datapacks (end in `.zip`), put them all in the `world/datapacks` folder.\n**1b.** If using mods (end in `.jar`), put them all in the `mods` folder.\n\n**2.** Start your server, wait for it to load, then stop it.\n\n**3a.** [Terralith only] Inside the `world` folder, delete the entire `region` folder, and *nothing* else.\n**3b.** [Incendium/Amplified Nether only] Inside the nether folder, delete the entire `region` folder, and *nothing* else. On Spigot/Paper, the nether folder is `world_the_nether`, and it\'s `world/DIM-1` on Fabric/Vanilla.\n\n**4.** Start your server again, and enjoy!'
		elif self.values[0] == 'Singleplayer':
			embed.title = 'FAQ - Server Installation (Alternate)'
			embed.description = 'Pick your favorite server software (Fabric, Paper, etc), as this method will work on all of them; even if you\'re using a hosting service, or not!\n\n**1.** Create a __singleplayer world__ with the datapacks/mods you are using. Make sure you add the datapacks using the __datapack button.__ DO **NOT** add them after you create the world.\n**2.** As soon as you load the overworld, leave the game.\n**3.** On your server, delete the `world`, `the_nether`, and `the_end` folders.\n**4.** Find the folder of the entire singleplayer world (it is the folder that contains `region` folder).\n**5.** Rename that folder to `world`, and move it to your server.\n**6.** Start up your server.'
		await msg.edit(embed=embed)

class Server(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ServerMenu())

class ConfigMenu(discord.ui.Select):
	def __init__(self):
		options = [
        	discord.SelectOption(label='Bigger Biomes', description='How to increase biome size in Terralith', emoji='🌍'),
        	discord.SelectOption(label='Smaller Biomes', description='How to decrease biome size in Terralith', emoji='🌍'),
			discord.SelectOption(label='Remove Biomes', description='How to remove/replace biomes in Terralith', emoji='🌍'),
			discord.SelectOption(label='Taller Nether', description='How to add space above bedrock in Amplified Nether', emoji='🔥'),
			discord.SelectOption(label='Biome Layout', description='How to change Terralith\'s biome layout', emoji='🌍'),
			discord.SelectOption(label='Amplified Terrain', description='Super tall mountains in Terralith?', emoji='🌍')
		]
		super().__init__(placeholder='Select a configuration...', min_values=1, max_values=1, options=options)
		
	async def callback(self, interaction: discord.Interaction):
		msg = interaction.message
		embed = interaction.message.embeds[0]
		if self.values[0] == 'Bigger Biomes':
			embed.title = 'FAQ - Configuration (Bigger Biomes)'
			embed.description = 'Currently, the Terralith biome sizes are on average slightly larger than Vanilla, but *can* be huge. If you still want larger biomes:\n - Unzip Terralith and open the `Terralith/data/minecraft/worldgen/noise/` folder.\n - Subtract **1** from all instances of `firstOctave` in the `erosion`, `continentalness`, `temperature`, and `vegetation` files.\n - Do *not* edit the `ridge` file.'
		elif self.values[0] == 'Smaller Biomes':
			embed.title = 'FAQ - Configuration (Smaller Biomes)'
			embed.description = 'Keep in mind that doing this will make the biomes quite tiny. There is a reason the biomes are the size that they are. If you still want smaller biomes:\n - Unzip Terralith and open the `Terralith/data/minecraft/worldgen/noise/` folder.\n - Open the `erosion` file.\n - Change `firstOctave` from **-10** to **-9**.'
		elif self.values[0] == 'Amplified Terrain':
			embed.title = 'FAQ - Configuration (Amplified Terrain)'
			embed.description = 'There isn\'t an easy way to do this. Thankfully, if you like *really* tall mountains, and enjoy your computer blowing up, there is a datapack just for that. Because it is so unstable, it is not released publically, and only available to [Patrons](https://www.patreon.com/stardustlabs), [Supporters](https://bisecthosting.com/stardust), [Donators](https://ko-fi.com/stardustlabs), and Server Boosters.'
		elif self.values[0] == 'Remove Biomes':
			embed.title = 'FAQ - Configuration (Remove Biomes)'
			embed.description = 'This is a little difficult and finicky.\n - Unzip Terralith and open the `Terralith/data/minecraft/dimension/` folder.\n - Open `overworld.json` and replace all instances of the biome you don\'t want with biomes you do.\n - To simply remove a biome, you should replace its instances with a similar Minecraft or Terralith biome.\n - When removing Skylands, replace their instances with an ocean type.\n - Be careful, as this doesn\'t always work well and can break.'
		elif self.values[0] == 'Biome Layout':
			embed.title = 'FAQ - Configuration (Biome Layout)'
			embed.description = '*No.*'
		elif self.values[0] == 'Taller Nether':
			embed.title = 'FAQ - Configuration (Taller Nether)'
			embed.description = 'This tutorial (graciously provided by Kuma) will show you how to add extra space above the bedrock roof in Amplified Nether.\n - Download slicedlime\'s datapack [here](https://github.com/slicedlime/examples).\n - Unzip Amplified Nether and navigate to the `/data/minecraft/` directory. Copy the `dimension_type` folder from slicedlime\'s datapack and stick it here.\n - Delete every file in the `dimension_type` directory EXCEPT `the_nether.json`.\n - Edit that file and look for `”height”:` and change the value to 320. This will add 64 blocks of air above the bedrock roof.\n - __If on 1.18/1.18.1 only__, find the line that says `"infiniburn": "minecraft:infiniburn_nether"` and remove the `#`.\n - Save/exit, rezip Amplified Nether, and load it to your world. Enjoy!\n - This will *not* work with Better Nether.'
		await msg.edit(embed=embed)

class Config(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ConfigMenu())

class UpdateMenu(discord.ui.Select):
	def __init__(self):
		options = [
        	discord.SelectOption(label='Terralith', emoji='🌍'),
			discord.SelectOption(label='Terralith (1.19)', emoji='🌍'),
        	discord.SelectOption(label='Incendium', emoji='🔥'),
			discord.SelectOption(label='Amplified Nether', emoji='🔥'),
			discord.SelectOption(label='Nullscape', emoji='🌌')
		]
		super().__init__(placeholder='Select a project...', min_values=1, max_values=1, options=options)
		
	async def callback(self, interaction: discord.Interaction):
		msg = interaction.message
		embed = interaction.message.embeds[0]
		if self.values[0] == 'Terralith':
			embed.title = 'FAQ - Updating (Terralith)'
			embed.description = '_ _- All versions of Terralith 2.0.x work in both 1.18 and 1.18.1 (use 1.18.1 for security reasons). Terralith 2.1.x+ works on 1.18.2 only, and Terralith 2.2.x is for 1.19.x only.\n - Updating Terralith - for example, 2.0.3 to 2.0.8 - is perfectly okay! You can do so with extremely minimal chunk borders.\n - If using the datapack version, *make sure you use the same seed both times* from [SeedFix](https://seedfix.stardustlabs.net/). This is the seed you entered into the site the first time, *not* from `/seed`.\n - If updating from Terralith 2.0.x to 2.1.x+, check if you have any deserts generated in your world. If so, make sure you generate them all the way, since 2.1 completely revamped the desert terrain. If you don\'t, you will have ugly chunk borders there.\n- Updating from 2.2.x (1.18.2) to 2.3.x (1.19)? Click on the Terralith (1.19) option from the Selection Menu.'
		if self.values[0] == 'Terralith (1.19)':
			embed.title = 'FAQ - Updating (Terralith 1.19)'
			embed.description = '**1.** If you used Seedfix, continue. If you downloaded the datapack directly from Planet Minecraft without entering a seed into seedfix website, skip to Step 4\n**2.** Open your `world/level.dat` using Misode\'s NBT Viewer extension for Visual Studio Code or NBT Explorer\n**3.** In the `level.dat`, change the overworld seed in `Data>WorldGenSettings>dimensions` to the seed displayed in `Data>WorldGenSettings>dimensions>minecraft:overworld>generator>biome_source`. If it is the same, you\'re all good! Do not forget the  "-" if there is any\n**4.** Once that is done, you can replace Terralith 2.x.x with Terralith 2.3.x'
		elif self.values[0] == 'Incendium':
			embed.title = 'FAQ - Updating (Incendium)'
			embed.description = '_ _- You cannot update Incendium worlds used in 1.17.1 or lower to 1.18.2 (Incendium 5.0.5).\n - You can update from Incendium 3.4.x to 4.0. Upon updating, hold each Incendium item in your main hand for about 2 seconds. This will update it to its "new" version.\n - Updating to minor versions works fine.'
		elif self.values[0] == 'Nullscape':
			embed.title = 'FAQ - Updating (Nullscape)'
			embed.description = '_ _- Updating to minor versions works fine.\n - Updating from 1.17.1 worlds to 1.18.1 worlds *can* work okay. be careful.\n - When Nullscape updates to 1.19, it will not be compatable with previous versions. You will have to reset your end.\n - If upon installation or updating you find things start to break, ask in the Discord, and we will probably ask for your `level.dat` to do some magic.'
		elif self.values[0] == 'Amplified Nether':
			embed.title = 'FAQ - Updating (Amplified Nether)'
			embed.description = '_ _- Updating between minor and major versions is okay, except for updating to 1.18.x'
		await msg.edit(embed=embed)

class Update(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(UpdateMenu())

class ModsMenu(discord.ui.Select):
	def __init__(self):
		options = [
        	discord.SelectOption(label='Server-/Client-Side', description='Mods that work on both Fabric servers and clients'),
        	discord.SelectOption(label='Server-Side', description='Mods that work only on Fabric servers'),
			discord.SelectOption(label='Client-Side', description='Mods that work only on Fabric clients'),
			discord.SelectOption(label='Shaders', description='Good shader pack recommendations')
		]
		super().__init__(placeholder='Select a mod category...', min_values=1, max_values=1, options=options)
		
	async def callback(self, interaction: discord.Interaction):
		msg = interaction.message
		embed = interaction.message.embeds[0]
		if self.values[0] == 'Server-/Client-Side':
			embed.title = 'FAQ - Mods (Server-/Client-Side)'
			embed.description = '**Carpet Mod** allows you to take full control of what matters from a technical perspective of the game, and fixes many things.\n**C2ME** is designed to improve the performance of chunk generation, I/O, and loading.\n**DimensionalThreading** optimizes the processing of multiple Dimensions, by assigning them independent threads.\n**FerriteCore** reduces the memory usage of Minecraft in a few different ways.\n**Lazy DFU** will not immediately create the rules required to migrate data from older versions of Minecraft to newer versions until it actually needs to do so.\n**Lithium** works to optimize many areas of the game in order to provide better overall performance.'
			self.view.clear_items()
			self.view.add_item(discord.ui.Button(label='Carpet Mod', emoji='<:carpet:963157735501881366>', url='https://github.com/gnembon/fabric-carpet/releases'))
			self.view.add_item(discord.ui.Button(label='C2ME', emoji='<:c2me:963157735451529249>', url='https://www.curseforge.com/minecraft/mc-mods/c2me-fabric/files'))
			self.view.add_item(discord.ui.Button(label='DimensionalThreading', emoji='<:dimthread:963157735359279245>', url='https://github.com/WearBlackAllDay/DimensionalThreading/releases'))
			self.view.add_item(discord.ui.Button(label='FerriteCore', emoji='<:ferrite:963157735778701362> ', url='https://www.curseforge.com/minecraft/mc-mods/ferritecore-fabric/files'))
			self.view.add_item(discord.ui.Button(label='LazyDFU', emoji='<:lazydfu:963157735308951633>', url='https://www.curseforge.com/minecraft/mc-mods/lazydfu/files'))
			self.view.add_item(discord.ui.Button(label='Lithium', emoji='<:lithium:963157735631884308>', url='https://github.com/CaffeineMC/lithium-fabric/releases'))
			self.view.add_item(ModsMenu())
		elif self.values[0] == 'Server-Side':
			embed.title = 'FAQ - Mods (Server-Side)'
			embed.description = '**FastFurnace** does a couple things relating to the vanilla furnaces so they run faster during their update method, improving TPS.\n**Krypton** attempts to optimize the Minecraft networking stack.\n**Starlight** rewrites the light engine to fix lighting performance and lighting errors. __Note__: Although this works client-side as well, it works "better" on a server, and is incompatible with Phosphor.'
			self.view.clear_items()
			self.view.add_item(discord.ui.Button(label='FastFurnace', emoji='<:fastfurnace:963159538293432320>', url='https://www.curseforge.com/minecraft/mc-mods/fastfurnace/files'))
			self.view.add_item(discord.ui.Button(label='Krypton', emoji='<:krypton:963159538217914479>', url='https://www.curseforge.com/minecraft/mc-mods/krypton/files'))
			self.view.add_item(discord.ui.Button(label='Starlight', emoji='<:starlight:963157735581552720>', url='https://www.curseforge.com/minecraft/mc-mods/starlight/files'))
			self.view.add_item(ModsMenu())
		elif self.values[0] == 'Client-Side':
			embed.title = 'FAQ - Mods (Client-Side)'
			embed.description = '**Sodium** greatly improves frame rates, reduces micro-stutter, and fixes graphical issues in Minecraft. __Note__: This is incompatible with several mods, but *heavily* increases performance - very worth it.\n**Phosphor** aims to save your CPU cycles and improve performance by optimizing one of Minecraft\'s most inefficient areas-- the lighting engine. __Note__: Although this works server-side as well, it works "better" on a client, and is incompatible with Starlight.\n**Better FPS - Render Distance** adds a few performance improvements to increase fps.\n**Cull Leaves** adds culling to leaf blocks, providing a huge performance boost over vanilla.\n**DashLoader** improves Minecraft client asset loading times about 6 times by caching all of the game\'s content.\n**EntityCulling** utilizes your other CPU cores/threads to do really quick path-tracing from your camera to all tile-entities to determine whether to render them.'
			self.view.clear_items()
			self.view.add_item(discord.ui.Button(label='Sodium', emoji='<:sodium:963161419736571984>', url='https://modrinth.com/mod/sodium/versions'))
			self.view.add_item(discord.ui.Button(label='Phosphor', emoji='<:phosphor:963157735665463296>', url='https://github.com/CaffeineMC/phosphor-fabric/releases'))
			self.view.add_item(discord.ui.Button(label='Better FPS', emoji='<:betterfps:963161419765940296>', url='https://www.curseforge.com/minecraft/mc-mods/better-fps-render-distance-fabric/files/'))
			self.view.add_item(discord.ui.Button(label='Cull Leaves', emoji='<:cullleaves:963161419820433438>', url='https://www.curseforge.com/minecraft/mc-mods/cull-leaves/files'))
			self.view.add_item(discord.ui.Button(label='DashLoader', emoji='<:dashloader:963161420055339008>', url='https://www.curseforge.com/minecraft/mc-mods/dashloader/files'))
			self.view.add_item(discord.ui.Button(label='EntityCulling', emoji='<:entityculling:963161420147597332>', url='https://www.curseforge.com/minecraft/mc-mods/entityculling/files'))
			self.view.add_item(ModsMenu())
		elif self.values[0] == 'Shaders':
			embed.title = 'FAQ - Mods (Shaders)'
			embed.description = '**Iris** is an open-source shaders mod compatible with OptiFine shaderpacks. This is better than OptiFine - use this as your preferred shader mod!\n\n**Complementary** is an amazing shader pack based on Capt Tatsu\'s "BSL Shaders". Most Terralith screenshots you see are taken with this pack!\n**Nostalgia** is a shaderpack meant to loosely replicate the look and feel of "first-gen" shaderpacks, while also adding new features and visual effects like volumetric fog.\n**Seus** brings you quality visuals at a reasonable performance using traditional rasterization-based rendering methods.\n**BSL** is a shaderpack with high customization and optimization, like realtime shadows, volumetric light, ambient occlusion, bloom, customizable clouds and water, and built in anti-aliasing.'
			self.view.clear_items()
			self.view.add_item(discord.ui.Button(label='Iris', emoji='<:iris:963163615962230784>', url='https://irisshaders.net/'))
			self.view.add_item(discord.ui.Button(label='Complementary', emoji='<:complementary_stan:911647941670871100>', url='https://www.curseforge.com/minecraft/customization/complementary-shaders/files'))
			self.view.add_item(discord.ui.Button(label='Nostalgia', emoji='<:nostalgia:963163615945424976>', url='https://www.curseforge.com/minecraft/customization/nostalgia-shader/files'))
			self.view.add_item(discord.ui.Button(label='Seus', emoji='<:seus:963163615777685554>', url='https://www.sonicether.com/seus/'))
			self.view.add_item(discord.ui.Button(label='BSL', emoji='<:bsl:963163615890919484>', url='https://www.curseforge.com/minecraft/customization/bsl-shaders'))
			self.view.add_item(ModsMenu())
		await msg.edit(embed=embed, view=self.view)

class Mods(discord.ui.View):
	def __init__(self):
		super().__init__(timeout=None)
		self.add_item(discord.ui.Button(label='Fabric Launcher', emoji='<:fabric:962456210773262346>', url='https://fabricmc.net/use/installer/'))
		self.add_item(discord.ui.Button(label='Fabric API', emoji='<:fabric:962456210773262346>', url='https://www.curseforge.com/minecraft/mc-mods/fabric-api/files'))
		self.add_item(ModsMenu())

class FaqButtons(discord.ui.View):
	def __init__(self, client):
		super().__init__(timeout=None)
		self.client = client
		self.channel = self.client.get_channel(923571915879231509)
		self.add_item(FaqButtonsMenu(self.client))

async def setup(client):
	await client.add_cog(Faq(client))
