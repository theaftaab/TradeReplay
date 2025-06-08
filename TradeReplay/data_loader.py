import pandas as pd

class DataLoader:
    def __init__(self, filepath: str):
        self.df = pd.read_csv(filepath, parse_dates=["date"])
        self.df = self.df.drop(columns=[c for c in self.df.columns if "Unnamed" in c])
        self.df.rename(columns={"instrumnet": "instrument"}, inplace=True)
        self.df.sort_values("date", inplace=True)
        self.dates = self.df["date"].unique()

    def get_data_for_date(self, date):
        """Return all rows for that calendar date."""
        return self.df[self.df["date"] == date]

    def get_next_date(self, date):
        """Advance to the next trading date (or return None)."""
        idx = list(self.dates).index(date)
        return self.dates[idx + 1] if idx + 1 < len(self.dates) else None

    def get_prev_date(self, date):
        """Get the previous trading date (or None)."""
        idx = list(self.dates).index(date)
        return self.dates[idx - 1] if idx > 0 else None

    def get_min_date(self):
        return self.dates[0]

    def get_max_date(self):
        return self.dates[-1]