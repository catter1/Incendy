### NOTICE ###
# This is simply an archive of random bits of code!
# This command ispermanently removed, due to
# new visions for the Seedfix website.
# It *may* come back later, but in a different form.
# For now, this is just a place to store the disgusting
# code so it is out of my face.

import discord
from discord import app_commands
from discord.ext import commands
import requests
import json
import os
from libraries.image_tools import resize

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


old_seed_json = {
  "version": "2.0.10",
  "-317963479": {
    "user": "catter",
    "description": "This amazing seed has 120 out of all 124 biomes within 4k blocks of spawn!",
    "version": "2.0.10"
  },
  "3118923217130655594": {
    "user": "iFury",
    "description": "A beautiful shield biome with good vegetation and great for starting a survival world!",
    "version": "2.0.10"
  },
  "7478368035381388288": {
    "user": "Spence",
    "description": "Spawn in a lush valley surrounded by some of the best biomes Terralith has to offer! Lavender Valley to the east, blooming plateau and a forested highlands to the west.",
    "version": "2.0.10"
  },
  "2863773288559819620": {
    "user": "Townie",
    "description": "this seed includes a bowl caldera and forested highlands, but also in the surrounding area: a fortified village, Yellowstone, Siberian taiga, shield clearing, sakura grove, ice spikes, volcano, jungle, and a plain to spawn in. This is a perfect survival seed with a great biome diversity"
  },
  "-944961380": {
    "user": "Shawn",
    "description": "Spawn on a beautiful meadow plateau, with many canyons and other plateau's around, as well as many low highlands. There are so many great spots to build a base/town with amazing mountain/hill backdrops. . Should have every biome within 15k, there is a village 450 blocks from spawn, and another within 800.",
    "version": "2.0.10"
  },
  "78121119": {
    "user": "Tera",
    "description": "You will spawn on a small island placed with, around it, most of the available Terralith biomes and Terralith/Vanilla terrain you can encounter in a 10000 blocks radius. A Skyland next to spawn, multiple villages in the east, two perfectly generated volcanoes near a village up north, and at -2550 80 1550 you will find a huge Highlands biome that stops near a Canyon terrain region, creating a small island inside a river circle and next to it, an enormous cave entrance, with a Fungal cave, Dripstone cave and Frostfire cave further down.",
    "version": "2.0.10"
  },
  "-700459161": {
    "user": "Kuma",
    "description": "You spawn on a rocky mountain and met with very hilly Old Growth Spruce Forests and Yellowstones. The Rocky Mountains provide iron ores to help get your Minecraft adventure started! There is a rocky mountain crater near spawn.",
    "version": "2.0.10"
  },
  "3668461024515299453": {
    "user": "theAstra",
    "description": "At x - 1980 z - 5658 you will find an impressive floating archipelago of 9 Skylands. This archipelago dons an impressive three of the four season types and is an incredibly breathtaking sight to behold.",
    "version": "2.0.10"
  },
  "4350721007981905942": {
    "user": "LimeSplatus",
    "description": "A massive rocky mountain so tall its tallest peaks reach y219! You'll also discover a ginormous, gaping hole on one side of the mountain. Aswell as the peaks, you'll find your spawn surronded by a siberian taiga, yellowstone, dark forest and sakura grove",
    "version": "2.0.10"
  },
  "-3093879674648247331": {
    "user": "Baconbacon123",
    "description": "Spawn in the middle of a large meadow, nearby two villages, and surrounded on all sides by cliffs that lead down to rivers."
  },
  "-3388590163572487532": {
    "user": "Xhong Zina",
    "description": "Woodland Mansion very close to spawn!"
  },
  "-2823420731214867186": {
    "user": "Townie",
    "description": "there are 5 villages in this beautiful vista of a spawn, with countless mountains rising from a great plains biome. Head north and you will find more rocky terrain, with Yellowstone and a caldera."
  },
  "91827588818737371675": {
    "user": "ShulkZ__",
    "description": "Nice highlands spawn"
  },
  "-1563338999319242958": {
    "user": "KB_Q",
    "description": "Amazing jungle spawn with huge canyons of Terralith's most lush biomes such as Amethyst canyon, lush valley etc., along with large caverns filled with lush caves."
  },
  "6377241606867368960": {
    "user": "Starmute",
    "description": "A nice volcanic island spawn with quite a few biomes around!"
  },
  "83544775": {
    "user": "Cozy",
    "description": "Spawn in a village, explore and you'll find this beautiful canyon! (screenshot taken at coordinates: -313 75 -135)"
  },
  "-7045100911261610632": {
    "user": "Whodini",
    "description": "Fantasy Land"
  },
  "271022739846418583": {
    "user": "Airisu",
    "description": "Spawns in a small flat area except you're surrounded by mountains, especially a really tall Windswept Hills area that leads some a really chaotic windswept spirals\nThere are also other mountainous areas nearby"
  },
  "-9168064516517828490": {
    "user": "Skull_Fury",
    "description": "Spawn in front of some big Highlands valley. Near at the spawn there are two villages, plains and taiga villages. Near the plains one there is a lava lake, useful for speedrun. And again, under the plains village there are an Ice and Infested cave."
  },
  "7043943473785639815": {
    "user": "Flyworm Tomato",
    "description": "A giant Infested cave hole in a mountain, with a small village next to it. Inside is a mineshaft and Frostfire caves underneath. There is also a Moonlight grove close to spawn.  X= 237, Z= 241"
  },
  "4609199362958594652": {
    "user": "CaptMicrowave",
    "description": "Spawn directly into one of the cool new villages, surrounded by a forested highlands. Also nearby  is a second village at X 260 Z -130, a sunken ship, and abandoned portal."
  },
  "-2092331281844271208": {
    "user": "Enterenn",
    "description": "epic mega cave right below the spawn"
  },
  "6327946854225096385": {
    "user": "Raps",
    "description": "Very Big Arche at x -1307 and z 1724"
  },
  "460628901": {
    "user": "MrDude",
    "description": "there are 2 villages surrounded by snow mountains, right by spawn"
  },
  "3607545659191568079": {
    "user": "StrangeOne101",
    "description": "Beautiful, blooming valleys. High mountains, a lake at the bottom of one valley, and plateaus with lots of space. A seed that really showcases beautiful 1.18 terrain"
  },
  "9189599039221578247": {
    "user": "Ambassador Pineapple",
    "description": "Big 'ol hole not 300 blocks from spawn, next to a Jungle, a Savannah, and a massive Desert."
  },
  "0": {
    "user": "Skull_Fury",
    "description": "A modest cliff at the spawn."
  },
  "-552277208461250522": {
    "user": "tan_x_dx",
    "description": "Spawns you in the midst of a diverse array of pristine biomes and incredible mountains, all within 1000 blocks from spawn! Here's a bunch of screenshots with coords attached: https://imgur.com/a/vd8ADWS"
  },
  "-957356646": {
    "user": "tan_x_dx",
    "description": "Spawns you directly on the side of a gigantic badlands arch. Perfect for an evil lair! More pictures at https://imgur.com/a/8DLrvP7"
  },
  "-8375627511374355131": {
    "user": "Ordana \ud83d\udc1d",
    "description": "Gigantic, nearly entirely enclosed hollow dome of terracotta around a Red Oasis at -1362, 5669"
  },
  "09873463964": {
    "user": "Doom Destroyer",
    "description": "Hi! This is a test do not accept."
  },
  "-1939777557415907581": {
    "user": "RockFucker (He/They)",
    "description": "to get certain parts of this install the Immersive Weathering mod (fabric 0.13.3 game ver 1.18.2)"
  },
  "-8284977584069388045": {
    "user": "KB_Q",
    "description": "spawn in a highlands biome with a savanna badlands biome nearby, and a massive megacave system right below spawn, that extends thousands of blocks horizontally."
  },
  "333": {
    "user": "deuteronomy",
    "description": "Want to spawn on an Amethyst Rainforest Island with a Lush Cave nearby? No? Ok.\nWell at least there's an ocean monument nearby.\n\n(I dont have beef pc and was in a rush ok)"
  },
  "6553155458600003024": {
    "user": "twixstix",
    "description": "I think this is a pretty lucky seed - not only is there a Warped Mesa less than 200 blocks from spawn, but there's a Summer Skyland right next to it and a Ocean Monument directly underneath. Screenshot taken at x180 z-130."
  },
  "-8701902305087913335": {
    "user": "Kalikars",
    "description": "Gorgeous valley/mountain spawn with a variety of foliage-changing biomes in every direction. To top it off is a village right at spawn, nestled on a cliff plateau."
  },
  "5216508878210185211": {
    "user": "ShockNaught",
    "description": "Beautiful forested temperate biomes, with an ocean and village nearby."
  },
  "-1671780555917268290": {
    "user": "restingphantom",
    "description": "you spawn in the village 2 blocks next to a castle"
  },
  "3966743972808517464": {
    "user": "Chev",
    "description": "really interesting (and also a paint to get to) village found at ~ 2531, ~, 1697. opon starting the world, you can also find another fortified village, along with many others"
  },
  "-3322929792365038537": {
    "user": "Sazulo",
    "description": "Just north of the spawn point there is an alpine meadow with a mushroom cave and mineshaft at the bottom,  but the real interesting thing is to continue behind that. There is a meadow ( as seen on the screenshot ) with a mega infested cave and with two villages nearby."
  },
  "-8893950782768070013": {
    "user": "nythr",
    "description": "A strange icy spire pokes out from the ground right at spawn. Biomes near spawn include Alpine Highlands, Snowy Taiga, Mega Taiga, Frozen Ocean, Yellowstone and Forested Highland."
  },
  "-2144052612": {
    "user": "A\ud835\udd26\u0e4ft\u0433\u01ff\u0e20",
    "description": "A mountain island spawn with some great biomes and structures around ! This is really a showcase for Cave and Cliffs"
  },
  "5952484189621697232": {
    "user": "t4pyR",
    "description": "A little ice fishing cabin surrounded by huge mountains, dense forests and ice spikes with two rivers joining into a frozen lake which the house is built on, there is a village on the mountain to the left.\nVERY far from spawn, at -22059 / 12300. Large biomes ON"
  },
  "-1162934693": {
    "user": "Miner",
    "description": "Huge badlands dotted with painted badlands and granite cliffs, and a warped badlands; both around X: 4199 Z:1515. A warm ocean with lots of coral cuts through. This area is the motherlode of stained clay as well as scenic backgrounds."
  },
  "3750": {
    "user": "destro",
    "description": "comically large spring skylands\nspans about 57 chunks\ncoords: 26594 225 -14037"
  },
  "6310146535764099255": {
    "user": "argo lost 2FA access",
    "description": "Spawn on side of small lake, surrounded by low hills, with island in the middle, with a village either side of it!"
  },
  "-4848521006353683848": {
    "user": "Judiax",
    "description": "Spawn on a jungle tree, with a giant canyon view with giant waterfalls that lead to a ocean, with various structures and biomes such as a dense jungle where you spawn"
  },
  "-396414569": {
    "user": "Stormtalon",
    "description": "Spawn in a bamboo jungle valley, with a badlands plateau to the NE.  Across the plateau is a desert village, and continuing to the NE is a jungle with scars from old volcanic eruptions and a jungle mountain with an absolutely enormous cavern beneath it, visible thru an opening on the south side.  (1.19 terralith)"
  },
  "-6869893195326409591": {
    "user": "Pengin",
    "description": "Not based at spawn, but located at [830x ~y -830z] there is a ravine which spans from a mountaintop to bedrock then proceeds to expand in a cave which expands over what is presumed to be a 1000 x 1000 block area centered on the aforementioned coordinates (1.19 Terralith)"
  },
  "6648185367752580446": {
    "user": "Sticks",
    "description": "spawn and theres also a fortified village in 112 120 380 (literally in front of you where you spawn)"
  },
  "2758705742394658062": {
    "user": "WAJ",
    "description": "cord's near -4400 -5500"
  },
  "6675176345072873672": {
    "user": "Harrier",
    "description": "Huge Lush Cave intersecting two villages (actually found by Tera) 1.19"
  },
  "1381254027": {
    "user": "SpluoSplatus",
    "description": "A stunning spawn atop a fractured savanna peak, surronded by an orchid swamp, and a lush valley (Seed also works if you type in \"Starmute\" no quotes into the seed field)"
  }
}

old_seeds_json = {
  "version": "2.0.10",
  "-317963479": {
    "user": "catter",
    "description": "This amazing seed has 120 out of all 124 biomes within 4k blocks of spawn!",
    "version": "2.0.10"
  },
  "3118923217130655594": {
    "user": "iFury",
    "description": "A beautiful shield biome with good vegetation and great for starting a survival world!",
    "version": "2.0.10"
  },
  "7478368035381388288": {
    "user": "Spence",
    "description": "Spawn in a lush valley surrounded by some of the best biomes Terralith has to offer! Lavender Valley to the east, blooming plateau and a forested highlands to the west.",
    "version": "2.0.10"
  },
  "2863773288559819620": {
    "user": "Townie",
    "description": "this seed includes a bowl caldera and forested highlands, but also in the surrounding area: a fortified village, Yellowstone, Siberian taiga, shield clearing, sakura grove, ice spikes, volcano, jungle, and a plain to spawn in. This is a perfect survival seed with a great biome diversity"
  },
  "-944961380": {
    "user": "Shawn",
    "description": "Spawn on a beautiful meadow plateau, with many canyons and other plateau's around, as well as many low highlands. There are so many great spots to build a base/town with amazing mountain/hill backdrops. . Should have every biome within 15k, there is a village 450 blocks from spawn, and another within 800.",
    "version": "2.0.10"
  },
  "78121119": {
    "user": "Tera",
    "description": "You will spawn on a small island placed with, around it, most of the available Terralith biomes and Terralith/Vanilla terrain you can encounter in a 10000 blocks radius. A Skyland next to spawn, multiple villages in the east, two perfectly generated volcanoes near a village up north, and at -2550 80 1550 you will find a huge Highlands biome that stops near a Canyon terrain region, creating a small island inside a river circle and next to it, an enormous cave entrance, with a Fungal cave, Dripstone cave and Frostfire cave further down.",
    "version": "2.0.10"
  },
  "-700459161": {
    "user": "Kuma",
    "description": "You spawn on a rocky mountain and met with very hilly Old Growth Spruce Forests and Yellowstones. The Rocky Mountains provide iron ores to help get your Minecraft adventure started! There is a rocky mountain crater near spawn.",
    "version": "2.0.10"
  },
  "3668461024515299453": {
    "user": "theAstra",
    "description": "At x - 1980 z - 5658 you will find an impressive floating archipelago of 9 Skylands. This archipelago dons an impressive three of the four season types and is an incredibly breathtaking sight to behold.",
    "version": "2.0.10"
  },
  "4350721007981905942": {
    "user": "LimeSplatus",
    "description": "A massive rocky mountain so tall its tallest peaks reach y219! You'll also discover a ginormous, gaping hole on one side of the mountain. Aswell as the peaks, you'll find your spawn surronded by a siberian taiga, yellowstone, dark forest and sakura grove",
    "version": "2.0.10"
  },
  "-3093879674648247331": {
    "user": "Baconbacon123",
    "description": "Spawn in the middle of a large meadow, nearby two villages, and surrounded on all sides by cliffs that lead down to rivers."
  },
  "-3388590163572487532": {
    "user": "Xhong Zina",
    "description": "Woodland Mansion very close to spawn!"
  },
  "-2823420731214867186": {
    "user": "Townie",
    "description": "there are 5 villages in this beautiful vista of a spawn, with countless mountains rising from a great plains biome. Head north and you will find more rocky terrain, with Yellowstone and a caldera."
  },
  "91827588818737371675": {
    "user": "ShulkZ__",
    "description": "Nice highlands spawn"
  },
  "-1563338999319242958": {
    "user": "KB_Q",
    "description": "Amazing jungle spawn with huge canyons of Terralith's most lush biomes such as Amethyst canyon, lush valley etc., along with large caverns filled with lush caves."
  },
  "6377241606867368960": {
    "user": "Starmute",
    "description": "A nice volcanic island spawn with quite a few biomes around!"
  },
  "83544775": {
    "user": "Cozy",
    "description": "Spawn in a village, explore and you'll find this beautiful canyon! (screenshot taken at coordinates: -313 75 -135)"
  },
  "-7045100911261610632": {
    "user": "Whodini",
    "description": "Fantasy Land"
  },
  "271022739846418583": {
    "user": "Airisu",
    "description": "Spawns in a small flat area except you're surrounded by mountains, especially a really tall Windswept Hills area that leads some a really chaotic windswept spirals\nThere are also other mountainous areas nearby"
  },
  "-9168064516517828490": {
    "user": "Skull_Fury",
    "description": "Spawn in front of some big Highlands valley. Near at the spawn there are two villages, plains and taiga villages. Near the plains one there is a lava lake, useful for speedrun. And again, under the plains village there are an Ice and Infested cave."
  },
  "7043943473785639815": {
    "user": "Flyworm Tomato",
    "description": "A giant Infested cave hole in a mountain, with a small village next to it. Inside is a mineshaft and Frostfire caves underneath. There is also a Moonlight grove close to spawn.  X= 237, Z= 241"
  },
  "4609199362958594652": {
    "user": "CaptMicrowave",
    "description": "Spawn directly into one of the cool new villages, surrounded by a forested highlands. Also nearby  is a second village at X 260 Z -130, a sunken ship, and abandoned portal."
  },
  "-2092331281844271208": {
    "user": "Enterenn",
    "description": "epic mega cave right below the spawn"
  },
  "6327946854225096385": {
    "user": "Raps",
    "description": "Very Big Arche at x -1307 and z 1724"
  },
  "460628901": {
    "user": "MrDude",
    "description": "there are 2 villages surrounded by snow mountains, right by spawn"
  },
  "3607545659191568079": {
    "user": "StrangeOne101",
    "description": "Beautiful, blooming valleys. High mountains, a lake at the bottom of one valley, and plateaus with lots of space. A seed that really showcases beautiful 1.18 terrain"
  },
  "9189599039221578247": {
    "user": "Ambassador Pineapple",
    "description": "Big 'ol hole not 300 blocks from spawn, next to a Jungle, a Savannah, and a massive Desert."
  },
  "0": {
    "user": "Skull_Fury",
    "description": "A modest cliff at the spawn."
  },
  "-552277208461250522": {
    "user": "tan_x_dx",
    "description": "Spawns you in the midst of a diverse array of pristine biomes and incredible mountains, all within 1000 blocks from spawn! Here's a bunch of screenshots with coords attached: https://imgur.com/a/vd8ADWS"
  },
  "-957356646": {
    "user": "tan_x_dx",
    "description": "Spawns you directly on the side of a gigantic badlands arch. Perfect for an evil lair! More pictures at https://imgur.com/a/8DLrvP7"
  },
  "-8375627511374355131": {
    "user": "Ordana \ud83d\udc1d",
    "description": "Gigantic, nearly entirely enclosed hollow dome of terracotta around a Red Oasis at -1362, 5669"
  },
  "09873463964": {
    "user": "Doom Destroyer",
    "description": "Hi! This is a test do not accept."
  },
  "-1939777557415907581": {
    "user": "RockFucker (He/They)",
    "description": "to get certain parts of this install the Immersive Weathering mod (fabric 0.13.3 game ver 1.18.2)"
  },
  "-8284977584069388045": {
    "user": "KB_Q",
    "description": "spawn in a highlands biome with a savanna badlands biome nearby, and a massive megacave system right below spawn, that extends thousands of blocks horizontally."
  },
  "333": {
    "user": "deuteronomy",
    "description": "Want to spawn on an Amethyst Rainforest Island with a Lush Cave nearby? No? Ok.\nWell at least there's an ocean monument nearby.\n\n(I dont have beef pc and was in a rush ok)"
  },
  "6553155458600003024": {
    "user": "twixstix",
    "description": "I think this is a pretty lucky seed - not only is there a Warped Mesa less than 200 blocks from spawn, but there's a Summer Skyland right next to it and a Ocean Monument directly underneath. Screenshot taken at x180 z-130."
  },
  "-8701902305087913335": {
    "user": "Kalikars",
    "description": "Gorgeous valley/mountain spawn with a variety of foliage-changing biomes in every direction. To top it off is a village right at spawn, nestled on a cliff plateau."
  },
  "5216508878210185211": {
    "user": "ShockNaught",
    "description": "Beautiful forested temperate biomes, with an ocean and village nearby."
  },
  "-1671780555917268290": {
    "user": "restingphantom",
    "description": "you spawn in the village 2 blocks next to a castle"
  },
  "3966743972808517464": {
    "user": "Chev",
    "description": "really interesting (and also a paint to get to) village found at ~ 2531, ~, 1697. opon starting the world, you can also find another fortified village, along with many others"
  },
  "-3322929792365038537": {
    "user": "Sazulo",
    "description": "Just north of the spawn point there is an alpine meadow with a mushroom cave and mineshaft at the bottom,  but the real interesting thing is to continue behind that. There is a meadow ( as seen on the screenshot ) with a mega infested cave and with two villages nearby."
  },
  "-8893950782768070013": {
    "user": "nythr",
    "description": "A strange icy spire pokes out from the ground right at spawn. Biomes near spawn include Alpine Highlands, Snowy Taiga, Mega Taiga, Frozen Ocean, Yellowstone and Forested Highland."
  },
  "-2144052612": {
    "user": "A\ud835\udd26\u0e4ft\u0433\u01ff\u0e20",
    "description": "A mountain island spawn with some great biomes and structures around ! This is really a showcase for Cave and Cliffs"
  },
  "5952484189621697232": {
    "user": "t4pyR",
    "description": "A little ice fishing cabin surrounded by huge mountains, dense forests and ice spikes with two rivers joining into a frozen lake which the house is built on, there is a village on the mountain to the left.\nVERY far from spawn, at -22059 / 12300. Large biomes ON"
  },
  "-1162934693": {
    "user": "Miner",
    "description": "Huge badlands dotted with painted badlands and granite cliffs, and a warped badlands; both around X: 4199 Z:1515. A warm ocean with lots of coral cuts through. This area is the motherlode of stained clay as well as scenic backgrounds."
  },
  "3750": {
    "user": "destro",
    "description": "comically large spring skylands\nspans about 57 chunks\ncoords: 26594 225 -14037"
  },
  "6310146535764099255": {
    "user": "argo lost 2FA access",
    "description": "Spawn on side of small lake, surrounded by low hills, with island in the middle, with a village either side of it!"
  },
  "-4848521006353683848": {
    "user": "Judiax",
    "description": "Spawn on a jungle tree, with a giant canyon view with giant waterfalls that lead to a ocean, with various structures and biomes such as a dense jungle where you spawn"
  },
  "-396414569": {
    "user": "Stormtalon",
    "description": "Spawn in a bamboo jungle valley, with a badlands plateau to the NE.  Across the plateau is a desert village, and continuing to the NE is a jungle with scars from old volcanic eruptions and a jungle mountain with an absolutely enormous cavern beneath it, visible thru an opening on the south side.  (1.19 terralith)"
  },
  "-6869893195326409591": {
    "user": "Pengin",
    "description": "Not based at spawn, but located at [830x ~y -830z] there is a ravine which spans from a mountaintop to bedrock then proceeds to expand in a cave which expands over what is presumed to be a 1000 x 1000 block area centered on the aforementioned coordinates (1.19 Terralith)"
  },
  "6648185367752580446": {
    "user": "Sticks",
    "description": "spawn and theres also a fortified village in 112 120 380 (literally in front of you where you spawn)"
  },
  "2758705742394658062": {
    "user": "WAJ",
    "description": "cord's near -4400 -5500"
  },
  "6675176345072873672": {
    "user": "Harrier",
    "description": "Huge Lush Cave intersecting two villages (actually found by Tera) 1.19"
  },
  "1309364421585486824": {
    "user": "||\u14b7\u2237 \u14b2\ud835\ude79\u14b2",
    "description": "Spawn on top a volcano with a neighboring bamboo jungle mountain with a awesome cove and a small exit (image of cove) 1.18 terralith"
  },
  "1381254027": {
    "user": "SpluoSplatus",
    "description": "A stunning spawn atop a fractured savanna peak, surronded by an orchid swamp, and a lush valley (Seed also works if you type in \"Starmute\" no quotes into the seed field)"
  },
  "-1008858708006401318": {
    "user": "Townie",
    "description": "Two mainland islands separated by the ocean, featuring some of the best biomes in the mod. Yellowstone, Shield, White Cliffs, Forested Highlands, all the Jungle variants, Bryce Canyon + Desert. A mega village and woodland mansion can also be found. I made sure the world overall is good, rather than just a specific feature. Great seed for a survival world with friends."
  },
  "-6145466479441839070": {
    "user": "Sija",
    "description": "In this seed, the spawn is a beautiful Tropical jungle. And just south east, there is a big Sakura grove and Amethyst rainforest!"
  }
}