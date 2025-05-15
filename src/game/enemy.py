# TODO: enemies cannot move through immovables/other entities (walls, closed doors, player, other enemies etc...)
# TODO: make enemies spawn in small groups
# TODO: LOS implemented, make i


import tcod.los
from game.components import *
from game.tags import IsActor, IsEnemy, IsWall, IsDoor


# enemies cannot move through walls and closed doors, other actors
def enemy_blocked(world, enemy_pos):
    # walls
    if any(
        wall.components[Position] == enemy_pos
        for wall in world.Q.all_of(components=[Position], tags=[IsWall])
        ):
            return True
    # doors
    if any(
        door.components[Position] == enemy_pos
        for door in world.Q.all_of(components=[Position, DoorState], tags=[IsWall])
    ):
        return True
    # actors
    if any(
        actors.components[Position] == enemy_pos
        for actors in world.Q.all_of(components=[Position], tags=[IsActor])
    ):
        return True

    return False


# enemies move randomly before coming into player LOS // TODO: if small groups, see about staying close
def enemies_move_random(world, map_width, map_height, rng):
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
            if not enemy_blocked(world, new_pos):
                entity.components[Position] = new_pos


# spawn enemies prototype // TODO: make enemies start in small group
# TODO: make a new class for enemies, use this function to spawn them
# TODO: make static roll
def draw_enemies(world, rng, console_width, console_height):
    num_monsters = rng.randint(0, 10)

    for i in range(num_monsters):
        pos_x = rng.randint(0, console_width - 5)
        pos_y = rng.randint(0, console_height - 5)

        roll = rng.randint(0, 100)
        if roll < 60:
            monster = world[object()]
            monster.components[Position] = Position(pos_x, pos_y)
            monster.components[Graphic] = Graphic(ord("o"), fg=(0, 255, 0))
            monster.tags |= {IsActor, IsEnemy}
        elif roll < 90:
            monster = world[object()]
            monster.components[Position] = Position(pos_x, pos_y)
            monster.components[Graphic] = Graphic(ord("T"), fg=(0, 255, 0))
            monster.tags |= {IsActor, IsEnemy}
        else:
            monster = world[object()]
            monster.components[Position] = Position(pos_x, pos_y)
            monster.components[Graphic] = Graphic(ord("B"), fg=(100, 100, 255))
            monster.tags |= {IsActor, IsEnemy}

# get bresenham line between monster and player position -> if enemy is in FOV, calculate and return bresenham
# TODO: IndexError bug here
def enemy_LOS(fov_map, player_entity, enemy_entity):
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
    bresenhamList = enemy_LOS(fov_map, player_entity, enemy_entity)
    if bresenhamList and len(bresenhamList) > 1:
        # move along path towards player
        next_x, next_y = bresenhamList[1]
        new_pos = Position(next_x, next_y)
        if not enemy_blocked(world, new_pos):
            enemy_entity.components[Position] = new_pos

