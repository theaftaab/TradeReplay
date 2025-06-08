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
        Runs from self.current to self.end_date,
        calling strategy.decide(...) on each date.
        """
        while self.current and self.current <= self.end_date:
            daily_df = self.loader.get_data_for_date(self.current)
            strategy.decide(self, daily_df)
            self.current = self.loader.get_next_date(self.current)

        # write out your trades
        self.tradebook.save()