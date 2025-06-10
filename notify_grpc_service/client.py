import logging

import grpc
import notyfy_pb2
import notyfy_pb2_grpc


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(message)s',
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger('NotificationServer')


def send_notification_grpc():
    channel = grpc.insecure_channel('localhost:50051')
    stub = notyfy_pb2_grpc.NotificationSenderStub(channel)

    notification = notyfy_pb2.Notification(
        id=123,
        user_id=456,
        type=notyfy_pb2.NotificationType.EVENT_REMINDER,
        title='Event Reminder',
        message='You have an event scheduled for tomorrow at 10:00',
    )

    logger.info('Sending a notification: %s', notification)
    try:
        response = stub.send_notification(notification)
    except grpc.RpcError as error:
        logger.info(
            'Error when calling RPC: %s: %s', error.code(), error.details()
        )
    else:
        logger.info('Server response:')
        logger.info('Successfully: %s', response.success)
        logger.info('Message: %s', response.message)
        if response.notification:
            logger.info(
                'Received notification: \n===\n%s===\n', response.notification
            )


if __name__ == '__main__':
    send_notification_grpc()
