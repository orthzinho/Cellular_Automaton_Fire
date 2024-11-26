import pygame
import sys
import random
import math

from Values import *

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.SCALED)
pygame.display.set_caption('Editable Tile Grid')
clock = pygame.time.Clock()

#====================================================================================================================================================#
# NÚCLEO FUNCIONAL: MATEMÁTICA
#====================================================================================================================================================#

def crossproduct3D(a: pygame.Vector3, b: pygame.Vector3):
    x = (a.y * b.z) - (a.z * b.y)
    y = (a.z * b.x) - (a.x * b.z)
    z = (a.x * b.y) - (a.y * b.x)

    return pygame.Vector3( x,y,z )


#====================================================================================================================================================#
# NÚCLEO DE INICIALIZAÇÃO: FUNDAMENTOS DA GRID
#====================================================================================================================================================#


tile_states = [0] * (GRID_WIDTH * GRID_HEIGHT)  # Grid Array defining
heightmap = [0] * (GRID_WIDTH * GRID_HEIGHT)  # Grid Array defining

shademap = [0.0] * ((GRID_WIDTH * GRID_HEIGHT))

grid_surface = pygame.Surface((WIDTH, HEIGHT))  # Define the surface that holds the visual grid

tilechangeQueue = []  # Stores which tiles to change in next frame

#====================================================================================================================================================#
# NÚCLEO DE PROCESSAMENTO: ALTERAÇÃO DE QUADROS
#====================================================================================================================================================#

def changetile(pos, newtype):
    tile_states[int(pos.x) + (GRID_WIDTH * int(pos.y))] = newtype

def appendQueue(pos: pygame.Vector2, newtype):
    # Now append the new (pos, newtype) pair
    if 0 <= pos.x < GRID_WIDTH and 0 <= pos.y < GRID_HEIGHT:
        tilechangeQueue.append((pos, newtype))

def checktile(pos):
    if 0 <= pos.x < GRID_WIDTH and 0 <= pos.y < GRID_HEIGHT:
        return tile_states[int(pos.x) + (GRID_WIDTH * int(pos.y))]
    return 0

def indexToPos(index):
    x = index % GRID_WIDTH  # x is the remainder when index is divided by GRID_WIDTH
    y = index // GRID_WIDTH  # y is the integer division of index by GRID_WIDTH
    return pygame.Vector2(x, y)


#====================================================================================================================================================#
# NÚCLEO DE PROCESSAMENTO: HEIGHTMAP
#====================================================================================================================================================#

def generateHeight():
#    # Center of the mountain
#    center_x = GRID_WIDTH // 2
#    center_y = GRID_HEIGHT // 2
#    
#    # Maximum height of the mountain
#    max_height = 500  # Adjust as necessary
#    
#    for tile in range(len(heightmap)):
#        pos = indexToPos(tile)
#        
#        # Calculate the Euclidean distance from the center of the grid
#        dx = pos.x - center_x
#        dy = pos.y - center_y
#        distance = (dx**2 + dy**2)
#        
#        height = max(0, max_height - int(distance * 0.1))  # 0.5 controls the size of the mountain
#
#        # Set the height for the current tile
#        changeHeight(pos, height)
#        appendQueue(pos,1)
    pass


def drawHeight():
    for tile in range(len(heightmap)):
        pos = indexToPos(tile)
        changeHeight(pos,getH(pos))

def getH(pos):
    if pos.x >= 0 and pos.x < GRID_WIDTH and pos.y >= 0 and pos.y < GRID_HEIGHT:
        return heightmap[int(pos.x) + (GRID_WIDTH * int(pos.y))]
    else:
        return 0  # or a default value

def changeHeight(pos, newheight):
    if newheight < MAX_HEIGHT and newheight >= 0:
        heightmap[int(pos.x) + (GRID_WIDTH * int(pos.y))] = newheight
    appendQueue(pos, checktile(pos))


#====================================================================================================================================================#
# NÚCLEO DE PROCESSAMENTO: SHADER
#====================================================================================================================================================#

def surfaceNormal(pos):
    v1 = pygame.Vector3(pos.x-1, pos.y+1, getH(pygame.Vector2(pos.x-1, pos.y+1)))
    v2 = pygame.Vector3(pos.x-1, pos.y-1, getH(pygame.Vector2(pos.x-1, pos.y-1)))
    v3 = pygame.Vector3(pos.x+1, pos.y+1, getH(pygame.Vector2(pos.x+1, pos.y+1)))

    return crossproduct3D(v2 - v1,v3 - v1)

sunlightVector = pygame.Vector3(-2,-2,4)
timeElapsed = 0

def shadeNormal(pos):
    global sunlightVector

    normal = surfaceNormal(pos).normalize()
    
    sunlight = pygame.Vector3(sunlightVector).normalize()

    dot_light = normal.dot(sunlight)

    shading = dot_light + 1
    return shading

#====================================================================================================================================================#
# NÚCLEO DE PROCESSAMENTO: O FOGO SE ESPALHA
#====================================================================================================================================================#

def FireSpread(pos, radius):
    if checktile(pos) in FIRES:
        if checktile(pos) == 3:
            for y in range(-radius, radius + 1):
                for x in range(-radius, radius + 1):
                    distanceSquared = x**2 + y**2
                    randgen = random.random()
                    xx = pos.x + x
                    yy = pos.y + y
                    spreadChance = 1

                    if getH(pygame.Vector2(xx,yy)) > getH(pos):
                        spreadChance = 0.9
                    elif getH(pygame.Vector2(xx,yy)) < getH(pos):
                        spreadChance = 0.04
                    else:
                        spreadChance = 0.5

                    if randgen < spreadChance:
                        if randgen < ES_CHANCE:
                            xxx = pos.x + x * random.randint(2, ES_MAXSIZE)
                            yyy = pos.y + y * random.randint(2, ES_MAXSIZE)
                            if checktile(pygame.Vector2(xxx, yyy)) in SPREADABLES:
                                appendQueue(pygame.Vector2(xxx, yyy), 3)
                        
                        
                        if distanceSquared <= radius**2:
                            if ((x == 0 and y == 0) or randgen > SPREAD_EF * MATERIALMODIFIERS[checktile(pygame.Vector2(xx, yy))]):
                                if randgen < 0.06:
                                    appendQueue(pygame.Vector2(xx, yy), checktile(pos) + 1)
                            elif checktile(pygame.Vector2(xx, yy)) in SPREADABLES:
                                appendQueue(pygame.Vector2(xx, yy), random.randint(3,4))
                        
            appendQueue(pos, checktile(pos) + 1)
        else:
            appendQueue(pos, checktile(pos) + math.floor(random.randint(-6,19)/10))
            #appendQueue(pos, checktile(pos) + 1)


#====================================================================================================================================================#
# NÚCLEO DE PROCESSAMENTO: UPDATE GERAL DO SISTEMA
#====================================================================================================================================================#

def update():
    drawQueued()
    processQueue()
    #draw_grid()
    pygame.display.flip()

def processQueue():
    for pos, newtype in tilechangeQueue:
        changetile(pos, newtype)  # Change tile type as per queued updates
    tilechangeQueue.clear()  # Clear queue after processing


#====================================================================================================================================================#
# NÚCLEO DE PROCESSAMENTO: DESENHAR O GRID
#====================================================================================================================================================#

def draw_grid():    
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            color = TILESTATES[tile_states[y * GRID_WIDTH + x]]  # Get the color for the tile based on its state
            pygame.draw.rect(grid_surface, color, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))  # Draw the rectangle (tile) on the grid_surface
    
    # Blit the grid_surface onto the main screen
    screen.blit(grid_surface, (0, 0))
   
def drawQueued():
    for pos, newtype in tilechangeQueue:
        if not newtype in FIRES:
            colorRaw = TILESTATES[newtype]
            shading_factor = shadeNormal(pos)
            color = (
                max(20, min(255, int(colorRaw[0] * shading_factor))),
                max(20, min(255, int(colorRaw[1] * shading_factor))),
                max(20, min(255, int(colorRaw[2] * shading_factor)))
            )
        else:
            color = TILESTATES[newtype]
        pygame.draw.rect(grid_surface, color, (pos.x * TILE_SIZE, pos.y * TILE_SIZE, TILE_SIZE, TILE_SIZE))  # Draw the rectangle (tile) on the grid_surface
    screen.blit(grid_surface, (0, 0))


#====================================================================================================================================================#
# NÚCLEO DE PROCESSAMENTO: MOUSE INPUTS
#====================================================================================================================================================#

def save_tile_array(filename):
    with open(filename, 'w') as file:
        file.write(" ".join(map(str, tile_states)))  # Write each state on a new line
    print("Tile array saved to", filename)
    draw_grid()

def load_tile_array(filename):
    global tile_states  # Ensure we're modifying the global tile_states list
    try:
        with open(filename, 'r') as file:
            data = file.read().strip().split(' ')
            tile_states = [0] * (GRID_WIDTH * GRID_HEIGHT)  
            for index, value in enumerate(data):
                if value.isdigit():
                    value = int(value)
                    if 0 <= value < len(TILESTATES):
                        tile_states[index] = value
                    else:
                        print(f"Invalid value {value} at index {index}; using default.")
                if index >= GRID_WIDTH * GRID_HEIGHT - 1:
                    break  # Stop reading if we've filled the grid
        print("Tile array loaded from", filename)
    except FileNotFoundError:
        print("File not found:", filename)
    except Exception as e:
        print("An error occurred while loading the tile array:", e)
    draw_grid()


def save_heightmap(filename):
    with open(filename, 'w') as file:
        file.write(" ".join(map(str, heightmap)))  # Write each state on a new line
    print("Tile array saved to", filename)
    draw_grid()
    generateHeight()

def load_heightmap(filename):
    global heightmap # Ensure we're modifying the global tile_states list
    try:
        with open(filename, 'r') as file:
            data = file.read().strip().split(' ')
            heightmap = [0] * (GRID_WIDTH * GRID_HEIGHT)  
            for index, value in enumerate(data):
                if value.isdigit():
                    value = int(value)
                    if 0 <= value < MAX_HEIGHT +1:
                        heightmap[index] = value
                    else:
                        print(f"Invalid value {value} at index {index}; using default.")
                if index >= GRID_WIDTH * GRID_HEIGHT - 1:
                    break  # Stop reading if we've filled the grid
        print("Tile array loaded from", filename)
    except FileNotFoundError:
        print("File not found:", filename)
    except Exception as e:
        print("An error occurred while loading the tile array:", e)
    
    draw_grid()
    drawHeight()

def gridpos(x, y):
    return pygame.Vector2(x // TILE_SIZE, y // TILE_SIZE)

#====================================================================================================================================================#
# NÚCLEO DE PROCESSAMENTO: MOUSE INPUTS
#====================================================================================================================================================#

mouse1_down = False
mouse2_down = False

p_mouse = pygame.Vector2(pygame.mouse.get_pos())
mouse = pygame.Vector2(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])

#====================================================================================================================================================#
# NÚCLEO DE PROCESSAMENTO: PINCEL
#====================================================================================================================================================#

brushtype = 0
brushSize = 1

def changetile_brush(pos, brushsize, tiletype, Hfactor):
    radius = brushsize // 2
    center_x, center_y = pos.x, pos.y

    for y in range(-radius, radius + 1):
        for x in range(-radius, radius + 1):
            distance = x**2 + y**2

            if distance <= radius**2:
                tile = pygame.Vector2(int(center_x + x), int(center_y + y))
                                      
                if 0 <= tile.x < GRID_WIDTH and 0 <= tile.y < GRID_HEIGHT:
                    if tiletype != 0:
                        changeHeight(tile, getH(tile) + (int(radius - (math.sqrt(distance)))*Hfactor))
                    else:
                        changeHeight(tile, 0)
                    appendQueue(pygame.Vector2(tile.x, tile.y), tiletype)
                    

#====================================================================================================================================================#
# NÚCLEO DE PROCESSAMENTO: CHUNKS
#====================================================================================================================================================#

chunkPdown = True
def processChunk():
    global currentChunk, chunkPdown
    chunk = chunks[currentChunk]

    for pos_x, pos_y in chunk:
        FireSpread(pygame.Vector2(pos_x, pos_y), 1)
    

    if chunkPdown == True:
        currentChunk += 1
        if currentChunk >= len(chunks):
            chunkPdown = False
    if chunkPdown == False:
        currentChunk -= 1
        if currentChunk <= -1:
            chunkPdown = True
    
    if currentChunk % CHUNKUPDATE == 0:
        update()
    
    

def create_chunks():
    chunks = []
    for y in range(0, GRID_HEIGHT, CHUNK_HEIGHT):  # Iterate over the rows
        chunk = []
        for i in range(CHUNK_HEIGHT):  # Add tiles in the row(s)
            if 0 <= y + i < GRID_HEIGHT:  # Ensure we're within bounds
                for x in range(GRID_WIDTH):  # Add all columns in this row
                    chunk.append((x, y + i))  # Append the tile position (x, y)
        chunks.append(chunk)
    return chunks

chunks = create_chunks()
currentChunk = 0


#====================================================================================================================================================#
# NÚCLEO DE PROCESSAMENTO: DEBUG INTERFACE
#====================================================================================================================================================#
#
#debug = False
#
#def toggleDebug():
#    pass
#
#def draw_debug_info():
#    if debug:
#        info = [
#            f"Brush Size: {BrushRadius}",
#            f"Brush Type: {BrushType}",
#            f"Update Depth: {MAX_UPD_DEPTH}",
#            f"Update Cooldown: {UPDATE_COOLDOWN}",
#            f"Wind Speed X: {windspeedx}",
#            f"Wind Speed Y: {windspeedy}",
#            f"FPS: {int(clock.get_fps())}"
#        ]
#        
#        for i, line in enumerate(info):
#            text_surface = font.render(line, True, (255, 255, 255))
#            pygame.draw.rect(screen, (0,0,0),(0, 25*i + 10 , 200 , 25))
#            screen.blit(text_surface, (10, 10 + i * 25))
#
#====================================================================================================================================================#
# LOOP PRINCIPAL
#====================================================================================================================================================#

draw_grid()
generateHeight()
update()

shiftDown = False

while True:
    mouse = pygame.Vector2(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])

    for event in pygame.event.get():
        # Quit the program
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Detect Mouse presses
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse1_down = True
            if event.button == 3:  # Right mouse button
                mouse2_down = True

        # Detect Mouse releases
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button
                mouse1_down = False
            if event.button == 3:  # Right mouse button
                mouse2_down = False

        # Scroll to change brush size
        if event.type == pygame.MOUSEWHEEL:
            if event.y > 0:  # Scroll up
                brushSize = min(brushSize + 1, MAX_BRUSH_SIZE)
            elif event.y < 0:  # Scroll down
                brushSize = max(brushSize - 1, MIN_BRUSH_SIZE)
        

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_l:  # Load
                load_tile_array('Saves\saveslot1.txt')
                load_heightmap('Saves\saveslot2.txt')
            if event.key == pygame.K_s:  # Save
                save_tile_array('Saves\saveslot1.txt')
                save_heightmap('Saves\saveslot2.txt')
            if event.key == pygame.K_SPACE:  # Save
                shadeNormal(gridpos(mouse.x, mouse.y))

            if pygame.K_0 <= event.key <= pygame.K_9:
                brushtype = event.key - pygame.K_0

            if event.key == pygame.K_SPACE:  # Change type
                surfaceNormal(gridpos(mouse.x, mouse.y))
            
            if event.key == pygame.K_LSHIFT:
                shiftDown = True

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LSHIFT:
                shiftDown = False


    if mouse1_down:
        if shiftDown:
            changetile_brush(gridpos(mouse.x, mouse.y), brushSize, brushtype, -1)
        else:
            changetile_brush(gridpos(mouse.x, mouse.y), brushSize, brushtype, 1)
        update()
    else:
        processChunk()

    if mouse2_down:
        changetile_brush(gridpos(mouse.x, mouse.y), brushSize, brushtype, 0)
        update()

    clock.tick(4800)