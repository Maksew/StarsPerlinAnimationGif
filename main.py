from noise import pnoise2
import numpy as np
from PIL import Image, ImageDraw
from random import randint

class Star:
    def __init__(self, x, y, rayon, couleur, vitesse_x, vitesse_y):
        self.x = x
        self.y = y
        self.rayon = rayon
        self.couleur = couleur
        self.vitesse_x = vitesse_x
        self.vitesse_y = vitesse_y

    def move(self, largeur, hauteur):
        self.x = (self.x + self.vitesse_x) % largeur
        self.y = (self.y + self.vitesse_y) % hauteur


def adjust_opacity(world):
    world_normalized = ((world - np.min(world)) / (np.max(world) - np.min(world))) * 255
    threshold = 50
    world_opacity = np.clip(world_normalized - threshold, 0, 255)

    return world_opacity


def generate_perlin_background(width, height, time=0, scale=150):
    shape = (height, width)
    world = np.zeros(shape, dtype=np.float32)
    frequency = 1.0 / scale
    for i in range(shape[0]):
        for j in range(shape[1]):
            noise_val = pnoise2(x=i * frequency,
                                y=j * frequency + time,
                                octaves=1,
                                repeatx=1024,
                                repeaty=1024,
                                base=42)
            world[i][j] = noise_val

    world_opacity = adjust_opacity(world)

    color_1 = np.array([80, 0, 80], dtype=np.uint8)
    color_2 = np.array([0, 0, 0], dtype=np.uint8)

    blend_factor = world_opacity / 255.0
    blended_color = (color_1 * blend_factor[:, :, None]) + (color_2 * (1 - blend_factor[:, :, None]))

    return Image.fromarray(blended_color.astype(np.uint8))

def red_tint():
    return (randint(200, 255), randint(0, 50), randint(0, 50))

def pink_tint():
    return (randint(200, 255), randint(100, 150), randint(180, 255))

def purple_tint():
    return (randint(150, 200), randint(0, 50), randint(200, 255))

def beige_tint():
    return (randint(220, 255), randint(180, 220), randint(150, 190))


def generate_stars(nb_stars, largeur, hauteur, tint_function):
    return [Star(randint(0, largeur), randint(0, hauteur), randint(1, 3),
                 tint_function(), randint(0, 1), randint(0, 1))
            for _ in range(nb_stars)]

largeur, hauteur = 500, 500

stars_red = generate_stars(125, largeur, hauteur, red_tint)
stars_pink = generate_stars(125, largeur, hauteur, pink_tint)
stars_purple = generate_stars(125, largeur, hauteur, purple_tint)
stars_beige = generate_stars(125, largeur, hauteur, beige_tint)

stars = stars_red + stars_pink + stars_purple + stars_beige

repeaty_value = 100
time_increment = 0.2
frames_needed = int(repeaty_value / time_increment)
composite_frames = []

angle_increment = 2 * np.pi / frames_needed

for frame in range(frames_needed):
    background = generate_perlin_background(largeur, hauteur, time=frame * time_increment)
    background_copy = background.convert("RGBA")
    star_image = Image.new('RGBA', (largeur, hauteur), (0, 0, 0, 0))
    draw = ImageDraw.Draw(star_image)
    angle = frame * angle_increment

    for star in stars:
        star.move(largeur, hauteur)
        draw.ellipse((star.x - star.rayon, star.y - star.rayon, star.x + star.rayon, star.y + star.rayon),
                     fill=star.couleur)

    composite_image = Image.alpha_composite(background_copy, star_image)
    composite_frames.append(composite_image)
    composite_image.save(f'frame_{frame:03d}.png')

#Utilisation de 'magick convert -delay 3.3 -loop 0 frame_*.png etoiles_loop.gif' pour la génération du gif.
