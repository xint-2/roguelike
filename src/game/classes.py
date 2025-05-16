# might be useful, idk yet

from __future__ import annotations
import attrs

from game.components import Position, Graphic
from game.tags import *

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


        
