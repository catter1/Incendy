import os
import discord
import cv2 as cv
import numpy as np
from PIL import Image, ImageFont, ImageDraw
from wand.image import Image

HEIGHT = 1008
WIDTH = 1792
RATIO = 0.5625

stats = {
    "version":"v3.0.0",
    "members":"19,300",
    "tweets":"123",
    "videos":"123",
    "streams":"123",
    "commands":[
        {"FAQ":"1,200"},
        {"QP":"934"},
        {"STATS":"623"},
        {"DISCORD":"439"},
        {"REMINDME":"231"}
    ],
    "downloads":{
        "total":"1,234,567",
        "terralith":"1,234,567",
        "incendium":"1,234,567",
        "nullscape":"1,234,567",
        "structory":"1,234,567",
        "continents":"1,234,567",
        "amplified":"1,234,567",
    }
}

def create_stats_image(stats: dict) -> str:
    img = Image.open(f"{os.curdir}/assets/Server Stats.jpg")
    font = ImageFont.truetype(f"{os.curdir}/assets/Kanit-Regular.ttf", 60)
    fontdis = ImageFont.truetype(f"{os.curdir}/assets/Kanit-Regular.ttf", 90)
    font5 = ImageFont.truetype(f"{os.curdir}/assets/Kanit-Regular.ttf", 40)
    draw = ImageDraw.Draw(img)

    cmdstr = ", ".join([f"{cmd.keys()[0]} ({cmd.values()[0]})" for cmd in stats["commands"]])

    #Version
    draw.text((75,260), stats["version"], font=font, fill=(214,246,255))
    #Top Commands
    draw.text((572,271), cmdstr, font=font5, fill=(214,246,255))

    #Members
    draw.text((75,475), stats["members"], font=fontdis, fill=(214,246,255))
    #Tweets
    draw.text((75,690), stats["tweets"], font=font, fill=(214,246,255))
    #Videos
    draw.text((75,860), stats["videos"], font=font, fill=(214,246,255))
    #Streams
    draw.text((75,1030), stats["streams"], font=font, fill=(214,246,255))

    #Total
    draw.text((813,525), stats["downloads"]["total"], font=font, fill=(214,246,255))
    #Terralith
    draw.text((813,685), stats["downloads"]["terralith"], font=font, fill=(214,246,255))
    #Incendium
    draw.text((813,855), stats["downloads"]["incendium"], font=font, fill=(214,246,255))
    #Continents
    draw.text((813,1025), stats["downloads"]["continents"], font=font, fill=(214,246,255))
    #Structory
    draw.text((1230,685), stats["downloads"]["structory"], font=font, fill=(214,246,255))
    #Nullscape
    draw.text((1230,855), stats["downloads"]["nullscape"], font=font, fill=(214,246,255))
    #Amplified Nether
    draw.text((1230,1025), stats["downloads"]["amplified"], font=font, fill=(214,246,255))

    filepath = f"{os.curdir}/tmp/stats.jpg"
    img.save(filepath)
    return filepath

# thanks! https://towardsdatascience.com/finding-most-common-colors-in-python-47ea0767a06a
def get_color(filename: str) -> discord.Color:
    img = cv.imread(filename) #Image here
    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    img = cv.resize(img, (80, 80), interpolation = cv.INTER_AREA)

    unique, counts = np.unique(img.reshape(-1, 3), axis=0, return_counts=True)
    final = unique[np.argmax(counts)]
    colour = discord.Colour.from_rgb(int(final[0]), int(final[1]), int(final[2]))

    return colour

def resize(path) -> None:
    image = Image(filename=path)

    if RATIO >= image.height/image.width :
        rswidth = (int)((HEIGHT * image.width) / image.height)
        image.sample(rswidth, HEIGHT)

        if image.width != WIDTH:
            image.crop(width=WIDTH, height=HEIGHT, gravity="center")

    else:
        rsheight = (int)((WIDTH * image.height) / image.width)
        image.sample(WIDTH, rsheight)

        if image.height != HEIGHT:
            image.crop(width=WIDTH, height=HEIGHT, gravity="center")

    image.save(filename=path)