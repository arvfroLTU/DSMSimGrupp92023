from SimEngine import *
import Sellers
from Bidders import *
from ReferenceCalculator import *
import random
import math
import yaml

seed = None

# File names for configs hardcoded, could be set with a user input function
configFile = "config.yaml"
sellerFile = "sellers.yaml"
bidderFile = "bidders.yaml"

# Default limits how many blocks each seller can have randomized
MAX_BLOCK = 3
MIN_BLOCK = 2

# The generation of bidders and sellers is made simple by keeping the same format as the .yaml files for them throughout and at the end initalizing the objects from that config
def readConfig(skipPrompts):
    "Reads any configs which are present, and generates configs if they do not exist or if user wished to generate them"
    generatedConfig = 0
    try:
        with open(configFile, "r") as f:
            conf = yaml.load(f, Loader=yaml.FullLoader)
    except:
        print("Could not find a config file, generating")
        conf = genConfig()
        generatedConfig = 1
    try:
        with open(sellerFile, "r") as f:
            if not skipPrompts: raise
            sellers = yaml.load(f, Loader=yaml.FullLoader)
        conf["sellers"] = len(sellers)
    except:
        sellers = None

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

    supply, demand = getResourceUsage(sellers, bidders)
    # Determine which variables need to be generated
    if bidders and sellers:
        conf["resource-usage"] = demand / supply
    elif not bidders and not sellers:
        demand = random.randrange(500, 5000)
        supply = round(demand / conf["resource-usage"])
        bidders = genBidders(conf["bidders"], demand, conf["radius"], conf["distance-limit"], conf["distance-penalty"])
        sellers = genSellers(conf["sellers"], supply, conf["radius"], conf)
    elif bidders and not sellers:
        supply = round(demand / conf["resource-usage"])
        sellers = genSellers(conf["sellers"], supply, conf["radius"])
    else:
        demand = round(conf["resource-usage"] * supply)
        bidders = genBidders(conf["bidders"], demand, conf["radius"], conf["distance-limit"], conf["distance-penalty"])
    
    # Set distance limit and penalty if it exists
    if conf["distance-limit"] != None:
        overrideLimit(bidders, conf["distance-limit"])
    if conf["distance-penalty"] != None:
        overridePenalty(bidders, conf["distance-penalty"])

    # Init both bidders and sellers
    noAuctions, sellerList = initSellers(sellers)
    bidderList = initBidders(bidders, math.ceil(noAuctions / conf["slotsize"]))
    return conf['slotsize'], conf['end-threshold'], sellerList, bidderList

# Arbitrary ranges for the random generation of a whole config (if the file is not found)
def genConfig():
    """Generates a config.yaml file and saves it"""
    conf = {}
    conf["seed"] = random.randrange(0, 10000)
    random.seed(conf["seed"])
    conf["sellers"] = random.randrange(5, 15)
    conf["bidders"] = random.randrange(2, 7)
    conf["resource-usage"] = round(random.uniform(0.25, 0.9), 4)
    conf["radius"] = random.randint(2, 10)
    conf["distance-limit"] = round(random.uniform(conf["radius"]*1.5, conf["radius"]*3),2)
    conf["distance-penalty"] = round(random.uniform(5,10),2)
    conf["slotsize"] = 2
    conf["end-threshold"] = 2
    with open("config.yaml", "w") as f:
        yaml.dump(conf, f, sort_keys=False)

# Verify that all necessary values are present in the config, arbitrary ranges on the random calls
def verifyConfig(conf):
    if not conf["seed"]:
        conf["seed"] = random.randrange(0, 10000)
    random.seed(conf["seed"])
    if not conf["sellers"]:
        conf["sellers"] = random.randrange(5, 15)
    if not conf["bidders"]:
        conf["bidders"] = random.randrange(2, 7)
    if not conf["resource-usage"]:
        conf["resource-usage"] = round(random.uniform(0.25, 0.9), 4)
    if not conf["radius"]:
        conf["radius"] = random.randint(2,10)
    if not conf["distance-limit"]:
        conf["distance-limit"] = round(random.uniform(conf["radius"]*1.5, conf["radius"]*3),2)
    if not conf["distance-penalty"]:    
        conf["distance-penalty"] = round(random.uniform(5,10),2)
    if not conf["slotsize"]:
        conf["slotsize"] = 2
    if not conf["end-threshold"]:
        conf["end-threshold"] = 2

# Generation of sellers, the total supply is divided up into parts (randomly distributed size)
# Furthermore each seller can have chain their blocks together, randomly generated in range 'min-block' 'max-block' from config

def genSellers(number, supply, radius, conf):
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
            "location": genLocation(radius),
            "blocks": blocks,
        }
    return sellers


def genBidders(number, demand, radius, limit, penalty):
    bidders = {}
    dividers = sorted(random.sample(range(1, demand), number))
    demands = [a - b for a, b in zip(dividers + [demand], [0] + dividers)]
    for i in range(number):
        bidders["Bidder" + str(i)] = {
            "location": genLocation(radius),
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
        for sellerKey in sellers:
            for block in sellers[sellerKey]["blocks"].items():
                supply += block[1][0]["quantity"]
    demand = 0
    if bidders:
        for bidderKey in bidders:
            demand += bidders[bidderKey]["need"]
    return supply, demand


def initSellers(sellers):
    sellerList = []
    noAuctions = 0
    for sellerKey in sellers:
        entity = Sellers.Sellers(sellerKey, sellers[sellerKey]["location"])
        firstBlock = sellers[sellerKey]["blocks"].pop("block1")
        entity.quantity.append(firstBlock[0]['quantity'])
        entity.genBlock(
            firstBlock[1]["price"], firstBlock[0]["quantity"], firstBlock[2]["discount"]
        )
        noAuctions += 1
        for block in sellers[sellerKey]["blocks"].items():
            entity.quantity.append(block[1][0]['quantity'])
            entity.addBlock(
                block[1][1]["price"], block[1][0]["quantity"], block[1][2]["discount"]
            )
            noAuctions += 1
        sellerList.append(entity)
    return noAuctions, sellerList


def initBidders(bidders, maxRounds):
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
        bidderList.append(entity)
    return bidderList

# Source with explanation: https://stackoverflow.com/a/50746409
def genLocation(radius):
    "Generate x,y points within circle with set radius with center in 0,0"
    r = radius * math.sqrt(random.random())
    theta = random.random() * 2 * math.pi
    x = round(r * math.cos(theta), 4)
    y = round(r * math.sin(theta), 4)
    return [x,y]

def overrideLimit(bidders, limit):
    for bidder in bidders.items():
        bidder[1]['distanceLimit'] = limit

def overridePenalty(bidders, penalty):
    for bidder in bidders.items():
        bidder[1]['distancePenalty'] = penalty

def start(skipPrompts):
    slotSize, endThreshold, sellerList, bidderList = readConfig(skipPrompts)
    fairness = 1
    #TODO Serialize matchmaking results and store in appropriate way
    matchmakingResults = matchMakingCalculation(sellerList, bidderList)
    fairness = matchmakingResults[0].get('fairness', None)
    distance = matchmakingResults[0].get('avgDistance', None)
    print(f"Best fairness value: {fairness}")
    print(f"Average distance {distance}")
    if fairness == None:
        print("No valid combinations were found")
    if skipPrompts:
        mp = matchmakingResults[0]['avgPrice']
        for bidder in bidderList:               # Give bidders a marketprice (price per unit) in order to formulate bids
            bidder.setMarketprice(mp)
        engine = SimEngine(sellerList, bidderList, slotSize, endThreshold)
        auctionResults = engine.simStart()
    else:
        auctionResults = []                     # always empty
    
    return matchmakingResults, auctionResults

if __name__ == "__main__":
    start(False)