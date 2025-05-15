# hold components for graphics and position of entities
# holds other values for entities as well such as door value

import attrs
import tcod.ecs.callbacks
from tcod.ecs import Entity

from typing import Self, Final

@attrs.define(frozen=True)
class Position:
    # an entities position

    x: int
    y: int

    def __add__(self, direction: tuple[int, int]) -> Self:
        # add a vector to this position.
        x, y = direction
        return self.__class__(self.x + x, self.y + y)

@tcod.ecs.callbacks.register_component_changed(component=Position)
def on_position_changed(entity : Entity, old: Position | None, new: Position | None) -> None:
    # mirror position components as a tag
    if old == new: # new position is equivalent to its previous value
        return # Ignore and return
    if old is not None: # Position component removed or chaged
        entity.tags.discard(old) # remove old position from tags
    if new is not None: #poisiton component added or changed 
        entity.tags.add(new) # add new position to tags


@attrs.define(frozen=True)
class Graphic:
    # an entities icon and color.

    ch: int = ord("!")
    fg: tuple[int, int, int] = (255, 255, 255)

@attrs.define(frozen=False)
class DoorState:
    is_open: bool = False


Gold: Final = ("Gold", int)
# amount of gold.

