
class StrategyType:
    STOCK = "Stock"
    FUTURE = "Future"
    MIX = "StockAndFuture"
    UNKNOWN = "Unknown"


class RunType:
    BACKTEST = "backtest"
    PAPER_TRADING = "paper_trading"
    BUILD_BACKTEST = "build_backtest"
    REAL_TRADING = "real_trading"


PORTFOLIO_TYPE = "8350"


# it is used to distinguish which kind of feeds that belong to
class PortfolioType:
    Stock = 2
    Future = 3


SUB_PORTFOLIOS = "9358"
ENTRY_DATE = "272"
ENTRY_TIME = "273"
