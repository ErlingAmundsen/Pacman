import pygame
from pygame.locals import *
from constants import *
from pacman import Pacman
from nodes import NodeGroup
from pellets import PelletGroup
from ghosts import GhostGroup
from fruit import Fruit
from pauser import Pause
from text import TextGroup
from sprites import LifeSprites
from sprites import MazeSprites
from mazes import MazeController
from mazedata import MazeData######
import algorithms as alg
import random

class GameController(object):
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SCREENSIZE, 0, 32)
        self.background = None
        self.background_norm = None
        self.background_flash = None
        self.clock = pygame.time.Clock()
        self.fruit = None
        self.pause = Pause(True)
        self.level = 0
        self.lives = 5
        self.score = 0
        self.textgroup = TextGroup()
        self.lifesprites = LifeSprites(self.lives)
        self.flashBG = False
        self.flashTime = 0.2
        self.flashTimer = 0
        self.fruitCaptured = []
        self.fruitNode = None
        self.maze = MazeController()
        self.mazedata = MazeData()######

    def setBackground(self):
        self.background_norm = pygame.surface.Surface(SCREENSIZE).convert()
        self.background_norm.fill(BLACK)
        self.background_flash = pygame.surface.Surface(SCREENSIZE).convert()
        self.background_flash.fill(BLACK)
        self.background_norm = self.mazesprites.constructBackground(self.background_norm, self.level%5)
        self.background_flash = self.mazesprites.constructBackground(self.background_flash, 5)
        self.flashBG = False
        self.background = self.background_norm

    def startGame(self):      
        self.mazedata.loadMaze(self.level)
        self.mazesprites = MazeSprites(self.mazedata.obj.name+".txt", self.mazedata.obj.name+"_rotation.txt")
        self.setBackground()
        self.nodes = NodeGroup(self.mazedata.obj.name+".txt")
        self.mazedata.obj.setPortalPairs(self.nodes)
        self.mazedata.obj.connectHomeNodes(self.nodes)
        self.pacman = Pacman(self.nodes.getNodeFromTiles(*self.mazedata.obj.pacmanStart))
        self.pellets = PelletGroup(self.mazedata.obj.name+".txt")
        self.ghosts = GhostGroup(self.nodes.getStartTempNode(), self.pacman)

        self.ghosts.pinky.setStartNode(self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(2, 3)))
        self.ghosts.inky.setStartNode(self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(0, 3)))
        self.ghosts.clyde.setStartNode(self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(4, 3)))
        self.ghosts.setSpawnNode(self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(2, 3)))
        self.ghosts.blinky.setStartNode(self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(2, 0)))
        self.nodes.denyHomeAccess(self.pacman)
        self.nodes.denyHomeAccessList(self.ghosts)
        self.ghosts.inky.startNode.denyAccess(RIGHT, self.ghosts.inky)
        self.ghosts.clyde.startNode.denyAccess(LEFT, self.ghosts.clyde)
        self.mazedata.obj.denyGhostsAccess(self.ghosts, self.nodes)

    def startGame_old(self):      
        self.mazedata.loadMaze(self.level)#######
        self.mazesprites = MazeSprites("maze1.txt", "maze1_rotation.txt")
        self.setBackground()
        self.nodes = NodeGroup("maze1.txt")
        self.nodes.setPortalPair((0,17), (27,17))
        homekey = self.nodes.createHomeNodes(11.5, 14)
        self.nodes.connectHomeNodes(homekey, (12,14), LEFT)
        self.nodes.connectHomeNodes(homekey, (15,14), RIGHT)
        self.pacman = Pacman(self.nodes.getNodeFromTiles(15, 26))
        self.pellets = PelletGroup("maze1.txt")
        self.ghosts = GhostGroup(self.nodes.getStartTempNode(), self.pacman)
        self.ghosts.blinky.setStartNode(self.nodes.getNodeFromTiles(2+11.5, 0+14))
        self.ghosts.pinky.setStartNode(self.nodes.getNodeFromTiles(2+11.5, 3+14))
        self.ghosts.inky.setStartNode(self.nodes.getNodeFromTiles(0+11.5, 3+14))
        self.ghosts.clyde.setStartNode(self.nodes.getNodeFromTiles(4+11.5, 3+14))
        self.ghosts.setSpawnNode(self.nodes.getNodeFromTiles(2+11.5, 3+14))

        self.nodes.denyHomeAccess(self.pacman)
        self.nodes.denyHomeAccessList(self.ghosts)
        self.nodes.denyAccessList(2+11.5, 3+14, LEFT, self.ghosts)
        self.nodes.denyAccessList(2+11.5, 3+14, RIGHT, self.ghosts)
        self.ghosts.inky.startNode.denyAccess(RIGHT, self.ghosts.inky)
        self.ghosts.clyde.startNode.denyAccess(LEFT, self.ghosts.clyde)
        self.nodes.denyAccessList(12, 14, UP, self.ghosts)
        self.nodes.denyAccessList(15, 14, UP, self.ghosts)
        self.nodes.denyAccessList(12, 26, UP, self.ghosts)
        self.nodes.denyAccessList(15, 26, UP, self.ghosts)

    def getDijkstraPath(self):
        lastPacmanNode = self.pacman.target
        lastPacmanNode = self.nodes.getPixelsFromNode(lastPacmanNode)
        previous_nodes, shortest_path = alg.dijkstra_or_a_star(self.nodes, self.ghosts.blinky.target, a_star=True)

        

    def update(self):
        dt = self.clock.tick(30) / 1000.0
        self.textgroup.update(dt)
        self.pellets.update(dt)

        
        if not self.pause.paused:
            self.ghosts.update(dt)      
            if self.fruit is not None:
                self.fruit.update(dt)
            self.checkPelletEvents()
            self.checkGhostEvents()
            self.checkFruitEvents()
        direction = None
        
        if self.pacman.alive:
            
            if not self.pause.paused:
                # self.pacman.position is floats, self.pacman.node.position is ints
                # so we need to check if they are close enough to be considered the same +-1 
        
                # only doing dijkstra if pacman is on a new node and not too close to a ghost
                if self.pacman.collideCheck(self.pacman.target) and not self.pacman.is_ghost_tooclose(self.ghosts):
                    

                    direction = self.pacman.randomDirection(self.pacman.validDirections())
                    
                    # get start node as a tuple (int, int)
                    start_node = self.pacman.target.position.asTuple()

                    # I dont know why I have to do this
                    if start_node == (216.0, 224):
                        start_node = (240, 224)

                    
                    # look into dijkstra_or_a_star as i have done changes there
                    previous_nodes, shortest_path = alg.dijkstra_or_a_star(self.nodes,start_node, a_star=False,ghosts = self.ghosts)
    

                
                    node_list = list(self.nodes.nodesLUT.keys())

                    # finds the best node to go to given that we want a long path
                    self.pacman.shouldPacmanGoThere(shortest_path, self.nodes,self.pacman.goalNode, node_list)
                    
                    node = self.pacman.goalNode

                    
                    # makes sure we have a destination
                    if node != None:
                        while shortest_path[node] == 0:

                            node_list.remove(node)
                            node = self.pacman.findNewTarget(self.nodes, shortest_path, node_list)
                            if node == None:
                                break
                            print('shortest', shortest_path[node])
                    self.pacman.goalNode = node
                    last = None
                    count = 0
                    
                        
                    # finds the first node from djikstra that is not the start node
                    if node != start_node and node is not None:
                        count = 0
                        while node != start_node:
                            if previous_nodes[node] == start_node:
                                last = node
                                count += 1
                            node = previous_nodes[node]
                    self.pacman.count = count
                    if last == None:
                        last = node

                        
            
                    # if we have a path we can follow
                    if node == None:    
                        print('no path found')
                        possible_directions = self.pacman.findwhereenemyiscomingfrom(self.ghosts)
                        print(possible_directions)
                        for direction in possible_directions:
                            if possible_directions[direction] and self.nodes.nodesLUT[start_node].neighbors[direction] is not None:
                                break
                        if direction == None:
                            direction = random.choice(self.pacman.validDirections())
                    else:
                    
                        direction = self.nodes.getDirection(self.nodes.nodesLUT[start_node], self.nodes.nodesLUT[last])
                    
                
                old, new = self.pacman.checkIfpacmanonNewNode()
                if old and not self.pacman.is_ghost_tooclose(self.ghosts):

                    # updates the visited nodes and the length of the neighbors
                    old = old.position.asTuple()
                    new = new.position.asTuple()
                    dir_ = self.nodes.getDirection(self.nodes.nodesLUT[old], self.nodes.nodesLUT[new])
                    if dir_ is not None:
                        self.nodes.nodesLUT[old].visited[dir_] = True
                        self.nodes.nodesLUT[new].visited[dir_*-1] = True



                        self.nodes.nodesLUT[old].neighborslength[dir_] += 10
                        self.nodes.nodesLUT[new].neighborslength[dir_*-1] += 10
                

                
                if self.pacman.is_ghost_tooclose(self.ghosts):
                    direction = self.pacman.is_ghost_tooclose(self.ghosts)
                    # check if direction is valid   
                    
                    for new_direction in self.nodes.nodesLUT[self.pacman.node.position.asTuple()].neighbors:
                        print('HELLO')
                        if new_direction is not None and new_direction != direction * -1:
                            break
                    direction = new_direction
            
        
                self.pacman.update(dt, direction)
        else:
            self.pacman.update(dt)

        if self.flashBG:
            self.flashTimer += dt
            if self.flashTimer >= self.flashTime:
                self.flashTimer = 0
                if self.background == self.background_norm:
                    self.background = self.background_flash
                else:
                    self.background = self.background_norm

        afterPauseMethod = self.pause.update(dt)
        if afterPauseMethod is not None:
            afterPauseMethod()
        self.checkEvents()
        self.render()

    def checkEvents(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    if self.pacman.alive:
                        self.pause.setPause(playerPaused=True)
                        if not self.pause.paused:
                            self.textgroup.hideText()
                            self.showEntities()
                        else:
                            self.textgroup.showText(PAUSETXT)
                            #self.hideEntities()

    def checkPelletEvents(self):
        pellet = self.pacman.eatPellets(self.pellets.pelletList)
        if pellet:
            self.pellets.numEaten += 1
            self.updateScore(pellet.points)
            if self.pellets.numEaten == 30:
                self.ghosts.inky.startNode.allowAccess(RIGHT, self.ghosts.inky)
            if self.pellets.numEaten == 70:
                self.ghosts.clyde.startNode.allowAccess(LEFT, self.ghosts.clyde)
            self.pellets.pelletList.remove(pellet)
            if pellet.name == POWERPELLET:
                self.ghosts.startFreight()
            if self.pellets.isEmpty():
                self.flashBG = True
                self.hideEntities()
                self.pause.setPause(pauseTime=3, func=self.nextLevel)

    def checkGhostEvents(self):
        for ghost in self.ghosts:
            if self.pacman.collideGhost(ghost):
                if ghost.mode.current is FREIGHT:
                    self.pacman.visible = False
                    ghost.visible = False
                    self.updateScore(ghost.points)                  
                    self.textgroup.addText(str(ghost.points), WHITE, ghost.position.x, ghost.position.y, 8, time=1)
                    self.ghosts.updatePoints()
                    self.pause.setPause(pauseTime=1, func=self.showEntities)
                    ghost.startSpawn()
                    self.nodes.allowHomeAccess(ghost)
                elif ghost.mode.current is not SPAWN:
                    if self.pacman.alive:
                        self.lives -=  1
                        self.lifesprites.removeImage()
                        self.pacman.die()               
                        self.ghosts.hide()
                        if self.lives <= 0:
                            self.textgroup.showText(GAMEOVERTXT)
                            self.pause.setPause(pauseTime=3, func=self.restartGame)
                        else:
                            self.pause.setPause(pauseTime=3, func=self.resetLevel)
    
    def checkFruitEvents(self):
        if self.pellets.numEaten == 50 or self.pellets.numEaten == 140:
            if self.fruit is None:
                self.fruit = Fruit(self.nodes.getNodeFromTiles(9, 20), self.level)
                print(self.fruit)
        if self.fruit is not None:
            if self.pacman.collideCheck(self.fruit):
                self.updateScore(self.fruit.points)
                self.textgroup.addText(str(self.fruit.points), WHITE, self.fruit.position.x, self.fruit.position.y, 8, time=1)
                fruitCaptured = False
                for fruit in self.fruitCaptured:
                    if fruit.get_offset() == self.fruit.image.get_offset():
                        fruitCaptured = True
                        break
                if not fruitCaptured:
                    self.fruitCaptured.append(self.fruit.image)
                self.fruit = None
            elif self.fruit.destroy:
                self.fruit = None

    def showEntities(self):
        self.pacman.visible = True
        self.ghosts.show()

    def hideEntities(self):
        self.pacman.visible = False
        self.ghosts.hide()

    def nextLevel(self):
        self.showEntities()
        self.level += 1
        self.pause.paused = True
        self.startGame()
        self.textgroup.updateLevel(self.level)

    def restartGame(self):
        self.lives = 5
        self.level = 0
        self.pause.paused = True
        self.fruit = None
        self.startGame()
        self.score = 0
        self.textgroup.updateScore(self.score)
        self.textgroup.updateLevel(self.level)
        self.textgroup.showText(READYTXT)
        self.lifesprites.resetLives(self.lives)
        self.fruitCaptured = []

    def resetLevel(self):
        self.pause.paused = True
        self.pacman.reset()
        self.ghosts.reset()
        self.fruit = None
        self.textgroup.showText(READYTXT)

    def updateScore(self, points):
        self.score += points
        self.textgroup.updateScore(self.score)

    def render(self):
        self.screen.blit(self.background, (0, 0))
        #self.nodes.render(self.screen)
        self.pellets.render(self.screen)
        if self.fruit is not None:
            self.fruit.render(self.screen)
        self.pacman.render(self.screen)
        self.ghosts.render(self.screen)
        self.textgroup.render(self.screen)

        for i in range(len(self.lifesprites.images)):
            x = self.lifesprites.images[i].get_width() * i
            y = SCREENHEIGHT - self.lifesprites.images[i].get_height()
            self.screen.blit(self.lifesprites.images[i], (x, y))

        for i in range(len(self.fruitCaptured)):
            x = SCREENWIDTH - self.fruitCaptured[i].get_width() * (i+1)
            y = SCREENHEIGHT - self.fruitCaptured[i].get_height()
            self.screen.blit(self.fruitCaptured[i], (x, y))
        pygame.display.update()


if __name__ == "__main__":
    game = GameController()
    game.startGame()
    # print the LUT of all the nodes
    # print(game.nodes.nodesLUT)
    # print(len(game.nodes._count))
    # print the amount of edges
    
    #TLDR commented below is to see if we have the correct amount of edges
    # in our lengthj table
    
    # edge_count = 0d
    # seen_nodes = []
    # for node in game.nodes.nodesLUT:
    #     neighbours = game.nodes.getNeighbors(node)
    #     for neighbour in neighbours:
    #         pair = (node, neighbour)
    #         pair2 = (neighbour, node)
    #         if pair not in seen_nodes and pair2 not in seen_nodes:
    #             seen_nodes.append(pair)
    #             seen_nodes.append(pair2)
    #             edge_count += 1
    # print(edge_count)
        
    while True:
        game.update()



