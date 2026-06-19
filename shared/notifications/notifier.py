from __future__ import annotations

import logging

from shared.utils.contracts import NotificationPort

logger = logging.getLogger(__name__)


class ConsoleNotifier(NotificationPort):
    def send(self, title: str, message: str) -> None:
        logger.info("notification", extra={"title": title, "notification_message": message})
