# -*- coding: utf-8 -*-
"""
Created on Fri Aug  9 11:29:20 2019

@author: Administrator
"""

import pandas as pd
from statsmodels.stats.stattools import medcouple

def winsorize(s, limits=(0.01, 0.01), drop=True):
    down = s.quantile(limits[0])
    up = s.quantile(1 - limits[1])
    if drop:
        s = s[(s >= down) & (s <= up)]
    else:
        s[s < down] = down
        s[s > up] = up
    return s

def xsigma(s, limit=3, drop=True):
    mean = s.mean()
    std = s.std()
    down = mean - limit * std
    up = mean + limit * std
    if drop:
        s = s[(s >= down) & (s <= up)]
    else:
        s[s < down] = down
        s[s > up] = up
    return s

def xmad(s, limit=3, drop=True):
    md = s.median()
    mad_e = abs(s - md).median() * 1.483
    down = md - limit * mad_e
    up = md + limit * mad_e
    if drop:
        s = s[(s >= down) & (s <= up)]
    else:
        s[s < down] = down
        s[s > up] = up
    return s
    
def adjboxplot(s, drop=True):

    if len(s) < 30:
        return s

    mc = medcouple(s)
    q1 = s.quantile(.25)
    q3 = s.quantile(.75)
    iqr = q3 - q1
    if mc >= 0:
        down = q1 - 1.5 * pd.np.exp(-3.5 * mc) * iqr
        up = q3 + 1.5 * pd.np.exp(4 * mc) * iqr
    else:
        down = q1 - 1.5 * pd.np.exp(-4 * mc) * iqr
        up = q3 + 1.5 * pd.np.exp(3.5 * mc) * iqr

    if drop:
        s = s[(s >= down) & (s <= up)]
    else:
        s[s < down] = down
        s[s > up] = up
    return s  