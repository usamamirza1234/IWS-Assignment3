import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import matplotlib.pyplot as plt

def get_quote_data(quote, page_number):
    text = quote.find('span', class_='text').text.strip()
    author = quote.find('small', class_='author').text.strip()
    tagsList = [tag.text for tag in quote.find('div', class_='tags').find_all('a')]
    return [text, author,  ', '.join(tagsList),page_number]

def check_module(url):
    response = requests.get(url)
    return response.status_code == 200

def crawl_module(base_url):
    page_number = 1
    while True:
        url = urljoin(base_url, f'page/{page_number}/')

        if not check_module(url):
            break

        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        quotes = soup.find_all('div', class_='quote')

        if not quotes:  # If there are no quotes on the page, terminate the loop
            break

        for quote in quotes:
            singleQuote = get_quote_data(quote, page_number)

            allQuotes.append(singleQuote)

        page_number += 1

    return page_number  # Add this line to return the page_number

allQuotes = []
start_time = time.time()
page_number = crawl_module('http://quotes.toscrape.com')
end_time = time.time()
time_taken = end_time - start_time
print(f'Time taken to crawl: {time_taken:.2f} seconds')

if allQuotes:
    dataframe = pd.DataFrame(allQuotes, columns=['text', 'author', 'tagsList', 'page_number'])
    print(dataframe)

    total_valid_pages = page_number - 1
    print(f'Total count of valid pages: {total_valid_pages}')

    author_quotes_count = dataframe['author'].value_counts()
    print('Frequency distribution of quotes per author:')
    print(author_quotes_count)

    all_tags = [tag for tagsList in dataframe['tagsList'].str.split(', ') for tag in tagsList]
    tags_count = pd.Series(all_tags).value_counts()
    print('Frequency distribution of tags:')
    print(tags_count)

    dataframe['quote_length'] = dataframe['text'].apply(lambda x: len(x.split()))
    avg_length_per_author = dataframe.groupby('author')['quote_length'].mean()

    plt.figure(figsize=(10, 6))
    avg_length_per_author.plot(kind='bar', color='skyblue')
    plt.title('Average Length of Quotes per Author')
    plt.xlabel('Author')
    plt.ylabel('Average Length (words)')
    plt.show()
else:
    print('No data found.')



