# Simulation environment for demand-supply matching

This repository provides a system for simulating and investigating different behaviors and factors in a demand-supply market. Based of https://github.com/elliotpk/d0020e, see that repository for more details.

# How to run:
The code is made in Python 3.12 and before you can run the code you will need to have a few things installed:
## Things to install and get:
You will need these packages Pymongo, pyyaml, python flask, networkx, pandas and requests.

You will also need MongoDB https://www.mongodb.com/docs/manual/installation/ .

You will also need a google maps API key, you can create an account for free and get 300$ to use.

https://developers.google.com/maps/documentation/javascript/get-api-key

When you have your API key enter it in Src/static/templates/results and switch API_KEY_HERE with your API key

![Image Alt text](/images/api.png)

## Run the program
In the config.yaml file you kan change the settings for the simulation such as how many packages each seller has for sale and how the demand and supply looks like, Amount of simultaneously auctiond, terms for environmental impact and much more.

![Image Alt text](/images/config.png)

Now just make sure in the terminal you are in Src/ and run main.py this will launch the website and start the simulation, at first the website will display error. This is because all of the calculations are not done yet once all the calculations are done the website should refresh and show the start page if not refresh manually after calculations are done.

## Class Diagram:
![Image Alt text](/images/uml.png)

## Sequence Diagram:
![Image Alt text](/images/seq.png)