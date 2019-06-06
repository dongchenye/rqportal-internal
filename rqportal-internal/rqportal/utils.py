import datetime

import six
from pandas import DataFrame
from pymongo import MongoClient
from dateutil.parser import parse as parse_date

from .const import StrategyType

# feeds for stock or mix strategies
_feeds_conf = None
_feeds_collections = {}

# feeds for future strategies
_future_feeds_conf = None
_future_feeds_collections = {}

# runinfo for all strategies
_runinfo_conf = None
_runinfo_collection = None

# strategy
_strategy_conf = None
_strategy_collection = None

_supported_runtype = None


def init_with(conf):
    global _feeds_conf, _runinfo_conf, _supported_runtype, _future_feeds_conf, _strategy_conf
    _feeds_conf = conf.get("feeds")
    _future_feeds_conf = conf.get('future_feeds')
    _runinfo_conf = conf.get("runrecord")
    _supported_runtype = conf.get("supported_runtype")
    _strategy_conf = conf.get("strategy")


def get_runinfo_collection(name: str):
    global _runinfo_collection, _runinfo_conf
    if not _runinfo_collection:
        url = _runinfo_conf['url']
        database = _runinfo_conf['database']
        _runinfo_collection = MongoClient(url).get_database(database)
    return _runinfo_collection[name]


def get_strategy_collection(name: str):
    global _strategy_collection
    if not _strategy_collection:
        url = _strategy_conf['url']
        database = _strategy_conf['database']
        _strategy_collection = MongoClient(url).get_database(database)
    return _strategy_collection[name]


def get_feeds_collections(name: str, run_id: int, run_type, strategy_type):
    if None in (run_type, strategy_type, ):
        return []

    if run_type not in _get_supported_runtype():
        run_type = "Backtest" if run_type == 'bt' else "Paper Trading"
        raise NotImplementedError('ERROR: {} does not support.'.format(run_type))

    global _feeds_collections, _feeds_conf, _future_feeds_conf, _future_feeds_collections
    if strategy_type == StrategyType.FUTURE:
        fd_conf = _future_feeds_conf
        fd_collections = _future_feeds_collections
    else:
        fd_conf = _feeds_conf
        fd_collections = _feeds_collections
    if len(fd_collections) == 0:
        for conf in fd_conf:
            start_id = conf['startid']
            end_id = conf['endid']
            if end_id < 0:
                end_id = float('inf')
            url = conf['url']
            database = conf['database']
            runtype = conf['runtype']
            collect = MongoClient(url).get_database(database)
            fd_collections.setdefault(runtype, dict()) \
                .setdefault((start_id, end_id), list()).append(collect)

    startend_collects = fd_collections.get(run_type)
    if startend_collects is None:
        raise RuntimeError(
            'runtype {} does not exist in config feeds'.format(run_type))

    cols = None
    for (start_id, end_id), collects in startend_collects.items():
        if start_id <= run_id <= end_id:
            cols = collects
            break
    if cols is None:
        print('ERROR: run_id %d is not in any collections')
        return None
    return [col[name] for col in cols]


def _get_supported_runtype():
    global _supported_runtype
    return tuple(_supported_runtype)


def date2datetime(date: int):
    year, r = divmod(date, 10000)
    month, day = divmod(r, 100)
    return datetime.datetime(year=year, month=month, day=day)


def intdate2date(date: int):
    year, r = divmod(date, 10000)
    month, day = divmod(r, 100)
    return datetime.date(year=year, month=month, day=day)


def time2datetime(time: int):
    # 150000000
    hour, r = divmod(time, 10000000)
    minute, r = divmod(r, 100000)
    second, milli = divmod(r, 1000)
    return datetime.timedelta(hours=hour, minutes=minute,
                              seconds=second, milliseconds=milli)


def entry_date2date(df: DataFrame):
    df["date"] = df["entry_date"].apply(lambda x: intdate2date(int(x)))
    del df["entry_date"]
    df.set_index("date", inplace=True)


def entry_datetime2datetime(df: DataFrame):
    df["datetime"] = df["entry_date"].apply(lambda x: date2datetime(int(x)))
    if "entry_time" in df.columns.values:
        df["datetime"] += df["entry_time"].apply(
            lambda x: time2datetime(int(x)))
        del df["entry_time"]
    del df["entry_date"]
    df.set_index(["datetime"], inplace=True)


def to_date_int(ds):
    if ds is None:
        return
    if isinstance(ds, six.string_types):
        ds = parse_date(ds)
    elif isinstance(ds, int):
        return ds
    year, month, day = ds.year, ds.month, ds.day
    return year*10000 + month*100 + day


def _convert_strategy_type(value):
    if value == 's' or value is None:
        return StrategyType.STOCK
    elif value == 'f':
        return StrategyType.FUTURE
    elif value == 'a':
        return StrategyType.MIX
    else:
        return StrategyType.UNKNOWN