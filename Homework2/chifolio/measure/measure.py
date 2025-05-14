# -*- coding: utf-8 -*-
"""
Created on Tue Dec  4 16:27:44 2018

@author: Administrator
"""

import pandas as pd
import statsmodels.api as sm
from collections import OrderedDict
from statsmodels.tsa.arima_model import ARMA

ANNUAL_FACTOR = {'monthly':12, 
                 'weekly': 52, 
                 'daily': 252}

class Measure(object):
    
    # -----------description-------------
    @classmethod
    def describe(cls, returns):  
        res = returns.describe()
        res['skew'] = returns.skew()
        res['kurtosis'] = returns.kurtosis()
        res['start'] = returns.index.min().strftime('%Y%m%d')
        res['end'] = returns.index.max().strftime('%Y%m%d')
        return res

    # -----------return related-------------
    @classmethod
    def cal_cagr(cls, returns, period='daily'):
        annual_factor = ANNUAL_FACTOR[period]
        num_years = len(returns) / annual_factor
        cum_ret = (1 + returns).cumprod()
        res = (cum_ret.iloc[-1]) ** (1 / num_years) - 1
        return res
    
    @classmethod    
    def cal_cumret(cls, returns):
        cum_ret = (1 + returns).cumprod()
        res = cum_ret.iloc[-1] - 1
        return res
    
    @classmethod
    def cal_aar(cls, returns, period='daily'):
        annual_factor = ANNUAL_FACTOR[period]
        average_ret = returns.mean()
        res = average_ret * annual_factor
        return res
    
    @classmethod
    def cal_alpha(cls, returns, bm_returns, risk_free=0, period='daily'):
        annual_factor = ANNUAL_FACTOR[period]
        y = returns - risk_free
        x = bm_returns - risk_free
        # need not add constant
        alpha =sm.OLS(y, x).fit().resid
        res = alpha.mean() * annual_factor
        return res
    
    @classmethod
    def cal_max_min_monthly_return(cls, returns, period='daily'):
        if period in ('daily', 'weekly'):
            monthly_return = (1 + returns).cumprod(
                    ).resample('M').last().pct_change()
        elif period == 'monthly':
            monthly_return = returns
        
        res = (monthly_return.max(), monthly_return.min())
        return res
        
    # -----------risk related-------------   
    @classmethod
    def cal_standard_deviation(cls, returns, period='daily'):
        annual_factor = ANNUAL_FACTOR[period]
        res = returns.std() * pd.np.sqrt(annual_factor)
        return res

    @classmethod
    def cal_downside_deviation(cls, returns, mar=0, period='daily'):
        """mar:vMinimum Acceptable Return
        """
        annual_factor = ANNUAL_FACTOR[period]
        returns_adj = returns - mar
        mask = returns_adj > 0
        returns_adj[mask] = 0
        square = returns_adj ** 2
        square_mean = square.sum() / len(square)
        res = pd.np.sqrt(square_mean * annual_factor)
        return res
    
    @classmethod
    def cal_marketbeta(cls, returns, bm_returns, risk_free=0):
        y = returns - risk_free
        x = bm_returns - risk_free
        res = sm.OLS(y, x).fit().params[0]
        return res
    
    @classmethod
    def cal_drawdown(cls, returns):
        cum_ret = (1 + returns).cumprod()
        drawdown = OrderedDict()
        for dt in cum_ret.index:
            drawdown[dt] = (cum_ret.loc[dt] - cum_ret.loc[:dt].max()) / (cum_ret.loc[:dt].max())
        res = pd.Series(drawdown)
        return res

    @classmethod
    def cal_max_drawdown(cls, returns):
        drawdown = cls.cal_drawdown(returns)
        res = drawdown.abs().max()
        return res

    @classmethod
    def cal_var(cls, returns, alpha=0.05):
        """This method calculates the historical simulation var 
        of the returns
        """
        res = abs(returns.quantile(q=alpha))
        return res
    
    # -----------risk&return related-------------   
    @classmethod
    def cal_sharpe(cls, returns, risk_free=0, period='daily'):
        returns_adj = returns - risk_free
        arr = cls.cal_aar(returns_adj, period)
        vol = cls.cal_standard_deviation(returns, period)
        res = arr / vol
        return res
    
    @classmethod
    def cal_sortino(cls, returns, mar=0, risk_free=0, period='daily'):
        returns_adj = returns - risk_free
        arr = cls.cal_aar(returns_adj, period)        
        downside_vol = cls.cal_downside_deviation(returns, mar, period)
        res = arr / downside_vol
        return res
    
    @classmethod    
    def cal_calmar(cls, returns, risk_free=0, period='daily'):
        returns_adj = returns - risk_free
        arr = cls.cal_aar(returns_adj, period)
        md = cls.cal_max_drawdown(returns)
        res = arr / md
        return res

    @classmethod        
    def cal_omega(cls, returns, mar=0):
        returns_adj = returns - mar
        profit = returns_adj[returns_adj > 0].sum()
        loss = returns_adj[returns_adj <= 0].sum()
        res = profit / loss
        return res
    
    @classmethod
    def cal_information(cls, returns, bm_returns, period='daily'):
        excess_ret = returns - bm_returns
        arr = cls.cal_aar(excess_ret, period)
        tracking_error = cls.cal_standard_deviation(excess_ret, period)
        res = arr / tracking_error
        return res

    @classmethod    
    def cal_treynor(cls, returns, bm_returns, risk_free=0, period='daily'):
        returns_adj = returns - risk_free
        arr = cls.cal_aar(returns_adj, period) 
        marketbeta = cls.cal_marketbeta(returns, bm_returns, risk_free)
        res = arr / marketbeta
        return res

    @classmethod        
    def cal_m_square(cls, returns, bm_returns, risk_free=0, period='daily'):
        sharpe = cls.cal_sharpe(returns, risk_free, period)
        bm_vol = cls.cal_standard_deviation(bm_vbm_returns, period='daily')
        res = sharpe * bm_vol + risk_free
        return res

    @classmethod        
    def cal_sterling(cls, returns, risk_free=0, period='daily'):
        returns_adj = returns - risk_free
        arr = cls.cal_aar(returns_adj, period)
        drawdown_mean = cls.cal_drawdown(returns).mean()
        res = arr / drawdown_mean
        return res

    @classmethod    
    def cal_burke(cls, returns, risk_free=0, period='daily'):
        returns_adj = returns - risk_free
        arr = cls.cal_aar(returns_adj, period)
        drawdown = cls.cal_drawdown(returns)
        drawdown_square = drawdown**2
        res = arr / pd.np.sqrt(drawdown_square.mean())
        return res
    
    @classmethod    
    def cal_tail(cls, returns, alpha=0.05):
        profit = abs(returns.quantile(1-alpha))
        loss = abs(returns.quantile(alpha))
        res = profit / loss
        return res
  
    @classmethod    
    def cal_rachev(cls, returns, alpha=0.05):
        profit_tail = abs(returns.quantile(1-alpha))
        profit = returns[returns >= profit_tail]
        
        loss_tail = returns.quantile(alpha)
        loss = returns[returns <= loss_tail]
        
        res = profit.sum() / abs(loss.sum())
        return res

    # -----------Stability&sustainability related-------------   
    @classmethod
    def cal_stability(cls, returns):
        y = pd.np.log((1 + returns).cumprod())
        x = pd.Series(pd.np.arange(len(cum_ret)), index=cum_ret.index)
        x_constant = sm.add_constant(x)
        res = sm.OLS(y, x_constant).fit().rsquared
        return res
    
    @classmethod
    def cal_arma(cls, returns, bm_returns, risk_free=0):
        # calculate excess return
        y = returns - risk_free
        x = bm_returns - risk_free
        alpha =sm.OLS(y, x).fit().resid
        model = ARMA(alpha, order=(1, 1))
        res = model.fit(disp=0, method='css')
        
        return res
    
    @classmethod
    def cal_monthly_odds(cls, returns, period='daily'):
        if period in ('daily', 'weekly'):
            monthly_return = (1 + returns).cumprod(
                    ).resample('M').last().pct_change()
        elif period == 'monthly':
            monthly_return = returns
            
        profit_count = (monthly_return>0).sum()
        loss_count = (monthly_return<=0).sum()
        res = profit_count / (loss_count + profit_count)
        return res
    
    @classmethod
    def cal_func(cls):
        pass
 
    # -----------concentration related------------- 
    
    # -----------concentration related------------- 
    
    
    
        
    