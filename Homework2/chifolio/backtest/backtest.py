# -*- coding: utf-8 -*-
"""
Created on Thu Nov 29 13:51:34 2018

@author: lianxb
"""
import numpy as np
import pandas as pd
from collections import OrderedDict

class Backtest(object):

    def __init__(self, returns, portfolio, cost=0):
        self.returns = returns
        self.portfolio = portfolio
        self.cost = cost
        self.account = {}
 
    def run(self):
        cost = self.cost
        ret = self.returns
        cumret = (1 + ret).cumprod()
        portfolio = self.portfolio
        calendar = ret.index.sort_values()
        
        wealth = 1
        holding = pd.Series()
        equity = pd.Series()
        position = pd.Series()
        
        wealth_dict = OrderedDict()  # account net asset value
        holding_dict = OrderedDict() # holding volume of each asset
        equity_dict = OrderedDict()  # equity value of each asset
        position_dict = OrderedDict()# position ratio of each asset
        turnover_dict = OrderedDict()
        cost_ratio_dict = OrderedDict()
        
        for i, dt in enumerate(calendar):
            p = cumret.loc[dt]
            target = portfolio.get(dt)

            # none rebalance date
            if (not holding.empty) and (target is None):
                equity = holding * p
                position = equity / equity.sum() 
                wealth = equity.sum()

                #wealth_dict[dt] = wealth
                holding_dict[dt] = holding
                equity_dict[dt] = equity
                position_dict[dt] = position
            
            # rebalance date
            if target is not None:
                # before rebalance
                equity = holding * p
                if not holding.empty:
                    wealth = equity.sum() 
                position = equity / equity.sum()

                #wealth_dict[dt] = wealth
                holding_dict[dt] = holding
                equity_dict[dt] = equity
                position_dict[dt] = position
                
                # turnover(one way)
                diff = target.sub(position, fill_value=0)
                turnover = abs(diff).sum() * 0.5
                turnover_dict[dt] = turnover

                # commission fee and slippage
                total_cost = wealth * turnover * 2 * cost
                cost_ratio_dict[dt] = total_cost / wealth
                
                holding = (wealth - total_cost) * target / p                


            wealth_dict[dt] = wealth

                                
        self.account['wealth'] = wealth_dict
        self.account['holding'] = holding_dict
        self.account['equity'] = equity_dict
        self.account['position'] = position_dict
        self.account['turnover'] = turnover_dict
        self.account['cost_ratio'] = cost_ratio_dict
 
        nav = pd.Series(wealth_dict)
        
        return nav
    
#    def run_long_short(self):
#        cost = self.cost
#        ret = self.returns
#        portfolio = self.portfolio
#        calendar = ret.index.sort_values()
#
#        wealth = 1        
#        signal = 0
#        wealth_dict = OrderedDict()  # account net asset value
#        
#        for i, dt in enumerate(calendar):
#            
#            if signal == 0:
#                wealth = wealth * (1 + 0)
#            elif signal == 1:
#                wealth = wealth * (1 + ret.loc[dt])
#            elif signal == -1:
#                wealth = wealth * (1 - ret.loc[dt])
#
#            wealth_dict[dt] = wealth
#
#            # refresh
#            newsignal = portfolio.get(dt)  
#            if newsignal is not None:
#                signal = newsignal
#
#        nav = pd.Series(wealth_dict)
#        
#        return nav
    
    def run_long_short(self):
        cost = self.cost
        ret = self.returns
        portfolio = self.portfolio
        calendar = ret.index.sort_values()

        wealth = 1        
        signal = 0
        wealth_dict = OrderedDict()  # account net asset value

        cumret = 1
        winloss = []
        
        for i, dt in enumerate(calendar):
            
            if signal == 0:
                wealth = wealth * (1 + 0)
            elif signal == 1:
                cumret = cumret * (1 + ret.loc[dt])
                wealth = wealth * (1 + ret.loc[dt])
            elif signal == -1:
                cumret = cumret * (1 - ret.loc[dt])
                wealth = wealth * (1 - ret.loc[dt])

            wealth_dict[dt] = wealth

            # refresh
            newsignal = portfolio.get(dt)  
            if newsignal is not None:
                # 开多
                if (signal == 0) & (newsignal == 1):
                    cumret = 1
                # 开空
                elif (signal == 0) & (newsignal == -1):
                    cumret = 1
                # 平多开空
                elif (signal == 1) & (newsignal == -1):
                    winloss.append(cumret)
                    cumret = 1
                # 平多
                elif (signal == 1) & (newsignal == 0):
                    winloss.append(cumret)
                # 平空开多
                elif (signal == -1) & (newsignal == 1):
                    winloss.append(cumret)
                    cumret = 1
                # 平空
                elif (signal == -1) & (newsignal == 0):
                    winloss.append(cumret)
                
                signal = newsignal           

        self.winloss = winloss
        nav = pd.Series(wealth_dict)
        
        return nav


# 返回换手率数据
class Backtest2(object):

    def __init__(self, returns, portfolio, cost=0):
        self.returns = returns
        self.portfolio = portfolio
        self.cost = cost
        self.account = {}

    def run(self):
        cost = self.cost
        ret = self.returns
        cumret = (1 + ret).cumprod()
        portfolio = self.portfolio
        calendar = ret.index.sort_values()

        wealth = 1
        holding = pd.Series()
        equity = pd.Series()
        position = pd.Series()

        wealth_dict = OrderedDict()  # account net asset value
        holding_dict = OrderedDict()  # holding volume of each asset
        equity_dict = OrderedDict()  # equity value of each asset
        position_dict = OrderedDict()  # position ratio of each asset
        turnover_dict = OrderedDict()
        cost_ratio_dict = OrderedDict()

        for i, dt in enumerate(calendar):
            p = cumret.loc[dt]
            target = portfolio.get(dt)

            # none rebalance date
            if (not holding.empty) and (target is None):
                equity = holding * p
                position = equity / equity.sum()
                wealth = equity.sum()

                # wealth_dict[dt] = wealth
                holding_dict[dt] = holding
                equity_dict[dt] = equity
                position_dict[dt] = position

            # rebalance date
            if target is not None:
                # before rebalance
                equity = holding * p
                if not holding.empty:
                    wealth = equity.sum()
                position = equity / equity.sum()

                # wealth_dict[dt] = wealth
                holding_dict[dt] = holding
                equity_dict[dt] = equity
                position_dict[dt] = position

                # turnover(one way)
                diff = target.sub(position, fill_value=0)
                turnover = abs(diff).sum() * 0.5
                turnover_dict[dt] = turnover

                # commission fee and slippage
                total_cost = wealth * turnover * 2 * cost
                cost_ratio_dict[dt] = total_cost / wealth

                holding = (wealth - total_cost) * target / p

            wealth_dict[dt] = wealth

        self.account['wealth'] = wealth_dict
        self.account['holding'] = holding_dict
        self.account['equity'] = equity_dict
        self.account['position'] = position_dict
        self.account['turnover'] = turnover_dict
        self.account['cost_ratio'] = cost_ratio_dict

        nav = pd.Series(wealth_dict)
        tvr = pd.Series(turnover_dict)

        return nav, tvr

    #    def run_long_short(trading_strategy_A_share):
    #        cost = trading_strategy_A_share.cost
    #        ret = trading_strategy_A_share.returns
    #        portfolio = trading_strategy_A_share.portfolio
    #        calendar = ret.index.sort_values()
    #
    #        wealth = 1
    #        signal = 0
    #        wealth_dict = OrderedDict()  # account net asset value
    #
    #        for i, dt in enumerate(calendar):
    #
    #            if signal == 0:
    #                wealth = wealth * (1 + 0)
    #            elif signal == 1:
    #                wealth = wealth * (1 + ret.loc[dt])
    #            elif signal == -1:
    #                wealth = wealth * (1 - ret.loc[dt])
    #
    #            wealth_dict[dt] = wealth
    #
    #            # refresh
    #            newsignal = portfolio.get(dt)
    #            if newsignal is not None:
    #                signal = newsignal
    #
    #        nav = pd.Series(wealth_dict)
    #
    #        return nav

    def run_long_short(self):
        cost = self.cost
        ret = self.returns
        portfolio = self.portfolio
        calendar = ret.index.sort_values()

        wealth = 1
        signal = 0
        wealth_dict = OrderedDict()  # account net asset value

        cumret = 1
        winloss = []

        for i, dt in enumerate(calendar):

            if signal == 0:
                wealth = wealth * (1 + 0)
            elif signal == 1:
                cumret = cumret * (1 + ret.loc[dt])
                wealth = wealth * (1 + ret.loc[dt])
            elif signal == -1:
                cumret = cumret * (1 - ret.loc[dt])
                wealth = wealth * (1 - ret.loc[dt])

            wealth_dict[dt] = wealth

            # refresh
            newsignal = portfolio.get(dt)
            if newsignal is not None:
                # 开多
                if (signal == 0) & (newsignal == 1):
                    cumret = 1
                # 开空
                elif (signal == 0) & (newsignal == -1):
                    cumret = 1
                # 平多开空
                elif (signal == 1) & (newsignal == -1):
                    winloss.append(cumret)
                    cumret = 1
                # 平多
                elif (signal == 1) & (newsignal == 0):
                    winloss.append(cumret)
                # 平空开多
                elif (signal == -1) & (newsignal == 1):
                    winloss.append(cumret)
                    cumret = 1
                # 平空
                elif (signal == -1) & (newsignal == 0):
                    winloss.append(cumret)

                signal = newsignal

        self.winloss = winloss
        nav = pd.Series(wealth_dict)

        return nav


class BacktestPlus(object):

    def __init__(self, returns, portfolio, cost=0):
        self.returns = returns
        self.portfolio = portfolio
        self.cost = cost
        self.account = {}

    def run(self):
        cost = self.cost
        ret = self.returns
        cumret = (1 + ret).cumprod()
        portfolio = self.portfolio
        calendar = ret.index.sort_values()

        wealth = 1
        holding = pd.Series()
        equity = pd.Series()
        position = pd.Series()

        wealth_dict = OrderedDict()  # account net asset value
        holding_dict = OrderedDict()  # holding volume of each asset
        equity_dict = OrderedDict()  # equity value of each asset
        position_dict = OrderedDict()  # position ratio of each asset
        turnover_dict = OrderedDict()
        leverage_dict = OrderedDict()  # leverage
        cost_ratio_dict = OrderedDict()

        # 负债项，用于处理杠杆
        liabilities = 0

        for i, dt in enumerate(calendar):
            p = cumret.loc[dt]
            target = portfolio.get(dt)

            # none rebalance date
            if (not holding.empty) and (target is None):
                equity = holding * p
                position = equity / equity.sum()
                wealth = equity.sum() - liabilities

                # wealth_dict[dt] = wealth
                holding_dict[dt] = holding
                equity_dict[dt] = equity
                position_dict[dt] = position

            # rebalance date
            if target is not None:
                # before rebalance
                equity = holding * p
                if not holding.empty:
                    wealth = equity.sum() - liabilities
                position = equity / equity.sum()

                # wealth_dict[dt] = wealth
                holding_dict[dt] = holding
                equity_dict[dt] = equity
                position_dict[dt] = position

                # turnover(one way)
                diff = target.sub(position, fill_value=0)
                turnover = abs(diff).sum() * 0.5
                turnover_dict[dt] = turnover

                # commission fee and slippage
                total_cost = wealth * turnover * 2 * cost
                cost_ratio_dict[dt] = total_cost / wealth

                holding = (wealth - total_cost) * target / p
                liabilities = (holding * p).sum() - wealth

            wealth_dict[dt] = wealth
            leverage_dict[dt] = equity.sum() / wealth  # 调仓日当天的杠杆还是旧杠杆

        self.account['wealth'] = wealth_dict
        self.account['holding'] = holding_dict
        self.account['equity'] = equity_dict
        self.account['position'] = position_dict
        self.account['turnover'] = turnover_dict
        self.account['leverage'] = leverage_dict
        self.account['cost_ratio'] = cost_ratio_dict

        nav = pd.Series(wealth_dict)

        return nav

    #    def run_long_short(trading_strategy_A_share):
    #        cost = trading_strategy_A_share.cost
    #        ret = trading_strategy_A_share.returns
    #        portfolio = trading_strategy_A_share.portfolio
    #        calendar = ret.index.sort_values()
    #
    #        wealth = 1
    #        signal = 0
    #        wealth_dict = OrderedDict()  # account net asset value
    #
    #        for i, dt in enumerate(calendar):
    #
    #            if signal == 0:
    #                wealth = wealth * (1 + 0)
    #            elif signal == 1:
    #                wealth = wealth * (1 + ret.loc[dt])
    #            elif signal == -1:
    #                wealth = wealth * (1 - ret.loc[dt])
    #
    #            wealth_dict[dt] = wealth
    #
    #            # refresh
    #            newsignal = portfolio.get(dt)
    #            if newsignal is not None:
    #                signal = newsignal
    #
    #        nav = pd.Series(wealth_dict)
    #
    #        return nav

    def run_long_short(self):
        cost = self.cost
        ret = self.returns
        portfolio = self.portfolio
        calendar = ret.index.sort_values()

        wealth = 1
        signal = 0
        wealth_dict = OrderedDict()  # account net asset value

        cumret = 1
        winloss = []

        for i, dt in enumerate(calendar):

            if signal == 0:
                wealth = wealth * (1 + 0)
            elif signal == 1:
                cumret = cumret * (1 + ret.loc[dt])
                wealth = wealth * (1 + ret.loc[dt])
            elif signal == -1:
                cumret = cumret * (1 - ret.loc[dt])
                wealth = wealth * (1 - ret.loc[dt])

            wealth_dict[dt] = wealth

            # refresh
            newsignal = portfolio.get(dt)
            if newsignal is not None:
                # 开多
                if (signal == 0) & (newsignal == 1):
                    cumret = 1
                # 开空
                elif (signal == 0) & (newsignal == -1):
                    cumret = 1
                # 平多开空
                elif (signal == 1) & (newsignal == -1):
                    winloss.append(cumret)
                    cumret = 1
                # 平多
                elif (signal == 1) & (newsignal == 0):
                    winloss.append(cumret)
                # 平空开多
                elif (signal == -1) & (newsignal == 1):
                    winloss.append(cumret)
                    cumret = 1
                # 平空
                elif (signal == -1) & (newsignal == 0):
                    winloss.append(cumret)

                signal = newsignal

        self.winloss = winloss
        nav = pd.Series(wealth_dict)

        return nav

class Backtest_new(object):

    def __init__(self, price, vwap_price, portfolio, wealth=1000000000, cost=0):
        self.price = price.fillna(method='ffill')
        self.vwap_price = vwap_price.fillna(method='ffill')
        self.portfolio = portfolio
        self.wealth = wealth
        self.cost = cost
        self.account = {}

    def run(self):
        cost = self.cost
        portfolio = self.portfolio
        wealth = self.wealth

        price = self.price
        vwap_price = self.vwap_price

        calendar = price.index.sort_values()

        holding = pd.Series()
        equity = pd.Series()
        position = pd.Series()

        wealth_dict = OrderedDict()  # account net asset value
        holding_dict = OrderedDict()  # holding volume of each asset
        equity_dict = OrderedDict()  # equity value of each asset
        position_dict = OrderedDict()  # position ratio of each asset
        turnover_dict = OrderedDict()
        cost_ratio_dict = OrderedDict()

        for i, dt in enumerate(calendar):
            p = price.loc[dt]
            vwap_p = vwap_price.loc[dt]
            target = portfolio.get(dt)

            # rebalance date
            if target is not None:
                # before rebalance
                equity = holding * vwap_p
                if not holding.empty:
                    wealth = equity.sum()
                position = equity / equity.sum()

                # turnover(one way)
                diff = target.sub(position, fill_value=0)
                turnover = abs(diff).sum() * 0.5
                turnover_dict[dt] = turnover

                # commission fee and slippage
                total_cost = wealth * turnover * 2 * cost
                cost_ratio_dict[dt] = total_cost / wealth

                holding = (wealth - total_cost) * target / vwap_p

            if not holding.empty:
                equity = holding * p
                position = equity / equity.sum()
                wealth = equity.sum()
                holding_dict[dt] = holding
                equity_dict[dt] = equity
                position_dict[dt] = position

            wealth_dict[dt] = wealth

        self.account['wealth'] = wealth_dict
        self.account['holding'] = holding_dict
        self.account['equity'] = equity_dict
        self.account['position'] = position_dict
        self.account['turnover'] = turnover_dict
        self.account['cost_ratio'] = cost_ratio_dict

        nav = pd.Series(wealth_dict)

        return nav













        
        