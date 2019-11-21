# -*- coding: utf-8 -*-
# @Author: youerning
# @Email: 673125641@qq.com
from pytdx.hq import TdxHq_API
from pytdx.params import TDXParams
from pytdx.config.hosts import hq_hosts
import os
from os import path


cur_dir = path.abspath(path.dirname(__file__))
data_path = path.join("data", "stock")
api = TdxHq_API(heartbeat=True, auto_retry=True) 
host = '119.147.212.81'
port = 7709
hy_file = path.join(cur_dir, 'stock.cfg')
years = 5



def get_hy():
    with open(hy_file) as rf:
        stk_lst = [line.split("|") for line in rf if len(line) > 8]

    return stk_lst

# def worker(market, code):
#     api = TdxHq_API()

def download():
    if not path.exists(data_path):
        os.makedirs(data_path)
    
    stk_lst = get_hy()
    
    with api.connect(host, port):
    # with api.connect(*hq_hosts[11][1:]):
        for item in stk_lst:
            market = item[0]
            code = item[1]
            data = []
            for i in range(years):
                new_data = api.get_security_bars(TDXParams.KLINE_TYPE_1HOUR, 
                                                 int(market), code, (years-i)*800, 800)

                if new_data:
                    data += new_data
                # data += api.get_index_bars(9, 1, code, (9-i)*200, 200)
            
            if data:
                fp = path.join(data_path, "%s.csv" % code)
                api.to_df(data).to_csv(fp, index=False)
                print("download %s|%s successfully" % (market, code))
            else:
                print("download %s|%s failed" % (market, code))
            # break

if __name__ == '__main__':
    download()