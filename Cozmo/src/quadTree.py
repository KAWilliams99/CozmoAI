
import tkinter as tk
from graphics import GraphWin, Rectangle, Line
import taskManager

class QuadTree():
    
    __MAX_OBJECTS = 10
    __MAX_LEVELS = 5

    __level = 0
    __objects = []
    __bounds = {}
    __nodes = []


    def __init__(self, pLevel, pBounds):
        self.__level = int(pLevel)
        self.__bounds = pBounds

    def clear(self):
        self.__objects.clear()
        self.__nodes.clear()

    def __split(self):
        subWidth = self.__bounds['width']/2
        subHeight = self.__bounds['height']/2
        x = self.__bounds['x']
        y = self.__bounds['y']

        self.__nodes[0] = QuadTree(self.__level+1, {x+subWidth, y, subWidth, subHeight})
        self.__nodes[1] = QuadTree(self.__level+1, {x, y, subWidth, subHeight})
        self.__nodes[2] = QuadTree(self.__level+1, {x, y+subHeight, subWidth, subHeight})
        self.__nodes[3] = QuadTree(self.__level+1, {x+subWidth, y+subHeight, subWidth, subHeight})

    def __getIndex(self):

        __index = -1
        verticalMidpoint = self.__bounds['y'] + (self.__bounds['height']/2)
        horizontalMidpoint = self.__bounds['x'] + (self.__bounds['width']/2)

        topQuadrant = (self.__bounds['y'] < verticalMidpoint and self.__bounds['y'] + self.__bounds['height'] < verticalMidpoint)
        bottomQuadrant = (self.__bounds['y'] > verticalMidpoint)

        if(self.__bounds['x'] < horizontalMidpoint and self.__bounds['x'] + self.__bounds['width'] < horizontalMidpoint):
            if(topQuadrant):
                __index = 1
            elif(bottomQuadrant):
                __index = 2
        elif(self.__bounds['x'] > horizontalMidpoint):
            if(topQuadrant):
                __index = 0
            elif(bottomQuadrant):
                __index = 3

        return __index

    def insert(self, pBounds):
        if(self.__nodes[0] is not None):
            indexSet = self.__getIndex()
            if(indexSet is not -1):
                self.__nodes[indexSet].insert(pBounds)
                return

        self.__objects.add(pBounds)

        if(self.__objects.len() > self.__MAX_OBJECTS and self.level < self.__MAX_LEVELS):
            if(self.__nodes[0] is None):
                self.__split()

            i = 0
            while(i < self.__objects.len()):
                index = self.__getIndex(self._objects.get(i))
                if (index is not -1):
                    self.__nodes[index].insert(self.__objects.remove(i))
                else:
                    i = i+1

    def retrieve(self, returnObjects, pBounds):
        index = self.getIndex(pBounds)
        if(index is not -1 and self.__nodes[0] is None):
            self.__nodes[index].retrieve(returnObjects, pBounds)

        returnObjects.add(self.__objects)

        return returnObjects
    
    def get_objs(self):
        objects = []
        for node in self.__nodes:
            objects.append(node.get_objs())
        objects.append(self.__objects)
        return objects


class DrawQuad():
    
    def __init__(self, *objects):
        self.root = tk.Tk()
##        self.window = GraphWin('quad', self.root.winfo.screenwidth()/2, self.root.winfo.screenheight/2)
        self.window = GraphWin('quad', 1920, 1080)
        for obj in objects:
            rect = Rectangle((obj['x'] + obj['width']/2, obj['y'] + obj['height']/2), obj['width'], obj['height'])
            rect.setFill('black')
            rect.draw(self.window)
        