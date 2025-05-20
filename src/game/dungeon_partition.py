# TODO: this is going to be where dungeons are generated
# TODO: move room drawing here?
# TODO: create connect rooms functions

import tcod.bsp
from tcod import libtcodpy

class Rect:
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        cx = (self.x1 + self.x2) // 2
        cy = (self.y1 + self.y2) // 2
        return(cx, cy)
    
    def closest_edge_point(self, tx, ty):
        # Clamp target (tx, ty) to the edge of this rectangle
        x = min(max(tx, self.x1), self.x2 - 1)
        y = min(max(ty, self.y1), self.y2 - 1)
        # If inside, push to nearest edge
        if self.x1 < tx < self.x2 - 1 and self.y1 < ty < self.y2 - 1:
            dx = min(tx - self.x1, self.x2 - 1 - tx)
            dy = min(ty - self.y1, self.y2 - 1 - ty)
            if dx < dy:
                x = self.x1 if tx - self.x1 < self.x2 - 1 - tx else self.x2 - 1
            else:
                y = self.y1 if ty - self.y1 < self.y2 - 1 - ty else self.y2 - 1
        return (x, y)


      
    def __repr__(self):
        return f"Rect({self.x1},{self.y1},{self.x2-self.x1},{self.y2-self.y1})"
    
def make_bsp_rooms(map_width=80, map_height=60, depth=5, min_size=6):
        bsp = tcod.bsp.BSP(x=0, y=0, width=map_width, height=map_height)
        bsp.split_recursive(
            depth=depth,
            min_width=min_size,
            min_height=min_size,
            max_horizontal_ratio=1.5,
            max_vertical_ratio=1.5,
        )

        def find_leaf_room(node):
        # recursively find a room in the leaves of this node.
            if hasattr(node, "room"):
                return node.room
            elif node.children:
                for child in node.children:
                    room = find_leaf_room(child)
                    if room:
                        return room
            return None
        

        rooms = []

        def create_room(node):
            # shrink the room a bit to leave walls between rooms
            margin = 2
            room_w = max(2, node.width - margin * 2)
            room_h = max(2, node.height - margin * 2)
            room_x = node.x + 1
            room_y = node.y + 1
            room = Rect(room_x, room_y, room_w, room_h)
            rooms.append(room)
            node.room = room
        
        for node in bsp.pre_order():
            if not node.children:
                create_room(node)

        # connect rooms
        corridors = []
        for node in bsp.pre_order():
            if node.children:
                left = node.children[0]
                right = node.children[1]
                left_room = find_leaf_room(left)
                right_room = find_leaf_room(right)
                if left_room and right_room:
                    lcx, lcy = left_room.center()
                    rcx, rcy = right_room.center()
                    left_edge = left_room.closest_edge_point(rcx, rcy)
                    right_edge = right_room.closest_edge_point(lcx, lcy)
                    # simple straight corridor
                    if libtcodpy.random_get_int(0, 0, 1):
                        corridors.append((left_edge, (right_edge[0], left_edge[1])))
                        corridors.append(((right_edge[0], left_edge[1]), right_edge))
                    else:
                        corridors.append((left_edge, (left_edge[0], right_edge[1])))
                        corridors.append(((left_edge[0], right_edge[1]), right_edge))

                    
        return rooms, corridors
