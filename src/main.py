from __future__ import annotations


import tcod.console
import tcod.tileset
import tcod.context

import g
import game.states
import game.state_tools

#WIDTH, HEIGHT = 80, 50
#FLAGS = tcod.context.SDL_WINDOW_RESIZABLE | tcod.context.SDL_WINDOW_MAXIMIZED

def main() -> None:
    """Entry point function."""
    tileset = tcod.tileset.load_tilesheet(
        "data/Alloy_curses_12x12.png", columns=16, rows=16, charmap=tcod.tileset.CHARMAP_CP437
    )
    tcod.tileset.procedural_block_elements(tileset=tileset)
    g.states = [game.states.MainMenu()]
    g.console = tcod.console.Console(80, 50)
    with tcod.context.new(console=g.console, tileset=tileset) as g.context:
        game.state_tools.main_loop()






""" Dynamic Window Sizing
def main() -> None:
    # Entry point function. 
    tileset = tcod.tileset.load_tilesheet(
        "data/Alloy_curses_12x12.png", columns=16, rows=16, charmap=tcod.tileset.CHARMAP_CP437
    )
    tcod.tileset.procedural_block_elements(tileset=tileset)
    g.states = [game.states.MainMenu()]
    with tcod.context.new(width=WIDTH, height=HEIGHT, tileset=tileset, sdl_window_flags=FLAGS) as g.context:
        while True:
            g.console = g.context.new_console()
            g.context.present(g.console, integer_scaling=True)
            game.state_tools.main_loop()
"""











if __name__ == "__main__":
    main()