# TODO: Implement enemy counter attacking!, make it better
# TODO: make a better log display -> display more lines
# TODO: dungeon generation


import attrs
import tcod.console
import tcod.event
from tcod.event import KeySym
from random import Random


import g
import game.menus
from game.world_tools import new_world, new_level
from game.components import Gold, Graphic, Position
from game.constants import DIRECTION_KEYS, INTERACTION_KEYS
from game.tags import * 
from game.state import Push, Reset, State, StateResult
from game.FOV import recompute_fov, fov_map, TORCH_RADIUS
from game.classes import Player, Enemy
import game.world_tools


@attrs.define()
class InGame:
    # Primary in-game state.
    visible = attrs.field(default=None)
    turns = attrs.field(default=0)
    def on_event(self, event: tcod.event.Event) -> None:

        # tcod-ecs query, fetch player entity
        players = list(g.world.Q.all_of(tags=[IsPlayer]))
        if not players:
            print("Player died")
            return Push(MainMenu())
        (player,) = players
        player_pos = player.components[Position]

        rng = g.world[None].components[Random]

        match event:
            case tcod.event.Quit():
                raise SystemExit()

            case tcod.event.KeyDown(sym=sym) if sym in DIRECTION_KEYS:

                # Positional events trigger
                direction = DIRECTION_KEYS[sym]
                new_position = player.components[Position] + DIRECTION_KEYS[sym]
                self.turns += 1

                # player regenrates 2 hp and mp every 20 turns
                if self.turns % 10 == 0:
                    print("regenerated")
                    max_hp = player.components.get("max_hp", 10)
                    player.components["hp"] = min(player.components.get("hp", 0) + 1, max_hp)
                    max_mp = player.components.get("max_mp", 10)
                    player.components["mp"] = min(player.components.get("mp", 0) + 1, max_mp)
            
                # melee_attack enemy
                enemy = next(
                    (e for e in g.world.Q.all_of(components=[Position], tags=[IsEnemy])
                     if e.components[Position] == new_position),
                    None 
                    )
                
                if enemy:
                    Player.melee_attack(g.world, player, rng=rng, target=enemy)
                    Enemy.counterstrike(g.world, enemy, rng, player)
                    return None
                
                # player movement block, cannot pass through walls, etc...
                if Player.block_movement(g.world, new_position):
                    return None
                
                player.components[Position] = new_position

                # --- Auto pickup gold --- TODO: item pickup here?
                # maybe move to player class

                for gold in g.world.Q.all_of(components=[Gold], tags=[player.components[Position], IsItem]):
                    player.components[Gold] = player.components.get(Gold, 0) + gold.components[Gold]
                    text = f"Picked up {gold.components[Gold]}g"
                    g.world[None].components[("Text", str)] = text
                    gold.clear()

                # --- Enemy Movement, Pathfinding and Attacking ---
                
                for enemy_entity in g.world.Q.all_of(components=[Position, Graphic], tags={IsEnemy}):
                    Enemy.enemy_move_random_single(g.world, enemy_entity=enemy_entity, map_width=80, map_height=50, rng=rng)
                    enemy_pos = enemy_entity.components[Position]
                    if abs(enemy_pos.x - player_pos.x) + abs(enemy_pos.y - player_pos.y) == 1:
                        Enemy.melee_attack(g.world, enemy_entity, g.world[None].components[Random], target=player)
                    else:
                        Enemy.enemy_pathfind(g.world, fov_map, player, enemy_entity)


                # recompute fov after player movement
                recompute_fov(fov_map, new_position.x, new_position.y, radius=TORCH_RADIUS)
                self.visible = fov_map.fov


                return None
            
        # INTERACTION GO
            case tcod.event.KeyDown(sym=sym) if sym in INTERACTION_KEYS:
            # check adjacent tiles (including current position) for doors // TODO: ^^ seperate this
                action = INTERACTION_KEYS[sym]
                player_pos = player.components[Position]

                if action == "interact":
                    Player.door_interaction(g.world, player, player_pos)
                    return None
                
                # need to implement new_level generation, save char stats but go to a new level
                if action == "stairs":
                    for entity in g.world.Q.all_of(components=[Position], tags=[IsLevelChange]):
                        if entity.components[Position] == player_pos:
                            game.world_tools.new_level(g.world, 80, 50)
                            return Reset(InGame())
                    g.world[None].components[("Text", str)] = "You are not standing on stairs."
                    return None


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
            if not hasattr(pos, "x") or not hasattr(pos, "y"):
                continue
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

        #if text := g.world[None].components.get(("Text", str)):
            #console.print(x=0, y=console.height - 1, string=text, fg=(255, 255, 255), bg=(0, 0, 0))

        log = g.world[None].components.get(("MessageLog", list), [])
        log_y = console.height - len(log) - 1
        for i, msg in enumerate(log):
            console.print(x=0, y=log_y + i, string=msg, fg=(255, 255, 255), bg=(0, 0, 0))

        # --- draw player stats ---
        players = list(g.world.Q.all_of(tags=[IsPlayer]))
        if players:
            player = players[0]
            attrs = player.components.get("attributes", {})
            hp = player.components.get("hp", 0)
            mp = player.components.get("mp", 0)
            gold = player.components.get(("Gold", int), 0)
            stats_str = f" Turn: {self.turns} HP: {hp:.0f} MP: {mp:.0f}  Gold: {gold}  STR: {attrs.get('STR', 0)}  DEX: {attrs.get('DEX', 0)}  CON: {attrs.get('CON', 0)} INT: {attrs.get('INT', 0)} WIS: {attrs.get('WIS', 0)} CHR: {attrs.get('CHR', 0)}"
            console.print(x=0, y=0, string=stats_str, fg=(255, 255, 255), bg=(0, 0, 0))

            

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


        