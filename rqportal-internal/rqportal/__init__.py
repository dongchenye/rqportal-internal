#!/usr/bin/env python
#
# Copyright 2016 Ricequant All Rights Reserved
#
# This is the ricequant risk analytics for backtesting result.
#
from .report import Report
from .utils import init_with
from .portal import portfolio, positions, trades, latest_positions
from .config import RQConfig
from .runinfo import RunInfo
from .strategy import Strategy

_inited = False

__all__ = [
    'init',
    'positions',
    'latest_positions',
    'portfolio',
    'trades',
    'RunInfo',
    'Report',
    'Strategy',
]


def init(config_path=None):
    global _inited
    if _inited:
        print('WARN: already inited')
        return

    conf = RQConfig(config_path)
    init_with(conf)
    _inited = True
