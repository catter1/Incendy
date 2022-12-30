import discord
import json
import datetime
from discord import app_commands
from discord.utils import get
from discord.ext import commands
from discord.ext.commands import has_permissions

class Roles(commands.Cog):
	def __init__(self, client):
		self.client = client

	async def cog_load(self):
		print(f' - {self.__cog_name__} cog loaded.')

	async def cog_unload(self):
		print(f' - {self.__cog_name__} cog unloaded.')

	@commands.Cog.listener()
	async def on_member_join(self, member):
		with open("resources/settings.json", 'r') as f:
			settings = json.load(f)
		
		if settings["locked"] == False:
			guild = self.client.get_guild(738046951236567162)
			role = guild.get_role(744790468428300330)
			await member.add_roles(role)

		# Check if user tries to circumvent SHUTUP
		with open('resources/timeout.json') as f:
			log = json.load(f)
		if str(member.id) in log["members"].keys():
			future = datetime.timedelta(days=28)
			await member.timeout(until=future, reason="Shutup loser")

	@app_commands.command(name="role", description="[ADMIN] Gives Members role to all users missing a role")
	@app_commands.default_permissions(administrator=True)
	@app_commands.checks.has_permissions(administrator=True)
	async def role(self, interaction: discord.Interaction):
		""" /role """
		
		guild = self.client.get_guild(738046951236567162)
		role = guild.get_role(744790468428300330)
		fixcount = 0
		
		await interaction.response.defer()
		async for member in guild.fetch_members(limit=None):
			if len(member.roles) <= 1:
				fixcount += 1
				await member.add_roles(role)
		
		await interaction.followup.send(f'**{fixcount}** members have been given the `Member` role.')

	@app_commands.command(name="lockdown", description="[ADMIN] Toggles the prevention of all new members from obtaining the Member role")
	@app_commands.default_permissions(administrator=True)
	@app_commands.checks.has_permissions(administrator=True)
	async def lockdown(self, interaction: discord.Interaction):
		""" /lockdown """

		with open("resources/settings.json", 'r') as f:
			settings = json.load(f)
		
		embed = discord.Embed()
		embed.set_author(name="Lockdown")
		if settings["locked"] == False:
			embed.color = discord.Colour.red()
			embed.add_field(name="**ENABLED**", value="New people who join will no longer receive the member role!")
			settings["locked"] = True
		else:
			embed.color = discord.Colour.green()
			embed.add_field(name="**DISABLED**", value="New people who join will now receive the member role!")
			settings["locked"] = False

		with open("resources/settings.json", "w") as f:
			json.dump(settings, f, indent=4)
		await interaction.response.send_message(embed=embed)

async def setup(client):
	await client.add_cog(Roles(client))