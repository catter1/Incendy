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
		The earlier version from `mc_versions`
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
	async upload_github()
		Uploads the Project to GitHub
	async upload_modrinth()
		Uploads the Project to Modrinth
	async upload_curseforge()
		Uploads the Project to Curseforge
	async upload_seedfix()
		Uploads the Project to Seedfix site
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
	patrons: str
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

		if self.project_name in ["Incendium Optional Resourcepack", "Biome Name Fix"]:
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

	
	async def set_translations(self, filepath: str, category: str, project: str) -> str:
		"""
		Get all the available translations for an available project.

		Translations will automatically be filled in or discarded depending on emptiness.

		Parameters
		----------
		filepath : str
			The base path of the project - does not include `assets/x/lang`
		category : str
			A category from [`all`, `incendium`, `omni-biome`]
		project : str
			A project from [`all`, `terralith`, `incendium`, `nullscape`]

		Returns
		----------
		lang_path : str
			The filepath where the translations were set
		"""

		# Var clean
		if category not in ["all", "incendium", "omni-biome"]:
			return "Invalid category!"
		elif category == "all":
			category = ["incendium", "omni-biome"]
		else:
			category = [category]

		if project not in ["all", "terralith", "incendium", "nullscape"]:
			return "Invalid category!"
		elif project == "all":
			project = ["terralith", "incendium", "nullscape"]
		else:
			project = [project]

		# Clone
		pat = self.client.keys["git-pat"]
		repo_path = f"{os.getcwd()}/tmp/translations"
		Repo.clone_from(url=f"https://Incendy-Bot:{pat}@github.com/Stardust-Labs-MC/translations.git", to_path=repo_path)

		# Init language info
		languages = [filename.split(".")[0] for filename in os.listdir(f"{repo_path}/incendium") if filename.split(".")[0] != "en_us"]
		languages.insert(0, "en_us")
		translations = {lang: {} for lang in languages}

		# Sort through and get translation information
		for cat in category:
			for lang in languages:
				with open(f"{repo_path}/{cat}/{lang}.json", 'r') as f:
					data = json.load(f)

				data = {item: data[item] for item in data if (cat == "omni-biome") and item.split(".")[1] not in project}

				for item in data:
					if data[item] == "" and lang != "en_us":
						data[item] = translations["en_us"][item]

				if data == translations.get("en_us"):
					translations.pop(lang, None)
					continue

				translations[lang].update(data)

		# Clean up
		shutil.rmtree(repo_path, ignore_errors=True)

		# Set the translations
		lang_path = f"{filepath}/assets/{self.project_id}/lang"
		os.makedirs(lang_path)

		category = "all" if self.project_id == "incendium" else "omni-biome"
		translations = await self.get_translations(category=category, project=self.project_id)

		for lang in translations:
			with open(f"{lang_path}/{lang}.json", 'w') as f:
				json.dump(translations[lang], f, indent=4)
					
		return lang_path
	
	def create_patron_md(self, filepath: str) -> str:
		"""
		Creates the patrons.md for the Project object.

		Parameters
		----------
		filepath : str
			The filepath to create the markdown file in

		Returns
		----------
		patron_filepath : str
			The filepath for the created patrons.md
		"""
		
		nl = "\n"
		data = f"""
		# Patreon Supporters

		Special thanks to all of our Patrons for supporting us! Here is a list of all patrons in our
		[Discord server](https://discord.gg/stardustlabs) at the time of publishing this version.

		**Overlord**
		{["- " + name + nl for name in self.patrons["overlord"]]}
		**Inferno**
		{["- " + name + nl for name in self.patrons["inferno"]]}
		**Sentry**
		{["- " + name + nl for name in self.patrons["sentry"]]}
		**Blaze**
		{["- " + name + nl for name in self.patrons["blaze"]]}
		"""

		with open(f"{filepath}/patrons.md", 'w') as f:
			f.write(data)

		return f"{filepath}/patrons.md"


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

			with open(f"{filepath}/build.gradle", 'r') as f:
				lines = f.readlines()

			for i, line in enumerate(lines):
				if "2.3.7" in lines:
					lines[i] = line.replace("2.3.7", self.version_number)
				if "terralith" in lines:
					lines[i] = line.replace("terralith", self.project_id)
				if "1.19.3" in lines:
					lines[i] = line.replace("1.19.3", self.newest_mc_version)

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
					lines[i] = line.replace("terralith", self.project_id)

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

			data["mods"][0]["modId"] = self.project_id
			data["mods"][0]["version"] = f"v{self.version_number}"
			data["mods"][0]["displayName"] = self.project_name
			data["mods"][0]["description"] = f"{self.descriptions[self.project_name]} (v{self.version_number} for {self.oldest_mc_version}-{self.newest_mc_version})"
			
			dependencies = data["dependencies"]["terralith"]
			del data["dependencies"]["terralith"]
			data["dependencies"][self.project_id] = dependencies
			minecraft_dict = next((d for d in data["dependencies"]["terralith"] if d["modId"] == "minecraft"), None)
			if minecraft_dict is not None:
				minecraft_dict["versionRange"] = f"[{self.oldest_mc_version},1.20)"

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

			for i, line in enumerate(lines):
				if "terralith" in line:
					lines[i] = line.replace("terralith", self.project_id)
				if "Terralith" in line:
					lines[i] = line.replace("Terralith", self.project_name_safe)
			
			with open(f"{filepath}/{self.project_name_safe}.java", 'w') as f:
				f.writelines(lines)

			return f"{filepath}/{self.project_name_safe}.class"
		

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
		self.create_patron_md(f"{filepath}/src/main/resources")
		if self.project_id in ["terralith", "incendium", "nullscape"]:
			await self.set_translations(f"{filepath}/src/main/resources")

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
		os.chdir(filepath)
		proc = subprocess.Popen([f"./gradlew", "build"])
		proc.wait(timeout=120.0)
		os.chdir("../..")

		# Grab jar and go!
		modfilename = f"tmp/{self.filename}.jar"
		shutil.copy(f"{filepath}/build/libs/{self.project_id}-{self.version_number}.jar", modfilename)

		# Clean up and return
		if os.path.isdir(filepath):
			shutil.rmtree(filepath, ignore_errors=True)
		return modfilename
	

	async def upload_modrinth(self, filepath: str) -> str:
		"""
		Upload the project to Modrinth.

		Parameters
		----------
		filepath : str
			The filepath for the file to upload

		Returns
		----------
		message : str
			Release link if successful, otherwise error message
		"""

		# Init extra request stuff
		base_url = "https://api.modrinth.com/v2"
		url = f"{base_url}/version"
		headers = {
			'User-Agent': self.keys['user-agent'],
			'Authorization': self.keys['modrinth-key']
		}

		# Build post data
		project_id = self.platforms["modrinth"]["projects"][self.project_name]
		loaders = ["minecraft"] if self.file_type == "resourcepack" else ["fabric", "forge", "quilt"]
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
		data_type = "application/zip" if self.file_type == "resourcepack" else "application/java-archive"
		files = {
			"data": json.dumps(data),
			"file": (self.filename, file, data_type)
		}

		# Post and reflect
		r = requests.post(url, headers=headers, files=files)

		if r.status_code == 200:
			return f"https://modrinth.com/project/{project_id}/versions/{self.version_number}"
		else:
			return r.text
		

	async def upload_curseforge(self, filepath: str) -> str:
		"""
		Upload the project to Curseforge.

		Parameters
		----------
		filepath : str
			The filepath for the file to upload

		Returns
		----------
		message : str
			Release link if successful, otherwise error message
		"""

		# Init extra request stuff
		project_id = self.platforms["modrinth"]["projects"][self.project_name]
		base_url = "https://minecraft.curseforge.com"
		url = f"{base_url}/api/projects/{project_id}/upload-file"
		headers = {
			'User-Agnet': self.keys['user-agent'],
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
			"1.19.4": 9559
		}
		gameVersions = [version_translations[version] for version in self.mc_versions]

		# Build post data
		metadata = {
			"changelog": self.changelog,
			"changelogType": "markdown",
			"displayName": self.filename.replace("_", " "),
			"gameVersions": gameVersions,
			"releaseType": "release"
		}
		metastr = json.dumps(metadata)

		# Create file data
		file = open(filepath, "rb")
		files = {
			"file": (self.filename, file, 'application/java-archive')
		}

		# Post and reflect
		r = requests.post(url, headers=headers, files=files, data={"metadata": metastr})

		if r.get("id"):
			return f"https://www.curseforge.com/minecraft/mc-mods/{self.project_id}/files/{r.get('id')}"
		else:
			r.text


	async def upload_github(self, filepath: str) -> str:
		"""
		Upload the project to GitHub.

		Parameters
		----------
		filepath : str
			The filepath for the file to upload

		Returns
		----------
		message : str
			Release link if successful, otherwise error message
		"""

		proj_tag = self.platforms["GitHub"]["projects"][self.project_name]
		pat = self.client.keys["git-pat"]
		auth = ('Incendy-Bot', pat)

		# Clone
		repo_path = f"{os.getcwd()}/tmp/{self.proj_tag}"
		repo = Repo.clone_from(url=f"https://Incendy-Bot:{pat}@github.com/Stardust-Labs-MC/{proj_tag}.git", to_path=repo_path)
		repo.create_remote(self.project_name, f"https://github.com/Stardust-Labs-MC/{proj_tag}.git")

		# Remove all except .git
		for thing in os.listdir(repo_path):
			if os.path.isdir(f"{repo_path}/{thing}"):
				if thing != '.git':
					shutil.rmtree(f"{repo_path}/{thing}")
			else:
				os.remove(f"{repo_path}/{thing}")

		# Save datapack
		zip_name = f"{repo_path}/{self.proj_tag}.zip"
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
				f.writelines(["__MACOSX"])
		else:
			with open(f"{repo_path}/.gitignore", 'r') as f:
				lines = f.readlines()
			if "__MACOSX" not in lines:
				lines.append("__MACOSX")
			with open(f"{repo_path}/.gitignore", 'w') as f:
				f.writelines(lines)

		# git add/commit/push
		origin = repo.remote(name="origin")
		repo.git.add(".")
		repo.index.commit(f"Updated to version {self.version_number}")
		origin.push()

		# Inits info for the release
		url = f'https://api.github.com/repos/Stardust-Labs-MC/{proj_tag}/releases'
		headers = {'Accept': 'application/vnd.github+json', 'Content-Type': 'application/json'}
		body = f"This version of {self.project_name} runs on {self.newest_mc_version}. Stardust Labs will offer support for this version.\n\nIf you would like the mod version, you can download it from [Modrinth](https://modrinth.com/mod/{self.platforms['Modrinth']['projects'][self.project_name]}).\n\nThe Source Code zips should be ignored (they are auto-generated by Github)."
		data = {
			'tag_name': f"v{self.version_number}",
			'name': f"{self.project_name} (MC {self.newest_mc_version}) {self.version_number}",
			'body': body
		}

		# Create the release
		response = requests.post(url, json=data, headers=headers, auth=auth)
		if response.status_code != 201:
			logging.error(response.text)
			return "There's been an error creating the release!"
		
		# Link for later
		release_link = response.json()['html_url']

		# Inits info for the binary
		url = f"https://uploads.github.com/repos/Stardust-Labs-MC/{proj_tag}/releases/{response.json()['id']}/assets?name={self.filename}"
		headers = {'Accept': 'application/vnd.github+json', 'Content-Type': 'application/zip'}
		
		# Send the binary
		response = requests.post(url, data=zip_contents, headers=headers, auth=auth)

		# Clean up
		shutil.rmtree(repo_path)
		
		# Finish off with responses for the user
		if response.status_code == 201:
			return f"The {self.project_name} repository has updated! You can view the release here: {release_link}"
		else:
			logging.error(response.text)
			return "There's been an error attaching the datapack to the release!"
	

	async def upload_seedfix(self, filepath: str) -> str:
		"""
		Upload the project to Seedfix site.

		Parameters
		----------
		filepath : str
			The filepath for the file to upload

		Returns
		----------
		message : str
			Release link if successful, otherwise error message
		"""

		if not os.path.exists("/home/catter/stardustSite"):
			return "Seedfix can only be updated on main server!"
		
		# Create filepath and save datapack
		site_path = "/home/catter/stardustSite"
		zip_name = f"Terralith_1.18.2_{self.version_number}.zip"
		os.mkdir(f"{site_path}/newterralith")
		shutil.copyfile(filepath, f"{site_path}/newterralith/Terralith_1.18.2_{self.version_number}.zip")

		with ZipFile(f"{site_path}/newterralith/{zip_name}", "r") as zf:
			zf.extractall(f"{site_path}/newterralith")
		os.remove(f"{site_path}/newterralith/{zip_name}")
		os.remove(f"{site_path}/overworld.json")

		shutil.rmtree(f"{site_path}/terralith", ignore_errors=True)
		shutil.rmtree(f"{site_path}/apiterralith", ignore_errors=True)
		shutil.move(f"{site_path}/newterralith", f"{site_path}/terralith")
		shutil.copytree(f"{site_path}/terralith", f"{site_path}/apiterralith")
		shutil.copy(f"{site_path}/terralith/data/minecraft/dimension/overworld.json",f"{site_path}/overworld.json")

		with open(f"{site_path}/static/info.json", "r") as f:
			data = json.load(f)
		data["version"] = self.version_number
		with open(f"{site_path}/static/info.json", "w") as f:
			f.writelines(json.dumps(data, indent=2))
        
		return "Terralith successfully updated!"
	

	async def upload_stardust(self, filepath: str) -> str:
		"""
		Upload the project to Stardust Labs site.

		Parameters
		----------
		filepath : str
			The filepath for the file to upload

		Returns
		----------
		message : str
			Release link if successful, otherwise error message
		"""
		
		return None
	

	async def upload_pmc(self) -> str:
		"""
		Upload the project changelogs to Planet Minecraft.

		Unlike its other upload method counterparts, this does NOT take in a filepath.
		This is because datapacks are no longer posted to PMC, but rather uploaded to Stardust Labs website.
		Just the changelogs are uplaoded here.

		Returns
		----------
		message : str
			Release link if successful, otherwise error message
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

		def insert_translations(zip_path: str) -> None:
			"""
			Insert translations into the resourcepack.

			Parameters
			----------
			zip_path : str
				The filepath for the zip file to insert the translations into
			"""

			if self.project_name == "Incendium Optional Resourcepack":
				lang_path = self.set_translations("tmp", "all", "incendium")
			elif self.project_name == "Biome Name Fix":
				lang_path = self.set_translations("tmp", "omni-biome", "all")

			for file in os.listdir(lang_path):
				full_path = f"assets/{self.project_id}/lang/{file}"
				zip_path.write(full_path)

		def insert_patrons(zip_path: str) -> None:
			"""
			Insert translations into the resourcepack.

			Parameters
			----------
			zip_path : str
				The filepath for the zip file to insert the translations into
			"""

			patron_filepath = self.create_patron_md("tmp")

			with ZipFile(zip_path, 'a') as zf:
				zf.write(patron_filepath)
			
			os.remove(patron_filepath)

		## Init the files/filepaths
		zip_filepath: str = None
		jar_filepath: str = None

		# Resourcepacks will ALWAYS be zips
		if self.file_type == "resourcepack":
			zip_filepath = f"tmp/{self.filename}.zip"
			await self.archive.save(zip_filepath)
			insert_translations(zip_filepath)

		# Datapacks should be mod-isized if uploaded to mod site
		elif self.file_type == "datapack":
			if any([platform in self.selected_platforms for platform in ["Curseforge", "Modrinth"]]):
				jar_filepath = await self.create_mod()
				
			if any([platform not in self.selected_platforms for platform in ["Curseforge", "Modrinth"]]):
				zip_filepath = f"tmp/{self.filename}.zip"
				await self.archive.save(zip_filepath)
				insert_patrons(zip_filepath)

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
			responses["curseforge"] = await self.upload_curseforge(jar_filepath)
		if "GitHub" in self.selected_platforms:
			responses["github"] = await self.upload_github(zip_filepath)
		if "Planet Minecraft" in self.selected_platforms:
			responses["pmc"] = await self.upload_pmc()
		if "Stardust Labs" in self.selected_platforms:
			responses["stardust"] = await self.upload_stardust(zip_filepath)
		if "Seedfix" in self.selected_platforms:
			responses["seedfix"] = await self.upload_seedfix(zip_filepath)

		# Clean up and return
		if zip_filepath:
			os.remove(zip_filepath)
		if jar_filepath:
			os.remove(zip_filepath)
			
		return responses