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
    ----------
      cash:int
            初始资金
      cm_rate:float
            交易手续费
      deal_price:str
            用于回测的股价类型(open, high, low, close), 默认为close

    回测示例
                            buy     sell    pos         total
    broker      2012-01-04
    backtest    2012-01-04  1
    broker      2012-01-05  1               +100        100
    backtest    2012-01-05  2
    broker      2012-01-06  2               +100        200
    backtest    2012-01-06  3       4
    broker      2012-01-09  3       4       +100/-200   100
    backtest    2012-01-09  5
    broker      2012-01-20  5               +100        100
    backtest    2012-01-20  6       7
    broker      2012-01-30  6       7       +100/-200   100
    backtest    2012-01-30  8
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
        # 用于跟踪交易订单情况
        self._id = 0

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
                if not order["done"]:
                    self.ctx.bt.on_order_timeout(order)
                continue

            new_order_lst.append(order)

        self.order_lst = new_order_lst
        for order in self.order_lst:
            # 每一轮tick将ttl减一，用于控制订单超时
            if order["ttl"] > 0:
                order["ttl"] -= 1

            # 如果当前tick，该股票有报价
            if order["code"] in tick_data:
                self.execute(order, tick_data)

    def execute(self, order, tick_data):
        """执行有效状态的订单"""
        # TODO:
        # 可以将买卖逻辑抽离出来用额外的两个函数_buy,_sell函数单独处理
        order_code = order["code"]
        order_price = order["price"]
        order_shares = order["shares"]
        stock_info = tick_data[order_code]
        stock_price = stock_info[self.deal_price]

        if order_price is None:
            order_price = stock_price

        if order["type"] == "buy" and order_price >= stock_price:
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

            deal = {"open_id": order["id"],
                    "open_price": stock_price,
                    "open_date": self.ctx.now,
                    "commission": commission,
                    "shares": order["shares"]}

            pos = {"open_id": order["id"],
                   "open_price": stock_price,
                   "open_date": self.ctx.now,
                   "shares": order["shares"]}

            self.cash = self.cash - cost - commission
            order["deal_lst"].append(deal)
            self.position[order_code].append(pos)

            order["ttl"] = 0
            order["done"] = True
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

            # total_pos_shares = sum([pos["shares"] for pos in self.position[order_code]])
            # if order_shares >= total_pos_shares:
            #     order_shares -= total_pos_shares

            #     if order_shares == 0:
            #         order["ttl"] == 0

            #     for pos in self.position[order_code]:
            #         pass

            #     # order["deal_lst"].extend(deal_lst)
            #     self.position.pop(order_code)
            #     self.ctx.bt.on_order_ok(order)

            tmp = order_shares
            deal_lst = []
            remove_pos_lst = []
            commission = 0
            # 当前计算手续费会不准确
            for pos in self.position[order_code]:
                if tmp == 0:
                    break

                time_diff = self.ctx.now - pos["open_date"]
                # 防止对当天完成的交易进行交易
                if time_diff.total_seconds() <= 19800:
                    continue

                if pos["shares"] <= tmp:
                    # 计算手续费等
                    new_cash = pos["shares"] * trade_price
                    commission += new_cash * self.cm_rate
                    deal_lst.append({
                                    "open_id": pos["open_id"],
                                    "open_price": pos["open_price"],
                                    "open_date": pos["open_date"],
                                    "close_id": order["id"],
                                    "close_price": trade_price,
                                    "close_date": self.ctx.now,
                                    "commission": None,
                                    "shares": pos["shares"],
                                    "profit": None})

                    tmp -= pos["shares"]
                    remove_pos_lst.append(pos)
                else:
                    # 计算手续费等
                    new_cash = tmp * trade_price
                    commission += new_cash * self.cm_rate
                    deal_lst.append({
                                    "open_id": pos["open_id"],
                                    "open_price": pos["open_price"],
                                    "open_date": pos["open_date"],
                                    "close_id": order["id"],
                                    "close_price": trade_price,
                                    "close_date": self.ctx.now,
                                    "commission": None,
                                    "shares": tmp,
                                    "profit": None})

                    pos["shares"] -= tmp
                    tmp = 0

            # 防止刚好仓位为0并且tmp == 0
            if tmp == 0:
                order["ttl"] = 0
                order["done"] = True

            # print(remove_pos_lst)
            for pos in remove_pos_lst:
                self.position[order_code].remove(pos)

            # 移除没有头寸的仓位
            if len(self.position[order_code]) == 0:
                self.position.pop(order_code)

            order["shares"] = tmp
            if commission < 5:
                commission = 5

            deal_shares = sum([deal["shares"] for deal in deal_lst])
            for deal in deal_lst:
                deal["commission"] = commission * (deal["shares"] / deal_shares)
                deal["profit"] = (deal["close_price"] - deal["open_price"]) * deal["shares"] - deal["commission"]
                new_cash = deal["shares"] * deal["close_price"]
                self.cash = self.cash + new_cash

            self.cash -= commission

            order["deal_lst"].extend(deal_lst)
            self.ctx.bt.on_order_ok(order)

    @property
    def stock_value(self):
        value = 0
        for code in self.position:
            latest_price = self.ctx.latest_price[code]
            for pos in self.position[code]:
                value += pos["shares"] * latest_price

        return value

    @property
    def assets_value(self):
        return self.cash + self.stock_value

    def get_shares(self, code):
        """返回指定股票代码的持仓数量"""
        if code not in self.position:
            return 0
        return sum([pos["shares"] for pos in self.position[code]])

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
                "id": 订单ID,
                "type": 订单类型, "buy",
                "code": 股票代码,
                "date": 提交日期,
                "ttl": 存活时间, 当ttl等于0时则超时，往后不会在执行
                "shares": 目标股份数量,
                "price": 目标价格,
                "done": 是否完成, 默认为False,
                "deal_lst": 交易成功的历史数据，如
                    [{
                      "open_id": 订单ID,
                      "open_price": 成交价格,
                      "open_date": 成交时间,
                      "commission": 交易手续费,
                      "shares": 成交份额
                    }]
                ""
            }
        """
        if shares % 100 != 0:
            raise ValueError("买入股票数量只能是100的整数倍")
        if shares <= 0:
            raise ValueError("买入股票数量必须大于0")

        self._id += 1
        order = {
            "id": self._id,
            "type": "buy",
            "code": code,
            "date": self.ctx.now,
            "ttl": ttl,
            "shares": shares,
            "price": price,
            "done": False,
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
                "id": 订单ID,
                "type": 订单类型, "sell",
                "code": 股票代码,
                "date": 提交日期,
                "ttl": 存活时间, 当ttl等于0时则超时，往后不会在执行
                "shares": 目标股份数量,
                "price": 目标价格,
                "done": 是否完成, 默认为False,
                "deal_lst": 交易成功的历史数据，如
                    [{
                      "open_id": 开仓订单ID,
                      "open_price": 开仓价格,
                      "open_date": 持仓时间,
                      "close_price": 成交价格,
                      "close_date": 成交时间,
                      "close_id": 平仓订单ID,
                      "commission": 交易手续费,
                      "shares": 成交份额,
                      "profit": 交易收益}]
                ""
            }
        """
        if shares % 100 != 0:
            raise ValueError("买入股票数量只能是100的整数倍")

        if code not in self.position:
            return

        pos_date_lst = [pos["open_date"] for pos in self.position[code]]
        time_diff = self.ctx.now - min(pos_date_lst)
        if time_diff.total_seconds() <= 19800:
            return

        self._id += 1
        order = {
            "id": self._id,
            "type": "sell",
            "code": code,
            "date": self.ctx.now,
            "ttl": ttl,
            "shares": shares,
            "price": price,
            "done": False,
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
