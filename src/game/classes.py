
# TODO: make enemy couterattack when player attacks it!
# TODO: enemy class -> group enemies
# TODO: dungeon generation
# TODO: enemy array

from __future__ import annotations
import attrs

# import enemy types
from game.components import Position, Graphic, DoorState, Gold
from game.constants import CARDINAL, DIRECTION_KEYS
from game.enemies import enemies_t1_template
from game.tags import *
import tcod.los

# --- Actor entities ---
class Actor():
    position: Position = attrs.field(factory=lambda: Position(0, 0))
    graphic: Graphic = attrs.field(factory=lambda: Graphic(ord("@")))
    # default attributes for player
    attributes = {
        "STR": 5,
        "DEX": 5,
        "CON": 5,
        "INT": 5,
        "WIS": 5,
        "CHR": 5,
        "SPD": 10,
    }
    skills = []
    items = []
    tags: {IsActor}
    name: str = ""

    # add a message to the log,     
    def add_message(world, message: str, max_lines: int = 5):
        log = world[None].components.setdefault(("MessageLog", list), [])
        log.append(message)
        if len(log) > max_lines:
            del log[0]

    def spawn_actor(self, world, x, y, ch, fg=[0,0,0], name="Actor", gold=0, is_player=False):
        actor = world[object()]
        actor.components[Position] = Position(x, y)
        actor.components[Graphic] = Graphic(ord(ch), fg=fg)
        actor.components["attributes"] = self.attributes.copy()
        actor.components["skills"] = list(self.skills)
        actor.components["items"] = list(self.items)
        actor.components["Gold"] = gold
        actor.components["name"] = name
        actor.components["hp"] = ((self.attributes["STR"] * 0.5) + self.attributes["CON"])
        actor.tags |= {IsActor}

        # change this later for neutral NPCS
        if is_player:
            actor.tags |= {IsPlayer}
        else:
            actor.tags |= {IsEnemy}
        return actor

    def melee_attack(world, actor, rng, target=None):
        actor_pos = actor.components[Position]
        damage_roll = rng.randint(1, 3) # needs calculation str, dex, weapon
        if target:
            enemy = target
            enemy.components["hp"] -= damage_roll
            text = f"{actor.components["name"]} attacks!, {enemy.components["name"]} takes {damage_roll} damage!"
            print(text)
            Actor.add_message(world, text)
            if enemy.components["hp"] <= 0:
                death_txt = f"{enemy.components["name"]} dies!"
                Actor.add_message(world, death_txt)
                enemy.clear()


    # TODO: refine this
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
        if any(
            actors.components[Position] == new_position
            for actors in world.Q.all_of(components=[Position], tags=[IsActor])
        ):
            return True
    # return false if it is passable
        return False
    
# --- Player ---
class Player(Actor):
    def __init__(self):
        super().__init__()

    def draw_player(world, x, y):
        actor_instance = Actor()
        player_entity = actor_instance.spawn_actor(
            world,
            x,
            y,
            ch="@",
            fg=[255, 255, 255],
            name="Player",
            gold=0,
            is_player=True
        )

    def player_move(player, sym):
        new_position = player.components[Position] + DIRECTION_KEYS[sym]
        return new_position
    
    
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

# --- Enemy ---
class Enemy(Actor):
    def __init__(self):
        super().__init__()

    # this draws a group of enemies 
    # TODO: refine this
    @staticmethod
    def enemy_move_random_single(world, enemy_entity, map_width, map_height, rng):
        pos = enemy_entity.components[Position]
        dx = rng.choice([-1, 0, 1])
        dy = rng.choice([-1, 0, 1])
        new_x = max(0, min(map_width - 1, pos.x + dx))
        new_y = max(0, min(map_height - 1, pos.y + dy))
        new_pos = Position(new_x, new_y)
        if not Actor.block_movement(world, new_pos):
            enemy_entity.components[Position] = new_pos

    
    # make this speed dependant i.e player_SPD > enemy_SPD = do not counter, add temporary speed to enemy for next counter
    def counterstrike(world, enemy_entity, rng, player_entity):
        if enemy_entity.components.get("hp", 0) > 1:
            enemy_speed = enemy_entity.components["attributes"].get("SPD", 0)
            player_speed = player_entity.components["attributes"].get("SPD", 0)
            if enemy_speed > player_speed:
                damage_roll = rng.randint(1, 3)
                player_entity.components["hp"] -= damage_roll
                # Subtract speed per counter
                enemy_entity.components["attributes"]["SPD"] -= 3
                text = f"{enemy_entity.components["name"]} counterstrikes!, {player_entity.components["name"]} takes {damage_roll} damage!"
                Actor.add_message(world, text)
                if player_entity.components["hp"] < 1:
                    death_text = f"{player_entity.components["name"]} dies!"
                    Actor.add_message(world, death_text)
                    player_entity.clear()
            else:
                # if enemy is slower give it a speed boost for next attack
                speed = f"enemy_speed: {enemy_entity.components["attributes"]["SPD"]}"
                print(speed)
                enemy_entity.components["attributes"]["SPD"] += 5




    # TODO: need to import something to define enemies before spawning, rather than define them here
    def draw_enemy(world, rng, x, y):
            roll = rng.randint(0, 100)
            if roll < 60:
                Enemy.spawn_enemy(world, "orc", x, y)
            elif roll < 90:
                Enemy.spawn_enemy(world, "troll", x, y)
            else:
                Enemy.spawn_enemy(world, "bat", x, y)



    # gets enemies from enemies.py 
    def spawn_enemy(world, enemy_name, x, y):
        template = enemies_t1_template[enemy_name]
        enemy_instance = Enemy()
    # Set attributes before spawning
        enemy_instance.attributes = template["attributes"].copy()
        return enemy_instance.spawn_actor(
            world, x, y,
            ch=template["ch"],
            fg=template["fg"],
            name=template["name"]
        )

    # get bresenham line between monster and player position -> if enemy is in FOV, calculate and return bresenham
    # TODO: IndexError bug here
    def enemy_LOS(fov_map, player_entity, enemy_entity):
        if not player_entity or Position not in player_entity.components:
            return None
        player_pos = player_entity.components[Position] # player position
        enemy_pos = enemy_entity.components[Position] # enemy position
        if fov_map.fov[enemy_pos.y, enemy_pos.x]: # if the enemy is within player fov ->
            # make a bresenham line algorithm, between monsters position and players position
            bresenhamList = tcod.los.bresenham(
                start=(enemy_pos.x, enemy_pos.y), # have to unpack positions of enemy and player
                end=(player_pos.x, player_pos.y)
            ).tolist()
            return bresenhamList
        return None
    
# enemy pathfinding towards player
    def enemy_pathfind(world, fov_map, player_entity, enemy_entity):
        bresenhamList = Enemy.enemy_LOS(fov_map, player_entity, enemy_entity)
        if bresenhamList and len(bresenhamList) > 1:
            # move along path towards player
            next_x, next_y = bresenhamList[1]
            new_pos = Position(next_x, next_y)
            if not Actor.block_movement(world, new_pos):
                enemy_entity.components[Position] = new_pos

# --- Static entities ---
class Static():
    position: Position = attrs.field(factory=lambda: Position(0, 0))
    graphic: Graphic = attrs.field(factory=lambda: Graphic(ord("")))

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


    def draw_ground(world, console_width):
        for position in Static.square(console_width):
            ground = world[object()]
            ground.components[Position] = position
            ground.components[Graphic] = Graphic(ord('"'), fg=(0, 75, 50))
            ground.tags |= {IsGround}
        #print(f"creating grass at {position}")

# draw a (size) square room // TODO: make a seperate class for rooms
    def draw_square_room(world, size, offset_x, offset_y):
        for room_pos in Static.square(size):
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
        for room_pos in Static.rectangle(width, height):
            offset_position = Position(room_pos.x + offset_x, room_pos.y + offset_y)

    # check for grass tile
            for entity in list(world.Q.all_of(components=[Position], tags=[IsGround])):
                if entity.components[Position] == offset_position:
                # delete grass tile
                    world[entity].clear
                #print(f"Deleted grass at {offset_position}")

    # draw a door
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
    def draw_downwards_stair(world, x, y):
        down_stair = world[object()]
        down_stair.components[Position] = Position(x, y)
        down_stair.components[Graphic] = Graphic(ord("<"), fg=(200, 200, 200))
        down_stair.tags |= {IsLevelChange}
    #print(f"down stair created at {edgerand}")

# --- Items ---
class Item(Static):
    def __init__(self):
        super().__init__()

    # draw gold // TODO: make items class
    def draw_gold(world, amount, rng):

        for _ in range(amount):
            gold = world[object()]
            gold.components[Position] = Position(rng.randint(0, 20), rng.randint(0, 20))
            gold.components[Graphic] = Graphic(ord("$"), fg=(255, 255, 0))
            gold.components[Gold] = rng.randint(1, 10)
            gold.tags |= {IsItem}