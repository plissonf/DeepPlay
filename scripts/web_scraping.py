#!/path/to/interpreter
#!/usr/bin/env python

from bs4 import BeautifulSoup
from lxml import html
import requests as rq
import re
import pandas as pd
import logging

def get_discipline_value(key):
    '''This function selects one of 6 disciplines (dictionary keys) and allocates its corresponding value (id)
    to discipline_url. The function is called in scraper() function to obtain corresponding html pages'''

    disc = {'STA': 8 ,
        'DYN': 6,
        'DNF': 7,
        'CWT': 3,
        'CNF': 4,
        'FIM': 5
        }
    if key in disc.keys():
        value = disc[key]
        discipline_url = '{}{}'.format('&disciplineId=', value)
        return discipline_url
    else:
        logging.warning('Check your spelling. ' + key + ' is not a freediving discipline')

def cleanser(a_list):
    '''This function changes the list named 'data' scrapped for each discipline and turns it
    into a cleaned and labelled dataframe df using regular expression.'''

    df = pd.DataFrame(a_list)
    df.columns = ['Ranking', 'Name', 'Results', 'Announced', 'Points', 'Penalties', 'Date', 'Place']
    df['Ranking'] = df['Ranking'].str.replace('.', '')
    df['Country'] = df['Name'].str.extract('.*\((.*)\).*', expand=True)
    df['Name'] = df['Name'].str.replace(r"\(.*\)","")
    df['Results'] = df['Results'].str.replace('m', '')
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.drop_duplicates(['Name', 'Results', 'Announced', 'Points', 'Penalties', 'Date', 'Place', 'Country'])
    return df

def scraper(key):
    ''' This function crawls through an entire freediving discipline, regardless how many pages it consists of. '''

    #Obtain html code for url and Parse the page
    base_url = 'https://www.aidainternational.org/Ranking/Rankings?page='
    url = '{}1{}'.format(base_url, get_discipline_value(key))

    page = rq.get(url)
    soup = BeautifulSoup(page.content, "lxml")


    #Use regex to identify the maximum number of pages for the discipline of interest
    page_count = soup.findAll(text=re.compile(r"Page .+ of .+"))
    max_pages = str(page_count).split(' ')[3].split('\\')[0]

    data = []
    for p in range(1, int(max_pages)+1):

        #For each page, create corresponding url, request the library, obtain html code and parse the page
        url = '{}{}{}'.format(base_url, p, get_discipline_value(key))

        #The break plays the role of safety guard if dictionary key is wrong (not spelled properly or non-existent) then the request
        #for library is not executed (and not going through the for loop to generate the data), an empty dataframe is saved
        if url == '{}{}None'.format(base_url, p):
            break
        else:
            new_page = rq.get(url)
            new_soup = BeautifulSoup(new_page.content, "lxml")

            #For each page, each parsed page is saved into the list named "data"
            rows = new_soup.table.tbody.findAll('tr')
            for row in rows:
                cols = row.find_all('td')
                cols = [ele.text.strip() for ele in cols]
                data.append([ele for ele in cols if ele])

            p += 1

    #Results from list "data" are cleaned using "cleanser" method and saved in a dataframe clean_df
    clean_df = cleanser(data)
    logging.warning('Finished!')

    #Dataframe df is saved in file results.txt to access results offline
    filename = '/Users/fabienplisson/Desktop/Github_shares/DeepPlay/deepplay/data/cleaned/results_{}.txt'.format(key)
    with open(filename, 'a') as f:
        f.write(str(clean_df))
    f.closed
