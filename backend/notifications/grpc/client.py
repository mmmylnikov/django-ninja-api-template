# mypy: ignore-errors

import logging

import grpc
from django.conf import settings

from notifications.grpc import notyfy_pb2, notyfy_pb2_grpc
from notifications.models import NotificationType


logger = logging.getLogger(__name__)

notification_type_mapping = {
    NotificationType.EVENT_REMINDER: notyfy_pb2.NotificationType.EVENT_REMINDER,
    NotificationType.BOOKING_CONFIRMATION: (
        notyfy_pb2.NotificationType.BOOKING_CONFIRMATION
    ),
    NotificationType.EVENT_CANCELLED: (
        notyfy_pb2.NotificationType.EVENT_CANCELLED
    ),
    NotificationType.EVENT_UPDATED: notyfy_pb2.NotificationType.EVENT_UPDATED,
}


class NotificationGrpcClient:
    def __init__(self) -> None:
        self._channel = None
        self._stub = None

    def send_notification(
        self,
        notification_id: int,
        user_id: int,
        notification_type: str,
        title: str,
        message: str,
    ) -> bool:
        notification_type_enum = notification_type_mapping.get(
            notification_type,
            notyfy_pb2.NotificationType.EVENT_REMINDER,
        )
        self._ensure_connection()
        notification_pb = notyfy_pb2.Notification(
            id=notification_id,
            user_id=user_id,
            type=notification_type_enum,
            title=title,
            message=message,
        )
        try:
            response = self._stub.send_notification(notification_pb)
        except grpc.RpcError as rpc_error:
            logger.exception(
                'gRPC error: %s: %s', rpc_error.code(), rpc_error.details()
            )
            return False
        except Exception:
            logger.exception('Error sending notification via gRPC')
            return False
        else:
            logger.debug(
                'gRPC response: success=%s, message=%s',
                response.success,
                response.message,
            )
            return response.success

    def _ensure_connection(self) -> None:
        if (
            self._channel is None
            or self._channel.connectivity_state(try_to_connect=False)
            != grpc.ChannelConnectivity.READY
        ):
            server_addr = (
                f'{settings.GRPC_SERVER_HOST}:{settings.GRPC_SERVER_PORT}'
            )
            logger.debug('Connecting to gRPC server at %s', server_addr)
            self._channel = grpc.insecure_channel(server_addr)
            self._stub = notyfy_pb2_grpc.NotificationSenderStub(self._channel)


grpc_client = NotificationGrpcClient()
