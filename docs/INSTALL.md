# 解决依赖
linux 平台talib安装

```
tar xf ta-lib-0.4.0-src.tar.gz

./configure --prefix=/home/anaconda3
make
make install

export PREFIX=/home/anaconda3
export TA_LIBRARY_PATH=$PREFIX/lib
export TA_INCLUDE_PATH=$PREFIX/include
pip3 install ta-lib
```

linux 平台matplotlib字体问题
```
wget https://www.wfonts.com/download/data/2014/06/01/simhei/simhei.zip
cp ~/Downloads/SimHei.ttf /home/anaconda3/lib/python3.7/site-packages/matplotlib/mpl-data/fonts/ttf

rm -fr ~/.cache/matplotlib

plt.rcParams['font.sans-serif'] = ['simhei']  # 指定默认字体
plt.rcParams['axes.unicode_minus'] = False   # 解决保存图像是负号'-'显示为方块的问题
```

安装mpl-finance
```
pip install https://github.com/matplotlib/mpl_finance/archive/master.zip
```