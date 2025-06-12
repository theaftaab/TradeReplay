import pandas as pd

class IndicatorEngine:
    """
    Precompute and attach TA-Lib indicators as new columns in loader.df
    so each indicator is calculated only once per symbol across all dates.
    """
    def __init__(self, loader, custom_indicators=None):
        self.loader = loader
        self.custom = custom_indicators or {}
        self._indicators = {}  # mapping: column_name -> (function, params dict)

        # try importing TA-Lib
        try:
            import talib
            self._talib = talib
        except ImportError:
            raise ImportError(
                "TA-Lib is required. Please install it with `pip install TA-Lib`"
            )

    def register_talib(self, name: str, **params) -> str:
        """
        Registers a TA-Lib indicator to be computed.

        Args:
            name: Name of the indicator (e.g., 'EMA', 'SMA', 'MACD', 'OBV').
            params: Keyword arguments expected by the TA-Lib function (e.g., timeperiod=14).

        Returns:
            The column name under which values will be stored.
        """
        fn = getattr(self._talib, name.upper(), None)
        if fn is None:
            raise AttributeError(f"TA-Lib has no indicator named '{name}'")

        # build unique column name based on params
        if params:
            param_str = "_".join(f"{k}{v}" for k, v in sorted(params.items()))
            col = f"{name.lower()}_{param_str}"
        else:
            col = name.lower()

        self._indicators[col] = (fn, params)
        return col

    def register_custom(self, name: str, func) -> str:
        """
        Registers a custom indicator function.

        Args:
            name: Desired column name for the indicator.
            func: A function accepting a pandas Series of closes and returning a sequence.

        Returns:
            The column name under which values will be stored.
        """
        col = name.lower()
        self._indicators[col] = (func, None)
        return col

    def compute_all(self):
        """
        Compute all registered indicators for every symbol and attach as columns.
        Must be called once after registering all desired indicators.
        """
        df = self.loader.df

        for col, (fn, params) in self._indicators.items():
            if params is not None:
                # TA-Lib functions expect numpy arrays and named params
                df[col] = (
                    df.groupby('instrument')['close']
                      .transform(lambda x: fn(x.values, **params))
                )
            else:
                # custom functions take pandas Series
                df[col] = (
                    df.groupby('instrument')['close']
                      .transform(lambda x: fn(x))
                )

        # update loader's DataFrame in place

        self.loader.df.to_csv("Data/Final_DF.csv", index=False)
        self.loader.df = df


    def get(self, symbol: str, date, column: str):
        """
        Retrieve a precomputed indicator value for a given symbol and date.
        Returns None if not found.
        """
        row = self.loader.df.loc[
            (self.loader.df['instrument'] == symbol) &
            (self.loader.df['date'] == date)
        ]
        if row.empty or column not in row:
            return None
        return float(row[column].iloc[0])

    def __getattr__(self, name):
        """
        Allow dynamic access to custom indicator functions registered via register_custom().
        """
        name_low = name.lower()
        if name_low in self.custom:
            return self.custom[name_low]
        raise AttributeError(f"No precomputed indicator named '{name}'")
