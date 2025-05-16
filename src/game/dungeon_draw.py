# TODO: move all components (wall,floor,door,ground) make classes?
# TODO: replace square,rectangle with tcod draw_rect equivalent 
# TODO: make a seperate file with graphics array -> array = (ch=(ord("#"), fg=(255, 255, 255), bg=(0, 0, 0), etc..)
# TODO: make algorithm to generate dungeon

from game.classes import Actor
from game.components import Position, Graphic, Gold, DoorState
from game.tags import *

# yields a position given a size
def square(size: int):
    for x in range(size):
        for y in range(size):
            yield Position(x, y)

# yields an Position given width and height
def rectangle(width: int, height: int):
    for i in range(width):
        for j in range(height):
            yield Position(i, j)
            

# keeps items from spawning in things // TODO: fix this, it does not work
def can_spawn_item(world, position):
    for wall in world.Q.all_of(components=[Position], tags=[IsWall, IsItem, IsActor, IsDoor]):
        if wall.components[Position] == position:
            return False
    return True

# draw player 

def draw_player(world, console_width, console_height):
    actor_instance = Actor()
    player_entity = actor_instance.spawn_actor(
        world,
        console_width // 2,
        console_height // 2,
        ch="@",
        fg=[255, 255, 255],
        name="Player",
        gold=0,
        is_player=True
        )


# draw gold // TODO: make items class
def draw_gold(world, amount, rng):

    for _ in range(amount):
        gold = world[object()]
        gold.components[Position] = Position(rng.randint(0, 20), rng.randint(0, 20))
        gold.components[Graphic] = Graphic(ord("$"), fg=(255, 255, 0))
        gold.components[Gold] = rng.randint(1, 10)
        gold.tags |= {IsItem}



def draw_ground(world, console_width):
    for position in square(console_width):
        ground = world[object()]
        ground.components[Position] = position
        ground.components[Graphic] = Graphic(ord('"'), fg=(0, 75, 50))
        ground.tags |= {IsGround}
        #print(f"creating grass at {position}")

# draw a (size) square room // TODO: make a seperate class for rooms
def draw_square_room(world, size, offset_x, offset_y):
    for room_pos in square(size):
        offset_positon = Position(room_pos.x + offset_x, room_pos.y + offset_y)

    # check for grass tile
        for entity in list(world.Q.all_of(components=[Position], tags=[IsGround])):
            if entity.components[Position] == offset_positon:
                # delete grass tile
                world[entity].clear
                #print(f"Grass deleted at {offset_positon}")
    
    # draw a door
        door_x = size // 2
        door_y = 0

        if room_pos.x == door_x and room_pos.y == door_y:
            door = world[object()]
            door.components[Position] = offset_positon
            door.components[Graphic] = Graphic(ord("+"), fg=(200, 180, 50))
            door.components[DoorState] = DoorState(is_open=False)
            door.tags |= {IsDoor}
            # mark as passable or interactable
            #print(f"Door created at {offset_positon}")

    # create walls for the room
        elif room_pos.x == 0 or room_pos.x == size - 1 or room_pos.y == 0 or room_pos.y == size - 1:
            wall = world[object()]
            wall.components[Position] = offset_positon
            wall.components[Graphic] = Graphic(ord("#"), fg=(100, 150, 150))
            wall.tags |= {IsWall}
            #print(f"Wall created at {offset_positon}")

    # create floors for the room
        else:
            room_floor = world[object()]
            room_floor.components[Position] = offset_positon
            room_floor.components[Graphic] = Graphic(ord("'"), fg=(100, 100, 100))
            room_floor.tags |= {IsFloor}
            #print(f"Room floor created at {offset_positon}")

# draw a (x:width, y:height) rectangular room // TODO: make a class for rooms
def draw_rectangle_room(world, width, height, offset_x, offset_y):
    for room_pos in rectangle(width, height):
        offset_position = Position(room_pos.x + offset_x, room_pos.y + offset_y)

    # check for grass tile
        for entity in list(world.Q.all_of(components=[Position], tags=[IsGround])):
            if entity.components[Position] == offset_position:
                # delete grass tile
                world[entity].clear
                #print(f"Deleted grass at {offset_position}")

    # draw a door // TODO: make this into a interactable class (Open=False or Open=True) ("+" closed, "/" open)
        door_x = width // 2
        door_y = 0

        if room_pos.x == door_x and room_pos.y == door_y:
            door = world[object()]
            door.components[Position] = offset_position
            door.components[Graphic] = Graphic(ord("+"), fg=(200, 180, 50))
            door.components[DoorState] = DoorState(is_open=False)
            door.tags |= {IsDoor}
            # mark as passable or interactable
            #print(f"Door created at {offset_position}")

    # create walls for the room
        elif room_pos.x == 0 or room_pos.x == width - 1 or room_pos.y == 0 or room_pos.y == height - 1:
            wall = world[object()]
            wall.components[Position] = offset_position
            wall.components[Graphic] = Graphic(ord("#"), fg=(100, 150, 150))
            wall.tags |= {IsWall}
           # print(f"Wall created at {offset_position}")

    # create floors for the room
        else:
            room_floor = world[object()]
            room_floor.components[Position] = offset_position
            room_floor.components[Graphic] = Graphic(ord("'"), fg=(100, 100, 100))
            room_floor.tags |= {IsFloor}
            #print(f"Room floor created at {offset_position}")

# draws downwards_stair // TODO: implement level change
def draw_downwards_stair(world, rng):
    edgerand = Position(rng.randint(50, 75), rng.randint(30, 45))
    down_stair = world[object()]
    down_stair.components[Position] = edgerand
    down_stair.components[Graphic] = Graphic(ord("<"), fg=(200, 200, 200))
    down_stair.tags |= {IsLevelChange}
    #print(f"down stair created at {edgerand}")

