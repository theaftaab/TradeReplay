import pandas as pd
from datetime import datetime
from TradeReplay.session import Session
from Strategies.EMACrossoverShift import EMACrossoverStrategy

if __name__ == "__main__":
    DATA_PATH  = "Data/TrainingData.csv"
    START_DATE = datetime(2012, 1, 2)
    END_DATE   = datetime(2017, 6, 30)

    sess = Session(
        data_path  = DATA_PATH,
        start_date = START_DATE,
        end_date   = END_DATE,
        brokerage  = 0.0005,
        investment = 100_000
    )

    strat = EMACrossoverStrategy(
        short=5,
        long=20,
        stop_loss_pct=0.03,  # e.g. 3% stop-loss
        target_multiple=2.5,  # e.g. 2.5× stop-distance
        quantity=1
    )
    sess.run(strat)

    # 1) register and compute your indicators explicitly
    strat.register_indicators(sess.indicator_engine)
    sess.indicator_engine.compute_all()

    # 2) *now* dump the full DataFrame (with EMA cols) to CSV
    # print("Saving full DataFrame with indicators…")
    # sess.loader.df.to_csv("data_with_indicators.csv", index=False)
    df = sess.loader.df
    df = df.dropna(subset=[strat.fast_col, strat.slow_col], how="any")\
           .reset_index(drop=True)
    sess.loader.df = df

    # 3) run the backtest
    sess.run(strat)

    # 4) inspect trades and final P&L as before
    trades_df = pd.read_csv(sess.tradebook.filepath, parse_dates=["date"])
    print(trades_df.head(), "\n...\n", trades_df.tail(), sep="\n")

    last_prices = {
        row.instrument: row.close
        for _, row in sess.loader.get_data_for_date(END_DATE).iterrows()
    }
    print("Final portfolio value:", sess.portfolio.total_value(last_prices))