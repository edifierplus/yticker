from collections import namedtuple

from pyquery import PyQuery
from selenium import webdriver

TickerTuple = namedtuple('Ticker', ['symbol', 'name', 'industry', 'type', 'exchange'])


class YahooLookupBrowser:
    """The browser simulator to lookup tickers in Yahoo Finance.
    """
    def __init__(self):
        self.browser = self._open_browser()
        self.base_url = "https://finance.yahoo.com/lookup/{category}?s={key}&t=A&b={start}&c={size}"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.browser.close()

    def _open_browser(self):
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        return webdriver.Firefox(options=options)

    def lookup(self, key, category='all', start=0, size=100):
        """Lookup tickers in Yahoo Finance.

        Args:
            key (str): The keyword of the lookup.
            category (str, optional): Category of the tickers. Defaults to 'all'.
            start (int, optional): Start index of the lookup page. Defaults to 0.
            size (int, optional): Size of the lookup page. Defaults to 100.

        Returns:
            (list, int): The pair of lookup results in the page and total tickers matching the keyword.
        """
        url = self.base_url.format(category=category, key=key, start=start, size=size)
        self.browser.get(url)
        raw_data = PyQuery(self.browser.page_source)

        title = raw_data("a[href*=\\/lookup]")[0].find('span').text_content()
        total = int(title[title.find('(') + 1:title.find(')')])

        if total == 0:
            return ([], 0)

        tbody = raw_data("tbody")
        ans = list()
        for row in tbody[0].findall('tr'):
            td = row.findall("td")
            td.pop(2)
            ans.append(TickerTuple._make(x.text_content() for x in td))

        return (ans, total)
