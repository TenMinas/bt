# The purpose of this code is to flesh out a dictionary that starts with the trading data and adds additional columns for all the indicators

#########################################################################################
#########################################################################################
def LOL(csvfilename):
    # lol >> list of lists of the data, one list per day
    #  InColNames = ["Date", "Close/Last", "Volume", "Open", "High", "Low"]
    #  Assume file HAS a header
    import csv
    lol = []
    line = []
    with open(csvfilename,'r') as data:
        csv_reader = csv.reader(data, delimiter=',')
        for line in csv_reader:
            lol.append(line)
    return lol
#########################################################################################
#########################################################################################
def cleancsv(lol, lol_len):
# This function gets rid of "$" in the data
    x = 1

    while x < lol_len:
        row = lol[x]
        # close = row[1]
        c = 1
        while c <= 5:
            item = row[c]
            if item[0] == "$":
                row[c] = item[1:]

            c +=1

        x+=1

    return(lol)
#########################################################################################
#########################################################################################
def convert(lol, lol_len):
    # This function assumes there is a header row.  
    # The headder row will be striped before saving to yaml format
    # The function returns CSVDict with the following columns:
        # nr : n
        # R : {
        #     Date : Date 
        #     C: Close
        #     V : Volume >>> Ignoring volume for these stratigies
        #     O : Open
        #     H : High
        #     L : Low
        # }
    # Where "R" is an integer representing the row number.  The oldest data has R = 1
    
    cr = lol_len - 1

    CSVDict = {}
    r = 1
    while cr > 0:

        templist = lol[cr]

        if (templist[2] != "N/A") and (templist[2] != "n/a"):
            if (int(templist[2]) > int(1000)):

                tempdict = {"Date": templist[0], "C": float(templist[1]), "O": float(templist[3]), "H": float(templist[4]), "L": float(templist[5])}

                CSVDict[r] = tempdict

                r += 1
        cr -= 1

    CSVDict["nr"] = r - 1

    return(CSVDict)
#########################################################################################
#########################################################################################
def Ich(datadict):
    # The purpose of this function is to calculate T, K & D for each trading day
    # The function adds these three key/values to datadict:
        # T : <<< Assumes Tn = 9
        # K :
        # D :
        # TR
        # pDM1 : +DM1
        # mDM1 : -DM1
        # TR14
        # pDM14 : +DM14
        # mDM14 : -DM14
        # pDI14 : +DI14
        # mDI14 : -DI14
        # AIU : Aroon Index-Up
        # AID : Aroon Index-Down
    
    
    # TKD Loop
    cr = 26

    while cr <= datadict["nr"]:
        # T Code
        THList = []
        TLList = []
        x = cr
        while x > cr - 9:
            # print(x)
            xH = datadict[x]["H"]
            xL = datadict[x]["L"]
            THList.append(xH)
            TLList.append(xL)
            x -=1
        THH = max(THList)
        TLL = min(TLList)
        T = float(((THH + TLL)/2))
        datadict[cr]["T"] = T
    
        # K Code
        THList = []
        TLList = []
        x = cr
        while x > cr - 26:
            # print(x)
            xH = datadict[x]["H"]
            xL = datadict[x]["L"]
            THList.append(xH)
            TLList.append(xL)
            x -=1
        THH = max(THList)
        TLL = min(TLList)
        K = float(((THH + TLL)/2))
        datadict[cr]["K"] = K

        # D Code
        datadict[cr]["D"] = float((((T - K)/T)*100))

        cr += 1

    # TR DM Loop
    cr = 2

    while cr <= datadict["nr"]:
        # Pull values for TR  & Code
        Hcr = datadict[cr]["H"]
        Lcr = datadict[cr]["L"]
        Hcrm1 = datadict[cr-1]["H"]
        Lcrm1 = datadict[cr-1]["L"]
        Ccrm1 = datadict[cr-1]["C"]
        
        #TR Code
        TR = float(max((Hcr-Lcr), (abs(Hcr-Ccrm1)), (abs(Lcr-Ccrm1))))
        datadict[cr]["TR"] = float(TR)

        # pDM1 Code
        if ((Hcr - Hcrm1) > (Lcrm1 - Lcr)):
            pDM1 = max((Hcr-Hcrm1), 0.0)
        else:
            pDM1 = 0.0        
        datadict[cr]["pDM1"] = float(pDM1)

        # mDM1 Code
        if ((Lcrm1 - Lcr) > (Hcr - Hcrm1)):
            mDM1 = max((Lcrm1-Lcr), 0.0)
        else:
            mDM1 = 0.0        
        datadict[cr]["mDM1"] = float(mDM1)

        cr +=1

    # TR14 DM14 DI14 Loop
    # cr15 code for TR14 DM14 & DI14
    x = 2
    TR14 = 0
    pDM14 = 0
    mDM14 = 0
    while x <= 15:
        TR14 = TR14 + datadict[x]["TR"]
        pDM14 = pDM14 + datadict[x]["pDM1"]
        mDM14 = mDM14 + datadict[x]["mDM1"]
        
        x +=1

    datadict[15]["TR14"] = float(TR14)
    datadict[15]["pDM14"] = float(pDM14)
    datadict[15]["mDM14"] = float(mDM14)
    datadict[15]["pDI14"] = float(((pDM14/TR14)*100))
    datadict[15]["mDI14"] = float(((mDM14/TR14)*100))
    datadict[15]["ATR"] = float(TR14 / 14)
    # end cr15 code for TR14 DM14 & DI14

    # Start ATR Loop
    TTR14 = TR14
    datadict[15]["ATR"] = float(TTR14 / 14)
    for r in range(16, (datadict["nr"] + 1)):
        TTR14 = TTR14 - datadict[r-14]["TR"] + datadict[r]["TR"]
        datadict[r]["ATR"] = float(TTR14 / 14)
    # End ATR Soop

    # # cr1 - crnr code for TR14 DM14 & DI14
    cr = 16

    while cr <= datadict["nr"]:

        TR14cr = datadict[cr-1]["TR14"] - (datadict[cr-1]["TR14"] / 14) + datadict[cr]["TR"]
        pDM14cr = datadict[cr-1]["pDM14"] - (datadict[cr-1]["pDM14"] / 14) + datadict[cr]["pDM1"]
        mDM14cr = datadict[cr-1]["mDM14"] - (datadict[cr-1]["mDM14"] / 14) + datadict[cr]["mDM1"]
        pDI14cr = 100* pDM14cr / TR14cr
        mDI14cr = 100* mDM14cr / TR14cr

        datadict[cr]["TR14"] = float(TR14cr)
        datadict[cr]["pDM14"] = float(pDM14cr)
        datadict[cr]["mDM14"] = float(mDM14cr)
        datadict[cr]["pDI14"] = float(pDI14cr)
        datadict[cr]["mDI14"] = float(mDI14cr)
        datadict[cr]["dd"] = float(pDI14cr - mDI14cr)
        datadict[cr]["ATR"] = float(TR14cr / 14)
        cr +=1




    # Start AIU & AID Loop
    R = 26

    while R <= datadict["nr"]:

        #AIU Code
        Hlist25 = []
        for r in range((R - 24), (R+1)):
            Hlist25.append(datadict[r]["H"])

        adhmax = max(Hlist25)
        adih = Hlist25.index(adhmax)
        AIU = ((25 - adih)/25) * 100
        datadict[R]["AIU"] = int(AIU)

        #AID Code
        Llist25 = []
        for r in range((R - 24), (R+1)):
            Llist25.append(datadict[r]["L"])

        adlmin = min(Llist25)
        adil = Llist25.index(adlmin)
        AID = ((25 - adil)/25) * 100
        datadict[R]["AID"] = int(AID)

        AD = AID - AIU
        datadict[R]["AD"] = AD

        R +=1


    # End AIU & AID Loop

    return(datadict)
#########################################################################################
#########################################################################################
import yaml
import datetime
from datetime import datetime

def gendatadict_v3_0(full_in_csvpath, full_outpath, testconfig):

    lol = LOL(full_in_csvpath)
    lol_len = len(lol)

    if (lol_len < 26):
        print("NOT enough data for indicator calculations")
        return("ERROR")

    cleancsv(lol, lol_len)
    datadict = convert(lol, lol_len)
    datadict = Ich(datadict)
    datadict["testconfig"] = testconfig

    # Generate yaml file with all the data dictionary info

    dtstr = (datetime.now()).strftime('%Y.%m.%d_%H.%M.%S')
    fname = full_outpath + "_" + dtstr + ".yaml"
    with open(fname, 'w+') as f: 
        yaml.dump(datadict, f) 
    
    return(datadict)
#########################################################################################
#########################################################################################

