import os
import sys

import news_classes

# import common package in parent directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))

import mongodb_client
from cloudAMQP_client import CloudAMQPClient

NUM_OF_CLASSES = 8
INITIAL_P = 1.0 / NUM_OF_CLASSES
ALPHA = 0.2


PREFERENCE_MODEL_TABLE_NAME = "user_preference_model"
NEWS_TABLE_NAME = "news"

LOG_CLICKS_TASK_QUEUE_URL = 'amqp://goxlxsjn:0Loy1rWQ4tG_zGjePmCDgd1wCtwd7QxC@spider.rmq.cloudamqp.com/goxlxsjn'
LOG_CLICKS_TASK_QUEUE_NAME = 'log-clicks-task-queue'

SLEEP_TIME_IN_SECONDS = 1

cloudAMQP_client = CloudAMQPClient(LOG_CLICKS_TASK_QUEUE_URL, LOG_CLICKS_TASK_QUEUE_NAME)

def handle_message(msg):
    if msg is None or not isinstance(msg, dict):
        print('message is broken')
        return

    if ('userId' not in msg or 'newsId' not in msg or 'timestamp' not in msg):
        return

    userId = msg['userId']
    newsId = msg['newsId']

    # Update user's preference model.
    db = mongodb_client.get_db()
    model = db[PREFERENCE_MODEL_TABLE_NAME].find_one({'userId':userId})

    # If model not exists, create a new one.
    if model is None:
        print("Creating preference model for new user: %s" % userId)
        new_model = {'userId':userId}
        preference = {}
        for i in news_classes.classes:
            preference[i] = float(INITIAL_P)
        new_model['preference'] = preference
        model = new_model

    # Update model using time decay method.
    news = db[NEWS_TABLE_NAME].find_one({'digest':newsId})

    if (news is None or 'class' not in news or news['class'] not in news_classes.classes):
        print('Skipping processing...')
        return

    click_class = news['class']

    # Update the clicked one.
    old_p = model['preference'][click_class]
    model['preference'][click_class] = float((1 - ALPHA) * old_p + ALPHA)

    # Update not clicked classes.
    for i, prob in model['preference'].items():
        if not i == click_class:
            model['preference'][i] = float((1 - ALPHA) * model['preference'][i])

    db[PREFERENCE_MODEL_TABLE_NAME].replace_one({'userId':userId}, model, upsert=True)


def run():
    while True:
        if cloudAMQP_client is not None:
            msg = cloudAMQP_client.getMessage()
            if msg is not None:
                # Parse and process the task
                try:
                    handle_message(msg)
                except Exception as e:
                    print(e)
                    pass
            cloudAMQP_client.sleep(SLEEP_TIME_IN_SECONDS)

if __name__ == "__main__":
    run()
