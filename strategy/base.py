# -*- coding: utf-8 -*-
# @Author: youerning
# @Email: 673125641@qq.com
import abc


class BaseStrategy(object):
    __class__ == abc.ABCMeta

    def buy(self, code, hist, pos_lst):
        return None

    def sell(self, code, hist, pos_lst):
        return None

    @abc.abstractmethod
    def on_data(self, code, hist, pos_lst):
        """
        return {
                "buy_lst": [],
                "sell_lst": []
                }
        """
        pass
