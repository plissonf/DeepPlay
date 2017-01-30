from bs4 import BeautifulSoup
from lxml import html
import requests as rq
import re
import pandas as pd

def discipline_scraper():
    ''' This function crawls through an entire freediving discipline, regardless how many pages it consists of. '''

    base_url = 'https://www.aidainternational.org/Ranking/Rankings?page='
    '''Pre-selected discipline Constant Weight CWT with id = 3'''
    discipline_url = '&disciplineId=3'
    '''Obtain html code for url'''
    page = rq.get(base_url)
    #discipline_id
    '''Parse the page'''
    soup = BeautifulSoup(page.content, "lxml")


    '''Use regex to identify the maximum number of pages for the discipline of interest'''
    p = 1
    page_count = soup.findAll(text=re.compile(r"Page .+ of .+"))
    max_pages = str(page_count).split(' ')[3].split('\\')[0]

    data = []
    while p < int(max_pages) :
        '''For each page, create corresponding url, obtain html code and parse'''
        url = '{}{}'.format(base_url, p, discipline_url)
        new_page = rq.get(url)
        new_soup = BeautifulSoup(new_page.content, "lxml")

        '''For each page, each parsed page is saved into the list named "data" '''
        rows = new_soup.table.tbody.findAll('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            data.append([ele for ele in cols if ele]) # data is a list

        p += 1

    '''Results from list "data" are saved in a dataframe df '''
    df=pd.DataFrame(data)
    cols = ["Ranking", "Name", "Results", "Announced", "Points", "Penalties", "Date", "Place"]
    df.columns = cols
    print df

    '''Dataframe df is saved in file results.txt to access results offline'''
    filename = '/Users/fabienplisson/Desktop/DeepPlay/deepplay/notebooks/results.txt'
    f = open(filename, 'a')
    f.write(str(df))
    f.close()
