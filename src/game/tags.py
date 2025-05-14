# https://en.wikipedia.org/wiki/Sentinel_value
# hold some sentinel values to be used as tags for {tcod-ecs}. these tags can be anything 
# that is both unique and unchanging, in this case Python strings are used.

from __future__ import annotations

from typing import Final

IsPlayer: Final = "IsPlayer"
# Entity is the player.

IsActor: Final = "IsActor"
# Entity is an actor.

IsGround: Final = "IsGround"
# is ground

IsWall: Final = "IsWall"
# is a wall

IsFloor: Final = "IsFloor"
# is a room floor

IsDoor: Final = "IsDoor"
# is a door

IsItem: Final = "IsItem"
# Entity is an item.

