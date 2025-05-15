
import attrs
import tcod.console
import tcod.event
from tcod.event import KeySym
from random import Random


import g
import game.menus
from game.world_tools import new_world
from game.components import Gold, Graphic, Position, DoorState
from game.constants import DIRECTION_KEYS, INTERACTION_KEYS, CARDINAL
from game.tags import * # Make into a list?
from game.state import Push, Reset, State, StateResult
from game.FOV import recompute_fov, fov_map, TORCH_RADIUS
from game.interaction import door_interaction, block_movement
from game.enemy import enemies_move_random, enemy_pathfind, enemy_blocked


@attrs.define()
class InGame:
    # Primary in-game state.
    visible = attrs.field(default=None)
    def on_event(self, event: tcod.event.Event) -> None:
        # tcod-ecs query, fetch player entity
        (player,) = g.world.Q.all_of(tags=[IsPlayer])


        match event:
            case tcod.event.Quit():
                raise SystemExit()
        # MOVEMENT GO
            case tcod.event.KeyDown(sym=sym) if sym in DIRECTION_KEYS:
                # new_position == players current position + new direction, POSITIONAL EVENTS
                new_position = player.components[Position] + DIRECTION_KEYS[sym]
                if block_movement(g.world, new_position):
                    return None

                #  TODO: other immovables here? / traps

                # player position is updated to new_position if there is no wall
                player.components[Position] = new_position
                #print(f"Player position: {player.components[Position]}")
                
                # Auto pickup gold // TODO: reuse for other items, append to inventory
                for gold in g.world.Q.all_of(components=[Gold], tags=[player.components[Position], IsItem]):
                    player.components[Gold] += gold.components[Gold]
                    text = f"Picked up {gold.components[Gold]}g, total: {player.components[Gold]}g"
                    g.world[None].components[("Text", str)] = text
                    gold.clear()


                # move enemies after player // TODO: I dont like static 
                enemies_move_random(g.world, 80, 50, g.world[None].components[Random])
                # pathfind for enemy
                for enemy_entity in g.world.Q.all_of(components=[Position, Graphic], tags={IsEnemy}):
                    enemy_pathfind(g.world, fov_map, player, enemy_entity)

                # recompute fov after player movement
                recompute_fov(fov_map, new_position.x, new_position.y, radius=TORCH_RADIUS)
                self.visible = fov_map.fov


                return None
            
        # INTERACTION GO
            case tcod.event.KeyDown(sym=sym) if sym in INTERACTION_KEYS:
            # check adjacent tiles (including current position) for doors // TODO: ^^ seperate this
                player_pos = player.components[Position]
                door_interaction(g.world, player, player_pos)


            case tcod.event.KeyDown(sym=KeySym.ESCAPE):
                return Push(MainMenu())
            case _:
                return None


    def on_draw(self, console: tcod.console.Console) -> None:

        # only draw entities if they are visible
        visible = self.visible if self.visible is not None else fov_map.fov
        
        # priority to determine which tile is drawn first
        priority = {
            IsPlayer: 5,
            IsEnemy: 4,
            IsActor: 3,
            IsWall: 2,
            IsDoor: 2,
            IsLevelChange: 2,
            IsItem: 1,
            IsFloor: 0,
            IsGround: -1,
        }
        tile_entities = {}

        # for all entities in the world registry
        for entity in g.world.Q.all_of(components=[Position, Graphic]):
            pos = entity.components[Position]
        # if the entity is within the bounds of the console
            if not (0 <= pos.x < console.width and 0 <= pos.y < console.height):
                continue
        # if the entity is not visible, go to next entity
            if not visible[pos.y, pos.x]:
                continue

        # Determine entity priority, loops over tags in a given entity
            entity_priority = max((priority.get(tag, -2) for tag in getattr(entity, "tags", set())), default=-2)
            key = (pos.y, pos.x)
            if key not in tile_entities or entity_priority > tile_entities[key][0]:
                tile_entities[key] = (entity_priority, entity)

        # Draw only the topmost entity at each tile
        for (y, x), (_, entity) in tile_entities.items():
            graphic = entity.components[Graphic]
            console.ch[y, x] = graphic.ch
            console.fg[y, x] = graphic.fg
        # Optionally: console.bg[y, x] = graphic.bg if you use backgrounds

        if text := g.world[None].components.get(("Text", str)):
            console.print(x=0, y=console.height - 1, string=text, fg=(255, 255, 255), bg=(0, 0, 0))
            

class MainMenu(game.menus.ListMenu):
    
    # Main/escape menu
    __slots__ = ()

    def __init__(self) -> None:
        # Initialize the main menu.
        items = [
            game.menus.SelectItem("New game", self.new_game),
            game.menus.SelectItem("Quit", self.quit),
        ]
        if hasattr(g, "world"):
            items.insert(0, game.menus.SelectItem("Continue", self.continue_))

        super().__init__(
            items=tuple(items),
            selected=0,
            x=5,
            y=5,
        )

    @staticmethod
    def continue_() -> StateResult:
        # Return to the game.
        return Reset(InGame())

    @staticmethod
    def new_game() -> StateResult:
        # Begin a new game.
        g.world = game.world_tools.new_world(80, 50)
        return Reset(InGame())

    @staticmethod
    def quit() -> StateResult:
        # Close the program.
        raise SystemExit


        