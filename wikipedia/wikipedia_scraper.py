from bs4 import BeautifulSoup
from joblib import Parallel, delayed
import requests
import redis


rdis = redis.StrictRedis(host='localhost', port=6379, db=0)


def is_ascii(s):
    return len(s) == len(s.encode())


def get_related_links(title):
    # Check if data is present in the Redis Database
    stored_data = rdis.lrange(title, 0, -1)
    if stored_data is not None:
        return stored_data

    # Fetch Data and store it in the Database

    r = requests.get('http://en.wikipedia.org/wiki/' + title)
    html = r.content

    # Scan the first 3 paragraphs for links
    overview_len = 3

    soup = BeautifulSoup(html, "html.parser")
    links = []

    for paragraph in soup.find_all('p')[:overview_len]:
        for link in paragraph.find_all('a'):
            link_title = link.get("title")
            if link_title is not None and is_ascii(link_title):
                links.append(link.get("title"))

    rdis.lpush(title, *links)


def test():
    keywords = ("Machine_Learning", "Artificial_Intelligence", "Computer_Vision", "Cryptography", "Computer_Science", "Wikipedia", "India", "Artificial_Neural_Networks")
    Parallel(n_jobs=8, backend="threading")(delayed(get_related_links)(i) for i in keywords)


if __name__ == '__main__':
    test()
