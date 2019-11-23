# -*- coding: utf-8 -*-
# @Author: youerning
# @Email: 673125641@qq.com

from abc import ABC, abstractmethod
import pandas as pd
import numpy as np


class Base(ABC):
    def initialize(self):
        pass

    def finish(self):
        pass

    @abstractmethod
    def run(self, tick):
        pass


class Stat(Base):
    def __init__(self):
        self._date_hist = []
        self._cash_hist = []
        self._stk_val_hist = []
        self._ast_val_hist = []
        self._returns_hist = []
        self._position_hist = []

    def run(self, tick):
        self._date_hist.append(tick)
        self._cash_hist.append(self.ctx.broker.cash)
        self._stk_val_hist.append(self.ctx.broker.stock_value)
        self._ast_val_hist.append(self.ctx.broker.assets_value)
        self._position_hist.append(len(self.ctx.broker.position))

    @property
    def data(self):
        df = pd.DataFrame({"cash": self._cash_hist,
                           "stock_value": self._stk_val_hist,
                           "assets_value": self._ast_val_hist, 
                           "pos_count": self._position_hist}, index=self._date_hist)
        df.index.name = "date"
        return df

    def get_dropdown(self):
        high_val = -1
        low_val = None
        high_index = 0
        low_index = 0
        dropdown_lst = []
        dropdown_index_lst = []

        for idx, val in enumerate(self._ast_val_hist):
            if val >= high_val:
                if high_val == low_val or high_index >= low_index:
                    high_val = low_val = val
                    high_index = low_index = idx
                    continue

                dropdown = (high_val - low_val) / high_val
                dropdown_lst.append(dropdown)
                dropdown_index_lst.append((high_index, low_index))

                high_val = low_val = val
                high_index = low_index = idx

            if low_val is None:
                low_val = val
                low_index = idx

            if val < low_val:
                low_val = val
                low_index = idx

        if low_index > high_index:
            dropdown = (high_val - low_val) / high_val
            dropdown_lst.append(dropdown)
            dropdown_index_lst.append((high_index, low_index))

        return dropdown_lst, dropdown_index_lst

    @property
    def max_dropdown(self):
        """最大回车率"""
        dropdown_lst, dropdown_index_lst = self.get_dropdown()
        if len(dropdown_lst) > 0:
            return max(dropdown_lst)
        else:
            return 0

    @property
    def annual_return(self):
        """
        年化收益率

        y = (v/c)^(D/T) - 1

        v: 最终价值
        c: 初始价值
        D: 有效投资时间(365)
        注: 虽然投资股票只有250天，但是持有股票后的非交易日也没办法投资到其他地方，所以这里我取365

        参考: https://wiki.mbalib.com/zh-tw/%E5%B9%B4%E5%8C%96%E6%94%B6%E7%9B%8A%E7%8E%87
        """
        D = 365
        c = self._ast_val_hist[0]
        v = self._ast_val_hist[-1]
        days = (self._date_hist[-1] - self._date_hist[0]).days

        ret = (v / c) ** (D / days) - 1
        return ret

    @property
    def cum_ret(self):
        """累计收益率"""
        ret_lst = pd.Series(self._ast_val_hist).pct_change().cumsum()

        return ret_lst

    @property
    def total_returns(self):
        init_val = self._ast_val_hist[0]
        final_val = self._ast_val_hist[-1]
        return (final_val - init_val) / init_val

    @property
    def sharpe(self, rf=0.04):
        """夏普比率, 不确定我这么算对不对
        计算公式: SharpeRatio = (E(Rp) - Rf) / op

        E(Rp): 投资预期报酬率
        Rf: 无风险利率
        op: 投资组合的波动率(标准差)(不确定对不对!!!)

        参卡:https://wiki.mbalib.com/zh-tw/%E5%A4%8F%E6%99%AE%E6%AF%94%E7%8E%87
        ---------
        Parameters:
          rf:float
                无风险利率，默认为4%
        ----
        """
        # 有可能返回nan, 而nan 类型是float，bool值为True
        return_std = (pd.Series(self._ast_val_hist, index=self._date_hist)
                        .pct_change()
                        .groupby(pd.Grouper(freq="W"))
                        .sum().std())

        # 防止return_sd == 0, 所以加上一个很小的数1e-5 == 0.00001
        ratio = (self.annual_return - rf) / (return_std + 1e-5)
        return ratio

    @property
    def win_ratio(self):
        return

    @property
    def profit_loss_ratio(self):
        return
