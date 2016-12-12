from bs4 import BeautifulSoup
import requests


def mutual_fund_parser(cik_or_ticker, get_all=False):
    """This method takes in a string CIK or ticker, obtains data,
       and parses into a tab-delimited file

       params:
       cik_or_ticker: The CIK or ticker to search for, must be a string
       get_all: A boolean value. If not provided, only the latest 13F record
                will be retrieved.
    """
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
    search_content = BeautifulSoup(search_results.content, features='html')
    file_urls = []
    # Get document urls for each of the 13F files from the initial search
    for line in search_content.findAll(name='tr'):
        if line.findChild(name='td', text='13F-HR'):
            file_urls.append(line.findNext(name='a').attrs['href'])
            if not get_all:
                break
    # Replace '-index.htm' at the end of the urls with '.txt' to immediately get txt file
    for i in range(len(file_urls)):
        file_urls[i] = file_urls[i].replace('-index.htm', '.txt')
    # Retrieve files and parse
    top_headers = '\t\t\t\t\t\t\t\t\tValue\t\tSHRS OR\t\tSH/\tPUT/\tINVESTMENT\tOTHER\t\tVOTING AUTHORITY\n'
    bottom_headers = ('NAME OF ISSUER\t\t\tTITLE OF CLASS\t\tCUSIP\t\t(x$1000)\tPRN AMOUNT\tPRN\tCALL'
                      '\tDISCRETION\tMANAGERS\tSOLE\tSHARED\tNONE\n')
    for url in file_urls:
        file_content = requests.get('https://www.sec.gov{0}'.format(url)).content
        file_date = file_content.split('<ACCEPTANCE-DATETIME>')[1][:8]
        with open('{0}-{1}.txt'.format(cik_or_ticker, file_date), 'w') as output_file:
            output_file.write(top_headers)
            output_file.write(bottom_headers)
            # Two cases here: files with XML and files without XML
            if '<XML>' in file_content:
                file_content = file_content.split('</SEC-HEADER>')[1]
                xml_soup = BeautifulSoup(file_content, features='xml')
                other_managers = xml_soup.findAll('otherIncludedManagersCount')[0].text
                for item in xml_soup.findAll(name='infoTable'):
                    fields = {
                        'name': item.nameOfIssuer.text,
                        'title': item.titleOfClass.text,
                        'cusip': item.cusip.text,
                        'value': item.value.text,
                        'shrs_or_prn_amt': item.shrsOrPrnAmt.sshPrnamt.text,
                        'sh_prn': item.shrsOrPrnAmt.sshPrnamtType.text,
                        'put_call': '\t',
                        'discretion': item.investmentDiscretion.text,
                        'sole': item.votingAuthority.Sole.text,
                        'shared': item.votingAuthority.Shared.text,
                        'none': item.votingAuthority.None.text
                    }
                    if int(other_managers) == 0:
                        fields['other_managers'] = '\t'
                    else:
                        fields['other_managers'] = item.otherManagers.text + '\t'
                    if len(fields['name']) < 32:
                        remaining = 32 - len(fields['name'])
                        if remaining / 8 > 0:
                            for i in range(remaining / 8):
                                fields['name'] += '\t'
                    if len(fields['title']) < 24:
                        remaining = 24 - len(fields['title'])
                        if remaining / 8.0 > 1 and not remaining % 8 == 0:
                            for i in range(remaining / 8):
                                fields['title'] += '\t'
                        else:
                            for i in range((remaining / 8) - 1):
                                fields['title'] += '\t'
                    if len(fields['value']) < 16:
                        remaining = 16 - len(fields['value'])
                        if remaining / 8.0 > 1 and not remaining % 8 == 0:
                            for i in range(remaining / 8):
                                fields['value'] += '\t'
                        else:
                            for i in range((remaining / 8) - 1):
                                fields['value'] += '\t'
                    if len(fields['shrs_or_prn_amt']) < 16:
                        remaining = 16 - len(fields['shrs_or_prn_amt'])
                        if remaining / 8.0 > 1 and not remaining % 8 == 0:
                            for i in range(remaining / 8):
                                fields['shrs_or_prn_amt'] += '\t'
                        else:
                            for i in range((remaining / 8) - 1):
                                fields['shrs_or_prn_amt'] += '\t'
                    output_file.write(
                        '{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}{7}\t\t\t{8}{9}\t{10}\t{11}\n'.format(
                            fields['name'], fields['title'], fields['cusip'], fields['value'],
                            fields['shrs_or_prn_amt'], fields['sh_prn'], fields['put_call'],
                            fields['discretion'], fields['other_managers'], fields['sole'],
                            fields['shared'], fields['none']
                        )
                    )
            else:
                file_content = file_content.split('<PAGE>')[-1]
