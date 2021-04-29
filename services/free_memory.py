import logging
from psutil import virtual_memory
from .base_services import TimedService


class FreeMemoryService(TimedService):
    DEFAULT_SLEEP = 10
    DEFAULT_THRESHOLD = 20

    def __init__(self, channels, config) -> None:
        if "threshold" in config.keys():
            self.threshold = int(config["threshold"])
        else:
            self.threshold = None
        if self.threshold is None:
            logging.warning(
                "Free memory threshold not specified for service {}, setting to {}%".format(
                    self._type(), self.DEFAULT_THRESHOLD
                )
            )
            self.threshold = self.DEFAULT_THRESHOLD
        self.threshold_exceeded = False
        super().__init__(channels, config)

    def do_service_logic(self):
        memory_stats = virtual_memory()
        if memory_stats.percent >= self.threshold:
            if not self.threshold_exceeded:
                message = "Memory usage exceeds threshold of {thr}%: {used:.2f} GB / {total:.2f} GB ({per:.2f}% full)".format(
                    thr=self.threshold,
                    used=memory_stats.used / float(1 << 30),
                    total=memory_stats.total / float(1 << 30),
                    per=memory_stats.percent,
                )
                self.send_message(message)
                logging.warning(message)
                self.threshold_exceeded = True
        else:
            if self.threshold_exceeded:
                self.threshold_exceeded = False
