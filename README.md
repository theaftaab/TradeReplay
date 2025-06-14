# TradeReplay - Simplified Trading Strategy Backtesting Framework

TradeReplay is designed to make trading strategy testing accessible to financial analysts, allowing them to focus on strategy development while the framework handles all the complex optimizations in the background.

## 🎯 Vision

Most financial analysts excel at developing trading strategies but may not have expertise in advanced topics like GPU utilization, multiprocessing, or memory optimization. TradeReplay aims to bridge this gap by:

1. **Simple Strategy Definition**: Write strategies as simple Python scripts without worrying about system-level optimizations
2. **Automatic Optimizations**: The framework handles GPU acceleration, parallel processing, and memory management internally
3. **Focus on Strategy**: Analysts can concentrate on their trading logic while the framework takes care of performance
4. **Built-in Analytics**: Comprehensive performance metrics and visualizations without additional coding

---

## ⚙️ Repository Structure

```text
Backtesting-Framework/
├── Data/                   # (ignored by Git) raw and intermediate CSV files
├── Strategies/             # User-defined strategy classes
│   └── EMACrossoverStrategy.py
├── TradeReplay/            # Core engine modules
│   ├── data_loader.py      # CSV loader, date navigation
│   ├── indicators.py       # TA-Lib registration and compute
│   ├── portfolio.py        # Portfolio & P&L tracking
│   ├── tradebook.py        # Trade logging
│   └── session.py          # Backtest orchestration (with tqdm + progress bar)
├── run.py                  # Example driver: instantiate Session + Strategy
├── requirements.txt        # Python dependencies (pandas, TA-Lib, tqdm, etc.)
└── .gitignore              # Ignore Data/, virtual env, caches, etc.
```

---

##  How It Works (Current)

1. **DataLoader** reads your time-series CSV, parses dates, renames columns, and exposes helper methods:
   - `get_data_for_date(date)`
   - `get_prev_date(date)` / `get_next_date(date)`

2. **IndicatorEngine** lets you register any TA-Lib indicator by name and params:
   ```python
   col = engine.register_talib("EMA", timeperiod=20)
   ```
   Calling `compute_all()` vectorizes the group-by transformation once, attaching new columns (e.g., `ema_timeperiod20`) to the master DataFrame.

3. **Portfolio** handles money, positions, buy/sell logic (with brokerage & DP charges), and writes each trade to **TradeBook** (a CSV log).

4. **Session** glues it all together:
   - Registers indicators
   - Calls `compute_all()`
   - Iterates through each date (with a **tqdm** progress bar)
   - Calls your strategy’s `decide(session, daily_df)`
   - Saves the tradebook at the end

5. **User Strategies** (in `Strategies/`): subclass the pattern by defining:
   ```python
   register_indicators(engine)
   decide(session, daily_df)
   ```
   For example, the `EMACrossoverStrategy` class implements:
   - Entry on a 5-20 EMA crossover
   - Exit on intraday stop-loss or profit-target
   - Logs every transaction

6. **Driver (`run.py`)** shows a sample end-to-end run, including:
   - Instantiating `Session` and your strategy
   - Manually calling `register_indicators` + `compute_all`
   - Optionally saving the full DataFrame with indicators to CSV
   - Running the backtest and printing trade summaries & final portfolio value

---

##  Usage

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
2. **Prepare data**
   - Place your OHLC (plus `instrument` & `date`) CSV in `Data/TrainingData.csv` (local only).
3. **Define your strategy**
   - Create a new class in `Strategies/` following the `EMACrossoverStrategy` template.
4. **Run backtest**
   ```bash
   python run.py
   ```
5. **Inspect results**
   - `tradebook.csv` contains every buy/sell with timestamps, P&L, and cash balances.
   - Final portfolio value printed to console.

---

## 🚀 Future Enhancements

1. **Smart Optimizations**
   - Automatic GPU acceleration for heavy computations
   - Intelligent multiprocessing for parallel strategy execution
   - Memory-efficient data handling
   - Cache optimization for frequently accessed data

2. **Enhanced Analytics**
   - Comprehensive performance metrics
   - Risk management tools
   - Portfolio optimization
   - Correlation analysis

3. **Data Integration**
   - Multiple data source support
   - Real-time data feeds
   - Historical data integration
   - Custom data preprocessing

4. **User Experience**
   - Strategy registry and management
   - Interactive visualization tools
   - Real-time monitoring
   - Strategy comparison and benchmarking

5. **Enterprise Features**
   - Team collaboration tools
   - Strategy version control
   - Performance reporting
   - Integration with trading platforms

---

Happy backtesting! 🚀
