import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import has_permissions
from resources import incendy

class Helps(commands.Cog):
	def __init__(self, client: incendy.IncendyBot):
		self.client = client

	async def cog_load(self):
		print(f' - {self.__cog_name__} cog loaded.')

	async def cog_unload(self):
		print(f' - {self.__cog_name__} cog unloaded.')

	### COMMANDS ###

	@app_commands.command(name="help", description="Displays the help menu")
	async def _help(self, interaction: discord.Interaction):
		""" /help """

		embed = discord.Embed(
			title='Help Menu',
			description='Welcome to the Help Menu! Read the context below to understand the descriptions for some of the commands. When you\'re ready, click any of the buttons below to view the available commands!',
			color=discord.Colour.brand_red()
		)
		
		entries = (
			('<argument>', 'The argument is __**required**__.'),
			('[argument]', 'The argument is __**optional**__.'),
			('[argument=True]', 'The argument is __**optional**__, but equal to __**True**__ if not set.'),
			('[A|B]', 'The argument can be __**either A or B**__.')
		)

		for name, value in entries:
			embed.add_field(name=name, value=value, inline=False)

		embed.set_footer(text="Buttons gone? The menu expired - do /help again!")

		await interaction.response.send_message(embed=embed, view=HelpView())

	@app_commands.command(name="close", description="Closes the support thread")
	@incendy.can_close()
	async def close(self, interaction: discord.Interaction):
		""" /close """
		
		await interaction.response.send_message("Closing thread now. Thanks!")
		await interaction.channel.edit(locked=True, archived=True)

	@app_commands.command(name="dwa", description="[ADMIN] Ask if the support question was resolved")
	@app_commands.default_permissions(administrator=True)
	@app_commands.checks.has_permissions(administrator=True)
	@has_permissions(administrator=True)
	@incendy.can_close()
	async def dwa(self, interaction: discord.Interaction):
		""" /dwa """

		await interaction.response.send_message(f"Hey <@{interaction.channel.owner_id}>, did we resolve your question? If so, close the support with `/close`. Thank you!")

	### LISTENERS ###

	@commands.Cog.listener()
	async def on_thread_create(self, thread):
		if thread.parent_id == 1045346794864918569: #1019651246078038128
			embed = discord.Embed(
				colour=discord.Colour.brand_green(),
				description="Thanks for creating a thread! Be patient, and we will answer your question when we are able to. In the meantime...\n\n• Check the FAQ by doing `/faq` to see if your question is already answered.\n• Did you **describe** your issue thoroughly?\n• Are relevant **logs** attached?\n• Is your thread **tagged** appropriately?\n• Ensure you've answered the questions outlined in our **Post Guidelines**.\n\nWhen your question is answered, please close it with `/close`. Thank you!"
			)
			embed.set_author(name="Your Support Question", icon_url="https://cdn.discordapp.com/emojis/1058423314672013382.png")

			view = discord.ui.View()
			view.add_item(CloseButton())

			await thread.send(embed=embed, view=view)

class CloseButton(discord.ui.Button):
	def __init__(self):
		super().__init__(style=discord.ButtonStyle.green, label="Close Thread", emoji="🚫")

	async def callback(self, interaction: discord.Interaction):
		if isinstance(interaction.channel, discord.Thread) and (interaction.user.id == interaction.channel.owner_id or interaction.user.guild_permissions.administrator):
			await interaction.response.send_message("Closing thread now. Thanks!")
			await interaction.channel.edit(locked=True, archived=True)
		else:
			await interaction.response.send_message("Sorry, you don't have permission to close this thread!", ephemeral=True)

class HelpView(discord.ui.View):
	def __init__(self):
		super().__init__(timeout=180)
		self.clear_items()
		self.add_item(SuperBackButton())
		self.add_item(BackButton())
		self.add_item(NextButton())
		self.add_item(SuperNextButton())
		self.add_item(ExitButton())

	async def on_timeout(self):
		self.clear_items()


class ExitButton(discord.ui.Button):
	def __init__(self):
		super().__init__(style=discord.ButtonStyle.red, label='Exit', disabled=False)
		
	async def callback(self, interaction: discord.Interaction):
		self.view.clear_items()
		await interaction.response.edit_message(view=self.view)


class BackButton(discord.ui.Button):
	def __init__(self, index='0', disabled=True):
		super().__init__(style=discord.ButtonStyle.blurple, label='❮', custom_id=index, disabled=disabled)
	
	async def callback(self, interaction: discord.Interaction):
		await do_button(self, interaction)


class NextButton(discord.ui.Button):
	def __init__(self, index='1', disabled=False):
		super().__init__(style=discord.ButtonStyle.blurple, label='❯', custom_id=index, disabled=disabled)

	async def callback(self, interaction: discord.Interaction):
		await do_button(self, interaction)


class SuperNextButton(discord.ui.Button):
	def __init__(self, index='end', disabled=False):
		super().__init__(style=discord.ButtonStyle.green, label='❯❯', custom_id=index, disabled=disabled)

	async def callback(self, interaction: discord.Interaction):
		await do_button(self, interaction)


class SuperBackButton(discord.ui.Button):
	def __init__(self, index='start', disabled=True):
		super().__init__(style=discord.ButtonStyle.green, label='❮❮', custom_id=index, disabled=disabled)

	async def callback(self, interaction: discord.Interaction):
		await do_button(self, interaction)


async def do_button(self, interaction: discord.Interaction):
	# Init info
	embed = interaction.message.embeds[0]
	is_admin = interaction.permissions.administrator

	# Get permission-friendly index and entries
	if self.custom_id == "start":
		upcoming_index = "1"
	elif self.custom_id == "end":
		upcoming_index = "6"
	else:
		upcoming_index = self.custom_id
	index = await get_index(upcoming_index, is_admin)
	entries = await update_content(index)

	# Edit embed with info
	embed.title = await get_title(index)
	embed.description = ''
	embed.clear_fields()
	for name, value in entries:
		embed.add_field(name=name, value=value, inline=False)

	# Get permission-friendly info for the new button indexes
	back_index = await get_index(str(int(index) - 1), is_admin)
	next_index = await get_index(str(int(index) + 1), is_admin)
	smart_max = await get_index("7", is_admin)
	#print(f"Current Index: {index}\nBack Index: {back_index}\nNext Index:{next_index}")

	# Set buttons correctly
	self.view.clear_items()
	if back_index == "0":
		self.view.add_item(SuperBackButton(disabled=True))
		self.view.add_item(BackButton(index=back_index, disabled=True))
	else:
		self.view.add_item(SuperBackButton(disabled=False))
		self.view.add_item(BackButton(index=back_index, disabled=False))
	if next_index == smart_max:
		self.view.add_item(NextButton(index=next_index, disabled=True))
		self.view.add_item(SuperNextButton(disabled=True))
	else:
		self.view.add_item(NextButton(index=next_index, disabled=False))
		self.view.add_item(SuperNextButton(disabled=False))
	self.view.add_item(ExitButton())

	# Edit message with embed and view
	embed.set_footer(text=f"Page {index}/{int(smart_max) - 1}")
	await interaction.response.edit_message(embed=embed, view=self.view)


async def get_index(index: str, is_admin: bool) -> str:
	# If the button presser ain't admin, reset them!
	if int(index) > 3:
		if not is_admin:
			index = "3"

	# This shouldn't happen, but just in case
	if int(index) > 7:
		if is_admin:
			index = "7"
	
	# Again, don't think it will happen, but just in case
	if int(index) <= 0:
		index = "0"

	return index


async def update_content(index: str) -> tuple:
	entries = ()

	match index:
		case "1":
			entries = (
				('help', 'Display this help menu'),
				('faq <q> [public=None]', 'Choose from a large list of FAQs to display'),
				('qp <post>', 'Posts a Quick Post: similar to an FAQ, but not directly related to support'),
				('wiki <action>', 'Do various **action**s through the Stardust Labs\' wiki, such as searching or uploading images')
			)
		case "2":
			entries = (
				('bug <project>', '**Contributors only.** Opens a bug report for a Stardust Labs **project**'),
				('close', 'Only for support threads. Closes the thread if user is done with it'),
				('contest <action> [submission]', 'Posts a **submission** to the ongoing contest, if there is one'),
				('discord <server>', 'Sends the Discord invite link from a list of datapack-relevant Discord server'),
				('remindme <time> <reminder>', 'Sets a reminder. Time should be formatted like this example: `12s` where `s` means `seconds`, supported from seconds to days'),
				('textlinks', 'Displays all available textlinks')
			)
		case "3":
			entries = (
				('changelog', 'View Incendy\'s changelog'),
				('feedback', 'Send feedback about Incendy so she can improve herself'),
				('incendy', 'Shows information about Incendy'),
				('ping', 'Shows you your connection latency'),
				('reportad <image>', 'If you see a bad/inappropriate ad on [our website](https://www.stardustlabs.net/), report an **image** of it here'),
				('server <valid> [image]', 'Advertises a server in <#756923587339878420>. Set **valid** to true if you\'ve read the rules. You will then be prompted for the server\'s name, ip, description, and an optional discord link and promotional **image**'),
				('stats [member]', 'Displays the stats for Stardust Labs and the Discord server, or optionally, a **member**')
			)
		case "4":
			entries = (
				('dwa', 'Only for support threads. Prompts user to close the thread with "**D**id **W**e **A**nswer your question?"'),
				('jschlatt [strings|minutes]', 'Purges all users matching **strings** in their names that joined in the past **minutes**. You can specify strings, minutes, or both; but not neither'),
				('shutup <user> [days=9999]', 'Times out a **user** for an __optional__ specified amount of **days**')
			)
		case "5":
			entries = (
				('cog <load|unload|reload> <cog>', 'Performs the specified **action** on a **cog**'),
				('github <project> <pack_ver> <mc_ver> <datapack>', 'Updates the **project**\'s GitHub repo, and creates a release with the provided **pack** and **mc** versions'),
				('role', 'Gives all users Member that do not have any roles')
			)
		case "6":
			entries = (
				('announce', 'catter\'s quick-command to post a message in current channel as Incendy'),
				('biome', 'Posts the Incendy message for <#916730198437814282>'),
				('library', 'Posts the Incendy message for <#900598465430716426>'),
				('featured', 'Posts the Incendy message for <#987857911252402206>'),
				('serverrules', 'Posts the Incendy message for <#756923587339878420>'),
				('stardustmc', 'Posts the Incendy message for <#1002721350143721603>')
			)
	
	return entries


async def get_title(index: str) -> str:
	match index:
		case "1":
			title = "Essential Commands"
		case "2":
			title = "Community Commands"
		case "3":
			title = "Misc Commands"
		case "4":
			title = "Admin (Moderation)"
		case "5":
			title = "Essential (Helper)"
		case "6":
			title = "Essential (Bulletin)"
		case _:
			title = index
	
	return title


async def setup(client):
	await client.add_cog(Helps(client))