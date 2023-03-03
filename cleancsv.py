

######################################################################################
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
######################################################################################

######################################################################################
def savedata(data, fname):

    # dtstr = (datetime.now()).strftime('%Y.%m.%d_%H.%M.%S')
    # fname = fpath + dtstr + "_" + prefix + ".csv"
    with open(fname, 'w+') as f: 
        write = csv.writer(f)
        write.writerows(data)
    return(fname)

######################################################################################


import csv

csvfilename = "/home/gary/Documents/GARY_FILES/coding/fincode/csvdata/AMD_10yr.csv"

lol = LOL(csvfilename)
lol_len = len(lol)
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

savedata(lol, csvfilename)

print("done")