# -*- coding: utf-8 -*-
"""
Created on Mon Dec 17 14:26:48 2018

@author: Administrator
"""
import pandas as pd
from data_api.ashare_api import fetch_calendar

class Calendar(object):
    def __init__(self, calendar):
        self.cal = calendar # a list
        self.cal_series = pd.Series(calendar, index=calendar)
    
    def every_day(self):
        res = self.cal
        return res

    def month_start(self, days_offset=0):
        cal = self.cal_series
        res = cal.groupby([cal.index.year, 
                           cal.index.month]).nth(days_offset).tolist()
        return res
        
    def month_end(self, days_offset=-1):
        cal = self.cal_series
        res = cal.groupby([cal.index.year, 
                           cal.index.month]).nth(days_offset).tolist()
        return res

    def week_start(self, days_offset=0):
        cal = self.cal_series
        res = cal.groupby([cal.index.year, 
                           cal.index.isocalendar().week]).nth(days_offset).tolist()
        return res

    def week_end(self, days_offset=-1):
        cal = self.cal_series
        res = cal.groupby([cal.index.year, 
                           cal.index.isocalendar().week]).nth(days_offset).tolist()
        return res
    
MONTH_END = Calendar(pd.DatetimeIndex(fetch_calendar())).month_end()
WEEK_END = Calendar(pd.DatetimeIndex(fetch_calendar())).week_end()