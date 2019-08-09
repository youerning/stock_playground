# -*- coding: utf-8 -*-
# @Author: youerning
# @Email: 673125641@qq.com

# from collections import defaultdict
from abc import ABC, abstractmethod
from collections import defaultdict
from .utils import logger


class Base(ABC):
    """交易平台的基类"""

    def initialize(self):
        pass

    @abstractmethod
    def buy(self):
        pass

    @abstractmethod
    def sell(self):
        pass

    @abstractmethod
    def run(self):
        pass

    def finish(self):
        pass


class BackTestBroker(Base):
    """
    由于回测的虚拟交易平台

    Parameters:
      cash:int
            初始资金
      cm_rate:float
            交易手续费
      deal_price:str
            用于回测的股价类型(open, high, low, close), 默认为close
    """

    def __init__(self, cash, cm_rate=0.0005, deal_price="close"):
        """
        postion: {
                "code": [{
                    "price": 持仓价格,
                    "date": 建仓时间,
                    "shares": 头寸数量,
                    "commission", 持仓手续费
                    },...]}
        """
        self.cash = cash
        self.cm_rate = cm_rate
        self.order_lst = []
        self.order_hist_lst = []
        self.deal_price = deal_price
        # 持仓
        self.position = defaultdict(list)
        self.logger = logger

    def info(self, msg):
        self.logger.info(msg)

    def run(self, tick):
        tick_data = self.ctx["tick_data"]

        # 移除position中持仓量为空的股票
        # remove_code_lst = []
        # for code in self.position:
        #     if len(self.position[code]) == 0:
        #         remove_code_lst.append(code)

        # for code in remove_code_lst:
        #     self.position.pop(code)

        # 移除超时订单
        new_order_lst = []
        for order in self.order_lst:
            if order["ttl"] == 0:
                deal_shares = 0
                for deal in order["deal_lst"]:
                    deal_shares += deal["shares"]

                if deal_shares != order["shares"]:
                    self.ctx.bt.on_order_timeout(order)
                continue

            new_order_lst.append(order)

        self.order_lst = new_order_lst
        for order in self.order_lst:
            # 每一轮tick将ttl减一，用于控制订单超时
            order["ttl"] -= 1
            # 如果当前tick，该股票有报价
            if order["code"] in tick_data:
                self.execute(order, tick_data)

    def execute(self, order, tick_data):
        """执行有效状态的订单"""
        order_code = order["code"]
        order_price = order["price"]
        order_shares = order["shares"]
        stock_info = tick_data[order_code]
        stock_price = stock_info[self.deal_price]

        if order_price is None:
            order_price = stock_price

        if order["type"] == "buy" and order_price >= stock_price and order_shares >= 100:
            trade_price = stock_price

            cost = trade_price * order["shares"]
            commission = cost * self.cm_rate
            if commission < 5:
                commission = 5

            if cost + commission > self.cash:
                # TODO:
                # 完成部分成交逻辑
                return

            # 符合条件开始交易
            if not self.ctx.bt.before_trade(order):
                return

            deal = {"price": stock_price,
                    "date": self.ctx.now,
                    "commission": commission,
                    "shares": order["shares"]}

            self.cash = self.cash - cost - commission
            order["deal_lst"].append(deal)
            self.position[order_code].append(deal.copy())

            order["ttl"] = 0
            self.ctx.bt.on_order_ok(order)

        elif order["type"] == "sell" and order_price <= stock_price and order_code in self.position:
            trade_price = stock_price
            time_diff = self.ctx.now - order["date"]
            # 15:00 - 09:30 = 19800 secs
            # A股T+1交易
            if time_diff.total_seconds() <= 19800:
                return

            # 符合条件开始交易
            if not self.ctx.bt.before_trade(order):
                return

            tmp = order_shares
            deal_lst = []
            remove_pos_lst = []
            for pos in self.position[order_code]:
                if tmp == 0:
                    break

                if pos["shares"] <= tmp:
                    # 计算手续费等
                    new_cash = pos["shares"] * trade_price
                    commission = new_cash * self.cm_rate
                    if commission < 5:
                        commission = 5
                    profit = new_cash - commission - (pos["shares"] * pos["price"])

                    deal_lst.append({
                                    "open_price": pos["price"],
                                    "close_price": trade_price,
                                    "close_date": self.ctx.now,
                                    "open_date": pos["date"],
                                    "commission": commission,
                                    "shares": pos["shares"],
                                    "profit": profit})

                    tmp -= pos["shares"]
                    remove_pos_lst.append(pos)
                    self.cash = self.cash + new_cash - commission
                else:
                    # 计算手续费等
                    new_cash = tmp * trade_price
                    commission = new_cash * self.cm_rate
                    if commission < 5:
                        commission = 5
                    profit = new_cash - commission - (tmp * pos["price"])

                    deal_lst.append({
                                    "open_price": pos["price"],
                                    "close_price": trade_price,
                                    "close_date": self.ctx.now,
                                    "open_date": pos["date"],
                                    "commission": commission,
                                    "shares": tmp,
                                    "profit": profit})

                    pos["shares"] -= tmp
                    tmp = 0
                    self.cash = self.cash + new_cash - commission

            # 防止刚好仓位为0并且tmp == 0
            if tmp == 0:
                order["ttl"] = 0

            # print(remove_pos_lst)
            for pos in remove_pos_lst:
                self.position[order_code].remove(pos)

            # 移除没有头寸的仓位
            if len(self.position[order_code]) == 0:
                self.position.pop(order_code)

            order["deal_lst"].extend(deal_lst)
            self.ctx.bt.on_order_ok(order)

    @property
    def stock_value(self):
        now = self.ctx.now
        value = 0
        for code in self.position:
            hist = self.ctx["feed"][code]
            latest_price = hist[hist.index <= now].iloc[-1][self.deal_price]
            for pos in self.position[code]:
                value += pos["shares"] * latest_price

        return value

    @property
    def assets_value(self):
        return self.cash + self.stock_value

    def get_drapdown(self):
        """返回最大回撤"""
        pass

    def get_return(self):
        """计算年化收益"""
        pass

    def submit(self, order):
        self.order_lst.append(order)
        self.order_hist_lst.append(order)

    def buy(self, code, shares, price=None, ttl=-1):
        """
        限价提交买入订单

        ---------
        Parameters:
          code:str
                股票代码
          price:float or None
                最高可买入的价格, 如果为None则按市价买入
          shares:int
                买入股票数量
          ttl:int
                订单允许存在的最大时间，默认为-1，永不超时

        ---------
        return:
          dict
             {
                "type": 订单类型, "buy",
                "code": 股票代码,
                "date": 提交日期,
                "ttl": 存活时间, 当ttl等于0时则超时，往后不会在执行
                "shares": 目标股份数量,
                "price": 目标价格,
                "deal_lst": 交易成功的历史数据，如
                    [{"price": 成交价格,
                      "date": 成交时间,
                      "commission": 交易手续费,
                      "shares": 成交份额
                    }]
                ""
            }
        """
        order = {
            "type": "buy",
            "code": code,
            "date": self.ctx.now,
            "ttl": ttl,
            "shares": shares,
            "price": price,
            "deal_lst": []
        }
        self.submit(order)
        return order

    def sell(self, code, shares, price=None, ttl=-1):
        """
        限价提交卖出订单
        ---------
        Parameters:
          code:str
                股票代码
          price:float or None
                最低可卖出的价格, 如果为None则按市价卖出
          shares:int
                卖出股票数量
          ttl:int
                订单允许存在的最大时间，默认为-1，永不超时

        ---------
        return:
          dict
             {
                "type": 订单类型, "sell",
                "code": 股票代码,
                "date": 提交日期,
                "ttl": 存活时间, 当ttl等于0时则超时，往后不会在执行
                "shares": 目标股份数量,
                "price": 目标价格,
                "deal_lst": 交易成功的历史数据，如
                    [{"open_price": 开仓价格,
                      "close_price": 成交价格,
                      "close_date": 成交时间,
                      "open_date": 持仓时间,
                      "commission": 交易手续费,
                      "shares": 成交份额,
                      "profit": 交易收益}]
                ""
            }
        """
        if code not in self.position:
            return

        order = {
            "type": "sell",
            "code": code,
            "date": self.ctx.now,
            "ttl": ttl,
            "shares": shares,
            "price": price,
            "deal_lst": []
        }
        self.submit(order)
        return order

    # def sell_all(self, code, price, ttl=-1):
    #     """以指定价格卖出当前所有持仓股票

    #     Args:
    #         code: 股票代码
    #         price: 最低可卖出的价格

    #     Returns:
    #         返回提交的订单

    #     """
    #     shares = 0
    #     if code in self.position:
    #         for pos in self.position[code]:
    #             shares += pos["shares"]
    #         return self.sell(code, price, shares, ttl)
    #     else:
    #         self.logger.warning("并不持有股票: %s" % code)

    # def stop_loss(self, code, price):
    #     """止损

    #     当价格低于指定价格卖出所有股票
    #     """
    #     self.sell_all(code, price)
    # def stop_profit(self, code, price):
    #     """止盈"""
    #     if code in self._pos_dict:
    #         shares = self._pos_dict[code].shares

    #     self.sell(code, price, shares)
