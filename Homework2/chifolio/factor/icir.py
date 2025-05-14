# -*- coding: utf-8 -*-
"""
Created on Fri Aug  9 14:41:54 2019

@author: Administrator
"""
import pandas as pd
from scipy import stats
from collections import OrderedDict

def cal_ic(descriptor, price, date_list,method='spearman', block=None):
    """计算IC
    """

    date_range = descriptor.index.levels[0]
    start, end = date_range.min(), date_range.max()

    week_rets = price.reindex(date_list).pct_change()
    forward_rets = week_rets.shift(-1)

    ic = OrderedDict()

    for dt in date_list:

        dtstr = dt.strftime('%Y%m%d')

        if block is not None:

            if dt < pd.to_datetime(start):
                continue
            if dt > pd.to_datetime(end):
                continue

            universe = block.get(dt)
            if universe is None:
                continue

            if descriptor.get(dtstr) is None:
                continue

            if len(descriptor.get(dtstr).dropna())<10:
                continue

            des = descriptor.get(dtstr).squeeze().reindex(universe) if descriptor.get(
                dtstr) is not None else descriptor.get(dtstr)
            ret = forward_rets.loc[dtstr].squeeze().reindex(universe)

        else:
            des = descriptor.get(dtstr)
            ret = forward_rets.loc[dtstr]

        if (des is None) or (ret.empty):
            continue

        ic[dt] = des.corr(ret.squeeze(), method=method)

    res = pd.Series(ic).dropna()

    return res

def ic_statistic(ic):
    res = pd.Series({'IC': ic.mean(), 'ICSTD': ic.std(), 
                     'IR': ic.mean()/ic.std(), 
                     'T': stats.ttest_1samp(ic.dropna(),0).statistic})
    return res

