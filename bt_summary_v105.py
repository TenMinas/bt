########################################################################################################
########################################################################################################
def bt_summary_main(tcdata, tradedict):
    # For each config, the summary should have a number of "summary_elements (sum_elem)":
        # num_trades
        # average amount invested (price_entry * qty)
        # net
        # bal_h >>> highest balance
        # bal_l >>> lowest balance
        # mtm_h_val >>> highest mtm >>> the high mark-to-market value from in to out including the first and last day
        # mtm_l_val >>> lowest mtm >>> similar to mtmh, but the lowest value
    # Provide option to sort on any of the paramaters
    # Algorithm
        # Iterate trade by trade through the tradedict
        # Parce the data into bins 
        # Except for the data needed for the high /low balance the bins can be a simple list
        # The bin for the high /low balance has to be a dict with the key being the trade number within the config
        # after all the data is parsed, do final calculations


   
    class Config_Summary(): #Same as the "Trades Class"
        # Each config is summarized
        def __init__(self, config, net, num_trades, h_stop, ATR, n_t, n_d, h_t, sym, leverage, max_risk, sa):
 
            self.config = config
            self.num_trades = num_trades
            self.net = net
            self.h_stop = h_stop
            self.ATR = ATR
            self.n_t = n_t
            self.n_d = n_d
            self.h_t = h_t
            self.sym = sym
            self.leverage = leverage
            self.max_risk = max_risk
            self.sa = sa
            # self.s = s 
            # self.t0 = t0
            # self.td = td

        def __repr__(self):
            return "Trade('%s', %d)" % (self.config, self.net, self.num_trades, self.h_stop, self.ATR, self.n_t, self.n_d, self.h_t, self.sym, self.leverage, self.max_risk, self.sa) 
        def match(self, **kwargs):
            return all(getattr(self, key) == val for (key, val) in kwargs.items())
        def set_new_value(self, k, v):
            setattr(self, k, v)
        def get_trade_value(self, key):
            return(getattr(self, key))          

    class All_the_Configs(): # Same as the "Summary Class"
        def __init__(self):
            self.__tList = []
        def addTrade(self, config, net, num_trades, h_stop, ATR, n_t, n_d, h_t, sym, leverage, max_risk, sa): 
            self.__tList.append(Config_Summary(config, net, num_trades, h_stop, ATR, n_t, n_d, h_t, sym, leverage, max_risk, sa))
        def findTrade(self, **kwargs):
            return next(self.__iterTrade(**kwargs), None)
        def allTrades(self, **kwargs):
            return list(self.__iterTrade(**kwargs))
        def __iterTrade(self, **kwargs):
            return (trade for trade in self.__tList if trade.match(**kwargs))
        def change_value(self, c, k, v):
            tr = self.findTrade(config = c)
            tr.set_new_value(k, v)
        def sort_trade_sum(self, kw):
            from operator import attrgetter
            list_of_trades = self.allTrades()
            sorted_list = sorted(list_of_trades, key = attrgetter(kw), reverse = True)
            return(sorted_list)
        def is_trade(self, c):
            if (self.findTrade(config = c)) != None:
                return(True)
            else:
                return(False)
        def add_to_value(self, c, k, delta_value): # c=config; k=key to the value; dv = delta value
            trade = self.findTrade(config = c)
            old_value = trade.get_trade_value(k) 
            new_value = old_value + delta_value
            trade.set_new_value(k, new_value)
        def get_trade_value(self, c, k):
            tr = self.findTrade(config = c)
            return(tr.get_value(k))

    print("bt_summary line 80")
    sum_trades = All_the_Configs()

    for key, value in tradedict.items():
        tk = key # 'key' is the "tk" in the rest of the program.  It looks like 'TK' in the main

        ct = get_config_trade(key) # See comments for the function
        if ((type(ct) == list) and ((len(ct)>1))): # Screens out the non-TK data
            c =int(ct[0])
            t = int(ct[1])
            ct = [c, t]

        # screening code
            if "exit_cond" in tradedict[tk]:
                out_code = tradedict[tk]["exit_cond"].get("out_code")
                qty = tradedict[tk].get("qty")
                if (out_code != None) and (out_code != "cancel_enter") and (qty != None) and ((abs(qty)) > 0): # screens out the non-trade data

                    if sum_trades.is_trade(ct[0]) == False:
                        sum_trades.addTrade(ct[0], 0, 0, 0, 0, 0, 0, 0, "sym", 0, 0, "sa")

                    # Code for number of trades which will be used in other calcs
                    sum_trades.add_to_value(ct[0], "num_trades", 1) 


        # Code for net
            # Get the data
            if "net" in tradedict[tk]:
                net = tradedict[tk].get("net")
            # if (net != None): # validate the data
                # print(tcdata[(ct[0])].get("h_ees"))
                sum_trades.add_to_value(ct[0], "net", round(net)) #Sum gains  & losses
                sum_trades.change_value(ct[0], "h_stop", round(tcdata[ct[0]].get("h_stop"), 2))
                sum_trades.change_value(ct[0], "n_t", tcdata[ct[0]].get("n_t"))
                sum_trades.change_value(ct[0], "n_d", tcdata[ct[0]].get("n_d"))                
                sum_trades.change_value(ct[0], "h_t", round(tcdata[ct[0]].get("h_t"), 4))
                sum_trades.change_value(ct[0], "sym", tcdata[ct[0]].get("sym"))
                sum_trades.change_value(ct[0], "leverage", tcdata[ct[0]].get("future_leverage"))
                sum_trades.change_value(ct[0], "max_risk", tcdata[ct[0]].get("max_risk"))
                sum_trades.change_value(ct[0], "sa", tcdata[ct[0]].get("sa"))
                # sum_trades.change_value(ct[0], "ATR", tcdata[ct[0]].get("ATR"))
                # sum_trades.change_value(ct[0], "t0", tcdata[ct[0]].get("t0"))
                # sum_trades.change_value(ct[0], "td", tcdata[ct[0]].get("td"))
                # sum_trades.change_value(ct[0], "s", tcdata[ct[0]].get("s"))                

    sorted_summary = sum_trades.sort_trade_sum("net")


    sym = tcdata[0]["sym"]
    save_sum_trades(sorted_summary, sym)

    # return(sorted_summary)


########################################################################################################
########################################################################################################


########################################################################################################
########################################################################################################
def get_config_trade(ct_string):
    # Given a string tk;
    # This function gets the config number and the trade number
    # And returns a list of two items
    ct_string = str(ct_string)
    separator = "-"
    ct_list = ct_string.rsplit(separator)

    return(ct_list)


########################################################################################################
########################################################################################################
def save_sum_trades(sum_trades, sym):
    import datetime
    from datetime import datetime
    import yaml
    import os

    btpath = "/home/gary/coding/fincode/btresults/"
    filename = "Summary"

    dtstr = (datetime.now()).strftime('%Y.%m.%d_%H.%M.%S')
    fname = btpath + filename + "_" + sym + "_" + dtstr + ".yaml"

    print("preparing Analyzed file")

    with open(fname, 'w') as f: 
        yaml.dump(sum_trades, f)

    print("Analysis Complete")
########################################################################################################
########################################################################################################
import yaml
def btsm():

    tcdata_path = "/home/gary/coding/fincode/btresults/tcdata_2022.02.19_17.42.32.yaml"
    Trade_Results_path = "/home/gary/coding/fincode/btresults/Trade_Results_2022.02.19_17.42.32.yaml"

    with open(tcdata_path, 'r') as f:
        tcdata = yaml.safe_load(f)

    with open(Trade_Results_path, 'r') as f:
        tradedict = yaml.safe_load(f)

    bt_summary_main(tcdata, tradedict)
#########################################################################################
#########################################################################################
if __name__ == "__main__":
    btsm()


