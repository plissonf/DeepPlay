
# AIDA Freediving Records

The project DeepPlay aims at exploring and displaying the world of competitive freediving using web-scraping, machine learning and data visualizations (e.g. D3.js). The main source of information is the official website of AIDA, International Association for the Development of Apnea. The present work has been created within 10 days including exploratory data analysis.

1- Scraping the data from the website

2- Data preparation / cleaning / extension (separate name / country, get GPS locations, get gender...)

3- Early data exploration (see exploratory_data_analysis.html)


-

Load modules


```python
from bs4 import BeautifulSoup
from lxml import html
import requests as rq
import pandas as pd
import re
import logging
```

-

The method get_discipline_value(key) selects one of 6 disciplines (dictionary keys: STA, DYN, DNF, CWT, CNF, FIM) and allocates its corresponding value (id) to a new url, discipline_url.
If the discipline is mispelled or inexistent, get_discipline_value throws the sentence "Check your spelling ... is not a freediving discipline".

The method is called within the following method scraper( ) function to obtain html pages associated with a discipline.


```python
def get_discipline_value(key):

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
```


```python
get_discipline_value('NFT')
```

-

The method cleanser( ) changes the list of lists named 'data' which is collected all html pages for each discipline into a cleaned and labelled dataframe df. The method uses regular expressions. It will also be called within the method scraper( ).


```python
def cleanser(a_list):
    
    df = pd.DataFrame(a_list)
    df.columns = ['Ranking', 'Name', 'Results', 'Announced', 'Points', 'Penalties', 'Date', 'Place']
    df['Ranking'] = df['Ranking'].str.replace('.', '')
    df['Country'] = df['Name'].str.extract('.*\((.*)\).*', expand=True)
    df['Name'] = df['Name'].str.replace(r"\(.*\)","")
    df['Results'] = df['Results'].str.replace('m', '')
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.drop_duplicates(['Name', 'Results', 'Announced', 'Points', 'Penalties', 'Date', 'Place', 'Country'])
    return df
```

-

The method scraper( ) crawls through an entire freediving discipline, identifies how many pages it consists of (max_pages), obtains html code from all urls and save this code into a list of lists (data). The later is saved into a cleaned data frame using cleanser( ), ready for data analysis


```python
def scraper(key):
    
    #Obtain html code for url and Parse the page
    base_url = 'https://www.aidainternational.org/Ranking/Rankings?page='
    url = '{}1{}'.format(base_url, get_discipline_value(key))

    page = rq.get(url)
    soup = BeautifulSoup(page.content, "lxml")


    #Use regex to identify the maximum number of pages for the discipline of interest
    page_count = soup.findAll(text=re.compile(r"Page .+ of .+"))
    max_pages = str(page_count).split(' ')[3].split('\\')[0]
    total_obs = int(max_pages)*20

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
    pd.set_option('max_rows', int(total_obs))
    pd.set_option('expand_frame_repr', True)

    #Dataframe df is saved in file results_key.csv to access results offline
    filename = '/Users/fabienplisson/Desktop/Github_shares/DeepPlay/deepplay/data/cleaned/results_{}.csv'.format(key)
    clean_df.to_csv(filename, encoding ='utf-8')
    logging.warning('Finished!')
    #with open(filename,'a') as f:
        #f.write(clean_df.encode('uft-8'))
    #f.closed

```


```python
scraper('DYN')
```

-

# Future Steps 

- Integrating all methods into class using Object-oriented programming (OOP)
- Tidying up data with more specific regular expressions
- Applying web-scraping to other websites to collect other features and datasets that share similar types of information (athlete name, country, record values (time, distance), location of the event, date).


```python

```
