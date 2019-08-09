# -*- coding: utf-8 -*-
# @Author: youerning
# @Email: 673125641@qq.com
import pytest
import sys
from nobody.utils import load_hist
from nobody.backtest import BackTest


class MyBackTest(BackTest):
    def initialize(self):
        self._first = True
        self._second = False

    def before_on_tick(self, tick):
        pass

    def after_on_tick(self, tick):
        pass

    def before_trade(self, order):
        return True

    def on_order_ok(self, order):
        pass

    def on_order_timeout(self, order):
        pass

    def finish(self):
        pass

    def on_tick(self, tick):
        pass


def callchain(self, tick):
    tick_data = self.ctx["tick_data"]

    code = list(tick_data.keys())[0]
    if self._first:
        for code, hist in tick_data.items():
            self.ctx.broker.buy(code, 100)

    self.ctx.broker.sell(code, 2000, ttl=3)
    self._first = False


def buy(self, tick):
    tick_data = self.ctx["tick_data"]

    code = list(tick_data.keys())[0]
    if self._first:
        self.ctx.broker.buy(code, 1500)
        self._first = False


def sell_in_empty(self, tick):
    tick_data = self.ctx["tick_data"]
    code = list(tick_data.keys())[0]
    self.ctx.broker.sell(code, 2000, ttl=5)
    self._first = False


def sell(self, tick):
    tick_data = self.ctx["tick_data"]

    code = list(tick_data.keys())[0]
    self.ctx.broker.buy(code, 100)
    self.ctx.broker.sell(code, 200)


@pytest.fixture()
def backtest():
    feed = {}

    for code, hist in load_hist("test_code"):
        feed[code] = hist

    if not feed:
        sys.exit("没有没有任何历史数据")

    mytest = MyBackTest(feed)
    return mytest


def test_callchain(mocker, backtest):
    mock_init = mocker.spy(backtest, "initialize")
    mock_before_on_tick = mocker.spy(backtest, "before_on_tick")
    mock_after_on_tick = mocker.spy(backtest, "after_on_tick")
    mock_before_trade = mocker.spy(backtest, "before_trade")
    mock_on_order_ok = mocker.spy(backtest, "on_order_ok")
    mock_on_order_timeout = mocker.spy(backtest, "on_order_timeout")
    bind_method = callchain.__get__(backtest, backtest.__class__)
    backtest.on_tick = bind_method
    backtest.start()

    assert mock_init.called
    assert mock_before_on_tick.called
    assert mock_after_on_tick.called
    assert mock_before_trade.called
    assert mock_on_order_ok.called
    assert mock_on_order_timeout.called

    data = backtest.stat.data
    assert data.cash[-1] == 100090


def test_buy(mocker, backtest):
    bind_method = buy.__get__(backtest, backtest.__class__)
    backtest.on_tick = bind_method
    backtest.start()
    assert backtest.stat.data.cash[-1] == 84992.5
    assert backtest.stat.data.stock_value[-1] == 16500
    assert backtest.stat.data.assets_value[-1] == 16500 + 84992.5


def test_sell_in_empty(mocker, backtest):
    bind_method = sell_in_empty.__get__(backtest, backtest.__class__)
    backtest.on_tick = bind_method
    backtest.start()
    order_hist_lst = backtest.ctx.broker.order_hist_lst

    assert len(order_hist_lst) == 0
    assert backtest.stat.data.cash[-1] == 100000
    assert backtest.stat.data.stock_value[-1] == 0
    assert backtest.stat.data.assets_value[-1] == 100000


def test_sell_and_buy(mocker, backtest):
    bind_method = sell.__get__(backtest, backtest.__class__)
    backtest.on_tick = bind_method
    backtest.start()
    order_hist_lst = backtest.ctx.broker.order_hist_lst

    assert len(order_hist_lst) == 9

    buy_count = len([order for order in order_hist_lst if order["type"] == "buy"])
    sell_count = len([order for order in order_hist_lst if order["type"] == "sell"])
    total_commission = sum([deal["commission"] for order in order_hist_lst for deal in order["deal_lst"]])
    import json
    with open("orders.json", "w") as wf:
        json.dump(order_hist_lst, wf, indent=4, default=str)

    assert buy_count == 6
    assert sell_count == 3
    assert total_commission == 35

    print(backtest.stat.data)
    assert backtest.stat.data.cash[-1] == 100000 - total_commission + 100 - 1100
    assert backtest.stat.data.stock_value[-1] == 1100
    assert backtest.stat.data.assets_value[-1] == 100000 + 100 - total_commission
