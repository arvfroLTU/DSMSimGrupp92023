from SimEngine import *
import Sellers
from Bidders import *
import random
import math
import yaml
import mongodb
from Database import API_Handling
import refCalc
import GUI

seed = None


# File names for configs hardcoded, could be set with a user input function
# The generation of bidders and sellers is made simple by keeping the same format as the .yaml files for them throughout and at the end initalizing the objects from that config


configFile = "config.yaml"
sellerFile = "sellers.yaml"
bidderFile = "bidders.yaml"


# Default limits how many blocks each seller can have randomized

MAX_BLOCK = 0           # = refers to index not amount
MIN_BLOCK = 0           


def readConfig(skipPrompts):
    "Reads any configs which are present, and generates configs if they do not exist or if user wished to generate them" # Prepares all variables for Start():
   
    generatedConfig = 0
   
    #Checks if a new config file needs to be generated
    try:
        with open(configFile, "r") as f:
            conf = yaml.load(f, Loader=yaml.FullLoader)
    except:
        print("Could not find a config file, generating")
        conf = genConfig()
        generatedConfig = 1
    #Loads Sellers from config file, and sets amount of sellers in the same file,  if such a  file exists  
    try:
        with open(sellerFile, "r") as f:
            if not skipPrompts: raise
            sellers = yaml.load(f, Loader=yaml.FullLoader)
        conf["sellers"] = len(sellers)
    except:
        sellers = None

    #Loads Bidders from config file, and sets amount of Bidders in the same file, if such a  file exists
    try:
        with open(bidderFile, "r") as f:
            if not skipPrompts: raise
            bidders = yaml.load(f, Loader=yaml.FullLoader)
        conf["bidders"] = len(bidders)
    except:
        bidders = None
   
    if not generatedConfig:
        verifyConfig(conf)
   
    # Checks to ensure that there is a max and min block, constants defined at the top
       
    if conf["min-block"] == None:
        conf["min-block"] = MIN_BLOCK


    if conf["max-block"] == None:
        conf["max-block"] = MAX_BLOCK
   
   
    # Determines supply and demand, based on Whether bidders and Sellers are present or not
   
    supply, demand = getResourceUsage(sellers, bidders)
   
    if bidders and sellers:                                      
        conf["resource-usage"] = demand / supply
    elif not bidders and not sellers:
        demand = random.randrange(500, 5000)
        supply = round(demand / conf["resource-usage"])
        bidders = genBidders(conf["bidders"], demand, conf["distance-limit"], conf["distance-penalty"]) # Removed Radius
        sellers = genSellers(conf["sellers"], supply, conf) # Removed Radius
    elif bidders and not sellers:
        supply = round(demand / conf["resource-usage"])
        sellers = genSellers(conf["sellers"], supply)  #Removed Radius conf["radius"])
    else:
        demand = round(conf["resource-usage"] * supply)
        bidders = genBidders(conf["bidders"], demand, conf["distance-limit"], conf["distance-penalty"]) # Removed Radius
   
    # Set distance limit and penalty if it exists
    if conf["distance-limit"] != None:
        overrideLimit(bidders, conf["distance-limit"])
    if conf["distance-penalty"] != None:
        overridePenalty(bidders, conf["distance-penalty"])


    # Init both bidders and sellers
    amountOfAuctions, sellerList = initSellers(sellers)
    bidderList = initBidders(bidders, math.ceil(amountOfAuctions / conf["slotsize"]))
    return conf['slotsize'], conf['end-threshold'], sellerList, bidderList

def genConfig():
    """Generates a config.yaml file and saves it, called if config file is missing"""
    conf = {}
    conf["seed"] = random.randrange(0, 10000)
    random.seed(conf["seed"])
    conf["sellers"] = random.randrange(5, 15)
    conf["bidders"] = random.randrange(2, 7)
    conf["resource-usage"] = round(random.uniform(0.25, 0.9), 4)
    conf["distance-limit"] = random.randrange(1,10)
    conf["distance-penalty"] = round(random.uniform(5,10),2)
    conf["slotsize"] = 2
    conf["end-threshold"] = 2
    conf["min-block"] = 1
    conf["max-block"] = 1
    conf["fairnessPercent"] = 0.5
    conf["ecoPercent"] = 0.5
    with open("config.yaml", "w") as f:
        yaml.dump(conf, f, sort_keys=False)


def verifyConfig(conf):
    'adds possibly missing variables to existing config file'
   
    if not conf["seed"]:
        conf["seed"] = random.randrange(0, 10000)
    random.seed(conf["seed"])
    if not conf["sellers"]:
        conf["sellers"] = random.randrange(5, 15)
    if not conf["bidders"]:
        conf["bidders"] = random.randrange(2, 7)
    if not conf["resource-usage"]:
        conf["resource-usage"] = round(random.uniform(0.25, 0.9), 4)
    if not conf["distance-limit"]:
        conf["distance-limit"] = round(random.uniform(conf["radius"]*1.5, conf["radius"]*3),2)
    if not conf["distance-penalty"]:    
        conf["distance-penalty"] = round(random.uniform(5,10),2)
    if not conf["slotsize"]:
        conf["slotsize"] = 2
    if not conf["end-threshold"]:
        conf["end-threshold"] = 2
    if not conf["min-block"]:
        conf["min-block"] = 1
    if not conf["max-block"]:
        conf["max-block"] = 1
    if not conf["fairnessPercent"]:
        conf["fairnessPercent"] = 0.5
    if not conf["ecoPercent"]:
        conf["ecoPercent="] = 0.5

# Generation of sellers, the total supply is divided up into parts (randomly distributed size)
# Furthermore each seller can have chain their blocks together, randomly generated in range 'min-block' 'max-block' from config


def genSellers(number, supply, conf):
    'generates Sellers in case Config file isnt present'
   
    sellers = {}
    dividers = sorted(random.sample(range(1, supply), number-1))
    supplies = [a - b for a, b in zip(dividers + [supply], [0] + dividers)]
    for i in range(number):
        toDistribute = supplies.pop()
        chainLen = random.randint(conf['min-block'], conf['max-block'])
        div = sorted(random.sample(range(1, toDistribute), chainLen))
        values = [a - b for a, b in zip(div + [toDistribute], [0] + div)]
        blocks = {}
        for j in range(len(values)):
            discount = 0
            if j != 0:
                discount = round(random.uniform(0.1, 0.50), 2)
            blocks["block" + str(j)] = [
                {"quantity": values.pop()},
                {"price": random.randrange(500, 5000)},
                {"discount": discount},
            ]
        sellers["Seller" + str(i)] = {
            "location": genLocation(),
            "blocks": blocks,
        }
    return sellers




def genBidders(number, demand, limit, penalty): #City and country variables, if specLocation is needed
    'generates Bidders in case Config file isnt present '
   
    bidders = {}
    dividers = sorted(random.sample(range(1, demand), number))
    demands = [a - b for a, b in zip(dividers + [demand], [0] + dividers)]
    for i in range(number):
        bidders["Bidder" + str(i)] = {
            "location": genLocation(),
            "need": demands.pop(),
            "behavior": Behaviour.randomBehaviour(),
            "distanceLimit": limit,
            "distancePenalty":penalty
        }
    return bidders




# Compute the resource usage by iterating over sellers and bidders supply/demand
def getResourceUsage(sellers, bidders):
    supply = 0
    if sellers:
        for SellerId in sellers:
            for block in sellers[SellerId]["blocks"].items():
                supply += block[1][0]["quantity"]
    demand = 0
    if bidders:
        for bidderId in bidders:
            demand += bidders[bidderId]["need"]
    return supply, demand




def initSellers(sellers):
    'Takes sellers and puts their blocks for sale up for auction within the simulation'
   
    sellerList = []
    amountOfAuctions = 0
   
    for SellerId in sellers:
       
        #Identifies a Seller and initializes a local seller variable that can later be added on to
       
        activeSeller = Sellers.Sellers(SellerId, sellers[SellerId]["location"])          # latches active Sellers location to a local seller variable
        firstBlock = sellers[SellerId]["blocks"].pop("block1")                           # Removes first block of active Seller as to not count it twice, and puts it in local variable
        activeSeller.quantity.append(firstBlock[0]['quantity'])    #Why?                 # add quantity to local seller variable
        activeSeller.genBlock(
            firstBlock[1]["price"], firstBlock[0]["quantity"], firstBlock[2]["discount"] #generates a block in local Seller variable from scrubbed data
        )
        amountOfAuctions += 1                                                            # counts removed first block possible auction
       
        #Adds rest of Sellers blocks to  local Seller variable
       
        for block in sellers[SellerId]["blocks"].items():  
            activeSeller.quantity.append(block[1][0]['quantity'])                        #discretely identifies quantity for current block
            activeSeller.addBlock(
                block[1][1]["price"], block[1][0]["quantity"], block[1][2]["discount"]   #stores entire block locally
            )
            amountOfAuctions += 1                                                          # counts current block as possible Auction
           
        #Sets up return result
        sellerList.append(activeSeller)        
    return amountOfAuctions, sellerList


def initBidders(bidders, maxRounds):
    'moves Bidder data  to a local array for use in the auctioning system'
    bidderList = []
    for bidder in bidders.items():
        data = bidder[1]            
        entity = Bidders(
            bidder[0],              
            data["location"],
            data["need"],
            maxRounds,                                      
            Behaviour.genBehaviour(data["behavior"]),
            data["distanceLimit"],
            data["distancePenalty"]
        )
        bidderList.append(entity)       # commits bidder to local variable for use in the auctioning system
    return bidderList


def genLocation():
    return refCalc.randLocation()

def overrideLimit(bidders, limit):
    for bidder in bidders.items():
        bidder[1]['distanceLimit'] = limit


def overridePenalty(bidders, penalty):
    for bidder in bidders.items():
        bidder[1]['distancePenalty'] = penalty


def outputHandler(matchmakingResults):
    
    fairness = matchmakingResults[0].get('fairness', None)                      #TODO prioritizing fairness, eco or score for the output happens refCalc, and not in config or main. pls fix., here would be a good place to put the sorting function
    distance = matchmakingResults[0].get('avgDistance', None)                 
    score = matchmakingResults[0].get('score', None)          
    eco = matchmakingResults[0].get('eco', None)         
    combo = matchmakingResults[0].get('combo', None)
    
    for i in range(0, len(combo)):
        try:
            sellers = combo[i]
            buyer = sellers['buyer']
            buyerID = buyer.id
            buyer = buyer.location.split(",")
            buyerCity = buyer[0]
            buyerCountry = buyer[1]
            buyerClosest =API_Handling.closestWarehouse(buyerCity, buyerCountry)
            sellers = sellers['blocks']
            mongodb.mongo(buyerID, score, eco, fairness, buyerCity, buyerCountry, buyerClosest, sellers)
        except:
            print("seller dissapeared due to indexing error")
            pass
    return fairness, score, distance

def start(skipPrompts):
    'Master function'
   
    slotSize, endThreshold, sellerList, bidderList = readConfig(skipPrompts)

    sortingMode =2             #modes choose what to sort by 1 is fairness, 2 is score, 3 is average distance
    matchmakingResults = refCalc.matchMakingCalculation(sellerList, bidderList)         #Calculation of Valid combinations of buyers and sellers
    matchmakingResults = refCalc.evaluateCombinations(matchmakingResults, sortingMode)
    fairness, score, distance = outputHandler(matchmakingResults)


    if sortingMode ==1:
        "Case 1, sorting for  Fairness"                                                     #use if sorted by fairness in referenceCalculator
        print(f"Best fairness value: {fairness}")                                       
        print(f"Average distance with best fairness value {distance}")
        print(f"Eco Score whle best fairness value  {score}")

    elif sortingMode == 2:
        "Case 2, sorting for  Score" 
        print(f"Best score {score}")
        print(f"Fairness value,  While best score: {fairness}")                             #use if sorted by Score in referenceCalculator
        print(f"Average distance over all transports,  While best Score {distance}")
    
    elif sortingMode == 3:
        "Case 3, sorting for  Distance"                                                     #use if sorted by distance in referenceCalculator                                    
        print(f"Best Average distance {distance}")
        print(f"Best fairness value while shortest average distance: {fairness}")                                      
        print(f"Score value while shortest average distance  {score}")
    else:
        print("NONEXISTENT MODE")
    
    
    if fairness == None:
        print("No valid combinations were found")
    if skipPrompts:
        mp = matchmakingResults[0]['avgPrice']
        for bidder in bidderList:               # Give bidders a marketprice (price per unit) in order to formulate bids
            bidder.setMarketprice(mp)
        engine = SimEngine(sellerList, bidderList, slotSize, endThreshold)
        auctionResults = engine.simStart()
    else:
        auctionResults = []                  
   
    return matchmakingResults, auctionResults        


if __name__ == "__main__":
    start(False)
   
GUI.app.run()
