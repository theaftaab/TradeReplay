from multiprocessing import Pool, cpu_count
from functools import partial
import pandas as pd
from tqdm import tqdm
from TradeReplay.session import SessionChunk
from TradeReplay.data_loader import DataLoader
import math

class MultiSession:
    """
    A helper to run multiple SessionChunk instances in parallel.
    """
    def __init__(
        self,
        data_path: str,
        strategy,
        symbols: list,
        start_date=None,
        end_date=None,
        brokerage=0.0005,
        investment=100_000,
    ):
        self.data_path = data_path
        self.strategy = strategy
        self.symbols = symbols
        self.start_date = start_date
        self.end_date = end_date
        self.brokerage = brokerage
        self.investment = investment

    def _make_symbol_chunks(self, n_procs: int) -> list[list[str]]:
        """
        Evenly divide the symbol list into n_procs sublists.
        
        Args:
            n_procs: Number of processes
            
        Returns:
            List of symbol chunks
        """
        chunk_size = math.ceil(len(self.symbols) / n_procs)
        return [
            self.symbols[i : i + chunk_size]
            for i in range(0, len(self.symbols), chunk_size)
        ]

    def _run_one_chunk(
        self,
        chunk_symbols: list[str],
    ) -> pd.DataFrame:
        """
        Instantiate a SessionChunk for this subset of symbols,
        run it, then return its indicator‐DataFrame (or tradebook).
        
        Args:
            chunk_symbols: List of symbols for this chunk
            
        Returns:
            DataFrame with results
        """
        sess = SessionChunk(
            data_path=self.data_path,
            start_date=self.start_date,
            end_date=self.end_date,
            brokerage=self.brokerage,
            investment=self.investment,
            symbols=chunk_symbols,
        )
        # precompute indicators once per process
        sess.prepare_indicators(self.strategy)
        # runs its own tqdm per process
        result_df = sess.run(self.strategy)
        return result_df

    def run_parallel(
        self,
        num_processes: int | None = None,
    ) -> pd.DataFrame:
        """
        Split symbols into chunks, run them in parallel, then concatenate results.
        
        Args:
            num_processes: Number of processes to use (default: None, uses all available cores)
            
        Returns:
            Combined DataFrame with results
        """
        n_procs = num_processes or cpu_count()
        chunks = self._make_symbol_chunks(n_procs)

        with Pool(processes=n_procs) as pool:
            # partial binds our strategy + other args
            worker = partial(self._run_one_chunk)
            dfs = pool.map(worker, chunks)

        # now dfs is a list of DataFrames (one per chunk); stitch them back together
        combined = pd.concat(dfs, axis=0, ignore_index=True)
        return combined
