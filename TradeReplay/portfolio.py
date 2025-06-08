class Portfolio:
    def __init__(self, initial_cash=1_00_000, brokerage=0.0005, dp_charge=15.93, tradebook=None):
        self.cash = initial_cash
        self.holdings = {}  # symbol -> {'quantity': int, 'buy_price': float}
        self.brokerage = brokerage
        self.dp_charge = dp_charge
        self.tradebook = tradebook

    def _log(self, date, symbol, action, quantity, price, net_amount):
        if self.tradebook:
            self.tradebook.register_trade(
                symbol=symbol,
                action=action,
                date=date,
                price=price,
                quantity=quantity,
                net_amount=net_amount
            )

    def buy(self, symbol, price, date, quantity):
        # quantity = int(self.cash // (price * (1 + self.brokerage)))
        if quantity <= 0:
            return  # Not enough cash

        cost = quantity * price
        charges = cost * self.brokerage + self.dp_charge
        total_cost = cost + charges

        if self.cash < total_cost:
            return  # Defensive check

        self.cash -= total_cost
        self.holdings[symbol] = {'quantity': quantity, 'buy_price': price}
        self._log(date, symbol, 'BUY', quantity, price, total_cost)

    def sell(self, symbol, price, date, quantity):
        if symbol not in self.holdings:
            return  # No holdings

        # quantity = self.holdings[symbol]['quantity']
        proceeds = quantity * price
        charges = proceeds * self.brokerage + self.dp_charge
        net_proceeds = proceeds - charges

        self.cash += net_proceeds
        del self.holdings[symbol]
        self._log(date, symbol, 'SELL', quantity, price, net_proceeds)

    def total_value(self, latest_prices):
        invested = sum(
            v['quantity'] * latest_prices.get(sym, v['buy_price'])
            for sym, v in self.holdings.items()
        )
        return self.cash + invested