from collections import namedtuple

from pyquery import PyQuery
from requests import get

TickerTuple = namedtuple('Ticker', ['symbol', 'name', 'industry', 'type', 'exchange'])


class YahooLookupBrowser:
    """The browser simulator to lookup tickers in Yahoo Finance.
    """

    def __init__(self):
        self.base_url = "https://finance.yahoo.com/lookup/{category}?s={key}&t=A&b={start}&c={size}"

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
        response = get(url)

        if not response.ok or 'Will be right back' in response.text:
            # page temporarily unavailable
            raise ConnectionRefusedError("Lookup page is temporarily unavailable")

        raw_data = PyQuery(response.text)
        title = raw_data("a[href*=\\/lookup]")[0].find('span').text_content()
        total = int(title[title.find('(') + 1:title.find(')')])

        if total == 0:
            # nothing is in the lookup page, so don't parse it
            return ([], 0)

        tbody = raw_data("tbody")
        ans = list()
        for row in tbody[0].findall('tr'):
            td = row.findall("td")
            td.pop(2)  # remove latest price
            ans.append(TickerTuple._make(x.text_content() for x in td))

        return (ans, total)
