# -*- coding: utf-8 -*-
# @Author: youerning
# @Email: 673125641@qq.com
import numpy as np
from bokeh.plotting import figure
from bokeh.plotting import output_file
from bokeh.plotting import gridplot
from bokeh.models import Arrow, OpenHead, NormalHead, VeeHead
from math import pi


class Html(object):
    def __init__(self, feed, stat, order_lst):
        self.feed = feed
        self.stat = stat
        self.order_lst = order_lst

    def report(self, file_name):
        output_file(file_name)
        p_trend = figure(title="策略收益", plot_width=800, plot_height=250, x_axis_type="datetime")
        p_trend.line(self.stat.data.index, self.stat.data.assets_value, color='navy', alpha=0.5)

        p_hist1 = figure(title="收益分布", plot_width=400, plot_height=300)
        p_hist2 = figure(title="持仓时间分布", plot_width=400, plot_height=300)

        hist1, edges1 = np.histogram(self.profit_lst, bins=30)
        hist2, edges2 = np.histogram(self.hold_time_lst, bins=30)

        p_hist1.quad(top=hist1, bottom=0, left=edges1[:-1], right=edges1[1:],
                     fill_color="navy", line_color="white", alpha=0.5)

        p_hist2.quad(top=hist2, bottom=0, left=edges2[:-1], right=edges2[1:],
                     fill_color="navy", line_color="white", alpha=0.5)

        # TODO:
        # 参考这个绘制heatmap https://bokeh.pydata.org/en/latest/docs/gallery/categorical.html

        plot_lst = []
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

            p = figure(x_axis_type="datetime", tools=TOOLS, plot_width=1000, title="MSFT Candlestick")
            p.xaxis.major_label_orientation = pi / 4
            p.grid.grid_line_alpha = 0.3

            p.segment(df.index, df.high, df.index, df.low, color="black")
            p.vbar(df.index[inc], w, df.open[inc], df.close[inc], fill_color="#D5E1DD", line_color="black")
            p.vbar(df.index[dec], w, df.open[dec], df.close[dec], fill_color="#F2583E", line_color="black")
            plot_lst.append(p)

            for order in self.order_lst:
                if len(order["deal_lst"]) == 0:
                    continue
                if order["type"] == "buy":
                    for deal in order["deal_lst"]:
                        x, y = deal["date"], deal["price"]
                        p.add_layout(Arrow(end=NormalHead(fill_color="red", fill_alpha=0.3, line_width=0, size=15),
                                           x_end=x, y_end=y, line_alpha=0, x_start=x, y_start=y + 10))

                if order["type"] == "sell":
                    for deal in order["deal_lst"]:
                        p.add_layout(Arrow(end=NormalHead(fill_color="green", fill_alpha=0.3, line_width=0, size=15),
                                           x_end=x, y_end=y, line_alpha=0, x_start=x, y_start=y - 10))
        # output_file("candlestick.html", title="candlestick.py example")

