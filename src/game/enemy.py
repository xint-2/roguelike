# TODO: enemies cannot move through immovables (walls, closed doors, etc...)
# TODO: enemy FOV
# TODO: enemy track and follow player once in FOV
# enemy moves randomly till player comes into view


from game.components import *
from game.tags import IsActor, IsEnemy

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

