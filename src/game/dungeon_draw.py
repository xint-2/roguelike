# TODO: move all components (wall,floor,door,ground) -> components.py

# TODO: make algorithm to generate dungeon

from random import Random
from game.components import Position, Graphic, Gold
from game.tags import *


def square(size: int):
    for x in range(size):
        for y in range(size):
            yield Position(x, y)


def rectangle(width: int, height: int):
    for i in range(width):
        for j in range(height):
            yield Position(i, j)


# draw player into
def draw_player(world, console_width, console_height):
    player = world[object()]
    player_position = Position(console_width // 2, console_height // 2)
    player.components[Position] = player_position
    player.components[Graphic] = Graphic(ord("@"))
    player.components[Gold] = 0
    player.tags |= {IsPlayer, IsActor}


# draw gold // TODO: make items class
def draw_gold(world, amount):
    rng = world[None].components[Random] = Random()
    for _ in range(amount):
        gold_position = Position(rng.randint(0, 20), rng.randint(0, 20))
        gold = world[object()]
        gold.components[Position] = gold_position
        gold.components[Graphic] = Graphic(ord("$"), fg=(255, 255, 0))
        gold.components[Gold] = rng.randint(1, 10)
        gold.tags |= {IsItem}


def draw_ground(world, console_width):
    for position in square(console_width):
        ground = world[object()]
        ground.components[Position] = position
        ground.components[Graphic] = Graphic(ord('"'), fg=(0, 75, 50))
        ground.tags |= {IsGround}
        print(f"creating grass at {position}")

# draw a (size) square room // TODO: make a seperate class for rooms
def draw_square_room(world, console_width, console_height, size):
    for room_pos in square(size):
        offset_x = (console_width - size) // 2
        offset_y = (console_height - size) // 2
        centered_position = Position(room_pos.x + offset_x, room_pos.y + offset_y)

    # check for grass tile
        for entity in list(world.Q.all_of(components=[Position], tags=[IsGround])):
            if entity.components[Position] == centered_position:
                # delete grass tile
                world[entity].clear
                print(f"Grass deleted at {centered_position}")
    
    # draw a door // TODO: make this into a interactable class (Open=False or Open=True) ("+" closed, "/" open)
        door_x = size // 2
        door_y = 0

        if room_pos.x == door_x and room_pos.y == door_y:
            door = world[object()]
            door.components[Position] = centered_position
            door.components[Graphic] = Graphic(ord("+"), fg=(200, 180, 50))
            door.tags |= {IsDoor}
            # mark as passable or interactable
            print(f"Door created at {centered_position}")

    # create walls for the room
        elif room_pos.x == 0 or room_pos.x == size - 1 or room_pos.y == 0 or room_pos.y == size - 1:
            wall = world[object()]
            wall.components[Position] = centered_position
            wall.components[Graphic] = Graphic(ord("#"), fg=(100, 150, 150))
            wall.tags |= {IsWall}
            print(f"Wall created at {centered_position}")

    # create floors for the room
        else:
            room_floor = world[object()]
            room_floor.components[Position] = centered_position
            room_floor.components[Graphic] = Graphic(ord("'"), fg=(100, 100, 100))
            room_floor.tags |= {IsFloor}
            print(f"Room floor created at {centered_position}")

# draw a (x:width, y:height) rectangular room // TODO: make a class for rooms
def draw_rectangle_room(world, console_width, console_height, width, height):
    for room_pos in rectangle(width, height):
        offset_x = (console_width - width) // 2
        offset_y = (console_height - height) // 2
        centered_position = Position(room_pos.x + offset_x, room_pos.y + offset_y)

    # check for grass tile
        for entity in list(world.Q.all_of(components=[Position], tags=[IsGround])):
            if entity.components[Position] == centered_position:
                # delete grass tile
                world[entity].clear
                print(f"Deleted grass at {centered_position}")

    # draw a door // TODO: make this into a interactable class (Open=False or Open=True) ("+" closed, "/" open)
        door_x = width // 2
        door_y = 0

        if room_pos.x == door_x and room_pos.y == door_y:
            door = world[object()]
            door.components[Position] = centered_position
            door.components[Graphic] = Graphic(ord("+"), fg=(200, 180, 50))
            door.tags |= {IsDoor}
            # mark as passable or interactable
            print(f"Door created at {centered_position}")

    # create walls for the room
        elif room_pos.x == 0 or room_pos.x == width - 1 or room_pos.y == 0 or room_pos.y == height - 1:
            wall = world[object()]
            wall.components[Position] = centered_position
            wall.components[Graphic] = Graphic(ord("#"), fg=(100, 150, 150))
            wall.tags |= {IsWall}
            print(f"Wall created at {centered_position}")

    # create floors for the room
        else:
            room_floor = world[object()]
            room_floor.components[Position] = centered_position
            room_floor.components[Graphic] = Graphic(ord("'"), fg=(100, 100, 100))
            room_floor.tags |= {IsFloor}
            print(f"Room floor created at {centered_position}")

def draw_downwards_stair(world, console_width, console_height):
    edge = Position(75, 45)
    down_stair = world[object()]
    down_stair.components[Position] = edge
    down_stair.components[Graphic] = Graphic(ord("<"), fg=(255, 255, 255))
    down_stair.tags |= {IsDoor}
    print(f"down stair created at {edge}")

