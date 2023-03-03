#########################################################################
#########################################################################

# This code assumes only one strat and one sym per run


#########################################################################
#########################################################################
def run_strat_ene(datadict, configdict, tradedict, P):

    from strat_v105 import strat

    return(strat(datadict, configdict, tradedict, P)) 


#########################################################################
#########################################################################
def run_btconfig_ver():
    import os

    btconfig_ver = "105"

    btpath = ((os.path.dirname(__file__)) + "/")

    return(btpath + "btconfig_v" + btconfig_ver + ".yaml")

#########################################################################
#########################################################################
def run_stoploss_signal(datadict, configdict, tradedict, P):

    from strat_v105 import stoploss_signal

    return(stoploss_signal(datadict, configdict, tradedict, P))

#########################################################################
#########################################################################
def run_enter_strat(datadict, configdict, tradedict, enter_cond):

    from strat_v105 import enter_strat 

    return(enter_strat(datadict, configdict, tradedict, enter_cond))

#########################################################################
#########################################################################
def run_exit_strat(configdict, tradedict, exit_cond):

    from strat_v105 import exit_strat 

    return(exit_strat(configdict, tradedict, exit_cond))

#########################################################################
#########################################################################
def run_flatten(datadict, configdict, tradedict, P):

    from strat_v105 import flatten 

    return(flatten(datadict, configdict, tradedict, P))

#########################################################################
#########################################################################
def run_mtm(configdict, tradedict, datadict, P):

    from strat_v105 import mtm 

    return(mtm(configdict, tradedict, datadict, P))

#########################################################################
#########################################################################
def run_bt_summary_main(tcdata, tradedict):

    from bt_summary_v105 import bt_summary_main 

    return(bt_summary_main(tcdata, tradedict))

#########################################################################
#########################################################################
