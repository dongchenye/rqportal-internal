import datetime
import json

import numpy
import pandas
from pandas import DataFrame
from pymongo import ASCENDING

from .fields import run_info_map
from .utils import get_runinfo_collection, intdate2date, _convert_strategy_type

_run_type = {
    'backtest': 'b',
    'build_backtest': 't',
    'paper_trading': 'p',
    'real_trading': 'r',
}

_run_type_revert = {
    'b': 'backtest',
    't': 'build_backtest',
    'p': 'paper_trading',
    'r': 'real_trading',
}

_hammer_status = {
    'started': '2',
    'normal_exit': '3',
    'paused': '8',

    'abnormal_exit': '4',
    'fail_start': 'F',
    'stop_exit': 'B',
    'deleted': 'L',
    'unknown': '\uFFFF',
}

_roles = {
    'admin': '3',
}

_time_units = {
    '2': 'Day',
    '4': 'Minute',
}

_run_record_project = {
    '_id': 0,
    'user-name': 1,
    'user-id': 1,
    'run-id': 1,
    'algo-id': 1,
    'title': 1,
    'strategy-type': 1,
    'time-unit': 1,
    'run-type': 1,
    'start-date': 1,
    'end-date': 1,
    'init-cash': 1,
    'start-time': 1,
    'end-time': 1,
}

_pt_run_record_project = {
    '_id': 0,
    'user-name': 1,
    'user-id': 1,
    'run-id': 1,
    'algo-id': 1,
    'title': 1,
    'strategy-type': 1,
    'time-unit': 1,
    'start-time': 1,
    'end-time': 1,
}

_bt_run_record_project = {
    '_id': 0,
    'user-name': 1,
    'user-id': 1,
    'run-id': 1,
    'algo-id': 1,
    'title': 1,
    'strategy-type': 1,
    'time-unit': 1,
    'start-date': 1,
    'end-date': 1,
    'init-cash': 1,
    'start-time': 1,
    'end-time': 1,
}

_pt_runinfo_fields = (
    'algo-id',
    'user-name',
    'user-id',
    'user-id',
    'title',
    'strategy-type',
    'start-time',
    'latest_backtest_run_id',
)

_runinfo_fields = (
    'algo-id',
    'user-name',
    'user-id',
    'title',
    'strategy-type',
    'time-unit',
    'start-date',
    'end-date',
    'init-cash',
    'start-time',
    'end-time',
)

_run_record_collect = None
_algo_last_runtime_collect = None


def _get_collect():
    global _run_record_collect
    if _run_record_collect is None:
        _run_record_collect = get_runinfo_collection('run-record')
    return _run_record_collect


def _get_last_runtime_collect():
    global _algo_last_runtime_collect
    if _algo_last_runtime_collect is None:
        _algo_last_runtime_collect = get_runinfo_collection('algo-last-run-time')
    return _algo_last_runtime_collect


def _get_last_min_backtest_runtime(algo_ids):
    ret = _get_last_runtime_collect().find(
        filter={
            'algo-id': {'$in': algo_ids}
        },
        projection={
            '_id': 0,
            'algo-id': 1,
            'last-min-backtest-run-start-time': 1,
        }
    )
    algo_id_last_min_runtime_map = {}
    for r in ret:
        if 'last-min-backtest-run-start-time' not in r:
            continue
        algo_id_last_min_runtime_map[r['algo-id']] = r['last-min-backtest-run-start-time']
    return algo_id_last_min_runtime_map


def _get_latest_backtest_run_ids(algo_ids=None):
    match_filter = {
        '$or': [
            {'run-type': _run_type['backtest']},
        ],
        'life-cycle-status': _hammer_status['normal_exit'],
    }
    if algo_ids is not None:
        match_filter['algo-id'] = {'$in': algo_ids}
    ret = _get_collect().aggregate([
        {'$match': match_filter},
        {'$project': {
            '_id': 0,
            'run-id': 1,
            'algo-id': 1,
            'start-time': 1,
        }},
        {'$group': {
            '_id': {'algo-id': '$algo-id'},
            'latest_run_id': {'$max': '$run-id'},
        }}
    ])
    algo_id_max_bt_runids = {}
    for r in ret:
        algo_id_max_bt_runids[r['_id']['algo-id']] = r['latest_run_id']
    return algo_id_max_bt_runids


def _standardize_runinfo(run_id):
    ret = _get_collect().find_one(
        filter={'run-id': run_id},
        projection={'_id': 0, 'source-code': 0},
    )
    if ret is None:
        print('ERROR: This run-id {} does not exist.'.format(run_id))
        return
    invert_map = {v: k for k, v in run_info_map.items()}
    stand_ret = {'stock_starting_cash': 0, 'future_starting_cash': 0}
    for k, v in ret.items():
        if k == 'strategy-extended-config':
            json_value = json.loads(v)
            stand_ret['commission_multiplier'] = json_value.get(run_info_map['commission_multiplier'], None)
            stand_ret['slippage'] = json_value.get(run_info_map['slippage'], None)
            stand_ret['benchmark'] = json_value.get(run_info_map['benchmark'], None)
            stand_ret['matching_type'] = json_value.get(run_info_map['matching_type'], None)
            stand_ret['margin_multiplier'] = json_value.get(run_info_map['margin_multiplier'], None)
        elif k in ('start-date', 'end-date'):
            stand_ret[invert_map[k]] = intdate2date(v)
        elif k == 'strategy-type':
            stand_ret[invert_map[k]] = _convert_strategy_type(v)
        elif k == "time-unit":
            stand_ret[invert_map[k]] = _convert_frequency(v)
        elif k == 'run-type':
            stand_ret[invert_map[k]] = 'PAPER_TRADING' if v == 'p' else 'BACKTEST'
        elif k == 'run-des':
            stand_ret[invert_map[k]] = json.loads(v).get('content', '')
        elif invert_map.get(k) is not None:
            stand_ret[invert_map[k]] = v
    stand_ret['starting_cash'] = stand_ret['future_starting_cash'] + stand_ret['stock_starting_cash']
    if not stand_ret.get('remark'):
        stand_ret['remark'] = ''
    return stand_ret


def _convert_frequency(value):
    return 'Day' if value == '2' else 'Minute'


def _parse_value(field_name, value):
    if field_name == 'strategy-type':
        return _convert_strategy_type(value)
    elif field_name in ('start-time', 'end-time',):
        return pandas.NaT if value is None \
            else datetime.datetime(1970, 1, 1, 8) + datetime.timedelta(
                milliseconds=value)
    elif field_name == 'time-unit':
        return 'Day' if value == '2' else 'Minute'
    elif field_name == 'run-type':
        return _run_type_revert[value]
    else:
        return value


class RunInfo:
    _runid_info_map = {}

    @classmethod
    def get(cls, run_id):
        if cls._runid_info_map.get(run_id) is not None:
            return cls._runid_info_map.get(run_id)

        ret = _get_collect().find_one(
            filter={'run-id': run_id},
            projection=_run_record_project,
        )
        if ret is None:
            print('ERROR: This run-id {} does not exist.'.format(run_id))
            return
        for key, value in ret.items():
            ret[key] = _parse_value(key, value)
        cls._runid_info_map[run_id] = ret
        return ret

    @staticmethod
    def running_pts():
        ret = _get_collect().find(
            filter={
                'run-type': _run_type['paper_trading'],
                'life-cycle-status': {
                    '$nin': [
                        _hammer_status['normal_exit'],
                        _hammer_status['abnormal_exit'],
                        _hammer_status['fail_start'],
                        _hammer_status['stop_exit'],
                        _hammer_status['deleted'],
                        _hammer_status['unknown'],
                    ]
                },
            },
            projection=_pt_run_record_project,
            sort=[('run-id', ASCENDING)]
        )
        n_run_ids = ret.count()
        n_fields = len(_pt_runinfo_fields)
        array = numpy.ndarray((n_run_ids, n_fields), dtype=object)
        array.fill(numpy.nan)
        run_ids = []
        run_id_algo_id_map = {}
        r_cnt = 0
        for r in ret:
            run_id = r.get('run-id')
            for i in range(n_fields):
                field_name = _pt_runinfo_fields[i]
                r_value = r.get(field_name)
                array[r_cnt, i] = _parse_value(field_name, r_value)
                if field_name == 'algo-id':
                    run_id_algo_id_map[run_id] = r_value
                else:  # do nothing
                    pass
            run_ids.append(run_id)
            r_cnt += 1

        algo_id_max_bt_runids = _get_latest_backtest_run_ids(
            list(run_id_algo_id_map.values()))
        for i in range(n_run_ids):
            run_id = run_ids[i]
            max_bt_runid = algo_id_max_bt_runids.get(
                run_id_algo_id_map[run_id])
            array[
                i, n_fields - 1] = numpy.nan if max_bt_runid is None else max_bt_runid

        ret = DataFrame(data=array, index=run_ids, columns=_pt_runinfo_fields)
        ret.index.name = 'run-id'
        return ret

    @staticmethod
    def latest_bts(algo_ids=None):
        if algo_ids and isinstance(algo_ids, int):
            algo_ids = [algo_ids]
        latest_runids = list(_get_latest_backtest_run_ids(algo_ids).values())
        ret = _get_collect().find(
            filter={'run-id': {'$in': latest_runids}},
            projection=_bt_run_record_project,
            sort=[('run-id', ASCENDING)],
        )
        n_run_ids = ret.count()
        n_fields = len(_runinfo_fields)
        array = numpy.ndarray((n_run_ids, n_fields), dtype=object)
        array.fill(numpy.nan)
        run_ids = []
        r_cnt = 0
        for r in ret:
            run_id = r.get('run-id')
            for i in range(n_fields):
                field_name = _runinfo_fields[i]
                r_value = r.get(field_name)
                array[r_cnt, i] = _parse_value(field_name, r_value)
            run_ids.append(run_id)
            r_cnt += 1

        ret = DataFrame(data=array, index=run_ids, columns=_runinfo_fields)
        ret.index.name = 'run-id'
        return ret
