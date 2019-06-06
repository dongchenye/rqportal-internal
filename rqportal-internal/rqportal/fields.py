portfolio_reverted_map = {
    "8355": "daily_returns",
    "8354": "pnl",
    "8359": "total_returns",
    "8412": "annualized_returns",
    "272": "entry_date",
    "273": "entry_time",
    "8351": "cash",
}

portfolio_map = {
    "entry_date": "272",

    "starting_cash": "8358",
    "cash": "8351",
    "total_returns": "8359",
    "daily_returns": "8355",
    "daily_pnl": "8354",
    "market_value": "8352",
    "portfolio_value": "8353",
    "annualized_returns": "8412",
    "transaction_cost": "8419",

    "dividend_receivable": "8413",
}

future_portfolio_map = {
    "entry_date": "272",

    "starting_cash": "8358",
    "cash": "8351",
    "total_returns": "8359",
    "daily_returns": "8355",
    "market_value": "8352",
    "daily_pnl": "8354",
    "portfolio_value": "8353",
    "transaction_cost": "8419",
    "annualized_returns": "8412",
    "margin": "8365",
}

tradedate_map = {
    "entry_date": "272",
    "entry_time": "273",
}

benchmark_reverted_map = {
    "272": "entry_date",
    "273": "entry_time",
    "8355": "benchmark_daily_returns"
}

position_map = {
    # date

    "order_book_id": "8042",
    "bought_value": "8304",
    "sold_value": "8305",
    "market_value": "8352",
    "entry_date": "272",
    "entry_time": "273",

    "quantity": "8317",
    "price": "31",
    "pnl": "8354",
}

stock_position_map = {
    "entry_date": "272",

    "order_book_id": "8042",
    "quantity": "8317",
    "bought_quantity": "8308",
    "sold_quantity": "8309",
    "bought_value": "8304",
    "sold_value": "8305",
    "avg_price": "6",
    "market_value": "8352",
    "transaction_cost": "8419",
}

future_position_map = {
    # date
    "entry_date": "272",

    "order_book_id": "8042",
    "daily_pnl": "8354",
    "transaction_cost": "8419",
    "market_value": "8352",

    # extended position
    "margin": "8318.8365",
    "buy_pnl": "8318.10427",
    "buy_transaction_cost": "8318.10431",
    "buy_margin": "8318.10429",
    "buy_quantity": "8318.8319",
    "buy_avg_open_price": "8318.10421",
    "buy_avg_holding_price": "8318.10423",
    "sell_pnl": "8318.10428",
    "sell_transaction_cost": "8318.10432",
    "sell_margin": "8318.10430",
    "sell_quantity": "8318.8320",
    "sell_avg_open_price": "8318.10422",
    "sell_avg_holding_price": "8318.10424",
}

trades_map = {
    # datetime
    "entry_date": "272",
    "entry_time": "273",

    "order_book_id": "8042",
    "side": "54",
    "last_price": "31",
    "last_quantity": "32",
    "exec_id": "17",
    "position_effect": "77",
    "commission": "8414",
    "tax": "8420",
    "order_id": "8066",

    "trade_id": "17",
}

risk_map = {
    "alpha": "8380",
    "beta": "8381",
    "sharpe": "8382",
    "sortino": "8383",
    "information_ratio": "8384",
    "volatility": "8385",
    "max_drawdown": "8386",
    "tracking_error": "8387",
    "downside_risk": "8391",
}

run_info_map = {
    "start_date": "start-date",
    "end_date": "end-date",
    "strategy_name": "title",
    "strategy_type": "strategy-type",
    "stock_starting_cash": "init-stock-cash",
    "future_starting_cash": "init-future-cash",
    "frequency": "time-unit",
    "run_type": "run-type",
    "commission_multiplier": "commissionMultiplier",
    "slippage": "slippage",
    "benchmark": "benchmarkInstrument",
    "matching_type": "matchMethod",
    "margin_multiplier": "marginMultiplier",
    "remark": "run-des",
}