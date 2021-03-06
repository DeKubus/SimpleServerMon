import abc
import logging


class CommunicationChannel:
    def __init__(self) -> None:
        logging.info("Instantiated communication channel {}".format(self._type()[:-7]))

    @abc.abstractmethod
    def send_message(self, message, source_sensor=None) -> None:
        raise NotImplementedError(
            "Logic for messaging channel {} was not implemented".format(self._type())
        )

    def _type(self) -> str:
        return self.__class__.__name__