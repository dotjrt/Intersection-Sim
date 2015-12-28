from random import randint
import time
import math

class Vehicle:       
    def __init__(self, idno, value):
        self.directions = ["N","S","E","W"]
        self.idno = idno
        self.travelDirection = self.directions[randint(0,3)]
        self.speed = 20     # meters/sec
        self.distanceFromIntersection = 100     # meters
        self.isActive = True
        self.canPass = True
        self.value = value
        self.bidAmount = value
        self.timeThroughIntersection = 0
        self.madeItThrough = False

    def changeBid(self, newBidAmount):
        self.bidAmount = newBidAmount
        
    def adjustSpeed(self, value):
        self.speed += value
        
    def adjustDistanceFromIntersection(self, timePassed):
        self.distanceFromIntersection -= (self.speed * timePassed)
        if self.distanceFromIntersection < -100:
            self.isActive = False

    def checkIfThroughIntersection(self, currentTime):
        if self.distanceFromIntersection <= 0 and self.madeItThrough == False:
            self.timeThroughIntersection = currentTime - self.idno
            self.madeItThrough = True
        
    def printVehicleData(self):
        print "Vehicle " + str(self.idno) + " -"
        print "Bid: " + str(self.bidAmount)
        print "Travel direction: " + str(self.travelDirection)
        print "Speed: " + str(self.speed)
        print "Distance from intersection: " + str(self.distanceFromIntersection)
        print "Active? " + str(self.isActive)
        print "-----------------------"

class Auctioneer: 

    def handleBids(self, activeVehicles):
        return sorted(activeVehicles, key=lambda v: v.bidAmount, reverse=True)

    def directTraffic(self, auctionResultList):
        index = 0
        for vehicle in auctionResultList:
            #speed up vehicles based on auction standing
            incrementor = (len(auctionResultList) - index - 1) * 0.1 
            vehicle.adjustSpeed(incrementor)
            index += 1
        self.avoidIntersectionCollisions(auctionResultList)
        self.handlePassing(auctionResultList)

    #avoid collisions when two cars are approaching intersection at same time in different directions
    def avoidIntersectionCollisions(self, activeVehicles):
        for v1 in activeVehicles:
            for v2 in activeVehicles:
                if v1 != v2:
                    if math.fabs(v1.distanceFromIntersection - v2.distanceFromIntersection) < 10:
                        if v1.distanceFromIntersection < 20 and v1.distanceFromIntersection > 0:
                            if oncomingDirections(v1.travelDirection, v2.travelDirection):
                                if v1.speed == v2.speed:
                                    print "Collision avoided!"
                                    v1.printVehicleData()
                                    v2.printVehicleData()
                                    v1.adjustSpeed(10)

    # let vehicles traveling faster pass (assuming a second passing lane) 
    def handlePassing(self, activeVehicles):
        for vehicle1 in activeVehicles:
            for vehicle2 in activeVehicles:
                if vehicle1 != vehicle2:
                    if vehicle1.travelDirection == vehicle2.travelDirection:
                        if math.fabs(vehicle1.distanceFromIntersection - vehicle2.distanceFromIntersection) < 10:
                            if vehicle1.speed > vehicle2.speed and vehicle1.canPass == True:
                                vehicle1.canPass = False
                            elif vehicle1.speed < vehicle2.speed and vehicle2.canPass == True:
                                vehicle2.canPass = False
                            elif vehicle1.speed > vehicle2.speed and vehicle1.canPass == False and vehicle2.canPass == False:
                                #slow down vehicle1 to match speed of vehicle2
                                speedDifference = vehicle2.speed - vehicle1.speed
                                vehicle1.adjustSpeed(speedDifference)
                            elif vehicle1.speed < vehicle2.speed and vehicle2.canPass == False and vehicle1.canPass == False:
                                #slow down vehicle2 to match speed of vehicle1
                                speedDifference = vehicle1.speed - vehicle2.speed
                                vehicle2.adjustSpeed(speedDifference)
                                
def oncomingDirections(d1, d2):
    if d1 == "N" and d2 == "E":
        return True
    elif d1 == "N" and d2 == "W":
        return True
    elif d1 == "S" and d2 == "E":
        return True
    elif d1 == "S" and d2 == "W":
        return True
    elif d1 == "W" and d2 == "N":
        return True
    elif d1 == "W" and d2 == "S":
        return True
    elif d1 == "E" and d2 == "N":
        return True
    elif d1 == "E" and d2 == "S":
        return True
    else:
        return False
                     
def printIntersectionData(time, allVehicles):
    print "Time: " + str(time)
    for vehicle in allVehicles:
        vehicle.printVehicleData()
    print "~~~~~~~~~~~~~~~~~~~~~~~"

def strategicBid(value, allVehicles):
    bid = value * ((float)(len(allVehicles) - 1) / (float)(len(allVehicles)))
    return bid

def runCollisionCheck(allVehicles):
    # check for collision of vehicles travelling in the same direction
    for vehicle1 in allVehicles:
        for vehicle2 in allVehicles:
            if vehicle1 != vehicle2:
                if math.fabs(vehicle1.distanceFromIntersection - vehicle2.distanceFromIntersection) < 3:
                    if vehicle1.distanceFromIntersection > 0:
                        if vehicle1.travelDirection == vehicle2.travelDirection:
                            if vehicle1.canPass == vehicle2.canPass:
                                print "Collision: V1 ID:" + str(vehicle1.idno) + "-" + str(vehicle1.distanceFromIntersection),
                                print " V2 ID:" + str(vehicle2.idno) + "-" + str(vehicle2.distanceFromIntersection)     
    
def main():
    RUNTIME = 100
    TIMEINCREMENT = 1

    winningBids = []
    allBids = []
    playerWins = 0
    auctionsRun = 0
    percentiles = []
    
    t0 = time.time()
    #initialize a single vehicle with idno 0
    allVehicles = []
    allVehicles.append(Vehicle(0, 75))
    a = Auctioneer()

    print "Running sim..."
    # main simulation loop
    t = 0
    #printIntersectionData(t, allVehicles)
    while t < RUNTIME:
        t += TIMEINCREMENT
        for vehicle in allVehicles:
            vehicle.adjustDistanceFromIntersection(TIMEINCREMENT)
            vehicle.checkIfThroughIntersection(t)
              
        allVehicles.append(Vehicle(t, randint(1,100)))
        allVehicles[0].changeBid(strategicBid(75.0, allVehicles))
        for vehicle in allVehicles:
            if vehicle.idno != 0:
                vehicle.changeBid(strategicBid(vehicle.value, allVehicles))
                    
        bidList = a.handleBids(allVehicles)

        winningBids.append(bidList[0].bidAmount)
        a.directTraffic(bidList)
                
        runCollisionCheck(allVehicles)
    
    tf = time.time()
    print "Sim complete. Run time: " + str(tf - t0) + " sec"

    allTimes = []
    for v in allVehicles:
        if v.timeThroughIntersection != 0:
            allTimes.append(v.timeThroughIntersection)

    avgTimeThru = (float)(sum(allTimes)) / len(allTimes)   
    print "# of cars that passed thru intersection (out of " + str(len(allVehicles)) + " vehicles spawned): " + str(len(allTimes))
    print "Average time to get through intersection: " + str(avgTimeThru) + " sec"

        
if __name__ == '__main__':
    main()
