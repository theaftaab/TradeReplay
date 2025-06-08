class DecisionStrategy:
    def decide(self, row):
        """
        row: dict or pd.Series containing a single row of OHLCV data
        Returns: 'BUY', 'SELL', or 'HOLD'
        """
        raise NotImplementedError("User must implement the decision logic.")