from compositecore import Leaf, CompositeMessage
from dungeonlevelfactory import unknown_level_map


class MemoryMap(Leaf):
    """
    A representation of the dungeon as seen by an entity.
    """
    def __init__(self):
        super(MemoryMap, self).__init__()
        self.component_type = "memory_map"
        self._memory_map = []

    def get_memory_of_map(self, dungeon_level):
        self.set_memory_map_if_not_set(dungeon_level)
        return self._memory_map[dungeon_level.depth]

    def set_memory_map_if_not_set(self, dungeon_level):
        """
        Lazily initiates unknown dungeon to the depth needed.
        """
        depth = dungeon_level.depth
        while(len(self._memory_map) <= depth):
            self._memory_map.append(None)
        if(self._memory_map[depth] is None):
            self._memory_map[depth] =\
                unknown_level_map(dungeon_level.width,
                                  dungeon_level.height,
                                  dungeon_level.depth)

    def update_memory_of_tile(self, tile, position, depth):
        """
        Writes the entity memory of a tile, to the memory map.
        """
        if (tile.get_first_entity() is self):
            return  # No need to remember where you was, you are not there.
        self.set_memory_map_if_not_set(self.parent.dungeon_level.dungeon_level)
        x, y = position
        self._memory_map[depth].tile_matrix[y][x] = tile.copy()

    def message(self, message):
        """
        Handles messages recieved.
        """
        if(message == CompositeMessage.DUNGEON_LEVEL_CHANGED):
            self.set_memory_map_if_not_set(self.parent.
                                           dungeon_level.dungeon_level)