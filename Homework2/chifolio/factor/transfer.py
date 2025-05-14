# -*- coding: utf-8 -*-
"""
Created on Fri Aug  9 13:21:15 2019

@author: Administrator
"""

import pandas as pd
import numpy as np
from collections import OrderedDict
import statsmodels.api as sm

normalize = lambda x: (x - x.mean()) / x.std()

def neutralize(descriptor, size=None, industry=None, others=None):
    """因子中性化
    """
    assert (size is not None) | (industry is not None), '行业和规模，必须指定至少一个'

    style_descriptors = []

    if size is not None:
        style_descriptors.append(size)
        intercept = True

    if industry is not None:
        industry = industry.dropna() # 这一步，一定要把缺失的扔掉，否则没有行业归类的股票，dummy值全为0【20180511】
        ind_dummy = pd.get_dummies(industry)    
        style_descriptors.append(ind_dummy)
        intercept = False
       
    x = pd.concat(style_descriptors, axis=1).dropna()
    X = sm.add_constant(x) if intercept else x
    X = X.reindex(index=descriptor.index)

    neutral_descriptor = OrderedDict()
    
    for dt in X.index.levels[0]:
        
        y = descriptor.loc[dt]
        
        if (len(y.dropna()) < 30) | (len(X.loc[dt].dropna()) < 30):
            #neutral_descriptor[dt] = np.nan
            continue
        
        mod = sm.OLS(y, X.loc[dt], missing='drop').fit()        
        neutral_descriptor[dt] = mod.resid    

    neutral_descriptor = pd.concat(neutral_descriptor)
    neutral_descriptor.index = neutral_descriptor.index.set_names(['date', 'asset'])
    
    return neutral_descriptor