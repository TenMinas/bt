########################################################################################################
########################################################################################################
def config(btconfig):
    # from gentestconfig_v105 import getlistdata, marketcheck

    tcdata = {}
    config = 0
    tempdict = {}

    sym = btconfig["testsyms"][0]
    salist = getlistdata(btconfig, "sa")
    # relist = getlistdata(btconfig, "rev")

    n_t_min = btconfig["n_t"]["min_range"]
    n_t_max = btconfig["n_t"]["max_range"]
    n_t_inc = btconfig["n_t"]["inc"]

    n_d_min = btconfig["n_d"]["min_range"]
    n_d_max = btconfig["n_d"]["max_range"]
    n_d_inc = btconfig["n_d"]["inc"]

    h_t_min = btconfig["h_t"]["min_range"]
    h_t_max = btconfig["h_t"]["max_range"]
    h_t_inc = btconfig["h_t"]["inc"]

    h_stop_min = btconfig["h_stop"]["min_range"]
    h_stop_max = btconfig["h_stop"]["max_range"]
    h_stop_inc = btconfig["h_stop"]["inc"]

    strat = btconfig["strat"]
    btconfig_ver = btconfig["btconfig_ver"]


    for s in range(len(salist)):
        # for r in range(len(relist)):

        for nt in range(n_t_min, n_t_max + n_t_inc, n_t_inc):

            for nd in range(n_d_min, n_d_max + n_d_inc, n_d_inc):
                h_t = h_t_min
                while h_t <= h_t_max + h_t_inc:
                    h_stop = h_stop_min
                    while h_stop <= h_stop_max + h_stop_inc:

                        market = marketcheck(btconfig, sym)
                        if market == "stocks":
                            max_risk = btconfig["max_risk"]["stocks"]
                            future_leverage = "n/a"

                        elif market == "futures":
                            max_risk = btconfig["max_risk"]["futures"]
                            future_leverage = btconfig["futuresyms"][sym]

                        else: raise Exception("error - gentestconfig") 

                        tempdict = {"sym" : sym, "market" : market, "future_leverage" : future_leverage, "strat" : strat,"max_risk" : max_risk, "sa" : salist[s], "re" : salist[s], "n_t" : nt, "h_t" : h_t, "h_stop" : h_stop, "btconfig_ver" : btconfig_ver, "n_d" : nd}

                        tcdata.update({config : tempdict})

                        config +=1

                        h_stop = h_stop + h_stop_inc
                    h_t = h_t + h_t_inc
            
    return(tcdata)

#########################################################################################
#########################################################################################
def marketcheck(btconfig, sym):
    for ss in btconfig["stocksyms"]:
        if ss == sym:
            return("stocks")
        else:
            for fs in btconfig["futuresyms"]:
                if fs == sym:
                    return("futures")

    return("error")
#########################################################################################
#########################################################################################
def getlistdata(btconfig, ind):
    paramlist = []
    tempind = btconfig[ind]
    if type(tempind) == list:
        paramindex = len(tempind)
        for pi in range(paramindex):
            paramlist.append(tempind[pi])

    return(paramlist)
#########################################################################################
#########################################################################################

def gentestconfig():
    import datetime
    import os
    from datetime import datetime
    import yaml
    from get_stratigies_v105 import run_btconfig_ver

    global btconfig
    # btpath = ((os.path.dirname(__file__)) + "/")
    btfullpath = run_btconfig_ver()


    with open(btfullpath, 'r') as f:
        btconfig = yaml.safe_load(f)

    full_outpath = (os.path.dirname(__file__)) + "/" + btconfig["paths"]["testconfigurations"]

    tcdata = config(btconfig)

    filename = "tcdata"
    sym = btconfig["testsyms"][0]

    dtstr = (datetime.now()).strftime('%Y.%m.%d_%H.%M.%S')

    fname = full_outpath + filename + "_" + sym +  "_"  + dtstr + ".yaml"

    with open(fname, 'w') as f: 
        yaml.dump(tcdata, f)

    print("Gen Test Cond - Done")

    return(tcdata) 


#########################################################################################
#########################################################################################
if __name__ == "__main__":
    gentestconfig()