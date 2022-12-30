# One time use to combine streams.txt and videos.txt with stats.json

import json

with open("resources/stats.json", "r") as f:
    stats = json.load(f)

with open("resources/streams.txt", "r") as f:
    streams = f.readlines()

with open("resources/videos.txt", "r") as f:
    videos = f.readlines()

for item in streams:
    stats["streams"].append(int(item))

for item in videos:
    if item.startswith('{'):
        item = item[:129] + "}"
        item = item.replace('\'', '"')
        vidinfo = json.loads(item)
        stats["videos"].append(vidinfo["id"]["videoId"])
    else:
        stats["videos"].append(item.strip())

with open("resources/stats.json", "w") as f:
    json.dump(stats, f, indent=4)