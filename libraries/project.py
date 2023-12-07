import json
import toml
import os
import shutil
import requests
import subprocess
import logging
import asyncio
import discord
from git import Repo
from zipfile import ZipFile
from distutils import dir_util
from libraries import incendy

class Project:
	"""
	A class representing a datapack or mod in order for it to be
	uploaded to Stardust Labs' various distribution platforms.

	...

	Attributes
	----------
	platforms : dict
		The common dictionary of distribution platforms and their attributes
	client : incendy.IncendyBot
		The current instance of the Incendy discord.Bot
	keys : dict
		All of Incendy's keys
	archive : discord.Attachment
		The file for the working datapack
	file_type : str
		The type of the given file; one of [`datapack`, `mod`, `resourcepack`]
	project_name : str
		The name of the project with title capitalization, spaces, and appropriate symbols
	project_name_safe : str
		Same as `project_name`, but replacing spaces with underscores and removing extra symbols
	project_id : str
		Same as `project_name`, but lowercase, replacing spaces with dashes, and removing extra symbols
	mc_versions : list[str]
		A list of all Minecraft versions that the Project supports
	newest_mc_version : str
		The latest version from `mc_versions`
	oldest_mc_version : str
		The earliest version from `mc_versions`
	version_number : str
		Version number for the pack in x.x.x format
	version_name : str
		Formatted name in v{version_number} ~ {newest_mc_version} format
	filename : str
		Formatted name in {project_name_safe}_{newest_mc_version}_v{version_name} format
	changelog : str
		The full changelog
	patrons : dict
		All Patrons in the Discord at the time of publishing
	selected_platforms : list[str]
		List of distribution platforms for the Project to be uplaoded to

	Methods
	-------
	set_[attribute](attribute: attr_type)
		Sets that attribute and other attributes related to it
	async set_translations()
		Gets and sets the translations for the Project
	async create_mod()
		Creates a mod version of the Project
	async create_datapack()
		Finalizes the datapack of the Project
	async upload_github()
		Uploads the Project to GitHub
	async upload_modrinth()
		Uploads the Project to Modrinth
	async upload_curseforge()
		Uploads the Project to Curseforge
	async upload_stardust()
		Uploads the Project to Stardust Labs site
	async upload_pmc()
		Uploads the Project changelogs to Planet Minecraft
	"""
	
	client: incendy.IncendyBot
	keys: dict
	archive: discord.Attachment
	file_type: str
	project_name: str
	project_name_safe: str
	project_id: str
	mc_versions: list[str]
	newest_mc_version: str
	oldest_mc_version: str
	version_number: str
	version_name: str
	filename: str
	changelog: str
	patrons: dict
	selected_platforms: list[str]
	
	def __init__(self, client: incendy.IncendyBot, archive: discord.Attachment, project_name: str, patrons: dict) -> None:
		"""
		Parameters
		----------
		client : incendy.IncendyBot
			The current instance of the Incendy discord.Bot
		archive : discord.Attachment
			The file for the working datapack
		project_name : str
			The name of the project with title capitalization, spaces, and appropriate symbols
		patrons : dict
			All Patrons in the Discord at the time of publishing
		"""

		with open("resources/platforms.json", 'r') as f:
			self.platforms = json.load(f)
		with open("resources/keys.json", 'r') as f:
			self.keys = json.load(f)
		self.client = client
		self.archive = archive
		self.project_name = project_name
		self.project_name_safe = self.project_name.replace(":", "").replace(" ", "_")
		self.project_id = self.project_name.lower().replace(":", "").replace(" ", "-")
		self.patrons = patrons

		if self.project_name == "Sparkles":
			self.file_type = "resourcepack"
		elif self.archive.content_type == "application/zip":
			self.file_type = "datapack"
		elif self.archive.content_type == "application/java-archive":
			self.file_type = "mod"
		else:
			self.file_type = self.archive.content_type
	
	def set_mc_versions(self, mc_versions: list[str]) -> None:
		"""Sets the supported Minecraft version list."""

		self.mc_versions = mc_versions
		self.newest_mc_version = self.mc_versions[-1]
		self.oldest_mc_version = self.mc_versions[0]
		
	def set_version_number(self, version_number: str) -> None:
		"""Sets the version number/name. `mc_versions` must be set beforehand."""

		self.version_number = version_number
		self.version_name = f"v{self.version_number} ~ {self.newest_mc_version}"
		self.filename = f"{self.project_name_safe}_{self.newest_mc_version}_v{self.version_number}"
	
	def set_changelog(self, changelog: str) -> None:
		"""Sets the changelog."""

		self.changelog = changelog
	
	def set_platforms(self, selected_platforms: list[str]) -> None:
		"""Sets the list of distribution platforms to upload to."""

		self.selected_platforms = selected_platforms

	
	async def set_translations(self, filepath: str, project: str):
		"""
		Get all the available translations for an available project.

		Translations will automatically be filled in or discarded depending on emptiness.

		Parameters
		----------
		filepath : str
			The local path of the project - does not include `assets/x/lang`
		project : str
			A project from [`all`, `terralith`, `incendium`, `nullscape`]

		Returns
		----------
		None
		"""

		# Var clean

		if project not in ["all", "terralith", "incendium", "nullscape", "structory", "structory_towers"]:
			return "Invalid category!"
		elif project == "all":
			projects = ["terralith", "incendium", "nullscape", "structory", "structory_towers"]
		else:
			projects = [project]

		# Clone
		pat = self.client.keys["git-pat"]
		repo_path = f"{os.getcwd()}/tmp/translations"
		Repo.clone_from(url=f"https://Incendy-Bot:{pat}@github.com/Stardust-Labs-MC/translations.git", to_path=repo_path)

		# Start migrating
		english: dict = {}
		for project in projects:

			# Init English
			with open(f"{repo_path}/{project}/en_us.json", 'r') as f:
				english[project] = json.load(f)
			
			# Transfer files
			lang_path = f"{filepath}/assets/{project}/lang"
			os.makedirs(lang_path)
			dir_util.copy_tree(f"{repo_path}/{project}", lang_path)

			# Fill in empty translations
			for file in os.listdir(lang_path):
				with open(f"{lang_path}/{file}", 'r') as f:
					data = json.load(f)

				filled_data = english[project].copy()
				for k in filled_data.keys():
					if data.get(k):
						filled_data[k] = data[k]

				with open(f"{lang_path}/{file}", 'w', encoding='utf-8') as f:
					json.dump(data, f, indent=4, ensure_ascii=False)
		
		# Clean up
		shutil.rmtree(repo_path, ignore_errors=True)
	
	def create_patron_txt(self, filepath: str) -> str:
		"""
		Creates the patrons.txt for the Project object.

		Parameters
		----------
		filepath : str
			The filepath to create the markdown file in

		Returns
		----------
		patron_filepath : str
			The filepath for the created patrons.txt
		"""

		if len(self.patrons.keys()) == 0:
			return
		
		blaze_str = "Blaze:\n"
		for name in self.patrons['blaze']:
			blaze_str += f"- {name}\n"
		sentry_str = "Sentry:\n"
		for name in self.patrons['sentry']:
			sentry_str += f"- {name}\n"
		inferno_str = "Inferno:\n"
		for name in self.patrons['inferno']:
			inferno_str += f"- {name}\n"
		overlord_str = "Overlord:\n"
		for name in self.patrons['overlord']:
			overlord_str += f"- {name}\n"
		undying_str = "Undying:\n"
		for name in self.patrons['undying']:
			undying_str += f"- {name}\n"
		flamekeeper_str = "Flamekeeper:\n"
		for name in self.patrons['flamekeeper']:
			flamekeeper_str += f"- {name}\n"

		data = f"Patreon Supporters\n\nSpecial thanks to all of our Patrons for supporting us! Here is a list of all patrons in our\nDiscord server (https://discord.gg/stardustlabs) at the time of publishing this version.\n\n{flamekeeper_str}\n{undying_str}\n{overlord_str}\n{inferno_str}\n{sentry_str}\n{blaze_str}"

		with open(f"{filepath}/patrons.txt", 'w') as f:
			f.write(data)

		return f"{filepath}/patrons.txt"


	async def create_mod(self) -> str:
		"""
		Create a mod version of the datapack.

		Returns
		----------
		filename : str
			The name and full path of the jar file
		"""

		self.descriptions = {
			"Terralith": "Terralith ~ Overworld Evolved",
			"Incendium": "Incendium ~ Nether Expansion",
			"Nullscape": "Nullscape ~ End Reborn",
			"Structory": "Structory",
			"Structory: Towers": "Structory: Towers",
			"Continents": "Continents",
			"Amplified Nether": "Amplified Nether"
		}
		

		def edit_build_gradle(filepath: str) -> str:
			"""
			Edits the (Forge) build.gradle for the Project object.

			Returns: filepath for build.gradle
			"""

			# Certified Forge moment :/
			version_dict = {
				"1.17.1": "1.17.1-37.1.1",
				"1.18": "1.18-38.0.17",
				"1.18.1": "1.18.1-39.1.0",
				"1.18.2": "1.18.2-40.2.0",
				"1.19": "1.19-41.1.0",
				"1.19.1": "1.19.1-42.0.9",
				"1.19.2": "1.19.2-43.3.0",
				"1.19.3": "1.19.3-44.1.0",
				"1.19.4": "1.19.4-45.2.0",
				"1.20": "1.20-46.0.14",
				"1.20.1": "1.20.1-47.2.0",
				"1.20.2": "1.20.2-48.0.49",
				"1.20.3": "1.20.3-49.0.2",
				"1.20.4": "1.20.3-49.0.2"
			}

			with open(f"{filepath}/build.gradle", 'r') as f:
				lines = f.readlines()

			for i, line in enumerate(lines):
				if "2.3.7" in line:
					lines[i] = line.replace("2.3.7", self.version_number)
				if "terralith" in line:
					lines[i] = line.replace("terralith", self.project_id.replace("-", ""))
				if "1.19.3" in line and not "44.1.16" in line and not "mappings channel" in line:
					lines[i] = line.replace("1.19.3", self.newest_mc_version)
				if "1.19.3-44.1.16" in line:
					lines[i] = line.replace("1.19.3-44.1.16", version_dict[self.newest_mc_version])
				if "mappings channel" in line:
					mapver = self.newest_mc_version if self.newest_mc_version not in ["1.20"] else "1.19.3"
					lines[i] = line.replace("1.19.3", mapver)

			with open(f"{filepath}/build.gradle", 'w') as f:
				f.writelines(lines)

			return f"{filepath}/build.gradle"
		
		def edit_settings_gradle(filepath: str) -> str:
			"""
			Edits the (Forge) settings.gradle for the Project object.

			Returns: filepath for settings.gradle
			"""

			with open(f"{filepath}/settings.gradle", 'r') as f:
				lines = f.readlines()

			for i, line in enumerate(lines):
				if "terralith" in lines:
					lines[i] = line.replace("terralith", self.project_id.replace("-", ""))

			with open(f"{filepath}/settings.gradle", 'w') as f:
				f.writelines(lines)

			return f"{filepath}/settings.gradle"


		def edit_mods_toml(filepath: str) -> str:
			"""
			Edits the (Forge) mods.toml for the Project object.

			Returns: filepath for mods.toml
			"""

			with open(f"{filepath}/mods.toml", 'r') as f:
				data = toml.load(f)

			data["mods"][0]["modId"] = self.project_id.replace("-", "")
			data["mods"][0]["version"] = f"{self.version_number}"
			data["mods"][0]["displayName"] = self.project_name
			data["mods"][0]["description"] = f"{self.descriptions[self.project_name]} (v{self.version_number} for {self.oldest_mc_version}-{self.newest_mc_version})"
			
			dependencies = data["dependencies"]["terralith"]
			del data["dependencies"]["terralith"]
			data["dependencies"][self.project_id] = dependencies
			minecraft_dict = next((d for d in data["dependencies"][self.project_id] if d["modId"] == "minecraft"), None)
			if minecraft_dict is not None:
				minecraft_dict["versionRange"] = f"[{self.oldest_mc_version},)"

			with open(f"{filepath}/mods.toml", 'w') as f:
				toml.dump(data, f)

			return f"{filepath}/mods.toml"
		

		def edit_java_class(filepath: str) -> str:
			"""
			Edits the (Forge) Java class for the Project object.
			
			Returns: filepath for [Name].class
			"""

			with open(f"{filepath}/Terralith.java", 'r') as f:
				lines = f.readlines()
			
			os.remove(f"{filepath}/Terralith.java")

			for i, line in enumerate(lines):
				if "terralith" in line:
					lines[i] = line.replace("terralith", self.project_id.replace('-', ''))
				if "Terralith" in line:
					lines[i] = line.replace("Terralith", self.project_name_safe.replace('_', ''))
			
			with open(f"{filepath}/{self.project_name_safe.replace('_', '')}.java", 'w') as f:
				f.writelines(lines)

			return f"{filepath}/{self.project_name_safe.replace('_', '')}.class"
		

		def edit_fabric_json(filepath: str) -> str:
			"""
			Edits the (Fabric) fabric.mod.json for the Project object.

			Returns: filepath for fabric.mod.json
			"""

			with open(f"{filepath}/fabric.mod.json", 'r') as f:
				data = json.load(f)

			data["id"] = self.project_name_safe.lower()
			data["version"] = str(self.version_number)
			data["name"] = self.project_name
			data["description"] = f"{self.descriptions[self.project_name]} (v{self.version_number} for {self.oldest_mc_version}-{self.newest_mc_version})"
			data["contact"]["sources"] = f"https://github.com/Stardust-Labs-MC/{self.platforms['GitHub']['projects'][self.project_name]}"
			data["contact"]["issues"] = f"https://github.com/Stardust-Labs-MC/{self.platforms['GitHub']['projects'][self.project_name]}/issues"
			data["depends"]["minecraft"] = f">={self.oldest_mc_version}"

			with open(f"{filepath}/fabric.mod.json", 'w') as f:
				json.dump(data, f, indent=4)

		def edit_quilt_json(filepath: str) -> str:
			"""
			Edits the (Quilt) quilt.mod.json for the Project object.

			Returns: filepath for quilt.mod.json
			"""

			with open(f"{filepath}/quilt.mod.json", 'r') as f:
				data = json.load(f)

			data["quilt_loader"]["id"] = self.project_name_safe.lower()
			data["quilt_loader"]["version"] = str(self.version_number)
			data["quilt_loader"]["metadata"]["name"] = self.project_name
			data["quilt_loader"]["metadata"]["description"] = f"{self.descriptions[self.project_name]} (v{self.version_number} for {self.oldest_mc_version}-{self.newest_mc_version})"
			data["quilt_loader"]["metadata"]["contact"]["sources"] = f"https://github.com/Stardust-Labs-MC/{self.platforms['GitHub']['projects'][self.project_name]}"
			data["quilt_loader"]["metadata"]["contact"]["issues"] = f"https://github.com/Stardust-Labs-MC/{self.platforms['GitHub']['projects'][self.project_name]}/issues"
			data["quilt_loader"]["depends"][0]["versions"] = f">={self.oldest_mc_version}"

			with open(f"{filepath}/quilt.mod.json", 'w') as f:
				json.dump(data, f, indent=4)


		# Init the mod dir
		filepath = f"tmp/{self.project_id}-mod"
		shutil.copytree("mod_template", filepath)
		
		# Get the datapack info into the mod
		zip_name = f"{filepath}/src/main/resources/{self.project_id}.zip"
		await self.archive.save(zip_name)
		with ZipFile(zip_name, 'r') as f:
			f.extractall(f"{filepath}/src/main/resources")
		os.remove(zip_name)

		# Create the files
		shutil.move(f"{filepath}/src/main/java/net/stardustlabs/terralith", f"{filepath}/src/main/java/net/stardustlabs/{self.project_id}")
		edit_build_gradle(filepath)
		edit_settings_gradle(filepath)
		edit_fabric_json(f"{filepath}/src/main/resources")
		edit_quilt_json(f"{filepath}/src/main/resources")
		edit_java_class(f"{filepath}/src/main/java/net/stardustlabs/{self.project_id}")
		edit_mods_toml(f"{filepath}/src/main/resources/META-INF")
		if not "Structory" in self.project_name:
			self.create_patron_txt(f"{filepath}/src/main/resources")
		if self.project_id in ["terralith", "incendium", "nullscape"]:
			await self.set_translations(filepath=f"{filepath}/src/main/resources", project=self.project_id)

		# Give gradle a second...
		await asyncio.sleep(2.0)
		if os.path.isdir("bin"):
			shutil.rmtree("bin", ignore_errors=True)
		if os.path.isdir("build"):
			shutil.rmtree("build", ignore_errors=True)
		if os.path.isdir("run"):
			shutil.rmtree("run", ignore_errors=True)
		await asyncio.sleep(2.0)

		# Run gradlew
		#log = open("logs/gradle.log", 'a')
		lastdir = os.getcwd()
		os.chdir(filepath)
		#log.flush()
		proc = subprocess.Popen([f"./gradlew", "build"])#, stdout=log, stderr=log)
		proc.wait(timeout=360.0)
		#log.close()
		os.chdir(lastdir)

		# Grab jar and go!
		modfilename = f"tmp/{self.filename}.jar"
		shutil.copy(f"{filepath}/build/libs/{self.project_id.replace('-', '')}-{self.version_number}.jar", modfilename)

		# Clean up and return
		if os.path.isdir(filepath):
			shutil.rmtree(filepath, ignore_errors=True)
		return modfilename
	

	async def upload_modrinth(self, filepath: str) -> str | None:
		"""
		Upload the project to Modrinth.

		Parameters
		----------
		filepath : str
			The filepath for the file to upload

		Returns
		----------
		message : str
			Release link if successful, otherwise None
		"""

		# Init extra request stuff
		base_url = "https://api.modrinth.com/v2"
		url = f"{base_url}/version"
		headers = {
			'User-Agent': self.keys['user-agent'],
			'Authorization': self.keys['modrinth-key']
		}

		# Build post data
		project_id = self.platforms["Modrinth"]["projects"][self.project_name]
		loaders = ["minecraft"] if self.file_type == "resourcepack" else ["fabric", "forge", "neoforge", "quilt"]
		data = {
			"name": self.version_name,
			"version_number": self.version_number,
			"changelog": self.changelog,
			"dependencies": [],
			"game_versions": self.mc_versions,
			"version_type": "release",
			"loaders": loaders,
			"featured": True,
			"project_id": project_id,
			"file_parts": ["file"]
		}

		# Create file data
		file = open(filepath, 'rb')
		if self.file_type == "resourcepack":
			files = {
				"data": json.dumps(data),
				"file": (f"{self.filename}.zip", file, "application/zip")
			}
		else:
			files = {
				"data": json.dumps(data),
				"file": (f"{self.filename}.jar", file, "application/java-archive")
			}

		# Post and reflect
		r = requests.post(url, headers=headers, files=files)

		if r.status_code == 200:
			_id = r.json().get('id')
			if _id == None:
				logging.error("Modrinth ID not found.")
				logging.error(r.json())
				return f"https://modrinth.com/project/{self.project_id}/versions"
			
			return f"https://modrinth.com/project/{self.project_id}/version/{_id}"
		else:
			logging.error(r.text)
			return None
		

	async def upload_curseforge(self, filepath: str) -> str | None:
		"""
		Upload the project to Curseforge.

		Parameters
		----------
		filepath : str
			The filepath for the file to upload

		Returns
		----------
		message : str
			Release link if successful, otherwise None
		"""

		# Init extra request stuff
		project_id = self.platforms["Curseforge"]["projects"][self.project_name]
		base_url = "https://minecraft.curseforge.com"
		url = f"{base_url}/api/projects/{project_id}/upload-file"
		headers = {
			'User-Agent': self.keys['user-agent'],
			'Accept': 'application/json',
			'X-Api-Token': self.keys['curseforge-key']
		}

		# Silly curseforge things
		version_translations = {
			"1.17.1": 8516,
			"1.18": 8830,
			"1.18.1": 8857,
			"1.18.2": 9008,
			"1.19": 9186,
			"1.19.1": 9259,
			"1.19.2": 9366,
			"1.19.3": 9550,
			"1.19.4": 9776,
			"1.20": 9971,
			"1.20.1": 9990,
			"1.20.2": 10236,
			"1.20.3": 10395,
			"1.20.4": 10407
		}
		gameVersions = [version_translations[version] for version in self.mc_versions]
		# This is [Fabric, Forge, NeoForge, Quilt]
		gameVersions.extend([7499, 7498, 10150, 9153])

		# Build post data
		metadata = {
			"changelog": self.changelog.replace("\n", "\n\n"),
			"changelogType": "markdown",
			"displayName": self.filename.replace("_", " "),
			"gameVersions": gameVersions,
			"releaseType": "release"
		}
		metastr = json.dumps(metadata)

		# Create file data
		file = open(filepath, "rb")
		files = {
			"file": (f"{self.filename}.jar", file, 'application/java-archive')
		}

		# Post and reflect
		r = requests.post(url, headers=headers, files=files, data={"metadata": metastr}, auth=("Starmute", self.keys['curseforge-key']))

		try:
			_id = r.json().get('id')
			if _id == None:
				logging.error("Curseforge ID not found.")
				logging.error(r.json())
				return None
			
			return f"https://www.curseforge.com/minecraft/mc-mods/{self.project_id}/files/{_id}"
		
		except requests.JSONDecodeError:
			logging.error(r.text)
			return None


	async def upload_github(self, filepath: str) -> str | None:
		"""
		Upload the project to GitHub.

		Parameters
		----------
		filepath : str
			The filepath for the file to upload

		Returns
		----------
		message : str
			Release link if successful, otherwise None
		"""

		proj_tag = self.platforms["GitHub"]["projects"][self.project_name]
		pat = self.client.keys["git-pat"]
		auth = ('Incendy-Bot', pat)

		# Clone
		repo_path = f"{os.getcwd()}/tmp/{proj_tag}"
		if "1.20" in self.newest_mc_version:
			branch = "1.20"
		else:
			branch = self.newest_mc_version
		repo = Repo.clone_from(url=f"https://Incendy-Bot:{pat}@github.com/Stardust-Labs-MC/{proj_tag}.git", to_path=repo_path, branch=branch)

		# Remove all except .git
		for thing in os.listdir(repo_path):
			if os.path.isdir(f"{repo_path}/{thing}"):
				if thing not in ['.git']:
					shutil.rmtree(f"{repo_path}/{thing}")
			else:
				if thing not in ['README.md']:
					os.remove(f"{repo_path}/{thing}")

		# Save datapack
		zip_name = f"{repo_path}/{proj_tag}.zip"
		shutil.copyfile(filepath, zip_name)
		with open(zip_name, 'rb') as f:
			zip_contents = f.read()

		# Unzip datapack
		with ZipFile(zip_name, 'r') as f:
			f.extractall(repo_path)
		os.remove(zip_name)

		# gitignore
		if not os.path.exists(f"{repo_path}/.gitignore"):
			with open(f"{repo_path}/.gitignore", 'w') as f:
				f.writelines(["__MACOSX\n", "patrons.txt\n", "README.md\n"])
		else:
			with open(f"{repo_path}/.gitignore", 'r') as f:
				lines = f.readlines()
			if "__MACOSX" not in lines:
				lines.append("__MACOSX\n")
			if "patrons.txt" not in lines:
				lines.append("patrons.txt\n")
			if "README.md" not in lines:
				lines.append("README.md\n")
			with open(f"{repo_path}/.gitignore", 'w') as f:
				f.writelines(lines)

		# git add/commit/push
		repo.git.symbolic_ref("HEAD", f"refs/heads/{branch}")
		origin = repo.remote(name="origin")
		repo.git.add(".")
		repo.index.commit(f"Updated to version {self.version_number}")
		origin.push()

		# Inits info for the release
		url = f'https://api.github.com/repos/Stardust-Labs-MC/{proj_tag}/releases'
		headers = {'Accept': 'application/vnd.github+json', 'Content-Type': 'application/json'}
		body = f"This version of {self.project_name} runs on {self.oldest_mc_version} - {self.newest_mc_version}. Stardust Labs will offer support for this version.\n\nIf you would like the mod version, you can download it from [Modrinth](https://modrinth.com/mod/{self.project_id}).\n\nThe Source Code zips should be ignored (they are auto-generated by Github)."
		data = {
			'tag_name': f"v{self.version_number}",
			'name': f"{self.project_name} (MC {self.oldest_mc_version} - {self.newest_mc_version}) {self.version_number}",
			'body': body
		}

		# Create the release
		response = requests.post(url, json=data, headers=headers, auth=auth)
		if response.status_code != 201:
			logging.error(response.text)
			return None
		
		# Link for later
		release_link = response.json()['html_url']

		# Inits info for the binary
		url = f"https://uploads.github.com/repos/Stardust-Labs-MC/{proj_tag}/releases/{response.json()['id']}/assets?name={self.filename}.zip"
		headers = {'Accept': 'application/vnd.github+json', 'Content-Type': 'application/zip'}
		
		# Send the binary
		response = requests.post(url, data=zip_contents, headers=headers, auth=auth)

		# Clean up
		shutil.rmtree(repo_path)
		
		# Finish off with responses for the user
		if response.status_code == 201:
			return release_link
		else:
			logging.error(response.text)
			return None
	

	async def upload_stardust(self) -> str | None:
		"""
		Upload the project to Stardust Labs site.

		Parameters
		----------
		filepath : str
			The filepath for the file to upload

		Returns
		----------
		message : str
			Download Library link if successful, otherwise None
		"""
		
		return None
	

	async def upload_pmc(self) -> str | None:
		"""
		Upload the project changelogs to Planet Minecraft.

		Unlike its other upload method counterparts, this does NOT take in a filepath.
		This is because datapacks are no longer posted to PMC, but rather uploaded to Stardust Labs website.
		Just the changelogs are uplaoded here.

		Returns
		----------
		message : str
			Project link if successful, otherwise None
		"""

		return None
	

	async def upload(self) -> dict:
		"""
		Uploads the project to all of the platforms given.

		This is done based on `selected_platforms`. The function will also automatically create a mod version if needed.

		Returns
		----------
		responses : dict
			A dictionary of all the responses per upload site.
		"""

		async def insert_translations(zip_path: str) -> None:
			"""
			Insert translations into the resourcepack.

			Parameters
			----------
			zip_path : str
				The filepath for the zip file to insert the translations into
			"""

			await self.set_translations(filepath="tmp", project="all")

			for project in os.listdir("tmp/assets"):
				for file in os.listdir(f"tmp/assets/{project}/lang"):
					full_path = f"tmp/assets/{project}/lang/{file}"
					with ZipFile(zip_path, 'a') as zf:
						zf.write(full_path, arcname=full_path[len("tmp/"):])

			shutil.rmtree("tmp/assets")

		def insert_patrons(zip_path: str) -> None:
			"""
			Insert patrons into the resourcepack.

			Parameters
			----------
			zip_path : str
				The filepath for the zip file to insert the patrons into
			"""

			patron_filepath = self.create_patron_txt("tmp")

			with ZipFile(zip_path, 'a') as zf:
				zf.write(patron_filepath, arcname=patron_filepath[len("tmp/"):])
			
			#os.remove(patron_filepath)

		## Init the files/filepaths
		zip_filepath: str = None
		jar_filepath: str = None

		# Resourcepacks will ALWAYS be zips
		if self.file_type == "resourcepack":
			zip_filepath = f"tmp/{self.filename}.zip"
			await self.archive.save(zip_filepath)
			await insert_translations(zip_filepath)

		# Datapacks should be mod-isized if uploaded to mod site
		elif self.file_type == "datapack":
			if any([platform in self.selected_platforms for platform in ["GitHub", "Planet Minecraft", "Stardust Labs"]]):
				zip_filepath = f"tmp/{self.filename}.zip"
				await self.archive.save(zip_filepath)
				if not "Structory" in self.project_name:
					insert_patrons(zip_filepath)

			if any([platform in self.selected_platforms for platform in ["Curseforge", "Modrinth"]]):
				jar_filepath = await self.create_mod()

		# Mods will ALWAYS be jars
		elif self.file_type == "mod":
			jar_filepath = f"tmp/{self.filename}.jar"
			await self.archive.save(jar_filepath)

		# Start uploading!
		responses = {}

		if "Modrinth" in self.selected_platforms:
			if self.file_type == "resourcepack":
				responses["modrinth"] = await self.upload_modrinth(zip_filepath)
			else:
				responses["modrinth"] = await self.upload_modrinth(jar_filepath)
		if "Curseforge" in self.selected_platforms:
			cf_resp = await self.upload_curseforge(jar_filepath)
			if len(cf_resp) < 1995:
				responses["curseforge"] = cf_resp
			else:
				responses["curseforge"] = "See cf_resp.txt"
				with open("cf_resp.txt", 'w') as f:
					f.write(cf_resp)
		if "GitHub" in self.selected_platforms:
			responses["github"] = await self.upload_github(zip_filepath)
		if "Planet Minecraft" in self.selected_platforms:
			responses["pmc"] = await self.upload_pmc()
		if "Stardust Labs" in self.selected_platforms:
			responses["stardust"] = await self.upload_stardust(zip_filepath)

		# Clean up and return
		if zip_filepath:
			os.remove(zip_filepath)
		if jar_filepath:
			os.remove(jar_filepath)
			
		return responses