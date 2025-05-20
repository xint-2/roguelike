# functions for working with worlds.
# TODO: make doors spawn right
# TODO: move BSP dungeon gen to static classes 

from tcod.ecs import Registry
import tcod.los
import random 
from random import Random

#from game.dungeon_draw import *
from game.classes import Player, Enemy, Static, Item
from game.components import Position, Graphic, DoorState
from game.tags import *
from game.FOV import update_fov_map_from_world
from game.dungeon_partition import Rect, make_bsp_rooms


# Think of the ECS registry as containing the world since this is how it will be used.
# Start this function with world = Registry().


# TODO: make class for BSP stuff -> classes.py
def new_world(console_width: int, console_height: int) -> Registry:
    # return a freshly generated world.
    world = Registry()
    rng = world[None].components[Random] = Random()

    # --- BSP DUNGEON GENERATION ---
    rooms, corridors = make_bsp_rooms(map_width=console_width, map_height=console_height)
    floor_positions = set()

    for room in rooms:
        for x in range(room.x1, room.x2):
            for y in range(room.y1, room.y2):
                # place floor tiles
                floor_positions.add((x, y))
                floor = world[object()]
                floor.components[Position] = Position(x, y)
                floor.components[Graphic] = Graphic(ord("'"), fg=(100, 100, 100))
                floor.tags |= {IsFloor}

    def bresenham_line(x1, y1, x2, y2):
        # use tcod bresenham line to get a list of points between two coordinates
        return tcod.los.bresenham(start=(x1, y1), end=(x2, y2))
        

    for corridor in corridors:
        (x1, y1), (x2, y2) = corridor
        # 50 % chance to draw a door at start of a corridor
        if random.random() < 0.5:
            for (dx, dy) in bresenham_line(x1, y1, x2, y2):
                if (dx, dy) not in floor_positions:
                    door_position = Position(dx, dy)
                    door = world[object()]
                    door.components[Position] = door_position
                    door.components[Graphic] = Graphic(ord("+"), fg=(200, 180, 50))
                    door.components[DoorState] = DoorState(is_open=False)
                    door.tags |= {IsDoor}
                    break
        # draw corridor floor
        for x,y in bresenham_line(x1, y1, x2, y2):
            floor_positions.add((x, y))
            floor = world[object()]
            floor.components[Position] = Position(x, y)
            floor.components[Graphic] = Graphic(ord("'"), fg=(100, 100, 100))
            floor.tags |= {IsFloor}
    
    # draw walls around all floor tiles
    for (x, y) in floor_positions:
        for dx in [-1, 0 ,1]:
            for dy in [-1, 0, 1]:
                wx, wy = x + dx, y + dy
                if (dx == 0 and dy == 0) or (wx, wy) in floor_positions:
                    continue
                # only place walls if not already a wall or floor
                wall = world[object()]
                wall.components[Position] = Position(wx, wy)
                wall.components[Graphic] = Graphic(ord("#"), fg=(100, 150, 150))
                wall.tags |= {IsWall}

    # draw doors // TODO: make doors spawn right !!!!

    # draw player and enemies...

    availabe_positions = list(floor_positions)


    # draw player
    random.shuffle(availabe_positions)
    if availabe_positions:
        x, y = availabe_positions[0]
        Player.draw_player(world, x, y)
    
    # draw gold // TODO: make it draw in visible tiles, also make new items -> first implement inventory
    Item.draw_gold(world, 10, rng)
    
    # draw downward stair, will be used for level change
    if availabe_positions:
        stair_x, stair_y = availabe_positions[-1]
        Static.draw_downwards_stair(world, stair_x, stair_y)

    # draw enemies
    num_enemies = 10
    if availabe_positions:
        random.shuffle(availabe_positions)
        for i in range(num_enemies):
            if i < len(availabe_positions):
                x, y = availabe_positions[i]
                #Enemy.draw_enemy(world, rng, x, y)

    update_fov_map_from_world(world)
    # update FOV LAST!
    return world


# Add other stuff here
def new_level(world: Registry, console_width: int, console_height: int) -> None:
        # 1) find the player entity and save it
    players = list(world.Q.all_of(tags=[IsPlayer]))
    if not players:
        raise RuntimeError("No player found!")
    player = players[0]
    player_pos = player.components[Position]

        # 2) remove all entities except the player
    for entity in list(world.Q.all_of(components=[Position])):
        if entity is player:
            continue
        world[entity].clear()

        # 3) generate new dungeon layour
    rooms, corridors = make_bsp_rooms(map_width=console_width, map_height=console_height)
    floor_positions = set()
    for room in rooms:
        for x in range(room.x1, room.x2):
            for y in range(room.y1, room.y2):
                floor_positions.add((x, y))
                floor = world[object()]
                floor.components[Position] = Position(x, y)
                floor.components[Graphic] = Graphic(ord("'"), fg=(100, 100, 100))
                floor.tags |= {IsFloor}
    # ...repeat for corridors, walls, doors, etc. as in new_world...

    # 4. Place player at new starting position
    if floor_positions:
        x, y = next(iter(floor_positions))
        player.components[Position] = Position(x, y)

    # 5. Place stairs, enemies, items, etc.
    # ...same as in new_world...

    update_fov_map_from_world(world)
