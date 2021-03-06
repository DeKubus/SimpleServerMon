import logging
from psutil import disk_partitions, disk_usage
from .base_sensors import TimedSensor


class DiskspaceSensor(TimedSensor):
    DEFAULT_SLEEP = 10
    DEFAULT_THRESHOLD = 20

    def __init__(self, channels, config) -> None:
        if "threshold" in config.keys():
            self.threshold = int(config["threshold"])
        else:
            self.threshold = None
        if self.threshold is None:
            logging.warning(
                "Disk space threshold not specified for sensor {}, setting to {}%".format(
                    self._type(), self.DEFAULT_THRESHOLD
                )
            )
            self.threshold = self.DEFAULT_THRESHOLD
        self.excluded_partitions = (
            config["excluded_partitions"] if "excluded_partitions" in config else []
        )
        self.was_exceeded = []
        super().__init__(channels, config)

    def do_sensor_logic(self) -> None:
        partitions = disk_partitions()
        too_full = []
        for partition in partitions:
            if partition.mountpoint not in self.excluded_partitions:
                try:
                    usage = disk_usage(partition.mountpoint)
                except FileNotFoundError as e:
                    logging.error(
                        "An error occurred while the disk usage has been determined: {}".format(
                            str(e)
                        )
                    )
                    continue
                percent_usage = usage.used / usage.total * 100
                if percent_usage >= self.threshold:
                    if partition.mountpoint not in self.was_exceeded:
                        message = "Disk usage exceeds threshold of {thr}% for partition {part} (device {dev}): {used:.2f} GB / {total:.2f} GB ({per:.2f}% full)".format(
                            thr=self.threshold,
                            part=partition.mountpoint,
                            dev=partition.device,
                            used=usage.used / float(1 << 30),
                            total=usage.total / float(1 << 30),
                            per=percent_usage,
                        )
                        too_full.append(message)
                        logging.warning(message)
                        self.was_exceeded.append(partition.mountpoint)
                else:
                    logging.debug(
                        "Threshold of {}% not exceeded for {}".format(
                            self.threshold, partition.mountpoint
                        )
                    )
                    if partition.mountpoint in self.was_exceeded:
                        self.was_exceeded.remove(partition.mountpoint)
                        logging.debug(
                            "Threshold for {} no longer exceeded".format(
                                partition.mountpoint
                            )
                        )
        if len(too_full) > 0:
            message = "\n".join(too_full)
            self.send_message(message)
