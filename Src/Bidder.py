import Behaviour
import random
# Matplotlib imported for testing only
import matplotlib.pyplot as plt 

###### amount should maybe be an amount taken from behaviour ######
class Bidder:
  def __init__(self, id, amount, needs, marketPrice, behaviour):
    self.id = id
    self.initAmount = amount
    self.currentAmount = self.initAmount
    self.needs = needs
    # Bidders will somewhat know the market price based on normal distribution (mean, standardDeviation)
    self.marketPrice = marketPrice*random.normalvariate(1, 0.03)
    #print("<init Class Bidder> Bidder ",self.id, " knows the market price: ", self.marketPrice)
    self.behaviour = behaviour
    self.marketPriceFactor = behaviour["marketPriceFactor"]
    # Stops the bidders from bidding over a certain value based on market price and aggressiveness (code is also added in Behaviour.py)
    self.stopBid = self.marketPrice*(1 + self.behaviour["aggressiveness"])

    # Bidders know this info about auctions
    self.auctionsLost = 0 # not used
    self.auctionBids = 0 # not used
    self.auctionList = []
    self.currentAuctions = len(self.auctionList) # not used
    self.winningAuctions = 0
    self.rounds = 0 # not used

  
  # New bid function (Work In Progress)
  # Returns a list of all the auctions that the bidder can bid on
  # Note: it doesn't set the current amount to a new value currently.
  ############# self.behaviour["bidOverMarketPrice"] and a value of a range, can turn on/off if market price matters in the simulation or not ##############
  def bid(self, input):
    # Update the aggressiveness of the behaviour (doesn't get new values for auctionsLost or auctionBids currently)
    self.behaviour["aggressiveness"] = self.behaviour["adaptiveAggressiveness"](len(input), self.auctionsLost, self.auctionBids)
    # Variables to keep track on the best bid for a certain auction
    tempBid = 0
    tempAuction = {}
    allBidsList = []

    for auction in input:
      # If a bidder only wants to bid max, it will do it in the first auction
      if self.behaviour["bid"](auction["top_bid"], self.marketPrice, self.currentAmount) and self.behaviour["onlyBidMaxAmount"]:
        allBidsList.append((self.currentAmount, auction))
        return allBidsList
      else:
        genBid = int(min(auction["top_bid"] * (1 + self.behaviour["aggressiveness"] * self.marketPriceFactor), self.currentAmount))
        
        # Print for testing purposes:
        #print("<from bid()> genBid: ", genBid, "  |  tempBid: ", tempBid, "  |  stopBid: ",self.behaviour["stopBid"](self.marketPrice), "  |  auction: ", auction["id"])
        
        # Checks if the bidder can bid and if it wants to bid if the market price is over the generated bid.
        if(self.behaviour["bid"](auction["top_bid"], self.marketPrice, self.currentAmount)
           and
           ((self.marketPrice > genBid and not self.behaviour["bidOverMarketPrice"]) or (self.behaviour["stopBid"](self.marketPrice) > genBid and self.behaviour["bidOverMarketPrice"]))
           or
           self.behaviour["bidOverMarketPrice"]
        ):
          tempBid = genBid
          tempAuction = auction
          allBidsList.append((tempBid, tempAuction))
        else:
          continue
    if(tempBid == 0 or (tempAuction["id"] == 0 and tempAuction["top_bid"] == 0 and tempAuction["quantity"] == 0)):
      return []
    else:
      return allBidsList

  def setCurrentAmount(self, amount):
    self.currentAmount = amount

  def setWinningAuctions(self, winningAuctions):
    self.winningAuctions = winningAuctions

  def setAuctionsLost(self, auctionsLost):
    self.auctionsLost = auctionsLost

  def setAuctionBids(self, auctionBids):
    self.auctionBids = auctionBids

  def addAuction(self, auction):
    self.auctionList.append(auction)
    self.currentAuctions = len(self.auctionList)

  def removeAuction(self, auctionId):
    for auction in self.auctionList:
      if(auction.auctionId == auctionId):
        self.auctionList.remove(auction)
        self.currentAuctions = len(self.auctionList)
  
  def updateMarketFactor(self, mean, standardDeviation):
    self.marketPriceFactor = self.behaviour["marketPriceFactorUpdate"](mean, standardDeviation)

  # Returns a list of dictionaries with info about how the bidder bids
  # Note: currently it can bid on many auctions even if it just needs a small amount to fulfill the needs
  ###### function, wins auction, need to know the Needs          ###### --Maybe works now?--
  ###### should be able to reset current items, winning auctions ###### --Maybe works now?--
  def bidUpdate(self, input):
    self.winningAuctions = 0
    satisfiedNeed = 0
    currentItems = 0

    for dictionary in input:
      if(dictionary["user"] == self.id):
          self.winningAuctions =+ 1
          satisfiedNeed = satisfiedNeed + dictionary["quantity"]

    currentItems = self.needs.amount - satisfiedNeed
    bidList = self.bid(input)
    #print("Bidder",self.id ," current winner in auction", bidList[0][1]["id"],"is ", bidList[0][1]["user"])
    #print("bidList: ", bidList)
    returnList = []

    # bid[0] = bid <int>, bid[1] = auction <dictionary>
    for bid in bidList:
      if(bid[1]["user"] == self.id):
        continue
      elif(0 < currentItems):
        returnList.append({'id' : bid[1]["id"], 'user' : self.id, 'top_bid' : bid[0]})

    return returnList 

class Needs:
  def __init__(self, amount, type):
    self.amount = amount
    self.type = type

# Testing method for testing different behaviours
def test():
  bidder1 = Bidder(1, 150000, Needs(55, "steel beam"), 15000, Behaviour.A)
  bidder2 = Bidder(2, 150000, Needs(55, "steel beam"), 15000, Behaviour.B)
  bidder3 = Bidder(3, 150000, Needs(55, "steel beam"), 15000, Behaviour.C)
  bidder4 = Bidder(4, 150000, Needs(55, "steel beam"), 15000, Behaviour.C)

  print("Created 3 bidders with behaviour type A, B and C respectively and an extra bidder with type C.")
  print("-----------------------------------------------------------------")

  print("Testing the bidUpdate() function:")
  simList = [{'id' : 1, 'quantity' : 60, 'user':None , 'top_bid' : 16000},
             {'id' : 2, 'quantity' : 55, 'user':None , 'top_bid' : 13000},
             {'id' : 3, 'quantity' : 40, 'user':None , 'top_bid' : 11000},
             {'id' : 4, 'quantity' : 50, 'user':None , 'top_bid' : 12000}]

  bidder1.updateMarketFactor(4, 2.15)
  bidder3.updateMarketFactor(4, 2.15)
  bidder4.updateMarketFactor(4, 2.15)           

  bidder1Info = bidder1.bidUpdate(simList)
  bidder3Info = bidder3.bidUpdate(simList)
  bidder4Info = bidder4.bidUpdate(simList)

  print("Bidder 1 decisions: ", bidder1Info)
  #print("Bidder 1 needs: ", bidder1.needs.amount)
  #print("Bidder 1 stopBid: ", bidder1.behaviour["stopBid"](bidder1.marketPrice))
  print("Bidder 3 decisions: ", bidder3Info)
  #print("Bidder 3 needs: ", bidder3.needs.amount)
  #print("Bidder 3 stopBid: ", bidder3.behaviour["stopBid"](bidder3.marketPrice))
  print("Bidder 4 decisions: ", bidder4Info)
  #print("Bidder 4 needs: ", bidder4.needs.amount)
  #print("Bidder 4 stopBid: ", bidder4.behaviour["stopBid"](bidder4.marketPrice))


def testNormalDistributionGraph():
  print("Normal distribution test (graph):")
  value = 0
  valueList = []
  for i in range(2000):
    value = random.normalvariate(1, 0.15)
    valueList.append(value)
  plt.hist(valueList, bins=200) 
  plt.show()


#test()
#testNormalDistributionGraph()

