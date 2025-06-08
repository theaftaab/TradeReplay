# %% [markdown]
# # Backtest Your Strategy
from pprint import pprint

# %%
import pandas as pd
import random
from datetime import datetime
from TradeReplay.decision  import DecisionStrategy
from TradeReplay.session   import Session

# %% define a simple momentum strategy
class MomentumStrategy(DecisionStrategy):
    def __init__(self, lookback=3):
        self.lookback = lookback
        self.history  = {}

    def decide(self, session, daily_df):
        """
        daily_df: pd.DataFrame with columns [date, open, high, low, close, volume, instrument]
        session: gives you session.portfolio and session.tradebook
        """
        for sym, group in daily_df.groupby("instrumnet"):
            closes = group["close"].tolist()
            # store history
            self.history.setdefault(sym, []).extend(closes)
            # only act if we have lookback+1 days
            prices = self.history[sym]
            if len(prices) >= self.lookback + 1:
                # simple momentum: if today’s close > close N days ago → BUY, else SELL
                if prices[-1] > prices[-1-self.lookback]:
                    session.portfolio.buy(sym, prices[-1], group["date"].iloc[0], quantity=random.randrange(1,10))
                elif sym in session.portfolio.holdings:
                    session.portfolio.sell(sym, prices[-1], group["date"].iloc[0], quantity=1)

# %% parameters
DATA_PATH  = "Data/TrainingData.csv"
START_DATE = datetime(2012,1,2)
END_DATE   = datetime(2012,6,30)

# %% run backtest
sess = Session(
    data_path = DATA_PATH,
    start_date=START_DATE,
    end_date  = END_DATE,
    brokerage = 0.0005,
    investment=100000
)
strategy = MomentumStrategy(lookback=5)
sess.run(strategy)

# %% inspect results
trades_df = pd.read_csv(sess.tradebook.filepath)
# pprint(trades_df.head(), trades_df.tail())
print(trades_df.head())
# print("Final portfolio value:",
#       sess.portfolio.total_value(
#           # use last known prices for mark-to-market
#           { row.instrument: row.close
#             for _, row in sess.loader.df[sess.loader.df.date == END_DATE].iterrows() }
#       )
# )
holdings = sess.portfolio.holdings
print(holdings)