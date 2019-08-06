# -*- coding: utf-8 -*-
# @Author: youerning
# @Email: 673125641@qq.com
import numpy as np
from bokeh.plotting import figure
from bokeh.plotting import output_file
from bokeh.layouts import gridplot
from bokeh.io import save
# from bokeh.plotting import gridplot
from bokeh.models import Arrow, NormalHead
from math import pi


class Html(object):
    def __init__(self, feed, stat, order_lst):
        self.feed = feed
        self.stat = stat
        self.order_lst = order_lst

    def report(self, file_name):
        output_file(file_name)
        # net_profit = self.stat.data.assets_value[-1] - self.stat.data.assets_value[0]
        profit_lst = []
        hold_time_lst = []
        commission = 0
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

        p_trend = figure(title="策略收益", plot_width=1000, plot_height=400, x_axis_type="datetime")
        p_trend.line(self.stat.data.index, self.stat.data.assets_value, color='navy', alpha=0.5)

        p_hist1 = figure(title="收益分布", plot_width=500, plot_height=400)
        p_hist2 = figure(title="持仓时间分布", plot_width=500, plot_height=400)

        hist1, edges1 = np.histogram(profit_lst, bins=30)
        hist2, edges2 = np.histogram(hold_time_lst, bins=30)

        p_hist1.quad(top=hist1, bottom=0, left=edges1[:-1], right=edges1[1:],
                     fill_color="navy", line_color="white", alpha=0.5)

        p_hist2.quad(top=hist2, bottom=0, left=edges2[:-1], right=edges2[1:],
                     fill_color="navy", line_color="white", alpha=0.5)

        # TODO:
        # 参考这个绘制heatmap https://bokeh.pydata.org/en/latest/docs/gallery/categorical.html

        p_stock_lst = []
        code_lst = {order["code"] for order in self.order_lst}
        rows = len(code_lst) + 2
        # 绘制持仓股票走势图
        for idx, code in enumerate(code_lst, start=rows):
            df = self.feed[code]

            inc = df.close > df.open
            dec = df.open > df.close
            # half day in ms
            w = 12 * 60 * 60 * 1000

            TOOLS = "pan,wheel_zoom,box_zoom,reset,save"

            p = figure(x_axis_type="datetime", tools=TOOLS, plot_width=1000, title="股票:%s交易信息" % code)
            p.xaxis.major_label_orientation = pi / 4
            p.grid.grid_line_alpha = 0.3

            p.segment(df.index, df.high, df.index, df.low, color="black")
            p.vbar(df.index[inc], w, df.open[inc], df.close[inc], fill_color="#D5E1DD", line_color="black")
            p.vbar(df.index[dec], w, df.open[dec], df.close[dec], fill_color="#F2583E", line_color="black")

            for order in self.order_lst:
                if len(order["deal_lst"]) == 0:
                    continue
                if order["type"] == "buy":
                    for deal in order["deal_lst"]:
                        x, y = deal["date"], deal["price"]
                        p.add_layout(Arrow(end=NormalHead(fill_color="red", fill_alpha=0.3, line_width=0, size=15),
                                           x_end=x, y_end=y, line_alpha=0, x_start=x, y_start=y - 10))

                if order["type"] == "sell":
                    for deal in order["deal_lst"]:
                        x, y = deal["close_date"], deal["close_price"]
                        p.add_layout(Arrow(end=NormalHead(fill_color="green", fill_alpha=0.3, line_width=0, size=15),
                                           x_end=x, y_end=y, line_alpha=0, x_start=x, y_start=y + 10))
            p_stock_lst.append(p)
        save(gridplot([[p_trend], [p_hist1, p_hist2], p_stock_lst]))
