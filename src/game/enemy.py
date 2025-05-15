# TODO: enemies cannot move through immovables (walls, closed doors, player, other enemies etc...)
# TODO: LOS implemented, make i


import tcod.los
from game.components import *
from game.tags import IsActor, IsEnemy, IsWall

def enemies_move_random(world, rng):
    for entity in world.Q.all_of(components=[Position], tags=[IsEnemy]):
        if IsEnemy in getattr(entity, "tags", set()) and Position in entity.components:
            pos = entity.components[Position]
            dx = rng.choice([-1, 0 ,1])
            dy = rng.choice([-1, 0 ,1])
            entity.components[Position] = Position(pos.x + dx, pos.y + dy)


def draw_enemies(world, rng, console_width, console_height):
    num_monsters = rng.randint(0, 10)

    for i in range(num_monsters):
        pos_x = rng.randint(0, console_width)
        pos_y = rng.randint(0, console_height)

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
def enemy_pathfind(fov_map, player_entity, enemy_entity):
    bresenhamList = enemy_LOS(fov_map, player_entity, enemy_entity)
    if bresenhamList and len(bresenhamList) > 1:
        # move along path towards player
        next_x, next_y = bresenhamList[1]
        enemy_entity.components[Position] = Position(next_x, next_y)

