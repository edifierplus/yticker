import pickle

import pandas as pd
from retry import retry

from .YahooLookupBrowser import YahooLookupBrowser


class YahooTickerDownloader:
    """Download tickers from Yahoo Finance via lookup page.
    """

    def __init__(self, cagetory: str = 'all'):
        self._category = cagetory
        self.start = 0
        self.perpage = 10000
        self.browser = YahooLookupBrowser()
        self.tickers = set()
        self.letters = list('abcdefghijklmnopqrstuvwxyz')
        self.initialize_queue()

    @property
    def category(self):
        return self._category

    @property
    def peak_query(self):
        return self.queue[self.idx]

    @property
    def index(self):
        return self.idx

    @property
    def queue_length(self):
        return len(self.queue)

    @property
    def done(self):
        return self.idx >= len(self.queue)

    def initialize_queue(self, initial: list = None):
        self.idx = 0
        self.queue = list(initial if initial is not None else self.letters)

    @retry(tries=5, delay=5, backoff=5)
    def lookup(self, key):
        return self.browser.lookup(key=key, category=self.category, start=self.start, size=self.perpage)

    def download_next(self):
        key = self.queue[self.idx]
        ans, total = self.lookup(key)

        self.tickers.update(ans)
        if total > self.perpage:
            add = [key + '%20' + t for t in self.letters] + [key + t for t in self.letters]
            self.queue += add

        self.idx += 1
        return (key, len(ans), total)

    def download_all(self):
        while self.done:
            self.download_next()

    def get_dataframe(self):
        return pd.DataFrame(sorted(list(self.tickers)))

    def save(self, path: str = 'YahooTickerDownloader.pickle'):
        with open(path, "wb") as f:
            pickle.dump(self, file=f, protocol=pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def load(path: str = 'YahooTickerDownloader.pickle'):
        with open(path, 'rb') as f:
            return pickle.load(f)
