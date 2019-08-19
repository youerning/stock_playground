# -*- coding: utf-8 -*-
# @Author: youerning
# @Email: 673125641@qq.com
import matplotlib.pyplot as plt
from matplotlib.pylab import date2num
from nobody.utils.utils import load_n_hist
from nobody.utils.utils import load_hist
from nobody.finder.k import K
from mpl_finance import candlestick_ohlc


fig = plt.figure(figsize=(16, 9))
ax = fig.add_subplot(111)
data = list(load_n_hist(1).values())[0]
# data = list(load_hist("000001.SZ"))[0][1]

data_list = []
for date, row in data[["open", "high", "low", "close"]].iterrows():
    t = date2num(date)
    open, high, low, close = row[:]
    datas = (t, open, high, low, close)
    data_list.append(datas)


kfind = K()
res = kfind.find(data, "djx")

# 绘制蜡烛图
candlestick_ohlc(ax, data_list, colorup='r', colordown='green', alpha=0.7, width=0.8)
# 将x轴设置为时间类型
ax.xaxis_date()

for idx in res:
    ax.annotate("",
                xy=(idx, data.loc[idx].close),
                xytext=(idx, data.loc[idx].close * 1.01 ),
                arrowprops=dict(facecolor="y",
                                alpha=1,
                                headlength=10,
                                width=10))
fig.savefig("kfind.png")
