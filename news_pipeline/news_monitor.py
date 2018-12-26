import datetime
import hashlib
import os
import redis
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))

import news_api_client
from cloudAMQP_client import CloudAMQPClient

NEWS_SOURCES = [
    'bbc-news',
    'bbc-sport',
    'bloomberg',
    'cnn',
    'entertainment-weekly',
    'espn',
    'ign',
    'techcrunch',
    'the-new-york-times',
    'the-wall-street-journal',
    'the-washington-post'
]

SLEEP_TIME_IN_SECONDS = 10
NEWS_TIME_OUT_IN_SECONDS = 3600 * 24 * 3

REDIS_HOST = 'localhost'
REDIS_PORT = 6379

SCRAPE_NEWS_TASK_QUEUE_URL = 'amqp://bqrsfgcp:hrqSAaXepjEF8J-Ba2W59-bDqngI9EYm@eagle.rmq.cloudamqp.com/bqrsfgcp'
SCRAPE_NEWS_TASK_QUEUE_NAME = 'scrape-news-queue'


redis_client = redis.StrictRedis(REDIS_HOST, REDIS_PORT)
cloudAMQP_client = CloudAMQPClient(SCRAPE_NEWS_TASK_QUEUE_URL, SCRAPE_NEWS_TASK_QUEUE_NAME)



def run():
    while True:
        news_list = news_api_client.getNewsFromSources(NEWS_SOURCES)
        num_of_new_news = 0

        for news in news_list:
            news_digest = hashlib.md5(news['description'].encode('utf-8')).hexdigest()

            if redis_client.get(news_digest) is None:
                num_of_new_news = num_of_new_news + 1
                news['digest'] = news_digest

                if news['publishedAt'] is None:
                    news['publishedAt'] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

                redis_client.set(news_digest, 'True')
                redis_client.expire(news_digest, NEWS_TIME_OUT_IN_SECONDS)

                cloudAMQP_client.sendMessage(news)

        print("Fetched %d news." % num_of_new_news)

        cloudAMQP_client.sleep(SLEEP_TIME_IN_SECONDS)


if __name__ == "__main__":
    run()
