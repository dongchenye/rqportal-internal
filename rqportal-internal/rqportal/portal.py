from typing import List, Dict

from bson import SON
from pandas import DataFrame
from pymongo import ASCENDING, DESCENDING

from .const import RunType, PORTFOLIO_TYPE, PortfolioType, SUB_PORTFOLIOS, \
    ENTRY_DATE, ENTRY_TIME
from .fields import portfolio_map, tradedate_map, benchmark_reverted_map, \
    position_map, \
    trades_map, future_position_map, stock_position_map, future_portfolio_map, \
    risk_map
from .runinfo import RunInfo
from .utils import get_feeds_collections, entry_datetime2datetime, \
    entry_date2date, to_date_int


def _mongo_filter(run_id: int, start_date: int = None, end_date: int = None):
    mongo_filter = {"run-id": run_id}
    entry_date = tradedate_map["entry_date"]
    if start_date and isinstance(start_date, int):
        mongo_filter[entry_date] = {"$gte": start_date}
    if end_date and isinstance(end_date, int):
        if mongo_filter.get(entry_date):
            mongo_filter.get(entry_date)["$lte"] = end_date
        else:
            mongo_filter[entry_date] = {"$lte": end_date}
    return mongo_filter


def _run_type(run_id):
    ret = RunInfo.get(run_id)
    if ret is None:
        return None
    runtype = ret.get('run-type')
    if runtype is None:
        raise RuntimeError(
            'Internal Error: run-type was missing for run_id {}'.format(
                runtype))
    if runtype in (RunType.BACKTEST, RunType.BUILD_BACKTEST):
        runtype = 'bt'
    elif runtype == RunType.PAPER_TRADING:
        runtype = 'pt'
    else:
        raise RuntimeError(
            'Internal Error: Unsupported run-type {} for run_id {}'.format(
                runtype, run_id))
    return runtype


def _strategy_type(run_id):
    info = RunInfo.get(run_id)
    if info is None:
        return None
    strategy_type = info.get('strategy-type')
    if strategy_type is None:
        raise RuntimeError(
            'Internal Error: strategy-type was missing for run_id {}'.format(
                strategy_type))
    return strategy_type


def _get_collections(collect_name, run_id):
    run_type = _run_type(run_id)
    if run_type is None:
        return []
    strategy_type = _strategy_type(run_id)
    if strategy_type is None:
        return []
    return get_feeds_collections(collect_name, run_id, run_type, strategy_type)


def _find_feeds(collect_name, run_id, mongo_filter, projection, sort=None,
                first=None):
    ret = []
    projection["_id"] = 0
    for collect in _get_collections(collect_name, run_id):
        if first is None:
            ret = list(collect.find(
                filter=mongo_filter, projection=projection, sort=sort
            ))
        else:
            ret = collect.find_one(
                filter=mongo_filter, projection=projection, sort=sort
            )

        if ret is None or len(ret) == 0:
            continue
        else:
            break
    return ret


def _aggregate_feeds(collect_name, run_id, aggregate_list):
    ret = []
    for collect in _get_collections(collect_name, run_id):
        ret = list(collect.aggregate(aggregate_list, allowDiskUse=True))
        if len(ret) == 0:
            continue
        else:
            break
    return ret


def _last_portfolio(run_id, fields, collection_name):
    return _find_feeds(
        collect_name=collection_name,
        run_id=run_id,
        mongo_filter=_mongo_filter(run_id),
        projection={field: 1 for field in fields},
        sort=[(portfolio_map["entry_date"], DESCENDING)],
        first=True
    )


def _portfolio(run_id: int, start_date: int = None, end_date: int = None,
               fields: List[str] = None) -> List[Dict]:
    mongo_filter = _mongo_filter(run_id, start_date, end_date)
    project = {}
    if fields:
        for field in fields:
            project[field] = 1
    else:
        for field in portfolio_map.values():
            project[field] = 1

    sort = [(portfolio_map["entry_date"], ASCENDING)]
    return _find_feeds("portfolio", run_id, mongo_filter, project, sort)


def _sub_portfolios(run_id: int, portfolio_type, start_date=None,
                    end_date=None):
    start_date = to_date_int(start_date)
    end_date = to_date_int(end_date)
    mongo_filter = _mongo_filter(run_id, start_date, end_date)
    project = {
        SUB_PORTFOLIOS: 1,
    }
    sort = [(portfolio_map["entry_date"], ASCENDING)]
    ret = _find_feeds("portfolio", run_id, mongo_filter, project, sort)

    if portfolio_type == PortfolioType.Stock:
        p_map = portfolio_map
    elif portfolio_type == PortfolioType.Future:
        p_map = future_portfolio_map
    else:
        print("Internal Error: Unsupported Portfolio Type {}".format(
            portfolio_type))
        return
    portfolios = []
    for r in ret:
        for _, sub_port in r[SUB_PORTFOLIOS].items():
            if sub_port[PORTFOLIO_TYPE] != portfolio_type:
                continue
            portfolios.append({
                field: sub_port.get(field, 0) for field in p_map.values()
            })
    df = DataFrame(portfolios)
    if df.empty:
        return df
    invert_map = {v: k for k, v in p_map.items()}
    df.rename(columns=invert_map, inplace=True)
    entry_date2date(df)
    return df


def _benchmark_portfolio(run_id: int, start_date: int = None,
                         end_date: int = None) -> DataFrame:
    mongo_filter = _mongo_filter(run_id, start_date, end_date)
    project = {
        portfolio_map["entry_date"]: 1,
        portfolio_map["daily_returns"]: 1
    }

    sort = [(portfolio_map["entry_date"], ASCENDING)]
    ret = _find_feeds("benchmark-portfolio", run_id, mongo_filter, project,
                      sort)
    df = DataFrame(list(ret))
    if df.empty:
        return df
    df.rename(columns=benchmark_reverted_map, inplace=True)
    entry_date2date(df)

    return df


def _stock_positions(run_id: int, start_date=None,
                     end_date=None):
    start_date = to_date_int(start_date)
    end_date = to_date_int(end_date)
    mongo_filter = _mongo_filter(run_id, start_date, end_date)
    mongo_filter[PORTFOLIO_TYPE] = PortfolioType.Stock
    project = {}
    for field in stock_position_map.values():
        project[field] = 1
    sort = [(position_map["entry_date"], ASCENDING)]
    ret = _find_feeds("position", run_id, mongo_filter, project, sort)
    df = DataFrame(list(ret))
    if df.empty:
        return df
    invert_map = {v: k for k, v in stock_position_map.items()}
    df.rename(columns=invert_map, inplace=True)
    df.fillna(inplace=True, value=0)
    entry_date2date(df)
    return df


def _future_positions(run_id: int, start_date=None,
                      end_date=None):
    start_date = to_date_int(start_date)
    end_date = to_date_int(end_date)
    mongo_filter = _mongo_filter(run_id, start_date, end_date)
    mongo_filter[PORTFOLIO_TYPE] = PortfolioType.Future
    project = {}
    for field in future_position_map.values():
        project[field] = 1
    sort = [(position_map["entry_date"], ASCENDING)]
    ret = _find_feeds("position", run_id, mongo_filter, project, sort)
    adjust_ret = []
    for r in ret:
        adjust_dict = {}
        for k, v in r.items():
            if isinstance(v, dict):
                for sk, se in v.items():
                    adjust_dict[".".join((k, sk))] = se
            else:
                adjust_dict[k] = v
        adjust_ret.append(adjust_dict)

    df = DataFrame(list(adjust_ret))
    if df.empty:
        return df

    invert_map = {}
    for k, v in future_position_map.items():
        if isinstance(v, dict):
            for sk, se in v.items():
                invert_map[".".join((k, sk))] = se
        else:
            invert_map[v] = k
    df.rename(columns=invert_map, inplace=True)
    df.fillna(inplace=True, value=0)
    entry_date2date(df)
    return df


def portfolio(run_id: int, start_date=None,
              end_date=None, contain_benchmark=True) -> DataFrame:
    start_date = to_date_int(start_date)
    end_date = to_date_int(end_date)
    ret = _portfolio(run_id=run_id, start_date=start_date, end_date=end_date,
                     fields=None)
    df = DataFrame(ret)
    if df.empty:
        print('WARN: No portfolio record for this run-id %d' % run_id)
        return df
    invert_map = {v: k for k, v in portfolio_map.items()}
    df.rename(columns=invert_map, inplace=True)
    entry_date2date(df)

    if contain_benchmark:
        benchmark_portfolio = _benchmark_portfolio(run_id, start_date,
                                                   end_date)
        ret = df.merge(benchmark_portfolio, how="left", left_index=True,
                       right_index=True)
        ret.fillna(inplace=True, value=0)
        return ret

    df.fillna(inplace=True, value=0)
    return df


def positions(run_id: int, values="market_value",
              start_date=None, end_date=None) -> DataFrame:
    start_date = to_date_int(start_date)
    end_date = to_date_int(end_date)
    cash_list = _portfolio(run_id=run_id, start_date=start_date,
                           end_date=end_date,
                           fields=[portfolio_map["cash"], portfolio_map["entry_date"]])
    if len(cash_list) == 0:
        print("Empty cash!")
        return DataFrame()

    match_filter = _mongo_filter(run_id, start_date, end_date)
    project = {
        position_map["order_book_id"]: 1,
        position_map["entry_date"]: 1,
        "_id": 0,
    }
    push_value = position_map['market_value']
    if values == "market_value":
        project[position_map['market_value']] = 1
    elif values == "total_cost":
        project[values] = {
            "$subtract": [
                "$" + position_map["bought_value"],
                "$" + position_map["sold_value"]
            ]
        }
        push_value = values
    else:
        print(
            "Invalid Parameter for values. It should be market_value/total_cost")
        return DataFrame()

    aggregate_list = [
        {"$match": match_filter},
        {"$project": project},
        {"$group": {
            "_id": {
                "entry_date": "$" + position_map["entry_date"],
            },
            "id_hold": {
                "$push": {
                    "order_book_id": "$" + position_map["order_book_id"],
                    values: "$" + push_value,
                }
            },
        }},
        {"$sort": SON([('_id.entry_date', 1), ('_id.entry_time', 1)])},
        # keep the order of keys
    ]

    ret = _aggregate_feeds("position", run_id, aggregate_list)
    df = DataFrame(cash_list)
    if df.empty:
        print('WARN: No position record for this run-id %d' % run_id)
        return df
    df.rename(columns={"8351": "cash", "272": "entry_date",}, inplace=True)
    entry_date2date(df)
    items = []
    for element in ret:
        item_dict = dict()
        for item in element["id_hold"]:
            item_dict[item["order_book_id"]] = item.get(values, 0)
        item_dict.update(element["_id"])
        items.append(item_dict)
    position_df = DataFrame(items)
    if len(items) != 0:
        entry_date2date(position_df)
    ret = df.merge(position_df, how="left", left_index=True, right_index=True)
    ret.fillna(inplace=True, value=0)
    return ret


def latest_positions(run_id):
    latest_entry = _find_feeds(
        collect_name="position",
        run_id=run_id,
        mongo_filter={"run-id": run_id},
        projection={
            "_id": 0,
            position_map["entry_date"]: 1,
            position_map["entry_time"]: 1,
        },
        sort=[(position_map["entry_date"], DESCENDING),
              (position_map["entry_time"], DESCENDING)],
        first=True
    )
    if latest_entry is None:
        print("WARN: there is no any position for run_id {}".format(run_id))
        return
    latest_entry["run-id"] = run_id
    ret = _find_feeds(
        collect_name="position",
        run_id=run_id,
        mongo_filter=latest_entry,
        projection={position_map[key]: 1 for key in position_map.keys()},
    )
    df = DataFrame(ret)
    if df.empty:
        print('WARN: No portfolio record for this run-id %d' % run_id)
        return df
    df.rename(columns={v: k for k, v in position_map.items()}, inplace=True)
    entry_datetime2datetime(df)
    return df


def trades(run_id: int, start_date=None,
           end_date=None, show_id=False) -> DataFrame:
    start_date = to_date_int(start_date)
    end_date = to_date_int(end_date)
    mongo_filter = _mongo_filter(run_id, start_date, end_date)
    project = {
        "_id": 0, trades_map["entry_date"]: 1,
        trades_map["entry_time"]: {
            "$ifNull": ["$" + trades_map["entry_time"], 150000000]},
        trades_map["last_quantity"]: 1,
        trades_map["last_price"]: 1,
        trades_map["order_book_id"]: 1,
        trades_map["side"]: {
            "$cond": {"if": {"$eq": ["$" + trades_map["side"], "1"]},
                      "then": "BUY", "else": "SELL"}},
        trades_map["commission"]: {
            "$ifNull": ["$" + trades_map["commission"], 0]},
        trades_map["tax"]: {"$ifNull": ["$" + trades_map["tax"], 0]},
        trades_map["position_effect"]: {
            "$cond": {
                "if": {"$eq": ["$" + trades_map["position_effect"], "C"]},
                "then": "CLOSE",
                "else": {
                    "$cond": {
                        "if": {
                            "$eq": ["$" + trades_map["position_effect"], "O"]},
                        "then": "OPEN", "else": ""
                    },
                }},
        },
        trades_map["exec_id"]: 1,
        trades_map["order_id"]: 1,
    }
    if show_id:
        project[trades_map["trade_id"]] = 1

    aggregate_list = [
        {"$match": mongo_filter},
        {"$project": project},
        {"$project": {
            "entry_date": "$" + trades_map["entry_date"],
            "entry_time": "$" + trades_map["entry_time"],
            "last_quantity": "$" + trades_map["last_quantity"],
            "side": "$" + trades_map["side"],
            "last_price": "$" + trades_map["last_price"],
            "trade_id": "$" + trades_map["trade_id"],
            "order_book_id": "$" + trades_map["order_book_id"],
            "transaction_cost": {
                "$add": [
                    "$" + trades_map["commission"],
                    "$" + trades_map["tax"]
                ]
            },
            "position_effect": "$" + trades_map["position_effect"],
            "exec_id": "$" + trades_map["exec_id"],
            "order_id": "$" + trades_map["order_id"],
            "commission": "$" + trades_map["commission"],
            "tax": "$" + trades_map["tax"],
        }},
        {"$sort": SON([('entry_date', 1), ('entry_time', 1)])},
        # keep the order of keys
    ]

    ret = _aggregate_feeds("trade", run_id, aggregate_list)
    df = DataFrame(list(ret))
    if df.empty:
        print('WARN: No trade record for this run-id %d' % run_id)
        return df
    df.fillna(inplace=True, value=0)
    entry_datetime2datetime(df)

    return df


def last_risk(run_id):
    ret = _find_feeds(
        collect_name="risk",
        run_id=run_id,
        mongo_filter=_mongo_filter(run_id),
        projection={risk_map[key]: 1 for key in risk_map.keys()},
        sort=[(ENTRY_DATE, DESCENDING), (ENTRY_TIME, DESCENDING)],
        first=True
    )
    new_risk = {}
    for k, v in risk_map.items():
        new_risk[k] = ret.get(v, 0)
    return new_risk
