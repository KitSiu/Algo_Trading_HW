"""chifolio - a general framework for portfolio management"""

__version__ = '0.1.0'
__author__ = 'lianxb <785674410@qq.com>'
__all__ = []

from .transfer import neutralize, normalize
from .icir import cal_ic, ic_statistic
from .outlier import winsorize, xsigma, xmad, adjboxplot
from .quantile import (get_quantile_portfolios,
                       cal_quantile_returns, 
                       #get_interaction_portfolios, 
                       get_partition_portfolio, 
                       get_merged_partition_portfolio)
from .quantile import ST, SUS, NEW, LMT, FIN, MKTCAP,T,NB, LMTDOWN#,INDUSTRY
from .describe import describe, coverage, character
