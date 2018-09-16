# Auth: Keon Williams
# Version: No. 1
# Node


from enum import Enum
from _testmultiphase import Str

class TILE(Enum):
    WALL = '#'
    START = 'S'
    END = 'E'
    OPEN = '.'
class OPENTYPE(list):
    DEADEND = str
    CORNER = str
    CROSSROADS = str

class Node():

    std_size = (1/16, 1/16)
    tile_type = None # type: TILE
    dirs = None # type: OPENTYPE
    place = [0, 0]
    
    def __init__(self, nodeType, dX, dY):
        self.place[0] = dX
        self.place[1] = dY
        if not isinstance(nodeType, Str):
            raise TypeError('nodeType must be of type char to instantiate a Node')
        else:
            self.tile_type = nodeType

    def tileSetter(self, directions:list):
        self.switch(len(directions))

    def switch(self, dirs):
        switcher = {
            '1': OPENTYPE.DEADEND,
            '2': OPENTYPE.CORNER,
            '3': OPENTYPE.CROSSROADS,
            '4': OPENTYPE.CROSSROADS
            }
        return switcher(dirs)
