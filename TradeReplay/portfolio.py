class Portfolio:
    def __init__(self,
                 initial_cash: float = 100_000,
                 brokerage: float    = 0.0005,
                 dp_charge: float    = 15.93,
                 tradebook=None):
        self.cash       = initial_cash
        self.holdings   = {}   # symbol → {'quantity': int, 'avg_price': float}
        self.brokerage  = brokerage
        self.dp_charge  = dp_charge
        self.tradebook  = tradebook

    def _invested_amount(self) -> float:
        return sum(
            pos['quantity'] * pos['avg_price']
            for pos in self.holdings.values()
        )
    def _log(self, date, symbol, action, quantity, price, net_amount):
        if not self.tradebook:
            return

        cash_after     = self.cash
        invested_after = self._invested_amount()

        self.tradebook.register_trade(
            symbol=symbol,
            action=action,
            date=date,
            price=price,
            quantity=quantity,
            net_amount=net_amount,
            cash_after=cash_after,
            invested_after=invested_after
        )
    def buy(self, symbol: str, price: float, date, quantity: int):
        if quantity <= 0:
            return  # nothing to do

        cost    = price * quantity
        charges = cost * self.brokerage + self.dp_charge
        total   = cost + charges

        if self.cash < total:
            # not enough cash to execute
            return

        # deduct cash
        self.cash -= total

        # update holdings: accumulate & recompute average price
        if symbol in self.holdings:
            old_qty   = self.holdings[symbol]['quantity']
            old_avg   = self.holdings[symbol]['avg_price']
            new_qty   = old_qty + quantity
            new_avg   = (old_avg * old_qty + price * quantity) / new_qty
        else:
            new_qty, new_avg = quantity, price

        self.holdings[symbol] = {
            'quantity':  new_qty,
            'avg_price': new_avg
        }

        # log the trade
        self._log(date, symbol, 'BUY', quantity, price, total)

    def sell(self, symbol: str, price: float, date, quantity: int):
        if symbol not in self.holdings:
            return  # you don’t own any

        held_qty = self.holdings[symbol]['quantity']
        if quantity <= 0:
            return

        # cap to what you actually hold
        qty_to_sell = min(quantity, held_qty)
        proceeds    = price * qty_to_sell
        charges     = proceeds * self.brokerage + self.dp_charge
        net_proceeds = proceeds - charges

        # credit cash
        self.cash += net_proceeds

        # update or remove holding
        if qty_to_sell == held_qty:
            del self.holdings[symbol]
        else:
            self.holdings[symbol]['quantity'] = held_qty - qty_to_sell
            # avg_price remains unchanged on partial sell

        # log the trade
        self._log(date, symbol, 'SELL', qty_to_sell, price, net_proceeds)

    def total_value(self, latest_prices: dict):
        """Mark-to-market: cash + sum(qty * price)."""
        invested = 0.0
        for sym, pos in self.holdings.items():
            market_price = latest_prices.get(sym, pos['avg_price'])
            invested    += pos['quantity'] * market_price
        return self.cash + invested