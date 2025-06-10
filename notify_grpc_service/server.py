import logging
from concurrent import futures

import grpc
import notyfy_pb2
import notyfy_pb2_grpc


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(message)s',
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger('NotificationServer')


class NotificationServicer(notyfy_pb2_grpc.NotificationSenderServicer):
    def send_notification(self, request, context):
        logger.info('=== Notification received ===')
        logger.info('ID: %s', request.id)
        logger.info('User ID: %s', request.user_id)
        logger.info('Type: %s', notyfy_pb2.NotificationType.Name(request.type))
        logger.info('Title: %s', request.title)
        logger.info('Message: %s', request.message)
        logger.info('===========================')

        return notyfy_pb2.NotificationResponse(
            success=True,
            message='The notification was received successfully',
            notification=request,
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    notyfy_pb2_grpc.add_NotificationSenderServicer_to_server(
        NotificationServicer(), server
    )
    server.add_insecure_port('[::]:50051')
    server.start()
    logger.info('The debug gRPC server is running on the port 50051')
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
