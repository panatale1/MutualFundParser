from bs4 import BeautifulSoup
import requests


def mutual_fund_parser(cik_or_ticker):
"""This method takes in a string CIK or ticker, obtains data,
   and parses into a tab-delimited file"""
    # Initial search parameters
    payload = {
        'CIK': cik_or_ticker,
        'Find': 'Search',
        'owner': 'exclude',
        'action': 'getcompany'
    }
    search_results = requests.get(
        'https://www.sec.gov/cgi-bin/browse-edgar', params=payload
    )
    search_content = BeautifulSoup(search-results.content, features='html')
    file_urls = []
    # Get document urls for each of the 13F files from the initial search
    for line in search_content.findAll(name='tr'):
        if line.findChild(name='td', text='13F-HR'):
            file_urls.append(line.findNext(name='a').attrs['href']
    # Replace '-index.htm' at the end of the urls with '.txt' to immediately get txt file
    for i in range(len(file_urls)):
        file_urls[i] = file_urls[i].replace('-index.htm', '.txt')

