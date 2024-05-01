import pygame
from vector import Vector2
from constants import *
import numpy as np
import sys

class Node(object):
    def __init__(self, x, y):
        self.position = Vector2(x, y)
        self.neighbors = {UP:None, DOWN:None, LEFT:None, RIGHT:None, PORTAL:None}

        self.neighbors_costs = {}
        
        ## added this for easier lookup later and we can initalize it at game start
        ## set to max just in case we dont map an edge
        self.neighborslength = {UP:None, DOWN:None, LEFT:None, RIGHT:None, PORTAL:None}
        ## This will be the check if the edge in that direction has been visited, so that we will be sure
        ## to continue untill all edges have been visited
        self.visited = {UP:None, DOWN:None, LEFT:None, RIGHT:None, PORTAL:None}
        
        self.access = {UP:[PACMAN, BLINKY, PINKY, INKY, CLYDE, FRUIT], 
                       DOWN:[PACMAN, BLINKY, PINKY, INKY, CLYDE, FRUIT], 
                       LEFT:[PACMAN, BLINKY, PINKY, INKY, CLYDE, FRUIT], 
                       RIGHT:[PACMAN, BLINKY, PINKY, INKY, CLYDE, FRUIT]}
        
        # added this to check if pacman is on a node
        self.collideRadius = 0

    def denyAccess(self, direction, entity):
        if entity.name in self.access[direction]:
            self.access[direction].remove(entity.name)

    def allowAccess(self, direction, entity):
        if entity.name not in self.access[direction]:
            self.access[direction].append(entity.name)

    def render(self, screen):
        for n in self.neighbors.keys():
            if self.neighbors[n] is not None:
                line_start = self.position.asTuple()
                line_end = self.neighbors[n].position.asTuple()
                pygame.draw.line(screen, WHITE, line_start, line_end, 4)
                pygame.draw.circle(screen, RED, self.position.asInt(), 12)


class NodeGroup(object):
    def __init__(self, level):
        self.level = level
        self.nodesLUT = {}
        self.nodeSymbols = ['+', 'P', 'n']
        self.pathSymbols = ['.', '-', '|', 'p']
        self._count = []
        data = self.readMazeFile(level)
        self.createNodeTable(data)
        self.connectHorizontally(data)
        self.connectVertically(data)
        self.homekey = None
        self.costs = self.get_nodes()
        self.data = data
        self.calc_distance(self.getStartTempNode())

    def readMazeFile(self, textfile):
        return np.loadtxt(textfile, dtype='<U1')
    
    ## added all below functions to calculate distance when creating the nodes
    ## to save time when calculating the path later on

    def checknext(self, next):
        # currently treating 
        if next == '.' or next == 'p':
            return DISTANCEDICT[PELLET]
        elif next == '-' or next == '|':
            return DISTANCEDICT[NOPELLET]
        if next == 'P' or next == 'n' or next == '+':
            return None
        else:
            return False
    

    def getlenghtright(self, data, row, col, lenght=0):
        lenght = 0
        check = True
        next_row = int(row)
        next_col = int(col)
        while check is not None:
            try:
                next = data[next_row][next_col+1]
            except Exception as e:
                print('error', e)
                return lenght
            check = self.checknext(next)
            if check is not None:
                lenght += check
            next_col += 1
        return lenght
    
    def getlenghtdown(self, data, row, col, lenght=0):
        lenght = 0
        check = True
        next_row = int(row)
        next_col = int(col)
        while check is not None:
            try:
                next = data[next_row-1][next_col]
            except:
                print('error on down')
                return lenght
            check = self.checknext(next)
            if check is not None:
                lenght += check
            next_row -= 1
        return lenght
    

    def createNodeTable(self, data, xoffset=0, yoffset=0):
        for row in list(range(data.shape[0])):
            for col in list(range(data.shape[1])):
                if data[row][col] in self.nodeSymbols:
                    x, y = self.constructKey(col+xoffset, row+yoffset)
                    self.nodesLUT[(x, y)] = Node(x, y)
                    

    def constructKey(self, x, y):
        return x * TILEWIDTH, y * TILEHEIGHT
    

    
    def connectHorizontally(self, data, xoffset=0, yoffset=0):
        for row in list(range(data.shape[0])):
            key = None
            for col in list(range(data.shape[1])):
                if data[row][col] in self.nodeSymbols:
                    if key is None:
                        key = self.constructKey(col+xoffset, row+yoffset)
                    else:
                        otherkey = self.constructKey(col+xoffset, row+yoffset)


                        self.nodesLUT[key].neighbors[RIGHT] = self.nodesLUT[otherkey]
                        self.nodesLUT[otherkey].neighbors[LEFT] = self.nodesLUT[key]
                       
                       # added this to get the lenght of the edge, adds same lenght to both nodes
                        # since they are the same edge
                        # len_right = self.getlenghtright(data, row, col)
                        # if len_right > 0:
                        #     self.nodesLUT[key].neighborslength[RIGHT] = len_right
                        #     self.nodesLUT[otherkey].neighborslength[LEFT] = len_right


                        # # here for debugging
                        # self._count.append(len_right)
                        
                        key = otherkey
                elif data[row][col] not in self.pathSymbols:
                    key = None

    def connectVertically(self, data, xoffset=0, yoffset=0):
        dataT = data.transpose()
        for col in list(range(dataT.shape[0])):
            key = None
            for row in list(range(dataT.shape[1])):
                if dataT[col][row] in self.nodeSymbols:
                    if key is None:
                        key = self.constructKey(col+xoffset, row+yoffset)
                    else:
                        otherkey = self.constructKey(col+xoffset, row+yoffset)
                        self.nodesLUT[key].neighbors[DOWN] = self.nodesLUT[otherkey]
                        self.nodesLUT[otherkey].neighbors[UP] = self.nodesLUT[key]

                        # ## see above
                        # len_down = self.getlenghtdown(dataT, row, col)
                        # if len_down > 0:
                        #     self.nodesLUT[key].neighborslength[DOWN] = len_down
                        #     self.nodesLUT[otherkey].neighborslength[UP] = len_down

                        # ## here for debugging
                        # self._count.append(len_down)


                        key = otherkey
                elif dataT[col][row] not in self.pathSymbols:
                    key = None


    def getStartTempNode(self):
        nodes = list(self.nodesLUT.values())
        return nodes[0]

    def setPortalPair(self, pair1, pair2):
        key1 = self.constructKey(*pair1)
        key2 = self.constructKey(*pair2)
        if key1 in self.nodesLUT.keys() and key2 in self.nodesLUT.keys():
            self.nodesLUT[key1].neighbors[PORTAL] = self.nodesLUT[key2]
            self.nodesLUT[key2].neighbors[PORTAL] = self.nodesLUT[key1]

    def createHomeNodes(self, xoffset, yoffset):
        homedata = np.array([['X','X','+','X','X'],
                             ['X','X','.','X','X'],
                             ['+','X','.','X','+'],
                             ['+','.','+','.','+'],
                             ['+','X','X','X','+']])

        self.createNodeTable(homedata, xoffset, yoffset)
        self.connectHorizontally(homedata, xoffset, yoffset)
        self.connectVertically(homedata, xoffset, yoffset)
        self.homekey = self.constructKey(xoffset+2, yoffset)
        return self.homekey

    def connectHomeNodes(self, homekey, otherkey, direction):     
        key = self.constructKey(*otherkey)
        self.nodesLUT[homekey].neighbors[direction] = self.nodesLUT[key]
        self.nodesLUT[key].neighbors[direction*-1] = self.nodesLUT[homekey]

    def getNodeFromPixels(self, xpixel, ypixel):
        if (xpixel, ypixel) in self.nodesLUT.keys():
            return self.nodesLUT[(xpixel, ypixel)]
        return None

    def getNodeFromTiles(self, col, row):
        x, y = self.constructKey(col, row)
        if (x, y) in self.nodesLUT.keys():
            return self.nodesLUT[(x, y)]
        return None
    
    ## Added this to implement Dijkstra's and or A*
    ## stolen from Homework 2
    def getListOfNodesPixels(self):
        return list(self.nodesLUT)

    # returns a node in (x,y) format
    def getPixelsFromNode(self, node):
        id = list(self.nodesLUT.values()).index(node)
        listOfPix = self.getListOfNodesPixels()
        return listOfPix[id]
    
    def denyAccess(self, col, row, direction, entity):
        node = self.getNodeFromTiles(col, row)
        if node is not None:
            node.denyAccess(direction, entity)

    def allowAccess(self, col, row, direction, entity):
        node = self.getNodeFromTiles(col, row)
        if node is not None:
            node.allowAccess(direction, entity)

    def denyAccessList(self, col, row, direction, entities):
        for entity in entities:
            self.denyAccess(col, row, direction, entity)

    def allowAccessList(self, col, row, direction, entities):
        for entity in entities:
            self.allowAccess(col, row, direction, entity)

    def denyHomeAccess(self, entity):
        self.nodesLUT[self.homekey].denyAccess(DOWN, entity)

    def allowHomeAccess(self, entity):
        self.nodesLUT[self.homekey].allowAccess(DOWN, entity)

    def denyHomeAccessList(self, entities):
        for entity in entities:
            self.denyHomeAccess(entity)

    def allowHomeAccessList(self, entities):
        for entity in entities:
            self.allowHomeAccess(entity)

    def render(self, screen):
        for node in self.nodesLUT.values():
            node.render(screen)


    ## made by me
            

    def getDirection(self, node1, node2):
        if node1.position.x == node2.position.x:
            if node1.position.y > node2.position.y:
                return UP
            else:
                return DOWN
        elif node1.position.y == node2.position.y:
            if node1.position.x > node2.position.x:
                return LEFT
            else:
                return RIGHT
        return None
    




    #################
    #################
    #################
    ################# 
            
    ## ADDEd from Homework 3
    def getListOfNodesVector(self):
        return list(self.nodesLUT)

    # returns a node in (x,y) format
    def getVectorFromLUTNode(self, node):
        id = list(self.nodesLUT.values()).index(node)
        listOfVectors = self.getListOfNodesVector()
        return listOfVectors[id]        
    
    def getNeighborsObj(self, node):
        node_obj = self.getNodeFromPixels(node[0], node[1])
        return node_obj.neighbors

    
    def getNeighbors(self, node):
        neighs_LUT = self.getNeighborsObj(node)
        vals = neighs_LUT.values()
        neighs_LUT2 = []
        for direction in vals:
            if not direction is None:
                neighs_LUT2.append(direction)
        list_neighs = []
        for neigh in neighs_LUT2:
            list_neighs.append(self.getVectorFromLUTNode(neigh))
        return list_neighs

    
    def get_nodes(self):
        costs_dict = {}
        listOfNodesPixels = self.getListOfNodesVector()
        for node in listOfNodesPixels:
            neigh = self.getNeighborsObj(node)
            temp_neighs = neigh.values()
            temp_list = []
            for direction in temp_neighs:
                if not direction is None:
                    temp_list.append(1)
                else:
                    temp_list.append(None)
            costs_dict[node] = temp_list
        print(costs_dict)
        return costs_dict
    
    ## made to get the lenght of the edge between two nodes
    def calc_distance_helper(self, node1, node2):
        if node1.position.x == node2.position.x:
            if node1.position.y > node2.position.y:
                return self.getlenghtdown(self.data, node1.position.y//TILEHEIGHT, node1.position.x//TILEWIDTH)
            else:
                return self.getlenghtdown(self.data, node2.position.y//TILEHEIGHT, node2.position.x//TILEWIDTH)
        elif node1.position.y == node2.position.y:
            start_col = min(node1.position.x, node2.position.x) // TILEWIDTH
            return self.getlenghtright(self.data, node1.position.y // TILEHEIGHT, start_col)

    
    def calc_distance(self, node1):
        # itterate over all nodes and get the distance to all neighbors then store it in the node.
        nodes = self.nodesLUT
        for node in nodes:
            neighs = nodes[node].neighbors
            for direction in neighs:
                if neighs[direction] is not None:
                    actual_dir = self.getDirection(nodes[node], neighs[direction])
                    dist = self.calc_distance_helper(nodes[node], neighs[direction])
                    if dist == 0:
                        # debuggin tool
                        print(node, direction, neighs[direction], 'dist = 0')
                    nodes[node].neighborslength[actual_dir] = dist
                    nodes[node].visited[actual_dir] = False


