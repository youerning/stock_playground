# -*- coding: utf-8 -*-
# @Author: youerning
# @Email: 673125641@qq.com
"""
构图规划 并且标明支撑/阻力位
000001.SH trend candlestick amd volume bar
399001.SZ trend candlestick amd volume bar
399006.SZ trend candlestick amd volume bar

历史涨停跌停持平趋势柱状图
当日涨跌分布图

今日涨跌停表
行业 股票数量 平均浮动 最大涨幅 上涨数量 平仓数量 下跌数量

"""
import dash
import pandas as pd
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from os import path
from nobody.utils import get_ts_client
from nobody.utils import load_hist

# 设置相关变量
ts = get_ts_client()
pro = ts.pro_api()
start_date = "2018-01-01"
external_stylesheets = ['https://cdn.bootcss.com/bootstrap/4.0.0/css/bootstrap.min.css']
sh_index_path = path.join("data", "index", "000001.SH.csv")
feed = {}

# 主题样式
main_style = {
    "margin": "0 5%"
}


count = 0
for code, hist in load_hist(start_date="2018-01-01"):
    count += 1
    feed[code] = hist
    if count == 10:
        break

# 获取数据
# 上证指数日线数据
if path.exists(sh_index_path):
    sh_index = pd.read_csv(sh_index_path, parse_dates=["trade_date"], index_col="trade_date")
else:
    sh_index = ts.pro_bar(ts_code='000001.SH', asset='I', start_date=start_date)
    sh_index.trade_date = pd.to_datetime(sh_index.trade_date)
    sh_index = sh_index.sort_values("trade_date")
    sh_index.to_csv(sh_index_path, index=False)
    sh_index.index = sh_index.trade_date

# 获取股票基本信息
stock_basic = pro.stock_basic(list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
code_name_map = {ts_code: name for ts_code, name in zip(stock_basic.ts_code, stock_basic.name)}
code_industry_map = {ts_code: name for ts_code, name in zip(stock_basic.ts_code, stock_basic.industry)}


# 统计最近10天的涨停跌停数量
l10 = {}
limit_up = 9.5
limit_down = -9.5
l10["x_range"] = [dt.strftime("%Y-%m-%d") for dt in sh_index.index[-10:]]
l10["limit_up"] = []
l10["limit_down"] = []
l10["limit_nothing"] = []
pct_chg_lst = []

for idx, dt in enumerate(l10["x_range"]):
    limit_up_count = 0
    limit_down_count = 0
    limit_nothing_count = 0

    for code, hist in feed.items():
        if dt not in hist.index:
            continue

        df = hist.loc[dt]
        if isinstance(df, pd.core.series.Series):
            if df.pct_chg > 9.5:
                limit_up_count += 1
            elif df.pct_chg < -9.5:
                limit_down_count += 1
            else:
                limit_nothing_count += 1

            if idx == len(l10["x_range"]) - 1:
                pct_chg_lst.append(df.pct_chg)

    l10["limit_up"].append(limit_up_count)
    l10["limit_down"].append(limit_down_count)
    l10["limit_nothing"].append(limit_nothing_count)

# 绘图
# sh_index 蜡烛图
sh_index_graph = dcc.Graph(id="sh_index",
                           figure={"data": [go.Candlestick(x=sh_index.index,
                                                           open=sh_index.open,
                                                           high=sh_index.high,
                                                           low=sh_index.low,
                                                           close=sh_index.close)
                                            ],
                                   "layout": go.Layout(xaxis={"title": "Date"},
                                                       yaxis={"title": "Price"},
                                                       title="SH Index",
                                                       height=600)})

# 历史涨跌幅
hist_zd_graph = dcc.Graph(id="hist_zd",
                          figure={"data": [{"x": l10["x_range"], "y": l10["limit_up"], "name": "limit_up", "type": "bar"},
                                           {"x": l10["x_range"], "y": l10["limit_down"], "name": "limit_down", "type": "bar"},
                                           {"x": l10["x_range"], "y": l10["limit_nothing"], "name": "limit_nothing", "type": "bar"},
                                           ],
                                  "layout": go.Layout(xaxis={"title": "Date"},
                                                      yaxis={"title": "Count"},
                                                      title="hist zd")})

# 浮动分布
hist_dist_graph = dcc.Graph(id="historam",
                            figure={"data": [go.Histogram(x=pct_chg_lst)],
                                    "layout": go.Layout(xaxis={"title": "hist"},
                                                        yaxis={"title": "pct_chg"})})


# 数据表格
# table_graph = dcc.Graph(id="table",
#                         figure={"data": []})

table_graph = dash_table.DataTable(
    id='table',
    columns=[{"name": i, "id": i} for i in sh_index.head(10).columns],
    data=sh_index.head(10).to_dict('records'),
)

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div(children=[
                      html.H1("市场全景图"),
                      html.H2("主要指数走势"),
                      sh_index_graph,
                      hist_zd_graph,
                      hist_dist_graph,
                      table_graph
                      ],
                      style=main_style)


if __name__ == '__main__':
    app.run_server(debug=True)
