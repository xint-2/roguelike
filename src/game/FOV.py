# FOV for player character
# TODO: make this better lol


from game.components import Position, Graphic, DoorState
import tcod
from game.tags import *

MAP_WIDTH = 80
MAP_HEIGHT = 50
FOV_ALGO = 0
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10

# FOV initialization
#--------------------
# map takes width and height of map // TODO: make this modular for given console size, define and import from constants?
fov_map = tcod.map.Map(80, 50)
# walkable is a boolean array walkable cells (walkable = True, can walk over)
fov_map.walkable[10, 10] = True
# transparent is a boolean array of transparent cells (transparent = True, entity is seethrough)
fov_map.transparent[10, 10] = True

# computes a fov on the current instance given, (x,y) = player_position, radius = how large around x,y
# light_walls = true, visible obstacles will be returned i.e walls, algorithm determines FOV algo, see docs
fov_map.compute_fov(10, 10, radius=10, light_walls=True, algorithm=0)
visible = fov_map.fov[15, 15]

# recomputes_fov, this is run when the player moves to bind FOV to player, runs whenever player moves -> states.py
def recompute_fov(fov_map, player_x, player_y, radius=TORCH_RADIUS):
    fov_map.compute_fov(player_x, player_y, radius=radius, light_walls=FOV_LIGHT_WALLS, algorithm=FOV_ALGO)

# update fov_map, is run when world is created
def update_fov_map_from_world(world):
    # sets all tiles by default to be non-walkable 
    fov_map.walkable[:, :] = False
    # sets all tiles by default to be seethrough 
    fov_map.transparent[:, :] = True

    #--- SET WALKABLE & TRASNPARENCY ---

    # First, set floors/ground to True
    for entity in world.Q.all_of(components=[Position]):
        pos = entity.components[Position]
        if 0 <= pos.x < MAP_WIDTH and 0 <= pos.y < MAP_HEIGHT:
            if IsFloor in entity.tags or IsGround in entity.tags:
                fov_map.walkable[pos.y, pos.x] = True
                fov_map.transparent[pos.y, pos.x] = True

    # Then, set doors (open/closed)
    for entity in world.Q.all_of(components=[Position, DoorState], tags=[IsDoor]):
        pos = entity.components[Position]
        door_state = entity.components.get(DoorState)
        is_open = getattr(door_state, "is_open", False)
        fov_map.walkable[pos.y, pos.x] = is_open
        fov_map.transparent[pos.y, pos.x] = is_open

    # Finally, set walls (always block)
    for entity in world.Q.all_of(components=[Position], tags=[IsWall]):
        pos = entity.components[Position]
        fov_map.walkable[pos.y, pos.x] = False
        fov_map.transparent[pos.y, pos.x] = False


# unused?
def update_player_fov(world):
    player = next(world.Q.all_f(tags=[IsPlayer]))
    pos = player.components[Position]
    visible = recompute_fov(fov_map, pos.x, pos.y)
    return visible

# unused?
def draw_visible_entities(world, visible):
    for entity in world.Q.all_of(components=[Position, Graphic]):
        pos = entity.components[Position]
        if visible[pos.x, pos.y]:
            pass
