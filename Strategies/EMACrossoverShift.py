# File: Strategies/EMACrossoverStrategy.py

class EMACrossoverStrategy:
    def __init__(
        self,
        short: int = 5,
        long: int = 20,
        stop_loss_pct: float = 0.02,
        target_multiple: float = 2.0,
        quantity: int = 1,
    ):
        """
        :param short: EMA fast span (timeperiod)
        :param long:  EMA slow span (timeperiod)
        :param stop_loss_pct: fraction below entry to place stop loss (e.g. 0.02 for 2%)
        :param target_multiple: multiple of the stop-loss distance to set the profit target
        :param quantity: number of shares/contracts to buy
        """
        self.short = short
        self.long = long
        self.stop_loss_pct = stop_loss_pct
        self.target_multiple = target_multiple
        self.quantity = quantity

        # will be populated by register_indicators
        self.fast_col = None
        self.slow_col = None

        # track open positions: symbol -> {entry_price, stop_price, target_price}
        self.positions = {}

    def register_indicators(self, engine):
        """
        Register fast and slow EMAs via TA-Lib.
        """
        self.fast_col = engine.register_talib("EMA", timeperiod=self.short)
        self.slow_col = engine.register_talib("EMA", timeperiod=self.long)

    def decide(self, session, daily_df):
        """
        Called once per date with that day's data slice.

        ENTRY:
          - yesterday's EMA(short) < EMA(long)
          - today's EMA(short) > EMA(long)
          -> buy quantity at close

        EXIT:
          - intraday high >= target_price OR
          - intraday low <= stop_price
          -> sell entire quantity at target or stop
        """
        loader = session.loader
        portfolio = session.portfolio
        today = session.current

        # fetch previous day's data
        prev_date = loader.get_prev_date(today)
        prev_df = loader.get_data_for_date(prev_date) if prev_date else None

        for _, row in daily_df.iterrows():
            sym = row.get("instrument")
            close_price = row.get("close")
            ema_fast = row.get(self.fast_col)
            ema_slow = row.get(self.slow_col)

            # ENTRY: no existing position for sym
            if sym not in self.positions:
                # need valid previous day's DataFrame and values
                if prev_df is None or prev_df.empty or close_price is None or ema_fast is None or ema_slow is None:
                    continue
                prev_row = prev_df[prev_df["instrument"] == sym]
                if prev_row.empty:
                    continue
                prev_fast = prev_row.iloc[0].get(self.fast_col)
                prev_slow = prev_row.iloc[0].get(self.slow_col)
                if prev_fast is None or prev_slow is None:
                    continue

                # detect crossover: yesterday fast < slow AND today fast > slow
                if prev_fast < prev_slow and ema_fast > ema_slow:
                    entry_price = close_price
                    stop_price = entry_price * (1 - self.stop_loss_pct)
                    profit_dist = entry_price - stop_price
                    target_price = entry_price + profit_dist * self.target_multiple

                    # execute buy
                    portfolio.buy(sym, entry_price, today, self.quantity)
                    self.positions[sym] = {
                        "entry_price": entry_price,
                        "stop_price": stop_price,
                        "target_price": target_price,
                    }

            # EXIT: existing position open
            else:
                pos = self.positions.get(sym)
                if not pos:
                    continue
                # cleanup if no holdings
                if sym not in portfolio.holdings or portfolio.holdings[sym]["quantity"] <= 0:
                    self.positions.pop(sym, None)
                    continue

                stop_price = pos["stop_price"]
                target_price = pos["target_price"]
                qty = portfolio.holdings[sym]["quantity"]
                intraday_high = row.get("high")
                intraday_low = row.get("low")

                # exit on target
                if intraday_high is not None and intraday_high >= target_price:
                    portfolio.sell(sym, target_price, today, qty)
                    self.positions.pop(sym, None)
                # exit on stop
                elif intraday_low is not None and intraday_low <= stop_price:
                    portfolio.sell(sym, stop_price, today, qty)
                    self.positions.pop(sym, None)
