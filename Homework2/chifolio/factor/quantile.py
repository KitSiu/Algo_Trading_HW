# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 10:20:37 2019

@author: Administrator
"""
import os
import pandas as pd
from collections import OrderedDict
from chifolio.backtest import Backtest
from chifolio.factor.outlier import winsorize
from chifolio.calendar import Calendar, MONTH_END
from data_api.ashare_api import (all_stock, 
                                 fetch_industry, 
                                 read_sql, 
                                 fetch_descriptor, 
                                 fetch_constituent, 
                                 fetch_calendar)
config_path = r'D:\ProgramData\Anaconda3\Lib\site-packages\chifolio\config\T.h5'
if os.path.exists(config_path):
    T = pd.read_hdf(r'D:\ProgramData\Anaconda3\Lib\site-packages\chifolio\config\T.h5')
    ST = pd.read_hdf(r'D:\ProgramData\Anaconda3\Lib\site-packages\chifolio\config\ST.h5')
    SUS = pd.read_hdf(r'D:\ProgramData\Anaconda3\Lib\site-packages\chifolio\config\SUS.h5')
    NEW = pd.read_hdf(r'D:\ProgramData\Anaconda3\Lib\site-packages\chifolio\config\NEW.h5')
    LMT = pd.read_hdf(r'D:\ProgramData\Anaconda3\Lib\site-packages\chifolio\config\LMT.h5')
    FIN = pd.read_hdf(r'D:\ProgramData\Anaconda3\Lib\site-packages\chifolio\config\FIN.h5')
    MKTCAP = pd.read_hdf(r'D:\ProgramData\Anaconda3\Lib\site-packages\chifolio\config\MKTCAP.h5')
    NB = pd.read_hdf(r'D:\ProgramData\Anaconda3\Lib\site-packages\chifolio\config\NB.h5')
    LMTDOWN = pd.read_hdf(r'D:\ProgramData\Anaconda3\Lib\site-packages\chifolio\config\LMTDOWN.h5')

else:

    T = fetch_constituent(block='T', start='19900101', end='99999999')# 待退市股票
    T.name = 'asset'

    ST = fetch_constituent(block='ST', start='19900101', end='99999999')# 风险警示股票
    ST.name = 'asset'

    SUS = fetch_constituent(block='SUSPENDED', start='19900101', end='99999999')# 停牌股票
    SUS.name = 'asset'

    NEW = fetch_constituent(block='NEW252', start='19900101', end='99999999')# 次新股
    NEW.name = 'asset'

    LMT = fetch_constituent(block='LIMITUP', start='19900101', end='99999999')# 次新股# 一字涨停股票
    LMT.name = 'asset'
    
    LMTDOWN = fetch_constituent(block='LIMITDOWN', start='19900101', end='99999999')# 
    LMTDOWN.name = 'asset'

    industry = fetch_industry('CS', start='19900101', end='20191231')
    industry.index = industry.index.set_names(['date', 'asset'])
    
    industry_plus = fetch_industry('CS-PLUS', start='20200101', end='99999999')
    industry_plus.index = industry_plus.index.set_names(['date', 'asset'])

    FIN1 = industry[(industry == '银行') | (industry == '非银行金融')]# 金融股票
    FIN2 = industry_plus[(industry_plus == '银行') | (industry_plus == '非银行金融') | (industry_plus == '综合金融')]# 金融股票
    FIN = pd.concat([FIN1, FIN2])
    
    #INDUSTRY = industry.groupby(level='asset').bfill()

    mktcap = fetch_descriptor(name=['total_mv'], start='19900101', end='99999999', source='tushare')
    mktcap.index.set_names(['date', 'asset'], inplace=True)
    MKTCAP = mktcap * 10000

    # 净资产小于0的股票
    NB = read_sql("select sid, date from ts_descriptor where book_value_mrq<0 order by date, sid")
    NB['date'] = pd.to_datetime(NB['date'])
    NB = NB.set_index('date').squeeze()
    NB.name = 'asset'
    
def get_universe(date, block='ALL', financial=True):
    """剔除黑名单，包括ST、停牌股、次新股、一字涨停股和金融行业股票
    
    Args:
        date，指定日期
        financial：是否剔除金融股，默认为不剔除
    """
    if type(date) == pd.Timestamp:
        date = date.strftime('%Y%m%d')    
        
    if block == 'ALL':
        universe = all_stock(date)
    else:
        const = fetch_constituent(block=block, start=date, end=date)
        universe = const.values.tolist()
    
    st = ST.get(date)
    suspended = SUS.get(date)
    new = NEW.get(date)
    limitup = LMT.get(date)
    
    if financial:    
        financial = FIN.get(date)
        res = list(set(universe) - set(st.tolist()) - set(suspended.tolist()) - 
                   set(new.tolist()) - set(limitup.tolist()) - set(financial.tolist()))    
    else:
        res = list(set(universe) - set(st.tolist()) - set(suspended.tolist()) - 
                   set(new.tolist()) - set(limitup.tolist()))   
    
    return res 
    
def cal_weigth(stocks, weight='equal_weighted', cap=None):
    """计算组合权重
    """
    if weight == 'equal_weighted':
        res = pd.Series(1/len(stocks), index=stocks)
    elif weight == 'mktcap_weighted':
        cap = cap.loc[stocks]
        res = cap / cap.sum()
    return res

def get_quantile_portfolios(descriptor, quantiles=10, block=None, 
                            financial=True, weight='equal_weighted'):
    """获取分组组合
    每月月末，按照因子从小到大排序，等分为N组
    其中，初始股票池为block，但会剔除次新股、ST、停牌股和一字涨停股票
    
    Args:
        descriptor: pd.Series, 因子数据，index为（date，sid）
        quantiles：int，分组数量，，默认为10组
        block：研究板块，默认为所有A股
        weight：组合加权方式，默认为等权重
        financial：是否剔除金融股，默认为不剔除
        
    Returns:
        res: list，组合列表，每个元素代表一个分组组合，一共有quantiles个组合，
        每个组合为一个OrderedDict，key为交易日，value为组合明细
    """
    date_range = descriptor.index.levels[0]
    start, end = date_range.min().strftime('%Y%m%d'), date_range.max().strftime('%Y%m%d')
    tc = fetch_calendar(start, end)
    month_ends = Calendar(pd.DatetimeIndex(tc)).month_end() 
    
    interval = 100 / quantiles
    history_portfolio = {i: OrderedDict() for i in range(quantiles)} # [OrderedDict() * 10]不行，浅复制
    
    for dt in month_ends:
        
        factor =  descriptor.get(dt)
        
        if factor is None:
            continue
        
        if block is not None:
            universe = block.get(dt)
            
            if universe is None:
                continue
            
            factor = factor.loc[universe]
        
        factor = factor.dropna()     
        for i in range(quantiles):
            floor = pd.np.percentile(factor, i*interval)
            celling = pd.np.percentile(factor, (i+1)*interval)
            if i == 0:
                target = factor[factor<celling].index
            elif i == quantiles-1:
                target = factor[factor>=floor].index
            else:
                target = factor[(factor>=floor) & (factor<celling)].index
                
            cap = MKTCAP.loc[dt]
            history_portfolio[i][dt] = cal_weigth(target, weight, cap)  
 
    return history_portfolio

def cal_quantile_returns(portfolios, price):
    """计算分组收益率
    
    Args：
        portfolios：list，分组组合列表
        price：pd.DataFrame，股票复权价格，column为股票代码，index为交易日期
        
    Returns：
        res: pd.DataFrame，分组收益率，column为分组名称，index为交易日期
    """
    rets = price.pct_change().fillna(0)
    pf_rets = OrderedDict()
    for i, pf in portfolios.items():
        nav = Backtest(rets, pf).run()
        pf_rets[i] = nav.pct_change().fillna(0)
    res = pd.DataFrame(pf_rets)
    return res

def get_interaction_portfolio(fst_portflios, scd_portflios, weight='equal_weighted'):
    """获取因子交叉组合
    Returns：
        history_portfolio: dict, key为分组名称，value为相应组合
    """
    res = {str(i) + str(j): OrderedDict(
                ) for i in range(len(fst_portflios)) for j in range(len(scd_portflios))}
    
    for dt in MONTH_END:
        cap = MKTCAP.get(dt)
        for i, pf1 in fst_portflios.items():
            for j, pf2 in scd_portflios.items():
                pf_name = str(i) + str(j)
                target = pf1[dt].index.intersection(pf2[dt].index)
                res[pf_name][dt] =  cal_weigth(target, weight, cap)
    
    return res


# 获取分层组合
def get_partition_portfolio(partition_factor, target_factor, 
                            q=5, weight='equal_weighted', block=None):
    

    res = {str(i) + str(j): OrderedDict(
            ) for i in range(q) for j in range(q)}

    for dt in MONTH_END:
        
        if block is not None:
            universe = block.get(dt)
        else:
            universe = all_stock(dt)
            
        if universe is None:
            continue
        
        cap = MKTCAP.get(dt)        
        partitions_factor_ = partition_factor.get(dt)
        target_factor_ = target_factor.get(dt)
        
        if (partitions_factor_ is None) | (target_factor_ is None):
            continue
        
        partitions_factor_ = partitions_factor_.loc[universe].dropna()
        target_factor_ = target_factor_.loc[universe].dropna()
        
        if len(target_factor_) < 30:
            continue

        partitions = pd.qcut(partitions_factor_, q=q, labels=list(range(q)))

        for label in range(q):
            partition = partitions[partitions==label].index
            sec_factor = target_factor_.loc[partition].dropna()
            sec_partitions = pd.qcut(sec_factor, q=q, labels=list(range(q)))
            for sec_label in range(q):
                pf_name = str(label) + str(sec_label)
                target = sec_partitions[sec_partitions==sec_label].index.tolist()
                res[pf_name][dt] = cal_weigth(target, weight, cap) 

    return res 

# 将分层组合进行合并（即中性化第一层）
def get_merged_partition_portfolio(partition_portfolio, q=5, weight='equal_weighted'):
    history_portfolio = {i: OrderedDict() for i in range(q)}
    for dt in partition_portfolio['00'].keys():
        cap = MKTCAP.loc[dt]
        for i in range(q):
            target = []
            for j in range(q):
                pf_name = str(j) + str(i)
                target += partition_portfolio[pf_name][dt].index.tolist()
            history_portfolio[i][dt] = cal_weigth(target, weight, cap) 
    return history_portfolio
