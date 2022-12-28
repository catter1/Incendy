from wand.image import Image

HEIGHT = 1008
WIDTH = 1792
RATIO = 0.5625

def resize(path):
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