from bs4 import BeautifulSoup
import scrapy
import re
from ..items import RunItem
from unidecode import unidecode

class Runs(scrapy.Spider):
    name = "runs"
    start_urls = ['https://gamesdonequick.com/tracker/runs/']

    def parse(self, response):
        """Find links to event bid pages and run "parse_event" on each."""
        
        event_runspge_lst = response.css('div.list-group a')
        yield from response.follow_all(event_runspge_lst, self.parse_event)

    def parse_event(self, response):
        """Extract run data for one event."""

        soup = BeautifulSoup(response.text, "lxml")
        event = unidecode(soup.title.text.split('—')[-1].strip().lower())
        header = self.clean_header([ele.text for ele in soup.find('thead').find_all('th')])
        table = soup.find('table')
        rows = table.find_all('tr', {'class': 'small'})
        
        for row in rows:
            run_id = row.a['href'].split('/')[-1]
            cols = self.clean_row([col.text for col in row.find_all('td')])

            meta_dict = {'run_id': run_id, 'event': event}
            item = RunItem(**dict(zip(header, cols)), **meta_dict)

            yield(item)

    def clean_row(self, row):
        """Simple method for cleaning text in row data."""

        row = [re.sub(' +', ' ', unidecode(ele)
                    .replace('Show Options', '')
                    .replace('Hide Options', '')
                    .replace('\n', '')
                    .replace('\r', '')
                    .replace('--', '')
                    .strip()
                    .lower())
                    for ele in row]
        
        return row

    def clean_header(self, header):
        """Simple method for cleaning text in header data."""

        header = [re.sub(' +', ' ', unidecode(ele)
                        .replace('AscDsc', '')
                        .replace('\n', '')
                        .replace('\r', '')
                        .strip()
                        .lower()).replace(' ', '_')
                        for ele in header]
        
        return header
    