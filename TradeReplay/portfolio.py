class Portfolio:
    def __init__(
        self,
        initial_cash: float = 100_000,
        brokerage: float = 0.0005,
        dp_charge: float = 15.93,
        tradebook=None
    ):
        self.cash = initial_cash
        self.holdings = {}   # symbol -> {'quantity': int, 'avg_price': float}
        self.brokerage = brokerage
        self.dp_charge = dp_charge
        self.tradebook = tradebook

    def _invested_amount(self) -> float:
        return sum(
            pos['quantity'] * pos['avg_price']
            for pos in self.holdings.values()
        )

    def _log(self, date, symbol, action, quantity, price, net_amount):
        if not self.tradebook:
            return
        cash_after = self.cash
        invested_after = self._invested_amount()
        self.tradebook.register_trade(
            symbol=symbol,
            action=action,
            date=str(date),
            price=price,
            quantity=quantity,
            net_amount=net_amount,
            cash_after=cash_after,
            invested_after=invested_after
        )
    def has_position(self, symbol: str) -> bool:
        """
        Returns True if we currently hold >0 shares of `symbol`.
        """
        return symbol in self.holdings and self.holdings[symbol]['quantity'] > 0

    def buy(self, symbol: str, price: float, date, quantity: int):
        if quantity <= 0:
            return
        cost = price * quantity
        charges = cost * self.brokerage + self.dp_charge
        total = cost + charges
        if self.cash < total:
            return  # insufficient funds

        self.cash -= total

        if symbol in self.holdings:
            old = self.holdings[symbol]
            new_qty = old['quantity'] + quantity
            new_avg = (old['avg_price'] * old['quantity'] + price * quantity) / new_qty
        else:
            new_qty, new_avg = quantity, price

        self.holdings[symbol] = {'quantity': new_qty, 'avg_price': new_avg}
        self._log(date, symbol, 'BUY', quantity, price, total)

    def sell(self, symbol: str, price: float, date, quantity: int):
        if symbol not in self.holdings or quantity <= 0:
            return
        held = self.holdings[symbol]['quantity']
        qty = min(quantity, held)
        proceeds = price * qty
        charges = proceeds * self.brokerage + self.dp_charge
        net = proceeds - charges

        self.cash += net

        if qty == held:
            del self.holdings[symbol]
        else:
            self.holdings[symbol]['quantity'] = held - qty

        self._log(date, symbol, 'SELL', qty, price, net)

    def total_value(self, latest_prices: dict):
        invested = sum(
            self.holdings[s]['quantity'] * latest_prices.get(s, self.holdings[s]['avg_price'])
            for s in self.holdings
        )
        return self.cash + invested