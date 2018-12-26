import os
import sys

# import common package in parent directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))

from cloudAMQP_client import CloudAMQPClient

SCRAPE_NEWS_TASK_QUEUE_URL = 'amqp://bqrsfgcp:hrqSAaXepjEF8J-Ba2W59-bDqngI9EYm@eagle.rmq.cloudamqp.com/bqrsfgcp'
SCRAPE_NEWS_TASK_QUEUE_NAME = 'scrape-news-queue'

DEDUPE_NEWS_TASK_QUEUE_URL = 'amqp://hlhtmkus:DgxLGj2hew73t7djxHdPvZeQewIRNuaY@eagle.rmq.cloudamqp.com/hlhtmkus'
DEDUPE_NEWS_TASK_QUEUE_NAME = 'dedupe-news-queue'

def clearQueue(queue_url, queue_name):
    scrape_news_queue_client = CloudAMQPClient(queue_url, queue_name)

    num_of_messages = 0

    while True:
        if scrape_news_queue_client is not None:
            msg = scrape_news_queue_client.getMessage()
            if msg is None:
                print("Cleared %d messages." % num_of_messages)
                return
            num_of_messages += 1


if __name__ == "__main__":
    clearQueue(SCRAPE_NEWS_TASK_QUEUE_URL, SCRAPE_NEWS_TASK_QUEUE_NAME)
    clearQueue(DEDUPE_NEWS_TASK_QUEUE_URL, DEDUPE_NEWS_TASK_QUEUE_NAME)
