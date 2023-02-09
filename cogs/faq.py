import discord
import requests
import json
from discord import app_commands
from discord.ext import commands
from resources import incendy

class Faq(commands.Cog):
    def __init__(self, client: incendy.IncendyBot):
        self.client = client
        
    async def cog_load(self):
        print(f' - {self.__cog_name__} cog loaded.')
    
    async def cog_unload(self):
        print(f' - {self.__cog_name__} cog unloaded.')

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
            "Mod vs Datapack": "For all Stardust Labs projects, the mod version is the same as the datapack in regards to performance and content. The only difference is the mods go in the `mods` folder, and datapacks in the `datapacks` folder.\n\nIn 1.18.2 and lower, the mod versions of the projects had Seedfix built in, which technically made them slightly different. Otherwise, you can enjoy the same experience with both! \:)",
            "Keep Exploring": "In Terralith, it is completely normal to spawn in an area that isn't as \"stunning\" or \"breathtaking\" as all the screenshots you see posted around are. To find them, you've got to go explore your world! Keep walking, and you *will* find beautiful landscapes.",
            "Find the Culprit": "Sometimes, when you are trying to figure out what mod is causing your crash, you need to result to the \"remove until it stops crashing\" method. Here is an efficient way to do so:\n - Divide your mods in half: Half A and Half B.\n - Add Half A to your game/server, and start.\n - If it crashes, remove half of Half A.\n - If it does not crash, add half of Half B.\n - Repeat the process until it's narrowed down to the culprit!",
            "Give Details": "Please, please provide details and be descriptive with your issue. We literally cannot help you without context. It also helps if you check the faq (`/faq`) and attach logs."
        }

        await interaction.response.send_message(qp_dict[qp])

    @qp.autocomplete('qp')
    async def autocomplete_callback(self, interaction: discord.Interaction, current: str):
        qp_list = sorted(["Standards", "Discord Links", "Try it and See", "Dont Ask to Ask", "Notch Code", "Optifine Alternatives", "Admin Menu", "Send Logs", "Wiki Link", "Dimension Folders", "Mod vs Datapack", "Keep Exploring", "Find the Culprit", "Give Details"])

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
                    description='Check out the in-depth compatibility table on the wiki by clicking the button below! Here are a couple of specific cases:\n\n**•** Incendium and Amplified Nether do **not** work together. Do `/faq Incendium vs Amplified Nether` for more information.\n**•** Terralith technically works with Biomes O\' Plenty and BYG if Terablender is present... but since Terrablender messes with the biome layout, we do not recommend it. There will be several micro biomes, Terralith will only make up around 5% of total biomes, and some surface biomes can be screwed up.\n**•** Better Nether works with Amplified Nether and Incendium, except in 1.18.2.\n**•** Both Structory and Continents work with Terralith, as well as almost all other worldgen and structure packs/mods.',
                    color=faq_colour
                )
                view = Compat()
            case "Configuration":
                embed = discord.Embed(
                    title='Configuration',
                    description='There is **no configuration file** for datapacks (custom world settings like Large Biomes do not work either). That said, if you want to modify how the packs work, you\'ll have to modify the code inside the datapack. Do keep in mind the [Stardust Labs License](https://github.com/Stardust-Labs-MC/license/blob/main/license.txt) found inside all datapacks, which prohibits you from distributing modified versions of the projects. Select a configuration from the selection menu below.',
                    color=faq_colour
                )
                view = Config()
            case "Contributing":
                embed = discord.Embed(
                    title='Contributing',
                    description='Interested in contributing to Stardust Labs in some way? Here are some ways you can help!',
                    color=faq_colour
                )
                embed.add_field(name="Wiki", value="The wiki could always use your help! You can do anything from adding mod/datapack compatabilities to the [compat table](https://stardustlabs.miraheze.org/wiki/Terralith_compatibilities), or help out greatly by helping with [Tera's to-do list](https://discord.com/channels/738046951236567162/794630105463783484/923270468956483584). Either way, ask in <#794630105463783484> and check out the [Wiki contribution guide](https://stardustlabs.miraheze.org/wiki/Contributing)! By helping out with some of the tougher stuff, you can earn the **Wiki Contributor** role.", inline=False)
                embed.add_field(name="Translations", value="In Incendium, there is a lot of stuff to be translated. If you know another language, go check out our [Localization Website](https://weblate.catter.dev) to start translating for Incendium, Kuma's [Omni Biome Name Fix resourcepack](https://modrinth.com/resourcepack/stardust-biome-name-fix), and future Stardust Labs projects! Is your language not there? Ask <@260929689126699008> to add it! By translating, you can earn the **Translator** role.", inline=False)
                embed.add_field(name="Code, Structures, and Community", value="For the most part, we don\'t accept code contributions for our projects unless you are skilled, well-known in the community, and we're intersted in working with you. It's a similar story for structures: we already have great builders that help us out, but occasionally we might see stuff we like from others and ask if they want to contribute. Finally, the best way you can contribute to Stardust Labs is to hang around and be part of the community! For those who have helped in some way with either code, structures, creating helpful third-party tools, or just being an integral part of our community, you can earn the **Contributor** role.", inline=False)
            case "Foliage Colors":
                embed = discord.Embed(
                    title='Foliage Colors',
                    description='Terralith uses a variety of grass and leaf colors, but does not use a resource pack. Instead, this is actually a Vanilla mechanic: for example, in Vanilla swamps, the water is browner and the leaves/grass is a dull/dark green. In Jungles and Mooshroom Islands, grass is a vibrant green.\n\nThis mechanic is what Terralith uses, but instead of doing different shades of green, Terralith will use the mechanic for all colors. This is how you see red leaves in Forested Highlands, blue grass in Mirage Isles, pink leaves in Sakura Groves, and much more.',
                    color=faq_colour
                )
            case "Incendium vs Amplified Nether":
                embed = discord.Embed(
                    title='FAQ - Incendium vs. Amplified Nether',
                    description='Incendium and Amplified Nether are very different packs, and are **not** compatible with each other.\n**-** __Amplified Nether__ is a Vanilla nether, with 3D biomes, cool terrain shapes, and an extended height.\n**-** __Incendium__ has what Amplified Nether has, but with custom mobs, items, biomes, structures, and a cool boss. (Although, the Incendium height extension is not quite as Amplified Nether\'s.)',
                    color=faq_colour
                )
            case "Is It Working":
                embed = discord.Embed(
                    title='How Do I Tell If It\'s Working?',
                    description="**•** Do `/datapack list` in game. Does the datapack appear green in that list? If not, it is not installed correctly - follow `/faq Server Installation` in the Discord.\n**•** If the first step was successful, type `/locate biome #terralith:all_terralith_biomes` (`/locatebiome #terralith:all_terralith_biomes` for 1.18.2 and lower) in game and see if you get a result. Replace `terralith` with whatever relevant datapack you're installing. If you did not get any results, follow the Server Installation mentioned before.\n**•** If you're using Structory, do `/locate structure structory:` (`/locate structory:` in 1.18.2 and below) and follow the previous steps.\n**•** For Continents, there isn't a sure way to tell. Just make sure you followed the Server installation FAQ, see if the land looks like continents, and use something like DynaMap if you'd like to see if it's working.",
                    color=faq_colour
                )
            case "License":
                embed = discord.Embed(
                    title='Stardust Labs License',
                    description='You can find the license inside all Stardust Labs datapacks, or view it at [this link](https://github.com/Stardust-Labs-MC/license/blob/main/license.txt). It applies to *all* projects created by Stardust Labs. Read it for important information, especially about modifying Stardust Labs\' projects.',
                    color=faq_colour
                )
            case "Multiverse":
                embed = discord.Embed(
                    title='Multiverse',
                    description='Multiverse is not the friendliest with worldgen datapacks. Below you can find a method to try - it\'s not 100% guarenteed to work, but it\'s the best we have, and nothing else we can do to help other than recommend a BungeeCord server rather than using Multiverse. MyWorlds is untested.\n\n**1.** Stop your server and take a backup.\n**2.** Make sure your main world is the one with the worldgen datapacks, and delete the `region` folder *inside* of that `world` folder (or whatever it is equivalently named).\n**3.** Delete Multiverse\'s `world.yml`, along with a `worlds.txt` if you have it.\n**4.** The default world in your `server.properties` should be the one with the worldgen datapacks.\n**5.** Boot up your server, join, and see if it worked.\n**6.** If it works and you just have leftover broken chunks, you can either reset the world, edit with MCA Selector, or using WorldEdit\'s `//regen` command.',
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
            case "Passive Animals":
                embed = discord.Embed(
                    title='Passive Animal Spawns',
                    description='Passive mobs only spawn on grass blocks (and similar), on less-spiky terrain, and closer to sea level. Because Terralith is more mountainous than Vanilla, and there are more biomes without grass blocks, you will tend to find less passive mobs.\n\nAlthough is is not possible to change passive mob spawning conditions, Terralith increases the spawn rates on the places they *are* able to spawn on. The TL;DR is that Terralith can\'t do anything about the rarity of mob spawning locations. If you want to learn more about Vanilla mob spawning rules, check out [this Minecraft Wiki article](https://minecraft.fandom.com/wiki/Spawn#Spawn_conditions).',
                    color=faq_colour
                )
            case "Pregeneration":
                embed = discord.Embed(
                    title='Pregeneration',
                    description='Worldgen alone only causes lag when generating chunks for the first time. Because of this, pregenerating your world is highly encouraged. One of the only and best pregen mods/plugins is Chunky.\n\nClick the buttons below for download links. Check out their respective websites for instructions on how to use it - don\'t ask here!.',
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
                    description='You cannot simply remove a worldgen pack from your world. The way to do so involves completely resetting your dimension, so we do not recommend it unless you have a good reason. In order to do so, you must follow these three steps:\n\n**1.** Ensure your world/server is stopped, and remove the worldgen datapack.\n**2.** You must completely reset the dimension that the worldgen pack was affecting. For the nether and end, this is done by deleting the `world/DIM-1` and `world/DIM1` folders in Vanilla/Fabric/Forge, and `world_nether` and `world_the_end` folders in Spigot/Paper, respectively. It\'s more tricky for the overworld - either just reset everything, or ask for further help.\n**3.** You must remove all biome entries from your `level.dat`. If you do not know how to do this, ask for assistance. There will be tools for this later.',
                    color=faq_colour
                )
            case "Resource Packs":
                embed = discord.Embed(
                    title='Resource Packs',
                    description='When using a minimap or any other mod that displays biomes, Stardust biome names may appear very long. <@212447019296489473> made a cool resource pack that fixes it! You can download it from the Modrinth page by clicking the button below.\n\nIf you want a resourcepack for Incendium that gives all of Incendium\'s custom stuff unique textures, check out <@234748321258799104>\'s Incendium Optional Resourcepack! You can download it from the GitHub repo by clicking the button below.',
                    color=faq_colour
                )
                view = Resource()
            case "Seedfix":
                embed = discord.Embed(
                    title='SeedFix',
                    description=' In 1.18.x **only**, there is a [Minecraft bug](https://bugs.mojang.com/browse/MC-195717) that makes all worldgen datapacks use the same seed. To use the datapack version of Terralith in 1.18.2, download a version from the SeedFix website, which allows you to input your own seed. The download is Terralith itself, so you put it in the datapack folder by itself. The mod versions have SeedFix built in, so you can use seeds as you normally would in Vanilla.\n\nAlso because of the bug, in 1.18.x, there are two "types" of seeds when dealing with worldgen datapacks.\n**•** The **world seed** is the seed you get from looking at `/seed`, `level.dat`, or `server.properties`. This seed effects how __structures__ generate and where __slime chunks__ are.\n\n**•** The **terrain seed** is the seed found in Terralith\'s `overworld.json` file (it\'s what SeedFix changes!). This seed affects how terrain generates and where biomes are.',
                    color=faq_colour
                )
                view = Seedfix()
            case "Server Installation":
                embed = discord.Embed(
                    title='Server Installation',
                    description='Select an installation method from the Select Menu below!\n\nYou should **__ONLY__** select the "Install Method 1.19.3 ONLY" selection if you are using 1.19.3 - it will *not* work if you are using 1.19.2 or lower!"',
                    color=faq_colour
                )
                view=Server()
            case "Stone Generation":
                embed = discord.Embed(
                    title='Stone Generation',
                    description='In Terralith, granite, diorite, and andesite do not generate in blobs like in Vanilla. Instead, they only generate in the respective cave biomes: Andesite Caves, Granite Caves, and Diorite Caves. These cave biomes are relatively common, and are made entirely out of their respective stone, which makes it perfect for mods like Create!\n\nIf you have trouble finding the caves, you can look at the surface of your world for granite pillars, andesite boulders, and diorite patches. These features mean the respective stone\'s cave biome can be found underneath! Check the graphic attached to see examples of how they look like, or view the [wiki entry](https://stardustlabs.miraheze.org/wiki/Terralith#Andesite_boulders).',
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
                embed.add_field(name="Support Methods", value="**•** Stardust Labs is partnered with **Bisect Hosting**! Use code `STARDUST` to get 25% off your first month, as well as access to the __Supporter Showcase__.\n**•**By **Nitro Boosting** the Discord server, you also gain access to the __Supporter Showcase__!\n**•** Subscribing to either our **Patreon** or **Server Subscription**, you have access to a range of __Patron Benefits__.\n**•** If a subscription doesn't suit you, feel free to do a one-time donation to our **Ko-Fi** to gain access to the __Supporter Showcase__.", inline=False)
                embed.add_field(name="Supporter Benefits", value="**•** The **Supporter Showcase** gives you access to small projects, such as Terralith: Fire Extinguisher. You also get access to a more exclusive <#774837076821540864>, being able to see images before anyone else.\n**•** Our **Patron Benefits** have a lot to offer, including beta versions of our main projects, access to our build server, and the ability to add an easter egg somewhere. More details in the Patreon/Server Subscription buttons below!", inline=False)
                view=Support()
            case "Traveller Maps":
                embed = discord.Embed(
                    title='Traveller\'s Maps',
                    description='If your world/server is crashing upon opening a chest in a Terralith structure, it is probably due to the Traveller\'s Maps. Because the lag is just absurd, they have been removed in the recent versions of Terralith. If you\'re on 1.18.2, ensure you\'re using Terralith v2.2.3, and if on 1.19.x, ensure you\'re on Terralith v2.3.3 or higher.\n\n As a fun note, some changes in Minecraft 1.19.3 has greatly improved the lookup speed for structures, which is what the maps rely on. Although the changes are appreciated, it is still slow, so the Traveller\'s Maps will likely not yet return.',
                    color=faq_colour
                )
            case "Updating Versions":
                embed = discord.Embed(
                    title='Updating Versions',
                    description='Make sure to always take a backup before updating! Select a datapack from the selection menu below to see information on updating those datapacks.',
                    color=faq_colour
                )
                view = Update()
            case "Version Table":
                embed = discord.Embed(
                    title='All Versions',
                    description='Here is a table of the versions of our packs with which version of Minecraft they belong to. You can find this with explanations and downloads for each pack in the GitHub repos, which are linked in <#900598465430716426>.',
                    color=faq_colour
                )
                file = discord.File("assets/Version_Table.png", filename="image.png")
                embed.set_image(url="attachment://image.png")
            case "WWOO":
                embed = discord.Embed(
                    title='WWOO Compatibility',
                    description='Terralith is compatible with William Wyther\'s Overhauled Overworld __only__ when using the mod version 3.0 or higher of WWOO. Terrablender ([Fabric](https://www.curseforge.com/minecraft/mc-mods/terrablender-fabric) or [Forge](https://www.curseforge.com/minecraft/mc-mods/terrablender)) is required.\n\nYou will need to go inside WWOO\'s configs and enable Terralith compat, or in-game if using Fabric with [ModMenu](https://www.curseforge.com/minecraft/mc-mods/modmenu) and [Cloth Config](https://www.curseforge.com/minecraft/mc-mods/cloth-config/files). More information can be found on WWOO\'s [CurseForge page](https://www.curseforge.com/minecraft/mc-mods/william-wythers-overhauled-overworld).',
                    color=faq_colour
                )
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
                else:
                    await interaction.response.send_message(embed=embed, file=file, ephemeral=public)
        else:
            if view:
                await interaction.response.send_message(embed=embed, view=view, ephemeral=public)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=public)

        # Enter into DB
        if interaction.guild_id == self.client.settings["stardust-guild-id"]:
            query = '''INSERT INTO faqs(user_id, faq_name, sent_on) VALUES($1, $2, $3);'''
            await self.client.db.execute(query, interaction.user.id, faq, interaction.created_at)

    @faq.autocomplete('faq')
    async def autocomplete_callback(self, interaction: discord.Interaction, current: str):
        faq_list = sorted(["Ore Distribution", "Biome IDs", "Removal", "Traveller Maps", "Passive Animals", "Pregeneration", "Foliage Colors", "Contributing", "Resource Packs", "Configuration", "Incendium vs Amplified Nether", "Server Installation", "Updating Versions", "Seedfix", "Compatibility", "Realms", "License", "Support Us", "Versions", "How Do I Tell", "Multiverse", "Stone Generation", "Structory Addons", "WWOO"])

        return [
            app_commands.Choice(name=faq, value=faq)
            for faq in faq_list
            if current.replace(" ", "").lower() in faq.replace(" ", "").lower()
        ]

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
        response = requests.get(url)

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
        self.add_item(discord.ui.Button(label='Compatibility Table', emoji='<:miraheze:890077957069111316>', url='https://stardustlabs.miraheze.org/wiki/Terralith_compatibilities'))

class Pregen(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(discord.ui.Button(label='Chunky (Fabric)', emoji='<:fabric:962456210773262346>', url='https://www.curseforge.com/minecraft/mc-mods/chunky-pregenerator'))
        self.add_item(discord.ui.Button(label='Chunky (Forge)', emoji='<:curseforge:1045336245900939274>', url='https://www.curseforge.com/minecraft/mc-mods/chunky-pregenerator-forge'))
        self.add_item(discord.ui.Button(label='Chunky (Paper/Spigot)', emoji='<:spigot:964945252890861649>', url='https://www.spigotmc.org/resources/chunky.81534/'))

class Realms(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(discord.ui.Button(label='Bisect Hosting', emoji='<:bisect:962410759462203462>', url='https://bisecthosting.com/stardust'))

class Resource(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(discord.ui.Button(label='Omni Biome Name Fix', emoji='<:modrinth:1045336248950214706>', url='https://modrinth.com/resourcepack/stardust-biome-name-fix'))
        self.add_item(discord.ui.Button(label='Incendium Optional Resourcepack', emoji='<:github:1045336251605188679>', url='https://github.com/Stardust-Labs-MC/downloads-library/tree/main/Incendium/Resource%20Pack'))

class Seedfix(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(discord.ui.Button(label='SeedFix Website', emoji='<:seedfix:917599175259070474>', url='https://seedfix.stardustlabs.net/'))
        self.add_item(discord.ui.Button(label='Mod Download', emoji='<:curseforge:1045336245900939274>', url='https://www.curseforge.com/minecraft/mc-mods/terralith'))

class Support(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(discord.ui.Button(label='Bisect Hosting', emoji='<:bisect:962410759462203462>', url='https://bisecthosting.com/stardust'))
        self.add_item(discord.ui.Button(label='Patreon', emoji='<:patreon:962411326628581376>', url='https://www.patreon.com/stardustlabs'))
        self.add_item(discord.ui.Button(label='Server Subscriptions', emoji='<:discord:1048627498734342206>', url='https://discord.com/servers/stardust-labs-738046951236567162'))
        self.add_item(discord.ui.Button(label='Ko-Fi', emoji='<:kofi:962411326666334259>', url='https://ko-fi.com/stardustlabs'))

### SELECT MENUS ###

class ConfigMenu(discord.ui.Select):
    def __init__(self):
        options = [
        	discord.SelectOption(label='Bigger Biomes', description='How to increase biome size in Terralith'),
        	discord.SelectOption(label='Smaller Biomes', description='How to decrease biome size in Terralith'),
			discord.SelectOption(label='Remove Biomes', description='How to remove/replace biomes in Terralith'),
			discord.SelectOption(label='Taller Nether', description='How to add space above bedrock in the Nether'),
			discord.SelectOption(label='Biome Layout', description='How to change Terralith\'s biome layout'),
			discord.SelectOption(label='Amplified Terrain', description='Super tall mountains in Terralith?')
		]
        super().__init__(placeholder='Select a configuration...', min_values=1, max_values=1, options=options)
        
    async def callback(self, interaction: discord.Interaction):
        embed = interaction.message.embeds[0]

        match self.values[0]:
            case 'Bigger Biomes':
                embed.title = 'Configuration (Bigger Biomes)'
                embed.description = 'Currently, the Terralith biome sizes are on average slightly larger than Vanilla, but *can* be huge. If you still want larger biomes:\n**•** Unzip Terralith and open the `Terralith/data/minecraft/worldgen/noise/` folder.\n**•** Subtract **1** from all instances of `firstOctave` in the `erosion`, `continentalness`, `temperature`, and `vegetation` files.\n**•** Do *not* edit the `ridge` file.'
            case 'Smaller Biomes':
                embed.title = 'Configuration (Smaller Biomes)'
                embed.description = 'Keep in mind that doing this will make the biomes quite tiny. There is a reason the biomes are the size that they are. If you still want smaller biomes:\n**•** Unzip Terralith and open the `Terralith/data/minecraft/worldgen/noise/` folder.\n**•** Open the `erosion` file.\n**•** Change `firstOctave` from **-10** to **-9**.'
            case 'Amplified Terrain':
                embed.title = 'Configuration (Amplified Terrain)'
                embed.description = 'There isn\'t an easy way to do this. Thankfully, if you like *really* tall mountains, and enjoy your computer blowing up, there is a datapack just for that. Because it is so unstable, it is not released publically, and only available to [Patrons](https://www.patreon.com/stardustlabs), [Supporters](https://bisecthosting.com/stardust), [Donators](https://ko-fi.com/stardustlabs), and Server Boosters.'
            case 'Remove Biomes':
                embed.title = 'Configuration (Remove Biomes)'
                embed.description = 'This is a little difficult and finicky.\n**•** Unzip Terralith and open the `Terralith/data/minecraft/dimension/` folder.\n**•** Open `overworld.json` and replace all instances of the biome you don\'t want with biomes you do.\n**•** To simply remove a biome, you should replace its instances with a similar Minecraft or Terralith biome.\n**•** When removing Skylands, replace their instances with an ocean type.\n**•** Be careful, as this doesn\'t always work well and can break.'
            case 'Biome Layout':
                embed.title = 'Configuration (Biome Layout)'
                embed.description = '*No.*'
            case 'Taller Nether':
                embed.title = 'Configuration (Taller Nether)'
                embed.description = 'This tutorial (graciously provided by <@212447019296489473>) will show you how to add extra space above the bedrock roof in Amplified Nether.\n**•** Download slicedlime\'s datapack [here](https://github.com/slicedlime/examples).\n**•** Unzip Amplified Nether and navigate to the `/data/minecraft/` directory. Copy the `dimension_type` folder from slicedlime\'s datapack and stick it here.\n**•** Delete every file in the `dimension_type` directory EXCEPT `the_nether.json`.\n**•** Edit that file and look for `”height”:` and change the value to 320. This will add 64 blocks of air above the bedrock roof.\n**•** __If on 1.18/1.18.1 only__, find the line that says `"infiniburn": "minecraft:infiniburn_nether"` and remove the `#`.\n**•** Save/exit, rezip Amplified Nether, and load it to your world. Enjoy!\n**•** This will *not* work with Better Nether.'
            
        await interaction.response.edit_message(embed=embed)

class Config(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ConfigMenu())

class ServerMenu(discord.ui.Select):
    def __init__(self):
        options = [
        	discord.SelectOption(label='Normal Install Method'),
			discord.SelectOption(label='Install Method 1.19.3 ONLY')
		]
        super().__init__(placeholder='Select a method...', min_values=1, max_values=1, options=options)
    
    async def callback(self, interaction: discord.Interaction):
        embed = interaction.message.embeds[0]
        
        match self.values[0]:
            case 'Normal Install Method':
                embed.title = 'Normal Install Method'
                embed.description = 'Pick your favorite server software (Fabric, Paper, etc) since this method will work on all of them, whether you\'re using a hosting service or not!\n\n**1.** If using datapacks (ends in `.zip`), put them all in the `world/datapacks` folder. If using mods (ends in `.jar`), put them all in the `mods` folder.\n\n**2.** Start your server, wait for it to load, then stop it.\n\n**3a.** [Terralith/Structory/Continents] Inside the `world` folder, delete the entire `region` folder, and *nothing* else.\n**3b.** [Incendium/Amplified Nether] Inside the nether folder, delete **__only__** the `region` folder, and **__nothing__** else. On Spigot/Paper, the nether folder is `world_nether`, and it\'s `world/DIM-1` on Fabric/Vanilla.\n**3c.** [Nullscape] Inside the end folder, delete **__only__** the `region` folder, and **__nothing__** else. On Spigot/Paper, the end folder is `world_the_end`, and it\'s `world/DIM1` on Fabric/Vanilla.\n\n**4.** Start your server again, and enjoy!\n\nNote: *If only using Structory, these steps are not necessary - you just might not find Structory structures within a couple chunks of spawn if you don\'t. Therefore, you can add Structory to an already generated world with no issues!'
            case 'Install Method 1.19.3 ONLY':
                embed.title = 'Install Method 1.19.3 ONLY'
                embed.description = '**__Warning__**: this method works on **1.19.3 ONLY!** It will __not__ work on 1.19.2 or lower. If you are on 1.19.2 or lower, select the "Normal Install Method" in the select menu below instead. If you use this method, and it does not work, try the Normal method.\n\nPick your favorite server software (Fabric, Paper, etc), since this method will work on all of them.\n\n**1.** __Do not__ start your server at all. If you are using a server host and they have already generated your `world` folder, this method will **not** work. Same goes for self hosting, and if you already started the server. Swap to "Normal Install Method" immediately!\n\n**2a.** [Datapacks only] Manually create a `world` folder. Inside that folder, manually create a `datapacks` folder. Insert all your datapacks in that folder.\n**2b.** [Mods only] Manually create a `mods` folder. Insert all your mods in that folder.\n\n**3.** Start your server and enjoy!'

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
                embed.description = '**•** Updating Terralith between minor versions (2.3.x) - for example, 2.3.3 to 2.3.5 - is perfectly fine! You can do so with little to no chunk borders.\n**•** If using the datapack version in 1.18.2, __make sure you use the same seed both times__ from [SeedFix](https://seedfix.stardustlabs.net/). This is the seed you entered into the site the first time (found in the name of the file you downloaded), *not* from `/seed`.\n**•** If updating from Terralith 2.0.x to 2.1.x, check if you have any deserts generated in your world. If so, make sure you generate them all the way, since 2.1.x completely revamped the desert terrain. If you don\'t, you will have ugly chunk borders there.\n**•** Updating from 2.2.x (1.18.2) to 2.3.x (1.19.x)? Click on the Terralith (1.19) option from the Selection Menu.'
            case 'Terralith (1.19)':
                embed.title = 'Updating (Terralith 1.19)'
                embed.description = '**1.** If you used Seedfix, continue. If you downloaded the datapack directly from Planet Minecraft without entering a seed into the Seedfix website, skip to Step **4**.\n**2.** Open your `world/level.dat` using <@149241652391706625>\'s [NBT Viewer](https://marketplace.visualstudio.com/items?itemName=Misodee.vscode-nbt) extension for [Visual Studio Code](https://code.visualstudio.com/) or [NBT Explorer](https://minecraft.fandom.com/wiki/Tutorials/Programs_and_editors/NBTExplorer).\n**3.** In the `level.dat`, change the overworld seed in `Data>WorldGenSettings>dimensions` to the seed displayed in `Data>WorldGenSettings>dimensions>minecraft:overworld>generator>biome_source`. If it is the same, you\'re all good! Do not forget the  "-" if there is any.\n**4.** Once that is done, you can replace Terralith 2.x.x with Terralith 2.3.x and start up your world!'
            case 'Incendium':
                embed.title = 'Updating (Incendium)'
                embed.description = '**•** You cannot update Incendium worlds used in 1.17.1 (Incendium 4.0.0) or lower to 1.18.2 (Incendium 5.0.x).\n**•** Updating from 1.18.2 to 1.19 (5.0.x to 5.1.x) is mostly fine!\n**•** Updating to minor versions (5.1.x) works fine - for example, 5.1.2 to 5.1.4.'
            case 'Nullscape':
                embed.title = 'Updating (Nullscape)'
                embed.description = '**•** Updating to minor versions (v1.2.x) works fine.\n**•** We do not recommend using any 1.18.x version of Nullscape. Period. We offer very little support for these versions.\n**•** Nullscape 1.19 (v1.2) is different from all other versions, since it is combined into one dimension, like it should! Because of that, you cannot update a 1.18.x Nullscape world (v1.1.x) to 1.19 (v1.2) without completely resetting your end and heavily editing your `level.dat`.'
            case 'Other Stardust Packs':
                embed.title = 'Updating (Other Stardust Packs)'
                embed.description = '**•** Updating between minor and major versions is mostly okay!\n**•** You cannot update Amplified Nether from older versions to 1.18.x or higher.'
        
        await interaction.response.edit_message(embed=embed)

class Update(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(UpdateMenu())

async def setup(client):
	await client.add_cog(Faq(client))