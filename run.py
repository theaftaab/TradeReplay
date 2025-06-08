import pandas as pd
from datetime import datetime
from TradeReplay.session import Session
from Strategies.EMACrossoverShift import EMAShiftStrategy

if __name__ == "__main__":
    DATA_PATH  = "Data/TrainingData.csv"
    START_DATE = datetime(2012, 1, 2)
    END_DATE   = datetime(2012, 6, 30)

    sess = Session(
        data_path  = DATA_PATH,
        start_date = START_DATE,
        end_date   = END_DATE,
        brokerage  = 0.0005,
        investment = 100_000
    )
    strat = EMAShiftStrategy(short=5, long=20)
    sess.run(strat)

    # Inspect trades
    trades_df = pd.read_csv(sess.tradebook.filepath, parse_dates=["date"])
    print(trades_df.head(), "\n...\n", trades_df.tail(), sep="\n")

    # Final mark-to-market
    last_prices = {
        row.instrument: row.close
        for _, row in sess.loader.get_data_for_date(END_DATE).iterrows()
    }
    print("Final portfolio value:", sess.portfolio.total_value(last_prices))