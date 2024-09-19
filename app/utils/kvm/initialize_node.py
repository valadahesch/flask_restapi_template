import json
from app.extensions import logger
from confluent_kafka import Consumer, KafkaError
from app.config import KafkaConfig
from app.controllers.service.CloudLab.Instance.Node import Node


def initialize_node_configuration():

    kafka_config_wait_node_up_operate = {
        'bootstrap.servers': KafkaConfig['host'],
        'group.id': KafkaConfig['topic_node_group'],
        'auto.offset.reset': 'earliest',
        'max.poll.interval.ms': 600000
    }
    consumer_wait_node_up_operate = Consumer(kafka_config_wait_node_up_operate)
    consumer_wait_node_up_operate.subscribe([KafkaConfig['topic_node']])

    while True:
        msg_host_image = consumer_wait_node_up_operate.poll(1.0)
        if msg_host_image is not None:
            if msg_host_image.error():
                if msg_host_image.error().code() == KafkaError._PARTITION_EOF:
                    logger.error('Reached end of partition for topic')
                else:
                    logger.error('Error while consuming message from topic: {}'.format(msg_host_image.error()))
            else:
                msg_offset=msg_host_image.offset()
                producer_msg = json.loads(msg_host_image.value().decode(encoding="utf-8"))
                logger.debug("消费者队列已收到请求,message offset:{0},message content:{1}".format(msg_offset,json.dumps(producer_msg,ensure_ascii=False)))
                Node().initializeNode(node_data=producer_msg)
