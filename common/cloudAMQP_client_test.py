from cloudAMQP_client import CloudAMQPClient

TEST_CLOUDAMQP_URL = "amqp://bqrsfgcp:hrqSAaXepjEF8J-Ba2W59-bDqngI9EYm@eagle.rmq.cloudamqp.com/bqrsfgcp"
TEST_QUEUE_NAME = "scape-news-queue"

def test_basic():
    client = CloudAMQPClient(TEST_CLOUDAMQP_URL, TEST_QUEUE_NAME)

    sentMsg = {'test':'test'}
    client.sendMessage(sentMsg)
    receivedMsg = client.getMessage()
    assert sentMsg == receivedMsg
    print('test_basic passed.')

if __name__ == "__main__":
    test_basic()
