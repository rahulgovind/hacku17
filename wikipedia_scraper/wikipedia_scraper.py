from bs4 import BeautifulSoup
import requests
import redis
import logging


logging.basicConfig(filename='scraper.log', level=logging.DEBUG)
rdis = redis.StrictRedis(host='localhost', port=6379, db=0)

blacklist = ['Wikipedia:Citation needed', 'Help:IPA for English', 'Help:Pronunciation respelling key']


def is_ascii(s):
    try:
        len(s) == len(s.encode())
    except UnicodeEncodeError:
        return False
    return True


def get_related_links(title):
    logging.info("Get Related Links: " + title)
    # Check if data is present in the Redis Database
    stored_data = rdis.lrange(title, 0, -1)
    if stored_data is not None and len(stored_data) > 1:
        logging.info("HIT: " + title)
        return [link.decode("utf-8") for link in stored_data]

    # Fetch Data and store it in the Database
    logging.info("MISS: " + title)

    r = requests.get('http://en.wikipedia.org/wiki/' + title.replace(" ", "_"))
    html = r.content

    # Scan the first 3 paragraphs for links
    overview_len = 3

    soup = BeautifulSoup(html, "html.parser")
    links = []

    for paragraph in soup.find_all('p')[:overview_len]:
        for link in paragraph.find_all('a'):
            link_title = link.get("title")
            if link_title is not None and is_ascii(link_title) and link_title not in blacklist:
                links.append(link.get("title").lower())
    if len(links) > 1:
        rdis.lpush(title.lower(), *links)

    return links


def get_related_topics(title, levels=1):
    logging.info("Get Related Topics: " + title)
    results_level = get_related_links(title)
    logging.info("Related Topics: " + str(len(results_level)))

    if levels < 1:
        return [(key, 1) for key in results_level]

    topics = {}

    for result in results_level:
        topics[result] = levels * 3

    for result in results_level:
        lower_topics = get_related_topics(result, levels-1)
        topics = merge_two_topics(topics, lower_topics)

    return topics.items()


def merge_two_topics(topic_1, topic_2):
    topics = topic_1
    for topic, reps in topic_2:
        if topic not in topics.keys():
            topics[topic] = 0
        topics[topic] += reps
    return topics


def get_topics_given_keywords(keywords):
    topics = {}
    for topic in keywords:
        topics = merge_two_topics(topics, get_related_topics(topic))
    topics_sorted = sorted(topics.items(), key=lambda tup: -tup[1])
    return topics_sorted


def get_topics_given_profiles(profiles):
    topics = {}
    for profile in profiles.keys():
        topics[profile] = get_topics_given_keywords(profiles[profile])
    return topics


if __name__ == '__main__':
    profiles = {"Machine Learning": ["Machine Learning", "Artificial Neural Networks"], "Cryptography": ["Encryption", "Decryption"]}
    get_topics_given_profiles(profiles)
