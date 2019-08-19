# -*- coding: utf-8 -*-
# @Author: youerning
# @Email: 673125641@qq.com
"""
通过蜡烛图吊颈线及RSI超卖买入, 下周一之前卖出

入场点: 吊颈线加RSI < 20
出场点:
    止损: 吊颈线最下方
    止盈: 阻力位或者RSI > 80
    截至时间: 下周一之前
"""
import json
import os
import sys
from os import path
from datetime import datetime
from nobody.utils import load_hist
from nobody.utils.utils import load_n_hist
from nobody.backtest import BackTest
from nobody.reporter import Plotter


class MyBackTest(BackTest):
    def initialize(self):
        self.info("initialize")
        self._first = True
    