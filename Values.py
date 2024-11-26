import pygame

TILE_SIZE   = 2
GRID_WIDTH  = 200
GRID_HEIGHT = 200

WIDTH = GRID_WIDTH * TILE_SIZE
HEIGHT = GRID_HEIGHT * TILE_SIZE

TILESTATES = [
    (10, 30, 128),   # Water
    (10, 60, 20),    # Dense
    (80, 128, 60),   # Sparse
    (255, 255, 175), # Fire
    (255, 200, 66),  # Apprentice Fire
    (255, 120, 40),  # Man, that's just sad Fire
    (230, 60, 30),   # Its over Fire
    (200, 40, 30),   # Little spark of a Fire
    (25, 25, 25),    # Charred
    (165, 42, 42),   # Firewall
]

MATERIALMODIFIERS = [
    0, # Water
    1, # Dense
    0.4, # Sparse
    0, # Fire
    0, # Weakling
    0, # Sad Fire
    0, # 
    0, #
    0, # Charred
    0.1, # Firewall
]

SPREADABLES = [1,2,9]
FIRES       = [3,4,5,6,7]

CHUNK_HEIGHT  = 4
MAX_HEIGHT    = 10000
CHUNKUPDATE   = 1 #once every X chunks, update da canvas

MIN_BRUSH_SIZE = 1
MAX_BRUSH_SIZE = 80

# ExtraSpread (ES) Mechanics
ES_CHANCE  = 0.08
ES_MAXSIZE = 3
SPREAD_EF  = 1  # Spread Efficiency (chance to successfully spread)