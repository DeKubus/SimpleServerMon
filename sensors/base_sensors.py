from time import sleep
import threading
import abc
import logging


class ServerMonSensor:
    def __init__(self, channels, config) -> None:
        self.channels = channels
        sensor_thread = threading.Thread(target=self.run_sensor)
        sensor_thread.start()

    def run_sensor(self) -> None:
        logging.info("Instantiated {}".format(self._type()))
        while True:
            logging.debug("Running logic for sensor {}".format(self._type()))
            self.do_sensor_logic()
            if hasattr(self, "update_interval"):
                sleep(self.update_interval)

    def send_message(self, message) -> None:
        for channel in self.channels:
            channel.send_message(message)

    @abc.abstractmethod
    def do_sensor_logic(self):
        raise NotImplementedError(
            "Logic for sensor {} was not implemented".format(self._type())
        )

    def _type(self) -> str:
        return self.__class__.__name__


class TimedSensor(ServerMonSensor):
    DEFAULT_SLEEP = 60

    def __init__(self, channels, config) -> None:
        if "update_interval" in config.keys():
            self.update_interval = int(config["update_interval"])
        else:
            self.update_interval = None
        if self.update_interval is None:
            logging.warning(
                "Update interval for sensor {} checks not specified, setting to {} seconds".format(
                    self._type(), self.DEFAULT_SLEEP
                )
            )
            self.update_interval = self.DEFAULT_SLEEP
        super().__init__(channels, config)