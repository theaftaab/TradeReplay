import pandas as pd
from tqdm import tqdm
from TradeReplay.decision import DecisionStrategy

class EMAShiftStrategy(DecisionStrategy):
    def __init__(self, short=5, long=20):
        self.short = short
        self.long  = long

    def decide(self, session, daily_df: pd.DataFrame):
        if daily_df.empty:
            return

        today = daily_df["date"].iloc[0]
        prev  = session.loader.get_prev_date(today)
        if prev is None:
            return

        # iterate unique symbols for a stable tqdm bar
        symbols = daily_df["instrument"].unique()
        for symbol in tqdm(symbols, desc=f"{today.date()} symbols", leave=False):
            grp = daily_df[daily_df.instrument == symbol]
            price = grp["close"].iloc[0]

            # compute EMAs (cached in IndicatorEngine)
            ema_s_prev = session.indicator_engine.ema(symbol, prev,  window=self.short)
            ema_l_prev = session.indicator_engine.ema(symbol, prev,  window=self.long)
            ema_s      = session.indicator_engine.ema(symbol, today, window=self.short)
            ema_l      = session.indicator_engine.ema(symbol, today, window=self.long)

            # BUY when short EMA crosses *above* long EMA
            if ema_s_prev < ema_l_prev and ema_s > ema_l:
                if symbol not in session.portfolio.holdings:
                    session.portfolio.buy(symbol, price, today, quantity=1)

            # SELL when short EMA crosses *below* long EMA
            elif ema_s_prev > ema_l_prev and ema_s < ema_l:
                if symbol in session.portfolio.holdings:
                    qty = session.portfolio.holdings[symbol]["quantity"]
                    session.portfolio.sell(symbol, price, today, quantity=qty)