Backtesting Framework

A lightweight, extensible Python backtesting library that handles data loading, indicator computation, portfolio management, and strategy execution. It uses TA-Lib under the hood for technical indicators and logs all trades to a CSV tradebook.

⸻

Repository Structure

Backtesting-Framework/
├── Data/                   # (ignored by Git) raw and intermediate CSV files
├── Strategies/             # User-defined strategy classes
│   └── EMACrossoverStrategy.py
├── TradeReplay/            # Core engine modules
│   ├── data_loader.py      # CSV loader, date navigation
│   ├── indicators.py       # TA-Lib registration and compute
│   ├── portfolio.py        # Portfolio & P&L tracking
│   ├── tradebook.py        # Trade logging
│   └── session.py          # Backtest orchestration (with tqdm)
├── run.py                  # Example driver: instantiate Session + Strategy
├── requirements.txt        # Python dependencies (pandas, TA-Lib, tqdm, etc.)
└── .gitignore              # Ignore Data/, virtual env, caches, etc.


⸻

How It Works (Current)
	1.	DataLoader reads your time-series CSV, parses dates, renames columns, and exposes helper methods:
	•	get_data_for_date(date)
	•	get_prev_date(date) / get_next_date(date)
	2.	IndicatorEngine lets you register any TA-Lib indicator by name and params:

col = engine.register_talib("EMA", timeperiod=20)

Calling compute_all() vectorizes the group-by transformation once, attaching new columns (e.g., ema_timeperiod20) to the master DataFrame.

	3.	Portfolio handles money, positions, buy/sell logic (with brokerage & DP charges), and writes each trade to TradeBook (a CSV log).
	4.	Session glues it all together:
	•	Registers indicators
	•	Calls compute_all()
	•	Iterates through each date (with a tqdm progress bar)
	•	Calls your strategy’s decide(session, daily_df)
	•	Saves the tradebook at the end
	5.	User Strategies (in Strategies/): subclass the pattern by defining:

register_indicators(engine)
decide(session, daily_df)

For example, the EMACrossoverStrategy class implements:
	•	Entry on a 5-20 EMA crossover
	•	Exit on intraday stop-loss or profit-target
	•	Logs every transaction

	6.	Driver (run.py) shows a sample end-to-end run, including:
	•	Instantiating Session and your strategy
	•	Manually calling register_indicators + compute_all
	•	Optionally saving the full DataFrame with indicators to CSV
	•	Running the backtest and printing trade summaries & final portfolio value

⸻

Usage
	1.	Install dependencies

pip install -r requirements.txt


	2.	Prepare data
	•	Place your OHLC (plus instrument & date) CSV in Data/TrainingData.csv (local only).
	3.	Define your strategy
	•	Create a new class in Strategies/ following the EMACrossoverStrategy template.
	4.	Run backtest

python run.py


	5.	Inspect results
	•	tradebook.csv contains every buy/sell with timestamps, P&L, and cash balances.
	•	Final portfolio value printed to console.

⸻

Future Scope
	•	Parallel computation of indicators (via joblib, Dask, or Ray) and per-symbol backtests for speed up across CPU cores.
	•	GPU support and RAPIDS/cuDF integration for massive-data workloads.
	•	Built-in analytics & metrics: Sharpe ratio, drawdown, VAMI, trade statistics, and visualization.
	•	Pluggable data sources: support for SQL, Parquet, live API feeds, and parquet partitions.
	•	Strategy registry & CLI: configure and run multiple strategies from a command-line interface or YAML/JSON config.
	•	Publisher-subscriber hooks: allow real-time event streaming into external systems (Dashboards, Slack alerts, etc.).
	•	Packaging: distribute as a pip-installable library with versioned releases and unit tests.
	•	Live trading adapter: connect signals to execution gateways (e.g., Interactive Brokers, Alpaca) for paper or real trades.

⸻

Happy backtesting! Feel free to open issues or PRs for enhancements. 🚀
