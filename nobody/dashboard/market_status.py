# -*- coding: utf-8 -*-
# @Author: youerning
# @Email: 673125641@qq.com
import pandas as pd
import numpy as np
from bokeh.plotting import figure
from bokeh.core.properties import value
from bokeh.models import ColumnDataSource
from bokeh.transform import dodge
from bokeh.io import output_file, save
from bokeh.layouts import Column
from nobody.utils import load_all_hist
from nobody.utils.utils import get_ts_client
from nobody.settings import config


output_file("market_status.html")
ts = get_ts_client()
feed = load_all_hist()
# 上证指数
sh_index = ts.pro_bar(ts_code='000001.SH', asset='I', start_date=config["START_DATE"])
sh_index.index = pd.to_datetime(sh_index.trade_date)
p_sh_index = figure(title="trend", plot_width=800, plot_height=300, x_axis_type="datetime")
p_sh_index.line(sh_index.index, sh_index.close, color='navy', alpha=0.5)


# 最近10天的涨停跌停数量
l10 = {}
limit_up = 9.5
limit_down = -9.5
l10["x_range"] = [dt.strftime("%Y-%m-%d") for dt in sh_index.index[-10:]]
l10["limit_up"] = []
l10["limit_down"] = []
pct_chg_lst = []

for idx, dt in enumerate(l10["x_range"]):
    limit_up_count = 0
    limit_down_count = 0

    for code, hist in feed.items():
        if dt not in hist.index:
            continue

        df = hist.loc[dt]
        if isinstance(df, pd.core.series.Series):
            if df.pct_chg > 9.5:
                limit_up_count += 1
            elif df.pct_chg < -9.5:
                limit_down_count += 1

            if idx == len(l10["x_range"]) - 1:
                pct_chg_lst.append(df.pct_chg)

    l10["limit_up"].append(limit_up_count)
    l10["limit_down"].append(limit_down_count)


source = ColumnDataSource(data=l10)

p_limit_hist = figure(x_range=l10["x_range"], y_range=(0, max(l10["limit_down"] + l10["limit_up"]) + 12),
                      plot_height=350, plot_width=800, title="Date",
                      toolbar_location=None, tools="")

p_limit_hist.vbar(x=dodge('x_range', -0.25, range=p_limit_hist.x_range),
                  top='limit_down', width=0.2, source=source,
                  color="#2ca25f", legend=value("跌停"))

p_limit_hist.vbar(x=dodge('x_range', 0.0, range=p_limit_hist.x_range),
                  top='limit_up', width=0.2, source=source,
                  color="#e84d60", legend=value("涨停"))

p_limit_hist.x_range.range_padding = 0.1
p_limit_hist.xgrid.grid_line_color = None
p_limit_hist.legend.location = "top_right"
p_limit_hist.legend.orientation = "horizontal"


# 最近一天涨跌幅分布
hist1, edges1 = np.histogram(pct_chg_lst, bins=20)
p_dist = figure(title="dist", plot_width=800, plot_height=400, y_range=(0, max(hist1)))
p_dist.quad(top=hist1, bottom=0, left=edges1[:-1], right=edges1[1:],
            fill_color="navy", line_color="white", alpha=0.5)

save(Column(p_sh_index, p_limit_hist, p_dist))
