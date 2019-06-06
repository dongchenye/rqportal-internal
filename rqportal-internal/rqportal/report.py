from functools import wraps

from rqportal.fields import portfolio_map
from .const import StrategyType, PortfolioType
from .portal import trades, _future_positions, _stock_positions, portfolio, \
    _sub_portfolios, last_risk, _last_portfolio
from .runinfo import RunInfo, _standardize_runinfo


def check_params(not_allowed_type=None):
    def _check_strategy_type(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            strategy_type = args[0]._strategy_type
            run_id = args[0]._run_id
            if strategy_type is None:
                print("ERROR: This run-id {} does not exist.".format(run_id))
                return
            elif strategy_type == not_allowed_type:
                print("WARN: %s strategy has no %s." % (strategy_type, " ".join(func.__name__.split("_"))))
                return
            return func(*args, **kwargs)
        return wrapper
    return _check_strategy_type


class Report:
    def __init__(self, run_id):
        self._run_id = run_id
        info = RunInfo.get(run_id)
        self._strategy_type = info.get('strategy-type') if info is not None else None

    @check_params()
    def summary(self):
        # risk
        ret = last_risk(self._run_id)
        # run info
        ret.update(_standardize_runinfo(self._run_id))
        # portfolio
        port = _last_portfolio(self._run_id, fields=portfolio_map.values(), collection_name='portfolio')
        for k, v in portfolio_map.items():
            if k in ('entry_date', ):
                continue
            ret[k] = port.get(portfolio_map[k], 0)
        # benchmark portfolio
        benchmark_port = _last_portfolio(self._run_id, fields=[portfolio_map['annualized_returns'], portfolio_map['total_returns']],
                                         collection_name='benchmark-portfolio')
        ret['benchmark_annualized_returns'] = benchmark_port.get(portfolio_map['annualized_returns'], None) if benchmark_port is not None else None
        ret['benchmark_total_returns'] = benchmark_port.get(portfolio_map['total_returns'], None) if benchmark_port is not None else None
        return ret

    @check_params()
    def total_portfolios(self, start_date=None, end_date=None):
        return portfolio(self._run_id, start_date, end_date,
                         contain_benchmark=False)

    @check_params(not_allowed_type=StrategyType.FUTURE)
    def stock_portfolios(self, start_date=None, end_date=None):
        return _sub_portfolios(self._run_id, PortfolioType.Stock, start_date,
                               end_date)

    @check_params(not_allowed_type=StrategyType.STOCK)
    def future_portfolios(self, start_date=None, end_date=None):
        return _sub_portfolios(self._run_id, PortfolioType.Future, start_date,
                               end_date)

    @check_params(not_allowed_type=StrategyType.FUTURE)
    def stock_positions(self, start_date=None, end_date=None):
        return _stock_positions(self._run_id, start_date, end_date)

    @check_params(not_allowed_type=StrategyType.STOCK)
    def future_positions(self, start_date=None, end_date=None):
        return _future_positions(self._run_id, start_date, end_date)

    @check_params()
    def trades(self, start_date=None, end_date=None):
        return trades(self._run_id, start_date, end_date)
