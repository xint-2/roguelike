# functions for working with worlds.

from tcod.ecs import Registry

from game.components import Graphic, Position
from game.dungeon_draw import *


# Think of the ECS registry as containing the world since this is how it will be used.
# Start this function with world = Registry().

def new_world(console_width: int, console_height: int) -> Registry:
    # return a freshly generated world.
    world = Registry()

    # draw player
    draw_player(world, console_width, console_height)
    
    # draw gold counds // TODO: make a seperate class for items
    draw_gold(world, 10)

    
    # draw ground
    draw_ground(world, console_width)


    # draw room
    draw_square_room(world, console_width, console_height, 10)
    #draw_rectangle_room(world, console_width, console_height, 10, 15)

    draw_downwards_stair(world, console_width, console_height)
    #draw downward stair

    return world