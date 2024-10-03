import json
import requests

def get_downloads(cf_key: str, git_pat: str) -> dict:
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
        url = f"https://www.planetminecraft.com/data-pack/{pmc_projects[project]}/statsv2"
        x = requests.get(url=url, headers=headers)
        try:
            pmc_downloads = x.json().get('downloads', 0)
        except requests.exceptions.JSONDecodeError:
            pmc_downloads = 0

        stats[project] += pmc_downloads

    # GitHub
    headers = {"Authorization": f"Bearer {git_pat}"}

    for project in projects:
        url = f"https://api.github.com/repos/Stardust-Labs-MC/{project}/releases"
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        for release in response.json():
            #release_id = release["id"]
            
            for asset in release["assets"]:
                asset_id = asset["id"]
                
                asset_url = f"https://api.github.com/repos/Stardust-Labs-MC/{project}/releases/assets/{asset_id}"
                
                asset_response = requests.get(asset_url, headers=headers)
                asset_response.raise_for_status()
                
                asset_info = asset_response.json()
                download_count = asset_info["download_count"]
                stats[project] += download_count

    # Seedfix
    #url = "https://seedfix.stardustlabs.net/api/get_downloads/"
    #x = requests.get(url=url, headers=headers)
    #stats["terralith"] += int(x.text)

    return stats

if __name__ == '__main__':
    print(get_downloads())
