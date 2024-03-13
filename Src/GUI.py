#
from flask import Flask,url_for,render_template
import webbrowser
import pymongo
import csv
import json

# Creates Flask application named "app" and pass it the __name__,  which holds the name
# of the current python module, flask needs it for some work behind the scenes
app = Flask(__name__) 
    
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["mydatabase"]
mycol = mydb["customers"]

# Loops through mongoDB data and takes out each pair of buyer/seller's respective city

temp = []
buyer = []
sellersInfo = []
i = 0
for x in mycol.find():
    temp.append(list(x.values()))

for x in temp:
    for y in x:  
        if(i < 5):
            buyer.append(y)
        if(i>5):
            sellersInfo.append(y)
        i+=1

temp = []
temp2 = []
sellerPlaces = []
a = [sellersInfo[1], sellersInfo[3]]
b = [sellersInfo[1], sellersInfo[7]]
c = [sellersInfo[1], sellersInfo[11]]

temp.append(a)
temp.append(b)
temp.append(c)

temp2.append(temp)

sellerPlaces = temp2

toHtml = [sellersInfo[0], sellersInfo[4],sellersInfo[0], sellersInfo[8],sellersInfo[0], sellersInfo[12]]

print(sellersInfo)
print(sellerPlaces)
# print(buyer)





# y = []
# Row below is used for testing the code without mongodb
# each = [["id", "buyer", "score", "eco", "fairness", "buyercity", "land", "warehouse1", "seller", "seller1stad", "land", "warehouse2", "seller2", "seller2stad", "land", "warehouse3"], ["id", "buyer", "score", "eco", "fairness", "buyercity2", "land", "warehouse4", "seller", "seller12stad", "land", "warehouse5", "seller2", "seller22stad", "land", "warehouse6"]]
# for x in mycol.find():
#   buyersandseller = []
#   tempHolder = []
#   z = x
#   z = list(x.values())
#   howMany = (len(z)-8) / 4
#   next = 9
#   theBuyer = z[5]
#   while howMany > 0:
#       pairPerDeal = []
#       pairPerDeal.append(theBuyer)
#       pairPerDeal.append(z[next])
#       pairPerDeal.append(z[7])
#       pairPerDeal.append(z[next+2])
#       tempHolder.append(pairPerDeal)
#       next = next + 4
#       howMany = howMany -1
#   y.append(list(x.values()))
#   buyersandseller.append(tempHolder)
#   print(buyersandseller)
# y2=y

companyNames = ['Company 1','Company 2','Company 3', 'Company 4', 'Company 5', 'Company 6']

# z = []
# for x in city.find():
#   z.append(list(x.values()))
# temp = []
# for x in z:
#     temp.append(x[1])
# z = temp
    
####

allWaypoints = []
waypoints = ""
import csv, json
buyersandseller = [[['Stockholm', 'Oslo'], ['Stockholm', 'Berlin']], [['Barcelona', 'Winterthur'], ['Barcelona', 'Berlin']]]
for each in sellerPlaces:
    tempWaypoint = []
    for pair in each:
        
        with open('Database/Network_Database/shortest_paths.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['From'] == pair[0]:
                    if row['To'] == pair[1]:
                        waypoints = row['Path']
                        waypoints = waypoints.replace(" ->", ",")
                elif row['To'] == pair[0]:
                    if row['From'] == pair[1]:
                        waypoints = row['Path']
                        waypoints = waypoints.replace(" ->", ",")
            tempWaypoint.append(waypoints)
    allWaypoints.append(tempWaypoint)
# allWaypoints = json.dumps(allWaypoints)
# buyersandseller = json.dumps(buyersandseller)
print(allWaypoints)

                
####

@app.route('/') # Tells python it will work with a web browser (HTTP client)
def index():
    return render_template('index.html')

# companyNames = ""
y = ""

@app.route('/result')
def result():
    return render_template("result.html", names = companyNames, data = buyer, allTheRoutes = allWaypoints, buyerandSellers = toHtml, sellersInfo = sellersInfo)

@app.route('/sortfairness')
def sortfairness():
    fair = []
    i = 0
    sort = []
    for x in y:
        fair.append(int(x[2]))
    for x in fair:
        sort.append(x)
    sort.sort(reverse=True)

    temp = []
    temp2=[]
    j = 0

    while(j < len(sort)):
        i = 0
        while(i < len(sort)):
            if(int(sort[j]) == int(fair[i])):
                temp+=[companyNames[i]]
                temp2+=[y[i]]
                i+=1
            else:
                i+=1
        y2 = temp2
        companyNames2 = temp
        j+=1

    return render_template("sortfairness.html", names = companyNames2, data = y2, allTheRoutes = allWaypoints, buyerandSellers = buyersandseller)

@app.route('/config')
def config():
    return render_template("config.html")


htmlLocation = 'http://127.0.0.1:5000'
webbrowser.open_new_tab(htmlLocation)

# app.run()



# Skriv i powershell:
# DSMSimGrupp92023/.venv/Scripts/Activate.ps1
# python -m flask --app .\Src\GUI.py run
# Länk för guide: https://medium.com/@dipan.saha/managing-git-repositories-with-vscode-setting-up-a-virtual-environment-62980b9e8106