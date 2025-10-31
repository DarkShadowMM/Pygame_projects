import pygame
import os
from os import walk

def import_folder(path):
    surface_list = []
    print(f"\n--- Starting import from: {path} ---") # Улучшенное сообщение о начале импорта
    
    # Проверка существования пути
    if not os.path.exists(path):
        print(f"!!! Error: Path does not exist: {path}")
        return []

    found_any_supported_files = False

    for root, dirs, files in walk(path):
        print(f"  Walking in directory: {root}")
        if dirs:
            print(f"    Subdirectories found: {dirs}")
        if files:
            print(f"    Files found in {root}: {files}")
        
        for image_file in files:
            full_image_path = os.path.join(root, image_file)
            print(f"      Checking file: {full_image_path}") # Выводим каждый проверяемый файл

            if image_file.lower().endswith(('.png', '.jpg', '.jpeg')): # Используйте .lower() для надежности
                try:
                    image_surf = pygame.image.load(full_image_path).convert_alpha()
                    surface_list.append(image_surf)
                    found_any_supported_files = True
                    print(f"        SUCCESS: Loaded {full_image_path}")
                except pygame.error as e:
                    print(f"        ERROR loading {full_image_path}: {e}")
            else:
                print(f"        SKIP: Not a supported image format ({image_file})")
    
    if not found_any_supported_files:
        print(f"--- WARNING: No supported image files found in {path} or its subdirectories. ---")
    
    print(f"--- Finished import from: {path}. Total images loaded: {len(surface_list)} ---")
    return surface_list