########################################################################################################
########################################################################################################
def strat(datadict, configdict, tradedict, P):

    atr = round(datadict[P]["ATR"], 4)

    # tk = tradedict["tk"]


    strat_dict = {}

    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # ees test condition definitions
    a_st = configdict["a_st"]
    b_st = configdict["b_st"]
    a_lt = configdict["a_lt"]
    b_lt = configdict["b_lt"]
    h_st = configdict["h_st"]
    h_lt = configdict["h_lt"]

    sa = configdict["sa"]

    # Calculate t0 values

    # t0_hl_list = hl_np(datadict, P, (n_t))
    t0_hl_list = hl_np(datadict, P-1, (n_t)) # (P-1) so the trade is day after signal
    t0h = t0_hl_list[0]
    t0l = t0_hl_list[1]
    t0 = (t0h + t0l)/2

    # td_hl_list = hl_np(datadict, P-n_d, (n_t))
    td_hl_list = hl_np(datadict, P-n_d-1, (n_t)) # (P-n_d-1) so the trade is day after signal
    tdh = td_hl_list[0]
    tdl = td_hl_list[1]  
    td = (tdh + tdl)/2

    s = t0 - td

    # Determine entry / exit signal based only on test conditions
    if s > (t0 * h_t):
        signal = "buy"

    elif s < -(t0 * h_t):
        signal = "sell"

    else: signal = "hold"



    ###################################

    # Return all the applicable data  

    strat_dict.update({"signal" : signal, "out_code" : "strat", "strat_data" : {"t0" : t0, "td" : td, "ATR" : atr, "s" : s, "h_t" : h_t, "sa" : sa, "n_t" : n_t, "n_d" : n_d}}) 

    return(strat_dict)   

########################################################################################################
########################################################################################################
def calc_s(datadict, row, a, b):
        # t0_hl_list = hl_np(datadict, P, (n_t))
    t0_hl_list = hl_np(datadict, P-1, (n_t)) # (P-1) so the trade is day after signal
    t0h = t0_hl_list[0]
    t0l = t0_hl_list[1]
    t0 = (t0h + t0l)/2

    # td_hl_list = hl_np(datadict, P-n_d, (n_t))
    td_hl_list = hl_np(datadict, P-n_d-1, (n_t)) # (P-n_d-1) so the trade is day after signal
    tdh = td_hl_list[0]
    tdl = td_hl_list[1]  
    td = (tdh + tdl)/2

    return(t0 - td)


########################################################################################################
########################################################################################################
def hl_np(datadict, row, n):

    HList = []
    LList = []

    x = row

    while x > row - n:
        xH = datadict[x]["H"]
        xL = datadict[x]["L"]
        HList.append(xH)
        LList.append(xL)
        x -=1
    
    return(max(HList), min(LList))

########################################################################################################
########################################################################################################

def enter_strat(datadict, configdict, tradedict, enter_cond): 
    # Called by and returns to backtesting_vxxx >> td_n_te

    npos = enter_cond["npos"]
    P = enter_cond["P_enter"]
    price_enter = enter_cond["price_enter"]

    tradedict["trade_num"] +=1
    tk = str(configdict["cc"]) + "-" + str(tradedict["trade_num"])
    tradedict["tk"] = tk
    tradedict.update({tk : {}})    
    # tradedict[tk].update({"enter_cond" : enter_cond})
    tradedict[tk]["enter_cond"] = enter_cond
    tradedict[tk]["pos"] = npos
    tradedict[tk]["qty"] = 0
    # tradedict[tk].update({"qty" : 0})

    #Initialize m2m if necessary
    if "m2m" not in tradedict[tk]:
        tradedict[tk].update({"m2m" : []})

    # Initialize sign
    if npos == "long":
        qty_sign = 1
    elif npos == "short":
        qty_sign = -1
    else: raise Exception("error - qty_enter - qty_sign")

    price_stop = get_stop_price(datadict, configdict, tradedict, P)

    if configdict["market"] == "stocks":
        num_shares = numshares(configdict, npos, price_enter, price_stop)
        qty = qty_sign * num_shares
        tradedict[tk]["qty"] = qty

        return("go")

    elif (configdict["market"] == "futures"):
        # For futures: need to approve or veto the entry based on risk
        max_risk = configdict["max_risk"]
        lever = configdict["future_leverage"]
        # The stop was set based on H or L. Now it is set based on price_enter just like the risk assessment
        f_risk = round(abs(price_enter - price_stop) * lever)

        if (f_risk) < max_risk:
            qty = qty_sign
            tradedict[tk]["qty"] = qty
            return("go")
        else: return("nogo", f_risk, max_risk)

    else: raise Exception("error - enter-risk")  
########################################################################################################
########################################################################################################
def exit_strat(configdict, tradedict, exit_cond):
    tk = tradedict["tk"]

    price_exit = exit_cond["price_exit"]
    qty = tradedict[tk]["qty"]
    price_enter = tradedict[tk]["enter_cond"]["price_enter"]

    net_pre = (price_exit - price_enter) * qty

    # Set exit data
    tradedict[tk]["exit_cond"] = exit_cond
    tradedict[tk]["pos"] = "out"

    if configdict["market"] == "stocks":
        tradedict[tk]["net"] = net_pre

    elif (configdict["market"] == "futures"):
        lever = configdict["future_leverage"]
        tradedict[tk]["net"] = (net_pre * lever)        

    else: raise Exception("error - exit")  


########################################################################################################
########################################################################################################
def mtm(configdict, tradedict, datadict, P):
    # Saves an end-of-day mark-to-market for both futures and stocks
    # This will facilitate how far the price deviates from the entry and exit
    # This function assumes there is an open trade, (i.e. pos != out)
    tk = tradedict["tk"]
    if "m2m" not in tradedict[tk]:
        return()

    qty = tradedict[tk]["qty"]
    price_today = datadict[P]["C"]
    price_enter = tradedict[tk]["enter_cond"]["price_enter"]
    m2m_pre = ((price_today - price_enter) * qty)

    if  configdict["market"] == "stocks":
        m2m = m2m_pre

    elif (configdict["market"] == "futures"):
        lever = configdict["future_leverage"]
        m2m = (m2m_pre * lever)       

    tradedict[tk]["m2m"].append({P : round(m2m)})

########################################################################################################
########################################################################################################
def flatten(datadict, configdict, tradedict, P):
    # At the end of all the data, any open trade will be flattend using the last day's close

    tk = tradedict["tk"]
    if "qty" in tradedict[tk]:
        qty = tradedict[tk]["qty"]
        pos = tradedict[tk]["pos"]
        if (qty == 0) or (pos == "out"):
            return()
        else:
            price_exit = datadict[P]["C"]

            exit_cond = {"price_exit" : price_exit, "P_exit" : P, "Date" : datadict[P]["Date"], "out_code" : "flatten"}

            exit_strat(configdict, tradedict, exit_cond)
    
            return()

    else: return()

########################################################################################################
########################################################################################################
def numshares(configdict, npos, price_enter, price_stop):
 # This function assumes it will only be called if the market == stocks

    risk_max = configdict["max_risk"]

    if npos == "long":
        if (price_enter - price_stop) == 0:
            return(int(0))
        else: return(int(risk_max / (price_enter - price_stop)))

    elif npos == "short":
        if (price_stop- price_enter) == 0:
            return(int(0))
        else: return(int((risk_max / (price_stop - price_enter))))

    else: raise Exception("error - numshares")


########################################################################################################
########################################################################################################
def get_stop_price(datadict, configdict, tradedict, P):

    tk = tradedict["tk"]

    if "price_stop" in tradedict[tk]:
        return(tradedict[tk]["price_stop"])
    else: return(calculate_stop_price(datadict, configdict, tradedict, P))

    ##################################################
def calculate_stop_price(datadict, configdict, tradedict, P):
    tk = tradedict["tk"]
    pos = tradedict[tk]["pos"]
    # H = datadict[P]["H"]
    # L = datadict[P]["L"]
    price_enter = tradedict[tk]["enter_cond"]["price_enter"]


    atr = datadict[P]["ATR"]
    h_stop = configdict["h_stop"]

    price_delta = (h_stop * atr)

    if pos == "long":
        tradedict[tk]["price_stop"] = (price_enter - price_delta)

    elif pos == "short":
        tradedict[tk]["price_stop"] = (price_enter + price_delta)

    else: raise Exception("error - calculate_stop_price")

    return(tradedict[tk]["price_stop"])

########################################################################################################
########################################################################################################
def stoploss_signal(datadict, configdict, tradedict, P):
    # The stop loss is NOT the primary means of exiting a trade. This should only be hit if the market does something really bad

    # Initialize stuff
    tk = tradedict["tk"]
    pos = tradedict[tk]["pos"]
    H = datadict[P]["H"]
    L = datadict[P]["L"]

    price_stop = get_stop_price(datadict, configdict, tradedict, P)

    # Compare with today's H / L and return signal indicating need to close
    if pos == "long":
        if L < price_stop:
            sl_signal = "exit"

        else: sl_signal = "hold"
    
    elif pos == "short": 
        if H > price_stop:
            sl_signal = "exit"

        else: sl_signal = "hold"
    
    else: sl_signal = "hold"

    slp_dict = {"sl_signal" : sl_signal, "price_stop" : price_stop}

    return(slp_dict)

########################################################################################################
########################################################################################################