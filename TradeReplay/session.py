# File: TradeReplay/session.py
from tqdm import tqdm
from TradeReplay.data_loader import DataLoader
from TradeReplay.portfolio import Portfolio
from TradeReplay.tradebook import TradeBook
from TradeReplay.indicators import IndicatorEngine

class Session:
    def __init__(
        self,
        data_path: str,
        start_date=None,
        end_date=None,
        brokerage=0.0005,
        investment=100_000
    ):
        self.loader = DataLoader(data_path)
        self.current = start_date or self.loader.get_min_date()
        self.end_date = end_date or self.loader.get_max_date()

        self.tradebook = TradeBook()
        self.portfolio = Portfolio(
            initial_cash=investment,
            brokerage=brokerage,
            tradebook=self.tradebook
        )

        self.indicator_engine = IndicatorEngine(self.loader)

    def run(self, strategy):
        """
        Execute the strategy over the date range with a tqdm progress bar.
        """
        # 1) Register & compute indicators
        strategy.register_indicators(self.indicator_engine)
        self.indicator_engine.compute_all()

        # 2) Build the list of dates to iterate
        all_dates = []
        d = self.current
        while d and d <= self.end_date:
            all_dates.append(d)
            d = self.loader.get_next_date(d)

        # 3) Loop with tqdm
        for today in tqdm(all_dates, desc="Backtest Progress", unit="day"):
            self.current = today
            daily_df = self.loader.get_data_for_date(today)
            strategy.decide(self, daily_df)

        # 4) Save trades
        self.tradebook.save()