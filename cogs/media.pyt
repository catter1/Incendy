import discord
import asyncio
import os
import json
import decimal
import time as pytime
from datetime import *
from twitchAPI.twitch import Twitch
from googleapiclient.discovery import build
from itertools import cycle
from discord import FFmpegPCMAudio
from discord.ext import commands, tasks
from discord.ext.tasks import loop

class Media(commands.Cog):
	def __init__(self, client):
		self.client = client
	
	with open('resources/keys.json', 'r') as f:
		keys = json.load(f)
	
	twitch = Twitch(keys["twitch-id"], keys["twitch-secret"])
	youtube = build('youtube', 'v3', developerKey=keys["youtube-key"])

	async def cog_load(self):
		print(f' - {self.__cog_name__} cog loaded.')
		self.twitch_timer.start()
		self.youtube_timer.start()

	async def cog_unload(self):
		print(f' - {self.__cog_name__} cog unloaded.')
		self.twitch_timer.stop()
		self.youtube_timer.stop()
	
	@tasks.loop(seconds=123.7)
	async def twitch_timer(self):
		await self.check_twitch()

	@tasks.loop(hours=5.0)
	async def youtube_timer(self):
		await self.check_youtube()

	async def check_twitch(self):
		streams = self.twitch.get_streams(game_id= "27471", first=100)
		page = str(streams['pagination']['cursor'])
		for instance in streams['data']:
			if "terralith" in str(instance['title']).lower():
				await self.process_stream(instance, "terralith")
			if "incendium" in str(instance['title']).lower():
				await self.process_stream(instance, "incendium")
		end = False
		while end == False:
			streams = self.twitch.get_streams(game_id= "27471", first=100, after=page) #game_id= "27471"
			try:
				page = str(streams['pagination']['cursor'])
			except KeyError:
				end = True
			for instance in streams['data']:
				if "terralith" in str(instance['title']).lower():
					await self.process_stream(instance, "terralith")
				if "incendium" in str(instance['title']).lower():
					await self.process_stream(instance, "incendium")

	async def process_stream(self, instance, pack):
		stream_ids = []
		with open('resources/streams.txt', 'r') as cache:
			stream_ids = cache.readlines()
		match = False
		for item in reversed(stream_ids):
			if instance['id'] in item:
				match = True
				break
		if not match:
			with open('resources/streams.txt', 'a') as cache:
				cache.write(f"\n{instance['id']}")
			await self.share_stream(instance, pack)
		stream_ids = []

	async def share_stream(self, stream, pack):
		channel = self.client.get_channel(879976073813700648)
		#Dimensions 640x360
		width = 1280
		height = 720
		if pack == "terralith":
			pack = " Terralith"
		if pack == "incendium":
			pack = "n Incendium"
		usr = self.twitch.get_users(logins= stream['user_login'])
		followers = self.twitch.get_users_follows(to_id= usr['data'][0]['id'])['total']
		embed = discord.Embed(title=str(stream['title']), colour=discord.Colour.blurple(), timestamp=datetime.utcnow(), url=f"https://www.twitch.tv/{stream['user_login']}")
		embed.set_author(name=stream['user_name'], icon_url=usr['data'][0]['profile_image_url'])
		embed.set_image(url=str(stream['thumbnail_url']).format(**locals()))
		embed.add_field(name=f"{stream['user_name']} has started a{pack} stream with {followers} followers!", value='Incendy finds cool new Terralith and Incendium streams and videos. Check them out!')
		embed.set_footer(text="Twitch", icon_url="https://cdn.discordapp.com/emojis/470883174872776704.png")
		print(f"[{datetime.utcnow()}] - Posted Twitch alert for {stream['user_name']} with title {stream['title']}")
		await channel.send(embed=embed)

	async def check_youtube(self):
		dateago = datetime.strftime((datetime.utcnow() - timedelta(minutes=302)), "%Y-%m-%dT%H:%M:%SZ") #2021-09-09T19:39:35Z
		irequest = self.youtube.search().list(part='snippet', maxResults=5, order='date', publishedAfter=dateago, q='incendium', type='video', videoCategoryId=20) #20 is gaming category
		iresponse = irequest.execute()
		trequest = self.youtube.search().list(part='snippet', maxResults=5, order='date', publishedAfter=dateago, q='terralith', type='video', videoCategoryId=20)
		tresponse = trequest.execute()

		yt_ids = []
		with open('resources/videos.txt', 'r') as cache:
			yt_ids = cache.readlines()
		iidsearch = []
		tidsearch = []
		for iindex in iresponse['items']:
			iidsearch.append(iindex)
		for tindex in tresponse['items']:
			tidsearch.append(tindex)
		
		await asyncio.sleep(0.7)
		for item in iidsearch:
			if not any(item['id']['videoId'] in ytid for ytid in yt_ids):
				with open('resources/videos.txt', 'a') as cache:
					cache.write(f"{item}\n")
				await self.share_video(item, "an Incendium")
		for item in tidsearch:
			if not any(item['id']['videoId'] in ytid for ytid in yt_ids):
				with open('resources/videos.txt', 'a') as cache:
					cache.write(f"{item}\n")
				await self.share_video(item, "a Terralith")
		yt_ids = []

	async def share_video(self, video, pack):
		channel = self.client.get_channel(879976073813700648) #735649413032050769
		imgsearch = self.youtube.channels().list(part='snippet', id=video['snippet']['channelId']).execute()
		for item in imgsearch['items']:
			imgurl = item['snippet']['thumbnails']['high']['url']
		subsearch = self.youtube.channels().list(part='statistics', id=video['snippet']['channelId']).execute()
		for item in subsearch['items']:
			subs = item['statistics']['subscriberCount']
		thumb = video['snippet']['thumbnails']['high']['url']

		embed = discord.Embed(title=str(video['snippet']['title']), colour=discord.Colour.red(), timestamp=datetime.utcnow(), url=f"https://www.youtube.com/watch?v={video['id']['videoId']}")
		embed.set_author(name=video['snippet']['channelTitle'], icon_url=imgurl)
		embed.set_image(url=thumb)
		embed.add_field(name=f"{video['snippet']['channelTitle']} has posted {pack} video with {subs} subs!", value='Incendy finds cool new Terralith and Incendium streams and videos. Check them out!')
		embed.set_footer(text="YouTube", icon_url="https://cdn.discordapp.com/emojis/885669600660963328.png")
		print(f"[{datetime.utcnow()}] - Posted YouTube alert for [{video['snippet']['channelTitle']}] with title [{video['snippet']['title']}]")
		await channel.send(embed=embed)

async def setup(client):
	await client.add_cog(Media(client))
