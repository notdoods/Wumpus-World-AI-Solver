# ======================================================================
# FILE:        MyAI.py
#
# AUTHOR:      Abdullah Younis
#
# DESCRIPTION: This file contains your agent class, which you will
#              implement. You are responsible for implementing the
#              'getAction' function and any helper methods you feel you
#              need.
#
# NOTES:       - If you are having trouble understanding how the shell
#                works, look at the other parts of the code, as well as
#                the documentation.
#
#              - You are only allowed to make changes to this portion of
#                the code. Any changes to other portions of the code will
#                be lost when the tournament runs your code.
# ======================================================================

from Agent import Agent

class MyAI ( Agent ):

    def __init__ ( self ):
        # ======================================================================
        # YOUR CODE BEGINS
        # ======================================================================
        self.goldLooted     =    False
        self.hasArrow       =    True
        self.screamed       =    False
        self.visited        =    set([(0,0)])
        self.unsafeStench   =    set()
        self.unsafeBreeze   =    set()
        self.unsafe         =    set()
        self.stenchSet      =    set()
        self.safeUnexplored =    set()
        self.safeSpots      =    set()
        self.posX           =    0
        self.posY           =    0
        self.direction      =    "Right"
        self.maxX           =    8
        self.maxY           =    8
        self.lastAction     =    "Start"
        self.nextMovement   =    (-1,-1)
        self.goalMovement   =    (-1,-1)
        self.count          =    0
        self.wumpus         =    (-1,-1)
        
        pass
        # ======================================================================
        # YOUR CODE ENDS
        # ======================================================================

    def getAction( self, stench, breeze, glitter, bump, scream ):
        # ======================================================================
        # YOUR CODE BEGINS
        # ======================================================================
        
        ###Update Positional Information based on last action
        currentP = (self.posX,self.posY)
        currentD = self.direction
        
        ##IMPORTANT## THIS ADDS THE LAST POSITION (If I move from (0,0) to (0,1), then it will add (0,0) as posX and posY have not changed yet
        if currentP not in self.visited and self.lastAction == "Forward" and not bump:
            self.visited.add(currentP)
        self.unsafe = self.unsafeBreeze | self.unsafeStench
        self.unsafe = self.unsafe.difference(self.visited)
        self.unsafe = self.unsafe.difference(self.safeSpots)
        
        #If Direction Change from last action happened, update direction info
        self.directionChange(currentD)
        currentD = self.direction
        
        #Reset goalMovement if it is at the goal
        goalCheck = self.goalMovement
        if goalCheck == (self.posX,self.posY) or goalCheck[0] > self.maxX or goalCheck[1] < self.maxY:
            self.goalMovement = (-1,-1)
        nextCheck = self.nextMovement
        if nextCheck == (self.posX,self.posY) or nextCheck[0] > self.maxX or nextCheck[1] < self.maxY:
            self.nextMovement = (-1,-1)
        
        if bump:
            self.bumpCheck()
        
        #If did not bump and moved forward, update position info
        if not bump and self.lastAction == "Forward" and self.posX < self.maxX+1 and self.posY < self.maxY+1:
            self.incrementPosition()
            currentP = (self.posX,self.posY)
            
        #Grab gold, update info
        elif self.lastAction == "Grab":
            self.goldLooted = True
        #Shoot arrow, update info
        elif self.lastAction == "Shoot":
            self.hasArrow = False
        
        if stench and (self.posX,self.posY) not in self.stenchSet:
            self.percepCheck("S")
            self.stenchSet.add((self.posX,self.posY))
        
        if stench and len(self.stenchSet) == 2 and self.wumpus == (-1,-1):
            self.findWumpus()
        
        if self.lastAction == "Shoot" and scream:
            self.screamed = True
            self.unsafeStench = set()
            self.unsafe = self.unsafeBreeze
            self.unsafe = self.unsafe.difference(self.visited)
        
        

        #Should be Number 1 Move when on gold spot
        self.count += 1
        if glitter:
            self.lastAction = "Grab"
            return Agent.Action.GRAB
        
        if self.count >= 65:
            self.goalMovement = (0,0)
            return self.safety()
        
        if self.count >= 65 and self.posX == 0 and self.posY == 0:
            return Agent.Action.CLIMB
    
        
        if self.unsafe == set([(2,0),(1,1),(0,2)]) and (self.visited == set([(0,0),(1,0),(0,1)]) or self.visited == set([(0,0),(1,0)])):
            self.goalMovement = (0,0)
            return self.safety()
        
        if self.posX == 0 and self.posY == 0 and breeze:
            return self.safety()
        
        ### Update information on current position and update information about the world
        #print("This is unsafeStench: " + str(self.unsafeStench))
        #print("This is stenchSet: " + str(self.stenchSet))
        #print("This is wumpus: " + str(self.wumpus))
        if stench and self.hasArrow and self.wumpus != (-1,-1) and len(self.stenchSet) >= 2:
            return self.smartShooting()
        
            
        
        if self.posX == 0 and self.posY == 0 and (stench and not self.screamed):
            return self.safety()
        
        #If current position is stench and is in the middle section and not at the top,
        # check the position to the left and up if information is known to see Up Movement is safe
        
        #Adds possible unsafe Breeze Areas to B list
            
        if (not breeze and not stench) or (not breeze and self.screamed):
            self.safeSpotFinder()
                
        if breeze:
            self.percepCheck("B")        
        ###Logical decisions
        #End Game
        if self.goldLooted and currentP == (0,0):
            return Agent.Action.CLIMB
        
        #If it is a safe space and have not collected gold yet, just move forward to only lose 1 points rather than turn and lose two w/ no knowledge yet.
        if not bump and (not stench or self.unsafeStench == set([])) and not breeze and not self.goldLooted and ((self.posX+1,self.posY) not in self.visited or (self.posX,self.posY+1) not in self.visited) and self.goalMovement == (-1,-1):
            if self.direction == "Right" or self.direction == "Up":
                self.lastAction = "Forward"
                return Agent.Action.FORWARD
        
        #If bumped into wall that is a safe position and has not been looted
        if bump and (not stench or self.unsafeStench == set([])) and not breeze and not self.goldLooted:
            if self.direction == "Right":
                self.lastAction = "TurnL"
                return Agent.Action.TURN_LEFT
            elif self.direction == "Up":
                self.lastAction = "TurnL"
                return Agent.Action.TURN_LEFT
            elif self.direction == "Left":
                self.lastAction = "TurnR"
                return Agent.Action.TURN_RIGHT
            elif self.direction == "Down":
                self.lastAction = "TurnR"
                return Agent.Action.TURN_RIGHT
            
            
        # If Gold is looted and not at start and is at the wall
        if self.goldLooted:
            self.goalMovement = (0,0)
            return self.safety()
            
            
        
        if self.isSurrounded() and not self.goldLooted:
            self.goalMovement == (0,0)
            return self.safety()
        elif not self.isSurrounded() and not self.goldLooted:
            if self.goalMovement == (-1,-1) or self.goalMovement == (self.posX,self.posY):
                self.findGoalMove(self.posX,self.posY)
            return self.findSafeMove()
        
        # ======================================================================
        # YOUR CODE ENDS
        # ======================================================================
    
    # ======================================================================
    # YOUR CODE BEGINS
    # ======================================================================
    
    #Helper Functions
    
    def findWumpus(self):
        allPossible = []
        possible = set()
        for x,y in self.stenchSet:
            allPossible.append((x+1,y))
            allPossible.append((x-1,y))
            allPossible.append((x,y+1))
            allPossible.append((x,y-1))
        
        for x in allPossible:
            if allPossible.count(x) >= 2:
                possible.add(x)
        p = possible.copy()
        for x in p:
            if x in self.visited:
                possible.remove(x)
                
        self.wumpus = possible.pop()
            
        
    
    def smartShooting(self):
        if (self.direction == "Right" and (self.posX<self.wumpus[0])) or (self.direction == "Down" and (self.wumpus[1]<self.posY)) or (self.direction == "Left" and (self.posX>self.wumpus[0])) or (self.direction == "Up" and (self.posY<self.wumpus[1])):
            self.lastAction = "Shoot"
            return Agent.Action.SHOOT
        ##to turn right
        elif (self.posX < self.wumpus[0] and self.direction == "Up") or (self.posX < self.wumpus[0] and self.direction == "Left") or (self.posX > self.wumpus[0] and self.direction == "Down") or (self.posX > self.wumpus[0] and self.direction == "Right") or (self.posY < self.wumpus[1] and self.direction == "Left") or (self.posY < self.wumpus[1] and self.direction == "Down") or (self.posY > self.wumpus[1] and self.direction == "Up") or (self.posY > self.wumpus[1] and self.direction == "Right"):
            self.lastAction = "TurnR"
            return Agent.Action.TURN_RIGHT
                                                                               
        elif (self.posX < self.wumpus[0] and self.direction == "Down") or (self.posX > self.wumpus[0] and self.direction == "Up") or (self.posY < self.wumpus[1] and self.direction == "Right")or (self.posY > self.wumpus[1] and self.direction == "Left"):
            self.lastAction = "TurnL"
            return Agent.Action.TURN_LEFT
            
        
        
    def safeSpotFinder(self):
        if self.posX-1 >= 0:
            self.safeSpots.add((self.posX-1,self.posY))
        if self.posX+1 <= self.maxX:
            self.safeSpots.add((self.posX+1,self.posY))
        if self.posY-1 >= 0:
            self.safeSpots.add((self.posX,self.posY-1))
        if self.posY+1 <= self.maxY:
            self.safeSpots.add((self.posX,self.posY+1))
        
        safeSpotsCopy = self.safeSpots.copy()
        for x,y in safeSpotsCopy:
            if (x,y) in self.visited:
                self.safeSpots.remove((x,y))
            if (x,y) == (self.posX,self.posY):
                self.safeSpots.remove((x,y))
        
    
    def incrementPosition(self):
        if self.direction == "Right":
            self.posX = self.posX + 1
        elif self.direction == "Left":
            self.posX = self.posX - 1
        elif self.direction == "Down":
            self.posY = self.posY - 1
        elif self.direction == "Up":
            self.posY = self.posY + 1
        
    def bumpCheck(self):
        if self.direction == "Right":
            self.maxX = self.posX
        elif self.direction == "Up":
            self.maxY = self.posY
        elif self.direction == "Down":
            self.posY = 0
        elif self.direction == "Left":
            self.posX = 0
        
    def directionChange(self,d):
        if self.lastAction == "TurnL":
            if d == "Right":
                self.direction = "Up"
            elif d == "Up":
                self.direction = "Left"
            elif d == "Left":
                self.direction = "Down"
            elif d == "Down":
                self.direction = "Right"
        elif self.lastAction == "TurnR":
            if d == "Right":
                self.direction = "Down"
            elif d == "Up":
                self.direction = "Right"
            elif d == "Left":
                self.direction = "Up"
            elif d == "Down":
                self.direction = "Left"
        
    
    def checkIfVisited(self,x,y,percep):
        #Adds possible location to list of unsafe areas based on stench or breeze
        if percep == "S":
            if (x,y) not in self.visited and (x,y) not in self.safeSpots:
                self.unsafeStench.add((x,y))
                self.unsafe.add((x,y))
        elif percep == "B":
            if (x,y) not in self.visited and (x,y) not in self.safeSpots:
                self.unsafeBreeze.add((x,y))
                self.unsafe.add((x,y))
            
    def percepCheck(self, x):
        #Checks if current spot(based on stench or breeze)
        if x == "S":
            if not self.screamed:
                if self.posX == 0 and self.posY == 0:
                    self.checkIfVisited(1,0,x)
                    self.checkIfVisited(0,1,x)
                elif self.posX == 0 and self.posY != 0:
                    self.checkIfVisited(1,self.posY,x)
                    self.checkIfVisited(0,self.posY-1,x)
                    if self.posY <= self.maxY:
                        self.checkIfVisited(0,self.posY+1,x)
                elif self.posX != 0 and self.posY == 0:
                    self.checkIfVisited(self.posX,1,x)
                    if self.posX+1 <= self.maxX:
                        self.checkIfVisited(self.posX+1,0,x)
                    self.checkIfVisited(self.posX-1,0,x)
                else:
                    if self.posY <= self.maxY:
                        self.checkIfVisited(self.posX,self.posY+1,x)
                    self.checkIfVisited(self.posX,self.posY-1,x)
                    if self.posX+1 <= self.maxX:
                        self.checkIfVisited(self.posX+1,self.posY,x)
                    self.checkIfVisited(self.posX-1,self.posY,x)
                
        elif x == "B":
            if self.posX == 0 and self.posY == 0:
                self.checkIfVisited(1,0,x)
                self.checkIfVisited(0,1,x)
            elif self.posX == 0 and self.posY != 0:
                self.checkIfVisited(1,self.posY,x)
                self.checkIfVisited(0,self.posY-1,x)
                self.checkIfVisited(0,self.posY+1,x)
            elif self.posX != 0 and self.posY == 0:
                self.checkIfVisited(self.posX, 1,x)
                self.checkIfVisited(self.posX+1,0,x)
                self.checkIfVisited(self.posX-1,0,x)
            else:
                self.checkIfVisited(self.posX,self.posY+1,x)
                self.checkIfVisited(self.posX,self.posY-1,x)
                self.checkIfVisited(self.posX+1,self.posY,x)
                self.checkIfVisited(self.posX-1,self.posY,x)
    
  
    def isSurrounded(self):
        check = set([(0,0)])
        for x,y in self.visited:
            if (x+1,y) not in check and x+1 <= self.maxX:
                check.add((x+1,y))
            if (x-1,y) not in check and x-1 >= 0:
                check.add((x-1,y))
            if (x,y+1) not in check and y+1 <= self.maxY:
                check.add((x,y+1))
            if (x,y-1) not in check and y-1 >= 0:
                check.add((x,y-1))
        checkCopy = set([])
        checkCopy = check.copy()
        for x,y in checkCopy:
            if (x,y) in self.unsafe:
                check.remove((x,y))
        checkCopy = check.copy()
        if checkCopy != self.visited:
            for x,y in self.visited:
                if (x,y) in checkCopy:
                    checkCopy.remove((x,y))

        if (self.posX,self.posY) in checkCopy:
            checkCopy.remove((self.posX,self.posY))
        if (self.posX,self.posY) in self.safeSpots:
            self.safeSpots.remove((self.posX,self.posY))
        fullUnexplored = checkCopy | self.safeSpots
        fuCopy = fullUnexplored.copy()
        for x,y in fuCopy:
            if x > self.maxX or y > self.maxY:
                fullUnexplored.remove((x,y))
        self.safeUnexplored = fullUnexplored
        return check == self.visited    
    
    def findSafeMove(self):
    #Finds the closest positional step to the goal move
        currentP = (self.posX, self.posY)
        goal = self.goalMovement
        direction = self.direction
        nextM = self.nextMovement
        possible = []
        foundGoal = False
        #Make a list of possible possible next moves once next movement starts or needs to be refreshed
        if nextM == currentP or nextM == (-1,-1):
            possible.append((currentP[0]+1,currentP[1]))
            if currentP[0]-1 >= 0:
                possible.append((currentP[0]-1,currentP[1]))
            possible.append((currentP[0],currentP[1]+1))
            if currentP[1]-1 >= 0:
                possible.append((currentP[0],currentP[1]-1))
            possibleCopy = possible
            for x in possibleCopy:
                if x not in self.visited and x != goal:
                    possible.remove(x)
            for x,y in possible:
                if (x,y) == goal:
                    self.nextMovement = (x,y)
                    foundGoal = True
                    break
            if not foundGoal:
                for x,y in possible:
                    distanceCY = abs(goal[1] - currentP[1])
                    distanceCX = abs(goal[0] - currentP[0])
                    distancePY = abs(goal[1] - y)
                    distancePX = abs(goal[0] - x)
                    if distancePY == (distanceCY - 1) or distancePX == (distanceCX - 1) and (x,y) in self.visited:
                        self.nextMovement = (x,y)
                        break
                    if (x,y) == goal:
                        self.nextMovement = (x,y)
                        break

        nextM = self.nextMovement
        if nextM[1] < currentP[1]:
            if direction == "Left":
                self.lastAction = "TurnL"
                return Agent.Action.TURN_LEFT
            elif direction == "Right" or direction == "Up":
                self.lastAction = "TurnR"
                return Agent.Action.TURN_RIGHT
            elif direction == "Down":
                self.lastAction = "Forward"
                return Agent.Action.FORWARD
        elif nextM[1] > currentP[1]:
            if direction == "Left":
                self.lastAction = "TurnR"
                return Agent.Action.TURN_RIGHT
            elif direction == "Right" or direction == "Down":
                self.lastAction = "TurnL"
                return Agent.Action.TURN_LEFT
            elif direction == "Up":
                self.lastAction = "Forward"
                return Agent.Action.FORWARD
        elif nextM[1] == currentP[1]:
            if nextM[0] < currentP[0]:
                if direction == "Up":
                    self.lastAction = "TurnL"
                    return Agent.Action.TURN_LEFT
                elif direction == "Right" or direction == "Down":
                    self.lastAction = "TurnR"
                    return Agent.Action.TURN_RIGHT
                elif direction == "Left":
                    #########print("I should have gone")
                    self.lastAction = "Forward"
                    return Agent.Action.FORWARD
            elif nextM[0] > currentP[0]:
                if direction == "Up":
                    self.lastAction = "TurnR"
                    return Agent.Action.TURN_RIGHT
                elif direction == "Left" or direction == "Down":
                    self.lastAction = "TurnL"
                    return Agent.Action.TURN_LEFT
                elif direction == "Right":
                    self.lastAction = "Forward"
                    return Agent.Action.FORWARD
            else:
                if direction == "Left":
                    self.lastAction = "TurnL"
                    return Agent.Action.TURN_LEFT
                elif direction == "Right" or direction == "Up":
                    self.lastAction = "TurnR"
                    return Agent.Action.TURN_RIGHT
                elif direction == "Down":
                    self.lastAction = "Forward"
                    return Agent.Action.FORWARD
    
    
    def findGoalMove(self,x, y):
    #Using safeUnexplored after isSurrounded is false, find the closest in safeUnexplored to travel to.
        d = {"Left": 0, "Down": 1, "Right": 2, "Up": 3}
        unexplored = self.safeUnexplored.copy()
        lowest = -1
        lowestP = (-1,-1)
        for a,b in unexplored:
            cost = 0
            direction = self.direction
            if b < y:
                cost += abs(d[direction] - d["Down"])
                direction = "Down"
            elif b > y:
                cost += abs(d[direction] - d["Up"])
                direction = "Up"
            if a < x:
                cost +=abs(d[direction] - d["Left"])
            elif a > x:
                cost += abs(d[direction] - d["Right"])
            downMovements = 0
            downMovements = abs(b - y)
            for i in range(downMovements):
                if b < y:
                    if (x,y-i-1) in self.unsafe:
                        cost = 100
                    else:
                        cost += abs(b - y)
                elif b > y:
                    if (x,y+i+1) in self.unsafe:
                        cost = 100
                    else:
                        cost += abs(b - y)
            horizontalM = 0
            horizontalM = abs(a - x)
            for i in range(horizontalM):
                if a < x:
                    if (x-i-1,b) in self.unsafe:
                        cost = 100
                    else:
                        cost += abs(a - x)
                elif a > x:
                    if (x+i+1,b) in self.unsafe:
                        cost = 100
                    else:
                        cost += abs(a - x)
            if lowest == -1 or cost < lowest:
                lowest = cost
                lowestP = (a,b)
        self.goalMovement = lowestP
        
    def safety(self):
        if self.posY == 0 and self.posX == 0:
            return Agent.Action.CLIMB
        currentP = (self.posX, self.posY)
        goal = (0,0)
        self.goalMovement = goal
        direction = self.direction
        nextM = self.nextMovement
        possible = []
        #Make a list of possible possible next moves once next movement starts or needs to be refreshed
        if nextM == currentP or nextM == (-1,-1):
            possible.append((currentP[0]+1,currentP[1]))
            if currentP[0]-1 >= 0:
                possible.append((currentP[0]-1,currentP[1]))
            possible.append((currentP[0],currentP[1]+1))
            if currentP[1]-1 >= 0:
                possible.append((currentP[0],currentP[1]-1))
            possibleCopy = possible
            for x in possibleCopy:
                if (x not in self.visited and x != goal):
                    possible.remove(x)
            possibleCopy = possible
            for x in possibleCopy:
                if (x not in self.visited and x in self.unsafe):
                    possible.remove(x)
            possibleCopy = possible
            for x,y in possibleCopy:
                if x == -1 or y == -1:
                    possible.remove((x,y))
            #print("This is final possible: " + str(possible))
            for x,y in possible:
                if (x,y) == (0,0):
                    self.nextMovement = (x,y)
                    break
                distanceCY = abs(goal[1] - currentP[1])
                distanceCX = abs(goal[0] - currentP[0])
                distancePY = abs(goal[1] - y)
                distancePX = abs(goal[0] - x)
                if distancePY == (distanceCY - 1) or distancePX == (distanceCX - 1):
                    self.nextMovement = (x,y)
                    break
        
        
        ####print("This is visited: " + str(self.visited))
            
        nextM = self.nextMovement
        #print("This is NextM: " + str(nextM))
        ####print("This is Goal: " + str(goal))
        if nextM[1] < currentP[1]:
            if direction == "Left":
                self.lastAction = "TurnL"
                return Agent.Action.TURN_LEFT
            elif direction == "Right" or direction == "Up":
                self.lastAction = "TurnR"
                return Agent.Action.TURN_RIGHT
            elif direction == "Down":
                self.lastAction = "Forward"
                return Agent.Action.FORWARD
        elif nextM[1] > currentP[1]:
            if direction == "Left":
                self.lastAction = "TurnR"
                return Agent.Action.TURN_RIGHT
            elif direction == "Right" or direction == "Down":
                self.lastAction = "TurnL"
                return Agent.Action.TURN_LEFT
            elif direction == "Up":
                self.lastAction = "Forward"
                return Agent.Action.FORWARD
        elif nextM[1] == currentP[1]:
            if nextM[0] < currentP[0]:
                if direction == "Up":
                    self.lastAction = "TurnL"
                    return Agent.Action.TURN_LEFT
                elif direction == "Right" or direction == "Down":
                    self.lastAction = "TurnR"
                    return Agent.Action.TURN_RIGHT
                elif direction == "Left":
                    self.lastAction = "Forward"
                    return Agent.Action.FORWARD
            elif nextM[0] > currentP[0]:
                if direction == "Up":
                    self.lastAction = "TurnR"
                    return Agent.Action.TURN_RIGHT
                elif direction == "Left" or direction == "Down":
                    self.lastAction = "TurnL"
                    return Agent.Action.TURN_LEFT
                elif direction == "Right":
                    self.lastAction = "Forward"
                    return Agent.Action.FORWARD
            else:
                if direction == "Left":
                    self.lastAction = "TurnL"
                    return Agent.Action.TURN_LEFT
                elif direction == "Right" or direction == "Up":
                    self.lastAction = "TurnR"
                    return Agent.Action.TURN_RIGHT
                elif direction == "Down":
                    self.lastAction = "Forward"
                    return Agent.Action.FORWARD
            
    
    # ======================================================================
    # YOUR CODE ENDS
    # ======================================================================