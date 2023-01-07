import json
import requests
from bs4 import BeautifulSoup

def get_downloads(cf_key: str) -> dict:
    stats = {}

    projects = ["terralith", "incendium", "nullscape", "amplified-nether", "continents", "structory", "structory-towers"]
    for project in projects:
        stats[project] = 0

    # Curseforge
    headers = {
        'Accept': 'application/json',
        'x-api-key': cf_key
    }
    cf_dict = {
        "terralith": 513688,
        "incendium": 591388,
        "nullscape": 570354,
        "amplified-nether": 552176,
        "continents": 682515,
        "structory": 636540,
        "structory-towers": 783522
    }
    for project in projects:
        r = requests.get(f'https://api.curseforge.com/v1/mods/{cf_dict[project]}', headers=headers)
        stats[project] += r.json()["data"]["downloadCount"]
    
    # Modrinth
    headers = {'User-Agent': 'catter1/Incendy (catter@zenysis.net)'}
    projects.remove('structory')
    projects.remove('structory-towers')
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
        #"structory-towers": "structory-towers",
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

if __name__ == '__main__':
    print(get_downloads())