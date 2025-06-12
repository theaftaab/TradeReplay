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
        # initialize data loader and date range
        self.loader = DataLoader(data_path)
        self.current = start_date or self.loader.get_min_date()
        self.end_date = end_date or self.loader.get_max_date()

        # initialize tradebook and portfolio
        self.tradebook = TradeBook()
        self.portfolio = Portfolio(
            initial_cash=investment,
            brokerage=brokerage,
            tradebook=self.tradebook
        )

        # initialize indicator engine
        self.indicator_engine = IndicatorEngine(self.loader)

    def run(self, strategy):
        """
        Execute the strategy over the date range, calling decide() each day.
        Precomputes all indicators the strategy registers before iterating.
        """
        # let the strategy register required indicators
        strategy.register_indicators(self.indicator_engine)
        # compute each indicator once, vectorized across symbols and dates
        self.indicator_engine.compute_all()

        # day-by-day simulation
        while self.current and self.current <= self.end_date:
            daily_df = self.loader.get_data_for_date(self.current)
            strategy.decide(self, daily_df)
            self.current = self.loader.get_next_date(self.current)

        # write out recorded trades
        self.tradebook.save()
