import pygame
from os.path import join
from os import walk
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = join('.')

    return join(base_path, relative_path)


WINDOW_WIDTH, WINDOW_HEIGHT = 1280,720
TILE_SIZE = 64
SHEILD_DURATION = 1000  # milliseconds