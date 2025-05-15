# implement fov here
from game.components import Position, Graphic, DoorState
import tcod
from game.tags import *

MAP_WIDTH = 80
MAP_HEIGHT = 50
FOV_ALGO = 0
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10

fov_map = tcod.map.Map(80, 50)
fov_map.walkable[10, 10] = True
fov_map.transparent[10, 10] = True
fov_map.compute_fov(10, 10, radius=10, light_walls=True, algorithm=0)
visible = fov_map.fov[15, 15]

def recompute_fov(fov_map, player_x, player_y, radius=TORCH_RADIUS):
    fov_map.compute_fov(player_x, player_y, radius=radius, light_walls=FOV_LIGHT_WALLS, algorithm=FOV_ALGO)


def update_fov_map_from_world(world):
    fov_map.walkable[:, :] = False
    fov_map.transparent[:, :] = True

    # loop through all entities
    for entity in world.Q.all_of(components=[Position]):
        pos = entity.components[Position]
        if 0 <= pos.x < MAP_WIDTH and 0 <= pos.y < MAP_HEIGHT:
            if IsWall in entity.tags:
                # walls block vision and arent walkable
                fov_map.walkable[pos.y, pos.x] = False
                fov_map.transparent[pos.y, pos.x] = False
            elif IsDoor in entity.tags:
                # closed doors block vision, open doors dont
                door_state = entity.components.get(DoorState)
                is_open = getattr(door_state, "is_open", False)
                fov_map.walkable[pos.y, pos.x] = is_open
                fov_map.transparent[pos.y, pos.x] = is_open
            else:
                # floors, ground, etc.
                fov_map.walkable[pos.y, pos.x] = True
                fov_map.transparent[pos.y, pos.x] = True

def update_player_fov(world):
    player = next(world.Q.all_f(tags=[IsPlayer]))
    pos = player.components[Position]
    visible = recompute_fov(fov_map, pos.x, pos.y)
    return visible

def draw_visible_entities(world, visible):
    for entity in world.Q.all_of(components=[Position, Graphic]):
        pos = entity.components[Position]
        if visible[pos.x, pos.y]:
            pass
