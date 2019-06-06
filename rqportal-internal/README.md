# Rqportal Internal

## 简介
这个python模块主要用于获取用户回测策略的portfolio, trade和position的feeds, 用户可以获取指定时间区间的各种feeds的信息。

## 安装
```
# 安装rqportal-internal
pip install -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com --extra-index-url https://ricequant:RiceQuant77@pypi.ricequant.com:8080/simple/  rqportal-internal


# 升级rqportal-internal
pip install --extra-index-url https://ricequant:RiceQuant77@pypi.ricequant.com:8080/simple/ -U --no-deps rqportal-internal

```

## 使用说明
```python
import rqportal

# 初始化rqportal, 主要用于加载配置
rqportal.init()

# 获取指定run ID的positions
rqportal.positions(run_id=2227)

# 获取指定run ID的portfolio
rqportal.portfolio(run_id=2227)

# 获取指定run ID的trades
rqportal.trades(run_id=2227)
```

```python

import rqportal
from rqportal import *

rqportal.init()

RunInfo.get(2227)

RunInfo.running_pts()

RunInfo.latest_bts()

```

## API
### init - 初始化rqportal internal
```
init(config_path=None, online=False)
```
#### 参数
> 参数 | 类型 | 说明
> -- | -- | --
> config_path | *str* | 配置文件的绝对路径, 如果为None, 我们使用默认的配置, 默认配置如下
> online | *True/False* | 如果为True, rqportal 查询线上的数据库; 否则查询内网的数据库, 具体可参考默认配置文件

#### 默认配置文件
```
feeds:
  - url: mongodb://root:root@192.168.10.152:27017
    database: pull
    startid: 0  # minimum runid
    endid: -1
    runtype: bt
  - url: mongodb://root:root@192.168.10.152:27017
    database: pull
    startid: 0  # minimum runid
    endid: -1
    runtype: pt

runrecord:
  url: mongodb://root:root@192.168.10.152:27017
  database: pull

supported_runtype:
  - bt
```

---

###portfolio - 获取回测每日收益数据, 非累积值

```
portfolio(run_id, start_date=None, end_date=None)
```
#### 参数
> 参数 | 类型 | 说明
> -- | -- | --
> run_id | *int* | 回测运行ID, 可从回测历史列表中获取
> start_date | *str* | 开始日期, 格式为 'YYYY-mm-dd', 默认从回测最早的日期开始
> end_date | *str* | 结束日期, 格式为 'YYYY-mm-dd', 默认以回测最晚的日期结束

#### 返回

*pandas DataFrame* - 收益
每列的定义可参考<a href="https://www.ricequant.com/api/python/chn#object-portfolio" target="\_blank">Python API文档</a>

#### 范例

- 获取回测ID为2012的每日收益数据

```
In: portfolio(2012)
Out:
                  daily_returns	pnl	total_returns	annualized_returns	cash	benchmark_daily_returns
2010-01-04 15:00:00	0.000000	0.00	0.000000	0.000000	100000.000000	-0.017267
2010-01-05 15:00:00	0.000000	0.00	0.000000	0.000000	100000.000000	0.007915
...
2015-11-03 15:00:00	-0.032762	-12187.12	2.598044	0.245341	467.473962	-0.002924
2015-11-04 15:00:00	0.069233	24910.28	2.847147	0.259573	467.473962	0.045671

```

- 获取回测ID为2012的一段时间内每日收益数据

```
In: portfolio(2012, start_date="2011-09-10", end_date="2011-10-20")
Out:
	                daily_returns	pnl	total_returns	annualized_returns	cash	benchmark_daily_returns
2011-09-13 15:00:00	-0.000128	-16.014597	0.246833	0.139163	65724.616896	0.000000
2011-09-14 15:00:00	-0.000596	-74.260000	0.246090	0.138523	65724.616896	-0.006299
2011-09-15 15:00:00	-0.000294	-36.660000	0.245724	0.138088	65724.616896	-0.001430
2011-09-16 15:00:00	-0.001494	-186.120000	0.243863	0.136851	65724.616896	0.001742
2011-09-19 15:00:00	-0.007149	-889.240000	0.234970	0.131392	65724.616896	-0.019277
2011-09-20 15:00:00	0.001499	185.180000	0.236822	0.132159	65724.616896	0.003799

```
---
### positions - 获取每日投资组合中每个证券持仓数据
```
positions(run_id, values="market_value", start_date=None, end_date=None)
```

#### 参数
> 参数 | 类型 | 说明
> -- | -- | --
> run_id | *int* | 回测运行ID, 可从回测历史列表中获取
> values | *str* | 持仓数据种类 ("market_value"/"total_cost"), 默认值为"market_value". 如果values为"market_value", 返回的持仓数据为投资组合中该证券当天实时市场价值（未实现/平仓的价值）; 如果values为"total_cost", 返回的数据为投资组合中该证券当天的总买入的价值减去该证券的总卖出价值的绝对值
> start_date | *str* | 开始日期, 格式为 'YYYY-mm-dd', 默认从回测最早的日期开始
> end_date | *str* | 结束日期, 格式为 'YYYY-mm-dd', 默认以回测最晚的日期结束

#### 返回
*pandas DataFrame* - 每日投资组合中每个证券的市场价值或总花费

#### 范例
- 获取回测ID为2012的每日投资组合中每个证券的市场价值

```
In: positions(2012, values="market_value")
Out:
	                cash	000916.XSHE	000926.XSHE	002485.XSHE	600270.XSHG	600626.XSHG	601718.XSHG
...
2013-10-08 15:00:00	42.49148	9368.5	53664.72	1867.25	14056.25	38426.75	31464
2013-10-09 15:00:00	42.49148	9614.5	53376.20	1867.25	15470.00	40183.00	31464
...
2013-10-31 15:00:00	42.49148	8097.5	52799.16	1716.00	17485.00	37935.00	30438
2013-11-01 15:00:00	42.49148	7933.5	52943.42	1738.00	17696.25	37935.00	30552

```


- 获取回测ID为2012的每日投资组合中每个证券的总花费

```
In: positions(2012, values="total_cost")
Out:
                        cash	000916.XSHE	 000926.XSHE	002485.XSHE	600270.XSHG	     600626.XSHG	601718.XSHG
...
2013-10-08 15:00:00	42.49148	5949.65552	51235.214402	3141.44346	11333.306277	28355.134863	33289.89627
2013-10-09 15:00:00	42.49148	5949.65552	51235.214402	3141.44346	11333.306277	28355.134863	33289.89627
...
2013-10-31 15:00:00	42.49148	5949.65552	51235.214402	3141.44346	11333.306277	28355.134863	33289.89627
2013-11-01 15:00:00	42.49148	5949.65552	51235.214402	3141.44346	11333.306277	28355.134863	33289.89627

```

---
### latest_positions - 获取最新持仓数据
```
latest_positions(run_id)
```

#### 参数
> 参数 | 类型 | 说明
> -- | -- | --
> run_id | *int* | 运行ID, 可从回测历史列表中获取

#### 返回
*pandas DataFrame* - 最新持仓数据

#### 范例

```
In: latest_positions(1204221)
Out:
                     price order_book_id  bought_value  sold_value  quantity  \
datetime
2014-12-31 15:00:00  19.16   000050.XSHE   8906.861982         0.0     800.0
2014-12-31 15:00:00  11.11   002400.XSHE   8935.977750         0.0     700.0
2014-12-31 15:00:00   6.40   600361.XSHG   9876.132720         0.0    2400.0
2014-12-31 15:00:00  25.37   600549.XSHG   9036.100750         0.0     500.0
2014-12-31 15:00:00   2.89   600567.XSHG   9755.504530         0.0    4800.0
2014-12-31 15:00:00   4.68   600601.XSHG   9705.923620         0.0    3700.0
2014-12-31 15:00:00   5.71   600673.XSHG   9758.988810         0.0    2700.0
2014-12-31 15:00:00  18.02   600677.XSHG   9740.966670         0.0     900.0
2014-12-31 15:00:00  17.98   600804.XSHG   8999.055240         0.0     600.0
2014-12-31 15:00:00   7.28   603128.XSHG   9701.918700         0.0    1900.0

                     market_value          pnl
datetime
2014-12-31 15:00:00       15328.0  6421.138018
2014-12-31 15:00:00        7777.0 -1158.977750
2014-12-31 15:00:00       15360.0  5483.867280
2014-12-31 15:00:00       12685.0  3648.899250
2014-12-31 15:00:00       13872.0  4116.495470
2014-12-31 15:00:00       17316.0  7610.076380
2014-12-31 15:00:00       15417.0  5658.011190
2014-12-31 15:00:00       16218.0  6477.033330
2014-12-31 15:00:00       10788.0  1788.944760
2014-12-31 15:00:00       13832.0  4130.081300
```


---
### trades - 获取每日交易数据
```
trades(run_id, start_date=None, end_date=None, show_id=False)
```

#### 参数
> 参数 | 类型 | 说明
> -- | -- | --
> run_id | *int* | 回测运行ID, 可从回测历史列表中获取
> start_date | *str* | 开始日期, 格式为 'YYYY-mm-dd', 默认从回测最早的日期开始
> end_date | *str* | 结束日期, 格式为 'YYYY-mm-dd', 默认以回测最晚的日期结束
> show_id | *bool* | 是否显示Trade ID。True显示, False不显示

#### 返回

*pandas DataFrame* - 每日交易数据
quantity: 买入或卖出证券的股数, 正数为买入, 负数为卖出。
price: 成交价

#### 范例

```
In: trades(2012)
Out:
	                quantity	order_book_id	price
2010-07-12 09:31:00	5000	000926.XSHE	9.371513
2010-07-12 09:31:00	6600	600270.XSHG	7.198844
...
2015-08-12 09:31:00	-6800	600382.XSHG	14.821747
2015-09-14 09:31:00	4000	000623.XSHE	25.210971

```

---
### RunInfo 对象 - 获取回测和模拟交易的运行相关信息
```
RunInfo.get(run_id)
```

#### 参数
> 参数 | 类型 | 说明
> -- | -- | --
> run_id | *int* | 回测或模拟交易运行ID

#### 返回

*python dictionary* - 该run_id对应的运行相关的信息


```
RunInfo.running_pts()
```

#### 返回

*pandas DataFrame* - 所有运行中的模拟交易对应的相关信息
> latest_backtest_run_id: 该模拟交易对应的策略当前最新的回测run-id

#### 范例

```
In: RunInfo.running_pts()
Out:
       algo-id               user-name                     title  \
run-id
499         81        lk@ricequant.com                   test_pt
1897        83        793530610@qq.com         xueqiu_mount_test
1898        73        793530610@qq.com                       xxx
1899        49        793530610@qq.com                     dexxx
1900        17        793530610@qq.com          get_minute_price
4118        32    shenqiwanzhu@163.com                       222
5196       555  wuchenyu@ricequant.com               HistoryTest
5329       473    kangol@ricequant.com  grid 2016-03-29 21:32:12
5429       132      shujf111@gmail.com              交易模型模板
5430       130      shujf111@gmail.com                 格雷厄姆
5431       123      shujf111@gmail.com                  history3

       strategy-type                  start-time latest_backtest_run_id
run-id
499           Future  2016-06-12 13:01:09.643000                    498
1897          Future  2016-07-04 20:10:09.542000                   2285
1898          Future  2016-07-04 20:10:10.183000                   2032
1899          Future  2016-07-04 20:10:10.685000                    290
1900          Future  2016-07-04 20:10:12.150000                    840
4118           Stock  2016-09-22 11:18:42.054000                   4117
5196           Stock  2016-11-20 21:16:03.496000                   4997
5329           Stock  2016-11-28 16:26:30.435000                   4263
5429           Stock  2016-12-01 09:42:25.331000                   2176
5430           Stock  2016-12-01 10:10:03.782000                   2012
5431           Stock  2016-12-01 10:11:59.255000                   2013

```


```
RunInfo.latest_bts()
```

#### 返回

*pandas DataFrame* - 所有正常退出的回测对应的运行相关信息

#### 范例
```
In: RunInfo.latest_bts()
Out:
      algo-id               user-name  \
run-id
564         82      poppinlp@gmail.com
609         85        et@ricequant.com
610         86        et123@everet.org
616         80        lk@ricequant.com
...        ...                     ...

           title strategy-type time-unit  \
run-id
564          123        Future       Day
609         test        Future    Minute
610          123        Future       Day
616        is_st        Future       Day
...          ...           ...       ...

       start-date  end-date init-cash                  start-time  \
run-id
564      20140104  20150104    100000  2016-06-13 15:20:00.446000
609      20140104  20140131    100000  2016-06-15 18:37:35.562000
610      20140104  20150104    100000  2016-06-15 18:45:49.391000
616      20160409  20160510    100000  2016-06-15 20:48:35.650000
...           ...       ...       ...                         ...
```

---
### Report 对象 - 获取回测和模拟交易的运行相关信息
```
import rqportal
rqportal.init()

report = Report(run_id)  # 传入run_id, 初始化Report

# 生成回测报告
# 主要获取4个方面的数据: 各种风险指标、策略相关信息、收益等信息
report.summary()

# 获取股票、期货或混合策略的Portfolio数据
report.total_portfolios(start_date=None, end_date=None)

# 获取股票的Portfolio, Position数据
report.stock_portfolios(start_date=None, end_date=None)
report.stock_positions(start_date=None, end_date=None)

# 获取期货的Portfolio, Position数据
report.future_portfolios(start_date=None, end_date=None)
report.future_positions(start_date=None, end_date=None)

# 获取交易详情数据
report.trades(start_date=None, end_date=None)
```


