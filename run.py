import pandas as pd
from datetime import datetime
from TradeReplay.session import Session
from Strategies.EMACrossoverShift import EMACrossoverStrategy

if __name__ == "__main__":
    DATA_PATH  = "Data/TrainingData.csv"
    START_DATE = datetime(2012, 1, 2)
    END_DATE   = datetime(2012, 6, 30)

    sess = Session(
        data_path=DATA_PATH,
        start_date=START_DATE,
        end_date=END_DATE,
        brokerage=0.0005,
        investment=100_000
    )

    strat = EMACrossoverStrategy(
        short=5,
        long=20,
        stop_loss_pct=0.03,  # e.g. 3% stop-loss
        target_multiple=2.5,  # e.g. 2.5× stop-distance
        quantity=1
    )
    # 3) Run the backtest and get final DataFrame
    df = sess.run(strat)
    df.to_csv("backtest_results.csv", index=False)

    # 4) inspect trades and final P&L as before
    trades_df = pd.read_csv(sess.tradebook.filepath, parse_dates=["date"])
    print(trades_df.head(), "\n...\n", trades_df.tail(), sep="\n")

    last_prices = {
        row.instrument: row.close
        for _, row in sess.loader.get_data_for_date(END_DATE).iterrows()
    }
    print("Final portfolio value:", sess.portfolio.total_value(last_prices))

    #testing who is commiting on my behalf