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
import talib
from os import path
from datetime import datetime
from nobody.utils import load_hist
from nobody.settings import config
from nobody.utils.utils import load_n_hist
from nobody.utils.utils import read_csv
from nobody.backtest import BackTest
from nobody.reporter import Plotter


class MyBackTest(BackTest):
    def initialize(self):
        self.info("initialize")
        self.loss_threshold = 0.03
        self.porfit_threshold = 0.05

    def on_tick(self, tick):
        # 周四全部清仓
        position = self.ctx.broker.position
        if tick.weekday() == 3:
            for code in position:
                self.ctx.broker.sell_all(code)
            return

        if tick.weekday() != 4:
            for code in position:
                pass

        tick_data = self.ctx["tick_data"]
        sh_index_atr5 = tick_data["000001.SH"]["atr5"]
        sh_index_atr10 = tick_data["000001.SH"]["atr10"]
        if sh_index_atr5 >= sh_index_atr10:
            return

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


if __name__ == '__main__':
    feed = {}

    sh_index_path = path.join(config["INDEX_DATA_PATH"], "000001.SH.csv")
    sh_index = read_csv(sh_index_path)
    sh_index["atr5"] = talib.ATR(sh_index.high, sh_index.low, sh_index.close, 5)
    sh_index["atr10"] = talib.ATR(sh_index.high, sh_index.low, sh_index.close, 10)
    sh_index["ma5"] = talib.MA(sh_index.close, 5)
    sh_index["ma10"] = talib.MA(sh_index.close, 10)
    feed['000001.SH'] = sh_index

    for code, hist in load_n_hist(10).items():
        hist["ma10"] = talib.MA(hist, 10)
        hist["ma20"] = talib.MA(hist, 20)
        hist["atr10"] = talib.ATR(hist.high, hist.low, hist.close, 10)
        hist["rsi"] = talib.RSI(hist.close, 10)
        feed[code] = hist

    # print(datetime.now())
    # print(len(feed))
    if not feed:
        sys.exit("没有没有任何历史数据")
    mytest = MyBackTest(feed, trade_cal=sh_index.index)
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
