import pygame
from os.path import join
from os import walk
import sys

import os

def join_path(*args):
    return os.path.join(*args)

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


WINDOW_WIDTH, WINDOW_HEIGHT = 1280,720
TILE_SIZE = 64
SHEILD_DURATION = 1000  # milliseconds

# Expose join_path as join for compatibility with game.py
join = join_path
