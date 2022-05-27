# =============================================================
#                       RRT algorithm
# =============================================================

"""
Authors: Jai Sharma and Divyansh Agrawal
Assignment: Project 5 - RRT
Task: implement RRT-Connect algorithm on 2d Map for Point Robot
"""
# import Libraries
import math
import random
import sys
import time
import pygame

# =============================================================
#                       RRT class
# =============================================================

class RRTconnect:
    
    class Node:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.path_x = []   # Path to x
            self.path_y = []   # Path to y
            self.parent = None
            
        def __repr__(self):
            return f'X: {self.x},Y: {self.y}'

    # initialize the object's states
    def __init__(self,start,goal,rand_area,expand_dis=0.1,path_resolution=0.05, goal_sample_rate = 1, max_iter=5000):
        self.start = self.Node(start[0], start[1])   # start node [x,y]
        self.end = self.Node(goal[0], goal[1])       # goal node [x,y]
        self.expand_dis = expand_dis                # step size, set to 0.1 
        self.path_resolution = path_resolution      # nodes can be accurate to 0.05
        self.goal_sample_rate = goal_sample_rate    # set to 1
        self.max_iter = max_iter                    # number of iterations to run, set to 3000
        self.node_list = []                         # saves node information
        
        self.V1 = [self.start]
        self.V2 = [self.end]
    

    # path planning function --> solve and visualize at the same time
    def algorithm(self, animation=True):
        mf = 100                # magnifying factor
        counter = 0
        path = None
        
        pygame.init()
        screen = pygame.display.set_mode((mf*10, mf*10))
        counter = 0
        path = None
        
        screen.fill((25,25,25))
        obstacleCol = (255,255,255)
        pygame.draw.circle(screen, obstacleCol, (100*2.5, 100*2.5), 100*1)
        pygame.draw.circle(screen, obstacleCol, (100*7.5, 100*2.5), 100*1)
        pygame.draw.circle(screen, obstacleCol, (100*7.5, 100*7.5), 100*1)
        pygame.draw.circle(screen, obstacleCol, (100*2.5, 100*7.5), 100*1)
        pygame.draw.circle(screen, obstacleCol, (100*5, 100*5), 100*1)
            
        # Goal threshold
        pygame.draw.circle(screen, (0,255,0), (mf*self.end.x, mf*10-(mf*self.end.y)), 14)
        pygame.draw.circle(screen, (0,0,255), (mf*self.start.x, mf*10-(mf*self.start.y)), 14)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        if counter == 0:
            # initialize  the remaining N-number of nodes
            for i in range(self.max_iter):
                time.sleep(0.01)
                # print("====================================================================================================================================================")
                
                # start node side
                rnd_node_S = self.getRandom()      # get random node
                nearest_ind_S = self.getNodeIndex(self.V1,rnd_node_S)                   # get nearest index
                nearest_node_S = self.V1[nearest_ind_S]                           # get node associated with nearest index
                new_node_S = self.steer(nearest_node_S, rnd_node_S, self.expand_dis)       # get new node

                # check if the edge enters obstacle space
                if self.obstacleCheck(new_node_S):
                    # print("A")
                    self.V1.append(new_node_S)   # record newNode if valid
                    # Drawing the nodes and edges
                    pygame.draw.circle(screen, (176,224,230), (100*new_node_S.x, 100*10 - 100*new_node_S.y), 4)
                    pygame.draw.line(screen, (0,0,255), (100*nearest_node_S.x, 100*10 - 100*nearest_node_S.y), (100*new_node_S.x, 100*10 - 100*new_node_S.y),3)

                # goal node side
                rnd_node_E = self.getRandom()      # get random node
                nearest_ind_E = self.getNodeIndex(self.V2,rnd_node_E)                   # get nearest index
                nearest_node_E = self.V2[nearest_ind_E]                           # get node associated with nearest index
                new_node_E = self.steer(nearest_node_E, rnd_node_E, self.expand_dis)       # get new node

                # check if the edge enters obstacle space
                if self.obstacleCheck(new_node_E):
                    self.V2.append(new_node_E)   # record newNode if valid
                    pygame.draw.circle(screen, (176,224,230), (100*new_node_E.x, 100*10 - 100*new_node_E.y), 4)
                    pygame.draw.line(screen, (0,255,0), (100*nearest_node_E.x, 100*10 - 100*nearest_node_E.y), (100*new_node_E.x, 100*10 - 100*new_node_E.y),3)

                # condition to see of they connect
                distance, _ = self.distAng(new_node_E,new_node_S)
                if distance < 0.05:
                    print("Goal Reached!!")
                    # print("E")
                    path_coord, fullNode_Path = self.backTrack(new_node_S, new_node_E)
                    fullNode_Path_copy = fullNode_Path
                    path_coord_copy = path_coord
                    for point in path_coord:
                        pygame.draw.circle(screen, (255,0,0), (100*point[0], 10*100-100*point[1]), 5)
                        pygame.display.update()
                    time.sleep(10)                                
                    return(path)
                    
                if len(self.V2) < len(self.V1):
                    midList = self.V2
                    self.V2 = self.V1
                    self.V1 = midList
                    
                pygame.display.update()
        

        return(None)
                        
    # function to steer from nearNode to randNode  --> get New Node
    def steer(self, fromN, toN, extend_length = float("inf") ):
            
        new_node = self.Node(fromN.x, fromN.y)
        d, theta = self.distAng(new_node, toN) # straight line, (distance and angle)

        new_node.path_x = [new_node.x]
        new_node.path_y = [new_node.y]

        extend_length = min(d, extend_length)
        n_expand = math.floor(extend_length / self.path_resolution) # round down
        # print("ExtensionLength = ", extend_length)

        for _ in range(n_expand):
            # update node values
            new_node.x += self.path_resolution * math.cos(theta)
            new_node.y += self.path_resolution * math.sin(theta)
            new_node.path_x.append(new_node.x)
            new_node.path_y.append(new_node.y)

        d, _ = self.distAng(new_node, toN)
        
        # if randNode is within step size of node
        if d <= self.path_resolution:  
            new_node.path_x.append(toN.x)
            new_node.path_y.append(toN.y)
            new_node.x = toN.x
            new_node.y = toN.y

        new_node.parent = fromN

        return(new_node)

    def steerAgain(self, fromN, toN, extend_length = float("inf") ):
            
        new_node = self.Node(fromN.x, fromN.y)
        new_node_copy = self.Node(fromN.x, fromN.y)
        d, theta = self.distAng(new_node, toN) # straight line, (distance and angle)

        new_node.path_x = [new_node.x]
        new_node.path_y = [new_node.y]

        extend_length = min(d, extend_length)
        n_expand = math.floor(extend_length / self.path_resolution) # round down
        for _ in range(n_expand):
            # update node values
            new_node.x += self.path_resolution * math.cos(theta)
            new_node.y += self.path_resolution * math.sin(theta)
            new_node.path_x.append(new_node.x)
            new_node.path_y.append(new_node.y)

            if not self.obstacleCheck(new_node):
                return new_node_copy

        d, _ = self.distAng(new_node, toN)
                # if randNode is within step size of node
        if d <= self.path_resolution:  
            new_node.path_x.append(toN.x)
            new_node.path_y.append(toN.y)
            new_node.x = toN.x
            new_node.y = toN.y

        new_node.parent = fromN
        return(new_node)
    
    @ staticmethod   
    # # backtrack from goal node to node unless node with no parent found
    def backTrack(node_new, node_new_prim):
        path1 = [(node_new.x, node_new.y)]
        path1_node = [node_new]
        node_now = node_new

        while node_now.parent is not None:
            node_now = node_now.parent
            path1.append((node_now.x, node_now.y))
            path1_node.append(node_now)

        path2 = [(node_new_prim.x, node_new_prim.y)]
        path2_node = [node_new_prim]
        node_now = node_new_prim

        while node_now.parent is not None:
            node_now = node_now.parent
            path2.append((node_now.x, node_now.y))
            path2_node.append(node_now)
        
        # print("Path 1:", len(path1)) 
        # print("-----------------------------------------")             
        # print("Path 2:", len(path2))  
        # print("-----------------------------------------")             
            

        return (list(list(reversed(path1)) + path2)), (list(list(reversed(path1_node)) + path2_node))
    
    
    
    # gives eucilidean distance to goal
    def dist2goal(self, x, y):
        distance = math.hypot(x - self.end.x, y - self.end.y)
        return(distance)
            
    # gives a random node from map 
    def getRandom(self):
        if random.randint(0, 100) > self.goal_sample_rate: # random integer
            xRand, yRand = random.uniform(0, 10), random.uniform(0, 10) # random float numbers between 0 and 10
            randNode = self.Node(xRand, yRand)    # build random node
        else:  # goal point sampling
            randNode = self.Node(self.end.x, self.end.y)
        return(randNode)

    @ staticmethod   
    def calcDist(fromN, toN):
        # print(fromN)
        # print(toN)
        distance = math.hypot(toN.x - fromN.x, toN.y - fromN.y)
        # angle = math.atan2(toN.y - fromN.y,toN.x - fromN.x)      
        return(distance)
     
    # gives distance and angle to next node, to build edge    
    @ staticmethod   
    def distAng(fromN, toN):
        # print(fromN)
        # print(toN)
        distance = math.hypot(toN.x - fromN.x, toN.y - fromN.y)
        angle = math.atan2(toN.y - fromN.y,toN.x - fromN.x)      
        return(distance, angle)
    
    @ staticmethod
    # get index of Nearest Node
    def getNodeIndex(nodeList, randNode):
        distanceList =  [(node.x - randNode.x)**2 + (node.y - randNode.y)**2
                         for node in nodeList]
        minIndex = distanceList.index(min(distanceList))
        # nearNode = self.minIndex[minIndex]
        # return(nearNode)
        return(minIndex)
    
    @ staticmethod
    def obstacleCheck(node):
        if node is None:
            return False
        
        x = node.x
        y = node.y
        
        if node.path_x:
            # Boundary condition
            if (x < 0) or (x > 10) or (y < 0) or (y > 10): 
                
                return False
            
            # Obstacle 1 (Circle Up)
            
            elif (x-2.5)**2 + (y-2.5)**2 - (1)**2 <= 0: 
                # print('Circle Up!')

                return False
            
              # Obstacle 4 (Circle Down)
            elif (x-2.5)**2 + (y-7.5)**2 - (1)**2 <= 0:
                # print('Circle Down!')
  
                return False
            
            elif (x-7.5)**2 + (y-2.5)**2 - (1)**2 <= 0:
                # print('Circle Down!')
  
                return False

            elif (x-7.5)**2 + (y-7.5)**2 - (1)**2 <= 0:
                # print('Circle Down!')
  
                return False

            elif (x-5)**2 + (y-5)**2 - (1)**2 <= 0:
                # print('Circle Down!')
  
                return False
            
            for (x, y) in zip(node.path_x, node.path_y):
                
                # Boundary condition
                if (x < 0) or (x > 10) or (y < 0) or (y > 10): 
                    return False
                
                elif (x-2.5)**2 + (y-2.5)**2 - (1)**2 <= 0: 
                # print('Circle Up!')

                    return False
            
              # Obstacle 4 (Circle Down)
                elif (x-2.5)**2 + (y-7.5)**2 - (1)**2 <= 0:
                    # print('Circle Down!')
    
                    return False
                
                elif (x-7.5)**2 + (y-2.5)**2 - (1)**2 <= 0:
                    # print('Circle Down!')
    
                    return False

                elif (x-7.5)**2 + (y-7.5)**2 - (1)**2 <= 0:
                    # print('Circle Down!')
    
                    return False

                elif (x-5)**2 + (y-5)**2 - (1)**2 <= 0:
                    # print('Circle Down!')
    
                    return False
                
                else:
                    # Node in Freespace
                    return True 
        
        return True    
         
    #@ staticmethod
    def changeNode(self, node1, node2):
        node = (node2.x, node2.y)
        newNode = self.Node(node[0],node[1])
        newNode.parent = node1
        return(newNode)
         
    @staticmethod
    def differentNode(node_new_prim, node_new):
        if node_new_prim.x == node_new.x and \
                node_new_prim.y == node_new.y:
            return True

        return False    
    
# =============================================================
#                         Main
# =============================================================

def main():
    rrt = RRTconnect(start = [1,1], goal = [9,9], rand_area=[0, 1000])
    rrt.algorithm(animation = True)
    

if __name__ == '__main__':
    main() 
    

    
