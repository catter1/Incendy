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
		g: discord.Thread
		g = self.client.get_channel(1036998149954351105)
		m = await g.fetch_message(1092099856954306580)
		await m.delete()
		#await interaction.channel.send("Hey y'all! It's getting close to a certain holiday that certain people may celebrate, and I wanted to give everyone the greatest gift of all: knowledge of cybersecurity :sunglasses:\n\nDuring the holidays especially, there are a lot of scam links. Discord especially... I already banned one person who's account got hacked and was sending phishing links (free nitro). Luckily, this person was able to get their account back. But you may not be so lucky.\n\nFirst of all, **one** click is all it takes. Just one. That can compromise your entire account, even if you don't explicitly say your private info. Outside of Discord, it can lead to more damage. It could instantly install malware, steal all accounts you are logged into (or passwords that your browser saves), and use all communication means (like email) that you have to phish more people. If your friend sends you a link from their actual email/Discord to this cool online Christmas card they made for you, wouldn't you click it? Always check the link first.\n\nAnd finally, scams aren't for stupid people. You don't have to be stupid to fall for scams. Although some scams are blatant, others are very well crafted. Here is a nice video (https://www.youtube.com/watch?v=ntrGrfvvkII) by Atomic Shrimp, who explains it quite nicely. Links are a lot more dangerous than you may think.\n\nAnyways, that's all. I wish that you will all be safe this holiday season, and for now on. It's a pleasure to be your friendly discord bot, and I love every minute of it here \<3")

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


	### LISTENERS ###

	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
		if payload.channel_id == 1001300888427700314:
			if not payload.member.bot and payload.emoji.name == "stardust":
				guild = self.client.get_guild(738046951236567162)
				role = guild.get_role(1045484675184984114)
				await payload.member.add_roles(role)

	@commands.Cog.listener()
	async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
		guild = self.client.get_guild(738046951236567162)
		user = guild.get_member(payload.user_id)

		if payload.channel_id == 1001300888427700314:
			if not user.bot and payload.emoji.name == "stardust":
				role = guild.get_role(1045484675184984114)
				await user.remove_roles(role)

### BUTTONS ###

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