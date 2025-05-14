"""chifolio - a general framework for portfolio management"""

__version__ = '0.1.0'
__author__ = 'lianxb <785674410@qq.com>'
__all__ = ['cal_cagr', 
           'cal_cumret', 
           'cal_aar',
           'describe',
           'cal_alpha', 
           'cal_max_min_monthly_return',
           'cal_standard_deviation', 
           'cal_downside_deviation',
           'cal_marketbeta',
           'cal_max_drawdown',
           'cal_var',
           'cal_sharpe',
           'cal_sortino',
           'cal_calmar',
           'cal_omega',
           'cal_information', 
           'cal_treynor', 
           'cal_m_square', 
           'cal_sterling',
           'cal_burke',
           'cal_tail', 
           'cal_rachev', 
           'cal_stability', 
           'cal_arma',
           'cal_monthly_odds']

from .measure import Measure
from .metric import create_return_risk_metrics

describe = Measure.describe
cal_cagr = Measure.cal_cagr
cal_cumret = Measure.cal_cumret
cal_aar = Measure.cal_aar
cal_alpha = Measure.cal_alpha
cal_max_min_monthly_return = Measure.cal_max_min_monthly_return
cal_standard_deviation = Measure.cal_standard_deviation
cal_downside_deviation = Measure.cal_downside_deviation
cal_marketbeta = Measure.cal_marketbeta
cal_max_drawdown = Measure.cal_max_drawdown
cal_var = Measure.cal_var
cal_sharpe = Measure.cal_sharpe
cal_sortino = Measure.cal_sortino
cal_calmar = Measure.cal_calmar
cal_omega = Measure.cal_omega
cal_information = Measure.cal_information
cal_treynor = Measure.cal_treynor
cal_m_square = Measure.cal_m_square
cal_sterling = Measure.cal_sterling
cal_burke = Measure.cal_burke
cal_tail = Measure.cal_tail
cal_rachev = Measure.cal_rachev
cal_stability = Measure.cal_stability
cal_arma = Measure.cal_arma
cal_monthly_odds = Measure.cal_monthly_odds