# -*- coding: utf-8 -*-
# @Author: youerning
# @Email: 673125641@qq.com
import json
import os
import sys
from os import path
from datetime import datetime
from nobody.utils import load_hist
from nobody.utils.utils import load_n_hist
from nobody.backtest import BackTest
from nobody.reporter import Plotter
# from nobody.reporter import Html


class MyBackTest(BackTest):
    def initialize(self):
        self.info("initialize")
        self._first = True

    # def before_on_tick(self, tick):
    #     self.info("before_on_tick")

    # def after_on_tick(self, tick):
    #     self.info("after_on_tick")

    # def on_order_ok(self, order):
    #     self.info("submit order successfully:")
    #     self.info(order)

    # def on_order_timeout(self, order):
    #     self.info("submit order timeout:")
    #     self.info(order)

    def finish(self):
        self.info("finish")

    def on_tick(self, tick):
        # self.info(tick)
        tick_data = self.ctx["tick_data"]
        # print(tick_data)
        # print(tick_data)
        # print(tick)
        # if self._first:
        #     self.ctx.broker.buy(code, hist.close, 100, ttl=5)
        #     self._first = False
        for code, hist in tick_data.items():
            # if self._first:
            #     self.ctx.broker.sell(code, hist.close, 1000, ttl=5)
            #     self.ctx.broker.buy(code, hist.close, 100, ttl=5)
            #     self._first = False
            if hist["ma10"] > 1.03 * hist["ma20"]:
                self.ctx.broker.buy(code, 500)

            if hist["ma10"] < 0.98 * hist["ma20"] and code in self.ctx.broker.position:
                self.ctx.broker.sell(code, 200)


# if __name__ == '__main__':
#     import pandas as pd
#     from utils import load_hist
#     feed = {}

#     feed["test_code"] = pd.read_csv("test.csv", parse_dates=["trade_date"], index_col="trade_date")
#     for code, hist in feed.items():
#         # hist = hist.iloc[:100]
#         hist["ma10"] = hist.close.rolling(10).mean()
#         hist["ma20"] = hist.close.rolling(20).mean()
#         feed[code] = hist

#     mytest = MyBackTest(feed)
#     mytest.start()
#     stats = mytest.stat
#     stats.data.to_csv("report/stat.csv")
#     print("最大回彻率: {}% ".format(stats.max_dropdown * 100))
#     print("年化收益: {}% ".format(stats.annual_return * 100))
#     print("夏普比率: {} ".format(stats.sharpe))


if __name__ == '__main__':
    feed = {}

    # print(datetime.now())
    # for code, hist in load_hist():
    #     # hist = hist.iloc[:30]
    #     hist["ma10"] = hist.close.rolling(10).mean()
    #     hist["ma20"] = hist.close.rolling(20).mean()
    #     feed[code] = hist

    for code, hist in load_n_hist(1).items():
        # hist = hist.iloc[:30]
        hist["ma10"] = hist.close.rolling(10).mean()
        hist["ma20"] = hist.close.rolling(20).mean()
        feed[code] = hist

    # print(datetime.now())
    # print(len(feed))
    if not feed:
        sys.exit("没有没有任何历史数据")
    mytest = MyBackTest(feed)
    mytest.start()
    order_lst = mytest.ctx.broker.order_hist_lst
    if not path.exists("report"):
        os.mkdir("report")
    with open("report/order_hist.json", "w") as wf:
        json.dump(order_lst, wf, indent=4, default=str)
    stats = mytest.stat
    stats.data.to_csv("report/stat.csv")
    print("策略收益： {:.3f}%".format(stats.total_returns * 100))
    print("最大回彻率: {:.3f}% ".format(stats.max_dropdown * 100))
    print("年化收益: {:.3f}% ".format(stats.annual_return * 100))
    print("夏普比率: {:.3f} ".format(stats.sharpe))

    plotter = Plotter(feed, stats, order_lst)
    plotter.report("report/report.png")

    # html = Html(feed, stats, order_lst)
    # html.report("report/report.html")
