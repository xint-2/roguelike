# Global constants are stored here

from __future__ import annotations

from typing import Final

from tcod.event import KeySym

CARDINAL = [(0,0), (0,1), (1,1),
            (1,0), (0,-1), (-1,0),
            (-1,-1), (1,-1), (-1,1)]

DIRECTION_KEYS: Final = {
    # Keypad
    KeySym.KP_4: (-1, 0),
    KeySym.KP_6: (1, 0),
    KeySym.KP_8: (0, -1),
    KeySym.KP_2: (0, 1),
    KeySym.KP_7: (-1, -1),
    KeySym.KP_1: (-1, 1),
    KeySym.KP_9: (1, -1),
    KeySym.KP_3: (1, 1),
    KeySym.KP_5: (0, 0),

    # Arrow keys
    KeySym.LEFT: (-1, 0),
    KeySym.RIGHT: (1, 0),
    KeySym.UP: (0, -1),
    KeySym.DOWN: (0, 1),   
}

INTERACTION_KEYS: Final = {
    
    KeySym.e: "interact",
    # interact and go down stairs
    KeySym.d: "stairs"





}
