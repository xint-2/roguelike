
# TODO: make player class, inherits actor --> door_interaction
# TODO: make enemy class, inherits actor --> update enemy_group function 

from __future__ import annotations
import attrs

# import enemy types
from game.components import Position, Graphic, DoorState
from game.constants import CARDINAL
from game.tags import *
import tcod.los


class Actor():
    position: Position = attrs.field(factory=lambda: Position(0, 0))
    graphic: Graphic = attrs.field(factory=lambda: Graphic(ord("@")))
    attributes = {
        "STR": 2,
        "DEX": 2,
        "CON": 2,
        "INT": 2,
        "WIS": 2,
        "CHR": 2
    }
    skills = []
    items = []
    tags: {IsActor}
    name: str = ""

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
        if is_player:
            actor.tags |= {IsPlayer}
        return actor

    def melee_attack(world, actor, rng, target=None):
        actor_pos = actor.components[Position]
        damage_roll = rng.randint(1, 3) # needs calculation str, dex, weapon
        if target:
            enemy = target
            enemy.components["hp"] -= damage_roll
            text = f"{actor.components["name"]} attacks!, {enemy.components["name"]} takes {damage_roll} damage!"
            world[None].components[("Text", str)] = text
            if enemy.components["hp"] <= 0:
                death_txt = f"{enemy.components["name"]} dies!"
                world[None].components[("Text", str)] = death_txt
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
    

class Player(Actor):
    def __init__(self):
        super().__init__()

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


class Enemy(Actor):
    def __init__(self):
        super().__init__()

    # this draws a group of enemies 
    # TODO: refine this
    def enemy_move_random(world, map_width, map_height, rng):
        for entity in world.Q.all_of(components=[Position], tags=[IsEnemy]):
            if IsEnemy in getattr(entity, "tags", set()) and Position in entity.components:
                pos = entity.components[Position]
            # destination x,y
                dx = rng.choice([-1, 0 ,1])
                dy = rng.choice([-1, 0 ,1])
            # bounds checking x,y for width,height of console
                new_x = max(0, min(map_width - 1, pos.x + dx))
                new_y = max(0, min(map_height - 1, pos.y + dy))
                new_pos = Position(new_x, new_y)
            # assign new position
                if not Actor.block_movement(world, new_pos):
                    entity.components[Position] = new_pos

    # TODO: need to import something to define enemies before spawning, rather than define them here
    def draw_enemy(world, rng, console_width, console_height):

        num_monsters = rng.randint(0, 10)
        monster_gold = rng.randint(0, 10)

        for _ in range(num_monsters):
            pos_x = rng.randint(0, console_width - 5)
            pos_y = rng.randint(0, console_height - 5)
            roll = rng.randint(0, 100)

        actor_instance = Actor()
        if roll < 60:
            enemy = actor_instance.spawn_actor(world, pos_x, pos_y, ch="o", fg=(0, 255, 0), name="Orc")
            enemy.tags |= {IsEnemy}
        elif roll < 90:
            enemy = actor_instance.spawn_actor(world, pos_x, pos_y, ch="T", fg=(0, 255, 0), name="Troll")
            enemy.tags |= {IsEnemy}
        else:
            enemy = actor_instance.spawn_actor(world, pos_x, pos_y, ch="b", fg=(100, 100, 255), name="Bat")
            enemy.tags |= {IsEnemy}

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
