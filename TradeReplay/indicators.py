class IndicatorEngine:
    def __init__(self, loader, custom_indicators=None):
        self.loader = loader
        self.custom = custom_indicators or {}
        self._cache = {}  # <-- simple in‐memory cache

        try:
            import talib
            self._talib = talib
        except ImportError:
            self._talib = None

    def register(self, name: str, func):
        """User calls this to add their own indicator."""
        self.custom[name.lower()] = func

    def _get_history(self, symbol, date, window):
        df_sym = (
            self.loader.df
            .loc[lambda d: (d.instrument == symbol) & (d.date <= date)]
            .sort_values("date")
        )
        # last `window` closes
        return df_sym["close"].iloc[-window:]

    def sma(self, symbol: str, date, window: int) -> float:
        key = ("sma", symbol, date, window)
        if key in self._cache:
            return self._cache[key]

        closes = self._get_history(symbol, date, window)
        val = closes.mean()
        self._cache[key] = val
        return val

    def ema(self, symbol: str, date, window: int) -> float:
        key = ("ema", symbol, date, window)
        if key in self._cache:
            return self._cache[key]

        closes = self._get_history(symbol, date, window)
        val = closes.ewm(span=window, adjust=False).mean().iloc[-1]
        self._cache[key] = val
        return val

    def __getattr__(self, name):
        # allow custom or TA-Lib indicators, but *do not* cache them automatically
        name_low = name.lower()
        if name_low in self.custom:
            fn = self.custom[name_low]
            return lambda symbol, date, *args, window, **kwargs: fn(
                self._get_history(symbol, date, window), *args, **kwargs
            )
        if self._talib and hasattr(self._talib, name.upper()):
            talib_fn = getattr(self._talib, name.upper())
            return lambda symbol, date, timeperiod, *args, **kwargs: talib_fn(
                self._get_history(symbol, date, timeperiod).values,
                timeperiod,
                *args,
                **kwargs
            )[-1]
        raise AttributeError(f"No indicator named {name!r} found")