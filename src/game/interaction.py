# player/entity interactions with the world
# closing and opening doors
# TODO: attacking enemies, enemy attacking?

from game.components import Position, Graphic, DoorState
from game.tags import IsDoor, IsWall
from game.constants import CARDINAL


    # opening and closing doors
def door_interaction(world, player, player_pos):
    # check for all cardinal directions
    for dx, dy in CARDINAL:
        check_pos = Position(player_pos.x + dx, player_pos.y + dy)
        for door in world.Q.all_of(components=[Position, DoorState], tags=[IsDoor]):
            if door.components[Position] == check_pos:
                door_state = door.components[DoorState]
                door_state.is_open = not door_state.is_open
                if door_state.is_open:
                    door.components[Graphic] = Graphic(ord("/"), fg=(200, 180, 50))
                else:
                    door.components[Graphic] = Graphic(ord("+"), fg=(200, 180, 50))
                return None
    
def block_movement(world, new_position):
    # if a wall is in the way, YOU CANNOT PASS = return True
    if any(
        wall.components[Position] == new_position
        for wall in world.Q.all_of(components=[Position], tags=[IsWall])
        ):
            return True
    # if a closed door is at new position, return impassable = True
    if any(
        door.components[Position] == new_position and not door.components[DoorState].is_open
        for door in world.Q.all_of(components=[Position, DoorState], tags=[IsDoor])
        ):
            return True
    # return false if it is passable
    return False

    
    