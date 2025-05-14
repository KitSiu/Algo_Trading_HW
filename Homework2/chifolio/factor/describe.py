# -*- coding: utf-8 -*-
"""
Created on Fri Aug  9 13:37:39 2019

@author: Administrator
"""

import pandas as pd
from collections import OrderedDict
from data_api.ashare_api import *
from chifolio.calendar import Calendar, MONTH_END
 
def describe(descriptor):
    """对因子值进行描述性分析
    """      
    des = descriptor.dropna()
    res = des.describe()
    res['skew'] = des.skew()
    res['kurtosis'] = des.kurtosis()
    
    return res

def coverage(descriptor):
    """进行描述性分析
    """
    des_count = descriptor.groupby(level='date', group_keys=False).count()
    all_count = read_sql("select date, count(*) as number from constituent " 
                         "where block='ALL' group by date order by date")
    all_count['date'] = pd.to_datetime(all_count['date'])
    all_count = all_count.set_index('date').squeeze().reindex(des_count.index)
    res = des_count / all_count
    res = res.resample('M').last()
    
    return res

#def character(descriptor):
#    """股票分组特征
#    """
#    start = descriptor.index.levels[0].min()
#    end = descriptor.index.levels[-1].max()
#    
#    characters = pd.read_hdf(r'E:\research\ashare-multi-factors\data\raw\common\characters.h5')
#    mktcap = characters['total_mv']
#    amount = characters['amount_252']
#    turnover = characters['turnover_252']
#    vol = characters['total_vol_252']
#    beta = characters['market_beta_252']
#    pe = 1 / characters['net_profit_to_total_mktcap_ttm']
#    pb = 1 / characters['book_value_to_total_mktcap_mrq']
#    roa = characters['net_profit_to_asset_ttm']
#    roa_var = characters['net_profit_to_asset_q_var']
#    revenue_growth = characters['revenue_yoy_pct_chg']
#    # 总市值
##    mktcap = fetch_descriptor(name=['total_mv'], start=start, 
##                              end=end, source='tushare', period='monthly')
#    
#    # 成交量(一个月平均换手率指标)
##    amount = fetch_descriptor(name=['amount_252'], start=start, 
##                              end=end, source='tushare', period='monthly')
#
#
#    # 换手率
##    turnover = fetch_descriptor(name=['turnover_252'], start=start, 
##                              end=end, source='tushare', period='monthly')
#    
#    # 波动率(一个月收益总波动率)
##    vol = fetch_descriptor(name=['total_vol_252'], start=start, 
##                              end=end, source='tushare', period='monthly')
#    
#    # beta
##    beta = fetch_descriptor(name=['market_beta_252'], start=start, 
##                              end=end, source='tushare', period='monthly')    
#    
#    # PE
##    ep = fetch_descriptor(name=['net_profit_to_total_mktcap_ttm'], start=start, 
##                              end=end, source='tushare', period='monthly')
##    pe = 1/ep
#    
#    # PB
##    bp = fetch_descriptor(name=['book_value_to_total_mktcap_mrq'], start=start, 
#  #                            end=end, source='tushare', period='monthly')
##    pb = 1/bp
#
##    # ROA(最近12个月资产收益率)
##    roa = fetch_descriptor(name=['net_profit_to_asset_ttm'], start=start, 
##                              end=end, source='tushare', period='monthly')
#    
##    # ROA波动(单季度资产收益率的方差)
##    roa_var = fetch_descriptor(name=['net_profit_to_asset_q_var'], start=start, 
##                              end=end, source='tushare', period='monthly')
#    
##    # 收入增长(营业收入同比增长率)
##    revenue_growth = fetch_descriptor(name=['revenue_yoy_pct_chg'], start=start, 
##                              end=end, source='tushare', period='monthly')
##    
#    # 按照descriptor分为10组，统计每组股票特征
#    char = OrderedDict()
#    for dt in descriptor.index.levels[0]:            
#        factor = descriptor.get(dt).dropna()
#        avg_mktcap = OrderedDict()
#        avg_amount = OrderedDict()
#        avg_turnover = OrderedDict()
#        avg_vol = OrderedDict()
#        avg_beta = OrderedDict()
#        avg_pe = OrderedDict()
#        avg_pb = OrderedDict()
#        avg_roa = OrderedDict()
#        avg_roa_var = OrderedDict()
#        avg_revenue_growth = OrderedDict()
#        for i in range(10):
#            floor = pd.np.percentile(factor, i*10)
#            celling = pd.np.percentile(factor, (i+1)*10)
#            if i == 0:
#                target = factor[factor<celling].index
#            elif i == 9:
#                target = factor[factor>=floor].index
#            else:
#                target = factor[(factor>=floor) & (factor<celling)].index
#            
#            avg_mktcap[i] = winsorize(mktcap.get(dt).loc[target]).mean()
#            avg_amount[i] = winsorize(amount.get(dt).loc[target]).mean()
#            avg_turnover[i] = winsorize(turnover.get(dt).loc[target]).mean()
#            avg_vol[i] = winsorize(vol.get(dt).loc[target]).mean()
#            avg_beta[i] = winsorize(beta.get(dt).loc[target]).mean()
#            avg_pe[i] = winsorize(pe.get(dt).loc[target]).mean()
#            avg_pb[i] = winsorize(pb.get(dt).loc[target]).mean()
#            avg_roa[i] = winsorize(roa.get(dt).loc[target]).mean()
#            avg_roa_var[i] = winsorize(roa_var.get(dt).loc[target]).mean()
#            avg_revenue_growth[i] = winsorize(revenue_growth.get(dt).loc[target]).mean()
#            
#        char[dt] = pd.DataFrame({'Average Market Cap': avg_mktcap, 
#                                 'Average Amount': avg_amount, 
#                                  'Average Turnover': avg_turnover, 
#                                  'Average Volatility': avg_vol, 
#                                  'Average Beta': avg_beta,
#                                  'Average PE': avg_pe, 
#                                  'Average PB': avg_pb, 
#                                  'Average ROA': avg_roa,
#                                  'Average ROA Variability': avg_roa_var,
#                                  'Average Revenue Growth': avg_revenue_growth})
#    
#    res = pd.concat(char).groupby(level=1).mean().T
#    
#    return res


def character(descriptor,period='Monthly'):
    """股票分组特征
    """
    start = descriptor.index.levels[0].min()
    end = descriptor.index.levels[-1].max()

    trade_day = fetch_calendar(start, end)
    month_end = pd.Series(trade_day, index=calendar).groupby([cal.index.year, cal.index.month]).nth(days_offset).tolist()
    week_end = pd.Series(trade_day, index=calendar).groupby([cal.index.year, cal.index.weekofyear]).nth(days_offset).tolist()

    characters = pd.read_hdf(r'D:\Anaconda3\Lib\site-packages\chifolio\config\characters.h5')
    mktcap = characters['total_mv']
    amount = characters['amount_252']
    turnover = characters['turnover_252']
    vol = characters['total_vol_252']
    beta = characters['market_beta_252']
    pe = 1 / characters['net_profit_to_total_mktcap_ttm']
    pb = 1 / characters['book_value_to_total_mktcap_mrq']
    roa = characters['net_profit_to_asset_ttm']
    roa_var = characters['net_profit_to_asset_q_var']
    revenue_growth = characters['revenue_yoy_pct_chg']
    # 总市值
#    mktcap = fetch_descriptor(name=['total_mv'], start=start, 
#                              end=end, source='tushare', period='monthly')
    
    # 成交量(一个月平均换手率指标)
#    amount = fetch_descriptor(name=['amount_252'], start=start, 
#                              end=end, source='tushare', period='monthly')


    # 换手率
#    turnover = fetch_descriptor(name=['turnover_252'], start=start, 
#                              end=end, source='tushare', period='monthly')
    
    # 波动率(一个月收益总波动率)
#    vol = fetch_descriptor(name=['total_vol_252'], start=start, 
#                              end=end, source='tushare', period='monthly')
    
    # beta
#    beta = fetch_descriptor(name=['market_beta_252'], start=start, 
#                              end=end, source='tushare', period='monthly')    
    
    # PE
#    ep = fetch_descriptor(name=['net_profit_to_total_mktcap_ttm'], start=start, 
#                              end=end, source='tushare', period='monthly')
#    pe = 1/ep
    
    # PB
#    bp = fetch_descriptor(name=['book_value_to_total_mktcap_mrq'], start=start, 
  #                            end=end, source='tushare', period='monthly')
#    pb = 1/bp

#    # ROA(最近12个月资产收益率)
#    roa = fetch_descriptor(name=['net_profit_to_asset_ttm'], start=start, 
#                              end=end, source='tushare', period='monthly')
    
#    # ROA波动(单季度资产收益率的方差)
#    roa_var = fetch_descriptor(name=['net_profit_to_asset_q_var'], start=start, 
#                              end=end, source='tushare', period='monthly')
    
#    # 收入增长(营业收入同比增长率)
#    revenue_growth = fetch_descriptor(name=['revenue_yoy_pct_chg'], start=start, 
#                              end=end, source='tushare', period='monthly')
  
#    characters = pd.DataFrame({'total_mv': mktcap,
#                               'amount_252': amount, 
#                               'turnover_252': turnover, 
#                               'total_vol_252': vol, 
#                               'market_beta_252': beta, 
#                               'net_profit_to_total_mktcap_ttm': ep, 
#                               'book_value_to_total_mktcap_mrq': bp, 
#                               'net_profit_to_asset_ttm': roa,
#                               'net_profit_to_asset_q_var': roa_var,
#                               'revenue_yoy_pct_chg': revenue_growth})
#    
#    characters.to_hdf(r'E:\research\ashare-multi-factors\data\raw\common\characters.h5', key='data')
#    
    # 按照descriptor分为10组，统计每组股票特征
    char = OrderedDict()
    if period=='Monthly':
        cal = month_end
    elif period=='Weekly':
        cal = week_end
    else:
        cal = trade_day
    for dt in cal:
        dt = pd.to_datetime(dt)
        factor = descriptor.get(dt).dropna()
        avg_mktcap = OrderedDict()
        avg_amount = OrderedDict()
        avg_turnover = OrderedDict()
        avg_vol = OrderedDict()
        avg_beta = OrderedDict()
        avg_pe = OrderedDict()
        avg_pb = OrderedDict()
        avg_roa = OrderedDict()
        avg_roa_var = OrderedDict()
        avg_revenue_growth = OrderedDict()
        for i in range(10):
            floor = pd.np.percentile(factor, i*10)
            celling = pd.np.percentile(factor, (i+1)*10)
            if i == 0:
                target = factor[factor<celling].index
            elif i == 9:
                target = factor[factor>=floor].index
            else:
                target = factor[(factor>=floor) & (factor<celling)].index
            
            avg_mktcap[i] = mktcap.get(dt).loc[target].mean()
            avg_amount[i] = amount.get(dt).loc[target].mean()
            avg_turnover[i] = turnover.get(dt).loc[target].mean()
            avg_vol[i] = vol.get(dt).loc[target].mean()
            avg_beta[i] = beta.get(dt).loc[target].mean()
            avg_pe[i] = pe.get(dt).loc[target].mean()
            avg_pb[i] = pb.get(dt).loc[target].mean()
            avg_roa[i] = roa.get(dt).loc[target].mean()
            avg_roa_var[i] = roa_var.get(dt).loc[target].mean()
            avg_revenue_growth[i] = revenue_growth.get(dt).loc[target].mean()
            
        char[dt] = pd.DataFrame({'Average Market Cap': avg_mktcap, 
                                 'Average Amount': avg_amount, 
                                  'Average Turnover': avg_turnover, 
                                  'Average Volatility': avg_vol, 
                                  'Average Beta': avg_beta,
                                  'Average PE': avg_pe, 
                                  'Average PB': avg_pb, 
                                  'Average ROA': avg_roa,
                                  'Average ROA Variability': avg_roa_var,
                                  'Average Revenue Growth': avg_revenue_growth})
    
    res = pd.concat(char).groupby(level=1).mean().T
    
    return res