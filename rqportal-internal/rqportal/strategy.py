import json
from collections import OrderedDict

import pandas
from pymongo import DESCENDING

from .runinfo import _get_latest_backtest_run_ids, \
    _get_last_min_backtest_runtime
from .utils import get_strategy_collection, _convert_strategy_type

_collect = None
INCLUDE = 1
EXCLUDE = 0


_strategy_fields = (
    'algo-id',
    'title',
    'strategy-type',
    'remark',
    'pt',  # True: this algorithm participates in pt,
    'latest_bt_id',
)


_strategy_field_map = {
    'algo-id': 'id',
    'title': 'name',
    'strategy-type': 'stype',
    'remark': 'descriptor',
}


def _get_collect():
    global _collect
    if _collect is None:
        _collect = get_strategy_collection('versioned-strategies')
    return _collect


class Strategy:
    @classmethod
    def get(cls, user_id):
        ret = _get_collect().find(
            filter={
                'user-id': str(user_id),
            },
            projection={
                '_id': EXCLUDE,
                'id': INCLUDE,
                'version': INCLUDE,
                'name': INCLUDE,
                'lang': INCLUDE,
                'descriptor': INCLUDE,
                'hidden': INCLUDE,
                'stype': INCLUDE,
                'last-modified-timestamp': INCLUDE,
            },
            sort=[('id', DESCENDING)]
        )
        algoid_version_map = {}
        algoid_info_map = OrderedDict()
        for r in ret:
            if r.get('hidden'):
                continue
            algo_id = r[_strategy_field_map['algo-id']]
            version = r['version']
            old_version = -1 if algo_id not in algoid_version_map else algoid_version_map[algo_id]
            if version > old_version:
                algoid_info_map[algo_id] = r
                algoid_version_map[algo_id] = version

        if len(algoid_info_map) == 0:
            print('No any algorithm for this user {user_id}'.format(user_id=user_id))
            return None

        algo_ids = list(algoid_info_map.keys())
        algo_id_max_bt_runids = {algo_id: None if max_bt_runid is None else str(max_bt_runid) for algo_id, max_bt_runid in _get_latest_backtest_run_ids(algo_ids).items()}
        algo_id_min_last_runtime_map = _get_last_min_backtest_runtime(algo_ids)
        strategy_infos = [
            {
                'algo-id': algo_id,
                'title': algo_info[_strategy_field_map['title']],
                'strategy-type': _convert_strategy_type(algo_info.get(_strategy_field_map['strategy-type'])),
                'remark': json.loads(algo_info[_strategy_field_map['remark']])['content'] if _strategy_field_map['remark'] in algo_info else '',
                'latest_run_id': algo_id_max_bt_runids.get(algo_id),
                'can_run_pt': True if algo_id in algo_id_min_last_runtime_map and int(algo_info['last-modified-timestamp']) < int(algo_id_min_last_runtime_map[algo_id]) else False
            }
            for algo_id, algo_info in algoid_info_map.items()
        ]

        result = pandas.DataFrame(strategy_infos)
        return result.set_index('algo-id')





