import pygame
from pygame.locals import *
from vector import Vector2
from constants import *
from entity import Entity
from sprites import PacmanSprites
import random
class Pacman(Entity):
    def __init__(self, node):
        Entity.__init__(self, node )
        self.name = PACMAN    
        self.color = YELLOW
        self.direction = LEFT
        self.setBetweenNodes(LEFT)
        self.alive = True
        self.sprites = PacmanSprites(self)

        self.lastPassedNode = None
        self.currentNode = None

        self.goalNode = None
        self.count = None

        self.previousLast = None
        self.currentdirection = None
        self.count = 0


    def reset(self):
        Entity.reset(self)
        self.direction = LEFT
        self.setBetweenNodes(LEFT)
        self.alive = True
        self.image = self.sprites.getStartImage()
        self.sprites.reset()

    def die(self):
        self.alive = False
        self.direction = STOP

    def update(self, dt, given_dir = None):	
        self.sprites.update(dt)
        self.position += self.directions[self.direction]*self.speed*dt
        direction = self.getValidKey()
        if given_dir is not None:
            direction = given_dir
        if self.overshotTarget():
            self.node = self.target
            if self.node.neighbors[PORTAL] is not None:
                self.node = self.node.neighbors[PORTAL]
            self.target = self.getNewTarget(direction)
            if self.target is not self.node:
                self.direction = direction
            else:
                self.target = self.getNewTarget(self.direction)

            if self.target is self.node:
                self.direction = STOP
    
            self.setPosition()
        else: 
            if self.oppositeDirection(direction):
                self.reverseDirection()

    def getValidKey(self):
        key_pressed = pygame.key.get_pressed()
        if key_pressed[K_UP]:
            return UP
        if key_pressed[K_DOWN]:
            return DOWN
        if key_pressed[K_LEFT]:
            return LEFT
        if key_pressed[K_RIGHT]:
            return RIGHT
        return STOP  

    def eatPellets(self, pelletList):
        for pellet in pelletList:
            if self.collideCheck(pellet):
                return pellet
        return None    
    
    def collideGhost(self, ghost):
        return self.collideCheck(ghost)

    def collideCheck(self, other):
        d = self.position - other.position
        dSquared = d.magnitudeSquared()
        rSquared = (self.collideRadius + other.collideRadius)**2
        if dSquared <= rSquared:
            return True
        return False
    
    def checkIfpacmanonNewNode(self):
        if self.node != self.lastPassedNode:
            lastNode = self.lastPassedNode
            self.lastPassedNode = self.node
            return lastNode, self.node
        return False, False
    
    def shouldPacmanGoThere(self, shortest_path,nodes ,goal_node = None, node_list = None):
        new_target = None
        if self.goalNode is None or shortest_path[goal_node] > 999:
            while not new_target:
                new_target = self.find_random_target(nodes, shortest_path, node_list or nodes.nodesLUT.keys())
                if new_target:
                    self.goalNode = new_target
                    print(f"New goal: {self.goalNode}")
                    return


    ## CHANGED FROM PRESENTATION TO GO FOR RANDOM POINTS INSTEAD (makes little difference)
    def find_random_target(self, nodes, shortest_path, node_list):
        # find a random node with at least 1 false in the visited list
        print('finding new target')
        best_path = 100000
        best_node = None
        max_count = 6
        finished_nodes = []
        for key in node_list:
            if key == (240, 224):
                continue
            try:
                path = shortest_path[key]
            except:
                continue
            count_ = sum(1 for value in nodes.nodesLUT[key].visited.values() if value == False)

            if count_ < max_count:
                max_count = count_
                finished_nodes.append(key)
        
        best_node = finished_nodes[random.randint(0, len(finished_nodes)-1)]
                
        return best_node
        

    def findNewTarget(self, nodes, shortest_path, node_list):
        # find a node with at least 1 false in the visited list
        print('finding new target')
        best_path = 100000
        best_node = None
        max_count = 6
        for key in node_list:
            if key == (240, 224):
                continue
            try:
                path = shortest_path[key]
            except:
                continue
            count_ = sum(1 for value in nodes.nodesLUT[key].visited.values() if value == False)

            if count_ < max_count:
                max_count = count_
                if path < best_path and path < 999:
                    best_path = path
                    best_node = key
        if best_node is None:
            best_node = self.betterfindNewTarget(nodes, shortest_path, node_list)
        return best_node

    def betterfindNewTarget(self, nodes, shortest_path, node_list):
        # find the furthest away node with at least 1 false in the visited list
        # use the manhattan distance to find the furthest away node from self.node
        print('finding new target')
        best_distance = 0
        best_node = None
        max_count = 6
        best_path = 0

        for key in node_list:
            if key == (240, 224):
                continue
            try:
                path = shortest_path[key]
            except:
                continue
            count_ = sum(1 for value in nodes.nodesLUT[key].visited.values() if value == False)
            if count_ < max_count and count_ > 0:
                max_count = count_
                distance = abs(key[0] - self.node.position.x) + abs(key[1] - self.node.position.y)
                if distance > best_distance and path < 999:
                    if path > best_path:
                        best_path = path
                        best_distance = distance
                        best_node = key
        
        if best_node is None:
            best_node = self.goalNode
        return best_node


    def findwhereenemyiscomingfrom(self, ghosts):
        dict_ = {UP:True, DOWN:True, LEFT:True, RIGHT:True}
        
        for ghost in ghosts:
            if ghost.target == self.previousLast or ghost.target == self.node or ghost.target == self.target:
                print('ghost is coming from', ghost.direction)
                if ghost.direction == LEFT:
                    dict_[RIGHT] = False
                if ghost.direction == RIGHT:
                    dict_[LEFT] = False
                if ghost.direction == UP:
                    dict_[DOWN] = False
                if ghost.direction == DOWN:
                    dict_[UP] = False
           
        return dict_
    
    def is_ghost_tooclose(self, ghosts):
        for ghost in ghosts:
            if ghost.target == self.node or ghost.target == self.target:
                return ghost.direction
            # get manhattan distance between ghost and pacman
            distance = abs(ghost.target.position.x - self.node.position.x) + abs(ghost.target.position.y - self.node.position.y)
            if distance < 3:
                return ghost.direction

        return False
                    
                

        
        
