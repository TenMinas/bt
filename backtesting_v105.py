
########################################################################################################
########################################################################################################
def trade_loop(datadict, btconfig, tcdata, tradedict):
    from get_stratigies_v105 import run_flatten, run_mtm

    configdict = {}
    nr = datadict["nr"]
    tk = "" # tk >> trade key

    P_offset = btconfig["P_offset"]

    ##########################################

    cc = 0 # cc >>> config counter

    # tradedict["trade_key"] = "" # This dict stores the trade_key
    for cc in range(len(tcdata)): # cc is the config counter
        configdict = tcdata[cc] # {"sym", "market", "strat", "sa", "re", "n_ST", h_ST, "h_P"}
        configdict["cc"] = cc


        tradedict["trade_num"] = 0 # This is reset for each config

        # tradedict["trade_key"] = str(cc) + "-" + "0" # Need to initilize to trade '0' prior to going thru the test data
        tk = str(cc) + "-" + "0"
        tradedict["tk"] = tk
        tradedict[tk] = {"pos" : "out"} # Need to start with this state
        tradedict[tk].update({"sym" : configdict["sym"]})

        for P in range((P_offset), (nr+1)):
            csl = False  # Check-Stop-Loss flag

            tk = tradedict["tk"]

            pos = tradedict[tk]["pos"]
            if (pos != "out"):
                run_mtm(configdict, tradedict, datadict, P) # End of Day - Mark to market
                csl = check_stoploss(tradedict, configdict, datadict, P) # Checking for Stoploss and exits the trade if the stop was hit

            if not csl:
                td_n_te(datadict, P, tradedict, configdict) #Trade decision and Trade Execution

            tk = tradedict["tk"]

            print("tk:", tk, " P:", P)

        # This flatten is at the end of the data for each config
        run_flatten(datadict, configdict, tradedict, P)




########################################################################################################
########################################################################################################
def TP4(datadict, P, ab):
    H = datadict[P]["H"]
    L = datadict[P]["L"]
    C = datadict[P]["C"]

    if ab == "ask":
        # return(((H + C)/2)) # Price for me to buy (ask)
        return(H) # Using worst case
    # else: return(((L + C)/2)) # Price for me to sell (bid)
    else: return (L) # Using worst case
########################################################################################################
########################################################################################################
def cancel_enter(f_risk, max_risk, tradedict):
    # This code is cancel entering if the risk is too high

    tk = tradedict["tk"]
    exit_cond = {"out_code" : "cancel_enter", "note" : ("futures risk ${} > max_risk ${}".format(round(f_risk), max_risk))}

    tradedict[tk].update({"qty" : 0})
    tradedict[tk]["pos"] = "out"
    tradedict[tk]["exit_cond"] = exit_cond

########################################################################################################
########################################################################################################

def check_stoploss(tradedict, configdict, datadict, P):
    from get_stratigies_v105 import run_stoploss_signal

    slp_dict = run_stoploss_signal(datadict, configdict, tradedict, P)

    sl_signal = slp_dict["sl_signal"]
    price_stop = slp_dict["price_stop"]

    if sl_signal == "exit":

        exit_cond = {"price_exit" : price_stop, "s_data" : "n/a", "Rule_#" : "n/a", "P_exit" : P, "Date" : datadict[P]["Date"], "out_code" : "stop"}
        exit_main(configdict, tradedict, exit_cond) # If need to close, pass control to Exit
        return(True)

    else: return(False)   # Return if don't need to close


########################################################################################################
########################################################################################################
def exit_main(configdict, tradedict, exit_cond):

    from get_stratigies_v105 import run_exit_strat 

    run_exit_strat(configdict, tradedict, exit_cond)    

########################################################################################################
########################################################################################################

def td_n_te(datadict, P, tradedict, configdict):
    # Merged the Trade decision and Trade Execution functions
    # There should be one or two trades executed.  
    # sig >>> signal from strategies
    # See backtesting_v7_7.py for the rest of the comments
    # tk_td_n_te = tradedict["trade_key"]
    # enter_cond: A dict w/ npos, price_enter, Rule #, P_enter, s_data; saved to tradedict by enter function

    from get_stratigies_v105 import run_strat_ene, run_enter_strat

    tk = tradedict["tk"]
    strat_dict = run_strat_ene(datadict, configdict, tradedict, P)
    signal = strat_dict["signal"]
    if signal == "hold":
        return()

    out_code = strat_dict["out_code"]
    s_data = strat_dict["strat_data"] #This is the data from the ene strategy function
    g_ng = "go"
    pos = tradedict[tk]["pos"]
    sa = configdict["sa"]
    re = configdict["re"]


    if ((signal == "sell") and (pos == "out") and (sa == False)):  # Rule #0
        return()

    elif ((signal == "buy") and (pos == "long")):  # Rule #0
        return()

    elif (signal == "sell") and (pos == "short"):  # Rule #0
        return()

    elif ((signal == "buy") and (pos == "out")):  # Rule #1 - Enter
        tradeprice  = TP4(datadict, P, "ask")
        enter_cond = {"npos" : "long", "price_enter" : tradeprice, "s_data" : s_data, "Rule_#" : "Rule 1", "P_enter" : P, "Date" : datadict[P]["Date"]}
        g_ng = run_enter_strat(datadict, configdict, tradedict, enter_cond)

    elif ((signal == "buy") and (pos == "short" and re == True)): # Rule #2 - Exit & reenter
        tradeprice  = TP4(datadict, P, "ask")
        exit_cond = {"price_exit" : tradeprice, "s_data" : s_data, "Rule_#" : "Rule 2a", "P_exit" : P, "Date" : datadict[P]["Date"], "out_code" : out_code}
        exit_main(configdict, tradedict, exit_cond)

        # Reenter at the same price
        enter_cond = {"npos" : "long", "price_enter" : tradeprice, "s_data" : s_data, "Rule_#" : "Rule 2b", "P_enter" : P, "Date" : datadict[P]["Date"]}
        g_ng = run_enter_strat(datadict, configdict, tradedict, enter_cond)

    elif ((signal == "buy") and (pos == "short" and re == False)):  # Rule #3
        tradeprice  = TP4(datadict, P, "ask")
        exit_cond = {"price_exit" : tradeprice, "s_data" : s_data, "Rule_#" : "Rule 3", "P_exit" : P, "Date" : datadict[P]["Date"], "out_code" : out_code}
        exit_main(configdict, tradedict, exit_cond)

    elif ((signal == "sell") and (pos == "long") and (sa == True) and (re == True)):  # Rule #4
        tradeprice  = TP4(datadict, P, "bid")
        exit_cond = {"price_exit" : tradeprice, "s_data" : s_data, "Rule_#" : "Rule 4a", "P_exit" : P, "Date" : datadict[P]["Date"], "out_code" : out_code}
        exit_main(configdict, tradedict, exit_cond)

        enter_cond = {"npos" : "short", "price_enter" : tradeprice, "s_data" : s_data, "Rule_#" : "Rule 4b", "P_enter" : P, "Date" : datadict[P]["Date"]}
        g_ng = run_enter_strat(datadict, configdict, tradedict, enter_cond)

    elif ((signal == "sell") and (pos == "long") and ( sa == True) and (re == False)):  # Rule #5
        tradeprice  = TP4(datadict, P, "bid")
        exit_cond = {"price_exit" : tradeprice, "s_data" : s_data, "Rule_#" : "Rule 5", "P_exit" : P, "Date" : datadict[P]["Date"], "out_code" : out_code}
        exit_main(configdict, tradedict, exit_cond)

    elif ((signal == "sell") and (pos == "long") and ( sa == False)):  # Rule #6
        tradeprice  = TP4(datadict, P, "bid")
        exit_cond = {"price_exit" : tradeprice, "s_data" : s_data, "Rule_#" : "Rule 6", "P_exit" : P, "Date" : datadict[P]["Date"], "out_code" : out_code}
        exit_main(configdict, tradedict, exit_cond)

    elif ((signal == "sell") and (pos == "out") and ( sa == True)):  # Rule #7
        tradeprice  = TP4(datadict, P, "bid")
        enter_cond = {"npos" : "short", "price_enter" : tradeprice, "s_data" : s_data, "Rule_#" : "Rule 7", "P_enter" : P, "Date" : datadict[P]["Date"]}
        g_ng = run_enter_strat(datadict, configdict, tradedict, enter_cond)

    # elif ((signal == "buy") and (pos == "long")):  # Rule #8 - Enter
    #     tradeprice  = TP4(datadict, P, "ask")
    #     enter_cond = {"npos" : "long", "price_enter" : tradeprice, "s_data" : s_data, "Rule_#" : "Rule 8", "P_enter" : P, "Date" : datadict[P]["Date"]}
    #     g_ng = run_enter_strat(datadict, configdict, tradedict, enter_cond)

    # elif ((signal == "sell") and (pos == "short") and ( sa == True)):  # Rule #9
    #     tradeprice  = TP4(datadict, P, "bid")
    #     exit_cond = {"price_exit" : tradeprice, "s_data" : s_data, "Rule_#" : "Rule 9", "P_exit" : P, "Date" : datadict[P]["Date"], "out_code" : out_code}
    #     exit_main(configdict, tradedict, P, exit_cond)

    else: raise Exception("error - td_n_te")   

    if g_ng[0] == "nogo":
        cancel_enter(g_ng[1], g_ng[2], tradedict)

########################################################################################################
########################################################################################################
def btmain():
    import datetime
    from datetime import datetime
    import yaml
    import os
    # import csv
    from get_stratigies_v105 import run_btconfig_ver
    from GenDataDict_v3_0 import gendatadict_v3_0
    from gentestconfig_v105 import gentestconfig


    btpath = ((os.path.dirname(__file__)) + "/")
    btfullpath = run_btconfig_ver()

    with open(btfullpath, 'r') as f:
        btconfig = yaml.safe_load(f)

    sym = btconfig["testsyms"][0]

    csvfilename = sym + ".csv" # The gendatadict function needs to know what data to use
    full_in_csvpath = btpath + btconfig["paths"]["csvdatapath"] + csvfilename
    tdfull_outpath = btpath + btconfig["paths"]["testdata"] + csvfilename
    

    tcdata = gentestconfig()
        # This will be generated by some code and copied to the various files
        # The various stratigies will iterated through the configuration parameters


    datadict = gendatadict_v3_0(full_in_csvpath, tdfull_outpath, tcdata)


    if datadict == "ERROR":
        return("ERROR - Not enough data")

    tradedict = {}
    # tradedict["testconfig"] = tcdata # Adds the configuration info to the Trade Results file


    trade_loop(datadict, btconfig, tcdata, tradedict)
    print("Done with trade loop for ", sym)


############################
# Save the tradedict to disk
############################
    filename = "TR"

    dtstr = (datetime.now()).strftime('%Y.%m.%d_%H.%M.%S')
    results_full_outpath = btpath + btconfig["paths"]["resultpath"]
    fname = results_full_outpath + filename + "_" + sym + "_" + dtstr + ".yaml"

    print("preparing Trade_Results file")

    with open(fname, 'w') as f: 
        yaml.dump(tradedict, f)

    print("Trade_Results Saved")

############################
# Execute the summary app
############################
    from get_stratigies_v105 import run_bt_summary_main
    print(256, "start bt_summary")
    run_bt_summary_main(tcdata, tradedict)
    print(258, "end bt_summary")
    # trade_summary = summary_results[0]
    # net_avg_sorted_dict = summary_results[1]
    # net_avg_sorted_dict.update({"btconfig" : btconfig})

############################
# Save the net_avg_sorted_dict to disk
############################
    # filename = "net_avg"
    # nasd = net_avg_sorted_dict

    # dtstr = (datetime.now()).strftime('%Y.%m.%d_%H.%M.%S')
    # results_full_outpath = btpath + btconfig["paths"]["resultpath"]
    # fname = results_full_outpath + filename + "_" + dtstr + ".yaml"
    # cfname = results_full_outpath + filename + "_" + dtstr + ".csv"

    # with open(fname, 'w') as f: 
    #     yaml.dump(net_avg_sorted_dict, f)

    # with open(cfname, mode='w') as csv_file:
    #     fieldnames = ['config', "net_avg", "net_sum", "num_trades", "n_ees", 'h_ees', "sym", 'leverage', "risk", "sa_re"]
    #     writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    #     writer.writeheader()

    #     for config in range(len(nasd)):
    #         net_avg = nasd[config]["net_avg"]
    #         net_sum = nasd[config]["net_sum"]
    #         num_trades = nasd[config]["num_trades"]
    #         n_ees = nasd[config]["n_ees"]
    #         h_ees = nasd[config]["h_ees"]
    #         csym = nasd[config]["sym"]  
    #         leverage = nasd[config]["leverage"]    
    #         risk = nasd[config]["risk"]    
    #         sa_re = nasd[config]["sa_re"]                                                  

    #         writer.writerow({'config': config, "net_avg" : net_avg, "net_sum" : net_sum, "num_trades" : num_trades, "n_ees" : n_ees, "h_ees" : h_ees, "sym" : csym, 'leverage': leverage, "risk" : risk, "sa_re" : sa_re})

############################
# Save the trade_summary to disk
############################
    # filename = "trade_summary"

    # dtstr = (datetime.now()).strftime('%Y.%m.%d_%H.%M.%S')
    # results_full_outpath = btpath + btconfig["paths"]["resultpath"]
    # fname = results_full_outpath + filename + "_" + dtstr + ".yaml"

    # with open(fname, 'w') as f: 
    #     yaml.dump(trade_summary, f)

############################
# All Done
############################    
    return("! Finished btmain !")

print(btmain())
########################################################################################################
########################################################################################################

