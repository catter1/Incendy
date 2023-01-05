import json
import requests
from bs4 import BeautifulSoup
import cloudscraper

def get_downloads() -> dict:
    stats = {}

    projects = ["terralith", "incendium", "nullscape", "amplified-nether", "continents", "structory", "structory-towers"]
    for project in projects:
        stats[project] = 0

    # Curseforge
    for project in projects:
        ## Thanks to these two SO links for bypassing Cloudflare! First link was my original attempt, 2nd link is current working attempt.
        # https://python.tutorialink.com/pythons-requests-triggers-cloudflares-security-while-urllib-does-not/
        # https://stackoverflow.com/questions/71764301/how-to-bypass-cloudflare-with-python-on-get-requests

        scraper = cloudscraper.create_scraper(browser={
            'browser': 'chrome',
            'platform': 'linux',
            'desktop': True
        })
        response = scraper.get(f"https://www.curseforge.com/minecraft/mc-mods/{project}")

        soup = BeautifulSoup(response.content, "html.parser")
        stats[project] += int(soup.find_all(text="Total Downloads")[0].parent.parent.contents[3].text.replace(",", ""))
    
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