from os import path
from pytdx.hq import TdxHq_API
from pytdx.params import TDXParams
from pytdx.config.hosts import hq_hosts

ktype = TDXParams.KLINE_TYPE_1HOUR
api = TdxHq_API(heartbeat=True, auto_retry=True, multithread=True)
index_data_path = path.join("data", "tdx", "index")
host = '119.147.212.81'
port = 7709
years = 2
count = 800


def main():
    code = "000001"
    market = 1
    index_data_path = path
    fp = path.join(index_data_path, "%s.csv" % code)

    with api.connect(host, port):
        data = []
        for i in range(years):
            new_data = api.get_index_bars(ktype, int(market), code, (years - i - 1) * count, count)

            if new_data:
                data += new_data
        
        if data:
            api.to_df(data).to_csv(fp, index=False)
            print("下载指数 %s|%s 成功" % (market, code))
        else:
            print("下载指数 %s|%s 失败" % (market, code))


if __name__ == "__main__":
    main()
