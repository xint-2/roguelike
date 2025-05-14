
import attrs
import tcod.console
import tcod.event
from tcod.event import KeySym

import g
import game.menus
import game.world_tools
from game.components import Gold, Graphic, Position
from game.constants import DIRECTION_KEYS, INTERACTION_KEYS, CARDINAL
from game.tags import *
from game.state import Push, Reset, State, StateResult


@attrs.define()
class InGame:
    # Primary in-game state.

    def on_event(self, event: tcod.event.Event) -> None:
        # tcod-ecs query, fetch player entity

        (player,) = g.world.Q.all_of(tags=[IsPlayer])
        match event:
            case tcod.event.Quit():
                raise SystemExit()
            case tcod.event.KeyDown(sym=sym) if sym in DIRECTION_KEYS:
                # new_position == players current position + new direction, POSITIONAL EVENTS
                new_position = player.components[Position] + DIRECTION_KEYS[sym]
                
                # if wall is at new position, return (i.e cannot move through walls)
                if any(
                    wall.components[Position] == new_position
                    for wall in g.world.Q.all_of(components=[Position], tags=[IsWall])
                ):
                    return
                # check for traps // TODO: other immovables here?

                # player position is updated to new_position if there is no wall
                player.components[Position] = new_position
                print(f"Player position: {player.components[Position]}")
                
                # Auto pickup gold // TODO: reuse for other items, append to inventory
                for gold in g.world.Q.all_of(components=[Gold], tags=[player.components[Position], IsItem]):
                    player.components[Gold] += gold.components[Gold]
                    text = f"Picked up {gold.components[Gold]}g, total: {player.components[Gold]}g"
                    g.world[None].components[("Text", str)] = text
                    gold.clear()
                return None
            
            # INTERACTION_KEYS // TODO: make new file for interactions
            case tcod.event.KeyDown(sym=sym) if sym in INTERACTION_KEYS:
            # check adjacent tiles (including current position) for doors
                player_pos = player.components[Position]
                for dx, dy in CARDINAL:
                    check_pos = Position(player_pos.x + dx, player_pos.y + dy)
                    for door in g.world.Q.all_of(components=[Position], tags=[IsDoor]):
                        if door.components[Position] == check_pos:
                            # example stoggle door state or print msg
                            print(f"Interacted with door at {check_pos}")
                            # door logic here
                            return None
                print("No door nearby to interact with")


            case tcod.event.KeyDown(sym=KeySym.ESCAPE):
                return Push(MainMenu())
            case _:
                return None


    # TODO: split these into another file with classes
    def on_draw(self, console: tcod.console.Console) -> None:
        
        #draw the ground
        for ground in g.world.Q.all_of(components=[Position, Graphic], tags=[IsGround]):
            pos = ground.components[Position]
            if not (0 <= pos.x < console.width and 0 <= pos.y < console.height):
                continue
            graphic = ground.components[Graphic]
            console.rgb[["ch", "fg"]][pos.y, pos.x] = graphic.ch, graphic.fg
        
        # drawing walls and such
        for immovable in g.world.Q.all_of(components=[Position, Graphic], tags=[IsWall]):
            pos = immovable.components[Position]
            if not (0 <= pos.x < console.width and 0 <= pos.y < console.height):
                continue
            graphic = immovable.components[Graphic]
            console.rgb[["ch", "fg"]][pos.y, pos.x] = graphic.ch, graphic.fg

        # drawing doors
        for doors in g.world.Q.all_of(components=[Position, Graphic], tags=[IsDoor]):
            pos = doors.components[Position]
            if not (0 <= pos.x < console.width and 0 <= pos.y < console.height):
                continue
            graphic = doors.components[Graphic]
            console.rgb[["ch", "fg"]][pos.y, pos.x] = graphic.ch, graphic.fg


        # draw room floor
        for floor in g.world.Q.all_of(components=[Position, Graphic], tags=[IsFloor]):
            pos = floor.components[Position]
            if not (0 <= pos.x < console.width and 0 <= pos.y < console.height):
                continue
            graphic = floor.components[Graphic]
            console.rgb[["ch", "fg"]][pos.y, pos.x] = graphic.ch, graphic.fg

        # drawing items
        for items in g.world.Q.all_of(components=[Position, Graphic], tags=[IsItem]):
            pos = items.components[Position]
            if not (0 <= pos.x < console.width and 0 <= pos.y < console.height):
                continue
            graphic = items.components[Graphic]
            console.rgb[["ch", "fg"]][pos.y, pos.x] = graphic.ch, graphic.fg
        
        # draw player
        for player in g.world.Q.all_of(components=[Position, Graphic], tags=[IsPlayer]):
            pos = player.components[Position]
            if not (0 <= pos.x < console.width and 0 <= pos.y < console.height):
                continue
            graphic = player.components[Graphic]
            console.rgb[["ch", "fg"]][pos.y, pos.x] = graphic.ch, graphic.fg
 

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


        