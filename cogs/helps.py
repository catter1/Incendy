import discord
import logging
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import has_permissions
from libraries import incendy
import libraries.constants as Constants

class Helps(commands.Cog):
	def __init__(self, client: incendy.IncendyBot):
		self.client = client

	async def cog_load(self):
		logging.info(f'> {self.__cog_name__} cog loaded')

	async def cog_unload(self):
		logging.info(f'> {self.__cog_name__} cog unloaded')

	### COMMANDS ###

	@app_commands.command(name="help", description="Displays the help menu")
	@app_commands.describe(
		public="Whether to make the Help menu visible to everyone. Keep it False unless you're trying to share!"
	)
	async def _help(self, interaction: discord.Interaction, public: bool = False):
		""" /help """

		public = not public
		embed = discord.Embed(
			title="Essential Commands",
			color=discord.Colour.brand_red()
		)
		
		entries = (
			('help', 'Display this help menu'),
			('faq <faq> [public=None]', 'Choose from a large list of FAQs to display'),
			('qp <qp>', 'Posts a Quick Post: similar to an FAQ, but not directly related to support'),
			('wiki <search|upload>', 'Do various actions through the Stardust Labs\' wiki')
		)

		for name, value in entries:
			embed.add_field(name=name, value=value, inline=False)
		
		if interaction.permissions.administrator:
			embed.set_footer(text="Page 1/6")
		else:
			embed.set_footer(text="Page 1/3")

		await interaction.response.send_message(embed=embed, view=HelpView(), ephemeral=public)

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
	async def on_thread_create(self, thread: discord.Thread):
		if thread.parent_id == Constants.Channel.SUPPORT:
			embed = discord.Embed(
				colour=discord.Colour.brand_green(),
				description="Thanks for creating a thread! Be patient, and we will answer your question when we are able to. In the meantime...\n\n• Check the FAQ by doing `/faq` to see if your question is already answered.\n• Did you **describe** your issue thoroughly?\n• Are relevant **logs** attached?\n• Is your thread **tagged** appropriately?\n• Ensure you've answered the questions outlined in our **Post Guidelines**.\n\nWhen your question is answered, please close it with `/close`, or click the button. Thank you!"
			)
			embed.set_author(name="Your Support Question", icon_url="https://cdn.discordapp.com/emojis/1058423314672013382.png")

			view = discord.ui.View()
			view.add_item(CloseButton())

			await thread.send(embed=embed, view=view)
			
		else:
			await thread.join()
		
		message = thread.get_partial_message(thread.id)
		try:
			await message.pin()
		except discord.HTTPException:
			pass

class CloseButton(discord.ui.Button):
	def __init__(self):
		super().__init__(style=discord.ButtonStyle.green, label="Close Thread", emoji="🚫")

	async def callback(self, interaction: discord.Interaction):
		if isinstance(interaction.channel, discord.Thread) and (interaction.user.id == interaction.channel.owner_id or interaction.user.id == interaction.user.guild_permissions.administrator):
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
	def __init__(self, index='2', disabled=False):
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
	back_index = str(int(await get_index(index, is_admin)) - 1)
	next_index = str(int(await get_index(index, is_admin)) + 1)
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
	if int(next_index) == int(smart_max) + 1:
		self.view.add_item(NextButton(index=next_index, disabled=True))
		self.view.add_item(SuperNextButton(disabled=True))
	else:
		self.view.add_item(NextButton(index=next_index, disabled=False))
		self.view.add_item(SuperNextButton(disabled=False))
	self.view.add_item(ExitButton())

	# Edit message with embed and view
	embed.set_footer(text=f"Page {index}/{int(smart_max)}")
	await interaction.response.edit_message(embed=embed, view=self.view)


async def get_index(index: str, is_admin: bool) -> str:
	# If the button presser ain't admin, reset them!
	if int(index) > 3:
		if not is_admin:
			index = "3"

	# This shouldn't happen, but just in case
	if int(index) > 6:
		if is_admin:
			index = "6"
	
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
				('faq <faq> [public=None]', 'Choose from a large list of FAQs to display'),
				('qp <qp>', 'Posts a Quick Post: similar to an FAQ, but not directly related to support'),
				('wiki <search|upload>', 'Do various actions through the Stardust Labs\' wiki')
			)
		case "2":
			entries = (
				('issue <project>', 'Opens an issue for a Stardust Labs **project**'),
				('close', 'Only for support threads. Closes the thread if user is done with it'),
				('contest <action> [submission]', 'Posts a **submission** to the ongoing contest, if there is one'),
				('datapack <analyze|mcmeta>', 'Various datapack development related commands'),
				('discord <server>', 'Sends the Discord invite link from a list of datapack-relevant Discord server'),
				('remindme <time> <reminder>', 'Sets a reminder. Time should be formatted like this example: `12s` where `s` means `seconds`, supported from seconds to days'),
				('textlinks', 'Displays all available textlinks')
			)
		case "3":
			entries = (
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
				('role', 'Gives all users Member that do not have any roles'),
				('thread <thread> <forum>', 'Moves any **thread** from its channel into a **forum** channel'),
				('upload <project> <archive>', 'Uploads the **project** to any distribution platform, accepting either a datapack or mod **archive** file')
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
			title = "Admin (Other)"
		case "6":
			title = "Admin (Bulletin)"
		case _:
			title = index
	
	return title


async def setup(client):
	await client.add_cog(Helps(client))