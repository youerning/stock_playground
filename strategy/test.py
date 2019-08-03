# -*- coding: utf-8 -*-
# @Author: youerning
# @Email: 673125641@qq.com
from base import BaseStrategy


class Strategy(BaseStrategy):
    def buy(self, df):
        pass

    def sell(self, df):
        pass

    def on_data(self, code, hist, pos_lst):
        pos_set = {pos["code"] for pos in pos_lst}

        if code in pos_set:
            sell_lst = self.sell(code, hist)
        buy_lst = self.buy(code, hist)

        return buy_lst, sell_lst
