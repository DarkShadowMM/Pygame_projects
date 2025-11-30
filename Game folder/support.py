import pygame
import os
from os import walk

# In support.py
def import_folder(path):
    surface_list = []
    for _, __, img_files in os.walk(path):
        img_files.sort() # <--- ADD THIS LINE to ensure 0.png comes before 1.png
        for image in img_files:
            full_path = path + '/' + image
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surf)
    return surface_list


def import_folder_dict(path):
    surface_dict = {}
    for _, __, img_files in walk(path):
        for img in img_files:
            full_path = f"{path}/{img}"
            image_surface = pygame.image.load(full_path).convert_alpha()
            surface_dict[img.split(".")[0]] = image_surface
    return surface_dict
