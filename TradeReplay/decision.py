from abc import ABC, abstractmethod

class DecisionStrategy(ABC):
    @abstractmethod
    def decide(self, session, daily_df):
        """
        Examine today's `daily_df` for the given `session` and
        execute any buys or sells via session.portfolio.
        """
        pass