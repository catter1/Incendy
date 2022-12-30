import discord
import asyncio
import requests
import socket
import urllib3
import typing
import json
import os
import random
import shutil
import subprocess
import googletrans
from resize import resize
from zipfile import ZipFile
from itertools import cycle
from discord import app_commands
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions
from collections import OrderedDict
from bs4 import BeautifulSoup
from datetime import *

class Basic(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.translator = googletrans.Translator()
        self.version = '3.0.0_BETA'

        self.translate_app = app_commands.ContextMenu(
            name='Translate to English',
            callback=self._translate,
        )
        self.client.tree.add_command(self.translate_app)
        self.client.tree.on_error = self.on_app_command_error
    
    async def cog_load(self):
        self.change_presence.start()
        #self.loop_get_stats.start()
        self.webchan = self.client.get_channel(917905247056306246)
        print(f' - {self.__cog_name__} cog loaded.')

    async def cog_unload(self):
        self.change_presence.stop()
        #self.loop_get_stats.stop()
        self.client.tree.remove_command(self.translate_app.name, type=self.translate_app.type)
        print(f' - {self.__cog_name__} cog unloaded.')

    @tasks.loop(seconds=1200.0)
    async def change_presence(self):
        projects = ["Terralith", "Incendium", "Nullscape", "Amplified Nether", "Structory", "Continents"]
        if random.randint(0, 100) == 12:
            game = discord.Game("Anvil Sand Farming")
        else:
            game = discord.Game(random.choice(projects))
        await self.client.change_presence(activity=game)

    @change_presence.before_loop
    async def before_change_presence(self):
        await self.client.wait_until_ready()
    
    @tasks.loop(hours=6.0)
    async def loop_get_stats(self):
        self.stats = await self.get_stats()

    @loop_get_stats.before_loop
    async def before_change_presence(self):
        await self.client.wait_until_ready()

    ### COOLDOWNS & CHECKS ###

    def in_bot_channel():
        def bot_channel(interaction: discord.Interaction):
            if interaction.channel_id == 871376111857193000 or interaction.channel_id == 923571915879231509:
                return True
            if interaction.user.guild_permissions.administrator:
                return True
            else:
                return False
        return app_commands.check(bot_channel)

    def can_report_bug():
        def bug_reporter(interaction: discord.Interaction):
            if any([role.id for role in interaction.user.roles if role.id == 749701703938605107 or role.id == 885719021176119298]):
                return True
            if interaction.user.guild_permissions.administrator:
                return True
            else:
                return False
        return app_commands.check(bug_reporter)

    def default_cd(interaction: discord.Interaction) -> typing.Optional[app_commands.Cooldown]:
        if interaction.user.guild_permissions.administrator:
            return None
        if interaction.channel_id == 871376111857193000:
            return None
        return app_commands.Cooldown(2, 25.0)

    def short_cd(interaction: discord.Interaction) -> typing.Optional[app_commands.Cooldown]:
        if interaction.user.guild_permissions.administrator:
            return None
        if interaction.channel_id == 871376111857193000:
            return None
        return app_commands.Cooldown(1, 15.0)
    
    def long_cd(interaction: discord.Interaction) -> typing.Optional[app_commands.Cooldown]:
        if interaction.user.guild_permissions.administrator:
            return None
        return app_commands.Cooldown(1, 35.0)

    def super_long_cd(interaction: discord.Interaction) -> typing.Optional[app_commands.Cooldown]:
        if interaction.user.guild_permissions.administrator:
            return None
        return app_commands.Cooldown(1, 6000.0)

    ### COMMANDS ###

    @app_commands.command(name="stats", description="Shows stats about Stardust Labs")
    @in_bot_channel()
    async def stats(self, interaction: discord.Interaction):
        """ /stats """

        catter = self.client.get_user(260929689126699008)
        stats = self.stats
        
        embed = discord.Embed(title='Stardust Labs Stats', color=discord.Colour.brand_red())
        embed.set_author(name='catter1', icon_url=catter.avatar)
        embed.add_field(name='Incendy Version', value=self.version, inline=False)
        embed.add_field(name='StardustTV Videos', value="{:,}".format(stats["videos"]))
        embed.add_field(name='StardustTV Streams', value="{:,}".format(stats["streams"]))
        embed.add_field(name='\u200b', value='\u200b')
        embed.add_field(name='Terralith Downloads', value="{:,}".format(stats["terralith"]))
        embed.add_field(name='Incendium Downloads', value="{:,}".format(stats["incendium"]))
        embed.add_field(name='Nullscape Downloads', value="{:,}".format(stats["nullscape"]))
        embed.add_field(name='Structory Downloads', value="{:,}".format(stats["structory"]))
        embed.add_field(name='Amplified Nether Downloads', value="{:,}".format(stats["amplified-nether"]))
        embed.add_field(name='Continents Downloads', value="{:,}".format(stats["continents"]))
        embed.set_footer(text='<:pmc:1045336243216584744> <:modrinth:1045336248950214706> <:curseforge:1045336245900939274> <:stardust:917599175259070474>')
        await interaction.response.send_message(embed=embed)

    async def get_stats(self) -> dict:
        stats = {}

        with open('resources/streams.txt', 'r') as f:
            stats["streams"] = len(f.readlines())
        with open('resources/videos.txt', 'r') as f:
            stats["videos"] = len(f.readlines())

        projects = ["terralith", "incendium", "nullscape", "amplified-nether", "continents", "structory"]
        for project in projects:
            stats[project] = 0

        # Curseforge
        for project in projects:
            ## Thanks! https://python.tutorialink.com/pythons-requests-triggers-cloudflares-security-while-urllib-does-not/
            answers = socket.getaddrinfo('www.curseforge.com', 443)
            (family, type, proto, canonname, (address, port)) = answers[0]
            headers = OrderedDict({
                'Host': "www.curseforge.com",
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
            })
            s = requests.Session()
            s.headers = headers
            urllib3.disable_warnings()
            response = s.get(f"https://{address}/minecraft/mc-mods/{project}", verify=False)

            soup = BeautifulSoup(response.content, "html.parser")
            stats[project] += int(soup.find_all(text="Total Downloads")[0].parent.parent.contents[3].text.replace(",", ""))
        
        # Modrinth
        headers = {'User-Agent': 'catter1/Incendy (catter@zenysis.net)'}
        projects.remove('structory')
        for project in projects:
            url = f"https://api.modrinth.com/v2/project/{project}"
            x = requests.get(url=url, headers=headers)
            stats[project] += json.loads(x.text)["downloads"]

        # PMC
        pmc_projects = {
            "terralith": "terralith-overworld-evolved-100-biomes-caves-and-more/",
            "incendium": "incendium-nether-expansion",
            "nullscape": "nullscape",
            "structory": "structory",
            "amplified-nether": "amplified-nether-1-18/",
            "continents": "continents"
        }
        for project in pmc_projects.keys():
            url = f"https://www.planetminecraft.com/data-pack/{pmc_projects[project]}"
            x = requests.get(url=url, headers=headers)
            soup = BeautifulSoup(x.text, "html.parser")
            stats[project] += int(soup.find_all(text=" downloads, ")[0].parent.contents[1].text.replace(",", ""))

        # Seedfix
        url = "https://seedfix.stardustlabs.net/api/get_downloads/"
        x = requests.get(url=url, headers=headers)
        stats["terralith"] += int(x.text)

        return stats

    @app_commands.command(name="discord", description="Gets links for other Discord servers")
    @app_commands.checks.dynamic_cooldown(default_cd)
    @app_commands.describe(
    	server="Discord server"
	)
    async def _discord(self, interaction: discord.Interaction, server: str):
        """ /discord [server] """

        await interaction.response.send_message(server)

    @_discord.autocomplete('server')
    async def autocomplete_callback(self, interaction: discord.Interaction, current: str):
        server_dict = {
            "New In Town": "https://discord.gg/KvdmxHM",
            "MC Configs": "https://discord.gg/EjrKNBU",
            "Still Loading": "https://discord.gg/vkUtRKCdtg",
            "REDUX": "https://discord.gg/BBNavaXH8v",
            "Hashs": "https://discord.gg/eKQSEmH9dY",
            "Botany": "https://discord.gg/BMzTfru5tp",
            "Distant Horizons": "https://discord.gg/Hdh2MSvwyc",
            "Complementary": "https://discord.gg/A6faFYt",
            "Apollo": "https://discord.gg/vFz67Pvceu",
            "Smithed": "https://discord.gg/gkp6UqEUph",
            "MC Commands": "https://discord.gg/QAFXFtZ",
            "Splatus": "https://discord.gg/5DqYxxZdeb",
            "WWOO": "https://discord.gg/jT34CWwzth",
            "BYG": "https://discord.gg/F28fGPCJH8",
            "Foka's Studios": "https://discord.gg/J6guYAySN8",
            "YUNG": "https://discord.gg/rns3beq",
            "BetterX": "https://discord.gg/kYuATbYbKW",
            #"LPS": "https://discord.gg/8ZmhaPPbjE",
            "ChoiceTheorem": "https://discord.gg/JzYEw7PxQv",
            "rx": "https://discord.gg/CzjCF8QNX6",
            "Stardust Labs": "https://discord.gg/stardustlabs"
        }
        server_list = sorted([server for server in server_dict.keys()])

        return [
            app_commands.Choice(name=server, value=server_dict[server])
            for server in server_list
            if current.replace(" ", "").lower() in server.replace(" ", "").lower()
        ]

    @app_commands.command(name="ping", description="Shows you your latency")
    @app_commands.checks.dynamic_cooldown(short_cd)
    async def ping(self, interaction: discord.Interaction):
        """ /ping """

        responses = [
            "I'm not your slave.",
            "Ha!",
            "Too slow.",
            "Go away.",
            "I'm not telling you.",
            "I *suppose* I could tell you... later.",
            "You'll never understand! No one ever does!",
            "Mortal. Your kind never ceases to entertain me."
        ]
        await interaction.response.send_message(f"{interaction.user.mention} {random.choice(responses)}")

    @app_commands.checks.dynamic_cooldown(long_cd)
    async def _translate(self, interaction: discord.Interaction, message: discord.Message):
        translation = self.translator.translate(message.content, dest='en')

        embed = discord.Embed(title="Translation", description=translation.text, colour=discord.Colour.brand_red())
        embed.set_footer(text=f"Translated from {googletrans.LANGUAGES[translation.src]}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="bug", description="Creates a bug report on a GitHub repo")
    @can_report_bug()
    async def bug(self, interaction: discord.Interaction, project: str):
        modal = BugInfo(project=project)
        await interaction.response.send_modal(modal)

    @bug.autocomplete('project')
    async def autocomplete_callback(self, interaction: discord.Interaction, current: str):
        projects = sorted(["Terralith", "Incendium", "Nullscape", "Structory", "Amplified-Nether", "Continents"])
        # if not interaction.user.guild_permissions.administrator:
        #     projects.remove("Incendium-Dev")

        return [
            app_commands.Choice(name=project, value=project)
            for project in projects
            if current.replace(" ", "").lower() in project.replace(" ", "").lower()
        ]

    @app_commands.command(name="feedback", description="Sends feedback to/about Incendy")
    @app_commands.checks.dynamic_cooldown(super_long_cd)
    @in_bot_channel()
    async def feedback(self, interaction: discord.Interaction):
        feedback_chan = self.client.get_channel(747626471819968554)
        await interaction.response.send_modal(Feedback(feedback_chan))

    @app_commands.command(name="reportad", description="Report an inappropriate ad on the Stardust Labs website")
    @app_commands.checks.dynamic_cooldown(super_long_cd)
    @app_commands.describe(
        ad="Image of the advertisement"
    )
    async def reportad(self, interaction: discord.Interaction, ad: discord.Attachment):
        if not ad.content_type.split("/")[0] == "image":
            interaction.response.send_message("Ad must be an image!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="Reported Ad",
            description="Here is a reported ad found on the [Stardust Labs website](https://www.stardustlabs.net/).",
            color=discord.Colour.brand_red()
        )
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
        embed.set_image(url=ad.url)

        await self.webchan.send(embed=embed)
        await interaction.response.send_message("Ad successfully reported! Thank you!", ephemeral=True)

    @app_commands.command(name="seed", description="[ADMIN] Submits a seed to the Seedfix site")
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(
    	seed="Seed number (must be integer)",
    	description="Description of seed, 450 characters or less",
        image="Image of the seed showing what makes it special (must be .png)"
	)
    async def seed(self, interaction: discord.Interaction, seed: int, description: str, image: discord.Attachment):
        """ /seed seed description image """

        if seed == None or description == None:
            embed = discord.Embed(color=discord.Colour.dark_teal(), title="Submit a Seed", description="Would you like to submit a seed to the Terralith Seed Library? At this webpage, users can browse, like, and download user-submitted seeds.")
            embed.add_field(name="**Command to Submit Seed:**", value="`!seed (seed) (description)` All fields are required. You must upload a screenshot as well. Look below for descriptions on each field.", inline=False)
            embed.add_field(name="seed", value="If you found this seed using the datapack, the seed is **NOT** from `/seed`. Instead, get it from the name of the zipped datpack.", inline=False)
            embed.add_field(name="description", value="Write a short description about your seed and why you think it's cool! Feel free to include biomes, formations, or even coordinates. You are limited to 450 characters.", inline=False)
            embed.add_field(name="screenshot", value="You must upload a screenshot (`png` only) of the seed. This `seed` command will be in the \"description\" of the image you upload. If screenshot is not relevant, it will be denied.", inline=False)
            await interaction.response.send_message(embed=embed)
        else:
            if len(interaction.message.attachments) == 0:
                await interaction.send("Please upload a screenshot in the same message as the command (And ensure it is a `png`).")
            elif len(interaction.message.attachments) > 1:
                await interaction.send("Please upload *only* one screenshot.")
            else:
                if not str(interaction.message.attachments[0]).endswith(".png"):
                    await interaction.send("Please upload only a `png` screenshot.")
                else:
                    try:
                        int(seed)
                    except:
                        await interaction.response.send_message("Your seed must be a valid integer.")
                    else:
                        if len(description) >= 450:
                            await interaction.response.send_message("Your description must be shorter than 450 characters.")
                        else:
                            await self.verify_seed(interaction, seed, description)
                            await interaction.response.send_message(f"Your seed has been submitted for approval! Once the Helpers verify your seed, you can find it at https://seedfix.stardustlabs.net/seeds/{seed}.")

    async def verify_seed(self, interaction: discord.Interaction, seed, description):
        img_data = requests.get(str(interaction.message.attachments[0])).content
        with open(f'seeds/{seed}.png', 'wb') as handler:
            handler.write(img_data)
            resize(f'seeds/{seed}.png')
        with open('resources/seeds.json', 'r') as f:
            data = json.load(f)
        info = {
            "user" : interaction.author.name,
            "description" : description
        }
        data[seed] = info
        with open('resources/seeds.json', 'w') as f:
            f.writelines(json.dumps(data, indent=2))
        
        embed = discord.Embed(color=discord.Colour.dark_teal(), title="Seed Submission")
        if interaction.author.avatar == None:
            embed.set_author(name=interaction.author.name, icon_url=self.client.user.avatar)
        else:
            embed.set_author(name=interaction.author.name, icon_url=interaction.author.avatar)
        embed.add_field(name=seed, value=description)
        file = discord.File(f"seeds/{seed}.png", filename="image.png")
        embed.set_image(url="attachment://image.png")
        embed.set_footer(text="React with ✅ to verify submission, and ❌ to deny.", icon_url=self.client.get_user(780588749825638410).avatar)
        x = await self.client.get_channel(928749390531809332).send(file=file, embed=embed)
        await x.add_reaction("✅")
        await x.add_reaction("❌")

    async def submit_seed(self, seed):
        with open('resources/seeds.json', 'r') as f:
            data = json.load(f)

        url = 'https://seedfix.stardustlabs.net/api/receive_content_from_incendy/'
        obj = data[seed]
        info = {
            'seed' : seed,
            'user' : obj["user"],
            'description' : obj["description"].replace('"', '\"'),
            'likes' : 0,
            'downloads' : 0,
            'curated' : False
        }
        info = json.dumps(info)

        data.pop(seed, None)
        with open('resources/seed.json', 'w') as f:
            f.writelines(json.dumps(data, indent=2))

        x = requests.post(url, data=info)
        print(x.text)

        os.replace(f'{os.path.expanduser("~")}/bots/Incendy/seeds/{seed}.png', f'{os.path.expanduser("~")}/stardustSite/static/images/seeds/{seed}.png')
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        msg = await self.client.get_channel(payload.channel_id).fetch_message(payload.message_id)
        if payload.channel_id == 928749390531809332 and payload.event_type == "REACTION_ADD" and not payload.member.bot and msg.author.bot and len(msg.embeds) == 1:
            if msg.embeds[0].title == "Seed Submission":
                if payload.emoji.name == "✅":
                    embed = msg.embeds[0]
                    seed = embed.fields[0].name
                    await self.submit_seed(seed)
                    embed.title = "Seed Submision - Accepted"
                    embed.set_footer(text="✅ Seed accepted.", icon_url=self.client.get_user(780588749825638410).avatar)
                    await msg.edit(embed=embed)
                elif payload.emoji.name == "❌":
                    embed = msg.embeds[0]
                    embed.title = "Seed Submision - Denied"
                    embed.set_footer(text="❌ Seed denied.", icon_url=self.client.get_user(780588749825638410).avatar)
                    await msg.edit(embed=embed)

    ### EVENTS ###

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            #SOON TM
            if message.content == '\U0001F1FB\U0001F1E8':
                await message.delete()
                await message.channel.send("<:soontm:780592610666348585>")

            #TERRALITH 1.16?!?!?
            if '1.16' in message.content.lower() and 'terralith' in message.content.lower():
                await message.add_reaction('<:NEVER:909247811256713236>')

            #Angry Ping
            if str('332701537535262720') in str(message.mentions):
                ids = [744788173128859670, 760569251618226257, 744788229579866162, 821429484674220036, 885719021176119298, 862343886864384010, 749701703938605107, 908104350218469438, 918174846318428200, 877672384872738867, 795469887790252084, 795469805678755850, 795463111561445438]
                if [role.id for role in message.author.roles if role.id in ids]:
                    await message.add_reaction('<:Kappa:852579238259327006>')
                elif 804009152288260106 in message.author.roles:
                    await message.add_reaction('<:birb:982866294187638815>')
                else:
                    await message.add_reaction('<:angryPING:875547905614839818>')
            
            #Pings Incendy
            if str('780588749825638410') in str(message.mentions):
                if random.randint(0, 20) == 1:
                    await message.add_reaction('<:cringe:828845270732374021>')
                else:
                    await message.add_reaction('👋')

            #Pastebin feature
            if len(message.attachments) > 0:
                for file in message.attachments:
                    if ".log" in file.filename or ".txt" in file.filename:

                        await file.save('resources/pastebin.txt')
                        with open('resources/pastebin.txt', 'r') as f:
                            content = f.read()
                        
                        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
                        url = "https://api.mclo.gs/1/log"
                        data = {"content": f"{content}"}
                        x = requests.post(url, data=data, headers=headers)

                        logurl = json.loads(x.text)["url"]

                        await message.reply(f"{file.filename}: {logurl}")
    
    ### ERRORS ###

    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            if interaction.command.name == "Translate to English":
                await interaction.response.send_message("Yikes! " + str(error) + ". We don't want to overwhelm the API servers...", ephemeral=True)
            elif interaction.command.name == "feedback" or interaction.command.name == "reportad":
                await interaction.response.send_message("Yikes! " + str(error), ephemeral=True)
            else:
                await interaction.response.send_message("Yikes! " + str(error) + ". If you want to keep using without a cooldown, head to <#871376111857193000>!", ephemeral=True)
        elif isinstance(error, app_commands.CheckFailure):
            if interaction.command.name == "stats" or interaction.command.name == "feedback":
                await interaction.response.send_message("This command can only be used in a bot command channel like <#871376111857193000>.", ephemeral=True)
            elif interaction.command.name == "bug":
                await interaction.response.send_message("This command is only available for Contributors!", ephemeral=True)
            else:
                raise error
        else:
            raise error

class Feedback(discord.ui.Modal, title='Incendy Feedback'):
    def __init__(self, feedback_chan: typing.Optional[typing.Union[discord.abc.GuildChannel, discord.Thread, discord.abc.PrivateChannel]]):
        super().__init__(timeout=300.0)
        self.feedback_chan = feedback_chan

    feedback = discord.ui.TextInput(
        label='Let Incendy know your feedback for her!',
        style=discord.TextStyle.long,
        placeholder='Insert feedback here...',
        required=True,
        max_length=1000
    )

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Incendy Feedback",
            description=self.feedback,
            color=discord.Colour.brand_red()
        )
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
        await self.feedback_chan.send(embed=embed)
        await interaction.response.send_message("Thanks for your feedback!")

class BugInfo(discord.ui.Modal, title='Bug Information'):
    def __init__(self, project: str):
        super().__init__(timeout=300.0)
        self.project = project
        with open('resources/keys.json', 'r') as f:
            self.pat = json.load(f)["git-pat"]
        
    bug_title = discord.ui.TextInput(
        label='The title for the bug report',
        style=discord.TextStyle.short,
        placeholder='Type title here...',
        required=True,
        max_length=100
    )
    bug_description = discord.ui.TextInput(
        label='The description for the bug report',
        style=discord.TextStyle.long,
        placeholder='Type description here...',
        required=True,
        max_length=1000
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        url = f'https://api.github.com/repos/Stardust-Labs-MC/{self.project}/issues'
        headers = {'User-Agent': 'application/vnd.github+json'}
        auth = ('catter1', self.pat)
        data = {
            'title': self.bug_title.value,
            'body': f'{self.bug_description.value}\n\n*Bug created by {interaction.user.name} via Incendy in the Stardust Labs discord server*'
        }

        response = requests.post(url, auth=auth, json=data, headers=headers)
        if response.status_code == 201:
            await interaction.response.send_message(f"Issue created successfully! You can view and add to it here: {response.json()['html_url']}")
        else:
            await interaction.response.send_message('There was an error creating the issue! Please try again, or contact catter if the issue continues.', ephemeral=True)
    
    async def on_error(self, interaction: discord.Interaction, error: Exception):
        await interaction.response.send_message("Oops! Something went wrong. Please try again.", ephemeral=True)
        raise error

async def setup(client):
    await client.add_cog(Basic(client))