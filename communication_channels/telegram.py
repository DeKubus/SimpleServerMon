from .base_channel import CommunicationChannel
import requests
import logging


class TelegramChannel(CommunicationChannel):
    def __init__(self, config) -> None:
        if "token" in config and len(config["token"]) > 42:
            self.telegram_token = config["token"]
        else:
            raise ValueError("Invalid Telegram token value provided, aborting")
        super().__init__()

    def send_message(self, message) -> None:
        response = requests.post(
            f"https://api.telegram.org/bot{self.telegram_token}/sendMessage",
            params={"chat_id": "305068973", "text": message},
        )
        if response.status_code < 200 or response.status_code > 299:
            logging.error(
                "Received error response from Telegram API: {} (status code {})".format(
                    response.content, response.status_code
                )
            )
