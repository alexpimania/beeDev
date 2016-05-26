# BEE digital currency trading engine.
# Contains:
# -  orderBook operations.
# -  Admin UI services.
#


import os
import json # to encode and decode Json
import sys

# Set the BEE_PATH from the corresponding OS environment variable.
# BEE_PATH contains the ini files and output files for each profile.

BEE_PATH = sys.argv[1]  # this argument is passed in by the calling script and will fail if not provided.


    
def getOrderBook(exchangeList):
    # Gets orderBooks for specified exchanges - as specified in the input exchangeList
    # Returns a merged orderbook.
    failedExchanges = []
    mergedOrderBook = [[],[]]

    def orderBookMerger(mergedOrderBook, newOrderBook): # Appends two order books
        mergedOrderBook[0] =  mergedOrderBook[0] + newOrderBook[0] # Add the two bid orderbooks
        mergedOrderBook[1] =  mergedOrderBook[1] + newOrderBook[1] # Add the two ask orderbooks
        return mergedOrderBook #Ends the orderBookMerger function and returns the new merged orderbook composed of the two inputs to the function

    with open(BEE_PATH + "/backend" + "/beeExchangeList.ini") as beeExchangeListFile:
        allExchanges = json.loads(beeExchangeListFile.read())
    
    # Step through all exchanges and match the one's of this profile. i.e. ignore those not in the profile's exchange list.
    for exchange in allExchanges:
        
        # If this exchange is in the profile's exchange list, then get the orderbook
        if exchange["exchangeName"] in exchangeList:

            # run the orderbook load routine for this type of exchange 
            try:
                newOrderBook = eval("orderBookLoad" + str(exchange["exchangeType"]))(str(exchange["exchangeURL"]))
            except:
                newOrderBook = [[],[]] # if the data download from the exchange failed, just add nothing!
                failedExchanges.append(exchange["exchangeName"])

            # Now merge the new orderbook with our accumulated orderbook
            mergedOrderBook = orderBookMerger(mergedOrderBook, newOrderBook) # merge the accumulated orderBook with the new orderrbook from this iteration's exchange.

    mergedOrderBook[0] = sorted(mergedOrderBook[0], key = lambda  x: x[0])[::-1] # Sorts bids according to price - in REVERSE
    mergedOrderBook[1] = sorted(mergedOrderBook[1], key = lambda  x: x[0]) # Sorts asks according to price.
    if failedExchanges:
        failedExchanges = "Exchanges that are down: (" + " | ".join(failedExchanges) + ")"

    return [mergedOrderBook, failedExchanges]


def getOrderBookStatsList(bidsAndAsks, depthList):
 
    # Given an orderbook and a list of depths, returns the following:
    # - bidsFiatTotal
    # - asksBTCTotal
    # - list of pricesAtBidDepths,
    # - list of pricesAtAskDepths,
    # - list of bid 'ratios' for each entry in depthList 
    bidDepth = 0
    bidsFiatTotal = 0
    maxOutError = []
    
    # Calc total of Amounts of bids for orderbook
    for bidOrder in bidsAndAsks[0]:
        # bidDepth = bidDepth + bidOrder[1]  # NOT REQUIRED?

        # Accumulate Price * Amount into bidsFiatTotal
        bidsFiatTotal = bidsFiatTotal + (bidOrder[0] * bidOrder[1])

    askDepth = 0
    asksBTCTotal = 0
    
    # Calc total of Amounts of asks for orderbook
    for askOrder in bidsAndAsks[1]:
        # askDepth = askDepth + askOrder[1]  # NOT REQUIRED?

        # Accumulate Price * Amount into bidsOrderFiat
        asksBTCTotal = asksBTCTotal + askOrder[1]

  
    # Now setup for getting the prices at all bid depths.
    depthListIndex = 0
    accumulatedBidAmount = 0
    accumulatedBidFiat = 0
    pricesAtBidDepths = []

    # Step through the bids
    for bidOrder in bidsAndAsks[0]:
        
        # Accumulate the amount of bids
        accumulatedBidAmount = accumulatedBidAmount + bidOrder[1]

        # Accumulate the fiat (e.g. USD) of bids. i.e. sum(bidOrder[amount] * bidOrder[BTC])
        accumulatedBidFiat = accumulatedBidFiat + (bidOrder[0] * bidOrder[1])
        
        # If we've reached the current depthList threshold, save then go to next depthList entry
        if accumulatedBidAmount >= float(depthList[depthListIndex]):
            
            # pricesAtBidDepths.append(bidOrder[0]) WAS THIS
            pricesAtBidDepths.append(round(accumulatedBidFiat / accumulatedBidAmount,2))

            depthListIndex = depthListIndex + 1

            # Leave the FOR loop if we've exhausted the list of depthList entries
            if depthListIndex == len(depthList):
                break
                

    # If we didn't find enough bids, append False entries to pricesAtBidDepths[]
    if len(pricesAtBidDepths) < len(depthList):
        maxOutError.append("bids have been maxed out")
        
    while len(pricesAtBidDepths) < len(depthList):       
        try:
            pricesAtBidDepths.append(round(accumulatedBidFiat / accumulatedBidAmount,2))
        except:
            pricesAtBidDepths.append("No Data")
            

    # Now setup for getting the prices at all ask depths.
    depthListIndex = 0
    accumulatedAskAmount = 0
    accumulatedAskFiat = 0
    pricesAtAskDepths = []
    # Step through the asks
    for askOrder in bidsAndAsks[1]:
        
        # Accumulate the amount of asks
        accumulatedAskAmount = accumulatedAskAmount + askOrder[1]

        # Accumulate the fiat (e.g USD) of asks. i.e. sum(askOrder[amount] * askOrder[BTC])
        accumulatedAskFiat = accumulatedAskFiat + (askOrder[0] * askOrder[1])

        # If we've reached the current depthList threshold, save to pricesAtAskDepths then go to next depthList entry 
        if accumulatedAskAmount >= float(depthList[depthListIndex]):
            
            # pricesAtAskDepths.append(askOrder[0]) WAS THIS
            pricesAtAskDepths.append(round(accumulatedAskFiat / accumulatedAskAmount,2))

            depthListIndex = depthListIndex + 1

            # If we've exhausted the list of depthList entries, leave the FOR loop 
            if depthListIndex == len(depthList):
                break

    # If we didn't find enough asks, append False entries to pricesAtAskDepths[]
    if len(pricesAtAskDepths) < len(depthList):
        maxOutError.append("asks have been maxed out")
        
    while len(pricesAtAskDepths) < len(depthList):
        try:
            pricesAtAskDepths.append(round(accumulatedBidFiat / accumulatedBidAmount,2))
        except:
            pricesAtAskDepths.append("No Data")


    # Now setup for getting the bid 'ratios' for all entries in depthList.
    depthListIndex = 0
    depthRatios = []

    # First, get price for depth of 1k
    bid1000Price = getBid1000Price(bidsAndAsks)  # If there isn't a depth of 1000, this will have returned 'False'

    # Calculate bid 'ratios'   i.e. (1k-nk)/1k for each depth
    for aDepth in depthList:
        if (isinstance(pricesAtBidDepths[depthListIndex],float) and isinstance(bid1000Price,float)):  # Check is is an float, and not 'False'
            depthRatios.append(round((bid1000Price - pricesAtBidDepths[depthListIndex]) / bid1000Price,3))
        else:
            depthRatios.append('False')

        depthListIndex = depthListIndex + 1


    return [[bidsFiatTotal, asksBTCTotal, pricesAtBidDepths, pricesAtAskDepths, depthRatios], " and ".join(maxOutError)]


def getBid1000Price(bidsAndAsks):
    # Returns the bid price at depth 1k, given a list of bids (and also asks are passed in for ease - but we ignore those here)

##    accumulatedBidAmount = 0
##
##    # Step through the bids up unto 1000
##    for currentBid in bidsAndAsks[0]:
##        
##        # Accumulate the amount of bids
##        accumulatedBidAmount = accumulatedBidAmount + currentBid[1]
##
##        # If we've reached the current depthList threshold, save then go to next depthList entry 
##        if accumulatedBidAmount >= 1000:
##            return currentBid[0]
##
##    # If we didn't find enough bids,  return 'False' 
##    return "False"

    # Now setup for getting the prices at all bid depths.
    accumulatedBidAmount = 0
    accumulatedBidFiat = 0
    pricesAtBidDepths = []

    # Step through the bids
    for bidOrder in bidsAndAsks[0]:
        
        # Accumulate the amount of bids
        accumulatedBidAmount = accumulatedBidAmount + bidOrder[1]

        # Accumulate the fiat (e.g. USD) of bids. i.e. sum(bidOrder[amount] * bidOrder[BTC])
        accumulatedBidFiat = accumulatedBidFiat + (bidOrder[0] * bidOrder[1])
        
        # If we've reached the depthList threshold, return the average
        if accumulatedBidAmount >= 1000: #float(depthList[depthListIndex]):
            
            return round(accumulatedBidFiat / accumulatedBidAmount,2) # i.e. the average price.
           
    # Ah, we didn't find enough bids. Return 'False' 
    return "False"    



#####################################################################################
########### The following are generic orderBook load routines.
########### Each exchange will be supported by one of the types listed below.
########### We generally don't have specific orderbook load routines for a given exchange,
########### we use a limited set of load routines as listed below.
#####################################################################################



def orderBookLoadtype1(URL):
    import requests #Import the module that is used to download order-book off API
    import json #Import module that has the ability to encode and decode Json

    bidsAndAsks = [] #Declaring a list called "bidsAndAsks" that will store the Bids and Asks extracted from the API in two lists
    bidsAndAsks = [[],[]] #Making the list called "bidsAndAsks" contain two empty lists a.k.a (Bids list and Asks list) used in a later part of the program to avoid an empty list error

    response = requests.get(URL, verify=False) #Getting the order book from the bitfinex api
    dictResponse = json.loads(response.content.decode("utf-8")) #Converting the json data from the API order book response to a construction of dictionaries and lists

    # get the bids from the APi response and put them into the std format
    for order in dictResponse["bids"]:
        bidsAndAsks[0].append([float(order["price"]), float(order["amount"])])

    # get the asks from the APi response and put them into the std format
    for order in dictResponse["asks"]:
        bidsAndAsks[1].append([float(order["price"]), float(order["amount"])])

    return bidsAndAsks


def orderBookLoadtype2(URL):
    import requests #Import the module that is used to download order-book off API
    import json #Import module that has the ability to encode and decode Json

    bidsAndAsks = [] #Declaring a list called "bidsAndAsks" that will store the Bids and Asks extracted from the API in two lists
    bidsAndAsks = [[],[]] #Making the list called "bidsAndAsks" contain two empty lists a.k.a (Bids list and Asks list) used in a later part of the program to avoid an empty list error

    response = requests.get(URL, verify=False) #Getting the order book from the bitfinex api
    dictResponse = json.loads(response.content.decode("utf-8")) #Converting the json data from the API order book response to a construction of dictionaries and lists

    # get the bids from the APi response and put them into the std format
    for order in dictResponse["bids"]:
        bidsAndAsks[0].append([float(order[0]), float(order[1])])

    # get the asks from the APi response and put them into the std format
    for order in dictResponse["asks"]:
        bidsAndAsks[1].append([float(order[0]), float(order[1])])

    return bidsAndAsks


def orderBookLoadtype3(URL):

    import requests #Import the module that is used to download order-book off API
    import json #Import module that has the ability to encode and decode Json

    bidsAndAsks = [] #Declaring a list called "bidsAndAsks" that will store the Bids and Asks extracted from the API in two lists
    bidsAndAsks = [[],[]] #Making the list called "bidsAndAsks" contain two empty lists a.k.a (Bids list and Asks list) used in a later part of the program to avoid an empty list error

    response = requests.get(URL, verify=False) #Getting the order book from the  api
    dictResponse = json.loads(response.content.decode("utf-8")) #Converting the json data from the API order book response to a construction of dictionaries and lists

    # get the bids from the APi response and put them into the std format
    for order in dictResponse["btc_usd"]["bids"]:
        bidsAndAsks[0].append([float(order[0]), float(order[1])])

    # get the asks from the APi response and put them into the std format
    for order in dictResponse["btc_usd"]["asks"]:
        bidsAndAsks[1].append([float(order[0]), float(order[1])])

    return bidsAndAsks    
    
    
def orderBookLoadtype4(URL):
    import requests #Import the module that is used to download order-book off API
    import json #Import module that has the ability to encode and decode Json

    bidsAndAsks = [] #Declaring a list called "bidsAndAsks" that will store the Bids and Asks extracted from the API in two lists
    bidsAndAsks = [[],[]] #Making the list called "bidsAndAsks" contain two empty lists a.k.a (Bids list and Asks list) used in a later part of the program to avoid an empty list error

    response = requests.get(URL, verify=False) #Getting the order book from the  api
    dictResponse = json.loads(response.content.decode("utf-8")) #Converting the json data from the API order book response to a construction of dictionaries and lists

    # get the bids from the APi response and put them into the std format
    for order in dictResponse["data"]["bids"]:
        bidsAndAsks[0].append([float(order["price"]), float(order["amount"])])

    # get the asks from the APi response and put them into the std format
    for order in dictResponse["data"]["asks"]:
        bidsAndAsks[1].append([float(order["price"]), float(order["amount"])])

    return bidsAndAsks    
    

def orderBookLoadtype5(URL):
    import requests #Import the module that is used to download order-book off API
    import json #Import module that has the ability to encode and decode Json

    bidsAndAsks = [] # will store the Bids and Asks extracted from the API in two lists
    bidsAndAsks = [[],[]] # contain two empty lists a.k.a (Bids list and Asks list) used in a later part of the program to avoid an empty list error

    response = requests.get(URL, verify=False) #Getting the order book from the  api
    dictResponse = json.loads(response.content.decode("utf-8")) #Converting the json data from the API order book response to a construction of dictionaries and lists

    # get the bids from the APi response and put them into the std format
    for order in dictResponse["result"]["XXBTZUSD"]["bids"]:
        bidsAndAsks[0].append([float(order[0]), float(order[1])])

    # get the asks from the APi response and put them into the std format
    for order in dictResponse["result"]["XXBTZUSD"]["asks"]:
        bidsAndAsks[1].append([float(order[0]), float(order[1])])

    return bidsAndAsks    


def orderBookLoadtype6(URL):
    import requests #Import the module that is used to download order-book off API
    import json #Import module that has the ability to encode and decode Json

    bidsAndAsks = [] # will store the Bids and Asks extracted from the API in two lists
    bidsAndAsks = [[],[]] # contain two empty lists a.k.a (Bids list and Asks list) used in a later part of the program to avoid an empty list error

    response = requests.get(URL, verify=False) #Getting the order book from the  api
    dictResponse = json.loads(response.content.decode("utf-8")) #Converting the json data from the API order book response to a construction of dictionaries and lists

    # get the bids from the APi response and put them into the std format
    for order in dictResponse["data"]:
        if order["type"] == "Sell":
            bidsAndAsks[1].append([float(order["price"]), float(order["quantity"])])
        if order["type"] == "buy":
            bidsAndAsks[0].append([float(order["price"]), float(order["quantity"])])

    return bidsAndAsks


def orderBookLoadtype7(URL):
    import requests #Import the module that is used to download order-book off API
    import json #Import module that has the ability to encode and decode Json

    bidsAndAsks = [] #Declaring a list called "bidsAndAsks" that will store the Bids and Asks extracted from the API in two lists
    bidsAndAsks = [[],[]] #Making the list called "bidsAndAsks" contain two empty lists a.k.a (Bids list and Asks list) used in a later part of the program to avoid an empty list error

    response = requests.get(URL, verify=False) #Getting the order book from the bitfinex api
    dictResponse = json.loads(response.content.decode("utf-8")) #Converting the json data from the API order book response to a construction of dictionaries and lists

    # get the bids from the APi response and put them into the std format
    for order in dictResponse["Bids"]:
        bidsAndAsks[0].append([float(order[0]), float(order[1])])

    # get the asks from the APi response and put them into the std format
    for order in dictResponse["Asks"]:
        bidsAndAsks[1].append([float(order[0]), float(order[1])])

    return bidsAndAsks
    
      
def orderBookLoadtype8(URL):
    import requests #Import the module that is used to download order-book off API
    import json #Import module that has the ability to encode and decode Json

    bidsAndAsks = [] #Declaring a list called "bidsAndAsks" that will store the Bids and Asks extracted from the API in two lists
    bidsAndAsks = [[],[]] #Making the list called "bidsAndAsks" contain two empty lists a.k.a (Bids list and Asks list) used in a later part of the program to avoid an empty list error

    response = requests.get(URL, verify=False) #Getting the order book from the bitfinex api
    dictResponse = json.loads(response.content.decode("utf-8")) #Converting the json data from the API order book response to a construction of dictionaries and lists

    # get the bids from the APi response and put them into the std format
    for order in dictResponse["bid"]:
        bidsAndAsks[0].append([float(order["usd"]), float(order["btc"])])

    # get the asks from the APi response and put them into the std format
    for order in dictResponse["ask"]:
        bidsAndAsks[1].append([float(order["usd"]), float(order["btc"])])

    return bidsAndAsks  


def orderBookLoadtype9(URL):
    import requests #Import the module that is used to download order-book off API
    import json #Import module that has the ability to encode and decode Json

    bidsAndAsks = [] #Declaring a list called "bidsAndAsks" that will store the Bids and Asks extracted from the API in two lists
    bidsAndAsks = [[],[]] #Making the list called "bidsAndAsks" contain two empty lists a.k.a (Bids list and Asks list) used in a later part of the program to avoid an empty list error

    response = requests.get(URL, verify=False) #Getting the order book from the bitfinex api
    dictResponse = json.loads(response.content.decode("utf-8")) #Converting the json data from the API order book response to a construction of dictionaries and lists

    # get the bids from the APi response and put them into the std format
    for order in dictResponse["bids"]:
        bidsAndAsks[0].append([float(order["price"]), float(order["volume"])])

    # get the asks from the APi response and put them into the std format
    for order in dictResponse["asks"]:
        bidsAndAsks[1].append([float(order["price"]), float(order["volume"])])

    return bidsAndAsks


def orderBookLoadtype10(URL):
    import requests #Import the module that is used to download order-book off API
    import json #Import module that has the ability to encode and decode Json

    bidsAndAsks = [] #Declaring a list called "bidsAndAsks" that will store the Bids and Asks extracted from the API in two lists
    bidsAndAsks = [[],[]] #Making the list called "bidsAndAsks" contain two empty lists a.k.a (Bids list and Asks list) used in a later part of the program to avoid an empty list error

    response = requests.get(URL, verify=False) #Getting the order book from the bitfinex api
    dictResponse = json.loads(response.content.decode("utf-8")) #Converting the json data from the API order book response to a construction of dictionaries and lists

    # get the bids from the APi response and put them into the std format
    for order in dictResponse["data"]["buy"]:
        bidsAndAsks[0].append([float(order["rate"]), float(order["amount"])])

    # get the asks from the APi response and put them into the std format
    for order in dictResponse["data"]["sell"]:
        bidsAndAsks[1].append([float(order["rate"]), float(order["amount"])])

    return bidsAndAsks


def orderBookLoadtype11(URL):
    import requests #Import the module that is used to download order-book off API
    import json #Import module that has the ability to encode and decode Json

    bidsAndAsks = [] #Declaring a list called "bidsAndAsks" that will store the Bids and Asks extracted from the API in two lists
    bidsAndAsks = [[],[]] #Making the list called "bidsAndAsks" contain two empty lists a.k.a (Bids list and Asks list) used in a later part of the program to avoid an empty list error

    response = requests.get(URL, verify=False) #Getting the order book from the bitfinex api
    dictResponse = json.loads(response.content.decode("utf-8")) #Converting the json data from the API order book response to a construction of dictionaries and lists

    # get the bids from the APi response and put them into the std format
    for order in dictResponse["BTC_USD"]["bid"]:
        bidsAndAsks[0].append([float(order[0]), float(order[2])])

    # get the asks from the APi response and put them into the std format
    for order in dictResponse["BTC_USD"]["ask"]:
        bidsAndAsks[1].append([float(order[0]), float(order[2])])

    return bidsAndAsks
#####################################################################################
########### The following are the UI admin services. These mostly return/expect JSON.
#####################################################################################




def getProfileNameList():
    # Returns a JSON list of all profile names. No input required.
    # This is used by the UI so it can display the profile list.
    
    import json #Import module that has the ability to encode and decode Json

    returnProfileNameList = [] # Define the list
    
    iniProfiles = json.loads(open(BEE_PATH + "/backend" + '/beeProfileList.ini').read())

    for aProfile in iniProfiles:
        returnProfileNameList.append(aProfile["profileName"]) 

    return json.dumps(returnProfileNameList, sort_keys=False, indent=4)

 

def getProfileDetails(profileToMatch):
    # Returns the JSON profile details for the specified profile (profileToMatch)
    # This is used by the UI so it can display the profile details.
    
    import json #Import module that has the ability to encode and decode Json

    iniProfiles = json.loads(open(BEE_PATH + "/backend" + '/beeProfileList.ini').read())

    for aProfile in iniProfiles:
        if aProfile["profileName"] == profileToMatch:
            #return aProfile
            return json.dumps(aProfile, sort_keys=False, indent=4)

    # If didn't find profileToMatch, return error.
    return "Not found"


def getExchangeList(exchangeGroup):

    # Returns the JSON list of all exchanges in the exchangeGroup. If no exchangeGroup specified, returns all exchanges.
    # Exchanges are obtained from an ini file beeExchangeList.ini
    
    import json #Import module that has the ability to encode and decode Json

    exchangeList = json.loads(open(BEE_PATH + "/backend" + '/beeExchangeList.ini').read())

    returnListOfExchanges = [] # Defines the list.

    # Build the list of exchanges specified by the exchangeGroup
    for anExchange in exchangeList:
        if anExchange["exchangeCurrency"] == exchangeGroup or exchangeGroup == "":
            returnListOfExchanges.append(anExchange["exchangeName"]) 

    returnListOfExchanges = sorted(returnListOfExchanges) # Sort the list
    
    return json.dumps(returnListOfExchanges, sort_keys=False, indent=4)



def updateProfile(profileDetailsJSON):
    # Takes a JSON profileDetails as input.
    # Updates an existing profile with the profileDetailsJSON if the profileName exists,
    # otherwise creates a new profile with profileDetailsJSON.
   
    import json #Import module that has the ability to encode and decode Json

    iniProfiles = json.loads(open(BEE_PATH + "/backend" + '/beeProfileList.ini').read())

    profileDetails = json.loads(profileDetailsJSON) # Convert to dict object

    # Ensure the depthlist entries are sorted numerically
    sortedDepthList = sorted(profileDetails["depthList"], key = lambda x: int(x))
    profileDetails["depthList"] = sortedDepthList     
    
    profileIndex = 0

    #Step through the profiles to see if we should update an existing entry.
    for aProfile in iniProfiles:
        if aProfile["profileName"] == profileDetails["profileName"]:

            # Found matching entry - so update it, write it all back to the ini file then return.
            iniProfiles[profileIndex] = profileDetails
            
            with open(BEE_PATH + "/backend" + '/beeProfileList.ini', 'w') as outfile:
                json.dump(iniProfiles, outfile, sort_keys = False, indent = 4, ensure_ascii = False)
            return "Update"
        profileIndex = profileIndex + 1
        
    # No match, so append the new profile (profileDetails) to the end of the profiles, write it all back to the ini file then return.

    profileDetails["lastRunTime"] = "" # since this is a new profile, ensure lastRunTime is blank
    
    iniProfiles.append(profileDetails)

    with open(BEE_PATH + "/backend" + '/beeProfileList.ini', 'w') as outfile:
                json.dump(iniProfiles, outfile, sort_keys = False, indent = 4, ensure_ascii = False)
    return "Add"


def deleteProfile(profileToDeleteName):
    # Deletes an existing profile if the profileName exists,
    # otherwise ignores and returns error "Not found".

    # import json #Import module that has the ability to encode and decode Json

    iniProfiles = json.loads(open(BEE_PATH + "/backend" + '/beeProfileList.ini').read())

    profileIndex = 0

    #Step through the profiles to see if we should delete an existing entry
    for aProfile in iniProfiles:
        if aProfile["profileName"] == profileToDeleteName:

            # Found matching entry - so delete it, write it all back to the ini file then return.
            del iniProfiles[profileIndex]

            with open(BEE_PATH + "/backend" + '/beeProfileList.ini', 'w') as outfile:
                json.dump(iniProfiles, outfile, sort_keys = False, indent = 4, ensure_ascii = False)
            return "Delete"
        
        profileIndex = profileIndex + 1    
                      
    # Could not find matching profile, so return 'Not found'
    return 'Not found'
                      


def generateOutput(profileName):
    # For a given profile, generates a line of output to the profile's output file.
    # (This functions runs getOrderBook, and therefore takes a while.

    from datetime import datetime # To access GMT time
    
    # Load all the profiles 
    iniProfiles = json.loads(open(BEE_PATH + "/backend" + '/beeProfileList.ini').read())

    # Find the matching profile.
    for aProfile in iniProfiles:
        if aProfile["profileName"] == profileName:

            # Found matching profile - so get the orderbook, generate the stats, write a new line to the output file then return.
            
            orderBook, failedExchanges = getOrderBook(aProfile["exchangeList"])

            # Get the stats
            statsList, maxOutError = getOrderBookStatsList(orderBook, aProfile["depthList"])
            # Returns:
            # - bidsFiatTotal
            # - asksBTCTotal
            # - list of pricesAtBidDepths,
            # - list of pricesAtAskDepths,
            # - list of bid 'ratios' for each entry in depthList 
            outputLine = constructProfileStatsTextLine(statsList)
            if failedExchanges:
                outputLine += failedExchanges
            if maxOutError:
                outputLine += maxOutError + "\n"
            else:
                outputLine += "\n"
            


            # Check the logfile directory exists. If not create it.
            if not os.path.exists(BEE_PATH + "/logfiles"):
                os.makedirs(BEE_PATH + "/logfiles") 
            
            # Build the output filename
            outFilename = BEE_PATH + "/logfiles/bee_" + aProfile["profileName"] + ".txt"

            # If the file does not already exist, write a header including field labels.
            # It will look something like this:
            #
            #    Profile: profile06
            #    Exchanges: Bitfinex, Bitstamp, Coinbase, Okcoin, Btce, Btcx, Itbit, 
            #
            #    GMT, Bid Total Fiat, Ask Total BTC, Bid10, Ask10, Bid100, Ask100, Bid1000, Ask1000, Bid10000, Ask10000, Bid100000, Ask100000, 

            if not os.path.exists(outFilename):
                with open(outFilename , 'w') as outf:
                    outf.write(constructProfileStatsTextHeader(aProfile))
            
            # Append the generated bid and ask prices to end of the output file.  i.e write the line    
            with open(outFilename , 'a') as outf:
                outf.write(outputLine)
            
            return "Found"

    return "Not found"


def getProfileStats(profileName):
    # for a specified profileName, returns JSON stats.
    # Typically used by the UI to retrieve and display the JSON stats.
    # If you want a CSV output, use getProfileStatsText instead.
    
    # Load all the profiles 
    iniProfiles = json.loads(open(BEE_PATH + "/backend" + '/beeProfileList.ini').read())

    # Find the matching profile.
    for aProfile in iniProfiles:
        if aProfile["profileName"] == profileName:

        # Found matching profile - so get the orderbook, generate the stats, then return the stats in JSON.
            orderBook, failedExchanges = getOrderBook(aProfile["exchangeList"])
            # Get the stats
            statsList, maxOutError = getOrderBookStatsList(orderBook, aProfile["depthList"])
            # Returns:
            # - bidsFiatTotal
            # - asksBTCTotal
            # - list of pricesAtBidDepths,
            # - list of pricesAtAskDepths,
            # - list of bid 'ratios' for each entry in depthList 

            return json.dumps(statsList, sort_keys=False, indent=4)

    return "Not found"

def getProfileStatsText(profileName):
    # for a specified profileName, returns TEXT stats.
    # Typically used by the UI to retrieve and display the TEXT stats.
    # If you want a JSON output, use getProfileStats() instead.

    anExchangeWasDown = False
    
    # Load all the profiles 
    iniProfiles = json.loads(open(BEE_PATH + "/backend" + '/beeProfileList.ini').read())

    # Find the matching profile.
    for aProfile in iniProfiles:
        if aProfile["profileName"] == profileName:

            # Found matching profile - so get the orderbook, generate the stats, then return the stats in JSON.

            orderBook, failedExchanges = getOrderBook(aProfile["exchangeList"])

            # Get the stats
            statsList, maxOutError = getOrderBookStatsList(orderBook, aProfile["depthList"])
            # Returns:
            # - bidsFiatTotal
            # - asksBTCTotal
            # - list of pricesAtBidDepths,
            # - list of pricesAtAskDepths,
            # - list of bid 'ratios' for each entry in depthList 

            headerText = constructProfileStatsTextHeader(aProfile)
            lineText   = constructProfileStatsTextLine(statsList) 
            outputLine = headerText + lineText
            
            if failedExchanges:
                outputLine += failedExchanges
            if maxOutError:
                outputLine += maxOutError + "\n"
            else:
                outputLine += "\n"
            return outputLine
            

    return "Not found"


def constructProfileStatsTextHeader(aProfile):

    # Given aProfile, returns the text header output for the profile.
    # It will look something like this:
    #
    #    Profile: profile06
    #    Exchanges: Bitfinex, Bitstamp, Coinbase, Okcoin, Btce, Btcx, Itbit, 
    #
    #    GMT, Bid Total Fiat, Ask Total BTC, Bid10, Ask10, Bid100, Ask100, Bid1000, Ask1000, Bid10000, Ask10000, Bid100000, Ask100000, 
    
    theOutput = "GMT, Bid Total Fiat, Ask Total BTC, "

    # Write out the list of depths labels for this profile.
    for depth in aProfile["depthList"]:
        theOutput = theOutput +"Bid" + str(depth) + ", " + "Ask" + str(depth) + ", "

    for depth in aProfile["depthList"]:
        theOutput = theOutput +"BidRatio" + str(depth) + ", " 

    theOutput = theOutput + " Warnings,\n\n"

    return theOutput


def constructProfileStatsTextLine(statsList):
    # Constructs the values of a line of profile stats -

    from datetime import datetime # To access GMT time

    # Build up the outputLine: GMT, BID TOTAL FIAT, ASK TOTAL BTC

##    # First, do GMTime and strip the milliseconds
##    GMTime = datetime.utcnow()
##    # Strip millisends from input HR time
##    GMTimeNoUsecs = datetime.strptime(GMTime.strftime('%Y-%m-%d %H:%M:%S'), "%Y-%m-%d %H:%M:%S")
##    
##    outputLine = str(GMTimeNoUsecs) + ", " + str(int(statsList[0])) + "," + str(int(statsList[1])) + ", "                  # ASK TOTAL BTC

    outputLine = getGMTime() + ", " + str(int(statsList[0])) + "," + str(int(statsList[1])) + ", "                  # ASK TOTAL BTC

    # Add BID LIMIT and ASK LIMIT pairs as required.
    depthCounter = 0
    while depthCounter < len(statsList[2]):
        outputLine = outputLine + str(statsList[2][depthCounter]) + ", " +  str(statsList[3][depthCounter]) + ", "      # ASKS
        
        depthCounter = depthCounter + 1
   
    # Add the bid 'ratios'
    depthCounter = 0
    while depthCounter < len(statsList[2]):
        outputLine = outputLine + str(statsList[4][depthCounter]) + ", "       # bid ratios (1k-nk)/1k for each depth
        
        depthCounter = depthCounter + 1
  

    return outputLine

def getGMTime():
    # returns GMT in string format

    from datetime import datetime # To access GMT time

    # do GMTime and strip the milliseconds
    GMTime = datetime.utcnow()
    # Strip millisends from input HR time
    GMTimeNoUsecs = datetime.strptime(GMTime.strftime('%Y-%m-%d %H:%M:%S'), "%Y-%m-%d %H:%M:%S")
    
    return str(GMTimeNoUsecs)


def getProfileTextFile(profileName, newlinechar="<br>"):
    # Used by the UI - returns the contents of the log file (.txt) for the specified profile.
    
    fileContents = ""
    fileName = BEE_PATH + "/logfiles/bee_" + profileName + ".txt"
    try:
        fileContents = open(fileName).read()
    except:
        return "This file does not exist!"
    return fileContents.replace("\n", newlinechar) # Replace NLs with HTML <br>


def statsEngine(action):

    import time
    
    ##    # starts, stops and checks the stats engine
    ##    shellOutput = os.popen(BEE_PATH + "/bee.sh " + action)

    shellOutput = ""
    
    # Allow only specific commands to prevent malicious command injection 
    if action in ["statcheck" , "statstop"]:
        shellOutput = os.popen(BEE_PATH + "/bee.sh " + action).read()
        # status, shellOutput = commands.getstatusoutput(BEE_PATH + "/bee.sh " + action)

    # The following is a workaround because .read() does not work with this command for some reason.
    if action == "statstart":

        # See if it's already running
        shellOutput = os.popen(BEE_PATH + "/bee.sh statcheck").read()
        if shellOutput != "running\n":

            shellOutput = os.popen(BEE_PATH + "/bee.sh statstart")

            time.sleep(1) # Pause a bit to ensure the next command works

            # check if the statstart worked correctly - and statstart is running
            shellOutput = os.popen(BEE_PATH + "/bee.sh statcheck").read()

            if shellOutput == "running\n":
                shellOutput = "started statistics engine\n" + BEE_PATH + "/backend"
            
    #import subprocess
    # shellOutput = subprocess.check_output(BEE_PATH + "/bee.sh " + action, shell=True)

    return shellOutput

def getExchangeDetails(exchangeName):
    # Given an exchangeName, returns a JSON payload of the specified exchange record. 

    import json #Import module that has the ability to encode and decode Json

    iniExchanges = json.loads(open(BEE_PATH + "/backend" + '/beeExchangeList.ini').read())

    for exchange in iniExchanges:
        if exchange["exchangeName"] == exchangeName:
            return json.dumps(exchange, sort_keys=False, indent=4)

    # If didn't find exchangeName, return error.
    return "Not found"
