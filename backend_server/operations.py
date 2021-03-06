import json
import os
import sys
import pickle
import redis

from bson.json_util import dumps
from datetime import datetime


sys.path.append(os.path.join(os.path.dirname(__file__),'..', 'common'))

import mongodb_client
from cloudAMQP_client import CloudAMQPClient
import news_recommendation_service_client

REDIS_HOST = "localhost"
REDIS_PORT = 6379

NEWS_TABLE_NAME = "news"

NEWS_LIST_BATCH_SIZE = 10
NEWS_LIMIT = 100
USER_NEWS_TIME_OUT_IN_SECONDS = 60

redis_client = redis.StrictRedis(REDIS_HOST, REDIS_PORT, db=0)

LOG_CLICKS_TASK_QUEUE_URL = 'amqp://goxlxsjn:0Loy1rWQ4tG_zGjePmCDgd1wCtwd7QxC@spider.rmq.cloudamqp.com/goxlxsjn'
LOG_CLICKS_TASK_QUEUE_NAME = 'log-clicks-task-queue'

cloudAMQP_client = CloudAMQPClient(LOG_CLICKS_TASK_QUEUE_URL, LOG_CLICKS_TASK_QUEUE_NAME)

def getOneNews():
    db = mongodb_client.get_db()
    news = db[NEWS_TABLE_NAME].find_one()
    return json.loads(dumps(news))

def getNewsSummariesForUser(user_id, page_num):
    page_num = int(page_num)
    begin_index = (page_num - 1) * NEWS_LIST_BATCH_SIZE
    end_index = page_num * NEWS_LIST_BATCH_SIZE

    sliced_news = []

    if redis_client.get(user_id) is not None:
        news_digests = pickle.loads(redis_client.get(user_id))
        sliced_news_digests = news_digests[begin_index:end_index]
        db = mongodb_client.get_db()
        sliced_news = list(db[NEWS_TABLE_NAME].find({'digest':{'$in':sliced_news_digests}}))

    else:
        db = mongodb_client.get_db()
        total_news = list(db[NEWS_TABLE_NAME].find().sort([('publishedAt', -1)]).limit(NEWS_LIMIT))
        total_news_digest = [news['digest'] for news in total_news]

        redis_client.set(user_id, pickle.dumps(total_news_digest))
        redis_client.expire(user_id, USER_NEWS_TIME_OUT_IN_SECONDS)

        sliced_news = total_news[begin_index:end_index]

    # TODO: use preference to customize returned news list.
    preference = news_recommendation_service_client.getPreferenceForUser(user_id)
    topPreference = None

    if preference is not None and len(preference) > 0;
        topPreference = preference[0]

    for news in sliced_news:
        del news['text']
        if news['class'] == topPreference:
            news['reason'] = 'Recommend'
        if news['publishedAt'].date() == datetime.today().date():
            news['time'] = 'today'

    return json.loads(dumps(sliced_news))

def logNewsClickForUser(user_id, news_id):
    message = {'userId':user_id, 'newsId':news_id, 'timestamp':str(datetime.utcnow())}
    cloudAMQP_client.sendMessage(message)
