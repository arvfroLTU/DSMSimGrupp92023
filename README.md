# Simulation environment for demand-supply matching

This repository provides a system for simulating a demand-supply market with different aspects. This project is based of another project that investigates different behaviors in a demand-supply market and the auctioning system. While our project focuses more on reality driven aspects of the market with an environmental perspective such as implementing real world locations, as well as visualising the results.

If you want to read more about the other project you can see this repository https://github.com/elliotpk/d0020e for more details and if you want to read about this project in more detail you can read the report for this project found [here](/doc/report.pdf).

# How to run:
The code is made in Python 3.12 and before you can run the code you will need to have a few things installed:
## Things to install and get:
You will need these packages Pymongo, pyyaml, python flask, networkx, pandas and requests.

You will also need MongoDB https://www.mongodb.com/docs/manual/installation/ .

You will also need a google maps API key, you can create an account for free and get 300$ to use.

https://developers.google.com/maps/documentation/javascript/get-api-key

When you have your API key enter it in Src/static/templates/results and switch API_KEY_HERE with your API key

![api script](/images/api.png)

## Run the program
In the config.yaml file you kan change the settings for the simulation such as how many packages each seller has for sale and how the demand and supply looks like, Amount of simultaneously auctiond, terms for environmental impact and much more.

![config example](/images/config.png)

Now just make sure in the terminal you are in Src/ and run main.py this will launch the website and start the simulation, at first the website will display error. This is because all of the calculations are not done yet once all the calculations are done the website should refresh and show the start page if not refresh manually after calculations are done.

## Run Example:
This is what the console look like when the program is done running:
![console example](/images/console.png)
Then the website should update by it self(if not refresh website manually) and you should see the start page like this.
![start page](/images/index.png)
If you now press the Start button you should be able to see the results.
![results example](/images/result.png)

## Class Diagram:
![Class diagram](/images/uml.png)

## Sequence Diagram:
![sequence diagram](/images/seq.png)