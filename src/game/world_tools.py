# functions for working with worlds.

from tcod.ecs import Registry
from random import Random

from game.components import Graphic, Position
from game.dungeon_draw import *
from game.enemy import draw_enemies
from game.FOV import update_fov_map_from_world


# Think of the ECS registry as containing the world since this is how it will be used.
# Start this function with world = Registry().

def new_world(console_width: int, console_height: int) -> Registry:
    # return a freshly generated world.
    world = Registry()
    rng = world[None].components[Random] = Random()

    # draw player
    draw_player(world, console_width, console_height)
    
    # draw gold counds // TODO: make a seperate class for items
    draw_gold(world, 10, rng)
    
    # draw ground
    draw_ground(world, console_width)

    # draw rooms
    draw_square_room(world, 10, 10, 10)
    draw_rectangle_room(world, 10, 20, 30, 20)

    draw_downwards_stair(world, rng)
    #draw downward stair
    
    draw_enemies(world, rng, console_width, console_height)
    #draw enemies

    update_fov_map_from_world(world)
    # update FOV LAST!
    return world