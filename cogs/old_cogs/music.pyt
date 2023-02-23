import discord
import os
import youtube_dl
import asyncio
#import spotipy
import time as pytime
import logging
from discord.ext import commands
from discord import FFmpegPCMAudio
from resources import incendy

class Music(commands.Cog):
	def __init__(self, client: incendy.IncendyBot):
		self.client = client

	async def cog_load(self):
		logging.info(f'> {self.__cog_name__} cog loaded')

	async def cog_unload(self):
		logging.info(f'> {self.__cog_name__} cog unloaded')
	
	@commands.command()
	async def join(self, ctx):
		await self.joiner(ctx)

	async def joiner(self, ctx):
		if ctx.author.voice is None:
			await ctx.send("You need to join a voice channel first! I don't like joining voice channels alone...")
		else:
			voice_channel = ctx.author.voice.channel
			if ctx.voice_client is None:
				await voice_channel.connect()
			else:
				await ctx.voice_client.move_to(voice_channel)

	@commands.command()
	async def leave(self, ctx):
		await ctx.voice_client.disconnect()

	@commands.command()
	async def speak(self, ctx, audio):
		ctx.voice_client.stop()
		if ctx.voice_client is not None:
			channel = ctx.message.author.voice.channel
			source = FFmpegPCMAudio(f'resources/{audio}.mp3')
			ctx.voice_client.play(source)

	@commands.command()
	async def play(self, ctx, *, url):
		await self.joiner(ctx)

		FFMPEG_OPTIONS = {'before_options':'-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options':'-vn'}
		YDL_OPTIONS = {'format':'bestaudio'}
		vc = ctx.voice_client

		if "youtube" in url:
			ctx.voice_client.stop()

			with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
				info = ydl.extract_info(url, download=False)
				url2 = info['formats'][0]['url']
				source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
				vc.play(source)
		else:
			await ctx.send("Sorry, I am only able to play YouTube links right now.")

	@commands.Cog.listener()
	async def on_voice_state_update(self, member, before, after):
		if not member.id == self.client.user.id:
			return
		elif before.channel is None:
			voice = after.channel.guild.voice_client
			chtime = 0
			while True:
				await asyncio.sleep(1)
				chtime += 1
				if voice.is_playing():
					chtime = 0
				if chtime == 300:
					await voice.disconnect()
				if not voice.is_connected():
					break

async def setup(client):
	await client.add_cog(Music(client))