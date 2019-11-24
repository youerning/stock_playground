# -*- coding: utf-8 -*-
# @Author: youerning
# @Email: 673125641@qq.com

"""
构图规划

总收益, 年化收益, 最大回撤, 夏普比率, 手续费比率(手续费/收益)
收益曲线
-------
持仓时间直方分布图|持仓收益直方分布图
-------
持有过的股票走势图，并且标记买入点/卖出点
"""
# import sys
import matplotlib.pyplot as plt
# import matplotlib as mpl


plt.style.use("ggplot")
plt.rcParams['font.sans-serif'] = ['simhei']  # 指定默认字体
plt.rcParams['axes.unicode_minus'] = False   # 解决保存图像是负号'-'显示为方块的问题


class Plotter(object):
    def __init__(self, feed, stat, order_lst):
        self.feed = feed
        self.stat = stat
        self.order_lst = order_lst

    def report(self, file_name):
        fig = self.plot()
        fig.savefig(file_name)

    def plot(self):
        net_profit = self.stat.data.assets_value[-1] - self.stat.data.assets_value[0]
        profit_lst = []
        hold_time_lst = []
        commission = 0
        # 手续费比率
        cm_in_netprofit = (commission / (net_profit + 1e-5)) * 100
        for order in self.order_lst:
            for deal in order["deal_lst"]:
                commission += deal["commission"]
                if order["type"] == "buy":
                    break
                profit_lst.append(deal["profit"])
                close_date = deal["close_date"]
                open_date = deal["open_date"]
                time_diff = close_date - open_date
                # 3600 * 24
                hold_time = time_diff.total_seconds() / 86400
                hold_time_lst.append(hold_time)

        title = "策略收益: {:.3f}% 年化收益: {:.3f}% 最大回撤: {:.3f}% 夏普比率: {:.3f}% 手续费比率: {:.3f}%\n\n策略走势"
        title = title.format(self.stat.total_returns * 100,
                             self.stat.annual_return * 100,
                             self.stat.max_dropdown * 100,
                             self.stat.sharpe,
                             cm_in_netprofit)
        fig = plt.figure(figsize=(12, 16))
        # fig.subplots_adjust(wspace=0.1, hspace=0.1, top=1)
        code_lst = {order["code"] for order in self.order_lst}
        # rows = len(code_lst) + 2
        rows = 2
        # date_formatter = mpl.dates.DateFormatter("%Y-%m-%d")

        # 绘制收益走势图
        ax_trend = fig.add_subplot(rows, 1, 1)
        ax_trend.set_title(title)
        self.stat.data.assets_value.plot(ax=ax_trend, sharex=False)
        ax_trend.set_xlabel("")
        # ax_trend.plot_date(self.stat.index, self.stat.assets_value)
        # ax_trend.xaxis.set_major_fomatter(date_formatter)

        # 绘制直方图
        ax_hist1 = fig.add_subplot(rows, 2, 3)
        ax_hist2 = fig.add_subplot(rows, 2, 4)

        if len(profit_lst) > 0:
            ax_hist1.hist(profit_lst)
        if len(hold_time_lst) > 0:
            ax_hist2.hist(hold_time_lst)

        ax_hist1.set_title("收益分布")
        ax_hist2.set_title("持仓时间分布")

        # # 绘制持仓股票走势图
        # for idx, code in enumerate(code_lst, start=3):
        #     ax = fig.add_subplot(rows, 1, idx)
        #     ax.get_xaxis().set_visible(False)
        #     hist = self.feed[code]
        #     # max_close = max(hist.close)
        #     hist.close.plot(ax=ax, sharex=False, title="%s" % code)
        #     for order in self.order_lst:
        #         if len(order["deal_lst"]) == 0:
        #             continue
        #         if order["type"] == "buy":
        #             for deal in order["deal_lst"]:
        #                 ax.annotate("",
        #                             xy=(deal["open_date"], deal["open_price"]),
        #                             xytext=(deal["open_date"], deal["open_price"] * 0.95),
        #                             arrowprops=dict(facecolor="r",
        #                                             alpha=0.3,
        #                                             headlength=10,
        #                                             width=10))

        #         if order["type"] == "sell":
        #             for deal in order["deal_lst"]:
        #                 ax.annotate("",
        #                             xy=(deal["close_date"], deal["close_price"]),
        #                             xytext=(deal["close_date"], deal["close_price"] * 1.05),
        #                             arrowprops=dict(facecolor="g",
        #                                             alpha=0.3,
        #                                             headlength=10,
        #                                             width=10))
        return fig
