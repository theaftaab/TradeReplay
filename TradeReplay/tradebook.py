import csv
import os

class TradeBook:
    def __init__(self, filepath='tradebook.csv'):
        self.filepath = filepath
        self.trades = []

    def register_trade(self,
                       symbol,
                       action,
                       date,
                       price,
                       quantity,
                       net_amount,
                       cash_after,
                       invested_after):
        self.trades.append({
            "symbol"         : symbol,
            "action"         : action,
            "date"           : str(date),
            "price"          : price,
            "quantity"       : quantity,
            "net_amount"     : net_amount,
            "cash_after"     : cash_after,
            "invested_after" : invested_after
        })

    def save(self):
        if not self.trades:
            return

        keys = self.trades[0].keys()
        with open(self.filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(self.trades)