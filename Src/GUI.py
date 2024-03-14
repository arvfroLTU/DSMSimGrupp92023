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

#Creates array with buyer and sellers location for shortest path calc
#ex [[['Stockholm', 'Oslo'], ['Stockholm', 'Berlin']], [['Barcelona', 'Winterthur'], ['Barcelona', 'Berlin']]]
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


companyNames = ['Company 1','Company 2','Company 3', 'Company 4', 'Company 5', 'Company 6']

#Gets the cities that the shortest path goes thru
allWaypoints = []
waypoints = ""
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


                
####

@app.route('/') # Tells python it will work with a web browser (HTTP client)
def index():
    return render_template('index.html')


@app.route('/result')
def result():
    return render_template("result.html", names = companyNames, data = buyer, allTheRoutes = allWaypoints, buyerandSellers = toHtml, sellersInfo = sellersInfo)

@app.route('/config')
def config():
    return render_template("config.html")


htmlLocation = 'http://127.0.0.1:5000'
webbrowser.open_new_tab(htmlLocation)

app.run()
